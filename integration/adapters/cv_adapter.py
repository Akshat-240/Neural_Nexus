from cv.evidence import analyze_evidence
from typing import Dict, Any

class CVAdapter:
    def __init__(self):
        pass

    def analyze(self, event_id: str, image_path: str, candidate_activity_id: str) -> Dict[str, Any]:
        """Analyzes an image and returns visual evidence scores."""
        return analyze_evidence(
            event_id=event_id,
            image_path=image_path,
            candidate_activity_id=candidate_activity_id
        )
