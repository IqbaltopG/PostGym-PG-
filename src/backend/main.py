import os
import time
import uuid
import shutil
import csv
import io
import json
import urllib.request
import re
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import fungsi database dan rules engine buatan kita
from database import (
    get_schedule,
    save_schedule,
    get_last_history,
    save_workout_log,
    get_all_history,
    quick_log_set,
    undo_last_set,
    get_all_workout_records_flat,
    generate_anonymous_account,
    get_account_status,
    redeem_voucher_code,
    simulate_qris,
    get_competitive_rank_info,
    get_today_session_summary,
    get_exercise_progress,
    get_workout_recap,
    get_all_distinct_exercises,
    get_connection
)
from rules import calculate_next_target
from pose_analyzer import PoseAnalyzer

pose_analyzer_instance = PoseAnalyzer()

app = FastAPI(title="POST GYM Backend")

# Enable CORS buat development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SCHEMAS ---
class ParseRequest(BaseModel):
    raw_text: str
    account_id: Optional[str] = None

class QuickLogRequest(BaseModel):
    canonical: str
    name: str
    muscle_group: str = "other"
    weight_kg: float
    reps: int
    note: str = ""
    date: Optional[str] = None

# --- API ENDPOINTS ---

@app.get("/api/today")
async def get_today_plan():
    """Mengembalikan plan hari ini beserta history gerakan dan Competitive Ranking"""
    rank_info = get_competitive_rank_info()
    today_session_summary = get_today_session_summary()

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
        return {
            "name": f"Jadwal {today_name.capitalize()}",
            "rank": rank_info,
            "gamification": rank_info,
            "session_summary": today_session_summary,
            "exercises": []
        }
        
    muscle_groups = schedule[today_name]
    if muscle_groups == ["rest"]:
        return {
            "name": f"Jadwal {today_name.capitalize()} (Hari Istirahat / Rest Day 🛌)",
            "rank": rank_info,
            "gamification": rank_info,
            "session_summary": today_session_summary,
            "exercises": []
        }

    plan = {
        "name": f"{today_name.capitalize()} ({', '.join(muscle_groups).title()})",
        "rank": rank_info,
        "gamification": rank_info,
        "session_summary": today_session_summary,
        "exercises": []
    }
    
    today_iso = datetime.today().strftime('%Y-%m-%d')
    conn = get_connection()
    placeholders = ','.join(['?'] * len(muscle_groups))
    lower_muscles = [m.lower() for m in muscle_groups]
    
    # Ambil session id hari ini jika ada untuk mengecek set yang sudah dicatat
    today_session = conn.execute("SELECT id FROM workout_sessions WHERE date = ?", (today_iso,)).fetchone()
    today_session_id = today_session['id'] if today_session else None

    rows = conn.execute(
        f"SELECT DISTINCT canonical, muscle_group, name FROM exercises WHERE LOWER(muscle_group) IN ({placeholders}) GROUP BY canonical",
        lower_muscles
    ).fetchall()
    
    target_exercises = [row['canonical'] for row in rows]
    meta_map = {row['canonical']: (row['name'], row['muscle_group']) for row in rows}
    
    for ex_canonical in target_exercises:
        history = get_last_history(ex_canonical)
        raw_name, mg = meta_map.get(ex_canonical, (ex_canonical.replace("_", " ").title(), muscle_groups[0]))
        
        # Ambil set yang sudah dicatat hari ini
        today_sets = []
        if today_session_id:
            ex_row = conn.execute("SELECT id FROM exercises WHERE session_id = ? AND canonical = ?", (today_session_id, ex_canonical)).fetchone()
            if ex_row:
                s_rows = conn.execute("SELECT id, weight_kg, reps, note FROM sets WHERE exercise_id = ? ORDER BY id ASC", (ex_row['id'],)).fetchall()
                today_sets = [{"id": s["id"], "weight": s["weight_kg"], "reps": s["reps"], "note": s["note"]} for s in s_rows]
        
        ex_data = {
            "name": raw_name,
            "canonical": ex_canonical,
            "muscle_group": mg,
            "last_weight": None,
            "last_reps": None,
            "last_sets": None,
            "recommendation": None,
            "today_sets": today_sets,
            "today_total_sets": len(today_sets)
        }
        
        if history:
            ex_data["last_weight"] = history["sets"][0]["weight"]
            ex_data["last_reps"] = ", ".join(str(s["reps"]) for s in history["sets"])
            ex_data["last_sets"] = len(history["sets"])
            
            # Panggil Rule Engine (Hypertrophy Rules)
            saran = calculate_next_target(history["sets"], rep_range=(8, 12))
            ex_data["recommendation"] = saran
            
        plan["exercises"].append(ex_data)
        
    conn.close()
    return plan


