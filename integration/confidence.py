def evaluate_confidence_policy(final_confidence: float) -> dict:
    """
    Evaluates the final fused confidence against defined thresholds to determine
    if human review is required.
    
    Thresholds:
    - >= 0.85: Verified automatically
    - < 0.85: Review required
    """
    if final_confidence >= 0.85:
        return {
            "review_required": False,
            "status": "verified"
        }
    else:
        return {
            "review_required": True,
            "status": "pending_review"
        }
