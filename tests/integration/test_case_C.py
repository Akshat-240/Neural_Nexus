import unittest
from integration.orchestrator import Orchestrator
import os

class TestCaseC(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator()
        
    def test_case_c(self):
        # PIP-1022 deviation, actual=50%, planned=80%, variance=-30%, deviation=True
        # Actual is 50% for anything not completed according to our heuristic in orchestrator.py
        report_text = "Pipe support installation at Unit 3 started today."
        
        res = self.orchestrator.process_update(
            project_id="PRJ-DEMO-01",
            report_text=report_text,
            image_ref=None
        )
        
        self.assertNotEqual(res.get("pipeline_status"), "failed")
        self.assertEqual(res["match"]["activity_id"], "PIP-1022")
        self.assertTrue(res["schedule"]["deviation_flag"])
        self.assertLess(res["schedule"]["variance_pct"], -10)

if __name__ == "__main__":
    unittest.main()
