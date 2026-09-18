from database import init_db, save_schedule, get_schedule, save_workout_log, get_last_history
import json
from datetime import datetime

print("1. Inisialisasi Database (Bikin tabel)...")
init_db()

print("\n2. Menyimpan Jadwal 'Crot dalam'...")
jadwal_ambatron = {
    "monday": ["chest", "back", "forearm", "bicep"],
    "wednesday": ["chest", "triceps", "shoulder", "bicep"],
    "friday": ["legs", "calves", "core"],
    "saturday": ["back", "triceps", "forearm", "shoulders", "core"]
}
save_schedule(jadwal_ambatron)

jadwal_tersimpan = get_schedule()
print(f"Jadwal hari Senin: {jadwal_tersimpan['monday']}")

print("\n3. Mensimulasikan AI selesai parsing teks (Save ke DB)...")
# Ini pura-puranya hasil output Qwen dari data log kamu tanggal 16 Sept
mock_ai_output = {
  "date": "2026-09-16",
  "sessions": [
    {
      "muscle_group": "chest",
      "exercises": [
        {
          "name": "incline press",
          "canonical": "incline_dumbbell_press",
          "sets": [
            {"weight_kg": 15.0, "reps": 10},
            {"weight_kg": 15.0, "reps": 11},
            {"weight_kg": 20.0, "reps": 6}
          ]
        }
      ]
    }
  ],
  "session_note": "form perfection again"
}
save_workout_log(mock_ai_output)
print("Data log berhasil disimpan ke SQLite!")

print("\n4. Test: Cek History Beban (Fitur untuk Auto-complete / Jadwal)!")
history = get_last_history("incline_dumbbell_press")

if history:
    print(f"Kamu pernah melakukan Incline Dumbbell Press pada {history['date']}!")
    for i, s in enumerate(history['sets']):
        print(f"  Set {i+1}: {s['weight']}kg x {s['reps']} rep")
else:
    print("Belum ada history untuk gerakan ini.")
