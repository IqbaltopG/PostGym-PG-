#!/usr/bin/env python3
"""
POST GYM — Unified Dataset & Fine-Tuning Pipeline
Otomatisasi pengolahan raw log -> gold dataset -> dataset_train.jsonl untuk fine-tuning SLM.
"""

import os
import re
import json
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
RAW_LOG_FILE = os.path.join(DATASET_DIR, "raw", "user_ambatron", "raw_log.txt")
SESSIONS_DIR = os.path.join(DATASET_DIR, "raw", "user_ambatron", "sessions")
GOLD_DIR = os.path.join(DATASET_DIR, "gold")
OUTPUT_JSONL = os.path.join(DATASET_DIR, "dataset_train.jsonl")

SYSTEM_PROMPT = """Kamu adalah parser log gym. Tugas: konversi teks bebas log latihan menjadi JSON terstruktur.
Aturan:
- "8x3" = 8 reps x 3 sets
- "each" atau "per tangan" = per_hand: true
- "bar only" atau "bar aja" = 20kg
- "gagal" atau "failure" = note + RPE 10
- "35k" = 35 kg
- Normalisasi nama exercise ke canonical form (snake_case)
- Pisahkan catatan umum ke session_note"""

def step1_split_raw_logs():
    """Memecah raw_log.txt menjadi sesi individual berdasarkan tanggal."""
    if not os.path.exists(RAW_LOG_FILE):
        print(f"[!] File raw log tidak ditemukan di {RAW_LOG_FILE}")
        return 0

    os.makedirs(SESSIONS_DIR, exist_ok=True)
    with open(RAW_LOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    date_pattern = re.compile(r'\b(\d{1,2}-\d{1,2}-\d{4})\b')
    current_date = None
    current_content = []
    saved_count = 0

    def save_session(date_str, content):
        nonlocal saved_count
        if not date_str or not content:
            return
        text = "".join(content).strip()
        if not text:
            return
        try:
            parsed_date = datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            parsed_date = date_str
        filename = os.path.join(SESSIONS_DIR, f"{parsed_date}.txt")
        with open(filename, 'w', encoding='utf-8') as out_f:
            out_f.write(text)
        saved_count += 1

    for line in lines:
        match = date_pattern.search(line)
        if match:
            if current_date:
                save_session(current_date, current_content)
            current_date = match.group(1)
            current_content = []
        elif current_date:
            current_content.append(line)

    if current_date:
        save_session(current_date, current_content)

    print(f"[*] Step 1: Berhasil memecah {saved_count} sesi dari raw_log.txt")
    return saved_count

def step2_build_chatml_dataset():
    """Mengompilasi semua gold sample menjadi format ChatML standar Unsloth."""
    gold_files = glob.glob(os.path.join(GOLD_DIR, "*.json"))
    if not gold_files:
        print(f"[!] Tidak ada file gold di {GOLD_DIR}")
        return 0

    total_valid = 0
    with open(OUTPUT_JSONL, 'w', encoding='utf-8') as outfile:
        for file_path in sorted(gold_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if "input" not in data or "output" not in data:
                    continue

                chat_format = {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": data["input"].strip()},
                        {"role": "assistant", "content": json.dumps(data["output"], separators=(',', ':'))}
                    ]
                }
                outfile.write(json.dumps(chat_format, ensure_ascii=False) + '\n')
                total_valid += 1
            except Exception as e:
                print(f"[!] Error membaca {file_path}: {e}")

    print(f"[*] Step 2: Berhasil mengompilasi {total_valid} sampel ChatML ke {OUTPUT_JSONL}")
    return total_valid

def step3_print_summary(session_count, sample_count):
    """Menampilkan status kesiapan training."""
    file_size_kb = os.path.getsize(OUTPUT_JSONL) / 1024 if os.path.exists(OUTPUT_JSONL) else 0
    print("\n" + "="*50)
    print("🚀 POST GYM — DATASET PIPELINE SIAP!")
    print(f"• Total Sesi Log Mentah  : {session_count} sesi")
    print(f"• Total Sampel Training  : {sample_count} pairs")
    print(f"• Ukuran File JSONL     : {file_size_kb:.2f} KB")
    print("="*50)
    print("Langkah selanjutnya:")
    print("1. Buka Google Colab -> Upload 'training/gymmate-finetune.ipynb'")
    print("2. Upload 'dataset/dataset_train.jsonl' ke panel Files di Colab")
    print("3. Jalankan 'Run All' di Colab (GPU T4) untuk fine-tuning otomatis!")
    print("="*50 + "\n")

if __name__ == "__main__":
    sessions = step1_split_raw_logs()
    samples = step2_build_chatml_dataset()
    step3_print_summary(sessions, samples)
