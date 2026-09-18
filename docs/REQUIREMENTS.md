# GymMate AI — Product Requirements Document

> **Versi:** 0.2.0  
> **Tanggal:** 2026-09-18  
> **Status:** Validated (evidence-based review completed)  
> **Author:** ambatron  
> **Tujuan:** Eksperimen pribadi + tugas besar kuliah (bukan produk komersial)

---

## Daftar Isi

- [1. Ringkasan Eksekutif](#1-ringkasan-eksekutif)
- [2. Problem Statement](#2-problem-statement)
- [3. Solusi](#3-solusi)
- [4. Target User](#4-target-user)
- [5. Arsitektur Sistem](#5-arsitektur-sistem)
- [6. Peran AI — Parsing Teks Bebas](#6-peran-ai--parsing-teks-bebas)
- [7. Fitur Core](#7-fitur-core)
- [8. Non-Fitur (Explicit Exclusion)](#8-non-fitur-explicit-exclusion)
- [9. Skema Data](#9-skema-data)
- [10. API Design](#10-api-design)
- [11. Rule Engine — Progressive Overload](#11-rule-engine--progressive-overload)
- [12. Frontend Design](#12-frontend-design)
- [13. Dataset Strategy](#13-dataset-strategy)
- [14. Competitive Analysis](#14-competitive-analysis)
- [15. Hardware & Constraint](#15-hardware--constraint)
- [16. Roadmap](#16-roadmap)
- [17. Risiko & Mitigasi](#17-risiko--mitigasi)
- [18. Success Metrics](#18-success-metrics)
- [19. Glosarium](#19-glosarium)
- [20. Referensi](#20-referensi)

---

## 1. Ringkasan Eksekutif

**GymMate AI** adalah aplikasi logger gym yang menerima input teks bebas (bahasa campur Indonesia-Inggris, typo, singkatan, ambigu) dan menggunakan Small Language Model (SLM) on-premise untuk mem-parsing teks tersebut menjadi data terstruktur. Data yang sudah terstruktur disimpan di SQLite, lalu digunakan oleh rule engine deterministik untuk memberikan rekomendasi progressive overload.

**Satu kalimat:**  
> *Nulis bebas kayak di Notes, tapi datanya bisa di-query dan kasih rekomendasi beban.*

---

## 2. Problem Statement

### 2.1 Masalah Inti

Orang gym (terutama pemula-intermediate) **malas mencatat latihan** karena:

| Pain Point | Detail |
|---|---|
| **Input ribet** | App existing (Strong, JEFIT, dll) maksa dropdown, pilih exercise dari list panjang, input set/rep/weight satu-satu |
| **Konteks switching** | Lagi ngos-ngosan habis set, harus navigasi UI yang complex |
| **Bahasa campur** | User Indonesia nulis "bench press 60kg 8x3" atau "bp 60 8rm 3set", app existing gak ngerti |
| **Friction = skip** | Ujung-ujungnya berhenti nyatat setelah 2 minggu |

### 2.2 Kenapa Existing App Gagal

| App | Kelebihan | Gagal di... |
|---|---|---|
| Strong | UI bagus, PR tracking | Input per-set manual, gak terima free text |
| JEFIT | Database exercise lengkap | Terlalu banyak fitur, bloated |
| Notes/Google Keep | Bebas nulis | Data gak terstruktur, gak bisa query/analisis |
| ChatGPT/Gemini | Bisa parsing text | Butuh internet, latency, gak persist data |

### 2.3 Insight Kunci

User **sudah punya habit nulis** (di Notes, WA ke diri sendiri). Masalahnya bukan motivasi nyatat — masalahnya **tool-nya yang gak cocok**. Kita butuh app yang nerima cara nulis mereka apa adanya, bukan maksa mereka nulis format tertentu.

---

## 3. Solusi

### 3.1 Flow Utama

```
User nulis bebas ──→ AI parsing ──→ JSON terstruktur ──→ Konfirmasi ──→ Simpan DB
                                                                           │
                                                          Rule engine ◄────┘
                                                              │
                                                    Rekomendasi beban
```

### 3.2 Contoh Input → Output

**Input (teks bebas):**
```
chest day
bench press 60kg 8x3, set terakhir gagal rep ke-7
incline db press 16kg each 10x3
pec deck 25kg 12x3
cable fly 10kg 15x2
capek bgt hari ini kurang tidur
```

**Output (JSON terstruktur):**
```json
{
  "date": "2026-09-18",
  "sessions": [
    {
      "muscle_group": "chest",
      "exercises": [
        {
          "name": "bench press",
          "canonical": "barbell_bench_press",
          "sets": [
            {"weight_kg": 60, "reps": 8, "rpe": null, "note": null},
            {"weight_kg": 60, "reps": 8, "rpe": null, "note": null},
            {"weight_kg": 60, "reps": 7, "rpe": 10, "note": "gagal rep ke-7"}
          ]
        },
        {
          "name": "incline db press",
          "canonical": "incline_dumbbell_press",
          "sets": [
            {"weight_kg": 16, "reps": 10, "rpe": null, "note": null, "per_hand": true},
            {"weight_kg": 16, "reps": 10, "rpe": null, "note": null, "per_hand": true},
            {"weight_kg": 16, "reps": 10, "rpe": null, "note": null, "per_hand": true}
          ]
        },
        {
          "name": "pec deck",
          "canonical": "pec_deck",
          "sets": [
            {"weight_kg": 25, "reps": 12, "rpe": null, "note": null},
            {"weight_kg": 25, "reps": 12, "rpe": null, "note": null},
            {"weight_kg": 25, "reps": 12, "rpe": null, "note": null}
          ]
        },
        {
          "name": "cable fly",
          "canonical": "cable_fly",
          "sets": [
            {"weight_kg": 10, "reps": 15, "rpe": null, "note": null},
            {"weight_kg": 10, "reps": 15, "rpe": null, "note": null}
          ]
        }
      ]
    }
  ],
  "session_note": "capek bgt hari ini kurang tidur"
}
```

### 3.3 Prinsip Desain

| Prinsip | Penjelasan |
|---|---|
| **Free-text first** | Textbox besar di tengah, bukan form. User nulis kayak di Notes |
| **AI hanya parsing** | AI tidak memberi saran, motivasi, atau coaching. Hanya konversi teks → JSON |
| **Confirm before save** | Hasil parsing ditampilkan, user bisa edit sebelum disimpan |
| **Offline-capable** | Semua berjalan di jaringan lokal, tidak butuh internet |
| **Ringan** | Frontend < 100KB, load < 1 detik di HP kentang |

---

## 4. Target User

### 4.1 Primary Persona

**Ardi, 24 tahun, gym-goer intermediate**
- Gym 4-5x seminggu, program PPL
- Pakai HP Infinix RAM 4GB
- Males buka app Strong karena harus pilih exercise dari dropdown
- Biasa nyatat di Notes dengan format sendiri yang tidak konsisten
- Mau tracking progress tapi gak mau ribet
- Bahasa sehari-hari campur Indonesia-Inggris

### 4.2 Secondary Persona

**Dito, 28 tahun, gym-goer pemula**
- Baru 3 bulan gym, belum hafal nama exercise
- Nulis "yang narik ke bawah pake kabel" bukan "lat pulldown"
- Butuh rekomendasi kapan naikkin beban

### 4.3 Anti-Persona (BUKAN untuk mereka)

- Powerlifter competitive yang butuh periodisasi mikro
- Personal trainer yang manage banyak client
- User yang mau tracking nutrisi/kalori
- User yang mau fitur sosial/komunitas

---

## 5. Arsitektur Sistem

### 5.1 Deployment: Server Lokal (Primary)

```
┌─────────────────────┐         WiFi          ┌──────────────────────────────┐
│   HP User (Infinix)  │ ◄──────────────────► │   Laptop Acer Aspire 5       │
│                       │    HTTP/JSON          │                              │
│  Browser              │                       │  ┌──────────────────────┐    │
│  └─ Alpine.js SPA     │                       │  │ FastAPI Server       │    │
│     (< 100KB)         │                       │  │  ├─ /api/parse       │    │
│                       │                       │  │  ├─ /api/logs        │    │
│                       │                       │  │  ├─ /api/schedule    │    │
│                       │                       │  │  ├─ /api/progress    │    │
│                       │                       │  │  └─ /api/recommend   │    │
│                       │                       │  └──────────┬───────────┘    │
│                       │                       │             │                │
│                       │                       │  ┌──────────▼───────────┐    │
│                       │                       │  │ llama.cpp (CUDA)     │    │
│                       │                       │  │ Qwen2.5-1.5B Q4_K_M │    │
│                       │                       │  │ + GBNF grammar       │    │
│                       │                       │  └──────────────────────┘    │
│                       │                       │                              │
│                       │                       │  ┌──────────────────────┐    │
│                       │                       │  │ SQLite               │    │
│                       │                       │  │ gymmate.db           │    │
│                       │                       │  └──────────────────────┘    │
│                       │                       │                              │
│                       │                       │  ┌──────────────────────┐    │
│                       │                       │  │ Rule Engine (Python) │    │
│                       │                       │  │ Progressive overload │    │
│                       │                       │  │ 1RM calculator       │    │
│                       │                       │  └──────────────────────┘    │
│                       │                       │                              │
│                       │                       │  RAM: 8GB | GPU: MX350 2GB  │
└─────────────────────┘                        └──────────────────────────────┘
```

### 5.2 Fallback Ladder

Jika primary deployment gagal atau tidak tersedia:

| Priority | Mode | Kondisi | Trade-off |
|---|---|---|---|
| 🥇 1 | **SLM on-device HP** | HP cukup kuat (RAM ≥ 6GB, Snapdragon 7xx+) | Ideal, tapi Infinix user terlalu lemot |
| 🥈 2 | **Server lokal (laptop)** | HP & laptop di WiFi yang sama | Butuh laptop nyala, tapi fast & private |
| 🥉 3 | **Browser WebGPU** | Browser support WebGPU, GPU cukup | Masih eksperimental, model harus download |
| 4 | **Cloud API** | Semua di atas gagal | Butuh internet, ada biaya, privacy concern |

### 5.3 Tech Stack

| Layer | Teknologi | Alasan |
|---|---|---|
| **Frontend** | HTML + Alpine.js + minimal CSS | Paling ringan, gak perlu build step, < 100KB |
| **Backend** | FastAPI (Python 3.11+) | Async, ringan, typing bagus, ecosystem ML Python |
| **AI Runtime** | llama.cpp + python binding | CUDA support MX350, GBNF grammar constraint |
| **Model** | Qwen2.5-1.5B-Instruct Q4_K_M | Kecil (< 1GB), multilingual (ZH/EN/ID passable), instruction-tuned |
| **Fine-tune** | LoRA via Unsloth di Google Colab | Free GPU T4/A100, LoRA hemat memory |
| **Database** | SQLite | Zero config, single file, cukup untuk single user |
| **Rule Engine** | Python (pure logic) | Deterministic, testable, no ML needed |

### 5.4 Kenapa Bukan...

| Alternatif | Alasan ditolak |
|---|---|
| React/Vue | Overkill untuk 4 tab, tambah bundle size |
| PostgreSQL/MySQL | Butuh server terpisah, overkill single user |
| Ollama | Extra abstraction layer, mending langsung llama.cpp |
| GPT-4/Gemini API | Butuh internet, biaya recurring, privacy |
| TensorFlow Lite | Lebih susah setup untuk text generation |

---

## 6. Peran AI — Parsing Teks Bebas

### 6.1 Scope AI (Yang DILAKUKAN)

| Task | Contoh |
|---|---|
| **Parsing teks → JSON** | "bp 60 8x3" → structured JSON |
| **Normalisasi nama exercise** | "squad" → "squat", "lat pull" → "lat_pulldown" |
| **Resolve singkatan** | "8x3" → 8 reps × 3 sets |
| **Resolve satuan** | "35k" → 35 kg, "each" → per_hand: true |
| **Resolve ambiguitas** | "16kg 10x2, 12x1" → 2 sets @10rep + 1 set @12rep |
| **Deteksi muscle group** | dari konteks exercise, infer "chest", "back", dll |
| **Pisahkan session note** | "capek bgt" → session_note, bukan exercise |
| **Handle campur bahasa** | "bench press 60 kilo 8 kali 3 set" → sama dengan "bp 60kg 8x3" |

### 6.2 Scope AI (Yang TIDAK DILAKUKAN)

| Task | Dikerjakan oleh |
|---|---|
| Rekomendasi beban | Rule engine (Python) |
| Query history | SQL query |
| Body weight trend | SQL + simple math |
| Jadwal latihan | Static config + SQL |
| Motivational coaching | ❌ Tidak ada |
| Form check | ❌ Tidak ada |
| Nutrisi | ❌ Tidak ada |

### 6.3 Model Selection

**Qwen2.5-1.5B-Instruct Q4_K_M**

| Kriteria | Spec |
|---|---|
| Parameter | 1.5B |
| Quantization | Q4_K_M (~986 MB) |
| Architecture | GQA (2 KV heads) → KV cache sangat kecil |
| Context length | 2048 tokens (cukup untuk 1 sesi gym, hemat VRAM) |
| Language | Multilingual — 18T tokens, 29+ bahasa termasuk Indonesian |
| License | Apache 2.0 |
| VRAM total (model + KV + buffer) | ~1.26 GB @ ctx 2048 (muat di MX350 2GB, sisa ~785 MB) |
| Inference speed (MX350, validated) | ~32-38 tok/s generation, ~350-550 tok/s prompt processing |
| Time to first token (512 prompt) | ~0.9-1.4 detik |

**Kenapa Qwen 1.5B (validated):**
- GQA dengan 2 KV heads → VRAM footprint sangat kecil, muat di 2GB dengan margin 38%
- Pre-trained 18T tokens termasuk Indonesian + explicit code-switching training
- IndoMMLU benchmark: significant gains vs Qwen2 di Indonesian exam tasks
- Tokenizer 151K vocabulary, efisien untuk Bahasa Indonesia (low fragmentation)
- Basis banyak Indonesian fine-tune (e.g. `Azzindani/Qwen2.5_1.5B_IT_ID_Legal`)
- Setelah LoRA fine-tune, akurasi parsing cukup untuk domain spesifik
- Caveat: model 1.5B bisa drift ke English di response panjang → fixable dengan fine-tune

### 6.4 GBNF Grammar Constraint

GBNF grammar di llama.cpp mem-mask logits token invalid ke -∞ saat sampling, memaksa output mengikuti struktur yang didefinisikan. Namun berdasarkan research, **GBNF bukan jaminan 100%** — perlu defense-in-depth:

**Known failure cases & mitigasi:**

| Failure Case | Mitigasi untuk GymMate |
|---|---|
| Truncation (hit max_tokens sebelum JSON selesai) | Set `n_predict` generous (2048+), output gym log biasanya < 800 token |
| Fail-open bug (grammar gagal compile → output unconstrained) | Validate grammar saat server start, post-validate setiap output |
| UTF-8 multi-byte mismatch | Output GymMate mostly ASCII (exercise names, angka), risiko rendah |
| String escaping (newline literal dalam JSON string) | Grammar harus explicit handle escape: `[^"\\\\]*` bukan `[^"]*` |
| Infinite array loop | Batasi max exercises per session, set timeout |
| Model off-distribution (mau nulis preamble tapi grammar paksa `{`) | Prompt harus align — instruksikan raw JSON tanpa preamble |

**Strategi defense-in-depth:**
```
GBNF constraint (structural) → json.loads() validation → schema check → retry 1x → fallback manual input
```

**Grammar definition:**

```gbnf
root        ::= "{" ws "\"date\":" ws date "," ws "\"sessions\":" ws sessions "," ws "\"session_note\":" ws (string | "null") ws "}"

date        ::= "\"" [0-9]{4} "-" [0-9]{2} "-" [0-9]{2} "\""

sessions    ::= "[" ws session ("," ws session)* ws "]"

session     ::= "{" ws "\"muscle_group\":" ws muscle_group "," ws "\"exercises\":" ws exercises ws "}"

muscle_group ::= "\"" ("chest" | "back" | "shoulders" | "legs" | "arms" | "core" | "full_body" | "cardio") "\""

exercises   ::= "[" ws exercise ("," ws exercise)* ws "]"

exercise    ::= "{" ws "\"name\":" ws string "," ws "\"canonical\":" ws string "," ws "\"sets\":" ws sets ws "}"

sets        ::= "[" ws set ("," ws set)* ws "]"

set         ::= "{" ws "\"weight_kg\":" ws number "," ws "\"reps\":" ws integer "," ws "\"rpe\":" ws (number | "null") "," ws "\"note\":" ws (string | "null") ("," ws "\"per_hand\":" ws boolean)? ws "}"

string      ::= "\"" [^"\\]* "\""
number      ::= "-"? [0-9]+ ("." [0-9]+)?
integer     ::= [0-9]+
boolean     ::= ("true" | "false")
ws          ::= [ \t\n\r]*
```

### 6.5 Prompt Template

```
<|im_start|>system
Kamu adalah parser log gym. Tugas: konversi teks bebas log latihan menjadi JSON terstruktur.
Aturan:
- "8x3" = 8 reps × 3 sets
- "each" atau "per tangan" = per_hand: true
- "bar only" atau "bar aja" = 20kg
- "gagal" atau "failure" = note + RPE 10
- "35k" = 35 kg
- Normalisasi nama exercise ke canonical form (snake_case)
- Pisahkan catatan umum ke session_note
<|im_end|>
<|im_start|>user
{user_input}
<|im_end|>
<|im_start|>assistant
```

### 6.6 Fine-tuning Strategy (Validated)

| Aspek | Detail |
|---|---|
| **Method** | QLoRA (4-bit) via Unsloth |
| **Platform** | Google Colab free T4 (15-16 GB VRAM, lebih dari cukup) |
| **Base model** | `unsloth/Qwen2.5-1.5B-Instruct-bnb-4bit` |
| **Dataset size target** | 200-500 pairs (raw text → JSON). 100-200 high-quality > 2000 noisy |
| **Epoch** | 1-3 max (> 3 epoch di < 500 samples = overfitting) |
| **LoRA rank** | r=8 atau r=16 (jangan r=64+, catastrophic forgetting) |
| **LoRA alpha** | 16 atau 32 |
| **LoRA dropout** | 0.05-0.1 |
| **Target modules** | `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj` |
| **Learning rate** | 2e-4 (turunkan ke 1.5e-4 kalau loss instabil) |
| **Optimizer** | adamw_8bit |
| **LR scheduler** | cosine dengan warmup 5-10 steps |
| **Batch size** | 2 + gradient_accumulation_steps=4 (effective batch 8) |
| **Training time** | ~3-10 menit di T4 untuk 500 samples |
| **VRAM usage** | ~4-5.5 GB (QLoRA) → sisa 10+ GB headroom di T4 |
| **Validation** | 10% held-out, metric = exact JSON match + field-level accuracy |
| **Export** | `model.save_pretrained_gguf(..., quantization_method="q4_k_m")` — 1 line |

**Tips penting (dari research):**

```python
# 1. Chat template — WAJIB pakai yang official
from unsloth.chat_templates import get_chat_template
tokenizer = get_chat_template(tokenizer, chat_template="qwen-2.5")

# 2. Train on responses only — tanpa ini model memorize prompt
from unsloth.chat_templates import train_on_responses_only
trainer = train_on_responses_only(
    trainer,
    instruction_part="<|im_start|>user\n",
    response_part="<|im_start|>assistant\n",
)

# 3. EOS token — pastikan benar, kalau salah model generate infinite
tokenizer.eos_token = "<|im_end|>"

# 4. Export GGUF — single file, no sharding bug untuk 1.5B
model.save_pretrained_gguf("gymmate-qwen-1.5b", tokenizer, quantization_method="q4_k_m")
```

### 6.7 Evaluation Metrics

| Metric | Target | Cara Ukur |
|---|---|---|
| **JSON validity** | > 99% | GBNF + post-validation + retry. Bukan 100% karena edge cases (lihat §6.4) |
| **Exercise name accuracy** | ≥ 95% | canonical name match vs gold |
| **Set/rep/weight accuracy** | ≥ 98% | exact match per field |
| **Muscle group accuracy** | ≥ 90% | match vs gold |
| **Time to first token** | < 1.5 detik | MX350 prompt processing ~350-550 tok/s |
| **Total generation (3-5 exercise)** | 12-25 detik | ~32-38 tok/s × ~400-800 output tokens. Tolerable untuk personal use + streaming |
| **Latency (user-perceived)** | < 2 detik | streaming first token |

---

## 7. Fitur Core

### 7.1 Tab Jadwal (Schedule)

**Tujuan:** User buka app, langsung tau hari ini latihan apa + beban yang harus diangkat.

| Element | Detail |
|---|---|
| Hari & muscle group | "Senin — Chest + Triceps" (dari konfigurasi jadwal user) |
| Exercise list | Daftar exercise yang biasa dilakukan di hari itu |
| Last weight & reps | Beban terakhir per exercise |
| Recommended weight | Dari rule engine (jika eligible naik beban) |
| Notes penting | Misal: "minggu lalu gagal di set 3 bench press" |
| Quick log button | Langsung buka Tab Log dengan context hari ini |

**Data source:** SQLite query last session untuk muscle group yang sama.

### 7.2 Tab Log (Core Feature)

**Tujuan:** Input utama. Textbox besar, tulis bebas, submit, konfirmasi, simpan.

**Flow detail:**

```
┌──────────────────────────────────────┐
│  📅 2026-09-18 (Senin)               │
│                                      │
│  ┌──────────────────────────────────┐ │
│  │                                  │ │
│  │  bench press 60kg 8x3            │ │
│  │  set terakhir gagal rep 7        │ │
│  │  incline db 16 each 10x3        │ │
│  │  pec deck 25 12x3               │ │
│  │  capek bgt kurang tidur          │ │
│  │                                  │ │
│  └──────────────────────────────────┘ │
│                                      │
│  [ 🤖 Parse & Preview ]              │
│                                      │
└──────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────┐
│  PREVIEW HASIL PARSING               │
│                                      │
│  ✅ Bench Press (Barbell)            │
│     60kg × 8 × 8 × 7(fail)          │
│                                      │
│  ✅ Incline DB Press                 │
│     16kg/hand × 10 × 10 × 10        │
│                                      │
│  ✅ Pec Deck                         │
│     25kg × 12 × 12 × 12             │
│                                      │
│  📝 Note: capek bgt kurang tidur     │
│                                      │
│  [ ✏️ Edit ]  [ ✅ Simpan ]           │
└──────────────────────────────────────┘
```

**Interaksi:**
- User bisa edit hasil parsing sebelum simpan (inline edit per field)
- Jika parsing salah, user koreksi → data koreksi disimpan untuk retraining
- Timestamp otomatis
- Support multiple session (pagi + sore)

### 7.3 Tab History

**Tujuan:** Lihat riwayat per exercise, tracking progress.

| Element | Detail |
|---|---|
| Search/filter exercise | Ketik nama exercise, autocomplete |
| Per-exercise history | Tabel: tanggal, weight, reps, sets, estimated 1RM |
| Grafik sederhana | Line chart: estimated 1RM over time per exercise |
| Session log | Klik tanggal → lihat full session log hari itu |

**Grafik library:** Chart.js (lightweight, ~60KB gzipped) atau uPlot (~35KB).

### 7.4 Tab Progress

**Tujuan:** Overview progress keseluruhan.

| Element | Detail |
|---|---|
| Body weight tracker | Input manual, line chart over time |
| Volume mingguan | Total volume (weight × reps × sets) per muscle group per minggu |
| PR board | Personal record per exercise (heaviest 1RM) |
| Streak | Berapa hari berturut-turut latihan |
| Deload alert | Kalau rule engine suggest deload |

### 7.5 Fitur Cross-Tab

| Fitur | Detail |
|---|---|
| **Date picker** | Default hari ini, bisa pilih tanggal lain untuk log retroaktif |
| **Dark mode** | Default dark (gym biasanya gelap), toggle available |
| **Export** | CSV/JSON export seluruh data (Pro feature) |
| **Backup/Restore** | Download/upload SQLite file |
| **PWA** | Installable, offline-capable (service worker cache static assets) |

---

## 8. Non-Fitur (Explicit Exclusion)

Berikut hal-hal yang **sengaja TIDAK dibuat** untuk menjaga fokus:

| Non-Fitur | Alasan |
|---|---|
| Tracking nutrisi/kalori | Scope berbeda, banyak app dedicated (MyFitnessPal) |
| Video form check | Butuh computer vision, scope terlalu besar |
| Fitur sosial / leaderboard | Bukan core value prop |
| Wearable integration | Complexity tinggi, user target gak punya smartwatch |
| Chatbot umum / AI coach | AI hanya untuk parsing, bukan conversational |
| Multi-user support | V1 single user, multi-user bisa later |
| Exercise database / tutorial | User sudah tau exercise-nya, mereka cuma males nyatat |
| Periodisasi otomatis | Terlalu opinionated, user beda-beda program |
| Rest timer | HP sudah punya timer bawaan |
| Plate calculator | Nice-to-have, bukan core. Mungkin V2 |

---

## 9. Skema Data

### 9.1 Database Schema (SQLite)

```sql
-- Canonical exercise reference
CREATE TABLE exercises (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_name  TEXT UNIQUE NOT NULL,     -- e.g. "barbell_bench_press"
    display_name    TEXT NOT NULL,            -- e.g. "Bench Press (Barbell)"
    muscle_group    TEXT NOT NULL,            -- e.g. "chest"
    equipment       TEXT,                     -- e.g. "barbell", "dumbbell", "cable", "machine"
    is_compound     BOOLEAN DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alias / nickname mapping
CREATE TABLE exercise_aliases (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    alias           TEXT UNIQUE NOT NULL,     -- e.g. "bp", "bench", "bench press"
    exercise_id     INTEGER NOT NULL REFERENCES exercises(id)
);

-- Workout session (satu hari bisa > 1 session)
CREATE TABLE sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            DATE NOT NULL,            -- e.g. "2026-09-18"
    muscle_group    TEXT,                      -- primary muscle group
    raw_input       TEXT,                      -- teks asli user (untuk retraining)
    parsed_json     TEXT,                      -- hasil parsing AI (full JSON)
    session_note    TEXT,                      -- catatan umum session
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual exercise log
CREATE TABLE exercise_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    exercise_id     INTEGER NOT NULL REFERENCES exercises(id),
    order_index     INTEGER NOT NULL,         -- urutan exercise dalam session
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual set
CREATE TABLE sets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_log_id INTEGER NOT NULL REFERENCES exercise_logs(id) ON DELETE CASCADE,
    set_number      INTEGER NOT NULL,
    weight_kg       REAL NOT NULL,
    reps            INTEGER NOT NULL,
    rpe             REAL,                     -- Rate of Perceived Exertion (1-10)
    per_hand        BOOLEAN DEFAULT 0,        -- true = weight is per hand/side
    is_warmup       BOOLEAN DEFAULT 0,
    is_dropset      BOOLEAN DEFAULT 0,
    note            TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Body weight tracking
CREATE TABLE body_weight (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            DATE UNIQUE NOT NULL,
    weight_kg       REAL NOT NULL,
    note            TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User schedule/split configuration
CREATE TABLE schedule (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week     INTEGER NOT NULL,         -- 0=Monday, 6=Sunday
    muscle_groups   TEXT NOT NULL,            -- comma-separated: "chest,triceps"
    label           TEXT,                     -- e.g. "Push Day"
    is_rest_day     BOOLEAN DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User corrections for retraining
CREATE TABLE corrections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_input       TEXT NOT NULL,            -- teks asli
    ai_output       TEXT NOT NULL,            -- JSON hasil AI (yang salah)
    corrected_output TEXT NOT NULL,           -- JSON yang dikoreksi user
    correction_type TEXT,                     -- "exercise_name", "weight", "reps", dll
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_sessions_date ON sessions(date);
CREATE INDEX idx_exercise_logs_session ON exercise_logs(session_id);
CREATE INDEX idx_exercise_logs_exercise ON exercise_logs(exercise_id);
CREATE INDEX idx_sets_exercise_log ON sets(exercise_log_id);
CREATE INDEX idx_body_weight_date ON body_weight(date);
CREATE INDEX idx_exercise_aliases_alias ON exercise_aliases(alias);
```

### 9.2 JSON Schema (AI Output)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GymMate AI Parse Result",
  "type": "object",
  "required": ["date", "sessions", "session_note"],
  "properties": {
    "date": {
      "type": "string",
      "format": "date",
      "description": "Tanggal sesi latihan (YYYY-MM-DD)"
    },
    "sessions": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["muscle_group", "exercises"],
        "properties": {
          "muscle_group": {
            "type": "string",
            "enum": ["chest", "back", "shoulders", "legs", "arms", "core", "full_body", "cardio"]
          },
          "exercises": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "required": ["name", "canonical", "sets"],
              "properties": {
                "name": {
                  "type": "string",
                  "description": "Nama exercise seperti yang ditulis user"
                },
                "canonical": {
                  "type": "string",
                  "pattern": "^[a-z_]+$",
                  "description": "Nama canonical (snake_case)"
                },
                "sets": {
                  "type": "array",
                  "minItems": 1,
                  "items": {
                    "type": "object",
                    "required": ["weight_kg", "reps"],
                    "properties": {
                      "weight_kg": { "type": "number", "minimum": 0 },
                      "reps": { "type": "integer", "minimum": 1 },
                      "rpe": { "type": ["number", "null"], "minimum": 1, "maximum": 10 },
                      "note": { "type": ["string", "null"] },
                      "per_hand": { "type": "boolean", "default": false },
                      "is_warmup": { "type": "boolean", "default": false },
                      "is_dropset": { "type": "boolean", "default": false }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "session_note": {
      "type": ["string", "null"],
      "description": "Catatan umum sesi (bukan per exercise)"
    }
  }
}
```

### 9.3 Canonical Exercise List (Seed Data)

Daftar exercise awal yang di-seed ke database. Bisa ditambah user.

<details>
<summary>Lihat daftar lengkap (klik expand)</summary>

**Chest:**
| Canonical | Display | Equipment | Compound |
|---|---|---|---|
| barbell_bench_press | Bench Press (Barbell) | barbell | ✅ |
| dumbbell_bench_press | Bench Press (Dumbbell) | dumbbell | ✅ |
| incline_barbell_bench_press | Incline Bench Press (Barbell) | barbell | ✅ |
| incline_dumbbell_press | Incline DB Press | dumbbell | ✅ |
| decline_bench_press | Decline Bench Press | barbell | ✅ |
| pec_deck | Pec Deck | machine | ❌ |
| cable_fly | Cable Fly | cable | ❌ |
| chest_dip | Chest Dip | bodyweight | ✅ |
| push_up | Push Up | bodyweight | ✅ |

**Back:**
| Canonical | Display | Equipment | Compound |
|---|---|---|---|
| barbell_row | Barbell Row | barbell | ✅ |
| dumbbell_row | Dumbbell Row | dumbbell | ✅ |
| lat_pulldown | Lat Pulldown | cable | ✅ |
| seated_cable_row | Seated Cable Row | cable | ✅ |
| pull_up | Pull Up | bodyweight | ✅ |
| chin_up | Chin Up | bodyweight | ✅ |
| t_bar_row | T-Bar Row | barbell | ✅ |
| face_pull | Face Pull | cable | ❌ |
| deadlift | Deadlift | barbell | ✅ |

**Shoulders:**
| Canonical | Display | Equipment | Compound |
|---|---|---|---|
| overhead_press | Overhead Press (Barbell) | barbell | ✅ |
| dumbbell_shoulder_press | Shoulder Press (Dumbbell) | dumbbell | ✅ |
| lateral_raise | Lateral Raise | dumbbell | ❌ |
| front_raise | Front Raise | dumbbell | ❌ |
| reverse_fly | Reverse Fly | dumbbell | ❌ |
| cable_lateral_raise | Cable Lateral Raise | cable | ❌ |
| arnold_press | Arnold Press | dumbbell | ✅ |

**Legs:**
| Canonical | Display | Equipment | Compound |
|---|---|---|---|
| barbell_squat | Squat (Barbell) | barbell | ✅ |
| leg_press | Leg Press | machine | ✅ |
| romanian_deadlift | Romanian Deadlift | barbell | ✅ |
| leg_extension | Leg Extension | machine | ❌ |
| leg_curl | Leg Curl | machine | ❌ |
| calf_raise | Calf Raise | machine | ❌ |
| bulgarian_split_squat | Bulgarian Split Squat | dumbbell | ✅ |
| hip_thrust | Hip Thrust | barbell | ✅ |
| goblet_squat | Goblet Squat | dumbbell | ✅ |

**Arms:**
| Canonical | Display | Equipment | Compound |
|---|---|---|---|
| barbell_curl | Barbell Curl | barbell | ❌ |
| dumbbell_curl | Dumbbell Curl | dumbbell | ❌ |
| hammer_curl | Hammer Curl | dumbbell | ❌ |
| cable_curl | Cable Curl | cable | ❌ |
| tricep_pushdown | Tricep Pushdown | cable | ❌ |
| skull_crusher | Skull Crusher | barbell | ❌ |
| overhead_tricep_extension | Overhead Tricep Extension | dumbbell | ❌ |
| dip | Dip (Tricep) | bodyweight | ✅ |

**Core:**
| Canonical | Display | Equipment | Compound |
|---|---|---|---|
| plank | Plank | bodyweight | ❌ |
| hanging_leg_raise | Hanging Leg Raise | bodyweight | ❌ |
| cable_crunch | Cable Crunch | cable | ❌ |
| ab_wheel | Ab Wheel | bodyweight | ❌ |
| russian_twist | Russian Twist | bodyweight | ❌ |

</details>

---

## 10. API Design

### 10.1 Endpoints

Base URL: `http://<laptop-ip>:8000/api/v1`

#### Parsing

```
POST /parse
Content-Type: application/json

Request:
{
  "raw_text": "bench press 60kg 8x3\nincline db 16 each 10x3",
  "date": "2026-09-18"                          // optional, default today
}

Response:
{
  "success": true,
  "parsed": { ... },                              // JSON sesuai skema §9.2
  "confidence": 0.92,                             // overall confidence
  "warnings": [                                   // hal yang perlu user cek
    {"field": "exercises[1].canonical", "message": "Apakah 'incline db' maksudnya incline_dumbbell_press?"}
  ],
  "latency_ms": 2340
}
```

#### Logs

```
POST /logs
Save parsed + confirmed workout log

GET /logs?date=2026-09-18
Get logs by date

GET /logs?from=2026-09-01&to=2026-09-18
Get logs by date range

DELETE /logs/{session_id}
Delete a session
```

#### Exercise History

```
GET /exercises/{canonical_name}/history?limit=30
Get history for specific exercise

Response:
{
  "exercise": "barbell_bench_press",
  "history": [
    {
      "date": "2026-09-18",
      "sets": [...],
      "estimated_1rm": 75.0,
      "total_volume": 1440
    }
  ]
}
```

#### Schedule

```
GET /schedule
Get current week schedule

GET /schedule/today
Get today's workout plan with recommendations

PUT /schedule
Update schedule configuration
```

#### Progress

```
GET /progress/body-weight?from=2026-01-01
Get body weight history

POST /progress/body-weight
Log body weight

GET /progress/volume?from=2026-09-01&group_by=week
Get volume trends

GET /progress/prs
Get all personal records
```

#### Recommendations

```
GET /recommend/{canonical_name}
Get progressive overload recommendation for exercise

Response:
{
  "exercise": "barbell_bench_press",
  "last_performance": {"weight_kg": 60, "reps": 8, "sets": 3, "rpe_avg": 8.5},
  "recommendation": {
    "action": "maintain",                        // "increase" | "maintain" | "deload"
    "suggested_weight_kg": 60,
    "reason": "RPE rata-rata > 8, maintain beban dulu sampai RPE ≤ 8"
  },
  "estimated_1rm": 75.0,
  "pr": {"weight_kg": 62.5, "date": "2026-09-10"}
}
```

#### Corrections (untuk retraining)

```
POST /corrections
Save user correction for retraining dataset

GET /corrections?limit=100
Get all corrections for export
```

### 10.2 Error Handling

```json
{
  "success": false,
  "error": {
    "code": "PARSE_FAILED",
    "message": "Model gagal menghasilkan JSON valid setelah 3 retry",
    "details": "..."
  }
}
```

| Error Code | HTTP Status | Keterangan |
|---|---|---|
| `PARSE_FAILED` | 500 | Model gagal parse (seharusnya jarang karena GBNF) |
| `PARSE_TIMEOUT` | 504 | Inference > 10 detik |
| `INVALID_INPUT` | 400 | Input kosong atau terlalu panjang (> 2000 chars) |
| `NOT_FOUND` | 404 | Resource tidak ditemukan |
| `MODEL_NOT_LOADED` | 503 | llama.cpp belum siap |

---

## 11. Rule Engine — Progressive Overload

### 11.1 Prinsip

Rule engine 100% deterministik (Python, bukan AI). Logic sederhana dan transparan.

### 11.2 Rumus 1RM

```
Estimated 1RM = weight × (1 + reps / 30)
```

Contoh: 60kg × 8 reps → 60 × (1 + 8/30) = 60 × 1.267 = 76 kg e1RM

### 11.3 Rules

```python
# Pseudocode rule engine

def recommend(exercise: Exercise, history: List[SessionLog]) -> Recommendation:
    last = get_last_session(exercise, history)
    
    if last is None:
        return Recommendation(action="no_data", reason="Belum ada data")
    
    avg_rpe = mean([s.rpe for s in last.sets if s.rpe is not None])
    all_reps_hit = all(s.reps >= target_reps for s in last.sets)
    had_failure = any(s.note and "gagal" in s.note.lower() for s in last.sets)
    
    # Cek consecutive failure
    consecutive_fails = count_consecutive_failures(exercise, history)
    
    if consecutive_fails >= 3:
        return Recommendation(
            action="deload",
            suggested_weight_kg=last.weight_kg * 0.9,  # -10%
            reason=f"Gagal 3 sesi berturut-turut, deload 10%"
        )
    
    if had_failure or (avg_rpe and avg_rpe > 9):
        return Recommendation(
            action="maintain",
            suggested_weight_kg=last.weight_kg,
            reason="Ada failure / RPE > 9, maintain dulu"
        )
    
    if all_reps_hit and (avg_rpe is None or avg_rpe <= 8):
        increment = get_increment(exercise)  # upper=2.5kg, lower=5kg
        return Recommendation(
            action="increase",
            suggested_weight_kg=last.weight_kg + increment,
            reason=f"Semua rep tercapai, RPE ≤ 8, naikkan {increment}kg"
        )
    
    return Recommendation(
        action="maintain",
        suggested_weight_kg=last.weight_kg,
        reason="Belum semua rep tercapai, maintain beban"
    )


def get_increment(exercise: Exercise) -> float:
    """Upper body +2.5kg, lower body +5kg"""
    upper_groups = {"chest", "back", "shoulders", "arms"}
    if exercise.muscle_group in upper_groups:
        return 2.5
    return 5.0
```

### 11.4 Decision Matrix

| Kondisi | Semua Rep Hit | RPE ≤ 8 | Failure | Aksi |
|---|---|---|---|---|
| A | ✅ | ✅ | ❌ | **Naikkan beban** (+2.5/+5 kg) |
| B | ✅ | ❌ | ❌ | **Maintain** (RPE masih tinggi) |
| C | ❌ | - | ❌ | **Maintain** (rep belum tercapai) |
| D | - | - | ✅ | **Maintain** (ada failure) |
| E | 3x gagal berturut | - | ✅ | **Deload** (-10% beban) |

---

## 12. Frontend Design

### 12.1 Tech

| Aspek | Detail |
|---|---|
| Framework | Alpine.js (14KB gzipped) |
| CSS | Minimal custom CSS, CSS variables untuk dark mode |
| Chart | uPlot (~35KB) atau Chart.js (~60KB) |
| Icons | Emoji-based (zero dependency) |
| Build | Tidak ada build step, static HTML files |
| Hosting | Served oleh FastAPI static files |
| Total bundle | Target < 100KB |

### 12.2 Layout

```
┌─────────────────────────────────────────────┐
│  🏋️ GymMate AI              [⚙️]  [🌙]     │
├─────────────────────────────────────────────┤
│                                             │
│  [ Tab Content Area ]                       │
│                                             │
│                                             │
│                                             │
│                                             │
│                                             │
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│  📅 Jadwal  │  ✍️ Log  │  📊 History  │  📈  │
└─────────────────────────────────────────────┘
```

- Bottom tab bar (mobile-friendly, thumb-reachable)
- Dark mode default
- No scrolling pada tab bar
- Content area scrollable

### 12.3 Responsive

| Breakpoint | Layout |
|---|---|
| < 640px (HP) | Single column, bottom tabs, full-width textbox |
| ≥ 640px (tablet/desktop) | Side tabs, wider layout |

### 12.4 Offline Strategy (PWA)

- Service worker cache semua static assets
- Log bisa disimpan offline (localStorage queue)
- Sync ke server saat reconnect
- Parsing tetap butuh server (atau fallback ke manual input)

---

## 13. Dataset Strategy

### 13.1 Sumber Data

| Source | Jumlah Target | Status |
|---|---|---|
| Log gym sendiri (2 bulan) | ~25 sesi | ✅ Sudah ada |
| Log gym teman | ~75 sesi | 🔄 Collecting |
| Synthetic (template-based) | ~400 sesi | 📝 To generate |
| User corrections (post-launch) | Ongoing | 🔮 Future |
| **Total target** | **~500 sesi** | |

### 13.2 Folder Structure

```
dataset/
├── raw/                    # Teks mentah dari user
│   ├── user_ambatron/
│   │   ├── 2026-07-01.txt
│   │   ├── 2026-07-03.txt
│   │   └── ...
│   └── user_friend1/
│       └── ...
├── gold/                   # Annotated pairs (raw → JSON)
│   ├── 2026-07-01.json     # {"input": "...", "output": {...}}
│   └── ...
├── synthetic/              # Generated training data
│   ├── templates.py        # Template engine
│   ├── generated/
│   │   └── ...
│   └── README.md
├── splits/                 # Train/val/test splits
│   ├── train.jsonl
│   ├── val.jsonl
│   └── test.jsonl
└── README.md               # Dataset conventions & annotation guide
```

### 13.3 Annotation Format

```json
{
  "id": "ambatron_2026-07-01",
  "input": "chest day\nbench press 60kg 8x3\nincline db 16 each 10x3\ncapek bgt",
  "output": {
    "date": "2026-07-01",
    "sessions": [
      {
        "muscle_group": "chest",
        "exercises": [
          {
            "name": "bench press",
            "canonical": "barbell_bench_press",
            "sets": [
              {"weight_kg": 60, "reps": 8, "rpe": null, "note": null},
              {"weight_kg": 60, "reps": 8, "rpe": null, "note": null},
              {"weight_kg": 60, "reps": 8, "rpe": null, "note": null}
            ]
          },
          {
            "name": "incline db",
            "canonical": "incline_dumbbell_press",
            "sets": [
              {"weight_kg": 16, "reps": 10, "rpe": null, "note": null, "per_hand": true},
              {"weight_kg": 16, "reps": 10, "rpe": null, "note": null, "per_hand": true},
              {"weight_kg": 16, "reps": 10, "rpe": null, "note": null, "per_hand": true}
            ]
          }
        ]
      }
    ],
    "session_note": "capek bgt"
  },
  "metadata": {
    "annotator": "ambatron",
    "difficulty": "easy",
    "tags": ["bilingual", "abbreviation"]
  }
}
```

### 13.4 Konvensi Anotasi

| Pattern | Interpretasi | Contoh |
|---|---|---|
| `NxM` | N reps × M sets | `10x3` = 10 rep, 3 set |
| `each` / `per tangan` | per_hand = true | `16kg each` = 16kg per hand |
| `bar only` / `bar aja` | weight = 20kg | bar standar olimpik |
| `gagal` / `failure` | note = "failure", RPE = 10 | "set 3 gagal rep 7" |
| `Nk` / `N ribu` | weight = N (angka kecil di gym) | `35k` = 35 kg |
| Drop set | is_dropset = true per set | "dropset 20-15-10" |
| Warmup | is_warmup = true | "warmup bar only 10x2" |
| Bodyweight | weight = 0, note = "bodyweight" | "push up 20x3" |
| Superset | 2 exercises, same session order | Handled as separate exercises |

### 13.5 Synthetic Data Generation Strategy

```python
# Template-based synthetic data generation
import random

TEMPLATES = [
    # Template 1: Standard format
    "{exercise} {weight}kg {reps}x{sets}",
    # Template 2: Indo abbreviation
    "{exercise_indo} {weight} {reps} kali {sets} set",
    # Template 3: With notes
    "{exercise} {weight}kg {reps}x{sets}, {note}",
    # Template 4: Typo simulation
    "{exercise_typo} {weight}kg {reps}x{sets}",
    # Template 5: Mixed format
    "{exercise} {weight} {reps}x{sets}\n{note_indo}",
]

VARIATIONS = {
    "weight_format": ["60kg", "60", "60 kg", "60kilo", "60k"],
    "rep_format": ["8x3", "8 x 3", "8rep 3set", "8 kali 3 set", "8reps x 3sets"],
    "notes": ["capek", "kurang tidur", "gagal set terakhir", "mantap hari ini", ""],
    "typos": {"bench press": ["bench pres", "benc press", "benchpress", "bp"]},
}
```

---

## 14. Competitive Analysis

> Berdasarkan research, sudah ada 8+ app/project yang solve masalah serupa.
> Tapi **tidak ada yang kombinasi local SLM + bahasa Indonesia**.

### 14.1 Existing Competitors

| App | Free Text | AI Parse | Local/Offline | Indonesian | Approach |
|---|---|---|---|---|---|
| **Gym Note Plus** (iOS) | ✅ | ✅ | ✅ | ❌ | Built-in NLP engine |
| **GymLog AI** (web) | ✅ | ✅ | ❌ | ❌ | Chat-first, cloud LLM |
| **Beau Gym Journal** | ✅ | ✅ | ✅ | ❌ | Voice + text, offline parse |
| **Syntax** (fitness) | ✅ | ✅ | ✅ | ❌ | Markdown files, local |
| **ChatRPE** | ✅ | ✅ | ❌ | ❌ | Siri + LLM |
| **WeightXReps** | ✅ | Regex | ✅ | ❌ | Pioneer text-based (2011) |
| **Liftosaur** | Semi (DSL) | Parser | ✅ | ❌ | Custom Liftoscript syntax |
| **Strong** | ❌ | ❌ | ✅ | ❌ | Traditional structured input |
| **Hevy** | ❌ | ❌ | ✅ | ❌ | Traditional structured input |
| **JEFIT** | ❌ | ❌ | Partial | ❌ | Traditional structured input |
| **GymMate AI** | ✅ | ✅ | ✅ | ✅ | **Fine-tuned local SLM** |

### 14.2 Open Source Projects

| Project | Approach |
|---|---|
| `Julien-Au/gymcoach` | Self-hosted AI tracker, natural language shorthand |
| `ericdahl/openclaw-workout-logger` | CLI + Claude parsing |
| `Martipetti/gym-tracker-skill` | Claude skill untuk parse Notes dumps |
| `raine/parse-gym-log` | Deterministic JS parser (regex) |
| `datavis-tech/fitdown` | Domain markup → structured JSON |

### 14.3 Positioning GymMate AI

**Unique combination yang belum ada:**
1. ✅ **Local SLM** (bukan cloud API) → privacy, zero recurring cost
2. ✅ **Fine-tuned** untuk domain spesifik (bukan general-purpose LLM)
3. ✅ **Bahasa Indonesia + campur Inggris** → tidak ada competitor yang support
4. ✅ **GBNF constrained output** → guaranteed structured JSON (dengan defense-in-depth)
5. ✅ **On-premise on budget hardware** (MX350) → edge AI yang accessible

**Hal yang bisa dipelajari dari competitors:**
- **WeightXReps** (2011): Regex-based parsing sudah proven, bisa jadi baseline/fallback
- **Gym Note Plus**: UX reference untuk text-first logging
- **Ink & Switch "Potluck"**: Academic case study text → live computation

---

## 15. Hardware & Constraint

### 15.1 Server (Laptop) — Validated Specs

| Spec | Detail |
|---|---|
| Device | Acer Aspire 5 |
| CPU | Intel Core i3-1115G4 (2C/4T) @ 3.00GHz |
| RAM | 8 GB DDR4 (~28-36 GB/s bandwidth) |
| GPU | NVIDIA GeForce MX350 (GP107 Pascal, **640 CUDA cores**) |
| GPU VRAM | 2 GB GDDR5, **56.1 GB/s bandwidth**, 64-bit bus |
| GPU Compute | Compute Capability **6.1 (sm_61)** |
| GPU TDP | 15-25W (shared heat pipe, thermal throttle ~75-82°C) |
| CUDA | ✅ Supported |
| Flash Attention | ❌ **TIDAK support** (butuh sm_70+ Volta) |
| OS | Linux |

### 15.2 Client (HP)

| Spec | Detail |
|---|---|
| Device | Infinix (model TBC) |
| RAM | 4 GB |
| Browser | Chrome / default browser |
| Koneksi | WiFi lokal ke laptop |

### 15.3 llama.cpp Build Instructions (MX350-specific)

```bash
# WAJIB compile dari source dengan sm_61 (Pascal)
# Pre-built binary seringkali hanya include sm_70+ (Volta)

git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp

cmake -B build \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=61

cmake --build build --config Release

# Environment variable untuk avoid Qwen CUDA graph hangs
export GGML_CUDA_DISABLE_GRAPHS=1
```

**Recommended command line:**
```bash
export GGML_CUDA_DISABLE_GRAPHS=1

./build/bin/llama-server \
  -m models/gymmate-qwen-1.5b-q4_k_m.gguf \
  -ngl 99 \
  -c 2048 \
  -b 512 \
  -ub 512 \
  --threads 4 \
  --host 0.0.0.0 \
  --port 8080
```

**⚠️ Jangan pakai:**
- `-fa` (Flash Attention) → crash/regression di Pascal
- CUDA Graphs → hang di Qwen2.5 architecture
- Partial offload (`-ngl 10`) → PCIe 3.0 x4 bottleneck → 1-3 tok/s

### 15.4 VRAM Budget (Validated)

| Component | VRAM (ctx 2048) | VRAM (ctx 4096) |
|---|---|---|
| Model weights (28 layers, Q4_K_M) | ~986 MB | ~986 MB |
| KV Cache (FP16, GQA 2 heads) | ~57 MB | ~115 MB |
| Compute/scratch buffer | ~120 MB | ~140 MB |
| CUDA context/driver | ~100 MB | ~100 MB |
| **Total** | **~1,263 MB (62%)** | **~1,341 MB (66%)** |
| **Sisa VRAM** | **~785 MB (38%)** | **~707 MB (35%)** |

> MX350 di laptop = Optimus architecture. Display dihandle iGPU, jadi 2GB VRAM MX350 100% available untuk CUDA.

### 15.5 Performance: GPU vs CPU

| Metric | CPU-only (i5-10210U) | MX350 GPU (-ngl 99) | Speedup |
|---|---|---|---|
| Token generation | ~15 tok/s | ~32-38 tok/s | **2.2-2.6x** |
| Prompt processing | ~35-55 tok/s | ~350-550 tok/s | **~10x** |
| Time to first token | ~9.5-14.5 detik | ~0.9-1.4 detik | **~10x** |
| CPU utilization | 100% all cores | ~5-12% idle | Sistem tidak lag |
| Host RAM usage | ~1.3 GB | ~0 (semua di VRAM) | Hemat RAM |

> ⚠️ **Thermal throttle**: Sustained generation bisa turunkan clock dari 1468 MHz → 900-1100 MHz (~20% speed drop). Untuk gym log parsing yang short-burst, ini bukan masalah.

### 15.6 System RAM Budget (8GB)

| Component | Estimated RAM |
|---|---|
| Linux OS + Desktop | ~1.5 GB |
| llama.cpp (GPU offload, KV in VRAM) | ~200 MB RAM only |
| FastAPI + Python | ~200 MB |
| SQLite | ~50 MB |
| Browser (jika test di laptop) | ~500 MB |
| **Buffer** | **~5.5 GB** |

---

## 16. Roadmap

### Phase 0: Foundation (Week 1-2)

- [x] Tulis PRD (dokumen ini)
- [ ] Setup project structure
- [ ] Setup development environment (Python, CUDA, llama.cpp)
- [ ] Buat SQLite schema + seed data exercise
- [ ] Buat FastAPI skeleton

### Phase 1: Dataset (Week 2-4)

- [ ] Kumpulkan raw log sendiri (format .txt)
- [ ] Buat annotation tool sederhana (script Python)
- [ ] Anotasi 25 sesi sendiri → gold/
- [ ] Mulai kumpulkan log teman
- [ ] Buat synthetic data generator
- [ ] Generate 400 synthetic pairs
- [ ] Buat train/val/test split (80/10/10)

### Phase 2: Fine-tune SLM (Week 4-6)

- [ ] Setup Colab notebook (Unsloth + LoRA)
- [ ] Fine-tune Qwen2.5-1.5B-Instruct
- [ ] Evaluate: JSON validity, field accuracy, latency
- [ ] Iterate on dataset + hyperparams
- [ ] Export ke GGUF Q4_K_M
- [ ] Test inference di laptop (llama.cpp + CUDA)
- [ ] Write GBNF grammar, test constraint

### Phase 3: Backend (Week 6-8)

- [ ] `/api/parse` — integrate llama.cpp
- [ ] `/api/logs` — CRUD
- [ ] `/api/exercises` — history query
- [ ] `/api/schedule` — config
- [ ] `/api/progress` — body weight, volume, PRs
- [ ] `/api/recommend` — rule engine
- [ ] `/api/corrections` — save user corrections
- [ ] Error handling, validation, logging
- [ ] API tests (pytest)

### Phase 4: Rule Engine (Week 7-8)

- [ ] Implement progressive overload logic
- [ ] Implement 1RM calculator
- [ ] Implement deload detection
- [ ] Unit tests dengan edge cases
- [ ] Integration test with real data

### Phase 5: Frontend (Week 8-10)

- [ ] Tab Jadwal
- [ ] Tab Log (textbox + parse + preview + save)
- [ ] Tab History (list + chart)
- [ ] Tab Progress (body weight + volume + PR)
- [ ] Dark mode
- [ ] Settings page (schedule config)
- [ ] PWA manifest + service worker
- [ ] Mobile responsive testing

### Phase 6: Integration & Testing (Week 10-11)

- [ ] End-to-end testing (HP Infinix → WiFi → Laptop)
- [ ] Latency testing (target < 5s)
- [ ] Edge case testing (typo, bahasa campur, format aneh)
- [ ] Fix bugs
- [ ] User correction flow testing

### Phase 7: Polish & Demo (Week 11-12)

- [ ] UX polish
- [ ] Onboarding flow (setup jadwal)
- [ ] README + setup guide
- [ ] Demo video
- [ ] Collect feedback dari 3-5 gym buddy

### Future (Post-MVP)

- [ ] Multi-user support
- [ ] Cloud sync option
- [ ] Plate calculator
- [ ] Exercise suggestion (based on muscle group)
- [ ] WebGPU fallback
- [ ] Retraining pipeline dari corrections
- [ ] Android wrapper (Capacitor/TWA)
- [ ] Payment integration (Midtrans)

---

## 17. Risiko & Mitigasi

| # | Risiko | Impact | Likelihood | Mitigasi |
|---|---|---|---|---|
| R1 | Model parsing accuracy rendah setelah fine-tune | 🔴 High | Medium | Iterasi dataset, GBNF constraint jamin JSON valid, confirm-before-save sebagai safety net |
| R2 | MX350 terlalu lambat (> 10s latency) | 🟡 Medium | Medium | Coba quantisasi lebih agresif (Q3_K_S), atau pindah ke model lebih kecil (0.5B) |
| R3 | Dataset terlalu sedikit / tidak representatif | 🔴 High | High | Augment dengan synthetic data, collect corrections dari user |
| R4 | User gak mau confirm setiap kali (friction) | 🟡 Medium | Low | Auto-save kalau confidence > 95%, hanya minta confirm kalau ada warning |
| R5 | WiFi connection putus saat di gym | 🟡 Medium | Medium | Offline queue (simpan di localStorage, sync nanti) |
| R6 | Laptop harus selalu nyala | 🟡 Medium | High | Jangka panjang: migrasi ke Raspberry Pi atau VPS murah. V1: ya memang harus nyala |
| R7 | Qwen kurang bagus untuk Bahasa Indonesia | 🟡 Medium | **Low (validated)** | Research: Qwen2.5 pre-trained 18T tokens termasuk Indonesian, IndoMMLU benchmark solid, explicit code-switching training. Fine-tune 100-300 samples locks in style |
| R8 | GBNF grammar bukan 100% reliable | 🟡 Medium | **Medium (validated)** | Research: 6 known failure cases (truncation, fail-open, UTF-8, escaping, infinite loop, OOD). Mitigasi: defense-in-depth (§6.4) |

---

## 18. Success Metrics

### 18.1 Technical Metrics

| Metric | Target | Cara Ukur |
|---|---|---|
| JSON parse success rate | 100% | GBNF + post-validation |
| Exercise name accuracy | ≥ 95% | Field match vs gold |
| Weight/rep accuracy | ≥ 98% | Field match vs gold |
| End-to-end latency | < 5 detik | Timer di API |
| Frontend load time | < 1 detik | Browser DevTools |
| Frontend bundle size | < 100 KB | Build output |
| Server uptime (saat gym) | > 99% | Log monitoring |

### 18.2 Personal Use & Experiment Metrics

| Metric | Target | Cara Ukur |
|---|---|---|
| Sendiri masih pakai setelah 1 bulan | Ya | Self-check |
| Log sessions per week | ≥ 3 (sesuai jadwal gym) | DB query |
| Correction rate (edit hasil parsing) | < 15% (turun seiring fine-tune iterate) | Corrections table |
| Time to log (buka app → selesai simpan) | < 60 detik | UX timing |
| Dataset corrections collected | > 50 (untuk retraining) | Corrections table count |

---

## 19. Glosarium

| Term | Definisi |
|---|---|
| **SLM** | Small Language Model — model bahasa kecil (< 3B parameter) |
| **LoRA** | Low-Rank Adaptation — teknik fine-tune yang hemat memory |
| **GBNF** | Grammar-Based Notation Format — grammar constraint di llama.cpp |
| **GGUF** | Format file model untuk llama.cpp |
| **Q4_K_M** | Level quantization (4-bit, medium quality) |
| **1RM** | One Rep Max — estimasi beban maksimal untuk 1 repetisi |
| **RPE** | Rate of Perceived Exertion — skala 1-10 tingkat kesulitan subjektif |
| **Progressive Overload** | Prinsip naikkan beban/volume secara bertahap |
| **Deload** | Penurunan beban sementara untuk recovery |
| **PPL** | Push Pull Legs — split program gym populer |
| **Canonical name** | Nama exercise yang di-normalisasi (snake_case, unik) |
| **per_hand** | Berat per tangan (untuk dumbbell/cable) |
| **Volume** | Total beban = weight × reps × sets |
| **PWA** | Progressive Web App — web app yang bisa di-install |

---

## Appendix A: Contoh Teks Input User (Variasi)

Kumpulan contoh teks yang harus bisa di-parse, menunjukkan variasi yang diharapkan:

```
# Contoh 1: Format rapi
chest day
bench press 60kg 8x3
incline dumbbell press 16kg each 10x3
pec deck 25kg 12x3

# Contoh 2: Singkatan + campur bahasa
bp 60 8x3
incline db 16 each 10x3
cable fly 10 15x2
capek bgt

# Contoh 3: Typo + informal
benxh press 60kg 8 kali 3 set
pec dek 25kg 12x3
lagi males hari ini

# Contoh 4: Drop set + failure
bench 60 8x2, set 3 gagal rep 7
incline 16 each 10x3
pec deck dropset 30-25-20 x 10

# Contoh 5: Minimal info
squat 80 5x5
rdl 60 8x3
leg press 120 10x3

# Contoh 6: Warmup included
bench press:
warmup bar only 10x2
working set 60 8x3

# Contoh 7: Bahasa Indonesia full
angkat beban dada hari ini
bench press enam puluh kilo delapan kali tiga set
mesin dada 25 kilo 12 kali 3 set

# Contoh 8: Ambigu (multiple weights)
bench press 50 8, 55 8, 60 6
lat pulldown 30 12x3, 25 15x1

# Contoh 9: With RPE
squat 80kg 5x3 RPE 7
rdl 60kg 8x3 RPE 8
leg press 120kg 10x3 gampang bgt

# Contoh 10: Superset
superset:
lat pulldown 35 10x3
seated row 30 10x3
```

---

## Appendix B: Estimated Latency per Session Size

| Session Size | Output Tokens (est.) | @ 32 tok/s | @ 38 tok/s |
|---|---|---|---|
| 2 exercises, 3 sets each | ~300 | ~9 detik | ~8 detik |
| 3 exercises, 3 sets each | ~450 | ~14 detik | ~12 detik |
| 5 exercises, 3 sets each | ~750 | ~23 detik | ~20 detik |
| 8 exercises, 3 sets each | ~1100 | ~34 detik | ~29 detik |

> Time to first token tetap ~1-1.4 detik regardless of session size. Streaming UX membuat ini terasa lebih cepat.

---

## 20. Referensi

### Akademis

| Ref | Detail |
|---|---|
| Sivarajkumar et al. (2024) | "Mining Clinical Notes for Physical Rehabilitation Exercise Information: NLP Algorithm Development and Validation Study." JMIR Medical Informatics. PMID: 38656860 |
| JAMIA (2026) | "Benchmarking Information Extraction of Physical Activity from EHR with Large Language Models." Oxford University Press |
| Li, Dey & Forlizzi | "Stage-Based Model of Personal Informatics." ACM CHI — manual data capture = highest friction phase |
| Epstein et al. | "Lived Informatics Model." ACM CHI — tracking abandonment when overhead > utility |
| Ink & Switch (2023) | "Potluck: Dynamic Documents as Personal Software." Case study: text-based workout log with live parsing |
| Tam et al. (2024) | "Let Me Speak Freely?" — accuracy drops up to 20-30% under rigid format constraints in reasoning models |

### Teknis

| Ref | Detail |
|---|---|
| llama.cpp | https://github.com/ggml-org/llama.cpp — GBNF grammar, CUDA backend |
| Unsloth | https://github.com/unslothai/unsloth — LoRA fine-tuning, GGUF export |
| Qwen2.5 Technical Report | Alibaba — 18T tokens, 29+ languages, GQA architecture |
| IndoMMLU | Indonesian multi-subject benchmark — Qwen2.5 evaluation |
| LORAXBENCH (EMNLP) | 20 Indonesian local languages evaluation |

### Competitors & Prior Art

| Ref | Detail |
|---|---|
| WeightXReps | https://weightxreps.net — pioneer text-based gym log (2011) |
| Gym Note Plus | https://gymnoteplus.com — AI text-first gym logger (iOS) |
| Syntax Fitness | https://syntax.fitness — Markdown-based workout tracker |
| `raine/parse-gym-log` | https://github.com/raine/parse-gym-log — deterministic JS parser |
| `datavis-tech/fitdown` | https://github.com/datavis-tech/fitdown — domain markup → JSON |

---

> **Dokumen ini adalah living document.** Update sesuai progress development.  
> **Validated:** 2026-09-18 via 4 parallel research agents (MX350 benchmarks, GBNF reliability, LoRA feasibility, market landscape).
> 
> **Next step:** Setup project structure dan mulai Phase 0.
