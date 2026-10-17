#!/usr/bin/env python3
"""
POST GYM — Indonesian Gym Slang & Edge-Case Dataset Generator
Menghasilkan sample gold dataset berisi variasi bahasa gaul, typo fonetis,
istilah deskriptif gerakan fisik, dan frasa kocak khas gym Indonesia.
"""

import os
import json
import random

GOLD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataset", "gold")

# Definisi kamus variasi slang per gerakan
EXERCISE_SLANGS = [
    # CORE
    {
        "names": ["begantung kaki naik naik", "gelantungan angkat kaki", "gantungan angkat kaki", "leg up in bar", "angkat kaki di tiang pullup"],
        "canonical": "hanging_leg_raise",
        "muscle_group": "core",
        "weights": [0.0],
        "reps_range": [8, 15],
        "is_bodyweight": True
    },
    {
        "names": ["roda gelinding perut", "dorong roda lantai", "roda perut", "abilow core", "roll perut"],
        "canonical": "ab_wheel",
        "muscle_group": "core",
        "weights": [0.0],
        "reps_range": [10, 20],
        "is_bodyweight": True
    },
    {
        "names": ["tahan badan lurus tiarap", "posisi push up diem", "tahan perut gemeter", "plang", "plenk"],
        "canonical": "plank",
        "muscle_group": "core",
        "weights": [0.0],
        "reps_range": [30, 60],
        "is_bodyweight": True
    },
    # LEGS
    {
        "names": ["pantat naik turun", "genjot bar", "dorong pinggul ke atas", "hiptrast", "hip trust", "sodok barbel pake panggul"],
        "canonical": "hip_thrust",
        "muscle_group": "legs",
        "weights": [30.0, 40.0, 50.0, 60.0, 70.0, 80.0],
        "reps_range": [8, 12]
    },
    {
        "names": ["kangkang mesin", "buka paha", "mesin kangkang", "hip abduksen", "abduktor paha luar"],
        "canonical": "hip_abduction",
        "muscle_group": "legs",
        "weights": [25.0, 30.0, 35.0, 40.0, 45.0],
        "reps_range": [10, 15]
    },
    {
        "names": ["jepit paha", "rapat paha", "adducter ke dalam", "mesin jepit paha", "adductor"],
        "canonical": "hip_adduction",
        "muscle_group": "legs",
        "weights": [20.0, 25.0, 30.0, 35.0],
        "reps_range": [10, 15]
    },
    {
        "names": ["squad bar only", "skot bar doang", "skwat batang doang", "jongkok pikul besi", "skot kosongan"],
        "canonical": "barbell_squat",
        "muscle_group": "legs",
        "weights": [20.0],
        "reps_range": [8, 12]
    },
    {
        "names": ["dorong plat miring", "injek mesin", "lek pres", "legpres", "dorong bantalan kaki"],
        "canonical": "leg_press",
        "muscle_group": "legs",
        "weights": [60.0, 80.0, 100.0, 120.0, 150.0],
        "reps_range": [8, 12]
    },
    {
        "names": ["tendang kaki ke depan", "lurusin dengkul", "lek eksten", "ekstensi kaki", "tendang mesin ke atas"],
        "canonical": "leg_extension",
        "muscle_group": "legs",
        "weights": [25.0, 30.0, 35.0, 40.0],
        "reps_range": [10, 15]
    },
    {
        "names": ["tekuk kaki ke belakang", "lek kerl", "rebahan tekuk kaki", "tarik bantalan ke pantat"],
        "canonical": "leg_curl",
        "muscle_group": "legs",
        "weights": [20.0, 25.0, 30.0, 35.0],
        "reps_range": [8, 12]
    },
    {
        "names": ["kaki satu di kursi", "gerakan sembah kubur", "bulgar", "split skwat", "siksaan satu kaki"],
        "canonical": "bulgarian_split_squat",
        "muscle_group": "legs",
        "weights": [6.0, 8.0, 10.0, 12.0],
        "reps_range": [8, 10],
        "per_hand": True
    },
    {
        "names": ["jinjit betis", "jinjit mesin", "kalf reis", "kalf pres", "betis"],
        "canonical": "calf_raise",
        "muscle_group": "legs",
        "weights": [30.0, 40.0, 50.0, 60.0],
        "reps_range": [12, 20]
    },
    # CHEST
    {
        "names": ["rebahan dorong bar", "brench pres", "bencpres", "bens", "tiduran dorong barbel", "brench"],
        "canonical": "barbell_bench_press",
        "muscle_group": "chest",
        "weights": [30.0, 40.0, 50.0, 60.0, 70.0],
        "reps_range": [6, 10]
    },
    {
        "names": ["incline press", "rebahan dorong miring", "incline chest press", "inklin", "inclin brench"],
        "canonical": "incline_chest_press",
        "muscle_group": "chest",
        "weights": [20.0, 25.0, 30.0, 35.0, 40.0],
        "reps_range": [7, 10]
    },
    {
        "names": ["incline dumbell press", "dada atas dambel", "incline db", "bangku miring dorong dambel"],
        "canonical": "incline_dumbbell_press",
        "muscle_group": "chest",
        "weights": [10.0, 12.0, 14.0, 16.0],
        "reps_range": [8, 12],
        "per_hand": True
    },
    {
        "names": ["belah dada", "peluk mesin", "buka tutup dada", "pekdek flai", "fly machine", "dada kupu-kupu"],
        "canonical": "pec_deck",
        "muscle_group": "chest",
        "weights": [20.0, 25.0, 30.0, 35.0],
        "reps_range": [10, 15]
    },
    {
        "names": ["dorong lantai", "pus up", "pushap", "tiarap dorong tanah"],
        "canonical": "push_up",
        "muscle_group": "chest",
        "weights": [0.0],
        "reps_range": [12, 25],
        "is_bodyweight": True
    },
    {
        "names": ["celup badan", "turun naik palang dua", "dips tiang"],
        "canonical": "dips",
        "muscle_group": "chest",
        "weights": [0.0],
        "reps_range": [6, 12],
        "is_bodyweight": True
    },
    # BACK
    {
        "names": ["tarik kabel dari atas", "tarik ke dada", "letpul", "latpul", "letpuldon", "lat pull down"],
        "canonical": "lat_pulldown",
        "muscle_group": "back",
        "weights": [30.0, 35.0, 40.0, 45.0, 50.0],
        "reps_range": [8, 12]
    },
    {
        "names": ["dayung duduk", "narik kabel perut", "sited row", "seated ro", "rowing duduk", "kabel row duduk"],
        "canonical": "seated_row",
        "muscle_group": "back",
        "weights": [30.0, 35.0, 40.0, 45.0],
        "reps_range": [8, 12]
    },
    {
        "names": ["bungkuk tarik besi", "barbel ro", "bb row", "dayung bungkuk", "narik stik ke perut berdiri"],
        "canonical": "barbell_row",
        "muscle_group": "back",
        "weights": [30.0, 40.0, 50.0],
        "reps_range": [8, 10]
    },
    {
        "names": ["gelantungan tarik badan", "pul ap", "pulup", "cin ap", "angkat badan di tiang"],
        "canonical": "pull_up",
        "muscle_group": "back",
        "weights": [0.0],
        "reps_range": [5, 10],
        "is_bodyweight": True
    },
    {
        "names": ["dedlif", "detlif", "angkat beban dari lantai", "dead lif", "angkat besi dari tanah"],
        "canonical": "deadlift",
        "muscle_group": "back",
        "weights": [50.0, 60.0, 70.0, 80.0, 100.0],
        "reps_range": [5, 8]
    },
    {
        "names": ["er de el", "rdl", "romanian dedlif", "nungging tarik barbel"],
        "canonical": "romanian_deadlift",
        "muscle_group": "back",
        "weights": [35.0, 40.0, 45.0, 50.0],
        "reps_range": [8, 10]
    },
    # SHOULDERS
    {
        "names": ["buka tangan ke samping", "lateral rise", "res bahu samping", "laterel", "kepak sayap bahu"],
        "canonical": "lateral_raise",
        "muscle_group": "shoulders",
        "weights": [5.0, 6.0, 7.5, 8.0, 10.0],
        "reps_range": [8, 15],
        "per_hand": True
    },
    {
        "names": ["duduk dorong beban ke atas", "solpres", "soldel pres", "pres bahu", "incline shoulder press"],
        "canonical": "dumbbell_shoulder_press",
        "muscle_group": "shoulders",
        "weights": [7.5, 10.0, 12.0, 14.0],
        "reps_range": [8, 12],
        "per_hand": True
    },
    {
        "names": ["peluk mesin kebalik", "bahu belakang mesin", "pec deck back shoulder", "rir delt", "bahu blkg"],
        "canonical": "reverse_fly",
        "muscle_group": "shoulders",
        "weights": [12.0, 16.0, 20.0],
        "reps_range": [8, 12]
    },
    {
        "names": ["tarik tali ke muka", "tarik tali ke jidat", "feis pul", "feispul", "tarik tali ke hidung"],
        "canonical": "face_pull",
        "muscle_group": "shoulders",
        "weights": [15.0, 20.0, 25.0],
        "reps_range": [12, 15]
    },
    {
        "names": ["gedik bahu", "angkat pundak", "gaya ga tau", "srag", "db shrug"],
        "canonical": "dumbbell_shrug",
        "muscle_group": "shoulders",
        "weights": [16.0, 20.0, 24.0],
        "reps_range": [12, 15],
        "per_hand": True
    },
    # ARMS
    {
        "names": ["tekuk lengan", "bisep krol", "baisep kerl", "pompa bisep", "bicep curl"],
        "canonical": "bicep_curl",
        "muscle_group": "arms",
        "weights": [7.5, 10.0, 12.0],
        "reps_range": [8, 12],
        "per_hand": True
    },
    {
        "names": ["palu dambel", "hemer krol", "posisi martil", "hammer curl"],
        "canonical": "hammer_curl",
        "muscle_group": "arms",
        "weights": [8.0, 10.0, 12.0],
        "reps_range": [8, 12],
        "per_hand": True
    },
    {
        "names": ["taruh lengan di bantalan miring", "preachears curl", "pricer curl", "ketiak nempel bantalan"],
        "canonical": "preacher_curl",
        "muscle_group": "arms",
        "weights": [10.0, 15.0, 20.0],
        "reps_range": [8, 10]
    },
    {
        "names": ["dorong tali ke bawah", "trisep pusdon", "pusdon", "tekan kabel ke bawah", "tali trisep"],
        "canonical": "tricep_pushdown",
        "muscle_group": "arms",
        "weights": [15.0, 20.0, 25.0],
        "reps_range": [10, 12]
    },
    {
        "names": ["dorong tali dari belakang kepala", "operhed trisep", "overhead extension"],
        "canonical": "overhead_tricep_extension",
        "muscle_group": "arms",
        "weights": [12.0, 15.0, 20.0],
        "reps_range": [10, 12]
    },
    {
        "names": ["hancur jidat", "skal kraser", "tekuk barbel ke dahi", "patah leher"],
        "canonical": "skullcrusher",
        "muscle_group": "arms",
        "weights": [10.0, 15.0, 20.0],
        "reps_range": [8, 12]
    },
    {
        "names": ["jm press", "jem pres", "jm pres"],
        "canonical": "jm_press",
        "muscle_group": "arms",
        "weights": [10.0, 15.0, 20.0],
        "reps_range": [8, 10]
    },
    {
        "names": ["tekuk pergelangan tangan", "forearm curl", "rist kerl", "foream"],
        "canonical": "wrist_curl",
        "muscle_group": "arms",
        "weights": [5.0, 7.5, 10.0],
        "reps_range": [15, 25],
        "per_hand": True
    }
]

