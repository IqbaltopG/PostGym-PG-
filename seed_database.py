import os
import json
from src.backend.database import save_workout_log, save_schedule

# Path ke direktori
GOLD_DIR = "dataset/gold"
SCHEDULE_PATH = "dataset/raw/user_ambatron/schedule.json"

def seed_schedule():
    print("Memuat jadwal gym dari schedule.json...")
    with open(SCHEDULE_PATH, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    # Dukung format nested {schedule_name, days: {...}} maupun flat {day: [...]}
    schedule = raw.get("days", raw)
    save_schedule(schedule)
    print("Jadwal berhasil dimuat ke database.")

def seed_database():
    print("Mulai menyuntikkan data Gold ke SQLite...")

    seed_schedule()
    
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
