# POST GYM 🏋️‍♂️

> Tracker latihan gym minimalis, cepat, dan 100% offline. Dibuat karena aplikasi gym mainstream (Strong, Hevy) terlalu ribet dipakai pas tangan lagi gemetaran di sela-sela set latihan.

---

## Kenapa Bikin Aplikasi Ini?

Sebagian besar aplikasi pencatat gym di Play Store atau App Store punya masalah yang sama:
1. **Terlalu banyak klik & dropdown**: Pas lagi ngos-ngosan abis set berat, kita dipaksa nyari nama alat dari daftar panjang, ngetik beban, dan ngisi repetisi satu per satu.
2. **Paywall berlebihan**: Fitur esensial kayak grafik perkembangan, riwayat lengkap, atau bikin jadwal latihan sering dikunci di balik langganan bulanan mahal.
3. **Data dikunci (Vendor Lock-in)**: Susah buat ngekstrak data latihan sendiri ke Excel atau backup lokal.
4. **Harus login & rawan tracking**: Minta email, nomor HP, atau akun Google cuma buat nyatet angka angkatan beban.

**POST GYM** fokus ke hal sederhana: **buka aplikasi, catat dalam 1 tap, dan simpan data sepenuhnya di perangkat sendiri.**

---

## Fitur Utama

### 1. 1-Tap Quick Logger (Frictionless UX)
- Jadwal latihan hari ini otomatis tampil di layar utama.
- Beban dan repetisi dari sesi sebelumnya langsung terisi otomatis.
- Cukup satu sentuhan tombol **"+ Catat Set"**, set langsung tercatat tanpa perlu ngetik ulang. Ada tombol tactile stepper (`-` / `+`) kalau bebannya beda.

### 2. Competitive Athletic Rank (Anti-Ego Lifting)
- Sistem ranking atletik bertingkat mirip game kompetitif (dari *Rookie Lifter*, *Bronze Athlete*, *Silver Grinder*, hingga *Grandmaster Athletic*).
- **Anti-Ego Lifting**: Ranking tidak cuma dihitung dari angka beban mentah (yang sering bikin orang angkat beban ngawur lalu cedera), melainkan dari **Work Capacity** (akumulasi volume kerja yang bersih, konsistensi repetisi, dan pemulihan).

### 3. Match Summary & Strain Telemetry
- Setiap kali sesi latihan diselesaikan, muncul ringkasan ala *match victory screen*:
  - **Skor Strain (0–21)**: Mengukur tingkat kelelahan dan intensitas sesi (mirip algoritma telemetry WHOOP).
  - **Total Tonnage**: Akumulasi total kilogram beban yang diangkat hari ini.
  - **Rank Points (RP)**: Poin kenaikan pangkat yang didapat dari sesi tersebut.

### 4. Akun Privat Tanpa Identitas (Model Mullvad VPN)
- Tidak ada form registrasi, email, password, atau nomor handphone.
- Setiap pengguna mendapatkan **16-digit ID acak unik** (contoh: `GYM-4829-1092-8834`).
- Pindah perangkat cukup dengan memasukkan 16-digit ID tersebut. Database SQLite menyimpannya secara rapi.

### 5. Bebas Lock-in (Export CSV & JSON)
- Data latihan adalah hak milik pengguna sepenuhnya.
- Tersedia tombol 1-klik untuk mengunduh seluruh riwayat sesi dalam format **CSV** (bisa langsung dibuka di Microsoft Excel / Google Sheets) maupun **JSON** mentah.

### 6. Edge AI Lokal (100% Offline & Private)
Fitur AI dijalankan sepenuhnya di CPU/GPU lokal tanpa mengirim data keluar laptop:
- **Gym Slang Free-Text Parser**: Kalau lagi malas nge-tap tombol dan lebih suka ngetik cepat di notes pakai bahasa gaul gym Indo (contoh: `"letpul 45kg 3 set trs bisep krol 10kg sampe tremor"`), Small Language Model (**Qwen 2.5 1.5B via llama.cpp**) akan otomatis mem-parsing teks acak tersebut menjadi data set dan repetisi terstruktur.
- **Squat Pose Form Checker**: Menggunakan Computer Vision (**YOLOv8 Pose**) untuk mendeteksi kedalaman squat (*hip crease* relatif terhadap lutut) dan menghitung repetisi valid langsung dari video rekaman.

### 7. Dark & Light Mode Berkontras Tinggi
- Tampilan Dark Mode (Zinc Pitch `#09090b` & Emerald `#22c55e`) yang hemat daya.
- Tampilan Light Mode (Clean Slate) dengan kontras teks tajam (WCAG AA), tidak silau dan tidak pudar di bawah terik lampu gym.

---

## Arsitektur & Cara Kerja

