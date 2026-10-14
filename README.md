# POST GYM 🏋️‍♂️🤖

> **100% Offline Edge-AI Gym Logger with Progressive Overload & Gamification**  
> *Catat latihan sesukamu pakai bahasa gaul gym — AI lokal yang urus strukturnya.*

---

## 📌 Ringkasan Proyek

Kebanyakan aplikasi gym (seperti Strong atau JEFIT) memaksa pengguna memilih latihan dari *dropdown* panjang dan menginput set/rep satu per satu. Hal ini menimbulkan friksi tinggi saat sedang beristirahat antar-set.

**POST GYM** menyelesaikan masalah ini dengan pendekatan **Free-Text First**:
- Ketik bebas seperti di aplikasi Notes (contoh: `bench press 60kg 8x3, set terakhir gagal rep ke-7`).
- **Small Language Model (SLM)** lokal mem-parsing teks tersebut secara otomatis menjadi data terstruktur JSON.
- **Rule Engine Deterministik** menghitung rekomendasi beban berikutnya berdasarkan prinsip *Double Progression* tanpa risiko halusinasi angka.
- **100% Offline & Private**: Data tidak pernah dikirim ke Cloud. Model berjalan di perangkat lokal menggunakan `llama.cpp` dengan akselerasi hardware Vulkan.

---

## ✨ Fitur Utama

- ✍️ **Free-Text Natural Language Logging**: Bebas nulis nama gerakan singkatan (`bp`, `rdl`, `jm press`), bahasa campur Indonesia-Inggris (`each`, `gagal rep 7`, `bar only`), maupun format repetisi (`10x3`, `8 8 7`).
- 🔒 **100% Local & Privacy-Preserving**: Model AI dijalankan secara lokal di laptop/PC. Catatan beban angkatan Anda aman dan tidak pernah dikirim ke server pihak ketiga.
- 🎯 **Rule Engine & Progressive Overload**: Rekomendasi beban deterministik menggunakan metode *Double Progression* (deteksi deload -5% saat underperform, dan saran kenaikan beban +2.5kg saat batas rep tercapai).
- 📈 **Progress & Consistency Tracking**: Grafik interaktif konsistensi latihan mingguan/bulanan dan perkembangan beban maksimal per gerakan (Chart.js).
- 🎮 **Gamifikasi RPG**: Dapatkan XP setiap sesi latihan untuk naik level dari *Couch Potato* (Level 1) hingga *Greek God* (Level 13+).
- 📱 **Mobile & Low-Spec Friendly**: Frontend berbasis Alpine.js dengan ukuran total bundle **< 100 KB** (tanpa butuh *node_modules* atau *build tools*).

---

## 🏛️ Arsitektur Sistem

```
┌────────────────────────────────────────────────────────┐
│             Client Device (HP / Browser)               │
│               Alpine.js SPA & Chart.js                 │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP POST /api/parse
                            ▼
┌────────────────────────────────────────────────────────┐
│           FastAPI Server (Python 3.11+)                │
│  - Heuristic Preprocessor (Regex multiplier expansion) │
│  - JSON Schema Validator & Deduplication               │
└─────────────┬────────────────────────────┬─────────────┘
              │ ChatML + Schema            │ CRUD
              ▼                            ▼
┌───────────────────────────┐  ┌─────────────────────────┐
│   llama.cpp (Vulkan)      │  │    SQLite Database      │
│ Qwen2.5-1.5B-Instruct     │  │      gymmate.db         │
│ GGUF Q4_K_M (~940 MB)     │  │  (Sessions, Sets, Logs) │
└───────────────────────────┘  └───────────┬─────────────┘
                                           │ Query
                                           ▼
                               ┌─────────────────────────┐
                               │   Python Rule Engine    │
                               │   (Double Progression)  │
                               └─────────────────────────┘
```

---

## 🛠️ Tech Stack

| Komponen | Teknologi | Keterangan |
|---|---|---|
| **Frontend** | HTML5, CSS3, Alpine.js, Chart.js | Zero build step, bundle < 100KB, mobile-first dark theme |
| **Backend** | Python 3.11+, FastAPI, Uvicorn | Asynchronous REST API |
| **Database** | SQLite3 | Single-file zero-configuration database |
| **AI Inference** | `llama.cpp` (Vulkan Backend) | Akselerasi GPU Vulkan untuk NVIDIA MX350 & Intel UHD |
| **Model** | Qwen2.5-1.5B-Instruct (GGUF Q4_K_M) | Footprint ~940MB, multilingual (Indonesian/English) |
| **Fine-Tuning** | QLoRA via Unsloth (Google Colab T4) | Dilatih khusus untuk domain gym slang & shorthand |

