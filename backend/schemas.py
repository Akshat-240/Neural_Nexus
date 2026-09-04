from pydantic import BaseModel
from typing import Optional
from datetime import date


class ProjectCreate(BaseModel):
    name: str
    location: Optional[str] = None
    status: str = "active"


class ProjectResponse(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class ActivityCreate(BaseModel):
    project_id: int
    activity_id: str
    activity_name: str
    wbs_code: Optional[str] = None
    level: str = "L5"
    discipline: Optional[str] = None
    location: Optional[str] = None
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    planned_progress: float = 0.0
    status: str = "planned"


class ActivityResponse(BaseModel):
    id: int
    project_id: int
    activity_id: str
    activity_name: str
    wbs_code: Optional[str] = None
    level: str
    discipline: Optional[str] = None
    location: Optional[str] = None
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    planned_progress: float
    status: str

    class Config:
        from_attributes = True


# Field Update Schemas

class FieldUpdateCreate(BaseModel):
    project_id: int
    activity_id: Optional[str] = None
    report_text: str
    source: str = "text"
    status: str = "pending"


class FieldUpdateResponse(BaseModel):
    id: int
    project_id: int
    activity_id: Optional[str] = None
    report_text: str
    source: str
    status: str

    class Config:
        from_attributes = True


# Evidence Schemas

class EvidenceCreate(BaseModel):
    field_update_id: int
    evidence_type: str
    file_reference: Optional[str] = None
    description: Optional[str] = None
    confidence: float = 0.0
    verification_status: str = "pending"


class EvidenceResponse(BaseModel):
    id: int
    field_update_id: int
    evidence_type: str
    file_reference: Optional[str] = None
    description: Optional[str] = None
    confidence: float
    verification_status: str

    class Config:
        from_attributes = True

class MatchingResultCreate(BaseModel):
    field_update_id: int
    activity_id: Optional[str] = None
    activity_name: Optional[str] = None
    semantic_score: float = 0.0
    context_score: float = 0.0
    visual_score: float = 0.0
    final_confidence: float = 0.0
    match_reason: Optional[str] = None
    review_required: str = "false"


class MatchingResultResponse(BaseModel):
    id: int
    field_update_id: int
    activity_id: Optional[str] = None
    activity_name: Optional[str] = None
    semantic_score: float
    context_score: float
    visual_score: float
    final_confidence: float
    match_reason: Optional[str] = None
    review_required: str

    class Config:
        from_attributes = True

# ---------------- VERIFICATION SCHEMAS ----------------

class VerificationResultCreate(BaseModel):
    field_update_id: int
    matching_result_id: Optional[int] = None
    final_confidence: float = 0.0
    decision: str = "review"
    verified_progress: float = 0.0
    verified_status: str = "pending"
    reviewer: Optional[str] = None
    review_comment: Optional[str] = None


class VerificationResultResponse(BaseModel):
    id: int
    field_update_id: int
    matching_result_id: Optional[int] = None
    final_confidence: float
    decision: str
    verified_progress: float
    verified_status: str
    reviewer: Optional[str] = None
    review_comment: Optional[str] = None

    class Config:
        from_attributes = True

# ---------------- SCHEDULE DEVIATION SCHEMAS ----------------

class ScheduleDeviationCreate(BaseModel):
    project_id: int
    activity_id: str
    planned_progress: float = 0.0
    actual_progress: float = 0.0
    progress_variance: float = 0.0
    schedule_variance_days: int = 0
    deviation_flag: str = "on_track"
    status: str = "pending"


class ScheduleDeviationResponse(BaseModel):
    id: int
    project_id: int
    activity_id: str
    planned_progress: float
    actual_progress: float
    progress_variance: float
    schedule_variance_days: int
    deviation_flag: str
    status: str

    class Config:
        from_attributes = True        