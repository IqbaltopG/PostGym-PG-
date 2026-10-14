import os
import json

NEW_GOLD_SESSIONS = {
    "2026-07-31": {
        "input": "leg\nweighted squad 7kg 8x3\nleg curl 20kg 12x1 , 25kg 8x2\nadducter ke dalam 25kg 8x1, 6x1 fail, 16kg 8x1\nleg extensions 20 12x1, 25kg 8x2",
        "output": {
            "date": "2026-07-31",
            "sessions": [
                {
                    "muscle_group": "legs",
                    "exercises": [
                        {"name": "weighted squad", "canonical": "barbell_squat", "sets": [{"weight_kg": 7.0, "reps": 8}, {"weight_kg": 7.0, "reps": 8}, {"weight_kg": 7.0, "reps": 8}]},
                        {"name": "leg curl", "canonical": "leg_curl", "sets": [{"weight_kg": 20.0, "reps": 12}, {"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 8}]},
                        {"name": "adducter ke dalam", "canonical": "hip_adduction", "sets": [{"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 6, "note": "fail", "rpe": 10}, {"weight_kg": 16.0, "reps": 8}]},
                        {"name": "leg extensions", "canonical": "leg_extension", "sets": [{"weight_kg": 20.0, "reps": 12}, {"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 8}]}
                    ]
                }
            ],
            "session_note": ""
        }
    },
    "2026-09-19": {
        "input": "back\nlat pull down 30kg 9x2, 10x1\nseated narrow grip row - 35kg 8x3\n\ntriceps\njm press 15kg 10x3\ntriceps push down 20kg 8x2, 6x1\n\nshoulder\nlateral rise 5kg each 10x3\nincline shoulder press 15kg 8x2, 10x1\npec deck back shoulder 12kg 10x3\n\nforearm\nforearm curl 7.5kg each 15x3\n\ncore\nabilow core 25kg 10x1, 11x2\nhanging leg raises in bar 10x3",
        "output": {
            "date": "2026-09-19",
            "sessions": [
                {
                    "muscle_group": "back",
                    "exercises": [
                        {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 30.0, "reps": 9}, {"weight_kg": 30.0, "reps": 9}, {"weight_kg": 30.0, "reps": 10}]},
                        {"name": "seated narrow grip row", "canonical": "seated_row", "sets": [{"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}]}
                    ]
                },
                {
                    "muscle_group": "triceps",
                    "exercises": [
                        {"name": "jm press", "canonical": "jm_press", "sets": [{"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}]},
                        {"name": "triceps push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 6}]}
                    ]
                },
                {
                    "muscle_group": "shoulders",
                    "exercises": [
                        {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 5.0, "reps": 10, "per_hand": True}, {"weight_kg": 5.0, "reps": 10, "per_hand": True}, {"weight_kg": 5.0, "reps": 10, "per_hand": True}]},
                        {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 15.0, "reps": 8}, {"weight_kg": 15.0, "reps": 8}, {"weight_kg": 15.0, "reps": 10}]},
                        {"name": "pec deck back shoulder", "canonical": "reverse_fly", "sets": [{"weight_kg": 12.0, "reps": 10}, {"weight_kg": 12.0, "reps": 10}, {"weight_kg": 12.0, "reps": 10}]}
                    ]
                },
                {
                    "muscle_group": "arms",
                    "exercises": [
                        {"name": "forearm curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 7.5, "reps": 15, "per_hand": True}, {"weight_kg": 7.5, "reps": 15, "per_hand": True}, {"weight_kg": 7.5, "reps": 15, "per_hand": True}]}
                    ]
                },
                {
                    "muscle_group": "core",
                    "exercises": [
                        {"name": "abilow core", "canonical": "ab_wheel", "sets": [{"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 11}, {"weight_kg": 25.0, "reps": 11}]},
                        {"name": "hanging leg raises in bar", "canonical": "hanging_leg_raise", "sets": [{"weight_kg": 0.0, "reps": 10}, {"weight_kg": 0.0, "reps": 10}, {"weight_kg": 0.0, "reps": 10}]}
                    ]
                }
            ],
            "session_note": ""
        }
    },
    "2026-09-21": {
        "input": "chest \npec deck 20kg 8x3\nincline press 20kg 8x2, 10x1\n\nback\nlat pull down - 30kg 10x2, 12x1\nseated row - 35k 9x3\n\nbiceps\npreachears curl 5kg each 11x3\nhammer curl 5kg each 11x3\n\nforearm\nforearm curl 7.5kg each 20x3",
        "output": {
            "date": "2026-09-21",
            "sessions": [
                {
                    "muscle_group": "chest",
                    "exercises": [
                        {"name": "pec deck", "canonical": "pec_deck", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}]},
                        {"name": "incline press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 10}]}
                    ]
                },
                {
                    "muscle_group": "back",
                    "exercises": [
                        {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 30.0, "reps": 10}, {"weight_kg": 30.0, "reps": 10}, {"weight_kg": 30.0, "reps": 12}]},
                        {"name": "seated row", "canonical": "seated_row", "sets": [{"weight_kg": 35.0, "reps": 9}, {"weight_kg": 35.0, "reps": 9}, {"weight_kg": 35.0, "reps": 9}]}
                    ]
                },
                {
                    "muscle_group": "biceps",
                    "exercises": [
                        {"name": "preachears curl", "canonical": "preacher_curl", "sets": [{"weight_kg": 5.0, "reps": 11, "per_hand": True}, {"weight_kg": 5.0, "reps": 11, "per_hand": True}, {"weight_kg": 5.0, "reps": 11, "per_hand": True}]},
                        {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 5.0, "reps": 11, "per_hand": True}, {"weight_kg": 5.0, "reps": 11, "per_hand": True}, {"weight_kg": 5.0, "reps": 11, "per_hand": True}]}
                    ]
                },
                {
                    "muscle_group": "arms",
                    "exercises": [
                        {"name": "forearm curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 20, "per_hand": True}]}
                    ]
                }
            ],
            "session_note": ""
        }
    },
    "2026-09-23": {
        "input": "cuki smith dipake orang 50 gerakan smith machine\n\nchest \npec deck 20kg 8x3\nincline chest press (multipress machine) press 20kg 12x1, 30kg 8x2\n\ntriceps\ntriceps push down 20kg 10x2, 9x1\njm press 15kg(maaf ya jm press keknya not today) ganti triceps overhead extention 10kg 8x3\n\nshoulder\nlateral rise 5kg each 10x3\nincline shoulder press 15kg 8x2, 10x1\nspec deck back shoulder 12kg 12x1, 16kg 7x1, 9x1\n\nbiceps\npreachears curl 7.5kg each right 8x3, left 8x2, 7x1\nhammer curl (skip sudah nda sanggup)",
        "output": {
            "date": "2026-09-23",
            "sessions": [
                {
                    "muscle_group": "chest",
                    "exercises": [
                        {"name": "pec deck", "canonical": "pec_deck", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}]},
                        {"name": "incline chest press (multipress machine)", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 20.0, "reps": 12}, {"weight_kg": 30.0, "reps": 8}, {"weight_kg": 30.0, "reps": 8}]}
                    ]
                },
                {
                    "muscle_group": "triceps",
                    "exercises": [
                        {"name": "triceps push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 9}]},
                        {"name": "triceps overhead extention", "canonical": "overhead_tricep_extension", "sets": [{"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 8}, {"weight_kg": 10.0, "reps": 8}]}
                    ]
                },
                {
                    "muscle_group": "shoulders",
                    "exercises": [
                        {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 5.0, "reps": 10, "per_hand": True}, {"weight_kg": 5.0, "reps": 10, "per_hand": True}, {"weight_kg": 5.0, "reps": 10, "per_hand": True}]},
                        {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 15.0, "reps": 8}, {"weight_kg": 15.0, "reps": 8}, {"weight_kg": 15.0, "reps": 10}]},
                        {"name": "pec deck back shoulder", "canonical": "reverse_fly", "sets": [{"weight_kg": 12.0, "reps": 12}, {"weight_kg": 16.0, "reps": 7}, {"weight_kg": 16.0, "reps": 9}]}
                    ]
                },
                {
                    "muscle_group": "biceps",
                    "exercises": [
                        {"name": "preachears curl", "canonical": "preacher_curl", "sets": [{"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 7, "per_hand": True}]}
                    ]
                }
            ],
            "session_note": "cuki smith dipake orang 50 gerakan smith machine"
        }
    },
    "2026-09-25": {
        "input": "leg\nsquad bar only(20kg) 10x3\nleg curl 30kg 11,12. 35kg 6x1\nadducter ke dalam 25kg 6,8,10\nleg extensions  30kg 10x1, 35kg 8x1, 10x1\ncalf press 64kg 11x1, 69kg 8x2\n\ncore\nabilow core 25kg 10x1 30kg \ncore training leg up in bar 10x3",
        "output": {
            "date": "2026-09-25",
            "sessions": [
                {
                    "muscle_group": "legs",
                    "exercises": [
                        {"name": "squad bar only", "canonical": "barbell_squat", "sets": [{"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 10}]},
                        {"name": "leg curl", "canonical": "leg_curl", "sets": [{"weight_kg": 30.0, "reps": 11}, {"weight_kg": 30.0, "reps": 12}, {"weight_kg": 35.0, "reps": 6}]},
                        {"name": "adducter ke dalam", "canonical": "hip_adduction", "sets": [{"weight_kg": 25.0, "reps": 6}, {"weight_kg": 25.0, "reps": 8}, {"weight_kg": 25.0, "reps": 10}]},
                        {"name": "leg extensions", "canonical": "leg_extension", "sets": [{"weight_kg": 30.0, "reps": 10}, {"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 10}]},
                        {"name": "calf press", "canonical": "calf_raise", "sets": [{"weight_kg": 64.0, "reps": 11}, {"weight_kg": 69.0, "reps": 8}, {"weight_kg": 69.0, "reps": 8}]}
                    ]
                },
                {
                    "muscle_group": "core",
                    "exercises": [
                        {"name": "abilow core", "canonical": "ab_wheel", "sets": [{"weight_kg": 25.0, "reps": 10}]},
                        {"name": "core training leg up in bar", "canonical": "hanging_leg_raise", "sets": [{"weight_kg": 0.0, "reps": 10}, {"weight_kg": 0.0, "reps": 10}, {"weight_kg": 0.0, "reps": 10}]}
                    ]
                }
            ],
            "session_note": ""
        }
    },
    "2026-09-26": {
        "input": "back\nlat pull down 35kg 8x3\nseated narrow grip row - 35kg 10x3\n\ntriceps\ntriceps push down 20kg 10x3\n\nshoulder\nlateral rise 5kg each 12x1, 7,5 each 8x2\nincline shoulder press 15kg 10x1, 12x1. 20kg 8x1",
        "output": {
            "date": "2026-09-26",
            "sessions": [
                {
                    "muscle_group": "back",
                    "exercises": [
                        {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}]},
                        {"name": "seated narrow grip row", "canonical": "seated_row", "sets": [{"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}]}
                    ]
                },
                {
                    "muscle_group": "triceps",
                    "exercises": [
                        {"name": "triceps push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 10}]}
                    ]
                },
                {
                    "muscle_group": "shoulders",
                    "exercises": [
                        {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 5.0, "reps": 12, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}]},
                        {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 12}, {"weight_kg": 20.0, "reps": 8}]}
                    ]
                }
            ],
            "session_note": "hari buru buru"
        }
    },
    "2026-09-28": {
        "input": "chest \npec deck 20kg 8x3\nincline press 20kg 8x1, 9x2\n\nback\nlat pull down - 35kg 8x3\nseated row - 35k 10x3\n\nbiceps\npreachears curl 5kg each 11x3\nhammer curl 5kg each 11x3\n\nforearm\nforearm curl 7.5kg each 20x3",
        "output": {
            "date": "2026-09-28",
            "sessions": [
                {
                    "muscle_group": "chest",
                    "exercises": [
                        {"name": "pec deck", "canonical": "pec_deck", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}]},
                        {"name": "incline press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}]}
                    ]
                },
                {
                    "muscle_group": "back",
                    "exercises": [
                        {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}]},
                        {"name": "seated row", "canonical": "seated_row", "sets": [{"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}]}
                    ]
                },
                {
                    "muscle_group": "biceps",
                    "exercises": [
                        {"name": "preachears curl", "canonical": "preacher_curl", "sets": [{"weight_kg": 5.0, "reps": 11, "per_hand": True}, {"weight_kg": 5.0, "reps": 11, "per_hand": True}, {"weight_kg": 5.0, "reps": 11, "per_hand": True}]},
                        {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 5.0, "reps": 11, "per_hand": True}, {"weight_kg": 5.0, "reps": 11, "per_hand": True}, {"weight_kg": 5.0, "reps": 11, "per_hand": True}]}
                    ]
                },
                {
                    "muscle_group": "arms",
                    "exercises": [
                        {"name": "forearm curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 20, "per_hand": True}]}
                    ]
                }
            ],
            "session_note": ""
        }
    },
    "2026-09-30": {
        "input": "chest \npec deck 20kg 8x2, 10x1\nincline chest press 20kg 9x3\n\ntriceps\ntriceps push down 20kg 8x2, 6x1\njm press 15kg 10x3\n\nshoulder\nlateral rise 7.5kg each 8x3\nincline shoulder press 20kg/10kg each 6x3\npec deck back shoulder 16kg 8x2, 10x1\n\nbiceps\npreachears curl 5kg drop beban fatigue 8x3\nhammer curl 7.5kg 8x3",
        "output": {
            "date": "2026-09-30",
            "sessions": [
                {
                    "muscle_group": "chest",
                    "exercises": [
                        {"name": "pec deck", "canonical": "pec_deck", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 10}]},
                        {"name": "incline chest press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}]}
                    ]
                },
                {
                    "muscle_group": "triceps",
                    "exercises": [
                        {"name": "triceps push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 6}]},
                        {"name": "jm press", "canonical": "jm_press", "sets": [{"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}]}
                    ]
                },
                {
                    "muscle_group": "shoulders",
                    "exercises": [
                        {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}]},
                        {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 10.0, "reps": 6, "per_hand": True}, {"weight_kg": 10.0, "reps": 6, "per_hand": True}, {"weight_kg": 10.0, "reps": 6, "per_hand": True}]},
                        {"name": "pec deck back shoulder", "canonical": "reverse_fly", "sets": [{"weight_kg": 16.0, "reps": 8}, {"weight_kg": 16.0, "reps": 8}, {"weight_kg": 16.0, "reps": 10}]}
                    ]
                },
                {
                    "muscle_group": "biceps",
                    "exercises": [
                        {"name": "preachears curl", "canonical": "preacher_curl", "sets": [{"weight_kg": 5.0, "reps": 8, "note": "drop beban fatigue"}, {"weight_kg": 5.0, "reps": 8, "note": "drop beban fatigue"}, {"weight_kg": 5.0, "reps": 8, "note": "drop beban fatigue"}]},
                        {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 7.5, "reps": 8}, {"weight_kg": 7.5, "reps": 8}, {"weight_kg": 7.5, "reps": 8}]}
                    ]
                }
            ],
            "session_note": ""
        }
    },
    "2026-10-02": {
        "input": "leg\nsquad bar only(20kg) 10x1, 11x1, 14x1\nleg curl 35kg 8x3\nadducter ke dalam 25kg 10x3\nleg extensions  35kg 8x2, 9x1\ncalf press 69kg 8x3\n\ncore\nabilow core 30kg 6x3\nhanging leg raise in bar 10x3",
        "output": {
            "date": "2026-10-02",
            "sessions": [
                {
                    "muscle_group": "legs",
                    "exercises": [
                        {"name": "squad bar only", "canonical": "barbell_squat", "sets": [{"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 11}, {"weight_kg": 20.0, "reps": 14}]},
                        {"name": "leg curl", "canonical": "leg_curl", "sets": [{"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}]},
                        {"name": "adducter ke dalam", "canonical": "hip_adduction", "sets": [{"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}]},
                        {"name": "leg extensions", "canonical": "leg_extension", "sets": [{"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 9}]},
                        {"name": "calf press", "canonical": "calf_raise", "sets": [{"weight_kg": 69.0, "reps": 8}, {"weight_kg": 69.0, "reps": 8}, {"weight_kg": 69.0, "reps": 8}]}
                    ]
                },
                {
                    "muscle_group": "core",
                    "exercises": [
                        {"name": "abilow core", "canonical": "ab_wheel", "sets": [{"weight_kg": 30.0, "reps": 6}, {"weight_kg": 30.0, "reps": 6}, {"weight_kg": 30.0, "reps": 6}]},
                        {"name": "hanging leg raise in bar", "canonical": "hanging_leg_raise", "sets": [{"weight_kg": 0.0, "reps": 10}, {"weight_kg": 0.0, "reps": 10}, {"weight_kg": 0.0, "reps": 10}]}
                    ]
                }
            ],
            "session_note": ""
        }
    },
    "2026-10-03": {
        "input": "back\nlat pull down 35kg 8x3\nseated narrow grip row - 35kg 10x3\n\ntriceps\njm press 15kg 10x2, 11x1\ntriceps push down 20kg 10x2, 7x1\n\nshoulder\nlateral rise 7,5kg each 8x3\nincline shoulder press 20kg 8x1\npec deck back shoulder 16kg 9x2, 7x1\n\nforearm\nforearm curl 7.5kg each 20x3\n\ncore\nabilow core 30kg 6x3\nhanging leg raises in bar 10x3",
        "output": {
            "date": "2026-10-03",
            "sessions": [
                {
                    "muscle_group": "back",
                    "exercises": [
                        {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}]},
                        {"name": "seated narrow grip row", "canonical": "seated_row", "sets": [{"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}]}
                    ]
                },
                {
                    "muscle_group": "triceps",
                    "exercises": [
                        {"name": "jm press", "canonical": "jm_press", "sets": [{"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 11}]},
                        {"name": "triceps push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 10}, {"weight_kg": 20.0, "reps": 7}]}
                    ]
                },
                {
                    "muscle_group": "shoulders",
                    "exercises": [
                        {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}]},
                        {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 20.0, "reps": 8}]},
                        {"name": "pec deck back shoulder", "canonical": "reverse_fly", "sets": [{"weight_kg": 16.0, "reps": 9}, {"weight_kg": 16.0, "reps": 9}, {"weight_kg": 16.0, "reps": 7}]}
                    ]
                },
                {
                    "muscle_group": "arms",
                    "exercises": [
                        {"name": "forearm curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 20, "per_hand": True}]}
                    ]
                },
                {
                    "muscle_group": "core",
                    "exercises": [
                        {"name": "abilow core", "canonical": "ab_wheel", "sets": [{"weight_kg": 30.0, "reps": 6}, {"weight_kg": 30.0, "reps": 6}, {"weight_kg": 30.0, "reps": 6}]},
                        {"name": "hanging leg raises in bar", "canonical": "hanging_leg_raise", "sets": [{"weight_kg": 0.0, "reps": 10}, {"weight_kg": 0.0, "reps": 10}, {"weight_kg": 0.0, "reps": 10}]}
                    ]
                }
            ],
            "session_note": ""
        }
    },
    "2026-10-05": {
        "input": "chest \npec deck 20kg 8x2, 10x1\nincline chest press 20kg 9x3\n\nback\nlat pull down 35kg 10x3\nseated narrow grip row - 35kg 10x2, 12x1\n\nbiceps\npreachears curl 7.5kg each 6x3\nhammer curl 7.5kg each 6x2, 8x1\n\nforearm\nforearm curl 7.5kg each 20x2, 15x2",
        "output": {
            "date": "2026-10-05",
            "sessions": [
                {
                    "muscle_group": "chest",
                    "exercises": [
                        {"name": "pec deck", "canonical": "pec_deck", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 10}]},
                        {"name": "incline chest press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}]}
                    ]
                },
                {
                    "muscle_group": "back",
                    "exercises": [
                        {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}]},
                        {"name": "seated narrow grip row", "canonical": "seated_row", "sets": [{"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 12}]}
                    ]
                },
                {
                    "muscle_group": "biceps",
                    "exercises": [
                        {"name": "preachears curl", "canonical": "preacher_curl", "sets": [{"weight_kg": 7.5, "reps": 6, "per_hand": True}, {"weight_kg": 7.5, "reps": 6, "per_hand": True}, {"weight_kg": 7.5, "reps": 6, "per_hand": True}]},
                        {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 7.5, "reps": 6, "per_hand": True}, {"weight_kg": 7.5, "reps": 6, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}]}
                    ]
                },
                {
                    "muscle_group": "arms",
                    "exercises": [
                        {"name": "forearm curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 15, "per_hand": True}, {"weight_kg": 7.5, "reps": 15, "per_hand": True}]}
                    ]
                }
            ],
            "session_note": ""
        }
    },
    "2026-10-07": {
        "input": "chest \npec deck 20kg 8x2, 10x1\nincline chest press 20kg 9x3\n\ntriceps\njm press 15kg 10x3\ntriceps push down 20kg 7x3\n\nshoulder\nlateral rise 7,5kg each 8x3\nincline shoulder press 20kg 8x1\npec deck back shoulder 16kg 7x2, 9x1\n\nbiceps\npreachears curl 7.5kg each 6x3\nhammer curl 7.5kg each 6x2, 8x1",
        "output": {
            "date": "2026-10-07",
            "sessions": [
                {
                    "muscle_group": "chest",
                    "exercises": [
                        {"name": "pec deck", "canonical": "pec_deck", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 10}]},
                        {"name": "incline chest press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}]}
                    ]
                },
                {
                    "muscle_group": "triceps",
                    "exercises": [
                        {"name": "jm press", "canonical": "jm_press", "sets": [{"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}]},
                        {"name": "triceps push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 20.0, "reps": 7}, {"weight_kg": 20.0, "reps": 7}, {"weight_kg": 20.0, "reps": 7}]}
                    ]
                },
                {
                    "muscle_group": "shoulders",
                    "exercises": [
                        {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}]},
                        {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 20.0, "reps": 8}]},
                        {"name": "pec deck back shoulder", "canonical": "reverse_fly", "sets": [{"weight_kg": 16.0, "reps": 7}, {"weight_kg": 16.0, "reps": 7}, {"weight_kg": 16.0, "reps": 9}]}
                    ]
                },
                {
                    "muscle_group": "biceps",
                    "exercises": [
                        {"name": "preachears curl", "canonical": "preacher_curl", "sets": [{"weight_kg": 7.5, "reps": 6, "per_hand": True}, {"weight_kg": 7.5, "reps": 6, "per_hand": True}, {"weight_kg": 7.5, "reps": 6, "per_hand": True}]},
                        {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 7.5, "reps": 6, "per_hand": True}, {"weight_kg": 7.5, "reps": 6, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}]}
                    ]
                }
            ],
            "session_note": "hari lelah under perform 2 hari ga pulang"
        }
    },
    "2026-10-09": {
        "input": "leg\nsquad bar only+10kg plate(30kg) 6,7,8\nleg curl 35kg 10x3\nadducter ke dalam 25kg 10x2, 7x1\nleg extensions  35kg 8x1, 10x2\ncalf press 69kg 8x2, 9x1\n\ncore\nabilow core 30kg 7x3\nhanging leg raise in bar 10x3",
        "output": {
            "date": "2026-10-09",
            "sessions": [
                {
                    "muscle_group": "legs",
                    "exercises": [
                        {"name": "squad bar only+10kg plate", "canonical": "barbell_squat", "sets": [{"weight_kg": 30.0, "reps": 6}, {"weight_kg": 30.0, "reps": 7}, {"weight_kg": 30.0, "reps": 8}]},
                        {"name": "leg curl", "canonical": "leg_curl", "sets": [{"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}]},
                        {"name": "adducter ke dalam", "canonical": "hip_adduction", "sets": [{"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 10}, {"weight_kg": 25.0, "reps": 7}]},
                        {"name": "leg extensions", "canonical": "leg_extension", "sets": [{"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 10}]},
                        {"name": "calf press", "canonical": "calf_raise", "sets": [{"weight_kg": 69.0, "reps": 8}, {"weight_kg": 69.0, "reps": 8}, {"weight_kg": 69.0, "reps": 9}]}
                    ]
                },
                {
                    "muscle_group": "core",
                    "exercises": [
                        {"name": "abilow core", "canonical": "ab_wheel", "sets": [{"weight_kg": 30.0, "reps": 7}, {"weight_kg": 30.0, "reps": 7}, {"weight_kg": 30.0, "reps": 7}]},
                        {"name": "hanging leg raise in bar", "canonical": "hanging_leg_raise", "sets": [{"weight_kg": 0.0, "reps": 10}, {"weight_kg": 0.0, "reps": 10}, {"weight_kg": 0.0, "reps": 10}]}
                    ]
                }
            ],
            "session_note": ""
        }
    },
    "2026-10-12": {
        "input": "chest \npec deck 20kg 9x2, 10x1\nincline chest press 20kg 9x3\n\nback\nlat pull down 35kg 10x1, 8x2\nseated narrow grip row - 40kg 7x3\n\nbiceps\npreachears curl 7.5kg each 8,6,5\nhammer curl 7.5kg each 6x2, 8x1\n\nforearm\nforearm curl 7.5kg each 20x3",
        "output": {
            "date": "2026-10-12",
            "sessions": [
                {
                    "muscle_group": "chest",
                    "exercises": [
                        {"name": "pec deck", "canonical": "pec_deck", "sets": [{"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 10}]},
                        {"name": "incline chest press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}]}
                    ]
                },
                {
                    "muscle_group": "back",
                    "exercises": [
                        {"name": "lat pull down", "canonical": "lat_pulldown", "sets": [{"weight_kg": 35.0, "reps": 10}, {"weight_kg": 35.0, "reps": 8}, {"weight_kg": 35.0, "reps": 8}]},
                        {"name": "seated narrow grip row", "canonical": "seated_row", "sets": [{"weight_kg": 40.0, "reps": 7}, {"weight_kg": 40.0, "reps": 7}, {"weight_kg": 40.0, "reps": 7}]}
                    ]
                },
                {
                    "muscle_group": "biceps",
                    "exercises": [
                        {"name": "preachears curl", "canonical": "preacher_curl", "sets": [{"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 6, "per_hand": True}, {"weight_kg": 7.5, "reps": 5, "per_hand": True}]},
                        {"name": "hammer curl", "canonical": "hammer_curl", "sets": [{"weight_kg": 7.5, "reps": 6, "per_hand": True}, {"weight_kg": 7.5, "reps": 6, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}]}
                    ]
                },
                {
                    "muscle_group": "arms",
                    "exercises": [
                        {"name": "forearm curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 20, "per_hand": True}]}
                    ]
                }
            ],
            "session_note": ""
        }
    },
    "2026-10-14": {
        "input": "chest(under perform kekenyangan) \npec deck 20kg 9x2, 7x1\nincline chest press 20kg 9x2, 7x1\n\ntriceps\njm press 15kg 10x3\ntriceps push down 20kg 8x2\none arm triceps push down 12x1 5kg each\n\nshoulder\nlateral rise 7,5kg each 8x3\nincline shoulder press 7.5kg each 8x3\npec deck back shoulder 16kg 8x3\n\nforearm\nforearm curl 7.5kg each 20x3",
        "output": {
            "date": "2026-10-14",
            "sessions": [
                {
                    "muscle_group": "chest",
                    "exercises": [
                        {"name": "pec deck", "canonical": "pec_deck", "sets": [{"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 7}]},
                        {"name": "incline chest press", "canonical": "incline_dumbbell_press", "sets": [{"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 9}, {"weight_kg": 20.0, "reps": 7}]}
                    ]
                },
                {
                    "muscle_group": "triceps",
                    "exercises": [
                        {"name": "jm press", "canonical": "jm_press", "sets": [{"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}, {"weight_kg": 15.0, "reps": 10}]},
                        {"name": "triceps push down", "canonical": "tricep_pushdown", "sets": [{"weight_kg": 20.0, "reps": 8}, {"weight_kg": 20.0, "reps": 8}]},
                        {"name": "one arm triceps push down", "canonical": "single_arm_tricep_pushdown", "sets": [{"weight_kg": 5.0, "reps": 12, "per_hand": True}]}
                    ]
                },
                {
                    "muscle_group": "shoulders",
                    "exercises": [
                        {"name": "lateral rise", "canonical": "lateral_raise", "sets": [{"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}]},
                        {"name": "incline shoulder press", "canonical": "dumbbell_shoulder_press", "sets": [{"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}, {"weight_kg": 7.5, "reps": 8, "per_hand": True}]},
                        {"name": "pec deck back shoulder", "canonical": "reverse_fly", "sets": [{"weight_kg": 16.0, "reps": 8}, {"weight_kg": 16.0, "reps": 8}, {"weight_kg": 16.0, "reps": 8}]}
                    ]
                },
                {
                    "muscle_group": "arms",
                    "exercises": [
                        {"name": "forearm curl", "canonical": "wrist_curl", "sets": [{"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 20, "per_hand": True}, {"weight_kg": 7.5, "reps": 20, "per_hand": True}]}
                    ]
                }
            ],
            "session_note": "under perform kekenyangan"
        }
    }
}

def write_recent_gold():
    gold_dir = "dataset/gold"
    os.makedirs(gold_dir, exist_ok=True)
    count = 0
    for date, item in NEW_GOLD_SESSIONS.items():
        file_path = os.path.join(gold_dir, f"{date}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=4)
        count += 1
        print(f"Generated: {file_path}")
    print(f"Done! Created {count} gold files.")

if __name__ == "__main__":
    write_recent_gold()
