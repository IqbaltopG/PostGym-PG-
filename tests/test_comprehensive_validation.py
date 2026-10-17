#!/usr/bin/env python3
"""
POST GYM — Comprehensive Validation Suite
Menguji akurasi model AI fine-tuned V2 + backend normalization engine
untuk semua kategori otot, slang gerakan fisik, typo fonetis, dan edge-case.
"""

import urllib.request
import json
import sys
import time

TEST_CASES = [
    # 1. CORE & DESKRIPTIF
    {
        "category": "Core / Descriptive",
        "input": "begantung kaki naik naik 12 10 10\nroda gelinding perut 15x3\ntahan badan lurus tiarap 45 detik x 3",
        "expected_canonicals": ["hanging_leg_raise", "ab_wheel", "plank"],
        "expected_muscle": "core"
    },
    # 2. DADA & VARIASI SLANG
    {
        "category": "Chest / Slang",
        "input": "rebahan dorong bar 50kg 8x3\nrebahan dorong miring 20k 10 10 8\npeluk mesin 35kg 12x3\ndorong lantai 20 15 12",
        "expected_canonicals": ["barbell_bench_press", "incline_chest_press", "pec_deck", "push_up"],
        "expected_muscle": "chest"
    },
    # 3. PUNGGUNG & SAYAP
    {
        "category": "Back / Lat & Rows",
        "input": "tarik kabel dari atas 40kg 10x3\ndayung duduk 35k 12 10 8\nbungkuk tarik besi 30kg 10x3\ngelantungan tarik badan 8 6 5",
        "expected_canonicals": ["lat_pulldown", "seated_row", "barbell_row", "pull_up"],
        "expected_muscle": "back"
    },
    # 4. KAKI, BOKONG & BETIS
    {
        "category": "Legs / Lower Body Slang",
        "input": "squad bar only 10x3\npantat naik turun 50kg 10 10 10\nkangkang mesin 35k 15x3\njepit paha 25kg 12x3\ntendang kaki ke depan 30kg 12x3\njinjit betis 40kg 15x3",
        "expected_canonicals": ["barbell_squat", "hip_thrust", "hip_abduction", "hip_adduction", "leg_extension", "calf_raise"],
        "expected_muscle": "legs"
    },
    # 5. BAHU & TRAPS
    {
        "category": "Shoulders / Raises & Press",
        "input": "duduk dorong beban ke atas 12.5kg each 10x3\nbuka tangan ke samping 7.5kg each 12x3\npeluk mesin kebalik 16kg 10x3\ntarik tali ke muka 15kg 12x3\ngedik bahu 20kg each 15x3",
        "expected_canonicals": ["dumbbell_shoulder_press", "lateral_raise", "reverse_fly", "face_pull", "dumbbell_shrug"],
        "expected_muscle": "shoulders"
    },
    # 6. LENGAN (BICEPS, TRICEPS, FOREARMS)
    {
        "category": "Arms / Biceps & Triceps",
        "input": "tekuk lengan 10kg each 10x3\npalu dambel 10kg each 10x3\ndorong tali ke bawah 20kg 10x3\nhancur jidat 15kg 10 10 8 sampe tremor\njm press 15kg 10x3\ntekuk pergelangan tangan 7.5kg each 20x3",
        "expected_canonicals": ["bicep_curl", "hammer_curl", "tricep_pushdown", "skullcrusher", "jm_press", "wrist_curl"],
        "expected_muscle": "arms"
    },
    # 7. TYPO FONETIS LOKAL INDONESIA
    {
        "category": "Phonetic Typos",
        "input": "skot 40k 10x3\nbencpres 50k 8x3\nletpul 35k 12 10 8\nhiptrast 60k 8x3\npusdon 20k 12x3\nbisep krol 8kg each 10x3",
        "expected_canonicals": ["barbell_squat", "barbell_bench_press", "lat_pulldown", "hip_thrust", "tricep_pushdown", "bicep_curl"],
        "expected_muscle": None
    },
    # 8. COMPOUND MULTIPLIER & SKIP NOTE
    {
        "category": "Compound Multipliers & Skip",
        "input": "incline press 20kg 9x2, 7x1\npec deck 20kg 9x2, 7x1\njm press 15kg 10x3 (skip)\ncapek banget hari ini",
        "expected_canonicals": ["incline_chest_press", "pec_deck"],
        "unexpected_canonicals": ["jm_press"],
        "expected_session_note": "capek banget hari ini"
    }
]

