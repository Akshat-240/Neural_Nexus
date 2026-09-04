from pydantic import BaseModel
from typing import Optional, Any

class PipelineState(BaseModel):
    event_id: str
    pipeline_status: str
    field_event: Optional[Any] = None
    match: Optional[Any] = None
    evidence: Optional[Any] = None
    verification: Optional[Any] = None
    schedule: Optional[Any] = None
    error: Optional[Any] = None
