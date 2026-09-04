from ai.pipeline import Person3Pipeline
from typing import Dict, Any, List

class AIAdapter:
    def __init__(self):
        # Using default deterministic/offline mode for the hackathon
        self.pipeline = Person3Pipeline(prefer_offline=True)

    def extract(self, raw_text: str, project_id: str, event_id: str = None) -> Dict[str, Any]:
        """Extracts field event from unstructured text."""
        return self.pipeline.extract(
            raw_text=raw_text,
            project_id=project_id,
            event_id=event_id
        )

    def match(self, field_event: Dict[str, Any], schedule_activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Matches a field event to a candidate schedule activity."""
        # Note: Person 3 pipeline matcher handles semantic + context score
        return self.pipeline.match(
            field_event=field_event,
            schedule_activities=schedule_activities
        )
