import os
import json

FUTURE_DATA = {
    "2026-10-01": {
        "date": "2026-10-01",
        "sessions": [
            {"muscle_group": "chest", "exercises": [
                {"name": "barbell bench press", "canonical": "barbell_bench_press", "sets": [{"weight_kg": 60.0, "reps": 8}, {"weight_kg": 60.0, "reps": 8}, {"weight_kg": 60.0, "reps": 6, "note": "failure", "rpe": 10}]},
                {"name": "cgbp", "canonical": "close_grip_bench_press", "sets": [{"weight_kg": 40.0, "reps": 10}, {"weight_kg": 40.0, "reps": 10}, {"weight_kg": 40.0, "reps": 10}]},
                {"name": "cable crossover", "canonical": "cable_crossover", "sets": [{"weight_kg": 15.0, "reps": 12, "per_hand": True}, {"weight_kg": 15.0, "reps": 12, "per_hand": True}, {"weight_kg": 15.0, "reps": 12, "per_hand": True}]}
            ]},
            {"muscle_group": "shoulder", "exercises": [
                {"name": "ohp", "canonical": "overhead_press", "sets": [{"weight_kg": 30.0, "reps": 8}, {"weight_kg": 30.0, "reps": 8}, {"weight_kg": 30.0, "reps": 7}]},
                {"name": "cable lateral raise", "canonical": "cable_lateral_raise", "sets": [{"weight_kg": 5.0, "reps": 15, "per_hand": True}, {"weight_kg": 5.0, "reps": 15, "per_hand": True}]}
            ]},
            {"muscle_group": "tricep", "exercises": [
                {"name": "skullcrusher", "canonical": "skullcrusher", "sets": [{"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 10}]}
            ]}
        ],
        "session_note": ""
    },
    "2026-10-02": {
        "date": "2026-10-02",
        "sessions": [
            {"muscle_group": "back", "exercises": [
                {"name": "barbell row", "canonical": "barbell_row", "sets": [{"weight_kg": 50.0, "reps": 10}, {"weight_kg": 50.0, "reps": 10}, {"weight_kg": 50.0, "reps": 10}]},
                {"name": "tbar row", "canonical": "t_bar_row", "sets": [{"weight_kg": 40.0, "reps": 8}, {"weight_kg": 40.0, "reps": 8}, {"weight_kg": 40.0, "reps": 8}]},
                {"name": "pull up bodyweight", "canonical": "pull_up", "sets": [{"weight_kg": 0.0, "reps": 10}, {"weight_kg": 0.0, "reps": 8}, {"weight_kg": 0.0, "reps": 6, "note": "fail", "rpe": 10}]}
            ]},
            {"muscle_group": "shoulder", "exercises": [
                {"name": "face pull", "canonical": "face_pull", "sets": [{"weight_kg": 15.0, "reps": 15}, {"weight_kg": 15.0, "reps": 15}, {"weight_kg": 15.0, "reps": 15}]},
                {"name": "shrugs", "canonical": "dumbbell_shrug", "sets": [{"weight_kg": 20.0, "reps": 12, "per_hand": True}, {"weight_kg": 20.0, "reps": 12, "per_hand": True}]}
            ]},
            {"muscle_group": "bicep", "exercises": [
                {"name": "incline dumbbell curl", "canonical": "incline_dumbbell_curl", "sets": [{"weight_kg": 10.0, "reps": 10, "per_hand": True}, {"weight_kg": 10.0, "reps": 10, "per_hand": True}]}
            ]}
        ],
        "session_note": ""
    },
    "2026-10-03": {
        "date": "2026-10-03",
        "sessions": [
            {"muscle_group": "leg", "exercises": [
                {"name": "rdl", "canonical": "romanian_deadlift", "sets": [{"weight_kg": 60.0, "reps": 10}, {"weight_kg": 60.0, "reps": 10}, {"weight_kg": 60.0, "reps": 10}]},
                {"name": "bss", "canonical": "bulgarian_split_squat", "sets": [{"weight_kg": 10.0, "reps": 10, "per_hand": True}, {"weight_kg": 10.0, "reps": 10, "per_hand": True}, {"weight_kg": 10.0, "reps": 10, "per_hand": True}]},
                {"name": "leg press", "canonical": "leg_press", "sets": [{"weight_kg": 100.0, "reps": 12}, {"weight_kg": 120.0, "reps": 10}, {"weight_kg": 140.0, "reps": 8}]},
                {"name": "standing calf raise", "canonical": "standing_calf_raise", "sets": [{"weight_kg": 40.0, "reps": 15}, {"weight_kg": 40.0, "reps": 15}, {"weight_kg": 40.0, "reps": 15}]}
            ]}
        ],
        "session_note": ""
    },
    "2026-10-04": {
        "date": "2026-10-04",
        "sessions": [
            {"muscle_group": "chest", "exercises": [
                {"name": "machine chest press", "canonical": "machine_chest_press", "sets": [{"weight_kg": 50.0, "reps": 10}, {"weight_kg": 50.0, "reps": 10}, {"weight_kg": 50.0, "reps": 10}]},
                {"name": "dip assisted", "canonical": "assisted_dip", "sets": [{"weight_kg": -20.0, "reps": 10}, {"weight_kg": -20.0, "reps": 10}, {"weight_kg": -20.0, "reps": 8}]}
            ]},
            {"muscle_group": "back", "exercises": [
                {"name": "cable pullover", "canonical": "cable_pullover", "sets": [{"weight_kg": 25.0, "reps": 12}, {"weight_kg": 25.0, "reps": 12}, {"weight_kg": 25.0, "reps": 12}]}
            ]},
            {"muscle_group": "bicep", "exercises": [
                {"name": "spider curl", "canonical": "spider_curl", "sets": [{"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}]}
            ]}
        ],
        "session_note": ""
    }
}

FUTURE_INPUTS = {
    "2026-10-01": "chest\nbarbell bench press 60k 8 8 6 fail\ncgbp 40kg 10x3\ncable crossover 15kg each 12x3\n\nshoulder\nohp 30kg 8 8 7\ncable lateral raise 5kg each 15x2\n\ntricep\nskullcrusher 20kg 10x3",
    "2026-10-02": "back\nbarbell row 50kg 10x3\ntbar row 40kg 8x3\npull up bodyweight 10 8 6 fail\n\nshoulder\nface pull 15kg 15x3\nshrugs 20kg each 12x2\n\nbicep\nincline dumbbell curl 10kg each 10x2",
    "2026-10-03": "leg\nrdl 60k 10x3\nbss 10kg each 10x3\nleg press 100k 12x1, 120kg 10x1, 140kg 8x1\nstanding calf raise 40kg 15x3",
    "2026-10-04": "chest\nmachine chest press 50kg 10x3\ndip assisted -20kg 10 10 8\n\nback\ncable pullover 25kg 12x3\n\nbicep\nspider curl 15kg 10x3"
}

def write_future_gold():
    out_dir = "dataset/gold"
    os.makedirs(out_dir, exist_ok=True)
    
    for date, json_data in FUTURE_DATA.items():
        final_json = {
            "input": FUTURE_INPUTS[date],
            "output": json_data
        }
        
        out_path = os.path.join(out_dir, f"{date}_future.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, indent=4)
        print(f"Created {out_path}")

if __name__ == "__main__":
    write_future_gold()
