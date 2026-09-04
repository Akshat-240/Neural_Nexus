"""Schedule matcher tying together vector retrieval, contextual re-ranking, and schema generation."""

import datetime
from typing import Any, Dict, List, Optional

from ai.matching.embedder import SemanticEmbedder
from ai.matching.reranker import ContextualReranker
from ai.matching.retriever import L5L6Retriever


class ScheduleMatcher:
    """Coordinates candidate retrieval, contextual re-ranking, and builds the match_result.json contract."""

    def __init__(
        self,
        embedder: Optional[SemanticEmbedder] = None,
        retriever: Optional[L5L6Retriever] = None,
        reranker: Optional[ContextualReranker] = None,
    ):
        """Initializes matcher with components."""
        self.embedder = embedder or SemanticEmbedder(prefer_offline=True)
        self.retriever = retriever or L5L6Retriever(embedder=self.embedder)
        self.reranker = reranker or ContextualReranker()

    def match(
        self,
        field_event: Dict[str, Any],
        schedule_activities: List[Dict[str, Any]],
        match_id: Optional[str] = None,
        visual_evidence_score: Optional[float] = None,
        top_k: int = 5,
        created_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Matches a field event to schedule activities and outputs a match_result.json compliant dict.

        Args:
            field_event: Extracted field event dict adhering to field_event.json.
            schedule_activities: List of activities conforming to schedule_activity.json.
            match_id: Match identifier (auto-generated if None).
            visual_evidence_score: Optional visual evidence score from Person 4.
            top_k: Number of candidate activities to return.
            created_at: ISO timestamp for the match.

        Returns:
            Match result dict strictly conforming to contracts/schemas/match_result.json.
        """
        event_id = field_event.get("event_id", "EVT-0001")
        if match_id:
            m_id = match_id
        else:
            import hashlib

            digest = hashlib.sha1(event_id.encode("utf-8")).hexdigest()
            m_id = f"MAT-{int(digest[:8], 16) % 10000:04d}"
        timestamp = created_at or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if not schedule_activities:
            return {
                "match_id": m_id,
                "event_id": event_id,
                "candidates": [],
                "selected_activity_id": None,
                "review_required": True,
                "review_reason": "No schedule activities provided for matching.",
                "created_at": timestamp,
            }

        # 1. Retrieve candidates via vector similarity
        raw_candidates = self.retriever.retrieve(
            field_event=field_event,
            schedule_activities=schedule_activities,
            top_k=top_k,
        )

        # 2. Contextual & WBS-aware re-ranking
        ranked_candidates, review_required, review_reason = self.reranker.rerank(
            field_event=field_event,
            candidates_with_sim=raw_candidates,
            visual_evidence_score=visual_evidence_score,
        )

        selected_id = ranked_candidates[0]["activity_id"] if ranked_candidates else None

        match_result = {
            "match_id": m_id,
            "event_id": event_id,
            "candidates": ranked_candidates,
            "selected_activity_id": selected_id,
            "review_required": review_required,
            "review_reason": review_reason,
            "created_at": timestamp,
        }

        return match_result