SESSION_NOTES = [
    "capek banget hari ini",
    "mantap pump keras",
    "kekenyangan lemes",
    "sampe tremor kakinya",
    "latihan bareng temen gym",
    "terburu buru waktu mepet",
    "fokus teknik tempo lambat",
    "sampe mampus set terakhir",
    "otot kebakar puas",
    "ngantuk tapi tetep konsisten",
    "gerimis tapi gas gym",
    "under perform kurang tidur"
]

FAILURE_SLANGS = [
    ("gagal di rep akhir", 10),
    ("sampe mampus", 10),
    ("sampe tremor", 10),
    ("sampe jebol", 10),
    ("fail", 10)
]

def generate_slang_sessions(count=30):
    random.seed(42)
    os.makedirs(GOLD_DIR, exist_ok=True)
    
    # Kelompokkan latihan per muscle group
    groups = {}
    for ex in EXERCISE_SLANGS:
        mg = ex["muscle_group"]
        groups.setdefault(mg, []).append(ex)

    # Preset split latihan umum
    splits = [
        ("chest", "triceps", "shoulders"),
        ("back", "arms", "core"),
        ("legs", "core"),
        ("chest", "shoulders"),
        ("back", "core"),
        ("arms", "shoulders")
    ]

    generated_files = []
    start_day = 1

    for i in range(count):
        chosen_split = splits[i % len(splits)]
        date_str = f"2026-11-{start_day:02d}"
        start_day += 1

        input_lines = []
        output_sessions = []
        
        session_note = random.choice(SESSION_NOTES)
        # 50% probabilitas session note ditaruh di teks
        has_note_in_text = random.random() > 0.3

        for mg in chosen_split:
            available_ex = groups.get(mg, [])
            if not available_ex:
                continue
            
            # Pilih 1 - 2 latihan per grup otot
            num_ex = random.randint(1, min(2, len(available_ex)))
            selected_ex = random.sample(available_ex, num_ex)
            
            ex_output_list = []
            input_lines.append(f"\n{mg}")

            for ex in selected_ex:
                name_variant = random.choice(ex["names"])
                weight = random.choice(ex["weights"])
                reps = random.randint(ex["reps_range"][0], ex["reps_range"][1])
                sets_count = random.choice([3, 4])
                is_per_hand = ex.get("per_hand", False)
                is_bw = ex.get("is_bodyweight", False)
                
                # Format penulisan teks
                style = random.choice(["multiplier", "commas", "spaces"])
                
                # Check apakah ada fail/note di set terakhir
                has_fail = random.random() < 0.25
                fail_text, rpe = random.choice(FAILURE_SLANGS) if has_fail else (None, None)

                # Format bobot string
                if is_bw:
                    w_str = ""
                else:
                    if random.random() > 0.5:
                        w_str = f"{int(weight) if weight.is_integer() else weight}kg"
                    else:
                        w_str = f"{int(weight) if weight.is_integer() else weight}k"

                hand_str = " each" if is_per_hand and random.random() > 0.4 else ""

                if style == "multiplier":
                    line_text = f"{name_variant} {w_str}{hand_str} {reps}x{sets_count}".strip()
                    if has_fail:
                        line_text += f" ({fail_text})"
                elif style == "commas":
                    reps_list = [str(max(4, reps - j)) for j in range(sets_count)]
                    line_text = f"{name_variant} {w_str}{hand_str} {','.join(reps_list)}".strip()
                    if has_fail:
                        line_text += f" {fail_text}"
                else:
                    reps_list = [str(max(4, reps - j)) for j in range(sets_count)]
                    line_text = f"{name_variant} {w_str}{hand_str} {' '.join(reps_list)}".strip()
                    if has_fail:
                        line_text += f" {fail_text}"

                input_lines.append(line_text)

                # Output sets structure
                sets_data = []
                for s_idx in range(sets_count):
                    r_val = max(4, reps - (s_idx if style != "multiplier" else 0))
                    s_obj = {
                        "weight_kg": float(weight),
                        "reps": r_val
                    }
                    if is_per_hand:
                        s_obj["per_hand"] = True
                    if has_fail and s_idx == sets_count - 1:
                        s_obj["note"] = fail_text
                        s_obj["rpe"] = rpe
                    sets_data.append(s_obj)

                ex_output_list.append({
                    "name": name_variant,
                    "canonical": ex["canonical"],
                    "sets": sets_data
                })

            output_sessions.append({
                "muscle_group": mg,
                "exercises": ex_output_list
            })

        if has_note_in_text:
            input_lines.append(f"\n{session_note}")

        full_input = "\n".join(input_lines).strip()
        full_output = {
            "date": date_str,
            "sessions": output_sessions,
            "session_note": session_note if has_note_in_text else None
        }

        # Simpan file gold
        filename = f"slang_sample_{i+1:02d}.json"
        filepath = os.path.join(GOLD_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"input": full_input, "output": full_output}, f, indent=2, ensure_ascii=False)
        generated_files.append(filename)

    print(f"[+] Berhasil membuat {len(generated_files)} sampel gold berbasis slang gym Indonesia!")
    return len(generated_files)

if __name__ == "__main__":
    generate_slang_sessions(30)
