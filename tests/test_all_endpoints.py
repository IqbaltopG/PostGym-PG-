"""
Comprehensive Integration Test Suite for POST GYM
Tests all 18 API Endpoints + Static Frontend Assets + Business Logic
"""
import unittest
import urllib.request
import urllib.parse
import json
import os

BASE_URL = "http://127.0.0.1:8000"

def request_json(path, data=None, method=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

class TestAllEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate clean test account
        status, res = request_json("/api/account/generate", data={}, method="POST")
        cls.test_account_id = res["account_id"]

    # 1. FRONTEND STATIC ASSETS
    def test_01_static_assets(self):
        # Index HTML
        with urllib.request.urlopen(f"{BASE_URL}/") as res:
            self.assertEqual(res.status, 200)
            html = res.read().decode("utf-8")
            self.assertIn("POST", html)
            self.assertIn("competitive-rank-badge", html)
            self.assertIn("showVictoryModal", html)
            self.assertNotIn("tier-access-banner", html)

        # Style CSS
        with urllib.request.urlopen(f"{BASE_URL}/style.css") as res:
            self.assertEqual(res.status, 200)
            css = res.read().decode("utf-8")
            self.assertIn(".competitive-rank-badge", css)
            self.assertIn(".victory-card", css)

        # App JS
        with urllib.request.urlopen(f"{BASE_URL}/app.js") as res:
            self.assertEqual(res.status, 200)
            js = res.read().decode("utf-8")
            self.assertIn("gymApp", js)
            self.assertIn("rankInfo", js)

    # 2. SCHEDULE & WORKOUT PLAN
    def test_02_today_plan_and_rank(self):
        status, data = request_json("/api/today")
        self.assertEqual(status, 200)
        self.assertIn("rank", data)
        self.assertIn("current_tier", data["rank"])
        self.assertIn("total_rp", data["rank"])
        self.assertIn("all_tiers", data["rank"])
        self.assertGreaterEqual(len(data["rank"]["all_tiers"]), 10)
        self.assertIn("exercises", data)

    def test_03_schedule_get_and_post(self):
        status, original = request_json("/api/schedule")
        self.assertEqual(status, 200)
        self.assertIsInstance(original, dict)

        # Save schedule
        test_sched = dict(original)
        test_sched["senin"] = ["chest", "triceps"]
        status, save_res = request_json("/api/schedule", data=test_sched, method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(save_res.get("status"), "success")

        # Verify
        status, updated = request_json("/api/schedule")
        self.assertEqual(status, 200)
        self.assertEqual(updated["senin"], ["chest", "triceps"])

    # 3. EXERCISE LIST & TELEMETRY PROGRESS
    def test_04_exercise_list(self):
        status, data = request_json("/api/exercises/list")
        self.assertEqual(status, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("canonical", data[0])
        self.assertIn("name", data[0])

    def test_05_progress_and_recap(self):
        # Progress for a known exercise
        canonical = "pec_deck"
        status, prog = request_json(f"/api/progress/exercise/{canonical}")
        self.assertEqual(status, 200)
        self.assertIsInstance(prog, list)

        # Consistency recap
        status, recap = request_json("/api/progress/recap?period=month")
        self.assertEqual(status, 200)
        self.assertIsInstance(recap, list)

    # 4. QUICK LOG, REVERT, AND SESSION SUMMARY
    def test_06_quick_log_and_undo_flow(self):
        payload = {
            "canonical": "lateral_raise",
            "name": "Dumbbell Lateral Raise",
            "muscle_group": "shoulders",
            "weight_kg": 10.0,
            "reps": 15,
            "note": "Comprehensive test set"
        }
        status, log_res = request_json("/api/quick-log", data=payload, method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(log_res["status"], "success")
        self.assertIn("today_sets", log_res)
        self.assertIn("rank", log_res)
        self.assertIn("session_summary", log_res)
        self.assertGreater(log_res["session_summary"]["total_sets"], 0)

        # Undo the set
        undo_payload = {"canonical": "lateral_raise"}
        status, undo_res = request_json("/api/quick-log/undo", data=undo_payload, method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(undo_res["status"], "success")
        self.assertIn("rank", undo_res)
        self.assertIn("session_summary", undo_res)

    # 5. DATA EXPORT (CSV & JSON)
    def test_07_export_endpoints(self):
        with urllib.request.urlopen(f"{BASE_URL}/api/export/csv") as res:
            self.assertEqual(res.status, 200)
            self.assertIn("text/csv", res.headers.get("Content-Type", ""))
            csv_text = res.read().decode("utf-8")
            self.assertIn("date,muscle_group,exercise_name,canonical,set_id,weight_kg,reps", csv_text)

        status, json_data = request_json("/api/export/json")
        self.assertEqual(status, 200)
        self.assertEqual(json_data.get("status"), "success")
        self.assertIn("data", json_data)
        self.assertGreater(json_data["total_records"], 0)

    # 6. MONETIZATION (ANONYMOUS ACCOUNT, VOUCHERS, QRIS)
    def test_08_account_monetization_flow(self):
        acc_id = self.test_account_id

        # Initial free status
        status, stat = request_json(f"/api/account/status?id={acc_id}")
        self.assertEqual(status, 200)
        self.assertFalse(stat["is_pro"])

        # Redeem invalid voucher
        status, bad_v = request_json("/api/account/redeem", data={"account_id": acc_id, "voucher_code": "INVALID-CODE"}, method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(bad_v.get("status"), "error")

        # Simulate QRIS payment (30 days)
        status, qris = request_json("/api/account/simulate-qris", data={"account_id": acc_id, "duration_days": 30}, method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(qris.get("status"), "success")
        self.assertTrue(qris.get("is_pro"))

        # Check status after QRIS
        status, stat_pro = request_json(f"/api/account/status?id={acc_id}")
        self.assertTrue(stat_pro["is_pro"])
        self.assertGreaterEqual(stat_pro["days_remaining"], 29)

    # 7. PRO ACCESS GATE FOR AI PARSER & VIDEO
    def test_09_pro_gate_enforcement(self):
        # 1. Fresh free account
        _, free_acc = request_json("/api/account/generate", data={}, method="POST")
        free_id = free_acc["account_id"]

        # 2. AI Parse attempted by free user -> blocked with pro_required
        parse_payload = {"raw_text": "incline press 20kg 10 10", "account_id": free_id}
        status, free_parse = request_json("/api/parse", data=parse_payload, method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(free_parse.get("status"), "pro_required")

        # 3. AI Parse attempted by PRO user -> permitted
        pro_parse_payload = {"raw_text": "pec deck 30kg 12x3", "account_id": self.test_account_id}
        status, pro_parse = request_json("/api/parse", data=pro_parse_payload, method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(pro_parse.get("status"), "success")
        self.assertIn("data", pro_parse)

    # 8. SAVE WORKOUT LOG & HISTORY
    def test_10_save_workout_log(self):
        mock_workout = {
            "date": "2026-10-18",
            "sessions": [
                {
                    "muscle_group": "chest",
                    "exercises": [
                        {
                            "name": "Pec Deck Machine",
                            "canonical": "pec_deck",
                            "sets": [
                                {"weight_kg": 35.0, "reps": 12},
                                {"weight_kg": 35.0, "reps": 12}
                            ]
                        }
                    ]
                }
            ],
            "session_note": "Integration test verified"
        }
        status, res = request_json("/api/save", data=mock_workout, method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(res.get("status"), "success")
        self.assertIn("rank", res)
        self.assertIn("session_summary", res)

        # Check history includes it
        status, history = request_json("/api/history")
        self.assertEqual(status, 200)
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)

    # 9. AI VIDEO POSE FORM CHECK (YOLOv8)
    def test_11_video_analysis_flow(self):
        import requests
        sample_video_path = os.path.join(os.path.dirname(__file__), "sample_squat.mp4")
        if not os.path.exists(sample_video_path):
            return # Skip if video sample not present

        # 1. Test Free User Attempt -> Blocked with pro_required
        _, free_acc = request_json("/api/account/generate", data={}, method="POST")
        with open(sample_video_path, "rb") as vf:
            resp = requests.post(
                f"{BASE_URL}/api/analyze-video",
                files={"video": ("sample.mp4", vf, "video/mp4")},
                data={"exercise": "squat", "account_id": free_acc["account_id"]}
            )
        self.assertEqual(resp.status_code, 200)
        free_data = resp.json()
        self.assertEqual(free_data.get("status"), "pro_required")

        # 2. Test PRO User Attempt -> Successfully Analyzed by YOLOv8 Pose
        with open(sample_video_path, "rb") as vf:
            resp_pro = requests.post(
                f"{BASE_URL}/api/analyze-video",
                files={"video": ("sample.mp4", vf, "video/mp4")},
                data={"exercise": "squat", "account_id": self.test_account_id}
            )
        self.assertEqual(resp_pro.status_code, 200)
        pro_data = resp_pro.json()
        self.assertEqual(pro_data.get("status"), "success")
        self.assertIn("total_reps", pro_data)
        self.assertIn("accuracy_percent", pro_data)
        self.assertIn("video_url", pro_data)

        # 3. Verify annotated video is reachable
        video_url = f"{BASE_URL}{pro_data['video_url']}"
        v_check = requests.head(video_url)
        self.assertEqual(v_check.status_code, 200)

if __name__ == "__main__":
    unittest.main()
