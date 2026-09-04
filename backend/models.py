from sqlalchemy import Column, Integer, String, Float, Date
from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    status = Column(String, default="active")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    activity_id = Column(String, unique=True, nullable=False)
    activity_name = Column(String, nullable=False)
    wbs_code = Column(String)
    level = Column(String, default="L5")
    discipline = Column(String)
    location = Column(String)
    planned_start = Column(Date)
    planned_finish = Column(Date)
    planned_progress = Column(Float, default=0.0)
    status = Column(String, default="planned")


class FieldUpdate(Base):
    __tablename__ = "field_updates"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    activity_id = Column(String, nullable=True)
    report_text = Column(String, nullable=False)
    source = Column(String, default="text")
    status = Column(String, default="pending")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    field_update_id = Column(Integer, nullable=False)
    evidence_type = Column(String, nullable=False)
    file_reference = Column(String, nullable=True)
    description = Column(String, nullable=True)
    confidence = Column(Float, default=0.0)
    verification_status = Column(String, default="pending")

class MatchingResult(Base):
    __tablename__ = "matching_results"

    id = Column(Integer, primary_key=True, index=True)
    field_update_id = Column(Integer, nullable=False)
    activity_id = Column(String, nullable=True)
    activity_name = Column(String, nullable=True)
    semantic_score = Column(Float, default=0.0)
    context_score = Column(Float, default=0.0)
    visual_score = Column(Float, default=0.0)
    final_confidence = Column(Float, default=0.0)
    match_reason = Column(String, nullable=True)
    review_required = Column(String, default="false")

class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, index=True)
    field_update_id = Column(Integer, nullable=False)
    matching_result_id = Column(Integer, nullable=True)

    final_confidence = Column(Float, default=0.0)
    decision = Column(String, default="review")

    verified_progress = Column(Float, default=0.0)
    verified_status = Column(String, default="pending")

    reviewer = Column(String, nullable=True)
    review_comment = Column(String, nullable=True)

class ScheduleDeviation(Base):
    __tablename__ = "schedule_deviations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    activity_id = Column(String, nullable=False)

    planned_progress = Column(Float, default=0.0)
    actual_progress = Column(Float, default=0.0)

    progress_variance = Column(Float, default=0.0)
    schedule_variance_days = Column(Integer, default=0)

    deviation_flag = Column(String, default="on_track")
    status = Column(String, default="pending")