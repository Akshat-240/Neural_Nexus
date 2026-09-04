import unittest
from integration.orchestrator import Orchestrator
import os

class TestCaseA(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator()
        
    def test_case_a(self):
        # High confidence, evidence supportive, automatically verified, schedule updated.
        report_text = "24-XX spool erected today at Unit 3."
        # using the test image from cv/
        image_ref = "cv/test.jpg"
        
        # We need to assume project_id 1 is PRJ-DEMO-01
        res = self.orchestrator.process_update(
            project_id="PRJ-DEMO-01",
            report_text=report_text,
            image_ref=image_ref
        )
        
        print("TEST CASE A RES:", res)
        self.assertNotEqual(res.get("pipeline_status"), "failed")
        self.assertEqual(res["match"]["activity_id"], "PIP-1024")
        self.assertTrue(res["evidence"]["supportive"])
        self.assertEqual(res["verification"]["status"], "verified")
        self.assertFalse(res["schedule"]["deviation_flag"])

if __name__ == "__main__":
    unittest.main()
