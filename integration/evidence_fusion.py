def fuse_evidence(semantic_score: float, context_score: float, visual_score: float) -> float:
    """
    Fuses Semantic (AI), Context (AI), and Visual (CV) scores into a final confidence score.
    Weights: 
    - Semantic: 40%
    - Context: 30%
    - Visual: 30%
    """
    # If there is no visual score provided, distribute weight to semantic and context
    if visual_score is None or visual_score < 0:
        return (semantic_score * 0.6) + (context_score * 0.4)

    final_score = (semantic_score * 0.4) + (context_score * 0.3) + (visual_score * 0.3)
    return round(final_score, 2)
