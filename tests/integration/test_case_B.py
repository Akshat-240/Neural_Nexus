import unittest
from integration.orchestrator import Orchestrator
import os

class TestCaseB(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator()
        
    def test_case_b(self):
        # Multiple candidates / low confidence, review required, no automatic schedule update
        report_text = "welding work ongoing." # Vague text
        
        res = self.orchestrator.process_update(
            project_id="PRJ-DEMO-01",
            report_text=report_text,
            image_ref=None
        )
        
        print("TEST CASE B RES:", res)
        self.assertNotEqual(res.get("pipeline_status"), "failed")
        self.assertTrue(res["verification"]["review_required"])
        self.assertEqual(res["verification"]["status"], "pending_review")

if __name__ == "__main__":
    unittest.main()
