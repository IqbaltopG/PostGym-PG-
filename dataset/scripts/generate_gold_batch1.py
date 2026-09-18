import json
import os

gold_dir = "../gold/"
os.makedirs(gold_dir, exist_ok=True)

remaining_data = {
    "2026-09-07": {
        "date": "2026-09-07",
        "sessions": [
            {"muscle_group": "chest", "exercises": [
                {"name": "incline press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 15, "reps": 9}, {"weight_kg": 15, "reps": 9}, {"weight_kg": 15, "reps": 10}]},
                {"name": "pec deck fly", "canonical": "pec_deck", "sets": [{"weight_kg": 16, "reps": 10}, {"weight_kg": 16, "reps": 10}, {"weight_kg": 16, "reps": 10}]}
            ]},
            {"muscle_group": "back", "exercises": [
                {"name": "lat pull down -", "canonical": "lat_pulldown", "sets": [{"weight_kg": 30, "reps": 8}, {"weight_kg": 30, "reps": 8}, {"weight_kg": 30, "reps": 8}]},
                {"name": "seated row -", "canonical": "seated_row", "sets": [{"weight_kg": 35, "reps": 8}, {"weight_kg": 35, "reps": 6}, {"weight_kg": 35, "reps": 6}]}
            ]},
            {"muscle_group": "arms", "exercises": [
                {"name": "preacher curl", "canonical": "preacher_curl", "sets": [{"weight_kg": 7.5, "reps": 5, "per_hand": True, "note": "trial and fail"}, {"weight_kg": 5, "reps": 10, "per_hand": True}, {"weight_kg": 5, "reps": 10, "per_hand": True}]},
                {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 5, "reps": 10, "per_hand": True}, {"weight_kg": 5, "reps": 10, "per_hand": True}, {"weight_kg": 5, "reps": 10, "per_hand": True}]}
            ]},
            {"muscle_group": "arms", "exercises": [
                {"name": "curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 7.5, "reps": 15, "per_hand": True}, {"weight_kg": 7.5, "reps": 15, "per_hand": True}, {"weight_kg": 7.5, "reps": 15, "per_hand": True}]}
            ]}
        ],
        "session_note": None
    },
    "2026-09-05": {
        "date": "2026-09-05",
        "sessions": [
            {"muscle_group": "back", "exercises": [
                {"name": "lat pull down -", "canonical": "lat_pulldown", "sets": [{"weight_kg": 30, "reps": 9}, {"weight_kg": 30, "reps": 9}, {"weight_kg": 30, "reps": 9}]},
                {"name": "seated row -", "canonical": "seated_row", "sets": [{"weight_kg": 35, "reps": 9}, {"weight_kg": 35, "reps": 9}, {"weight_kg": 35, "reps": 6}]}
            ]},
            {"muscle_group": "arms", "exercises": [
                {"name": "tricep push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 15, "reps": 10}, {"weight_kg": 15, "reps": 10}, {"weight_kg": 15, "reps": 9}]},
                {"name": "jm press", "canonical": "jm_press", "sets": [{"weight_kg": 10, "reps": 10}, {"weight_kg": 10, "reps": 10}, {"weight_kg": 10, "reps": 12}]}
            ]},
            {"muscle_group": "shoulders", "exercises": [
                {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 5, "reps": 9, "per_hand": True}, {"weight_kg": 5, "reps": 9, "per_hand": True}, {"weight_kg": 5, "reps": 9, "per_hand": True}]},
                {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 10, "reps": 12}, {"weight_kg": 15, "reps": 8}, {"weight_kg": 15, "reps": 8}]},
                {"name": "pec deck back shoulder", "canonical": "reverse_fly", "sets": [{"weight_kg": 12, "reps": 9}, {"weight_kg": 12, "reps": 8}]}
            ]},
            {"muscle_group": "arms", "exercises": [
                {"name": "forearm curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 15, "per_hand": True}, {"weight_kg": 7.5, "reps": 15, "per_hand": True}]}
            ]},
            {"muscle_group": "core", "exercises": [
                {"name": "abilow core", "canonical": "ab_wheel", "sets": [{"weight_kg": 25, "reps": 8}, {"weight_kg": 25, "reps": 8}, {"weight_kg": 25, "reps": 8}]},
                {"name": "leg up", "canonical": "hanging_leg_raise", "sets": [{"weight_kg": 0, "reps": 8, "note": "bodyweight"}, {"weight_kg": 0, "reps": 8, "note": "bodyweight"}, {"weight_kg": 0, "reps": 8, "note": "bodyweight"}]}
            ]}
        ],
        "session_note": None
    },
    "2026-09-04": {
        "date": "2026-09-04",
        "sessions": [
            {"muscle_group": "legs", "exercises": [
                {"name": "squad", "canonical": "barbell_squat", "sets": [{"weight_kg": 20, "reps": 10, "note": "bar only"}, {"weight_kg": 20, "reps": 10, "note": "bar only"}, {"weight_kg": 20, "reps": 11, "note": "bar only"}]},
                {"name": "leg curl", "canonical": "leg_curl", "sets": [{"weight_kg": 30, "reps": 10}, {"weight_kg": 30, "reps": 10}, {"weight_kg": 30, "reps": 10}]},
                {"name": "adducter ke dalam", "canonical": "hip_adduction", "sets": [{"weight_kg": 20, "reps": 8}, {"weight_kg": 20, "reps": 9}, {"weight_kg": 20, "reps": 12}]},
                {"name": "leg extensions", "canonical": "leg_extension", "sets": [{"weight_kg": 30, "reps": 8}, {"weight_kg": 30, "reps": 10}, {"weight_kg": 30, "reps": 10}]},
                {"name": "calf press", "canonical": "calf_raise", "sets": [{"weight_kg": 59, "reps": 10}, {"weight_kg": 59, "reps": 10}, {"weight_kg": 59, "reps": 11}]}
            ]},
            {"muscle_group": "core", "exercises": [
                {"name": "abilow core", "canonical": "ab_wheel", "sets": [{"weight_kg": 25, "reps": 8}, {"weight_kg": 25, "reps": 8}, {"weight_kg": 25, "reps": 8}]},
                {"name": "core training leg up in bar", "canonical": "hanging_leg_raise", "sets": [{"weight_kg": 0, "reps": 8, "note": "bodyweight"}, {"weight_kg": 0, "reps": 8, "note": "bodyweight"}, {"weight_kg": 0, "reps": 8, "note": "bodyweight"}]}
            ]}
        ],
        "session_note": None
    },
    "2026-09-02": {
        "date": "2026-09-02",
        "sessions": [
            {"muscle_group": "chest", "exercises": [
                {"name": "pec deck fly", "canonical": "pec_deck", "sets": [{"weight_kg": 16, "reps": 10}, {"weight_kg": 16, "reps": 10}, {"weight_kg": 16, "reps": 10}]},
                {"name": "incline press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 0, "reps": 8, "note": "weight missing"}, {"weight_kg": 0, "reps": 8, "note": "weight missing"}, {"weight_kg": 0, "reps": 10, "note": "weight missing"}]}
            ]},
            {"muscle_group": "shoulders", "exercises": [
                {"name": "back shoulder fly", "canonical": "reverse_fly", "sets": [{"weight_kg": 12, "reps": 8}, {"weight_kg": 12, "reps": 8}, {"weight_kg": 12, "reps": 8}]},
                {"name": "lateral raise", "canonical": "lateral_raise", "sets": [{"weight_kg": 5, "reps": 8, "per_hand": True}, {"weight_kg": 5, "reps": 10, "per_hand": True}, {"weight_kg": 5, "reps": 10, "per_hand": True}]},
                {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 5, "reps": 12, "per_hand": True}, {"weight_kg": 5, "reps": 12, "per_hand": True}, {"weight_kg": 5, "reps": 12, "per_hand": True}]}
            ]},
            {"muscle_group": "arms", "exercises": [
                {"name": "tricep push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 0, "reps": 10}, {"weight_kg": 0, "reps": 10}, {"weight_kg": 0, "reps": 7}]},
                {"name": "jm press", "canonical": "jm_press", "sets": [{"weight_kg": 10, "reps": 0, "note": "missing reps"}]}
            ]},
            {"muscle_group": "arms", "exercises": [
                {"name": "preacher curl", "canonical": "preacher_curl", "sets": [{"weight_kg": 5, "reps": 10, "per_hand": True}, {"weight_kg": 5, "reps": 10, "per_hand": True}, {"weight_kg": 5, "reps": 10, "per_hand": True}]}
            ]}
        ],
        "session_note": None
    },
    "2026-08-31": {
        "date": "2026-08-31",
        "sessions": [
            {"muscle_group": "chest", "exercises": [
                {"name": "incline press", "canonical": "incline_dumbbell_press", "sets": []},
                {"name": "pec deck fly", "canonical": "pec_deck", "sets": [{"weight_kg": 16, "reps": 10}, {"weight_kg": 16, "reps": 10}, {"weight_kg": 16, "reps": 7}]}
            ]},
            {"muscle_group": "back", "exercises": [
                {"name": "lat pull down -", "canonical": "lat_pulldown", "sets": [{"weight_kg": 30, "reps": 8}, {"weight_kg": 30, "reps": 8}, {"weight_kg": 30, "reps": 7}]},
                {"name": "seated row -", "canonical": "seated_row", "sets": [{"weight_kg": 35, "reps": 8}, {"weight_kg": 35, "reps": 8}, {"weight_kg": 35, "reps": 6}]}
            ]},
            {"muscle_group": "arms", "exercises": [
                {"name": "preacher curl", "canonical": "preacher_curl", "sets": [{"weight_kg": 5, "reps": 10, "per_hand": True}, {"weight_kg": 5, "reps": 10, "per_hand": True}, {"weight_kg": 5, "reps": 10, "per_hand": True}]},
                {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 5, "reps": 10, "per_hand": True}, {"weight_kg": 5, "reps": 10, "per_hand": True}, {"weight_kg": 5, "reps": 10, "per_hand": True}]}
            ]},
            {"muscle_group": "arms", "exercises": [
                {"name": "curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 5, "reps": 20, "per_hand": True}, {"weight_kg": 5, "reps": 20, "per_hand": True}, {"weight_kg": 5, "reps": 20, "per_hand": True}]}
            ]}
        ],
        "session_note": "under performed a bit form. perfection"
    },
    "2026-08-29": {
        "date": "2026-08-29",
        "sessions": [
            {"muscle_group": "back", "exercises": [
                {"name": "lat pull down -", "canonical": "lat_pulldown", "sets": [{"weight_kg": 30, "reps": 8}, {"weight_kg": 30, "reps": 8}, {"weight_kg": 30, "reps": 11}]},
                {"name": "seated row -", "canonical": "seated_row", "sets": [{"weight_kg": 35, "reps": 8}, {"weight_kg": 35, "reps": 8}, {"weight_kg": 35, "reps": 8}]}
            ]},
            {"muscle_group": "arms", "exercises": [
                {"name": "tricep push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 15, "reps": 8}, {"weight_kg": 15, "reps": 8}, {"weight_kg": 15, "reps": 8}]},
                {"name": "jm press", "canonical": "jm_press", "sets": [{"weight_kg": 10, "reps": 8}, {"weight_kg": 10, "reps": 10}, {"weight_kg": 10, "reps": 10}]}
            ]},
            {"muscle_group": "shoulders", "exercises": [
                {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 5, "reps": 8, "per_hand": True}, {"weight_kg": 5, "reps": 8, "per_hand": True}, {"weight_kg": 5, "reps": 8, "per_hand": True}]},
                {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 10, "reps": 11}, {"weight_kg": 10, "reps": 11}, {"weight_kg": 10, "reps": 12}]},
                {"name": "pec deck back shoulder", "canonical": "reverse_fly", "sets": [{"weight_kg": 12, "reps": 8}, {"weight_kg": 12, "reps": 8}, {"weight_kg": 12, "reps": 10}]}
            ]},
            {"muscle_group": "arms", "exercises": [
                {"name": "forearm curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 5, "reps": 15, "per_hand": True}, {"weight_kg": 5, "reps": 15, "per_hand": True}, {"weight_kg": 5, "reps": 15, "per_hand": True}]}
            ]},
            {"muscle_group": "core", "exercises": [
                {"name": "abilow core", "canonical": "ab_wheel", "sets": [{"weight_kg": 25, "reps": 8}, {"weight_kg": 25, "reps": 8}, {"weight_kg": 25, "reps": 8}]},
                {"name": "leg up", "canonical": "hanging_leg_raise", "sets": [{"weight_kg": 0, "reps": 10, "note": "bodyweight"}, {"weight_kg": 0, "reps": 10, "note": "bodyweight"}, {"weight_kg": 0, "reps": 10, "note": "bodyweight"}]}
            ]}
        ],
        "session_note": None
    }
}

for date, data in remaining_data.items():
    wrapper = {
        "id": f"ambatron_{date}",
        "input": open(f"../raw/user_ambatron/sessions/{date}.txt").read(),
        "output": data,
        "metadata": {"annotator": "ambatron", "difficulty": "medium", "tags": []}
    }
    with open(os.path.join(gold_dir, f"{date}.json"), "w") as f:
        json.dump(wrapper, f, indent=2)

print("Batch 1 selesai!")
