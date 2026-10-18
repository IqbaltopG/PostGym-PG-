document.addEventListener('alpine:init', () => {
    Alpine.data('gymApp', () => ({
        activeTab: 'jadwal', // Tab aktif: jadwal, log, vision, history, progress
        todayDate: new Date().toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'short' }),
        showRankModal: false, // Modal detail rank kompetitif
        showScheduleModal: false,
        showAccountModal: false,
        showCustomLogModal: false,
        showVictoryModal: false, // Modal ringkasan sesi latihan (Victory screen)
        
        rankInfo: null, // Info ranking kompetitif
        sessionSummary: null, // Ringkasan performa sesi hari ini (tonase, strain, RP gain)
        
        todaySchedule: { name: "Loading...", exercises: [] },
        logs: [], // Untuk tab history (riwayat)
        
        // --- 1. MULLVAD-STYLE ANONYMOUS ACCOUNT & MONETIZATION ---
        account: {
            account_id: '',
            is_pro: false,
            pro_expires_at: null,
            days_remaining: 0
        },
        voucherInput: '',
        voucherError: '',
        voucherSuccess: '',
        isRedeeming: false,
        isSimulatingQris: false,
        copyTooltip: 'Salin ID',

        // --- 2. QUICK LOG & DRAFT STATE ---
        quickLogLoading: {},
        quickLogFeedback: {},
        exerciseDrafts: {}, // canonical -> { weight: X, reps: Y }
        customLog: { canonical: '', name: '', muscle_group: 'chest', weight: 20, reps: 10 },

        // --- THEME (DARK / LIGHT MODE) ---
        theme: localStorage.getItem('postgym_theme') || 'dark',

        initTheme() {
            const saved = localStorage.getItem('postgym_theme') || 'dark';
            this.theme = saved;
            document.documentElement.setAttribute('data-theme', saved);
            document.body.className = saved + '-theme';
        },

        toggleTheme() {
            this.theme = this.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('postgym_theme', this.theme);
            document.documentElement.setAttribute('data-theme', this.theme);
            document.body.className = this.theme + '-theme';
            this.updateChartThemes();
        },

        async init() {
            this.initTheme();
            await this.initAccount();
            await this.loadSchedule();
            await this.loadHistory();
        },

        async initAccount() {
            let accId = localStorage.getItem('postgym_account_id');
            if (!accId) {
                try {
                    const res = await fetch('/api/account/generate', { method: 'POST' });
                    const data = await res.json();
                    accId = data.account_id;
                    localStorage.setItem('postgym_account_id', accId);
                } catch(e) {
                    console.error("Gagal generate account:", e);
                }
            }
            if (accId) {
                this.account.account_id = accId;
                await this.checkAccountStatus();
            }
        },

        async checkAccountStatus() {
            if (!this.account.account_id) return;
            try {
                const res = await fetch(`/api/account/status?id=${encodeURIComponent(this.account.account_id)}`);
                const data = await res.json();
                this.account = data;
            } catch(e) {
                console.error("Gagal cek status akun:", e);
            }
        },

        async redeemVoucher() {
            if (!this.voucherInput.trim()) return;
            this.isRedeeming = true;
            this.voucherError = '';
            this.voucherSuccess = '';
            try {
                const res = await fetch('/api/account/redeem', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: this.account.account_id,
                        voucher_code: this.voucherInput.trim()
                    })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    this.voucherSuccess = data.message;
                    this.voucherInput = '';
                    await this.checkAccountStatus();
                } else {
                    this.voucherError = data.message || 'Voucher tidak valid!';
                }
            } catch(e) {
                this.voucherError = 'Gagal menghubungi server!';
            } finally {
                this.isRedeeming = false;
            }
        },

        async simulateQrisPayment() {
            this.isSimulatingQris = true;
            this.voucherError = '';
            this.voucherSuccess = '';
            try {
                const res = await fetch('/api/account/simulate-qris', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: this.account.account_id,
                        duration_days: 30
                    })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    this.voucherSuccess = data.message;
                    await this.checkAccountStatus();
                } else {
                    this.voucherError = data.message || 'Simulasi QRIS gagal!';
                }
            } catch(e) {
                this.voucherError = 'Gagal memproses simulasi QRIS';
            } finally {
                this.isSimulatingQris = false;
            }
        },

        copyAccountId() {
            if (this.account.account_id) {
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(this.account.account_id);
                } else {
                    const temp = document.createElement("input");
                    temp.value = this.account.account_id;
                    document.body.appendChild(temp);
                    temp.select();
                    document.execCommand("copy");
                    document.body.removeChild(temp);
                }
                this.copyTooltip = 'Tersalin! ✅';
                setTimeout(() => { this.copyTooltip = 'Salin ID'; }, 2000);
            }
        },

        // --- 3. JADWAL & QUICK LOG ENGINE ---
        async loadSchedule() {
            try {
                const response = await fetch('/api/today');
                this.todaySchedule = await response.json();
                if (this.todaySchedule.rank) this.rankInfo = this.todaySchedule.rank;
                if (this.todaySchedule.session_summary) this.sessionSummary = this.todaySchedule.session_summary;

                // Inisialisasi draft input per exercise (berdasarkan rekomendasi / riwayat terakhir)
                if (this.todaySchedule.exercises) {
                    for (let ex of this.todaySchedule.exercises) {
                        if (!this.exerciseDrafts[ex.canonical]) {
                            let defaultW = 20;
                            let defaultR = 10;
                            if (ex.recommendation?.weight) {
                                defaultW = ex.recommendation.weight;
                                defaultR = ex.recommendation.target_reps || 10;
                            } else if (ex.last_weight !== null) {
                                defaultW = ex.last_weight;
                                const match = String(ex.last_reps || "").match(/\d+/);
                                defaultR = match ? parseInt(match[0]) : 10;
                            }
                            this.exerciseDrafts[ex.canonical] = { weight: defaultW, reps: defaultR };
                        }
                    }
                }
            } catch (error) {
                console.error("Gagal mengambil jadwal:", error);
            }
        },

        adjustDraft(canonical, field, delta) {
            if (!this.exerciseDrafts[canonical]) {
                this.exerciseDrafts[canonical] = { weight: 20, reps: 10 };
            }
            if (field === 'weight') {
                let current = parseFloat(this.exerciseDrafts[canonical].weight) || 0;
                let next = Math.max(0, current + delta);
                this.exerciseDrafts[canonical].weight = Math.round(next * 2) / 2; // kelipatan 0.5kg
            } else if (field === 'reps') {
                let current = parseInt(this.exerciseDrafts[canonical].reps) || 0;
                this.exerciseDrafts[canonical].reps = Math.max(1, current + delta);
            }
        },

        async quickLogSet(exercise) {
            const canonical = exercise.canonical;
            this.quickLogLoading[canonical] = true;
            this.quickLogFeedback[canonical] = '';

            const draft = this.exerciseDrafts[canonical] || {
                weight: exercise.recommendation?.weight || exercise.last_weight || 20,
                reps: exercise.recommendation?.target_reps || 10
            };

            const payload = {
                canonical: canonical,
                name: exercise.name,
                muscle_group: exercise.muscle_group || 'other',
                weight_kg: parseFloat(draft.weight) || 0,
                reps: parseInt(draft.reps) || 10,
                note: ''
            };

            try {
                const res = await fetch('/api/quick-log', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                if (result.status === 'success') {
                    exercise.today_sets = result.today_sets;
                    exercise.today_total_sets = result.today_sets.length;
                    if (result.rank) this.rankInfo = result.rank;
                    if (result.session_summary) this.sessionSummary = result.session_summary;
                    
                    const count = result.today_sets.length;
                    const rpNotice = result.session_summary ? ` (+${result.session_summary.rp_earned} RP)` : '';
                    this.quickLogFeedback[canonical] = `✅ Set ${count} (${payload.weight_kg}kg × ${payload.reps} reps) tercatat!${rpNotice}`;
                    setTimeout(() => {
                        if (this.quickLogFeedback[canonical]?.startsWith('✅')) {
                            this.quickLogFeedback[canonical] = '';
                        }
                    }, 3500);

                    this.loadHistory();
                } else {
                    alert('Gagal mencatat set: ' + (result.message || 'Error'));
                }
            } catch(e) {
                alert('Gagal koneksi ke server untuk mencatat set!');
            } finally {
                this.quickLogLoading[canonical] = false;
            }
        },

        async undoSet(exercise) {
            const canonical = exercise.canonical;
            if (!confirm(`Batalkan set terakhir untuk ${exercise.name}?`)) return;

            try {
                const res = await fetch('/api/quick-log/undo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ canonical: canonical })
                });
                const result = await res.json();
                if (result.status === 'success') {
                    this.quickLogFeedback[canonical] = '↺ Set terakhir dibatalkan';
                    setTimeout(() => { this.quickLogFeedback[canonical] = ''; }, 2500);
                    await this.loadSchedule();
                    await this.loadHistory();
                } else {
                    alert('Gagal membatalkan: ' + result.message);
                }
            } catch(e) {
                alert('Gagal membatalkan set!');
            }
        },

        async saveCustomQuickLog() {
            if (!this.customLog.name.trim()) {
                alert('Masukkan nama gerakan!');
                return;
            }
            const canonical = this.customLog.canonical || this.customLog.name.toLowerCase().trim().replace(/[^a-z0-9]+/g, '_');
            try {
                const res = await fetch('/api/quick-log', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        canonical: canonical,
                        name: this.customLog.name.trim(),
                        muscle_group: this.customLog.muscle_group || 'other',
                        weight_kg: parseFloat(this.customLog.weight) || 0,
                        reps: parseInt(this.customLog.reps) || 10,
                        note: 'Manual Quick Log'
                    })
                });
                const result = await res.json();
                if (result.status === 'success') {
                    alert('Berhasil mencatat latihan!');
                    this.showCustomLogModal = false;
                    this.customLog = { canonical: '', name: '', muscle_group: 'chest', weight: 20, reps: 10 };
                    await this.loadSchedule();
                    await this.loadHistory();
                } else {
                    alert('Gagal: ' + result.message);
                }
            } catch(e) {
                alert('Koneksi server gagal');
            }
        },

        // --- 4. DATA EXPORT (ANTI DATA LOCK-IN) ---
        downloadExport(format) {
            window.location.href = `/api/export/${format}`;
        },

        // --- 5. JADWAL SETTINGS ---
        scheduleForm: { senin: '', selasa: '', rabu: '', kamis: '', jumat: '', sabtu: '', minggu: '' },

        async openScheduleModal() {
            try {
                const res = await fetch('/api/schedule');
                const sched = await res.json();
                for (let day of ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']) {
                    this.scheduleForm[day] = (sched[day] || ['rest']).join(', ');
                }
                this.showScheduleModal = true;
            } catch(e) {
                alert("Gagal memuat jadwal!");
            }
        },

        async saveScheduleForm() {
            try {
                const payload = {};
                for (let day of ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']) {
                    const raw = this.scheduleForm[day] || 'rest';
                    payload[day] = raw.split(',').map(s => s.trim().toLowerCase()).filter(s => s.length > 0);
                    if (payload[day].length === 0) payload[day] = ['rest'];
                }
                const res = await fetch('/api/schedule', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                if (result.status === 'success') {
                    alert("Jadwal mingguan berhasil diperbarui!");
                    this.showScheduleModal = false;
                    this.loadSchedule();
                } else {
                    alert("Gagal menyimpan jadwal!");
                }
            } catch(e) {
                alert("Error saat menyimpan jadwal!");
            }
        },

        async loadHistory() {
            try {
                const response = await fetch('/api/history');
                this.logs = await response.json();
            } catch (error) {
                console.error("Gagal mengambil history:", error);
            }
        },

        // --- 6. CORE AI FREE-TEXT PARSER (PRO TIER) ---
        rawLogText: '',
        isParsing: false,
        parsedResult: null,
        editableJson: '',
        isSaving: false,

        async parseWithAI() {
            if (!this.rawLogText.trim()) return;
            
            this.isParsing = true;
            this.parsedResult = null;
            this.editableJson = '';

            try {
                const response = await fetch('/api/parse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        raw_text: this.rawLogText,
                        account_id: this.account.account_id
                    })
                });
                
                const result = await response.json();
                
                if (result.status === "pro_required") {
                    this.showAccountModal = true;
                    this.voucherError = result.message;
                    this.isParsing = false;
                    return;
                }

                if (result.status === "success") {
                    this.parsedResult = result.data;
                    this.editableJson = JSON.stringify(result.data, null, 2);
                } else {
                    alert("Error dari AI: " + result.message);
                }
            } catch(e) {
                alert("Gagal koneksi ke server AI!");
            }
            this.isParsing = false;
        },

        async saveToDB() {
            this.isSaving = true;
            try {
                const parsedData = JSON.parse(this.editableJson);
                const response = await fetch('/api/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(parsedData)
                });
                
                const result = await response.json();
                if (result.status === "success") {
                    this.rawLogText = '';
                    this.parsedResult = null;
                    this.editableJson = '';
                    if (result.rank) this.rankInfo = result.rank;
                    if (result.session_summary) {
                        this.sessionSummary = result.session_summary;
                        this.showVictoryModal = true;
                    }
                    await this.loadSchedule();
                    await this.loadHistory();
                    this.activeTab = 'jadwal';
                } else {
                    alert("Gagal menyimpan: " + result.message);
                }
            } catch(e) {
                alert("Format JSON tidak valid atau server error!");
            }
            this.isSaving = false;
        },

        // --- 7. GRAFIK KONSISTENSI & PROGRESS (CHART.JS) ---
        recapPeriod: 'month',
        selectedExercise: '',
        exerciseList: [],
        chartRecapInstance: null,
        chartProgInstance: null,
        recapTimer: null,
        isFetchingRecap: false,
        isFetchingProgress: false,

        updateChartThemes() {
            const isDark = this.theme === 'dark';
            const gridColor = isDark ? '#27272a' : '#e4e4e7';
            const textColor = isDark ? '#a1a1aa' : '#52525b';
            const titleColor = isDark ? '#fafafa' : '#09090b';

            if (this.chartRecapInstance) {
                try {
                    this.chartRecapInstance.options.scales.x.ticks.color = textColor;
                    this.chartRecapInstance.options.scales.y.ticks.color = textColor;
                    this.chartRecapInstance.options.scales.y.grid.color = gridColor;
                    this.chartRecapInstance.options.plugins.legend.labels.color = titleColor;
                    this.chartRecapInstance.update('none');
                } catch(e) { console.error("Error updating recap chart theme:", e); }
            }

            if (this.chartProgInstance) {
                try {
                    this.chartProgInstance.options.scales.x.ticks.color = textColor;
                    this.chartProgInstance.options.scales.y.ticks.color = textColor;
                    this.chartProgInstance.options.scales.y.grid.color = gridColor;
                    this.chartProgInstance.options.plugins.legend.labels.color = titleColor;
                    if (this.chartProgInstance.data.datasets && this.chartProgInstance.data.datasets[0]) {
                        this.chartProgInstance.data.datasets[0].backgroundColor = isDark ? 'rgba(34, 197, 94, 0.12)' : 'rgba(34, 197, 94, 0.18)';
                    }
                    this.chartProgInstance.update('none');
                } catch(e) { console.error("Error updating progress chart theme:", e); }
            }
        },

        async initCharts() {
            if (this.exerciseList.length === 0) {
                try {
                    const res = await fetch('/api/exercises/list');
                    this.exerciseList = await res.json();
                } catch(e) { console.error(e); }
            }
            if (this.recapTimer) clearTimeout(this.recapTimer);
            this.recapTimer = setTimeout(() => {
                this.fetchRecap();
                if (this.selectedExercise) this.fetchProgress();
            }, 60);
        },

        async fetchRecap() {
            if (this.isFetchingRecap) return;
            this.isFetchingRecap = true;
            try {
                const res = await fetch('/api/progress/recap?period=' + this.recapPeriod);
                const data = await res.json();
                const labels = data.map(d => d.period);
                const values = data.map(d => d.sessions);
                
                const isDark = this.theme === 'dark';
                const gridColor = isDark ? '#27272a' : '#e4e4e7';
                const textColor = isDark ? '#a1a1aa' : '#52525b';
                const titleColor = isDark ? '#fafafa' : '#09090b';

                const canvas = document.getElementById('recapChart');
                if (!canvas) return;

                // Jika chart sudah ada dan terikat ke canvas, update saja datanya agar tidak ada double render!
                const existing = typeof Chart !== 'undefined' ? Chart.getChart(canvas) : null;
                if (this.chartRecapInstance && existing) {
                    this.chartRecapInstance.data.labels = labels;
                    this.chartRecapInstance.data.datasets[0].data = values;
                    this.chartRecapInstance.options.scales.x.ticks.color = textColor;
                    this.chartRecapInstance.options.scales.y.ticks.color = textColor;
                    this.chartRecapInstance.options.scales.y.grid.color = gridColor;
                    this.chartRecapInstance.options.plugins.legend.labels.color = titleColor;
                    this.chartRecapInstance.update();
                    return;
                }

                if (existing) {
                    existing.destroy();
                }
                if (this.chartRecapInstance) {
                    try { this.chartRecapInstance.destroy(); } catch(e){}
                    this.chartRecapInstance = null;
                }

                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                this.chartRecapInstance = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Jumlah Sesi Latihan',
                            data: values,
                            backgroundColor: '#22c55e',
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: {
                            duration: 350
                        },
                        scales: {
                            y: { 
                                beginAtZero: true, 
                                grid: { color: gridColor }, 
                                ticks: { 
                                    color: textColor,
                                    precision: 0 
                                } 
                            },
                            x: { 
                                grid: { display: false }, 
                                ticks: { color: textColor } 
                            }
                        },
                        plugins: { 
                            legend: { 
                                labels: { 
                                    color: titleColor, 
                                    font: { family: 'inherit' } 
                                } 
                            } 
                        }
                    }
                });
            } catch(e) { 
                console.error("Error fetchRecap:", e); 
            } finally {
                this.isFetchingRecap = false;
            }
        },

        async fetchProgress() {
            const canvas = document.getElementById('progressChart');
            if (!this.selectedExercise) {
                if (canvas && typeof Chart !== 'undefined') {
                    const existing = Chart.getChart(canvas);
                    if (existing) existing.destroy();
                }
                if (this.chartProgInstance) {
                    try { this.chartProgInstance.destroy(); } catch(e){}
                    this.chartProgInstance = null;
                }
                return;
            }
            if (this.isFetchingProgress) return;
            this.isFetchingProgress = true;
            try {
                const res = await fetch('/api/progress/exercise/' + this.selectedExercise);
                const data = await res.json();
                const labels = data.map(d => d.date);
                const values = data.map(d => d.max_weight);
                
                const isDark = this.theme === 'dark';
                const gridColor = isDark ? '#27272a' : '#e4e4e7';
                const textColor = isDark ? '#a1a1aa' : '#52525b';
                const titleColor = isDark ? '#fafafa' : '#09090b';

                if (!canvas) return;

                const existing = typeof Chart !== 'undefined' ? Chart.getChart(canvas) : null;
                if (this.chartProgInstance && existing) {
                    this.chartProgInstance.data.labels = labels;
                    this.chartProgInstance.data.datasets[0].data = values;
                    if (this.chartProgInstance.data.datasets[0]) {
                        this.chartProgInstance.data.datasets[0].backgroundColor = isDark ? 'rgba(34, 197, 94, 0.12)' : 'rgba(34, 197, 94, 0.18)';
                    }
                    this.chartProgInstance.options.scales.x.ticks.color = textColor;
                    this.chartProgInstance.options.scales.y.ticks.color = textColor;
                    this.chartProgInstance.options.scales.y.grid.color = gridColor;
                    this.chartProgInstance.options.plugins.legend.labels.color = titleColor;
                    this.chartProgInstance.update();
                    return;
                }

                if (existing) {
                    existing.destroy();
                }
                if (this.chartProgInstance) {
                    try { this.chartProgInstance.destroy(); } catch(e){}
                    this.chartProgInstance = null;
                }

                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                this.chartProgInstance = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Beban Maks (kg)',
                            data: values,
                            borderColor: '#22c55e',
                            backgroundColor: isDark ? 'rgba(34, 197, 94, 0.12)' : 'rgba(34, 197, 94, 0.18)',
                            fill: true,
                            tension: 0.25,
                            pointBackgroundColor: '#22c55e',
                            pointRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: {
                            duration: 350
                        },
                        scales: {
                            y: { beginAtZero: true, grid: { color: gridColor }, ticks: { color: textColor } },
                            x: { grid: { display: false }, ticks: { color: textColor } }
                        },
                        plugins: { legend: { labels: { color: titleColor, font: { family: 'inherit' } } } }
                    }
                });
            } catch(e) { 
                console.error("Error fetchProgress:", e); 
            } finally {
                this.isFetchingProgress = false;
            }
        },

        // --- 8. AI VIDEO POSE FORM CHECKER (PRO TIER) ---
        selectedVideoExercise: 'squat',
        videoFile: null,
        videoFileName: '',
        videoFileSize: '',
        isAnalyzingVideo: false,
        videoResult: null,
        videoError: null,
        dragOver: false,

        handleVideoSelect(event) {
            const file = event.target.files[0];
            if (file) this.setVideoFile(file);
        },

        handleVideoDrop(event) {
            this.dragOver = false;
            const file = event.dataTransfer.files[0];
            if (file) this.setVideoFile(file);
        },

        setVideoFile(file) {
            this.videoFile = file;
            this.videoFileName = file.name;
            const mb = (file.size / (1024 * 1024)).toFixed(1);
            this.videoFileSize = `${mb} MB`;
            this.videoResult = null;
            this.videoError = null;
        },

        resetVideoAnalysis() {
            this.videoFile = null;
            this.videoFileName = '';
            this.videoFileSize = '';
            this.videoResult = null;
            this.videoError = null;
        },

        async uploadAndAnalyzeVideo() {
            if (!this.videoFile) return;
            this.isAnalyzingVideo = true;
            this.videoError = null;
            this.videoResult = null;

            try {
                const formData = new FormData();
                formData.append('video', this.videoFile);
                formData.append('exercise', this.selectedVideoExercise);
                if (this.account.account_id) {
                    formData.append('account_id', this.account.account_id);
                }

                const res = await fetch('/api/analyze-video', {
                    method: 'POST',
                    body: formData
                });

                if (!res.ok) {
                    throw new Error(`Server returned HTTP ${res.status}`);
                }

                const data = await res.json();
                if (data.status === 'pro_required') {
                    this.showAccountModal = true;
                    this.voucherError = data.message;
                    return;
                }

                if (data.status === 'success') {
                    this.videoResult = data;
                } else {
                    this.videoError = data.message || "Gagal menganalisis video!";
                }
            } catch (err) {
                console.error("Error analyzing video:", err);
                this.videoError = "Gagal memproses video: " + err.message;
            } finally {
                this.isAnalyzingVideo = false;
            }
        }
    }));
});
