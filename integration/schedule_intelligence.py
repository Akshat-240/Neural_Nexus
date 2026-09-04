def calculate_deviation(planned_progress: float, actual_progress: float) -> dict:
    """
    Calculates the variance between planned and actual progress and sets a deviation flag.
    """
    variance = actual_progress - planned_progress
    deviation_flag = variance < -10.0  # Flag if we are more than 10% behind
    
    return {
        "planned_progress_pct": planned_progress,
        "actual_progress_pct": actual_progress,
        "variance_pct": variance,
        "deviation_flag": deviation_flag
    }
