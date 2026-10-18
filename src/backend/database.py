import sqlite3
import json
from datetime import datetime
import os

# Gunakan absolute path agar selalu mengarah ke direktori file ini
DB_PATH = os.path.join(os.path.dirname(__file__), "gymmate.db")

def get_connection():
    # Koneksi ke database (kalau file belum ada, otomatis dibikin)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Biar hasilnya bisa diakses kayak dictionary
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Tabel Konfigurasi (Untuk simpan jadwal user)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')

    # 2. Tabel Sesi Latihan (Tanggal & Catatan umum)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workout_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE,
        session_note TEXT
    )
    ''')

    # 3. Tabel Gerakan / Exercise (Nyambung ke sesi)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        muscle_group TEXT,
        name TEXT,
        canonical TEXT,
        FOREIGN KEY (session_id) REFERENCES workout_sessions (id)
    )
    ''')

    # 4. Tabel Sets (Nyambung ke exercise)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_id INTEGER,
        weight_kg REAL,
        reps INTEGER,
        rpe INTEGER,
        note TEXT,
        per_hand BOOLEAN,
        FOREIGN KEY (exercise_id) REFERENCES exercises (id)
    )
    ''')

    # 5. Tabel Akun (Mullvad-style 16-digit ID)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        account_id TEXT PRIMARY KEY,
        is_pro INTEGER DEFAULT 0,
        pro_expires_at TEXT,
        created_at TEXT
    )
    ''')

    # 6. Tabel Voucher
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vouchers (
        code TEXT PRIMARY KEY,
        duration_days INTEGER DEFAULT 30,
        is_redeemed INTEGER DEFAULT 0,
        redeemed_by TEXT,
        redeemed_at TEXT
    )
    ''')

    # 7. Tabel Riwayat Klaim Voucher per Akun (Mendukung promo code multi-user)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS account_voucher_redemptions (
        account_id TEXT,
        code TEXT,
        redeemed_at TEXT,
        PRIMARY KEY (account_id, code)
    )
    ''')

    # Seed demo voucher gratis untuk pengujian & presentasi dosen
    demo_vouchers = [
        ("PGYM-PRO-2026", 30),
        ("POSTGYM-SUPER-PASS", 60),
        ("DOSEN-NILAI-A-PLUS", 365),
    ]
    for code, days in demo_vouchers:
        cursor.execute("INSERT OR IGNORE INTO vouchers (code, duration_days, is_redeemed) VALUES (?, ?, 0)", (code, days))

    conn.commit()
    conn.close()

# Inisialisasi database otomatis saat modul dimuat
init_db()

# --- FUNGSI-FUNGSI HELPER ---

def save_schedule(schedule_dict):
    """Simpan jadwal gym (Crot dalam) ke database"""
    conn = get_connection()
    conn.cursor().execute(
        "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
        ("weekly_schedule", json.dumps(schedule_dict))
    )
    conn.commit()
    conn.close()

def get_schedule():
    """Ambil jadwal gym dari database"""
    conn = get_connection()
    row = conn.cursor().execute("SELECT value FROM config WHERE key = 'weekly_schedule'").fetchone()
    conn.close()
    return json.loads(row['value']) if row else None

