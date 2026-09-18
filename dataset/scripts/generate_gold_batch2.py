import os
import json

DATA = {
    "2026-07-24": {
        "date": "2026-07-24",
        "sessions": [
            {"muscle_group": "back", "exercises": [
                {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}]},
                {"name": "seated row", "canonical": "seated_row", "sets": [{"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 8}]}
            ]},
            {"muscle_group": "shoulder", "exercises": [
                {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 5.0, "reps": 12}, {"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 8}]},
                {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 10}, {"weight_kg": 10.0, "reps": 12}]},
                {"name": "rear delt pec fly", "canonical": "reverse_fly", "sets": [{"weight_kg": 12.0, "reps": 8}, {"weight_kg": 12.0, "reps": 8}, {"weight_kg": 12.0, "reps": 8}]}
            ]},
            {"muscle_group": "tricep", "exercises": [
                {"name": "tricep push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 8}]},
                {"name": "overhead tricep extension", "canonical": "overhead_tricep_extension", "sets": [{"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 8}]}
            ]},
            {"muscle_group": "forearm", "exercises": [
                {"name": "forearm train", "canonical": "wrist_curl", "sets": [{"weight_kg": 5.0, "reps": 15, "per_hand": True}, {"weight_kg": 5.0, "reps": 15, "per_hand": True}, {"weight_kg": 5.0, "reps": 15, "per_hand": True}]},
                {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 5.0, "reps": 8, "per_hand": True}, {"weight_kg": 5.0, "reps": 8, "per_hand": True}, {"weight_kg": 5.0, "reps": 8, "per_hand": True}]}
            ]},
            {"muscle_group": "core", "exercises": [
                {"name": "abilow", "canonical": "ab_wheel", "sets": [{"weight_kg": 12.0, "reps": 12}, {"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 12}]},
                {"name": "kaya pull up tapi kaki naik naik", "canonical": "hanging_leg_raise", "sets": [{"weight_kg": 0.0, "reps": 8}, {"weight_kg": 0.0, "reps": 8}, {"weight_kg": 0.0, "reps": 8}]}
            ]}
        ],
        "session_note": ""
    },
    "2026-07-27": {
        "date": "2026-07-27",
        "sessions": [
            {"muscle_group": "back", "exercises": [
                {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 12}]},
                {"name": "seated row", "canonical": "seated_row", "sets": [{"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 10}]}
            ]},
            {"muscle_group": "chest", "exercises": [
                {"name": "pec deck fly upper front chest", "canonical": "pec_deck", "sets": [{"weight_kg": 12.0, "reps": 10}, {"weight_kg": 12.0, "reps": 10}, {"weight_kg": 12.0, "reps": 10}]},
                {"name": "incline press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 5.0, "reps": 6}, {"weight_kg": 5.0, "reps": 6}, {"weight_kg": 5.0, "reps": 6}]}
            ]}
        ],
        "session_note": ""
    },
    "2026-07-29": {
        "date": "2026-07-29",
        "sessions": [
            {"muscle_group": "chest", "exercises": [
                {"name": "incline press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 5.0, "reps": 6}, {"weight_kg": 5.0, "reps": 6}, {"weight_kg": 5.0, "reps": 6}]},
                {"name": "pecdeck fly", "canonical": "pec_deck", "sets": [{"weight_kg": 12.0, "reps": 10, "note": "failure", "rpe": 10}, {"weight_kg": 4.0, "reps": 8}, {"weight_kg": 4.0, "reps": 8}]}
            ]},
            {"muscle_group": "tricep", "exercises": [
                {"name": "tricep push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 8}]},
                {"name": "jm press", "canonical": "jm_press", "sets": [{"weight_kg": 5.0, "reps": 6}, {"weight_kg": 5.0, "reps": 6}, {"weight_kg": 5.0, "reps": 6}]}
            ]},
            {"muscle_group": "shoulder", "exercises": [
                {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 5.0, "reps": 12}, {"weight_kg": 5.0, "reps": 12}, {"weight_kg": 5.0, "reps": 12}]},
                {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 10.0, "reps": 8, "note": "failure", "rpe": 10}]},
                {"name": "rear delt pec fly", "canonical": "reverse_fly", "sets": [{"weight_kg": 8.0, "reps": 8}, {"weight_kg": 8.0, "reps": 8}, {"weight_kg": 8.0, "reps": 8}]}
            ]},
            {"muscle_group": "bicep", "exercises": [
                {"name": "bicep curl", "canonical": "bicep_curl", "sets": [{"weight_kg": 2.5, "reps": 10}, {"weight_kg": 2.5, "reps": 10}, {"weight_kg": 2.5, "reps": 10}]},
                {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 2.5, "reps": 12}, {"weight_kg": 5.0, "reps": 8}, {"weight_kg": 5.0, "reps": 8}]}
            ]}
        ],
        "session_note": ""
    },
    "2026-08-01": {
        "date": "2026-08-01",
        "sessions": [
            {"muscle_group": "back", "exercises": [
                {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}]},
                {"name": "seated row", "canonical": "seated_row", "sets": [{"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 8}]}
            ]},
            {"muscle_group": "core", "exercises": [
                {"name": "abilow", "canonical": "ab_wheel", "sets": [{"weight_kg": 12.0, "reps": 12}, {"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 12}]},
                {"name": "kaya pull up tapi kaki naik naik", "canonical": "hanging_leg_raise", "sets": [{"weight_kg": 0.0, "reps": 8}, {"weight_kg": 0.0, "reps": 8}, {"weight_kg": 0.0, "reps": 8}]}
            ]},
            {"muscle_group": "triceps", "exercises": [
                {"name": "tricep push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 8}]},
                {"name": "overhead tricep extension", "canonical": "overhead_tricep_extension", "sets": [{"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 8}]}
            ]},
            {"muscle_group": "shoulder", "exercises": [
                {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 5.0, "reps": 12}, {"weight_kg": 5.0, "reps": 12}, {"weight_kg": 5.0, "reps": 12}]},
                {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 8}]},
                {"name": "rear delt pec fly", "canonical": "reverse_fly", "sets": [{"weight_kg": 12.0, "reps": 8}, {"weight_kg": 12.0, "reps": 8}, {"weight_kg": 6.0, "reps": 1, "note": "failure", "rpe": 10}]}
            ]},
            {"muscle_group": "forearm", "exercises": [
                {"name": "forearm train", "canonical": "wrist_curl", "sets": [{"weight_kg": 5.0, "reps": 15, "per_hand": True}, {"weight_kg": 5.0, "reps": 15, "per_hand": True}, {"weight_kg": 5.0, "reps": 15, "per_hand": True}]}
            ]}
        ],
        "session_note": ""
    },
    "2026-08-03": {
        "date": "2026-08-03",
        "sessions": [
            {"muscle_group": "chest", "exercises": [
                {"name": "pec deck fly upper front chest", "canonical": "pec_deck", "sets": [{"weight_kg": 12.0, "reps": 10}, {"weight_kg": 16.0, "reps": 8}, {"weight_kg": 16.0, "reps": 8}]},
                {"name": "incline press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 5.0, "reps": 8}, {"weight_kg": 5.0, "reps": 8}, {"weight_kg": 10.0, "reps": 8}]}
            ]},
            {"muscle_group": "back", "exercises": [
                {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}]},
                {"name": "seated row", "canonical": "seated_row", "sets": [{"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 12}]}
            ]},
            {"muscle_group": "bicep", "exercises": [
                {"name": "bicep curl", "canonical": "bicep_curl", "sets": [{"weight_kg": 0.0, "reps": 6}, {"weight_kg": 0.0, "reps": 6, "note": "failure", "rpe": 10}]},
                {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 0.0, "reps": 8}, {"weight_kg": 0.0, "reps": 8}, {"weight_kg": 0.0, "reps": 8}]}
            ]},
            {"muscle_group": "fore arm", "exercises": [
                {"name": "curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 0.0, "reps": 15, "per_hand": True}, {"weight_kg": 0.0, "reps": 15, "per_hand": True}, {"weight_kg": 0.0, "reps": 15, "per_hand": True}]}
            ]}
        ],
        "session_note": ""
    },
    "2026-08-05": {
        "date": "2026-08-05",
        "sessions": [
            {"muscle_group": "chest", "exercises": [
                {"name": "incline press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 12}]},
                {"name": "pec deck fly", "canonical": "pec_deck", "sets": [{"weight_kg": 16.0, "reps": 8}, {"weight_kg": 16.0, "reps": 8}, {"weight_kg": 16.0, "reps": 5}]}
            ]},
            {"muscle_group": "shoulder", "exercises": [
                {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 10.0, "reps": 10}, {"weight_kg": 10.0, "reps": 10}, {"weight_kg": 10.0, "reps": 10}]},
                {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 10.0, "reps": 6}, {"weight_kg": 10.0, "reps": 6}, {"weight_kg": 10.0, "reps": 6}]},
                {"name": "pec deck back shoulder", "canonical": "reverse_fly", "sets": [{"weight_kg": 8.0, "reps": 12}, {"weight_kg": 12.0, "reps": 6}, {"weight_kg": 12.0, "reps": 6}]}
            ]},
            {"muscle_group": "triceps", "exercises": [
                {"name": "tricep push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 10}]},
                {"name": "jm press", "canonical": "jm_press", "sets": [{"weight_kg": 5.0, "reps": 6}, {"weight_kg": 5.0, "reps": 6}, {"weight_kg": 5.0, "reps": 6}]}
            ]},
            {"muscle_group": "bicep", "exercises": [
                {"name": "assisted bicep curl", "canonical": "bicep_curl", "sets": [{"weight_kg": 5.0, "reps": 6, "per_hand": True}, {"weight_kg": 5.0, "reps": 6, "per_hand": True}, {"weight_kg": 5.0, "reps": 6, "per_hand": True}]},
                {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 5.0, "reps": 7, "per_hand": True}, {"weight_kg": 5.0, "reps": 7, "per_hand": True}, {"weight_kg": 5.0, "reps": 7, "per_hand": True, "note": "failure", "rpe": 10}]}
            ]}
        ],
        "session_note": ""
    },
    "2026-08-08": {
        "date": "2026-08-08",
        "sessions": [
            {"muscle_group": "leg", "exercises": [
                {"name": "wighted squad no weight only bar", "canonical": "barbell_squat", "sets": [{"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 12}]},
                {"name": "leg curl", "canonical": "leg_curl", "sets": [{"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 12}, {"weight_kg": 30.0, "reps": 10}]},
                {"name": "adducter ke dalam", "canonical": "hip_adduction", "sets": [{"weight_kg": 25.0, "reps": 8}, {"weight_kg": 20.0, "reps": 6, "note": "fail", "rpe": 10}, {"weight_kg": 16.0, "reps": 6, "note": "fail", "rpe": 10}]},
                {"name": "leg extensions", "canonical": "leg_extension", "sets": [{"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 12}]},
                {"name": "calf press", "canonical": "calf_raise", "sets": [{"weight_kg": 29.0, "reps": 12}, {"weight_kg": 39.0, "reps": 12}, {"weight_kg": 49.0, "reps": 11}]}
            ]},
            {"muscle_group": "back", "exercises": [
                {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 20.0, "reps": 12}, {"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}]},
                {"name": "seated row", "canonical": "seated_row", "sets": [{"weight_kg": 25.0, "reps": 12}, {"weight_kg": 25.0, "reps": 12}, {"weight_kg": 30.0, "reps": 8}, {"weight_kg": 30.0, "reps": 8}]}
            ]}
        ],
        "session_note": ""
    },
    "2026-08-10": {
        "date": "2026-08-10",
        "sessions": [
            {"muscle_group": "chest", "exercises": [
                {"name": "incline press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 10.0, "reps": 10}, {"weight_kg": 10.0, "reps": 10}, {"weight_kg": 10.0, "reps": 6, "note": "failure", "rpe": 10}]},
                {"name": "pec deck fly", "canonical": "pec_deck", "sets": [{"weight_kg": 16.0, "reps": 8}, {"weight_kg": 16.0, "reps": 8}, {"weight_kg": 16.0, "reps": 5, "note": "failure", "rpe": 10}]}
            ]},
            {"muscle_group": "back", "exercises": [
                {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 20.0, "reps": 12}, {"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}]},
                {"name": "seated row", "canonical": "seated_row", "sets": [{"weight_kg": 30.0, "reps": 8}, {"weight_kg": 30.0, "reps": 8}, {"weight_kg": 30.0, "reps": 10}]}
            ]},
            {"muscle_group": "bicep", "exercises": [
                {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 5.0, "reps": 8, "per_hand": True}, {"weight_kg": 5.0, "reps": 8, "per_hand": True}, {"weight_kg": 5.0, "reps": 8, "per_hand": True}]},
                {"name": "preachers curl", "canonical": "preacher_curl", "sets": [{"weight_kg": 5.0, "reps": 8, "per_hand": True}, {"weight_kg": 5.0, "reps": 8, "per_hand": True}, {"weight_kg": 5.0, "reps": 6, "per_hand": True, "note": "failure", "rpe": 10}]}
            ]},
            {"muscle_group": "forearm", "exercises": [
                {"name": "forearm curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 5.0, "reps": 15, "per_hand": True}, {"weight_kg": 5.0, "reps": 15, "per_hand": True}, {"weight_kg": 5.0, "reps": 15, "per_hand": True}]}
            ]}
        ],
        "session_note": ""
    },
    # Skip file 31-july yang cuma isi "rest" karena tidak perlu diparse AI
}

def write_gold_files():
    out_dir = "dataset/gold"
    os.makedirs(out_dir, exist_ok=True)
    
    for date, json_data in DATA.items():
        # Baca raw text-nya
        raw_path = f"dataset/raw/user_ambatron/sessions/{date}.txt"
        with open(raw_path, 'r', encoding='utf-8') as f:
            raw_text = f.read().strip()
            
        final_json = {
            "input": raw_text,
            "output": json_data
        }
        
        out_path = os.path.join(out_dir, f"{date}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, indent=4)
        print(f"Created {out_path}")

if __name__ == "__main__":
    write_gold_files()