---

## ⚡ Performa Hardware (Benchmarked on Acer Aspire 5)

Sistem diuji pada spesifikasi laptop entry-level (Intel Core i3-1115G4, RAM 8GB, GPU NVIDIA GeForce MX350 2GB):

| Metrik | Hasil Pengujian |
|---|---|
| **VRAM Consumption** | ~1.26 GB / 2.00 GB (Sisa ruang ~740 MB aman) |
| **Generation Speed** | ~32 – 38 tokens / detik |
| **Prompt Processing** | ~350 – 550 tokens / detik |
| **Time to First Token** | ~0.9 – 1.4 detik |
| **Total Parse Latency** | ~3 – 5 detik per log sesi lengkap |

---

## 🚀 Panduan Instalasi & Menjalankan

### 1. Clone Repository
```bash
git clone https://github.com/IqbaltopG/PostGym-PG-.git
cd PostGym-PG-
```

### 2. Setup Environment Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r src/backend/requirements.txt
```

### 3. Letakkan Model GGUF
Download atau export model `Qwen2.5-1.5B-Instruct` format GGUF (`Q4_K_M`) dan letakkan di dalam folder `models/`:
```bash
# Struktur: models/Qwen2.5-1.5B-Instruct.Q4_K_M.gguf
```

### 4. Jalankan AI Inference Server (`llama.cpp`)
Jalankan `llama-server` dengan akselerasi GPU:
```bash
./llama.cpp/build/bin/llama-server \
  -m models/Qwen2.5-1.5B-Instruct.Q4_K_M.gguf \
  -ngl 99 \
  -c 2048 \
  --port 8080
```

### 5. Jalankan Backend FastAPI
Di terminal baru:
```bash
source venv/bin/activate
cd src/backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Buka **`http://localhost:8000`** di browser laptop Anda, atau buka **`http://<IP-Laptop-Anda>:8000`** langsung dari browser handphone (pastikan terhubung ke WiFi yang sama).

---

## 📁 Struktur Direktori

```
aplikasi-gym/
├── dataset/                    # Pipeline data training & anotasi
│   ├── gold/                   # 50+ anotasi pasangan input-output JSON terverifikasi
│   ├── raw/                    # Catatan teks mentah asli (24 Juli - 14 Okt 2026)
│   ├── scripts/                # Script preprocessing & builder dataset ChatML
│   ├── dataset_train.jsonl     # Dataset final siap training Unsloth
│   └── gymmate-finetune.ipynb  # Google Colab notebook untuk QLoRA fine-tuning
├── docs/                       # Dokumentasi arsitektur & PRD
├── models/                     # Tempat file bobot GGUF (dikecualikan dari git)
├── src/
│   ├── backend/                # Server FastAPI & Logic
│   │   ├── main.py             # Endpoint API & integrasi llama-server
│   │   ├── database.py         # Skema & query SQLite
│   │   ├── rules.py            # Rule engine Double Progression
│   │   └── requirements.txt    # Dependensi backend
│   └── frontend/               # Single Page Application
│       ├── index.html          # UI antarmuka utama (4 tab)
│       ├── app.js              # Logika state reaktif (Alpine.js)
│       ├── style.css           # Styling mobile dark-mode
│       ├── alpine.min.js       # Framework reaktif lokal
│       └── chart.min.js        # Library grafik lokal
├── README.md
└── .gitignore
```

---

## 🔮 Roadmap Pengembangan Lanjutan

- [x] Natural Language Parsing via Local SLM (Qwen 2.5 1.5B)
- [x] Heuristic Preprocessing (Regex multiplier & decimal handler)
- [x] Double Progression Rule Engine
- [x] Interactive Charting & RPG Gamification Leveling
- [ ] **Video Form Check (CV)**: Analisis sudut sendi & rep counting otomatis untuk gerakan Squat menggunakan YOLOv8n-pose.
- [ ] **Data Export**: Fitur ekspor riwayat latihan ke format CSV & JSON.

---

## 📜 Lisensi & Catatan Privasi

Aplikasi ini dikembangkan untuk keperluan akademik dan penggunaan pribadi. File `.gitignore` telah dikonfigurasi untuk mengecualikan model GGUF dan database pribadi. Catatan beban angkatan Anda tetap berada 100% di perangkat Anda sendiri.