def save_workout_log(parsed_json):
    """Simpan hasil parsing AI (JSON) ke SQLite"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        date = parsed_json['date']
        note = parsed_json.get('session_note')
        
        # Insert sesi (abaikan kalau hari itu udah ada, atau bisa juga update)
        cursor.execute("INSERT OR IGNORE INTO workout_sessions (date, session_note) VALUES (?, ?)", (date, note))
        
        # Ambil ID sesi
        cursor.execute("SELECT id FROM workout_sessions WHERE date = ?", (date,))
        session_id = cursor.fetchone()['id']

        # Bersihkan data lama tanggal ini supaya simpan ulang tidak menumpuk data
        cursor.execute("DELETE FROM sets WHERE exercise_id IN (SELECT id FROM exercises WHERE session_id = ?)", (session_id,))
        cursor.execute("DELETE FROM exercises WHERE session_id = ?", (session_id,))
        cursor.execute("UPDATE workout_sessions SET session_note = ? WHERE id = ?", (note, session_id))

        # Insert semua exercise dan set
        for group in parsed_json['sessions']:
            muscle = group['muscle_group']
            for ex in group['exercises']:
                cursor.execute('''
                    INSERT INTO exercises (session_id, muscle_group, name, canonical) 
                    VALUES (?, ?, ?, ?)
                ''', (session_id, muscle, ex['name'], ex['canonical']))
                
                ex_id = cursor.lastrowid
                
                for s in ex['sets']:
                    cursor.execute('''
                        INSERT INTO sets (exercise_id, weight_kg, reps, rpe, note, per_hand)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (ex_id, s.get('weight_kg', 0), s['reps'], s.get('rpe'), s.get('note'), s.get('per_hand', False)))
                    
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_history():
    conn = get_connection()
    sessions = conn.execute("SELECT * FROM workout_sessions ORDER BY date DESC").fetchall()
    
    result = []
    for s in sessions:
        exs = conn.execute("SELECT * FROM exercises WHERE session_id = ?", (s['id'],)).fetchall()
        ex_list = []
        for e in exs:
            sets = conn.execute("SELECT weight_kg AS weight, reps FROM sets WHERE exercise_id = ?", (e['id'],)).fetchall()
            ex_list.append({
                "name": e['name'],
                "sets_summary": ", ".join([f"{st['weight']}kg x {st['reps']}" for st in sets])
            })
        result.append({
            "date": s['date'],
            "note": s['session_note'],
            "exercises": ex_list
        })
    conn.close()
    return result

def get_exercise_progress(canonical_name):
    conn = get_connection()
    query = '''
        SELECT ws.date, 
               MAX(CASE WHEN s.per_hand = 1 THEN s.weight_kg * 2 ELSE s.weight_kg END) as max_weight
        FROM workout_sessions ws
        JOIN exercises e ON e.session_id = ws.id
        JOIN sets s ON s.exercise_id = e.id
        WHERE e.canonical = ?
        GROUP BY ws.date
        ORDER BY ws.date ASC
    '''
    rows = conn.execute(query, (canonical_name,)).fetchall()
    conn.close()
    return [{"date": r["date"], "max_weight": r["max_weight"]} for r in rows]

def get_workout_recap(period="month"):
    conn = get_connection()
    if period == "week":
        fmt = '%Y-W%W'
    elif period == "year":
        fmt = '%Y'
    else: # month default
        fmt = '%Y-%m'
        
    query = f'''
        SELECT strftime('{fmt}', date) as period, COUNT(*) as sessions
        FROM workout_sessions
        GROUP BY period
        ORDER BY period ASC
    '''
    rows = conn.execute(query).fetchall()
    conn.close()
    return [{"period": r["period"], "sessions": r["sessions"]} for r in rows]

def get_last_history(canonical_name):
    """Cari history terakhir dari suatu gerakan"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Cari sesi terakhir dimana gerakan ini dilakukan
    query = '''
        SELECT ws.date, s.weight_kg, s.reps, s.note
        FROM exercises e
        JOIN workout_sessions ws ON e.session_id = ws.id
        JOIN sets s ON s.exercise_id = e.id
        WHERE e.canonical = ?
        ORDER BY ws.date DESC
    '''
    
    rows = cursor.execute(query, (canonical_name,)).fetchall()
    conn.close()
    
    if not rows:
        return None
        
    # Group berdasarkan tanggal
    last_date = rows[0]['date']
    last_sets = [{"weight": r['weight_kg'], "reps": r['reps'], "note": r['note']} for r in rows if r['date'] == last_date]
    
    return {"date": last_date, "sets": last_sets}


# --- QUICK LOG (1-TAP LOGGING FOR FREE TIER) ---

