import re
import os
from datetime import datetime

input_file = "../raw/user_ambatron/raw_log.txt"
output_dir = "../raw/user_ambatron/sessions/"

with open(input_file, 'r') as f:
    lines = f.readlines()

current_date = None
current_content = []

# Regex untuk mencari format tanggal seperti 18-09-2026 atau senin 27-07-2026
date_pattern = re.compile(r'\b(\d{1,2}-\d{1,2}-\d{4})\b')

def save_session(date_str, content):
    if not date_str or not content:
        return
    
    # Bersihkan whitespace berlebih di awal/akhir
    text = "".join(content).strip()
    if not text:
        return
        
    # Ubah format tanggal dari DD-MM-YYYY ke YYYY-MM-DD
    try:
        parsed_date = datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    except ValueError:
        parsed_date = date_str # Fallback jika gagal parse
        
    filename = os.path.join(output_dir, f"{parsed_date}.txt")
    with open(filename, 'w') as out_f:
        out_f.write(text)
    print(f"Saved: {filename}")

for line in lines:
    match = date_pattern.search(line)
    if match:
        # Jika menemukan tanggal baru, simpan konten sebelumnya
        if current_date:
            save_session(current_date, current_content)
        
        current_date = match.group(1)
        current_content = [] # Reset konten untuk tanggal baru
    elif current_date:
        # Abaikan baris kosong di awal/akhir blok, tapi simpan newline di tengah
        current_content.append(line)

# Simpan sesi terakhir
if current_date:
    save_session(current_date, current_content)

print("Selesai memecah log!")
