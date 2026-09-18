document.addEventListener('alpine:init', () => {
    Alpine.data('gymApp', () => ({
        activeTab: 'jadwal', // Tab aktif: jadwal, log, history
        todayDate: new Date().toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'short' }),
        
        todaySchedule: { name: "Loading...", exercises: [] },
        logs: [], // Untuk tab history (riwayat)
        
        async init() {
            this.loadSchedule();
            this.loadHistory();
        },
        
        async loadSchedule() {
            try {
                const response = await fetch('/api/today');
                this.todaySchedule = await response.json();
            } catch (error) {
                console.error("Gagal mengambil jadwal:", error);
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
                    body: JSON.stringify({ raw_text: this.rawLogText })
                });
                
                const result = await response.json();
                
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
                    alert("Berhasil disimpan ke Database!");
                    this.rawLogText = '';
                    this.parsedResult = null;
                    this.editableJson = '';
                    
                    this.loadSchedule();
                    this.loadHistory();
                    this.tab = 'history'; // Pindah ke tab history setelah save
                } else {
                    alert("Gagal menyimpan: " + result.message);
                }
            } catch(e) {
                alert("Format JSON tidak valid atau server error!");
            }
            this.isSaving = false;
        },

        // --- FITUR GRAFIK (CHART.JS) ---
        recapPeriod: 'month',
        selectedExercise: '',
        exerciseList: [],
        chartRecapInstance: null,
        chartProgInstance: null,

        async initCharts() {
            // Ambil daftar gerakan buat dropdown
            if (this.exerciseList.length === 0) {
                try {
                    const res = await fetch('/api/exercises/list');
                    this.exerciseList = await res.json();
                } catch(e) { console.error(e); }
            }
            // Langsung render grafik konsistensi
            setTimeout(() => this.fetchRecap(), 100);
        },

        async fetchRecap() {
            try {
                const res = await fetch('/api/progress/recap?period=' + this.recapPeriod);
                const data = await res.json();
                const labels = data.map(d => d.period);
                const values = data.map(d => d.sessions);
                
                if(this.chartRecapInstance) this.chartRecapInstance.destroy();
                const ctx = document.getElementById('recapChart').getContext('2d');
                this.chartRecapInstance = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{ label: 'Jumlah Sesi Latihan', data: values, backgroundColor: '#03dac6' }]
                    },
                    options: { scales: { y: { beginAtZero: true, ticks: { color: '#ccc' } }, x: { ticks: { color: '#ccc' } } }, plugins: { legend: { labels: { color: '#fff' } } } }
                });
            } catch(e) { console.error(e); }
        },

        async fetchProgress() {
            if(!this.selectedExercise) {
                if(this.chartProgInstance) this.chartProgInstance.destroy();
                return;
            }
            try {
                const res = await fetch('/api/progress/exercise/' + this.selectedExercise);
                const data = await res.json();
                const labels = data.map(d => d.date);
                const values = data.map(d => d.max_weight);
                
                if(this.chartProgInstance) this.chartProgInstance.destroy();
                const ctx = document.getElementById('progressChart').getContext('2d');
                this.chartProgInstance = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{ label: 'Beban Maks (kg)', data: values, borderColor: '#bb86fc', backgroundColor: 'rgba(187, 134, 252, 0.2)', fill: true, tension: 0.3 }]
                    },
                    options: { scales: { y: { beginAtZero: true, ticks: { color: '#ccc' } }, x: { ticks: { color: '#ccc' } } }, plugins: { legend: { labels: { color: '#fff' } } } }
                });
            } catch(e) { console.error(e); }
        }
    }));
});
