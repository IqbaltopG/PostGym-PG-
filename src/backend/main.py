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

    # Detail progress level
    sessions_in_level = total_sessions % 5
    sessions_needed = 5 - sessions_in_level
    progress_percent = int((sessions_in_level / 5) * 100)

    gamification_info = {
        "level": level,
        "title": title,
        "total_sessions": total_sessions,
        "sessions_needed": sessions_needed,
        "progress_percent": progress_percent
    }

    DAY_NAME_ID = {
        "monday": "senin",
        "tuesday": "selasa",
        "wednesday": "rabu",
        "thursday": "kamis",
        "friday": "jumat",
        "saturday": "sabtu",
        "sunday": "minggu",
    }
    today_eng = datetime.today().strftime('%A').lower()
    today_name = DAY_NAME_ID.get(today_eng, today_eng)
    
    schedule = get_schedule()
    if not schedule or today_name not in schedule:
        return {"name": f"Jadwal {today_name.capitalize()}", "gamification": gamification_info, "exercises": []}
        
    muscle_groups = schedule[today_name]
    if muscle_groups == ["rest"]:
        return {
            "name": f"Jadwal {today_name.capitalize()} (Hari Istirahat / Rest Day 🛌)",
            "gamification": gamification_info,
            "exercises": []
        }

    plan = {
        "name": f"{today_name.capitalize()} ({', '.join(muscle_groups).title()})",
        "gamification": gamification_info,
        "exercises": []
    }
    
    # Query semua gerakan (canonical) yang pernah kamu lakukan untuk grup otot di jadwal hari ini
    conn = get_connection()
    placeholders = ','.join(['?'] * len(muscle_groups))
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
            
            # Panggil Rule Engine (Hypertrophy Rules)
            saran = calculate_next_target(history["sets"], rep_range=(8, 12))
            ex_data["recommendation"] = saran
            
        plan["exercises"].append(ex_data)
        
    return plan


import json
import urllib.request
import re

def preprocess_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        line_clean = line.strip()
        # Abaikan latihan yang di-skip oleh user (contoh: "jm press 15kg 10x3(skip)")
        if re.search(r'\(skip\)|skip sudah nda sanggup', line_clean, re.IGNORECASE):
            continue
        lines.append(line_clean)
    text = '\n'.join(lines)

    # Tangani istilah gerakan fisik informal / slang gym
    text = re.sub(r'\b(pantat\s*naik\s*turun|naik\s*turun\s*pantat|dorong\s*pantat)\b', 'hip thrust', text, flags=re.IGNORECASE)

    # Ubah desimal berkoma Indonesia "7,5kg" -> "7.5kg"
    processed = re.sub(r'(\d+),(\d+)', r'\1.\2', text)

    # Ubah singkatan berat "60k" -> "60kg" (kecuali jika bagian dari kata)
    processed = re.sub(r'(\d+(?:\.\d+)?)\s*k(?![a-zA-Z0-9])', r'\1kg', processed)

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
    processed = re.sub(r'(\d+)\s*[xX]\s*(\d+)', expand_multiplier, processed)
    
    # Hapus koma pemisah antar angka (biar "10, 11 11" jadi "10 11 11")
    processed = re.sub(r'(\d+),\s+(\d+)', r'\1 \2', processed)
    
    return processed

CANONICAL_MAP = {
    "pantat_naik_turun": "hip_thrust",
    "hip_thrust": "hip_thrust",
    "glute_bridge": "hip_thrust",
    "squad": "barbell_squat",
    "squat": "barbell_squat",
    "weighted_squad": "barbell_squat",
    "squad_bar_only": "barbell_squat",
    "dumbbell_squat": "barbell_squat",
    "incline_press": "incline_chest_press",
    "incline_chest_press": "incline_chest_press",
    "incline_chest_press_multipress_machine": "incline_chest_press",
    "incline_db_press": "incline_dumbbell_press",
    "incline_dumbbell_press": "incline_dumbbell_press",
    "pec_deck_fly": "pec_deck",
    "pecdeck_fly": "pec_deck",
    "fly_machine": "pec_deck",
    "pec_deck_fly_upper_front_chest": "pec_deck",
    "pec_deck_back_shoulder": "reverse_fly",
    "rear_delt_fly": "reverse_fly",
    "rear_delt_pec_fly": "reverse_fly",
    "back_shoulder_fly": "reverse_fly",
    "lateral_rise": "lateral_raise",
    "incline_shoulder_press": "dumbbell_shoulder_press",
    "preachears_curl": "preacher_curl",
    "preachers_curl": "preacher_curl",
    "forearm_curl": "wrist_curl",
    "forearm_train": "wrist_curl",
    "curl": "wrist_curl",
    "seated_narrow_grip_row": "seated_row",
    "seated_cable_row": "seated_row",
    "adducter_ke_dalam": "hip_adduction",
    "adductor": "hip_adduction",
    "abilow_core": "ab_wheel",
    "abilow": "ab_wheel",
    "hanging_leg_raises_in_bar": "hanging_leg_raise",
    "hanging_leg_raise_in_bar": "hanging_leg_raise",
    "core_training_leg_up_in_bar": "hanging_leg_raise",
    "leg_up": "hanging_leg_raise",
    "triceps_push_down": "tricep_pushdown",
    "triceps_overhead_extention": "overhead_tricep_extension",
    "overhead_extension": "overhead_tricep_extension",
    "one_arm_triceps_push_down": "single_arm_tricep_pushdown",
    "calf_press": "calf_raise",
}

def normalize_canonical(raw_canonical: str) -> str:
    cleaned = re.sub(r'[^a-z0-9_]', '', raw_canonical.lower().strip().replace(' ', '_'))
    return CANONICAL_MAP.get(cleaned, cleaned)

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
            
            # Normalisasi canonical, sanitasi set, dan deduplikasi
            for session in ai_output.get("sessions", []):
                seen = set()
                unique_ex = []
                for ex in session.get("exercises", []):
                    raw_c = ex.get("canonical", "")
                    normalized_c = normalize_canonical(raw_c)
                    ex["canonical"] = normalized_c
                    
                    # Validasi set: pastikan weight dan reps valid angka
                    clean_sets = []
                    for s in ex.get("sets", []):
                        try:
                            w = float(s.get("weight_kg", 0))
                            r = int(s.get("reps", 0))
                            if r > 0:
                                s["weight_kg"] = w
                                s["reps"] = r
                                clean_sets.append(s)
                        except (ValueError, TypeError):
                            continue
                    ex["sets"] = clean_sets

                    if normalized_c not in seen and len(clean_sets) > 0:
                        seen.add(normalized_c)
                        unique_ex.append(ex)
                session["exercises"] = unique_ex

            return {"status": "success", "data": ai_output}
    except Exception as e:
        return {"status": "error", "message": f"Koneksi ke AI runtime gagal ({str(e)}). Pastikan llama-server berjalan di port 8080."}

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
