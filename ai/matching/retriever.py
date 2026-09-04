"""L5/L6 candidate retrieval across schedule activities using semantic embeddings."""

from typing import Any, Dict, List, Optional, Tuple

from ai.matching.embedder import SemanticEmbedder


class L5L6Retriever:
    """Indexes L5/L6 schedule activities and retrieves top-k candidates for a field event."""

    def __init__(self, embedder: Optional[SemanticEmbedder] = None):
        """Initializes retriever with a semantic embedder.

        Args:
            embedder: SemanticEmbedder instance (default offline instance created if None).
        """
        self.embedder = embedder or SemanticEmbedder(prefer_offline=True)

    @staticmethod
    def build_activity_search_text(act: Dict[str, Any]) -> str:
        """Constructs a composite search string from schedule activity fields.

        Args:
            act: Schedule activity dictionary conforming to schedule_activity.json.

        Returns:
            Formatted text string.
        """
        name = act.get("activity_name", "")
        discipline = act.get("discipline", "")
        location = act.get("location", "")
        wbs = act.get("wbs", {})
        wbs_str = f"{wbs.get('code', '')} {wbs.get('level', '')}"
        return f"{name} {discipline} {location} {wbs_str}".strip()

    @staticmethod
    def build_event_query_text(field_event: Dict[str, Any]) -> str:
        """Constructs a composite query string from extracted field event details.

        Args:
            field_event: Field event dict conforming to field_event.json.

        Returns:
            Formatted query string.
        """
        extracted = field_event.get("extracted", {})
        activity = extracted.get("activity", "")
        context = extracted.get("context", "")
        discipline = extracted.get("discipline", "")
        location = extracted.get("location", "")
        asset = extracted.get("asset_or_reference", "")
        raw = field_event.get("raw_text", "")

        return f"{activity} {context} {discipline} {location} {asset} {raw}".strip()

    def retrieve(
        self,
        field_event: Dict[str, Any],
        schedule_activities: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Retrieves top-k candidate activities ranked by semantic similarity.

        Args:
            field_event: Extracted field event dict.
            schedule_activities: List of schedule activity dicts.
            top_k: Number of candidate activities to return.

        Returns:
            List of tuples: (schedule_activity_dict, semantic_similarity_score)
        """
        if not schedule_activities:
            return []

        query_text = self.build_event_query_text(field_event)
        query_vec = self.embedder.embed_text(query_text)

        candidates_with_scores: List[Tuple[Dict[str, Any], float]] = []

        for act in schedule_activities:
            act_text = self.build_activity_search_text(act)
            act_vec = self.embedder.embed_text(act_text)
            sim = self.embedder.compute_cosine_similarity(query_vec, act_vec)
            candidates_with_scores.append((act, float(sim)))

        # Sort descending by similarity score
        candidates_with_scores.sort(key=lambda x: x[1], reverse=True)

        return candidates_with_scores[:top_k]
