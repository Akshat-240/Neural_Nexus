"""Person 3 AI/ML Pipeline: Structured field report extraction and L5/L6 schedule matching."""

from typing import Any, Dict, List, Optional, Tuple

from ai.extraction.extractor import FieldReportExtractor
from ai.matching.embedder import SemanticEmbedder
from ai.matching.matcher import ScheduleMatcher


class Person3Pipeline:
    """End-to-end Person 3 pipeline orchestrator.

    Executes:
    Raw field report -> LLM/Deterministic Extraction -> Structured Field Event
    -> Normalization -> L5/L6 Retrieval -> Contextual Re-ranking -> Match Result
    """

    def __init__(
        self,
        prefer_offline: bool = True,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Initializes Person 3 pipeline.

        Args:
            prefer_offline: If True (default), runs deterministic offline extraction and
                            local NumPy vectorizer. If False and api_key is available,
                            uses external LLM / embedding API.
            api_key: Optional API key.
            base_url: Optional base URL for OpenAI-compatible endpoint.
            model: Optional model name.
        """
        self.extractor = FieldReportExtractor(
            api_key=api_key,
            base_url=base_url,
            model=model,
            prefer_offline=prefer_offline,
        )
        self.embedder = SemanticEmbedder(
            api_key=api_key,
            base_url=base_url,
            prefer_offline=prefer_offline,
        )
        self.matcher = ScheduleMatcher(embedder=self.embedder)

    def extract(
        self,
        raw_text: str,
        event_id: Optional[str] = None,
        project_id: str = "PRJ-DEMO-01",
        source_ref: str = "daily_report",
        source_type: str = "text",
        evidence_refs: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Runs stage 1: Structured extraction and normalization.

        Args:
            raw_text: Unstructured field note.
            event_id: Unique event ID.
            project_id: Project identifier.
            source_ref: Source report reference.
            source_type: Source type (default 'text').
            evidence_refs: Associated evidence IDs.

        Returns:
            Dict conforming to contracts/schemas/field_event.json.
        """
        return self.extractor.extract(
            raw_text=raw_text,
            event_id=event_id,
            project_id=project_id,
            source_ref=source_ref,
            source_type=source_type,
            evidence_refs=evidence_refs,
        )

    def match(
        self,
        field_event: Dict[str, Any],
        schedule_activities: List[Dict[str, Any]],
        match_id: Optional[str] = None,
        visual_evidence_score: Optional[float] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Runs stage 2: L5/L6 retrieval, contextual re-ranking, and explainability.

        Args:
            field_event: Extracted field event dict.
            schedule_activities: List of schedule activity dicts.
            match_id: Unique match ID.
            visual_evidence_score: Optional visual score from Person 4.
            top_k: Number of candidates to return.

        Returns:
            Dict conforming to contracts/schemas/match_result.json.
        """
        return self.matcher.match(
            field_event=field_event,
            schedule_activities=schedule_activities,
            match_id=match_id,
            visual_evidence_score=visual_evidence_score,
            top_k=top_k,
        )

    def run(
        self,
        raw_text: str,
        schedule_activities: List[Dict[str, Any]],
        event_id: Optional[str] = None,
        project_id: str = "PRJ-DEMO-01",
        source_ref: str = "daily_report",
        evidence_refs: Optional[List[str]] = None,
        visual_evidence_score: Optional[float] = None,
        top_k: int = 5,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Executes full Person 3 pipeline: extraction + matching.

        Args:
            raw_text: Free-text field report.
            schedule_activities: List of schedule activity records.
            event_id: Optional event ID.
            project_id: Project ID.
            source_ref: Source reference.
            evidence_refs: Optional evidence IDs.
            visual_evidence_score: Optional CV score.
            top_k: Number of candidates to rank.

        Returns:
            Tuple of (field_event_dict, match_result_dict).
        """
        field_event = self.extract(
            raw_text=raw_text,
            event_id=event_id,
            project_id=project_id,
            source_ref=source_ref,
            evidence_refs=evidence_refs,
        )

        match_result = self.match(
            field_event=field_event,
            schedule_activities=schedule_activities,
            visual_evidence_score=visual_evidence_score,
            top_k=top_k,
        )

        return field_event, match_result


def get_demo_schedule_activities() -> List[Dict[str, Any]]:
    """Returns the benchmark demo schedule activities corresponding to Case A, B, and C."""
    return [
        {
            "activity_id": "PIP-1024",
            "project_id": "PRJ-DEMO-01",
            "wbs": {"code": "1.1.4", "level": "L5"},
            "activity_name": "Erect Line 24-XX",
            "discipline": "Piping",
            "location": "Unit 3",
            "planned": {"start": "2026-08-25", "finish": "2026-09-02", "progress_pct": 100.0},
            "weight": 1.0,
            "status": "in_progress",
        },
        {
            "activity_id": "PIP-1025",
            "project_id": "PRJ-DEMO-01",
            "wbs": {"code": "1.1.4.1", "level": "L5"},
            "activity_name": "Fit-up Line 24-XX",
            "discipline": "Piping",
            "location": "Unit 3",
            "planned": {"start": "2026-08-20", "finish": "2026-08-26", "progress_pct": 100.0},
            "weight": 1.0,
            "status": "completed",
        },
        {
            "activity_id": "PIP-1026",
            "project_id": "PRJ-DEMO-01",
            "wbs": {"code": "1.1.4.2", "level": "L5"},
            "activity_name": "Weld Line 24-XX",
            "discipline": "Piping",
            "location": "Unit 3",
            "planned": {"start": "2026-08-27", "finish": "2026-09-01", "progress_pct": 80.0},
            "weight": 1.0,
            "status": "in_progress",
        },
        {
            "activity_id": "PIP-1027",
            "project_id": "PRJ-DEMO-01",
            "wbs": {"code": "1.1.4.3", "level": "L5"},
            "activity_name": "Hydrotest Line 24-XX",
            "discipline": "Piping",
            "location": "Unit 3",
            "planned": {"start": "2026-09-05", "finish": "2026-09-08", "progress_pct": 0.0},
            "weight": 1.0,
            "status": "not_started",
        },
        {
            "activity_id": "PIP-1022",
            "project_id": "PRJ-DEMO-01",
            "wbs": {"code": "1.1.3", "level": "L5"},
            "activity_name": "Pipe support installation",
            "discipline": "Mechanical",
            "location": "Unit 3",
            "planned": {"start": "2026-08-15", "finish": "2026-09-10", "progress_pct": 80.0},
            "weight": 1.0,
            "status": "in_progress",
        },
    ]
