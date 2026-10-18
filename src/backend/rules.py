def calculate_next_target(history_sets, rep_range=(8, 12), weight_increment=None, muscle_group="other"):
    """
    Menghitung target beban dan repetisi untuk sesi berikutnya
    menggunakan metode Double Progression (Gold Standard Hipertrofi).
    
    history_sets: list of dict, contoh: [{'weight': 15, 'reps': 10}, ...]
    rep_range: tuple (min_reps, max_reps)
    weight_increment: float opsional. Jika None, otomatis adaptif berdasarkan otot:
      - Compound / Otot Besar (chest, back, legs): +2.5 kg
      - Isolasi / Otot Kecil (shoulders, arms, core, calves): +1.0 kg (micro-loading anti-ego lifting)
    """
    if not history_sets:
        return {"action": "maintain", "weight": None, "target_reps": f"{rep_range[0]}-{rep_range[1]}", "message": "Belum ada data, cari beban awalmu."}

    min_rep_target, max_rep_target = rep_range
    current_weight = history_sets[0]['weight'] # Asumsi beban acuan sesi terakhir
    
    reps_achieved = [s['reps'] for s in history_sets if s.get('reps', 0) > 0]
    if not reps_achieved:
        return {"action": "maintain", "weight": current_weight, "target_reps": f"{min_rep_target}-{max_rep_target}", "message": "Fokus pada beban awal."}

    # Tentukan kenaikan beban adaptif jika tidak ditentukan secara manual
    if weight_increment is None:
        mg = str(muscle_group).lower()
        if mg in ['chest', 'back', 'legs', 'compound']:
            weight_increment = 2.5
        elif mg in ['shoulders', 'arms', 'biceps', 'triceps', 'core', 'calves']:
            weight_increment = 1.0  # Micro-loading agar form tidak rusak
        else:
            weight_increment = 2.5

    # 1. Deteksi kegagalan ekstrim (di bawah batas minimal, misal < 8 rep)
    if any(r < min_rep_target for r in reps_achieved):
        deload_weight = current_weight * 0.95 # Turunkan 5%
        deload_rounded = round(deload_weight / 0.5) * 0.5
        return {
            "action": "deload",
            "weight": deload_rounded,
            "target_reps": f"{min_rep_target}-{max_rep_target}",
            "message": f"Belum tembus batas minimal ({min_rep_target} rep). Turunkan beban sedikit ke {deload_rounded}kg agar form tetap aman (Deload)."
        }

    # 2. Double Progression: Cek apakah semua working sets tembus batas atas (>= 12 rep)
    # Minimal 2 working sets
    if all(r >= max_rep_target for r in reps_achieved) and len(reps_achieved) >= 2:
        next_weight = round((current_weight + weight_increment) * 2) / 2
        return {
            "action": "progress_weight",
            "weight": next_weight,
            "target_reps": f"{min_rep_target}",
            "message": f"Keren! Kamu sudah tembus batas atas (≥{max_rep_target} reps). Naikkan beban (+{weight_increment}kg) ke {next_weight}kg, targetkan kembali minimal {min_rep_target} rep."
        }
    
    # 3. Kalau belum semua set tembus batas atas, pertahankan beban dan kejar repetisi
    return {
        "action": "progress_reps",
        "weight": current_weight,
        "target_reps": f"{min_rep_target}-{max_rep_target}",
        "message": f"Beban dipertahankan di {current_weight}kg. Fokus tambah repetisi sampai semua set tembus {max_rep_target} rep (Double Progression)."
    }

# --- TEST LOGIC ---
if __name__ == "__main__":
    print("Test 1: Belum nyampe batas atas (Incline Press 15kg: 11, 10, 8)")
    hasil = calculate_next_target([{'weight': 15, 'reps': 11}, {'weight': 15, 'reps': 10}, {'weight': 15, 'reps': 8}])
    print("Saran AI:", hasil['message'], "| Target Beban:", hasil['weight'])
    
    print("\nTest 2: Tembus batas atas! (Pec Deck 16kg: 12, 12, 12)")
    hasil = calculate_next_target([{'weight': 16, 'reps': 12}, {'weight': 16, 'reps': 12}, {'weight': 16, 'reps': 12}])
    print("Saran AI:", hasil['message'], "| Target Beban:", hasil['weight'])

    print("\nTest 3: Underperforming / Gagal (JM Press 15kg: 8, 7, 5)")
    hasil = calculate_next_target([{'weight': 15, 'reps': 8}, {'weight': 15, 'reps': 7}, {'weight': 15, 'reps': 5}])
    print("Saran AI:", hasil['message'], "| Target Beban:", hasil['weight'])