@app.post("/api/quick-log")
async def api_quick_log(req: QuickLogRequest):
    """
    1-Tap Quick Log untuk Free Tier:
    Menyimpan 1 set latihan langsung ke database tanpa perlu AI parser.
    """
    try:
        res = quick_log_set(
            canonical=req.canonical,
            name=req.name,
            muscle_group=req.muscle_group,
            weight_kg=req.weight_kg,
            reps=req.reps,
            note=req.note,
            date_str=req.date
        )
        res["rank"] = get_competitive_rank_info()
        res["session_summary"] = get_today_session_summary(req.date)
        return res
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/quick-log/undo")
async def api_quick_log_undo(req: dict):
    """Membatalkan set terakhir dari gerakan hari ini"""
    try:
        canonical = req.get("canonical")
        date_str = req.get("date")
        if not canonical:
            return {"status": "error", "message": "Canonical name required"}
        res = undo_last_set(canonical, date_str)
        if isinstance(res, dict):
            res["rank"] = get_competitive_rank_info()
            res["session_summary"] = get_today_session_summary(date_str)
        return res
    except Exception as e:
        return {"status": "error", "message": str(e)}

def preprocess_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        line_clean = line.strip()
        # Abaikan latihan yang di-skip oleh user (contoh: "jm press 15kg 10x3(skip)")
        if re.search(r'\(skip\)|skip sudah nda sanggup', line_clean, re.IGNORECASE):
            continue
        lines.append(line_clean)
    text = '\n'.join(lines)

    # Tangani istilah gerakan fisik informal & slang kocak gym Indonesia
    slang_patterns = [
        (r'\b(begantung\s*kaki\s*naik\s*naik|gelantungan\s*angkat\s*kaki|gantungan\s*angkat\s*kaki|leg\s*up\s*in\s*bar)\b', 'hanging leg raise'),
        (r'\b(pantat\s*naik\s*turun|naik\s*turun\s*pantat|genjot\s*bar|dorong\s*pinggul|dorong\s*pantat)\b', 'hip thrust'),
        (r'\b(kangkang\s*mesin|buka\s*paha|mesin\s*kangkang)\b', 'hip abduction'),
        (r'\b(jepit\s*paha|rapat\s*paha|mesin\s*jepit\s*paha)\b', 'hip adduction'),
        (r'\b(rebahan\s*dorong\s*bar|tiduran\s*dorong\s*barbel|dorong\s*tiang\s*rebahan)\b', 'barbell bench press'),
        (r'\b(rebahan\s*dorong\s*miring|dorong\s*miring\s*ke\s*atas)\b', 'incline chest press'),
        (r'\b(belah\s*dada|peluk\s*mesin|buka\s*tutup\s*dada|dada\s*kupu\s*kupu)\b', 'pec deck'),
        (r'\b(tarik\s*kabel\s*dari\s*atas|tarik\s*ke\s*dada)\b', 'lat pulldown'),
        (r'\b(dayung\s*duduk|narik\s*kabel\s*perut)\b', 'seated row'),
        (r'\b(bungkuk\s*tarik\s*besi|dayung\s*bungkuk)\b', 'barbell row'),
        (r'\b(gelantungan\s*tarik\s*badan|angkat\s*badan\s*di\s*tiang)\b', 'pull up'),
        (r'\b(dorong\s*plat\s*miring|injek\s*mesin|dorong\s*bantalan\s*kaki)\b', 'leg press'),
        (r'\b(tendang\s*kaki\s*ke\s*depan|lurusin\s*dengkul|tendang\s*mesin\s*ke\s*atas)\b', 'leg extension'),
        (r'\b(tekuk\s*kaki\s*ke\s*belakang|rebahan\s*tekuk\s*kaki|tarik\s*bantalan\s*ke\s*pantat)\b', 'leg curl'),
        (r'\b(kaki\s*satu\s*di\s*kursi|gerakan\s*sembah\s*kubur|siksaan\s*satu\s*kaki)\b', 'bulgarian split squat'),
        (r'\b(jinjit\s*betis|jinjit\s*mesin)\b', 'calf raise'),
        (r'\b(duduk\s*dorong\s*beban\s*ke\s*atas|dorong\s*dambel\s*ke\s*atas)\b', 'dumbbell shoulder press'),
        (r'\b(buka\s*tangan\s*ke\s*samping|kepak\s*sayap\s*bahu)\b', 'lateral raise'),
        (r'\b(peluk\s*mesin\s*kebalik|bahu\s*belakang\s*mesin)\b', 'reverse fly'),
        (r'\b(tarik\s*tali\s*ke\s*(?:muka|jidat|hidung|mata))\b', 'face pull'),
        (r'\b(gedik\s*bahu|angkat\s*pundak|gaya\s*ga\s*tau)\b', 'dumbbell shrug'),
        (r'\b(pompa\s*bisep|tekuk\s*lengan)\b', 'bicep curl'),
        (r'\b(palu\s*dambel|posisi\s*martil)\b', 'hammer curl'),
        (r'\b(taruh\s*lengan\s*di\s*bantalan\s*miring|ketiak\s*nempel\s*bantalan)\b', 'preacher curl'),
        (r'\b(dorong\s*tali\s*ke\s*bawah|tekan\s*kabel\s*ke\s*bawah|tali\s*trisep)\b', 'tricep pushdown'),
        (r'\b(dorong\s*tali\s*dari\s*belakang\s*kepala)\b', 'overhead tricep extension'),
        (r'\b(hancur\s*jidat|patah\s*leher|tekuk\s*barbel\s*ke\s*dahi)\b', 'skullcrusher'),
        (r'\b(tekuk\s*pergelangan\s*tangan)\b', 'wrist curl'),
        (r'\b(roda\s*gelinding\s*perut|dorong\s*roda\s*lantai|roda\s*perut)\b', 'ab wheel'),
        (r'\b(dorong\s*lantai|tiarap\s*dorong\s*tanah)\b', 'push up'),
        (r'\b(celup\s*badan|turun\s*naik\s*palang\s*dua)\b', 'dips'),
        (r'\b(tahan\s*badan\s*lurus\s*tiarap|posisi\s*push\s*up\s*diem|tahan\s*perut\s*gemeter)\b', 'plank'),
    ]
    for pattern, replacement in slang_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

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
    # Core & Descriptives
    "begantung_kaki_naik_naik": "hanging_leg_raise",
    "gelantungan_angkat_kaki": "hanging_leg_raise",
    "gantungan_angkat_kaki": "hanging_leg_raise",
    "hanging_leg_raises_in_bar": "hanging_leg_raise",
    "hanging_leg_raise_in_bar": "hanging_leg_raise",
    "core_training_leg_up_in_bar": "hanging_leg_raise",
    "leg_up": "hanging_leg_raise",
    "leg_up_in_bar": "hanging_leg_raise",
    "roda_gelinding_perut": "ab_wheel",
    "dorong_roda_lantai": "ab_wheel",
    "roda_perut": "ab_wheel",
    "abilow_core": "ab_wheel",
    "abilow": "ab_wheel",
    "ab_wheel": "ab_wheel",
    "plank": "plank",
    "plenk": "plank",
    "plang": "plank",

    # Legs & Glutes
    "pantat_naik_turun": "hip_thrust",
    "hip_thrust": "hip_thrust",
    "hiptrast": "hip_thrust",
    "hip_trust": "hip_thrust",
    "genjot_bar": "hip_thrust",
    "glute_bridge": "hip_thrust",
    "kangkang_mesin": "hip_abduction",
    "buka_paha": "hip_abduction",
    "hip_abduction": "hip_abduction",
    "hip_abduksen": "hip_abduction",
    "abduktor": "hip_abduction",
    "jepit_paha": "hip_adduction",
    "rapat_paha": "hip_adduction",
    "hip_adduction": "hip_adduction",
    "adducter_ke_dalam": "hip_adduction",
    "adductor": "hip_adduction",
    "squad": "barbell_squat",
    "squat": "barbell_squat",
    "skot": "barbell_squat",
    "skwat": "barbell_squat",
    "skuat": "barbell_squat",
    "weighted_squad": "barbell_squat",
    "squad_bar_only": "barbell_squat",
    "dumbbell_squat": "barbell_squat",
    "jongkok_pikul_besi": "barbell_squat",
    "dorong_plat_miring": "leg_press",
    "injek_mesin": "leg_press",
    "lek_pres": "leg_press",
    "legpres": "leg_press",
    "leg_press": "leg_press",
    "tendang_kaki_ke_depan": "leg_extension",
    "lurusin_dengkul": "leg_extension",
    "lek_eksten": "leg_extension",
    "leg_extension": "leg_extension",
    "tekuk_kaki_ke_belakang": "leg_curl",
    "lek_kerl": "leg_curl",
    "leg_curl": "leg_curl",
    "kaki_satu_di_kursi": "bulgarian_split_squat",
    "gerakan_sembah_kubur": "bulgarian_split_squat",
    "bulgar": "bulgarian_split_squat",
    "bulgarian_split_squat": "bulgarian_split_squat",
    "jinjit_betis": "calf_raise",
    "jinjit_mesin": "calf_raise",
    "kalf_reis": "calf_raise",
    "calf_press": "calf_raise",
    "calf_raise": "calf_raise",

    # Chest
    "rebahan_dorong_bar": "barbell_bench_press",
    "tiduran_dorong_barbel": "barbell_bench_press",
    "brench_pres": "barbell_bench_press",
    "bencpres": "barbell_bench_press",
    "bens": "barbell_bench_press",
    "bench_press": "barbell_bench_press",
    "barbell_bench_press": "barbell_bench_press",
    "incline_press": "incline_chest_press",
    "incline_chest_press": "incline_chest_press",
    "incline_chest_press_multipress_machine": "incline_chest_press",
    "rebahan_dorong_miring": "incline_chest_press",
    "inklin": "incline_chest_press",
    "incline_db_press": "incline_dumbbell_press",
    "incline_dumbbell_press": "incline_dumbbell_press",
    "belah_dada": "pec_deck",
    "peluk_mesin": "pec_deck",
    "buka_tutup_dada": "pec_deck",
    "pec_deck": "pec_deck",
    "pec_deck_fly": "pec_deck",
    "pecdeck_fly": "pec_deck",
    "pekdek": "pec_deck",
    "fly_machine": "pec_deck",
    "pec_deck_fly_upper_front_chest": "pec_deck",
    "dorong_lantai": "push_up",
    "push_up": "push_up",
    "pus_up": "push_up",
    "pushap": "push_up",
    "celup_badan": "dips",
    "dips": "dips",

    # Back
    "tarik_kabel_dari_atas": "lat_pulldown",
    "tarik_ke_dada": "lat_pulldown",
    "letpul": "lat_pulldown",
    "latpul": "lat_pulldown",
    "letpuldon": "lat_pulldown",
    "lat_pulldown": "lat_pulldown",
    "lat_pull_down": "lat_pulldown",
    "dayung_duduk": "seated_row",
    "narik_kabel_perut": "seated_row",
    "sited_row": "seated_row",
    "seated_narrow_grip_row": "seated_row",
    "seated_cable_row": "seated_row",
    "seated_row": "seated_row",
    "bungkuk_tarik_besi": "barbell_row",
    "barbel_ro": "barbell_row",
    "bb_row": "barbell_row",
    "barbell_row": "barbell_row",
    "gelantungan_tarik_badan": "pull_up",
    "pull_up": "pull_up",
    "pul_ap": "pull_up",
    "pulup": "pull_up",
    "dedlif": "deadlift",
    "detlif": "deadlift",
    "deadlift": "deadlift",
    "er_de_el": "romanian_deadlift",
    "rdl": "romanian_deadlift",
    "romanian_deadlift": "romanian_deadlift",

    # Shoulders
    "lateral_rise": "lateral_raise",
    "lateral_raise": "lateral_raise",
    "buka_tangan_ke_samping": "lateral_raise",
    "kepak_sayap_bahu": "lateral_raise",
    "duduk_dorong_beban_ke_atas": "dumbbell_shoulder_press",
    "solpres": "dumbbell_shoulder_press",
    "soldel_pres": "dumbbell_shoulder_press",
    "incline_shoulder_press": "dumbbell_shoulder_press",
    "dumbbell_shoulder_press": "dumbbell_shoulder_press",
    "peluk_mesin_kebalik": "reverse_fly",
    "bahu_belakang_mesin": "reverse_fly",
    "pec_deck_back_shoulder": "reverse_fly",
    "rear_delt_fly": "reverse_fly",
    "rear_delt_pec_fly": "reverse_fly",
    "back_shoulder_fly": "reverse_fly",
    "reverse_fly": "reverse_fly",
    "tarik_tali_ke_muka": "face_pull",
    "tarik_tali_ke_jidat": "face_pull",
    "feis_pul": "face_pull",
    "feispul": "face_pull",
    "face_pull": "face_pull",
    "gedik_bahu": "dumbbell_shrug",
    "angkat_pundak": "dumbbell_shrug",
    "gaya_ga_tau": "dumbbell_shrug",
    "srag": "dumbbell_shrug",
    "dumbbell_shrug": "dumbbell_shrug",

    # Arms
    "tekuk_lengan": "bicep_curl",
    "pompa_bisep": "bicep_curl",
    "bisep_krol": "bicep_curl",
    "baisep_kerl": "bicep_curl",
    "bicep_curl": "bicep_curl",
    "palu_dambel": "hammer_curl",
    "posisi_martil": "hammer_curl",
    "hemer_krol": "hammer_curl",
    "hammer_curl": "hammer_curl",
    "taruh_lengan_di_bantalan_miring": "preacher_curl",
    "ketiak_nempel_bantalan": "preacher_curl",
    "preachears_curl": "preacher_curl",
    "preachers_curl": "preacher_curl",
    "preacher_curl": "preacher_curl",
    "dorong_tali_ke_bawah": "tricep_pushdown",
    "tekan_kabel_ke_bawah": "tricep_pushdown",
    "tali_trisep": "tricep_pushdown",
    "trisep_pusdon": "tricep_pushdown",
    "pusdon": "tricep_pushdown",
    "tricep_pushdown": "tricep_pushdown",
    "triceps_push_down": "tricep_pushdown",
    "one_arm_triceps_push_down": "single_arm_tricep_pushdown",
    "dorong_tali_dari_belakang_kepala": "overhead_tricep_extension",
    "triceps_overhead_extention": "overhead_tricep_extension",
    "overhead_extension": "overhead_tricep_extension",
    "overhead_tricep_extension": "overhead_tricep_extension",
    "hancur_jidat": "skullcrusher",
    "patah_leher": "skullcrusher",
    "skal_kraser": "skullcrusher",
    "skullcrusher": "skullcrusher",
    "skull_crusher": "skullcrusher",
    "skull_crushers": "skullcrusher",
    "barbell_skullcrusher": "skullcrusher",
    "dumbbell_skullcrusher": "skullcrusher",
    "jm_press": "jm_press",
    "tekuk_pergelangan_tangan": "wrist_curl",
    "forearm_curl": "wrist_curl",
    "forearm_train": "wrist_curl",
    "wrist_curl": "wrist_curl",
    "curl": "wrist_curl",
}

