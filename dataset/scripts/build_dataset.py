import json
import os
import glob

gold_dir = "../gold/"
output_file = "../dataset_train.jsonl"

system_prompt = """Kamu adalah parser log gym. Tugas: konversi teks bebas log latihan menjadi JSON terstruktur.
Aturan:
- "8x3" = 8 reps x 3 sets
- "each" atau "per tangan" = per_hand: true
- "bar only" atau "bar aja" = 20kg
- "gagal" atau "failure" = note + RPE 10
- "35k" = 35 kg
- Normalisasi nama exercise ke canonical form (snake_case)
- Pisahkan catatan umum ke session_note"""

gold_files = glob.glob(os.path.join(gold_dir, "*.json"))

with open(output_file, 'w', encoding='utf-8') as outfile:
    for file_path in gold_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Format ChatML standar untuk Unsloth
            chat_format = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": data["input"]},
                    {"role": "assistant", "content": json.dumps(data["output"], separators=(',', ':'))}
                ]
            }
            
            json.dump(chat_format, outfile)
            outfile.write('\n')

print(f"Berhasil membuat {output_file} dengan {len(gold_files)} sampel data.")
