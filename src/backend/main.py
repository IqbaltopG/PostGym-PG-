import os
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import fungsi database dan rules engine buatan kita
from database import get_schedule, get_last_history, save_workout_log, get_all_history
from rules import calculate_next_target

app = FastAPI(title="POST GYM Backend")

# Enable CORS buat development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SCHEMA ---
class ParseRequest(BaseModel):
    raw_text: str

# --- API ENDPOINTS ---

@app.get("/api/today")
async def get_today_plan():
    """Mengembalikan plan hari ini beserta history gerakan dan Gamification"""
    # Hitung level RPG
    from database import get_connection
    conn = get_connection()
    total_sessions = conn.execute("SELECT COUNT(*) FROM workout_sessions").fetchone()[0]
    conn.close()
    
    # Logika Gelar
    level = (total_sessions // 5) + 1
    if level <= 2: title = "🐣 Couch Potato"
    elif level <= 5: title = "🦍 Gym Bro"
    elif level <= 8: title = "🦾 Iron Man"
    elif level <= 12: title = "🔱 Poseidon"
    else: title = "⚡ Greek God"

    today_name = datetime.today().strftime('%A').lower()
    
    schedule = get_schedule()
    if not schedule or today_name not in schedule:
        return {"name": f"Jadwal {today_name.capitalize()}", "gamification": {"level": level, "title": title, "total_sessions": total_sessions}, "exercises": []}
        
    muscle_groups = schedule[today_name]
    plan = {
        "name": f"{today_name.capitalize()} ({', '.join(muscle_groups).title()})",
        "gamification": {
            "level": level,
            "title": title,
            "total_sessions": total_sessions
        },
        "exercises": []
    }
    
    # Query semua gerakan (canonical) yang pernah kamu lakukan untuk grup otot di jadwal hari ini
    conn = get_connection()
    placeholders = ','.join(['?'] * len(muscle_groups))
    
    # Supaya pencariannya case-insensitive dan spasi/karakter aman, pastikan format string sesuai
    # (Di schedule.json hurufnya besar "Chest", tapi di DB kecil "chest")
    lower_muscles = [m.lower() for m in muscle_groups]
    
    rows = conn.execute(f"SELECT DISTINCT canonical FROM exercises WHERE LOWER(muscle_group) IN ({placeholders})", lower_muscles).fetchall()
    target_exercises = [row['canonical'] for row in rows]
    conn.close()
    
    for ex_canonical in target_exercises:
        history = get_last_history(ex_canonical)
        
        ex_data = {
            "name": ex_canonical.replace("_", " ").title(),
            "canonical": ex_canonical,
            "last_weight": None,
            "last_reps": None,
            "last_sets": None,
            "recommendation": None
        }
        
        if history:
            ex_data["last_weight"] = history["sets"][0]["weight"]
            ex_data["last_reps"] = ", ".join(str(s["reps"]) for s in history["sets"])
            ex_data["last_sets"] = len(history["sets"])
            
            # THE MAGIC: Panggil Rule Engine (Hypertrophy Rules)
            saran = calculate_next_target(history["sets"], rep_range=(8, 12))
            ex_data["recommendation"] = saran
            
        plan["exercises"].append(ex_data)
        
    return plan


import json
import urllib.request
import re

def preprocess_text(text: str) -> str:
    # Mengubah format "10x3" ATAU "3x10" menjadi "10 10 10"
    def expand_multiplier(match):
        a = int(match.group(1))
        b = int(match.group(2))
        
        # Heuristik Gym: Repetisi biasanya lebih besar dari jumlah Set
        if a >= b:
            reps = a
            sets = b
        else:
            reps = b
            sets = a
            
        return ' '.join([str(reps)] * sets)
    
    # Cari pola (angka)x(angka)
    processed = re.sub(r'(\d+)\s*[xX]\s*(\d+)', expand_multiplier, text)
    
    # Hapus koma pemisah antar angka (biar "10, 11 11" jadi "10 11 11")
    # Hati-hati jangan sampai merusak desimal "12,5" (nggak ada spasi)
    processed = re.sub(r'(\d+),\s+(\d+)', r'\1 \2', processed)
    
    return processed

@app.post("/api/parse")
async def parse_log(request: ParseRequest):
    """
    Endpoint ini nembak langsung ke llama-server lokal.
    Hanya me-return hasil JSON, TIDAK menyimpan ke database.
    """
    cleaned_text = preprocess_text(request.raw_text)

    system_prompt = """Kamu adalah parser log gym. Tugas: konversi teks bebas log latihan menjadi JSON terstruktur.
Aturan:
- "8x3" = 8 reps x 3 sets
- "each" atau "per tangan" = per_hand: true
- "bar only" atau "bar aja" = 20kg
- "gagal" atau "failure" = note + RPE 10
- "35k" = 35 kg
- Normalisasi nama exercise ke canonical form (snake_case)
- Pisahkan catatan umum ke session_note"""

    prompt_chatml = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{cleaned_text}<|im_end|>\n<|im_start|>assistant\n"
    
    payload = {
        "prompt": prompt_chatml,
        "n_predict": 1024,
        "temperature": 0.1,
        "stop": ["<|im_end|>"],
        "json_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "sessions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "muscle_group": {"type": "string"},
                            "exercises": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "canonical": {"type": "string"},
                                        "sets": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "weight_kg": {"type": "number"},
                                                    "reps": {"type": "integer"},
                                                    "note": {"type": "string"},
                                                    "per_hand": {"type": "boolean"}
                                                },
                                                "required": ["weight_kg", "reps"]
                                            }
                                        }
                                    },
                                    "required": ["name", "canonical", "sets"]
                                }
                            }
                        },
                        "required": ["muscle_group", "exercises"]
                    }
                },
                "session_note": {"type": "string"}
            },
            "required": ["date", "sessions", "session_note"]
        }
    }

    req = urllib.request.Request(
        "http://127.0.0.1:8080/completion",
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result.get('content', '{}')
            ai_output = json.loads(content)
            
            # Filter deduplikasi (hapus kalau canonical sama di otot yang sama)
            for session in ai_output.get("sessions", []):
                seen = set()
                unique_ex = []
                for ex in session.get("exercises", []):
                    canonical = ex.get("canonical", "").replace("_", "").replace(" ", "").lower()
                    if canonical not in seen:
                        seen.add(canonical)
                        unique_ex.append(ex)
                session["exercises"] = unique_ex

            return {"status": "success", "data": ai_output}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/save")
async def save_log(data: dict):
    """Menerima JSON yang sudah diedit/divalidasi user dan menyimpannya ke DB"""
    try:
        save_workout_log(data)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/history")
async def get_history():
    """Endpoint untuk mengambil semua data riwayat dari database"""
    return get_all_history()

from database import get_exercise_progress, get_workout_recap

@app.get("/api/progress/exercise/{canonical_name}")
async def api_exercise_progress(canonical_name: str):
    return get_exercise_progress(canonical_name)

@app.get("/api/progress/recap")
async def api_recap(period: str = "month"):
    return get_workout_recap(period)

@app.get("/api/exercises/list")
async def get_exercises_list():
    import database
    conn = database.get_connection()
    rows = conn.execute("SELECT DISTINCT canonical, name FROM exercises GROUP BY canonical ORDER BY name ASC").fetchall()
    conn.close()
    return [{"canonical": r["canonical"], "name": r["name"]} for r in rows]

# --- SERVE FRONTEND ---
# Serve folder frontend sebagai static files di route utama "/"
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
