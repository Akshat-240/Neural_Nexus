from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from .models import (
    Project,
    Activity,
    FieldUpdate,
    Evidence,
    MatchingResult,
    VerificationResult,
    ScheduleDeviation
)

from .schemas import (
    ProjectCreate,
    ProjectResponse,
    ActivityCreate,
    ActivityResponse,
    FieldUpdateCreate,
    FieldUpdateResponse,
    EvidenceCreate,
    EvidenceResponse,
    MatchingResultCreate,
    MatchingResultResponse,
    VerificationResultCreate,
    VerificationResultResponse,
    ScheduleDeviationCreate,
    ScheduleDeviationResponse
)

from .crud import (
    create_project,
    get_projects,
    create_activity,
    get_activities,
    create_field_update,
    get_field_updates,
    create_evidence,
    get_evidence,
    create_matching_result,
    get_matching_results,
    create_verification_result,
    get_verification_results,
    create_schedule_deviation,
    get_schedule_deviations
)


app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "SIH26122 Backend is Running!"}


@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as connection:
            return {"message": "Database connected successfully!"}
    except Exception as e:
        return {"message": "Database connection failed", "error": str(e)}


# ---------------- PROJECT APIs ----------------

@app.post("/projects", response_model=ProjectResponse)
def add_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    return create_project(db, project)


@app.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return get_projects(db)


# ---------------- ACTIVITY APIs ----------------

@app.post("/activities", response_model=ActivityResponse)
def add_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db)
):
    return create_activity(db, activity)


@app.get("/activities", response_model=list[ActivityResponse])
def list_activities(db: Session = Depends(get_db)):
    return get_activities(db)


# ---------------- FIELD UPDATE APIs ----------------

@app.post("/field-updates", response_model=FieldUpdateResponse)
def add_field_update(
    field_update: FieldUpdateCreate,
    db: Session = Depends(get_db)
):
    return create_field_update(db, field_update)


@app.get("/field-updates", response_model=list[FieldUpdateResponse])
def list_field_updates(db: Session = Depends(get_db)):
    return get_field_updates(db)


# ---------------- EVIDENCE APIs ----------------

@app.post("/evidence", response_model=EvidenceResponse)
def add_evidence(
    evidence: EvidenceCreate,
    db: Session = Depends(get_db)
):
    return create_evidence(db, evidence)


@app.get("/evidence", response_model=list[EvidenceResponse])
def list_evidence(db: Session = Depends(get_db)):
    return get_evidence(db)


# ---------------- MATCHING RESULT APIs ----------------

@app.post("/matching-results", response_model=MatchingResultResponse)
def add_matching_result(
    matching_result: MatchingResultCreate,
    db: Session = Depends(get_db)
):
    return create_matching_result(db, matching_result)


@app.get("/matching-results", response_model=list[MatchingResultResponse])
def list_matching_results(db: Session = Depends(get_db)):
    return get_matching_results(db)


# ---------------- VERIFICATION APIs ----------------

@app.post("/verification-results", response_model=VerificationResultResponse)
def add_verification_result(
    verification: VerificationResultCreate,
    db: Session = Depends(get_db)
):
    return create_verification_result(db, verification)


@app.get("/verification-results", response_model=list[VerificationResultResponse])
def list_verification_results(db: Session = Depends(get_db)):
    return get_verification_results(db)


# ---------------- SCHEDULE DEVIATION APIs ----------------

@app.post("/schedule-deviations", response_model=ScheduleDeviationResponse)
def add_schedule_deviation(
    schedule: ScheduleDeviationCreate,
    db: Session = Depends(get_db)
):
    return create_schedule_deviation(db, schedule)


@app.get("/schedule-deviations", response_model=list[ScheduleDeviationResponse])
def list_schedule_deviations(db: Session = Depends(get_db)):
    return get_schedule_deviations(db)