```
┌────────────────────────────────────────────────────────┐
│                   Frontend Client                      │
│        Alpine.js + Vanilla CSS + Chart.js (SPA)        │
│          Ukuran bundle total < 100 KB (No Node)        │
└───────────────────────────┬────────────────────────────┘
                            │ REST API (JSON)
                            ▼
┌────────────────────────────────────────────────────────┐
│                FastAPI Backend (Python)                │
│  - Endpoint Quick Log, Jadwal, History, Export, Rank   │
│  - Rule Engine Double Progression & Anti-Ego Logic     │
│  - Mullvad-style Anonymous Account & Voucher Auth      │
└─────────────┬────────────────────────────┬─────────────┘
              │                            │
              ▼                            ▼
┌───────────────────────────┐  ┌─────────────────────────┐
│   llama.cpp (Vulkan GPU)  │  │   Database SQLite       │
│  Qwen 2.5 1.5B (GGUF)     │  │   gymmate.db            │
│  (Parsing Bahasa Gaul)    │  │   (Relasional & Cepat)  │
└───────────────────────────┘  └─────────────────────────┘
              │
              ▼
┌───────────────────────────┐
│   YOLOv8-Pose (CV Model)  │
│   (Form Check Squat)      │
└───────────────────────────┘
```

---

## Spesifikasi & Dependensi

| Komponen | Teknologi | Alasan Pemilihan |
|---|---|---|
| **Frontend** | HTML5, CSS3, Alpine.js, Chart.js | Ringan, responsif di HP, tanpa build-step (`node_modules`), buka langsung jalan. |
| **Backend** | Python 3.11+, FastAPI, Uvicorn | Asynchronous, performa tinggi, dan mudah diintegrasikan dengan modul AI/CV. |
| **Database** | SQLite3 | Portabel, zero-configuration, cukup satu file `.db`. |
| **SLM Inference** | `llama.cpp` (Vulkan Backend) | Akselerasi hardware lancar bahkan di laptop spek terjangkau (NVIDIA MX350 / Intel iGPU). |
| **Computer Vision** | Ultralytics YOLOv8-pose | Pelacakan landmark sendi tubuh secara akurat dan cepat. |

---

## Panduan Instalasi & Menjalankan

### 1. Clone Repository
```bash
git clone https://github.com/IqbaltopG/PostGym-PG-.git
cd PostGym-PG-
```

### 2. Siapkan Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r src/backend/requirements.txt
```

### 3. Unduh Bobot Model GGUF (Untuk Fitur AI Parser)
Letakkan file model `Qwen2.5-1.5B-Instruct` format GGUF (`Q4_K_M`) di dalam direktori `models/`:
```bash
# Struktur: models/Qwen2.5-1.5B-Instruct.Q4_K_M-V2.gguf
```

Jalankan inference server:
```bash
./llama.cpp/build/bin/llama-server \
  -m models/Qwen2.5-1.5B-Instruct.Q4_K_M-V2.gguf \
  -ngl 99 \
  -c 2048 \
  --port 8080
```

### 4. Jalankan Server FastAPI
Di terminal baru:
```bash
source venv/bin/activate
cd src/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Akses aplikasi di browser:
- Dari laptop: `http://localhost:8000`
- Dari HP (WiFi yang sama): `http://<IP-Laptop-Kamu>:8000`

---

## Pengujian Otomatis (Integration Tests)

Seluruh endpoint backend, validasi akun Mullvad, voucher, logger, rank points, dan ekspor data diuji secara menyeluruh melalui test suite:

```bash
python3 tests/test_all_endpoints.py
```

Semua 11 skenario pengujian utama (Akun, Voucher, Jadwal, Quick Log, History, Double Progression, Ekspor CSV/JSON, Health Check) wajib berstatus **PASSED (100%)**.

---

## Struktur Direktori

```
aplikasi-gym/
├── src/
│   ├── backend/
│   │   ├── main.py             # Endpoint API FastAPI
│   │   ├── database.py         # Skema SQLite, operasi CRUD, & rank system
│   │   ├── rules.py            # Rule engine progresif & kalkulasi strain
│   │   ├── pose_tracker.py     # Modul Computer Vision YOLOv8 pose
│   │   └── requirements.txt    # Daftar dependensi Python
│   └── frontend/
│       ├── index.html          # Antarmuka SPA utama
│       ├── app.js              # State management Alpine.js
│       ├── style.css           # Design tokens, dark & light theme
│       ├── alpine.min.js       # Framework reaktif frontend
│       └── chart.min.js        # Rendering grafik performa
├── tests/
│   └── test_all_endpoints.py   # Suite uji otomatis menyeluruh
├── training/                   # Skrip pipeline dataset slang & fine-tuning
├── models/                     # Tempat model GGUF & YOLO (dikecualikan dari git)
├── README.md                   # Dokumentasi teknis proyek
└── .gitignore
```

---

## Lisensi & Privasi

Proyek ini dibangun untuk kebutuhan tugas besar akademik dan penggunaan fitness harian. Seluruh data latihan, akun, dan video pose bersifat 100% privat dan tersimpan lokal di perangkat Anda tanpa analitik pihak ketiga.
