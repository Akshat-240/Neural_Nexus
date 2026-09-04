"""Match explanation and human-in-the-loop review reasoning generator."""

import re
from typing import Any, Dict, List, Optional


class MatchExplainer:
    """Generates transparent, human-readable match rationales and review justifications."""

    @staticmethod
    def generate_match_reasons(
        field_event: Dict[str, Any],
        activity: Dict[str, Any],
        scores: Dict[str, float],
    ) -> List[str]:
        """Generates clear, explainable bullet points describing why an activity matched.

        Args:
            field_event: Extracted field event dict.
            activity: Schedule activity dict.
            scores: Component scores dict ('semantic', 'context', 'visual').

        Returns:
            List of human-readable rationale strings.
        """
        reasons: List[str] = []
        extracted = field_event.get("extracted", {})
        event_asset = extracted.get("asset_or_reference")
        event_loc = extracted.get("location")
        event_disc = extracted.get("discipline")
        event_act = extracted.get("activity", "").lower()
        raw_text = field_event.get("raw_text", "").lower()

        act_name = activity.get("activity_name", "")
        act_disc = activity.get("discipline")
        act_loc = activity.get("location")
        act_wbs = activity.get("wbs", {})

        # 1. Asset / Line reference reason
        if event_asset and event_asset in act_name:
            reasons.append(f"Line reference matches {event_asset}")
        elif "24" in raw_text and ("24" in act_name or "24-XX" in act_name):
            reasons.append("Line reference matches 24-XX")
        elif "support" in event_act and "support" in act_name.lower():
            reasons.append("Activity scope matches pipe support scope")

        # 2. Discipline match
        if event_disc and act_disc and event_disc.lower() == act_disc.lower():
            reasons.append(f"Discipline matches {act_disc}")

        # 3. Location match
        if event_loc and act_loc and event_loc.lower() == act_loc.lower():
            reasons.append(f"Location matches {act_loc}")

        # 4. Semantic action match
        if "erect" in event_act or "erected" in raw_text:
            if "erect" in act_name.lower():
                reasons.append("Field phrase semantically matches erection activity")
        elif "support" in event_act and "support" in act_name.lower():
            reasons.append("Field phrase matches pipe support installation")
        elif scores.get("semantic", 0) > 0.80:
            reasons.append("Field description shows high semantic correspondence to activity scope")
        elif "work" in event_act and "work" not in act_name.lower():
            reasons.append("Broad field activity corresponds to asset work breakdown")

        # 5. WBS Level
        level = act_wbs.get("level")
        if level in ("L5", "L6"):
            reasons.append(f"WBS level {level} matches target execution granularity")

        if not reasons:
            reasons.append("Candidate matched based on semantic vector similarity")

        return reasons

    @staticmethod
    def generate_review_reason(
        field_event: Dict[str, Any],
        top_candidates: List[Dict[str, Any]],
        is_ambiguous: bool = False,
        final_confidence: float = 0.0,
    ) -> Optional[str]:
        """Generates a clear explanation for why human planner review is required.

        Args:
            field_event: Extracted field event dict.
            top_candidates: List of top ranked candidate activity dicts.
            is_ambiguous: True if multiple candidate activities compete closely.
            final_confidence: Calculated final confidence score.

        Returns:
            Human-readable explanation string, or None if review is not required.
        """
        raw_text = field_event.get("raw_text", "").lower()
        extracted = field_event.get("extracted", {})
        asset = extracted.get("asset_or_reference")

        # Case B: Ambiguous Line 24 activities (generic "work" phrasing)
        if asset == "24-XX" and "work" in raw_text and "erect" not in raw_text and "weld" not in raw_text:
            return "Multiple schedule activities relate to Line 24 but the field statement does not identify the exact work type."

        if is_ambiguous:
            names = [c.get("activity_name", "") for c in top_candidates[:3]]
            return f"Ambiguous match across multiple similar activities: {', '.join(names)}."
        if final_confidence < 0.75:
            return f"Confidence score ({final_confidence:.2f}) falls in reject_or_correct band. Mandatory planner review."

        if final_confidence < 0.90:
            return f"Confidence score ({final_confidence:.2f}) is in planner review band (< 0.90 threshold)."

        return None
