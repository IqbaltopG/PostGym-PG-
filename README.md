# POST GYM 🏋️‍♂️🤖

**POST GYM** adalah asisten *logger* gym berbasis AI (Small Language Model) yang bisa berjalan **100% Offline** di perangkat spesifikasi rendah (Laptop/HP). 

Berbeda dengan aplikasi gym biasa yang memaksa user memilih gerakan dari *dropdown*, **POST GYM** membebaskan user untuk mencatat dengan teks bebas, gaya bahasa *slang*, atau singkatan. AI akan secara otomatis mem-*parsing* catatan tersebut menjadi data terstruktur JSON via metode *HTTP POST*.

## Fitur Utama
- **Free-Text Logging:** Ketik bebas (contoh: `bench press 60kg 10x3`), AI yang urus sisanya.
- **100% Local & Private:** Data tidak pernah dikirim ke Cloud. Model AI dijalankan murni secara lokal menggunakan `llama.cpp` dengan akselerasi Vulkan.
- **Rule Engine & Rekomendasi:** Sistem akan membaca jadwal (Push/Pull/Legs) dan memberikan rekomendasi target beban berdasarkan prinsip *Progressive Overload*.
- **Progress Tracking:** Grafik konsistensi dan perkembangan beban maksimum per gerakan.
- **Gamifikasi RPG:** Kumpulkan sesi latihan untuk naik level dari *Couch Potato* menjadi *Greek God*!

## Tech Stack
- **Frontend:** HTML5, CSS3, Alpine.js (Tidak butuh *build tools*).
- **Backend:** Python FastAPI, SQLite.
- **AI Engine:** llama.cpp (Vulkan Backend).
- **Model:** Qwen2.5-1.5B-Instruct (di-finetune menggunakan LoRA).

## Instalasi

1. **Clone repository:**
   ```bash
   git clone https://github.com/USERNAME/gymmate-ai.git
   cd gymmate-ai
   ```

2. **Install dependensi Python:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Download Model (Qwen 1.5B GGUF):**
   - Letakkan file `.gguf` di dalam folder `models/`.

4. **Jalankan Server AI (llama.cpp):**
   ```bash
   ./llama.cpp/build/bin/llama-server -m models/Qwen2.5-1.5B-Instruct.Q4_K_M.gguf -ngl 99 -c 2048 --port 8080
   ```

5. **Jalankan Backend FastAPI:**
   ```bash
   cd src/backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

Buka `http://localhost:8000` di *browser* Anda!

## Disclaimer Privasi
File `.gitignore` telah diatur untuk mengecualikan `gymmate.db` dan `dataset/`. Data beban angkatan Anda aman dan tidak akan ter- *upload* secara publik.

---
*Dibuat untuk Tugas Besar - 2026*
