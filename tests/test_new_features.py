import urllib.request
import json
import unittest

BASE_URL = "http://127.0.0.1:8000"

class TestPostGymNewFeatures(unittest.TestCase):
    def test_01_account_generation_and_status(self):
        # 1. Generate anonymous account
        req = urllib.request.Request(f"{BASE_URL}/api/account/generate", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            self.assertIn("account_id", data)
            self.assertTrue(data["account_id"].startswith("PGYM-"))
            self.assertFalse(data["is_pro"])

        acc_id = data["account_id"]

        # 2. Check initial status
        with urllib.request.urlopen(f"{BASE_URL}/api/account/status?id={acc_id}") as res:
            stat = json.loads(res.read().decode())
            self.assertEqual(stat["account_id"], acc_id)
            self.assertFalse(stat["is_pro"])
            self.assertEqual(stat["days_remaining"], 0)

        # 3. Redeem demo voucher
        voucher_payload = json.dumps({"account_id": acc_id, "voucher_code": "PGYM-PRO-2026"}).encode()
        req = urllib.request.Request(f"{BASE_URL}/api/account/redeem", data=voucher_payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            red = json.loads(res.read().decode())
            self.assertEqual(red["status"], "success")
            self.assertTrue(red["is_pro"])
            self.assertEqual(red["days_added"], 30)

        # 4. Status after voucher
        with urllib.request.urlopen(f"{BASE_URL}/api/account/status?id={acc_id}") as res:
            stat2 = json.loads(res.read().decode())
            self.assertTrue(stat2["is_pro"])
            self.assertGreaterEqual(stat2["days_remaining"], 29)

    def test_02_quick_log_and_undo(self):
        payload = json.dumps({
            "canonical": "pec_deck",
            "name": "Pec Deck Fly",
            "muscle_group": "chest",
            "weight_kg": 35.0,
            "reps": 12,
            "note": "Unit test 1-tap"
        }).encode()
        req = urllib.request.Request(f"{BASE_URL}/api/quick-log", data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            self.assertEqual(data["status"], "success")
            self.assertIn("today_sets", data)
            self.assertGreater(len(data["today_sets"]), 0)

        # Undo
        undo_payload = json.dumps({"canonical": "pec_deck"}).encode()
        req = urllib.request.Request(f"{BASE_URL}/api/quick-log/undo", data=undo_payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            undo_data = json.loads(res.read().decode())
            self.assertEqual(undo_data["status"], "success")

    def test_03_export_endpoints(self):
        # CSV Export
        with urllib.request.urlopen(f"{BASE_URL}/api/export/csv") as res:
            self.assertEqual(res.status, 200)
            self.assertIn("text/csv", res.headers.get("Content-Type", ""))
            content = res.read().decode()
            self.assertIn("date,muscle_group,exercise_name", content)

        # JSON Export
        with urllib.request.urlopen(f"{BASE_URL}/api/export/json") as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode())
            self.assertEqual(data["status"], "success")
            self.assertIn("data", data)
            self.assertGreater(data["total_records"], 0)

    def test_04_qris_simulation(self):
        req = urllib.request.Request(f"{BASE_URL}/api/account/generate", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            acc = json.loads(res.read().decode())
            acc_id = acc["account_id"]

        qris_payload = json.dumps({"account_id": acc_id, "duration_days": 30}).encode()
        req = urllib.request.Request(f"{BASE_URL}/api/account/simulate-qris", data=qris_payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            qris_res = json.loads(res.read().decode())
            self.assertEqual(qris_res["status"], "success")
            self.assertTrue(qris_res["is_pro"])

    def test_05_competitive_rank_and_session_summary(self):
        with urllib.request.urlopen(f"{BASE_URL}/api/today") as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode())
            self.assertIn("rank", data)
            rank = data["rank"]
            self.assertIn("total_rp", rank)
            self.assertIn("current_tier", rank)
            self.assertIn("tier_icon", rank)
            self.assertIn("progress_percent", rank)
            self.assertIn("all_tiers", rank)
            self.assertGreaterEqual(rank["total_rp"], 0)

if __name__ == "__main__":
    unittest.main()