def quick_log_set(canonical: str, name: str, muscle_group: str, weight_kg: float, reps: int, note: str = "", date_str: str = None):
    """
    Menyimpan 1 set latihan langsung ke sesi hari ini tanpa perlu AI parser.
    Sangat cepat, hemat resource, dan cocok untuk Free Tier.
    """
    if not date_str:
        date_str = datetime.today().strftime('%Y-%m-%d')
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Pastikan sesi hari ini ada
        cursor.execute("INSERT OR IGNORE INTO workout_sessions (date, session_note) VALUES (?, ?)", (date_str, ""))
        cursor.execute("SELECT id FROM workout_sessions WHERE date = ?", (date_str,))
        session_id = cursor.fetchone()['id']

        # 2. Cari apakah gerakan ini sudah ada di sesi hari ini
        cursor.execute("SELECT id FROM exercises WHERE session_id = ? AND canonical = ?", (session_id, canonical))
        ex_row = cursor.fetchone()
        if ex_row:
            ex_id = ex_row['id']
        else:
            cursor.execute(
                "INSERT INTO exercises (session_id, muscle_group, name, canonical) VALUES (?, ?, ?, ?)",
                (session_id, muscle_group, name, canonical)
            )
            ex_id = cursor.lastrowid

        # 3. Masukkan set baru
        cursor.execute(
            "INSERT INTO sets (exercise_id, weight_kg, reps, rpe, note, per_hand) VALUES (?, ?, ?, ?, ?, ?)",
            (ex_id, float(weight_kg), int(reps), None, note, False)
        )
        set_id = cursor.lastrowid

        # 4. Ambil ringkasan set hari ini untuk gerakan ini
        sets_rows = cursor.execute(
            "SELECT id, weight_kg, reps, note FROM sets WHERE exercise_id = ? ORDER BY id ASC",
            (ex_id,)
        ).fetchall()
        
        conn.commit()
        return {
            "status": "success",
            "session_id": session_id,
            "exercise_id": ex_id,
            "set_id": set_id,
            "today_sets": [{"id": r["id"], "weight": r["weight_kg"], "reps": r["reps"], "note": r["note"]} for r in sets_rows]
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def undo_last_set(canonical: str, date_str: str = None):
    """Membatalkan set terakhir yang baru dicatat untuk gerakan ini hari ini"""
    if not date_str:
        date_str = datetime.today().strftime('%Y-%m-%d')
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM workout_sessions WHERE date = ?", (date_str,))
        session = cursor.fetchone()
        if not session:
            return {"status": "error", "message": "Tidak ada sesi hari ini"}
            
        cursor.execute("SELECT id FROM exercises WHERE session_id = ? AND canonical = ?", (session['id'], canonical))
        ex = cursor.fetchone()
        if not ex:
            return {"status": "error", "message": "Gerakan belum tercatat hari ini"}
            
        cursor.execute("SELECT id FROM sets WHERE exercise_id = ? ORDER BY id DESC LIMIT 1", (ex['id'],))
        last_s = cursor.fetchone()
        if not last_s:
            return {"status": "error", "message": "Tidak ada set yang bisa dibatalkan"}
            
        cursor.execute("DELETE FROM sets WHERE id = ?", (last_s['id'],))
        
        # Cek sisa set
        cursor.execute("SELECT COUNT(*) FROM sets WHERE exercise_id = ?", (ex['id'],))
        remaining = cursor.fetchone()[0]
        if remaining == 0:
            cursor.execute("DELETE FROM exercises WHERE id = ?", (ex['id'],))
            
        conn.commit()
        return {"status": "success", "remaining_sets": remaining}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# --- DATA EXPORT (CSV & JSON) ---

def get_all_workout_records_flat():
    """Mengambil seluruh data latihan dari SQLite dalam format flat untuk CSV / JSON Export"""
    conn = get_connection()
    query = '''
        SELECT 
            ws.date,
            e.muscle_group,
            e.name AS exercise_name,
            e.canonical,
            s.id AS set_id,
            s.weight_kg,
            s.reps,
            s.rpe,
            s.note,
            s.per_hand,
            ws.session_note
        FROM workout_sessions ws
        JOIN exercises e ON e.session_id = ws.id
        JOIN sets s ON s.exercise_id = e.id
        ORDER BY ws.date DESC, e.id ASC, s.id ASC
    '''
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- MULLVAD-STYLE ANONYMOUS ACCOUNTS & MONETIZATION ---

import secrets
from datetime import timedelta

def generate_anonymous_account():
    """Membuat 16-digit Account ID unik bergaya Mullvad (Zero PII, privasi 100%)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Format: PGYM-XXXX-XXXX-XXXX-XXXX (16 digit angka)
    for _ in range(10):
        p1 = secrets.randbelow(9000) + 1000
        p2 = secrets.randbelow(9000) + 1000
        p3 = secrets.randbelow(9000) + 1000
        p4 = secrets.randbelow(9000) + 1000
        account_id = f"PGYM-{p1}-{p2}-{p3}-{p4}"
        
        existing = cursor.execute("SELECT account_id FROM accounts WHERE account_id = ?", (account_id,)).fetchone()
        if not existing:
            created_at = datetime.utcnow().isoformat()
            cursor.execute(
                "INSERT INTO accounts (account_id, is_pro, pro_expires_at, created_at) VALUES (?, 0, NULL, ?)",
                (account_id, created_at)
            )
            conn.commit()
            conn.close()
            return {
                "account_id": account_id,
                "is_pro": False,
                "pro_expires_at": None,
                "created_at": created_at
            }
            
    conn.close()
    raise RuntimeError("Gagal generate account id unik")

def get_account_status(account_id: str):
    """Mengecek status akun dan tanggal kedaluwarsa PRO"""
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM accounts WHERE account_id = ?", (account_id,)).fetchone()
    
    if not row:
        # Jika akun belum ada di DB, buatkan secara otomatis
        conn.close()
        created_at = datetime.utcnow().isoformat()
        conn = get_connection()
        conn.execute(
            "INSERT OR IGNORE INTO accounts (account_id, is_pro, pro_expires_at, created_at) VALUES (?, 0, NULL, ?)",
            (account_id, created_at)
        )
        conn.commit()
        conn.close()
        return {
            "account_id": account_id,
            "is_pro": False,
            "pro_expires_at": None,
            "days_remaining": 0
        }
        
    is_pro = bool(row["is_pro"])
    pro_expires_at = row["pro_expires_at"]
    days_remaining = 0
    
    if is_pro and pro_expires_at:
        try:
            exp_dt = datetime.fromisoformat(pro_expires_at)
            now_dt = datetime.utcnow()
            if exp_dt < now_dt:
                # Masa aktif habis
                is_pro = False
                cursor.execute("UPDATE accounts SET is_pro = 0 WHERE account_id = ?", (account_id,))
                conn.commit()
            else:
                days_remaining = max(1, (exp_dt - now_dt).days + 1)
        except Exception:
            is_pro = False
            
    conn.close()
    return {
        "account_id": account_id,
        "is_pro": is_pro,
        "pro_expires_at": pro_expires_at if is_pro else None,
        "days_remaining": days_remaining
    }

def redeem_voucher_code(account_id: str, voucher_code: str):
    """Aktivasi voucher langganan PRO (1 akun hanya dapat klaim 1 kali per kode voucher)"""
    clean_code = voucher_code.strip().upper()
    conn = get_connection()
    cursor = conn.cursor()
    
    voucher = cursor.execute("SELECT * FROM vouchers WHERE UPPER(code) = ?", (clean_code,)).fetchone()
    if not voucher:
        conn.close()
        return {"status": "error", "message": "Kode voucher tidak valid!"}

    # Cek apakah akun ini sudah pernah klaim kode ini
    already = cursor.execute(
        "SELECT 1 FROM account_voucher_redemptions WHERE account_id = ? AND UPPER(code) = ?",
        (account_id, clean_code)
    ).fetchone()
    if already:
        conn.close()
        return {"status": "error", "message": "Akun ini sudah pernah mengklaim voucher tersebut!"}
        
    # Pastikan akun ada
    cursor.execute("INSERT OR IGNORE INTO accounts (account_id, is_pro, pro_expires_at, created_at) VALUES (?, 0, NULL, ?)",
                   (account_id, datetime.utcnow().isoformat()))
    
    acc = cursor.execute("SELECT * FROM accounts WHERE account_id = ?", (account_id,)).fetchone()
    now_dt = datetime.utcnow()
    duration = voucher["duration_days"]
    
    if acc["is_pro"] and acc["pro_expires_at"]:
        try:
            current_exp = datetime.fromisoformat(acc["pro_expires_at"])
            base_dt = current_exp if current_exp > now_dt else now_dt
        except Exception:
            base_dt = now_dt
    else:
        base_dt = now_dt
        
    new_expires_at = (base_dt + timedelta(days=duration)).isoformat()
    
    cursor.execute("UPDATE accounts SET is_pro = 1, pro_expires_at = ? WHERE account_id = ?", (new_expires_at, account_id))
    cursor.execute(
        "INSERT INTO account_voucher_redemptions (account_id, code, redeemed_at) VALUES (?, ?, ?)",
        (account_id, clean_code, now_dt.isoformat())
    )
    
    conn.commit()
    conn.close()
    return {
        "status": "success",
        "message": f"Selamat! PRO aktif selama +{duration} hari.",
        "account_id": account_id,
        "is_pro": True,
        "pro_expires_at": new_expires_at,
        "days_added": duration
    }

def simulate_qris(account_id: str, duration_days: int = 30):
    """Simulasi pembayaran instan QRIS (keperluan demo dosen tanpa gateway sungguhan)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT OR IGNORE INTO accounts (account_id, is_pro, pro_expires_at, created_at) VALUES (?, 0, NULL, ?)",
                   (account_id, datetime.utcnow().isoformat()))
    
    acc = cursor.execute("SELECT * FROM accounts WHERE account_id = ?", (account_id,)).fetchone()
    now_dt = datetime.utcnow()
    
    if acc["is_pro"] and acc["pro_expires_at"]:
        try:
            current_exp = datetime.fromisoformat(acc["pro_expires_at"])
            base_dt = current_exp if current_exp > now_dt else now_dt
        except Exception:
            base_dt = now_dt
    else:
        base_dt = now_dt
        
    new_expires_at = (base_dt + timedelta(days=duration_days)).isoformat()
    
    cursor.execute("UPDATE accounts SET is_pro = 1, pro_expires_at = ? WHERE account_id = ?", (new_expires_at, account_id))
    conn.commit()
    conn.close()
    return {
        "status": "success",
        "message": f"Pembayaran QRIS Rp 25.000 Terverifikasi! Akun PRO aktif +{duration_days} hari.",
        "account_id": account_id,
        "is_pro": True,
        "pro_expires_at": new_expires_at
    }

