"""Comprehensive unit and integration tests for Person 3 AI/ML Pipeline."""

import json
import os
import unittest

from ai.extraction.extractor import FieldReportExtractor
from ai.extraction.normalizer import (
    extract_and_normalize_asset,
    extract_progress_pct,
    normalize_discipline,
    normalize_field_event_data,
    normalize_location,
    normalize_status,
)
from ai.matching.embedder import SemanticEmbedder
from ai.matching.explainer import MatchExplainer
from ai.matching.matcher import ScheduleMatcher
from ai.matching.reranker import ContextualReranker
from ai.matching.retriever import L5L6Retriever
from ai.pipeline import Person3Pipeline, get_demo_schedule_activities


class TestNormalization(unittest.TestCase):
    """Tests for construction discipline, location, asset, and progress normalizers."""

    def test_discipline_normalization(self):
        self.assertEqual(normalize_discipline("spool erection"), "Piping")
        self.assertEqual(normalize_discipline("pipe"), "Piping")
        self.assertEqual(normalize_discipline("supports"), "Mechanical")
        self.assertEqual(normalize_discipline("pipe support"), "Mechanical")
        self.assertEqual(normalize_discipline("concrete foundation"), "Civil")
        self.assertEqual(normalize_discipline("cable tray"), "Electrical")
        self.assertEqual(normalize_discipline("pressure transmitter"), "Instrumentation")

    def test_location_normalization(self):
        self.assertEqual(normalize_location("u3"), "Unit 3")
        self.assertEqual(normalize_location("u-3"), "Unit 3")
        self.assertEqual(normalize_location("unit-3"), "Unit 3")
        self.assertEqual(normalize_location("Unit 3"), "Unit 3")
        self.assertEqual(normalize_location("Area 5"), "Area 5")
        self.assertIsNone(normalize_location("unspecified room"))

    def test_asset_normalization(self):
        self.assertEqual(extract_and_normalize_asset("24-XX spool erected"), "24-XX")
        self.assertEqual(extract_and_normalize_asset("Line 24 work completed"), "24-XX")
        self.assertEqual(extract_and_normalize_asset("work on Line-24"), "24-XX")
        self.assertEqual(extract_and_normalize_asset("pump P-101A checked"), "P-101A")
        self.assertIsNone(extract_and_normalize_asset("routine cleanup without tags"))

    def test_progress_pct_extraction(self):
        self.assertEqual(extract_progress_pct("approximately 50 percent complete"), 50.0)
        self.assertEqual(extract_progress_pct("progress at 75%"), 75.0)
        self.assertEqual(extract_progress_pct("fifty percent done"), 50.0)
        self.assertIsNone(extract_progress_pct("completed today"))

    def test_status_normalization(self):
        self.assertEqual(normalize_status("erected today"), "completed")
        self.assertEqual(normalize_status("work completed"), "completed")
        self.assertEqual(normalize_status("support installation", progress_pct=50.0), "in_progress")
        self.assertEqual(normalize_status("ongoing work"), "in_progress")


class TestFieldReportExtractor(unittest.TestCase):
    """Tests for structured field report extraction and schema adherence."""

    def setUp(self):
        self.extractor = FieldReportExtractor(prefer_offline=True)

    def test_empty_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.extractor.extract("")

        with self.assertRaises(ValueError):
            self.extractor.extract("   ")

    def test_offline_case_a_extraction(self):
        raw = "24-XX spool erected today at Unit 3."
        evt = self.extractor.extract(raw, event_id="EVT-0001", project_id="PRJ-DEMO-01")

        self.assertEqual(evt["event_id"], "EVT-0001")
        self.assertEqual(evt["project_id"], "PRJ-DEMO-01")
        self.assertEqual(evt["extracted"]["discipline"], "Piping")
        self.assertEqual(evt["extracted"]["location"], "Unit 3")
        self.assertEqual(evt["extracted"]["asset_or_reference"], "24-XX")
        self.assertEqual(evt["extracted"]["status"], "completed")
        self.assertGreaterEqual(evt["extraction_confidence"], 0.90)

    def test_offline_case_b_extraction(self):
        raw = "Line 24 work completed."
        evt = self.extractor.extract(raw, event_id="EVT-0002", project_id="PRJ-DEMO-01")

        self.assertEqual(evt["extracted"]["discipline"], "Piping")
        self.assertEqual(evt["extracted"]["asset_or_reference"], "24-XX")
        self.assertEqual(evt["extracted"]["status"], "completed")
        self.assertLess(evt["extraction_confidence"], 0.85)

    def test_offline_case_c_extraction(self):
        raw = "Pipe support installation is approximately 50 percent complete at Unit 3."
        evt = self.extractor.extract(raw, event_id="EVT-0003", project_id="PRJ-DEMO-01")

        self.assertEqual(evt["extracted"]["discipline"], "Mechanical")
        self.assertEqual(evt["extracted"]["status"], "in_progress")
        self.assertIn("progress", evt)
        self.assertEqual(evt["progress"]["actual_progress_pct"], 50.0)


