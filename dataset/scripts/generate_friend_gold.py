import os
import json

FRIEND_DATA = {
    "2026-10-10": {
        "input": """Chest :
fly machine
(25/30 kg ) 10/9 ( mgk 10)  x 3 set
Low cable fly
(10 x 2 kg) 9  x 3 set
Incline press 
(12, 5 kg x 2 ) 10 x 3 set

Shoulder:
Lateral raises (mid delt)
(7,5 kg) 9 - bs 10 x 3 set
Incline shoulder press (front delt)
(7,5 kg) 9 x 3 set
Rear delt pec fly (rear delt)
(16 kg - bs naik 1 plate) 10 / 8 x 3 set

Tricep:
Tricep push down
(30 kg) 8 - 9 x 3 (insight pake rope)
(20 kg) 8 - 9 x 3 (insight rope after jm press)
Overhead extension
(20 kg) 7 x 3 (insight)
JM press
(7,5 kg) 10 x 3 set""",
        "output": {
            "date": "2026-10-10",
            "sessions": [
                {"muscle_group": "chest", "exercises": [
                    {"name": "fly machine", "canonical": "pec_deck", "sets": [
                        {"weight_kg": 25.0, "reps": 10}, 
                        {"weight_kg": 30.0, "reps": 9}, 
                        {"weight_kg": 30.0, "reps": 10, "note": "mgk 10"}
                    ]},
                    {"name": "Low cable fly", "canonical": "cable_fly", "sets": [
                        {"weight_kg": 10.0, "reps": 9, "per_hand": True}, 
                        {"weight_kg": 10.0, "reps": 9, "per_hand": True}, 
                        {"weight_kg": 10.0, "reps": 9, "per_hand": True}
                    ]},
                    {"name": "Incline press", "canonical": "incline_dumbbell_press", "sets": [
                        {"weight_kg": 12.5, "reps": 10, "per_hand": True}, 
                        {"weight_kg": 12.5, "reps": 10, "per_hand": True}, 
                        {"weight_kg": 12.5, "reps": 10, "per_hand": True}
                    ]}
                ]},
                {"muscle_group": "shoulder", "exercises": [
                    {"name": "Lateral raises (mid delt)", "canonical": "lateral_raise", "sets": [
                        {"weight_kg": 7.5, "reps": 9, "note": "bs 10", "per_hand": True}, 
                        {"weight_kg": 7.5, "reps": 9, "note": "bs 10", "per_hand": True}, 
                        {"weight_kg": 7.5, "reps": 9, "note": "bs 10", "per_hand": True}
                    ]},
                    {"name": "Incline shoulder press (front delt)", "canonical": "dumbbell_shoulder_press", "sets": [
                        {"weight_kg": 7.5, "reps": 9, "per_hand": True}, 
                        {"weight_kg": 7.5, "reps": 9, "per_hand": True}, 
                        {"weight_kg": 7.5, "reps": 9, "per_hand": True}
                    ]},
                    {"name": "Rear delt pec fly (rear delt)", "canonical": "reverse_fly", "sets": [
                        {"weight_kg": 16.0, "reps": 10, "note": "bs naik 1 plate"}, 
                        {"weight_kg": 16.0, "reps": 8, "note": "bs naik 1 plate"}, 
                        {"weight_kg": 16.0, "reps": 8, "note": "bs naik 1 plate"}
                    ]}
                ]},
                {"muscle_group": "tricep", "exercises": [
                    {"name": "Tricep push down", "canonical": "tricep_pushdown", "sets": [
                        {"weight_kg": 30.0, "reps": 8, "note": "insight pake rope"}, 
                        {"weight_kg": 30.0, "reps": 9, "note": "insight pake rope"}, 
                        {"weight_kg": 30.0, "reps": 9, "note": "insight pake rope"},
                        {"weight_kg": 20.0, "reps": 8, "note": "insight rope after jm press"}, 
                        {"weight_kg": 20.0, "reps": 9, "note": "insight rope after jm press"}, 
                        {"weight_kg": 20.0, "reps": 9, "note": "insight rope after jm press"}
                    ]},
                    {"name": "Overhead extension", "canonical": "overhead_tricep_extension", "sets": [
                        {"weight_kg": 20.0, "reps": 7, "note": "insight"}, 
                        {"weight_kg": 20.0, "reps": 7, "note": "insight"}, 
                        {"weight_kg": 20.0, "reps": 7, "note": "insight"}
                    ]},
                    {"name": "JM press", "canonical": "jm_press", "sets": [
                        {"weight_kg": 7.5, "reps": 10}, 
                        {"weight_kg": 7.5, "reps": 10}, 
                        {"weight_kg": 7.5, "reps": 10}
                    ]}
                ]}
            ],
            "session_note": ""
        }
    },
    "2026-10-11": {
        "input": """Back:
Latt pull
(40 kg) 9 - 10 x 3 set
Seated row
(35 kg) 9 x 3 set

Bicep;
Preacher curl
(7,5 kg) 9 x 3 set

Forearms
(7,5 kg) 20 x 3 set
(10 kg) 13 x 3

Core:
Abilow 
(20 kg) 10 x 3 set""",
        "output": {
            "date": "2026-10-11",
            "sessions": [
                {"muscle_group": "back", "exercises": [
                    {"name": "Latt pull", "canonical": "lat_pulldown", "sets": [
                        {"weight_kg": 40.0, "reps": 9}, 
                        {"weight_kg": 40.0, "reps": 10}, 
                        {"weight_kg": 40.0, "reps": 10}
                    ]},
                    {"name": "Seated row", "canonical": "seated_row", "sets": [
                        {"weight_kg": 35.0, "reps": 9}, 
                        {"weight_kg": 35.0, "reps": 9}, 
                        {"weight_kg": 35.0, "reps": 9}
                    ]}
                ]},
                {"muscle_group": "bicep", "exercises": [
                    {"name": "Preacher curl", "canonical": "preacher_curl", "sets": [
                        {"weight_kg": 7.5, "reps": 9, "per_hand": True}, 
                        {"weight_kg": 7.5, "reps": 9, "per_hand": True}, 
                        {"weight_kg": 7.5, "reps": 9, "per_hand": True}
                    ]}
                ]},
                {"muscle_group": "forearms", "exercises": [
                    {"name": "Forearms", "canonical": "wrist_curl", "sets": [
                        {"weight_kg": 7.5, "reps": 20}, 
                        {"weight_kg": 7.5, "reps": 20}, 
                        {"weight_kg": 7.5, "reps": 20},
                        {"weight_kg": 10.0, "reps": 13}, 
                        {"weight_kg": 10.0, "reps": 13}, 
                        {"weight_kg": 10.0, "reps": 13}
                    ]}
                ]},
                {"muscle_group": "core", "exercises": [
                    {"name": "Abilow", "canonical": "ab_wheel", "sets": [
                        {"weight_kg": 20.0, "reps": 10}, 
                        {"weight_kg": 20.0, "reps": 10}, 
                        {"weight_kg": 20.0, "reps": 10}
                    ]}
                ]}
            ],
            "session_note": ""
        }
    },
    "2026-10-12": {
        "input": """Lower
Squat
(5 x 2 kg) 10 x 3 set
Leg curl seated
(45 kg - bs naik 50) 10 / 9 x 3 set
Adductor
(20 kg - bs naik 1) 9 / 8 x 3 set
Leg exstension
(45 kg) 9 x 3 set
Calf press
(44 kg - bs naik 1) 10 x 3 set""",
        "output": {
            "date": "2026-10-12",
            "sessions": [
                {"muscle_group": "lower", "exercises": [
                    {"name": "Squat", "canonical": "dumbbell_squat", "sets": [
                        {"weight_kg": 5.0, "reps": 10, "per_hand": True}, 
                        {"weight_kg": 5.0, "reps": 10, "per_hand": True}, 
                        {"weight_kg": 5.0, "reps": 10, "per_hand": True}
                    ]},
                    {"name": "Leg curl seated", "canonical": "seated_leg_curl", "sets": [
                        {"weight_kg": 45.0, "reps": 10, "note": "bs naik 50"}, 
                        {"weight_kg": 45.0, "reps": 9, "note": "bs naik 50"}, 
                        {"weight_kg": 45.0, "reps": 9, "note": "bs naik 50"}
                    ]},
                    {"name": "Adductor", "canonical": "hip_adduction", "sets": [
                        {"weight_kg": 20.0, "reps": 9, "note": "bs naik 1"}, 
                        {"weight_kg": 20.0, "reps": 8, "note": "bs naik 1"}, 
                        {"weight_kg": 20.0, "reps": 8, "note": "bs naik 1"}
                    ]},
                    {"name": "Leg exstension", "canonical": "leg_extension", "sets": [
                        {"weight_kg": 45.0, "reps": 9}, 
                        {"weight_kg": 45.0, "reps": 9}, 
                        {"weight_kg": 45.0, "reps": 9}
                    ]},
                    {"name": "Calf press", "canonical": "calf_raise", "sets": [
                        {"weight_kg": 44.0, "reps": 10, "note": "bs naik 1"}, 
                        {"weight_kg": 44.0, "reps": 10, "note": "bs naik 1"}, 
                        {"weight_kg": 44.0, "reps": 10, "note": "bs naik 1"}
                    ]}
                ]}
            ],
            "session_note": ""
        }
    }
}

def write_friend_gold():
    out_dir = "dataset/gold"
    os.makedirs(out_dir, exist_ok=True)
    
    for date, data in FRIEND_DATA.items():
        out_path = os.path.join(out_dir, f"{date}_friend.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Created {out_path}")

if __name__ == "__main__":
    write_friend_gold()
