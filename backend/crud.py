from sqlalchemy.orm import Session

from models import (
    Project,
    Activity,
    FieldUpdate,
    Evidence,
    MatchingResult,
    VerificationResult,
    ScheduleDeviation
)

from schemas import (
    ProjectCreate,
    ActivityCreate,
    FieldUpdateCreate,
    EvidenceCreate,
    MatchingResultCreate,
    VerificationResultCreate,
    ScheduleDeviationCreate
)


def create_project(db: Session, project: ProjectCreate):
    db_project = Project(
        name=project.name,
        location=project.location,
        status=project.status
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


def get_projects(db: Session):
    return db.query(Project).all()


def create_activity(db: Session, activity: ActivityCreate):
    db_activity = Activity(
        project_id=activity.project_id,
        activity_id=activity.activity_id,
        activity_name=activity.activity_name,
        wbs_code=activity.wbs_code,
        level=activity.level,
        discipline=activity.discipline,
        location=activity.location,
        planned_start=activity.planned_start,
        planned_finish=activity.planned_finish,
        planned_progress=activity.planned_progress,
        status=activity.status
    )

    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)

    return db_activity


def get_activities(db: Session):
    return db.query(Activity).all()


def create_field_update(db: Session, field_update: FieldUpdateCreate):
    db_field_update = FieldUpdate(
        project_id=field_update.project_id,
        activity_id=field_update.activity_id,
        report_text=field_update.report_text,
        source=field_update.source,
        status=field_update.status
    )

    db.add(db_field_update)
    db.commit()
    db.refresh(db_field_update)

    return db_field_update


def get_field_updates(db: Session):
    return db.query(FieldUpdate).all()


def create_evidence(db: Session, evidence: EvidenceCreate):
    db_evidence = Evidence(
        field_update_id=evidence.field_update_id,
        evidence_type=evidence.evidence_type,
        file_reference=evidence.file_reference,
        description=evidence.description,
        confidence=evidence.confidence,
        verification_status=evidence.verification_status
    )

    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)

    return db_evidence


def get_evidence(db: Session):
    return db.query(Evidence).all()


# ---------------- MATCHING RESULT ----------------

def create_matching_result(
    db: Session,
    matching_result: MatchingResultCreate
):
    db_matching_result = MatchingResult(
        field_update_id=matching_result.field_update_id,
        activity_id=matching_result.activity_id,
        activity_name=matching_result.activity_name,
        semantic_score=matching_result.semantic_score,
        context_score=matching_result.context_score,
        visual_score=matching_result.visual_score,
        final_confidence=matching_result.final_confidence,
        match_reason=matching_result.match_reason,
        review_required=matching_result.review_required
    )

    db.add(db_matching_result)
    db.commit()
    db.refresh(db_matching_result)

    return db_matching_result


def get_matching_results(db: Session):
    return db.query(MatchingResult).all()

# ---------------- VERIFICATION RESULT ----------------

def create_verification_result(
    db: Session,
    verification: VerificationResultCreate
):
    db_verification = VerificationResult(
        field_update_id=verification.field_update_id,
        matching_result_id=verification.matching_result_id,
        final_confidence=verification.final_confidence,
        decision=verification.decision,
        verified_progress=verification.verified_progress,
        verified_status=verification.verified_status,
        reviewer=verification.reviewer,
        review_comment=verification.review_comment
    )

    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)

    return db_verification


def get_verification_results(db: Session):
    return db.query(VerificationResult).all()

# ---------------- SCHEDULE DEVIATION ----------------

def create_schedule_deviation(
    db: Session,
    schedule: ScheduleDeviationCreate
):
    db_schedule = ScheduleDeviation(
        project_id=schedule.project_id,
        activity_id=schedule.activity_id,
        planned_progress=schedule.planned_progress,
        actual_progress=schedule.actual_progress,
        progress_variance=schedule.progress_variance,
        schedule_variance_days=schedule.schedule_variance_days,
        deviation_flag=schedule.deviation_flag,
        status=schedule.status
    )

    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)

    return db_schedule


def get_schedule_deviations(db: Session):
    return db.query(ScheduleDeviation).all()