EXERCISE_MUSCLE_MAP = {
    "skullcrusher": "arms",
    "jm_press": "arms",
    "tricep_pushdown": "arms",
    "single_arm_tricep_pushdown": "arms",
    "overhead_tricep_extension": "arms",
    "bicep_curl": "arms",
    "hammer_curl": "arms",
    "preacher_curl": "arms",
    "wrist_curl": "arms",
    "incline_chest_press": "chest",
    "barbell_bench_press": "chest",
    "incline_dumbbell_press": "chest",
    "pec_deck": "chest",
    "push_up": "chest",
    "dips": "chest",
    "lat_pulldown": "back",
    "seated_row": "back",
    "barbell_row": "back",
    "pull_up": "back",
    "deadlift": "back",
    "romanian_deadlift": "back",
    "t_bar_row": "back",
    "barbell_squat": "legs",
    "leg_press": "legs",
    "leg_extension": "legs",
    "leg_curl": "legs",
    "hip_thrust": "legs",
    "hip_abduction": "legs",
    "hip_adduction": "legs",
    "bulgarian_split_squat": "legs",
    "calf_raise": "legs",
    "lateral_raise": "shoulders",
    "dumbbell_shoulder_press": "shoulders",
    "overhead_press": "shoulders",
    "reverse_fly": "shoulders",
    "face_pull": "shoulders",
    "dumbbell_shrug": "shoulders",
    "hanging_leg_raise": "core",
    "ab_wheel": "core",
    "plank": "core",
}

