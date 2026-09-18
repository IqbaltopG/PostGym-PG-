import os
import json
import sqlite3
from src.backend.database import save_workout_log

# Path ke direktori
GOLD_DIR = "dataset/gold"

def seed_database():
    print("Mulai menyuntikkan data Gold ke SQLite...")
    
    # Ambil semua file .json di folder gold
    gold_files = [f for f in os.listdir(GOLD_DIR) if f.endswith('.json')]
    
    count = 0
    for filename in gold_files:
        filepath = os.path.join(GOLD_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # data["output"] adalah format JSON AI yang bersih
            parsed_json = data["output"]
            
            try:
                save_workout_log(parsed_json)
                count += 1
            except Exception as e:
                print(f"Gagal memasukkan {filename}: {e}")
                
    print(f"Sukses! Berhasil menyuntikkan {count} sesi latihan ke dalam gymmate.db")

if __name__ == "__main__":
    seed_database()
