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

    conn.commit()
    conn.close()

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
    
    date = parsed_json['date']
    note = parsed_json.get('session_note')
    
    # Insert sesi (abaikan kalau hari itu udah ada, atau bisa juga update)
    cursor.execute("INSERT OR IGNORE INTO workout_sessions (date, session_note) VALUES (?, ?)", (date, note))
    
    # Ambil ID sesi
    cursor.execute("SELECT id FROM workout_sessions WHERE date = ?", (date,))
    session_id = cursor.fetchone()['id']
    
    # Insert semua exercise dan set
    for group in parsed_json['sessions']:
        muscle = group['muscle_group']
        for ex in group['exercises']:
            cursor.execute('''
                INSERT INTO exercises (session_id, muscle_group, name, canonical) 
                VALUES (?, ?, ?, ?)
            ''', (session_id, muscle, ex['name'], ex['canonical']))
            
    try:
        date = parsed_json['date']
        note = parsed_json.get('session_note')
        
        # Insert sesi (abaikan kalau hari itu udah ada, atau bisa juga update)
        cursor.execute("INSERT OR IGNORE INTO workout_sessions (date, session_note) VALUES (?, ?)", (date, note))
        
        # Ambil ID sesi
        cursor.execute("SELECT id FROM workout_sessions WHERE date = ?", (date,))
        session_id = cursor.fetchone()['id']
        
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