class TestEmbeddingsAndRetrieval(unittest.TestCase):
    """Tests for SemanticEmbedder and L5L6Retriever."""

    def setUp(self):
        self.embedder = SemanticEmbedder(prefer_offline=True)
        self.retriever = L5L6Retriever(embedder=self.embedder)
        self.activities = get_demo_schedule_activities()

    def test_embedder_self_similarity(self):
        text = "Erect Line 24-XX Piping Unit 3"
        sim = self.embedder.similarity(text, text)
        self.assertAlmostEqual(sim, 1.0, places=2)

    def test_embedder_unrelated_similarity_is_low(self):
        text_a = "Erect Line 24-XX Piping Unit 3"
        text_b = "Excavation and foundation work Civil Area 9"
        sim = self.embedder.similarity(text_a, text_b)
        self.assertLess(sim, 0.40)

    def test_retriever_ranks_piping_for_piping_event(self):
        field_event = {
            "raw_text": "24-XX spool erected today at Unit 3.",
            "extracted": {
                "activity": "24-XX spool erection",
                "discipline": "Piping",
                "location": "Unit 3",
                "asset_or_reference": "24-XX",
                "context": "Spool erection",
            },
        }
        candidates = self.retriever.retrieve(field_event, self.activities, top_k=3)
        self.assertTrue(len(candidates) >= 1)
        # Top candidate must be a 24-XX activity
        self.assertIn("24-XX", candidates[0][0]["activity_name"])


