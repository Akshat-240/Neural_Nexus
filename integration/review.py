def process_review_decision(decision: str, original_state: dict) -> dict:
    """
    Handles a human reviewer's decision on a pending verification result.
    Decision can be 'approve', 'correct', or 'reject'.
    """
    if decision == "approve":
        original_state["verification"]["status"] = "verified"
        original_state["verification"]["review_required"] = False
    elif decision == "reject":
        original_state["verification"]["status"] = "rejected"
        original_state["verification"]["review_required"] = False
    elif decision == "correct":
        original_state["verification"]["status"] = "corrected"
        original_state["verification"]["review_required"] = False
        
    original_state["pipeline_status"] = original_state["verification"]["status"]
    return original_state
