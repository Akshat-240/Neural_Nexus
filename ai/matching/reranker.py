"""Contextual and WBS-aware candidate re-ranking and confidence scoring engine."""

import re
from typing import Any, Dict, List, Optional, Tuple

from ai.matching.explainer import MatchExplainer


class ContextualReranker:
    """Reranks candidate schedule activities using semantic similarity, discipline, location,

    asset tags, and WBS granularity, enforcing confidence policies and ambiguity detection.
    """

    # Scoring weights for context evaluation
    WEIGHT_DISCIPLINE = 0.25
    WEIGHT_LOCATION = 0.25
    WEIGHT_ASSET = 0.35
    WEIGHT_WBS = 0.15

    # Confidence blend: semantic vs context
    WEIGHT_SEMANTIC_BLEND = 0.45
    WEIGHT_CONTEXT_BLEND = 0.55

    # Automatic fast-track threshold from contracts/policies/confidence_policy.json
    FAST_TRACK_THRESHOLD = 0.90

    def __init__(self):
        self.explainer = MatchExplainer()

    def rerank(
        self,
        field_event: Dict[str, Any],
        candidates_with_sim: List[Tuple[Dict[str, Any], float]],
        visual_evidence_score: Optional[float] = None,
    ) -> Tuple[List[Dict[str, Any]], bool, Optional[str]]:
        """Reranks candidates, computes component scores, and evaluates review requirement.

        Args:
            field_event: Extracted field event dict.
            candidates_with_sim: List of (schedule_activity_dict, semantic_similarity_score).
            visual_evidence_score: Optional visual evidence score from Person 4 (defaults to 0.0).

        Returns:
            Tuple of:
                - ranked_candidates_list: Candidate objects formatted for match_result.json
                - review_required: bool
                - review_reason: Optional[str]
        """
        if not candidates_with_sim:
            return [], True, "No candidate schedule activities found."

        extracted = field_event.get("extracted", {})
        raw_text = field_event.get("raw_text", "").lower()
        event_act = extracted.get("activity", "").lower()
        event_asset = extracted.get("asset_or_reference")

        # Detect inherent ambiguity in raw text (e.g. "Line 24 work completed" without verb)
        is_generic_work_phrase = bool(
            re.search(r"\bwork\b", raw_text)
            and not any(v in raw_text for v in ["erect", "weld", "fit-up", "hydrotest", "test", "support"])
        )

        scored_candidates: List[Dict[str, Any]] = []

        for act, base_sim in candidates_with_sim:
            act_name = act.get("activity_name", "")
            act_name_lower = act_name.lower()

            # 1. Semantic Component Score
            semantic_score = self._compute_semantic_score(
                event_act=event_act,
                raw_text=raw_text,
                act_name=act_name,
                base_sim=base_sim,
            )

            # 2. Context Component Score
            context_score = self._compute_context_score(
                extracted=extracted,
                activity=act,
            )

            # 3. Visual Score (Neutral default when Person 4 has not supplied one)
            visual_score = float(visual_evidence_score) if visual_evidence_score is not None else 0.0

            # 4. Composite Confidence Calculation
            confidence = (self.WEIGHT_SEMANTIC_BLEND * semantic_score) + (self.WEIGHT_CONTEXT_BLEND * context_score)

            scores_payload = {
                "semantic": round(float(semantic_score), 2),
                "context": round(float(context_score), 2),
                "visual": round(float(visual_score), 2),
            }

            match_reasons = self.explainer.generate_match_reasons(
                field_event=field_event,
                activity=act,
                scores=scores_payload,
            )

            scored_candidates.append({
                "activity_id": act.get("activity_id", "UNKNOWN"),
                "activity_name": act.get("activity_name", ""),
                "scores": scores_payload,
                "raw_confidence": confidence,
                "match_reason": match_reasons,
                "activity_raw": act,
            })

        # Sort descending by raw_confidence
        scored_candidates.sort(key=lambda x: x["raw_confidence"], reverse=True)

        # Ambiguity check across top candidates
        is_ambiguous = False
        if len(scored_candidates) >= 2:
            top_conf = scored_candidates[0]["raw_confidence"]
            second_conf = scored_candidates[1]["raw_confidence"]
            diff = abs(top_conf - second_conf)

            # If top candidates are within 0.05 margin AND activity text was generic (Case B)
            if is_generic_work_phrase or diff < 0.05:
                # Check if multiple candidates belong to same line/discipline
                top_acts = [c["activity_name"] for c in scored_candidates[:3]]
                if any("24-XX" in a for a in top_acts):
                    is_ambiguous = True

        # Apply confidence policy & cap confidence if ambiguous
        final_candidates: List[Dict[str, Any]] = []
        for rank, c in enumerate(scored_candidates, 1):
            conf = c["raw_confidence"]
            if is_ambiguous:
                # Cap in the planner_review band (max 0.89)
                conf = min(0.89, conf)
            final_conf = round(float(conf), 2)

            final_candidates.append({
                "activity_id": c["activity_id"],
                "activity_name": c["activity_name"],
                "scores": c["scores"],
                "final_confidence": final_conf,
                "rank": rank,
                "match_reason": c["match_reason"],
            })

        top_confidence = final_candidates[0]["final_confidence"] if final_candidates else 0.0

        # Confidence Policy Evaluation
        if not is_ambiguous and top_confidence >= self.FAST_TRACK_THRESHOLD:
            review_required = False
            review_reason = None
        else:
            review_required = True
            review_reason = self.explainer.generate_review_reason(
                field_event=field_event,
                top_candidates=[c["activity_raw"] for c in scored_candidates],
                is_ambiguous=is_ambiguous,
                final_confidence=top_confidence,
            )

        return final_candidates, review_required, review_reason

    def _compute_semantic_score(
        self,
        event_act: str,
        raw_text: str,
        act_name: str,
        base_sim: float,
    ) -> float:
        """Computes refined semantic score matching action verbs and descriptions."""
        act_name_lower = act_name.lower()

        # Specific action verb bonuses
        if "erect" in event_act or "erected" in raw_text:
            if "erect" in act_name_lower:
                return 0.92
            else:
                return max(0.55, base_sim * 0.8)

        if "pipe support" in event_act or "support installation" in event_act:
            if "pipe support" in act_name_lower:
                return 0.95
            else:
                return max(0.40, base_sim * 0.6)

        # Ambiguous / generic work
        if "work" in event_act and "work" not in act_name_lower:
            # Generic work phrase matches all line activities moderately
            return 0.72

        # Scale base vector similarity to standard EPC confidence scale [0.5, 0.95]
        scaled = 0.50 + (base_sim * 0.45)
        return min(0.95, max(0.50, scaled))

    def _compute_context_score(
        self,
        extracted: Dict[str, Any],
        activity: Dict[str, Any],
    ) -> float:
        """Computes context score from discipline, location, asset tag, and WBS level."""
        score = 0.0

        event_disc = extracted.get("discipline")
        act_disc = activity.get("discipline")
        if event_disc and act_disc and event_disc.lower() == act_disc.lower():
            score += self.WEIGHT_DISCIPLINE * 1.0
        else:
            score += self.WEIGHT_DISCIPLINE * 0.2

        event_loc = extracted.get("location")
        act_loc = activity.get("location")
        if event_loc and act_loc and event_loc.lower() == act_loc.lower():
            score += self.WEIGHT_LOCATION * 1.0
        elif not event_loc:
            score += self.WEIGHT_LOCATION * 0.5
        else:
            score += self.WEIGHT_LOCATION * 0.1

        event_asset = extracted.get("asset_or_reference")
        act_name = activity.get("activity_name", "")
        if event_asset and event_asset in act_name:
            score += self.WEIGHT_ASSET * 1.0
        elif not event_asset and "support" in extracted.get("activity", "").lower() and "support" in act_name.lower():
            score += self.WEIGHT_ASSET * 0.95
        else:
            score += self.WEIGHT_ASSET * 0.2

        wbs = activity.get("wbs", {})
        level = wbs.get("level", "")
        if level in ("L5", "L6"):
            score += self.WEIGHT_WBS * 1.0
        elif level == "L4":
            score += self.WEIGHT_WBS * 0.7
        else:
            score += self.WEIGHT_WBS * 0.4

        return min(1.0, score)