class TestDemoCasesEndToEnd(unittest.TestCase):
    """End-to-end test cases verifying Case A, Case B, and Case C matching behavior."""

    def setUp(self):
        self.pipeline = Person3Pipeline(prefer_offline=True)
        self.activities = get_demo_schedule_activities()

    def test_case_a_high_confidence(self):
        """Case A: 24-XX spool erected today at Unit 3.

        Expected: PIP-1024 Erect Line 24-XX, confidence >= 0.90, review_required = False.
        """
        raw = "24-XX spool erected today at Unit 3."
        field_event, match_result = self.pipeline.run(raw, self.activities, event_id="EVT-0001")

        # Extraction checks
        self.assertEqual(field_event["extracted"]["discipline"], "Piping")
        self.assertEqual(field_event["extracted"]["location"], "Unit 3")
        self.assertEqual(field_event["extracted"]["asset_or_reference"], "24-XX")

        # Matching checks
        self.assertEqual(match_result["selected_activity_id"], "PIP-1024")
        self.assertEqual(match_result["candidates"][0]["activity_name"], "Erect Line 24-XX")
        self.assertGreaterEqual(match_result["candidates"][0]["final_confidence"], 0.90)
        self.assertFalse(match_result["review_required"])
        self.assertIsNone(match_result["review_reason"])

        # Check match reasons contain expected explanations
        reasons = match_result["candidates"][0]["match_reason"]
        self.assertTrue(any("24-XX" in r for r in reasons))
        self.assertTrue(any("Piping" in r for r in reasons))
        self.assertTrue(any("Unit 3" in r for r in reasons))

    def test_case_b_ambiguity_and_human_review(self):
        """Case B: Line 24 work completed.

        Expected: Ambiguous candidates (PIP-1024, 1025, 1026, 1027), confidence <= 0.89, review_required = True.
        """
        raw = "Line 24 work completed."
        field_event, match_result = self.pipeline.run(raw, self.activities, event_id="EVT-0002")

        # Ambiguity check
        self.assertTrue(match_result["review_required"])
        self.assertLessEqual(match_result["candidates"][0]["final_confidence"], 0.89)
        self.assertIn("Multiple schedule activities relate to Line 24", match_result["review_reason"])

        # Check that top candidate set includes Line 24 activities
        candidate_ids = [c["activity_id"] for c in match_result["candidates"][:4]]
        expected_ids = {"PIP-1024", "PIP-1025", "PIP-1026", "PIP-1027"}
        self.assertTrue(set(candidate_ids).issubset(expected_ids) or len(set(candidate_ids).intersection(expected_ids)) >= 3)

    def test_case_c_deviation_and_progress(self):
        """Case C: Pipe support installation is approximately 50 percent complete at Unit 3.

        Expected: PIP-1022 Pipe support installation, progress = 50.0%.
        """
        raw = "Pipe support installation is approximately 50 percent complete at Unit 3."
        field_event, match_result = self.pipeline.run(raw, self.activities, event_id="EVT-0003")

        # Extraction checks
        self.assertEqual(field_event["extracted"]["discipline"], "Mechanical")
        self.assertEqual(field_event["extracted"]["location"], "Unit 3")
        self.assertIn("progress", field_event)
        self.assertEqual(field_event["progress"]["actual_progress_pct"], 50.0)

        # Matching checks
        self.assertEqual(match_result["selected_activity_id"], "PIP-1022")
        self.assertEqual(match_result["candidates"][0]["activity_name"], "Pipe support installation")
        self.assertGreaterEqual(match_result["candidates"][0]["final_confidence"], 0.90)

    def test_fixtures_matching_directly(self):
        """Verifies matching directly on pre-extracted fixture JSON files."""
        # Fixture 1: High confidence
        with open("tests/fixtures/field_event_high_confidence.json") as f:
            fe_high = json.load(f)
        res_high = self.pipeline.match(fe_high, self.activities)
        self.assertEqual(res_high["selected_activity_id"], "PIP-1024")
        self.assertFalse(res_high["review_required"])

        # Fixture 2: Ambiguous
        with open("tests/fixtures/field_event_ambiguous.json") as f:
            fe_amb = json.load(f)
        res_amb = self.pipeline.match(fe_amb, self.activities)
        self.assertTrue(res_amb["review_required"])
        self.assertIn("Multiple schedule activities relate to Line 24", res_amb["review_reason"])

        # Fixture 3: Deviation
        with open("tests/fixtures/field_event_deviation.json") as f:
            fe_dev = json.load(f)
        res_dev = self.pipeline.match(fe_dev, self.activities)
        self.assertEqual(res_dev["selected_activity_id"], "PIP-1022")
        self.assertFalse(res_dev["review_required"])
        self.assertEqual(res_dev["candidates"][0]["activity_name"], "Pipe support installation")
        self.assertGreaterEqual(res_dev["candidates"][0]["final_confidence"], 0.90)


class TestContractSchemaCompliance(unittest.TestCase):
    """Verifies that generated FieldEvent and MatchResult objects match existing schema templates."""

    def setUp(self):
        self.pipeline = Person3Pipeline(prefer_offline=True)
        self.activities = get_demo_schedule_activities()

        with open("contracts/schemas/field_event.json") as f:
            self.fe_schema = json.load(f)
        with open("contracts/schemas/match_result.json") as f:
            self.mr_schema = json.load(f)

    def test_field_event_schema_compliance(self):
        evt, _ = self.pipeline.run("24-XX spool erected today at Unit 3.", self.activities, event_id="EVT-0001")

        for key in self.fe_schema:
            self.assertIn(key, evt, f"Missing required root key: {key}")

        for key in self.fe_schema["source"]:
            self.assertIn(key, evt["source"], f"Missing source key: {key}")

        for key in self.fe_schema["extracted"]:
            self.assertIn(key, evt["extracted"], f"Missing extracted key: {key}")

    def test_match_result_schema_compliance(self):
        _, mat = self.pipeline.run("24-XX spool erected today at Unit 3.", self.activities, event_id="EVT-0001")

        for key in self.mr_schema:
            self.assertIn(key, mat, f"Missing required match key: {key}")

        candidate = mat["candidates"][0]
        schema_candidate = self.mr_schema["candidates"][0]

        for key in schema_candidate:
            self.assertIn(key, candidate, f"Missing candidate key: {key}")

        for key in schema_candidate["scores"]:
            self.assertIn(key, candidate["scores"], f"Missing score key: {key}")


if __name__ == "__main__":
    unittest.main()