def run_validation():
    print("=" * 70)
    print("🏋️‍♂️ POST GYM — SYSTEM VALIDATION SUITE (AI V2 & CANONICAL ENGINE)")
    print("=" * 70)
    
    total_tests = len(TEST_CASES)
    passed_tests = 0
    all_canonicals_tested = 0
    matched_canonicals = 0
    results_summary = []

    for idx, tc in enumerate(TEST_CASES, 1):
        print(f"\n[{idx}/{total_tests}] Testing Category: {tc['category']}")
        payload = {"raw_text": tc["input"]}
        req = urllib.request.Request(
            "http://localhost:8000/api/parse",
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )

        try:
            start_t = time.time()
            with urllib.request.urlopen(req, timeout=30) as resp:
                res_data = json.loads(resp.read().decode('utf-8'))
            elapsed = time.time() - start_t
            
            if res_data.get("status") != "success":
                print(f"  ❌ FAILED: API Error -> {res_data.get('message')}")
                results_summary.append({"test": tc["category"], "status": "FAIL", "reason": res_data.get('message')})
                continue

            parsed = res_data.get("data", {})
            found_canonicals = []
            for s in parsed.get("sessions", []):
                for ex in s.get("exercises", []):
                    found_canonicals.append(ex.get("canonical"))

            print(f"  ⏱️  Inference Time: {elapsed:.2f}s")
            print(f"  📥 Expected Canonicals: {tc['expected_canonicals']}")
            print(f"  📤 Found Canonicals   : {found_canonicals}")

            # Check expected canonicals
            tc_passed = True
            missing = []
            for exp in tc["expected_canonicals"]:
                all_canonicals_tested += 1
                if exp in found_canonicals:
                    matched_canonicals += 1
                else:
                    missing.append(exp)
                    tc_passed = False

            # Check unexpected (e.g. skipped exercises)
            if "unexpected_canonicals" in tc:
                for unexp in tc["unexpected_canonicals"]:
                    if unexp in found_canonicals:
                        print(f"  ⚠️  Warning: Skipped exercise '{unexp}' was still included!")
                        tc_passed = False

            # Check session note
            if "expected_session_note" in tc:
                actual_note = parsed.get("session_note", "")
                if tc["expected_session_note"] not in actual_note:
                    print(f"  ⚠️  Note Mismatch: Expected '{tc['expected_session_note']}', got '{actual_note}'")

            if tc_passed:
                print(f"  ✅ PASSED (All {len(tc['expected_canonicals'])} canonicals matched perfectly!)")
                passed_tests += 1
                results_summary.append({"test": tc["category"], "status": "PASS", "missing": []})
            else:
                print(f"  ❌ PARTIAL / MISSED: Missing {missing}")
                results_summary.append({"test": tc["category"], "status": "PARTIAL", "missing": missing})

        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results_summary.append({"test": tc["category"], "status": "ERROR", "reason": str(e)})

    print("\n" + "=" * 70)
    print("📊 VALIDATION SUITE SUMMARY REPORT")
    print("=" * 70)
    print(f"• Total Test Suites Passed : {passed_tests} / {total_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"• Total Canonicals Verified: {matched_canonicals} / {all_canonicals_tested} ({matched_canonicals/all_canonicals_tested*100:.1f}%)")
    print("=" * 70)

    # Simpan hasil laporan ke file JSON untuk audit subagent
    with open("tests/validation_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "matched_canonicals": matched_canonicals,
            "all_canonicals_tested": all_canonicals_tested,
            "results": results_summary
        }, f, indent=2)

    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