def normalize_canonical(raw_canonical: str, raw_name: str = "") -> str:
    cleaned_c = re.sub(r'[^a-z0-9_]', '', raw_canonical.lower().strip().replace(' ', '_'))
    cleaned_n = re.sub(r'[^a-z0-9_]', '', raw_name.lower().strip().replace(' ', '_')) if raw_name else ""
    
    # 1. Cek dari nama gerakan terlebih dahulu jika cocok dengan kamus
    if cleaned_n and cleaned_n in CANONICAL_MAP:
        return CANONICAL_MAP[cleaned_n]
    # 2. Cek dari canonical hasil output model
    if cleaned_c in CANONICAL_MAP:
        return CANONICAL_MAP[cleaned_c]
    return cleaned_c

@app.post("/api/parse")
async def parse_log(request: ParseRequest):
    """
    Endpoint ini nembak langsung ke llama-server lokal.
    Hanya me-return hasil JSON, TIDAK menyimpan ke database.
    Fitur AI Eksklusif: Memerlukan Akun PRO jika account_id disediakan.
    """
    if request.account_id:
        acc_status = get_account_status(request.account_id)
        if not acc_status.get("is_pro"):
            return {
                "status": "pro_required",
                "message": "Fitur AI Text Parser eksklusif untuk member PRO. Gunakan voucher demo 'PGYM-PRO-2026' atau scan QRIS di menu Akun!"
            }

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
            
            # Normalisasi canonical, sanitasi set, dan deduplikasi global
            global_seen = set()
            clean_sessions = []
            for session in ai_output.get("sessions", []):
                unique_ex = []
                for ex in session.get("exercises", []):
                    raw_c = ex.get("canonical", "")
                    raw_n = ex.get("name", "")
                    normalized_c = normalize_canonical(raw_c, raw_n)
                    ex["canonical"] = normalized_c

                    # Perbaiki muscle_group jika salah klasifikasi
                    if normalized_c in EXERCISE_MUSCLE_MAP:
                        cur_mg = session.get("muscle_group", "").lower()
                        if cur_mg in ["body_part_exercises", "body_part_exercise", "other", ""] or (normalized_c in ["skullcrusher", "jm_press"] and cur_mg == "shoulders"):
                            session["muscle_group"] = EXERCISE_MUSCLE_MAP[normalized_c]
                    
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

                    if normalized_c not in global_seen and len(clean_sets) > 0:
                        global_seen.add(normalized_c)
                        unique_ex.append(ex)
                
                if unique_ex:
                    session["exercises"] = unique_ex
                    clean_sessions.append(session)

            ai_output["sessions"] = clean_sessions
            return {"status": "success", "data": ai_output}
    except Exception as e:
        return {"status": "error", "message": f"Koneksi ke AI runtime gagal ({str(e)}). Pastikan llama-server berjalan di port 8080."}

