def calculate_next_target(history_sets, rep_range=(8, 12), weight_increment=2.5):
    """
    Menghitung target beban dan repetisi untuk sesi berikutnya
    menggunakan metode Double Progression.
    
    history_sets: list of dict, contoh: [{'weight': 15, 'reps': 10}, ...]
    rep_range: tuple (min_reps, max_reps)
    """
    if not history_sets:
        return {"action": "maintain", "weight": None, "target_reps": "8-12", "message": "Belum ada data, cari beban awalmu."}

    min_rep_target, max_rep_target = rep_range
    current_weight = history_sets[0]['weight'] # Asumsi semua set bebannya sama untuk penyederhanaan
    
    reps_achieved = [s['reps'] for s in history_sets if s['reps'] > 0]
    
    # Deteksi kegagalan ekstrim (di bawah batas bawah)
    if any(r < min_rep_target for r in reps_achieved):
        deload_weight = current_weight * 0.95 # Turunkan 5%
        return {
            "action": "deload",
            "weight": round(deload_weight / 0.5) * 0.5, # Bulatkan ke 0.5kg terdekat
            "target_reps": f"{min_rep_target}-{max_rep_target}",
            "message": "Kamu gagal mencapai repetisi minimal. Turunkan beban 5% agar form tetap aman (Deload)."
        }

    # Double Progression: Cek apakah semua set mencapai max rep
    if all(r >= max_rep_target for r in reps_achieved) and len(reps_achieved) >= 3:
        next_weight = current_weight + weight_increment
        return {
            "action": "progress_weight",
            "weight": next_weight,
            "target_reps": f"{min_rep_target}",
            "message": f"Keren! Kamu sudah tembus batas atas. Saatnya naik beban ke {next_weight}kg, targetkan minimal {min_rep_target} rep."
        }
    
    # Kalau belum tembus batas atas, tahan beban, tambah rep
    return {
        "action": "progress_reps",
        "weight": current_weight,
        "target_reps": "Tambah rep dari sesi lalu!",
        "message": "Beban dipertahankan. Fokus tambah total repetisi atau perbaiki form (Double Progression)."
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