@app.post("/api/save")
async def save_log(data: dict):
    """Menerima JSON yang sudah diedit/divalidasi user dan menyimpannya ke DB"""
    try:
        save_workout_log(data)
        return {
            "status": "success",
            "rank": get_competitive_rank_info(),
            "session_summary": get_today_session_summary(data.get("date"))
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/history")
async def get_history():
    """Endpoint untuk mengambil semua data riwayat dari database"""
    return get_all_history()

@app.get("/api/progress/exercise/{canonical_name}")
async def api_exercise_progress(canonical_name: str):
    return get_exercise_progress(canonical_name)

@app.get("/api/progress/recap")
async def api_recap(period: str = "month"):
    return get_workout_recap(period)

@app.get("/api/exercises/list")
async def get_exercises_list():
    return get_all_distinct_exercises()

@app.get("/api/schedule")
async def api_get_schedule():
    return get_schedule() or {}

@app.post("/api/schedule")
async def api_save_schedule(new_sched: dict):
    save_schedule(new_sched)
    return {"status": "success"}

# --- AI VIDEO FORM CHECK ENDPOINT ---
@app.post("/api/analyze-video")
def analyze_video_endpoint(
    video: UploadFile = File(...),
    exercise: str = Form("squat"),
    account_id: Optional[str] = Form(None)
):
    """Menganalisis video latihan menggunakan YOLOv8n-pose dan menghitung repetisi & kedalaman"""
    if account_id:
        acc_status = get_account_status(account_id)
        if not acc_status.get("is_pro"):
            return {
                "status": "pro_required",
                "message": "Fitur AI Video Form Check eksklusif untuk member PRO. Gunakan voucher demo 'PGYM-PRO-2026' atau scan QRIS di menu Akun!"
            }

    try:
        print(f"--> [DEBUG] 1. Upload received: {video.filename}, exercise={exercise}", flush=True)
        uploads_dir = os.path.join(os.path.dirname(__file__), "../frontend/uploads")
        processed_dir = os.path.join(os.path.dirname(__file__), "../frontend/processed")
        os.makedirs(uploads_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)

        file_id = str(uuid.uuid4())[:8]
        ext = os.path.splitext(video.filename)[1] or ".mp4"
        input_path = os.path.join(uploads_dir, f"raw_{file_id}{ext}")
        output_filename = f"annotated_{file_id}.mp4"
        output_path = os.path.join(processed_dir, output_filename)

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        print(f"--> [DEBUG] 2. File saved to {input_path} ({os.path.getsize(input_path)} bytes)", flush=True)

        print(f"--> [DEBUG] 3. Starting analyze_video...", flush=True)
        result = pose_analyzer_instance.analyze_video(input_path, output_path, exercise=exercise)
        print(f"--> [DEBUG] 4. Analysis complete! Result: {result}", flush=True)

        # Auto-delete video mentah segera setelah analisis demi privasi & hemat ruang disk
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
                print(f"--> [PRIVACY] Video mentah {input_path} berhasil dihapus otomatis.", flush=True)
        except Exception as e:
            print(f"--> [WARN] Gagal auto-delete video mentah {input_path}: {e}", flush=True)

        return result
    except Exception as e:
        print(f"--> [DEBUG] ERROR in video endpoint: {e}", flush=True)
        return {"status": "error", "message": str(e)}


# --- DATA EXPORT ENDPOINTS (CSV & JSON) ---

@app.get("/api/export/csv")
async def export_csv():
    """Mengunduh seluruh database riwayat latihan user dalam format CSV (Data Ownership / Anti-Lockin)"""
    records = get_all_workout_records_flat()
    output = io.StringIO()
    fieldnames = [
        "date", "muscle_group", "exercise_name", "canonical",
        "set_id", "weight_kg", "reps", "rpe", "note", "per_hand", "session_note"
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for r in records:
        writer.writerow(r)
    output.seek(0)
    
    filename = f"postgym_workouts_{datetime.today().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/export/json")
async def export_json():
    """Mengunduh seluruh database riwayat latihan user dalam format JSON"""
    records = get_all_workout_records_flat()
    filename = f"postgym_workouts_{datetime.today().strftime('%Y%m%d')}.json"
    return JSONResponse(
        content={
            "status": "success",
            "app": "POST GYM",
            "exported_at": datetime.utcnow().isoformat(),
            "total_records": len(records),
            "data": records
        },
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# --- MULLVAD-STYLE ANONYMOUS ACCOUNTS & MONETIZATION ENDPOINTS ---

@app.post("/api/account/generate")
async def api_generate_account():
    """Membuat 16-digit Account ID baru tanpa email / nama / password (Cypherpunk Privacy)"""
    return generate_anonymous_account()

@app.get("/api/account/status")
async def api_account_status(id: str):
    """Mengecek status Free / Pro serta sisa masa aktif akun"""
    if not id:
        return {"status": "error", "message": "Query param 'id' diperlukan"}
    return get_account_status(id)

@app.post("/api/account/redeem")
async def api_redeem_voucher(req: dict):
    """Menebus voucher langganan PRO (contoh: PGYM-PRO-2026)"""
    account_id = req.get("account_id")
    voucher_code = req.get("voucher_code")
    if not account_id or not voucher_code:
        return {"status": "error", "message": "Account ID dan Kode Voucher wajib diisi!"}
    return redeem_voucher_code(account_id, voucher_code)

@app.post("/api/account/simulate-qris")
async def api_simulate_qris(req: dict):
    """Simulasi pembayaran instan QRIS untuk presentasi dosen"""
    account_id = req.get("account_id")
    duration = int(req.get("duration_days", 30))
    if not account_id:
        return {"status": "error", "message": "Account ID wajib diisi!"}
    return simulate_qris(account_id, duration)


# --- SERVE FRONTEND & PROCESSED MEDIA ---
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
processed_path = os.path.join(frontend_path, "processed")
os.makedirs(processed_path, exist_ok=True)

app.mount("/processed", StaticFiles(directory=processed_path), name="processed")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
