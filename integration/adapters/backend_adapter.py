from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend import crud, schemas, models
from typing import List, Dict, Any, Optional

# Ensure tables are created
Base.metadata.create_all(bind=engine)

class BackendAdapter:
    def __init__(self):
        pass
        
    def get_session(self) -> Session:
        return SessionLocal()
        
    def get_activities_for_project(self, project_id: int) -> List[Dict[str, Any]]:
        with self.get_session() as db:
            activities = crud.get_activities(db)
            # Filter by project_id and format to what AI expects
            filtered = [a for a in activities if a.project_id == project_id]
            
            result = []
            for a in filtered:
                # Convert DB model to dict matching schedule_activity.json / AI expectations
                result.append({
                    "activity_id": a.activity_id,
                    "project_id": str(a.project_id),
                    "wbs": {"code": a.wbs_code or "", "level": a.level},
                    "activity_name": a.activity_name,
                    "discipline": a.discipline or "",
                    "location": a.location or "",
                    "planned": {
                        "start": str(a.planned_start) if a.planned_start else None,
                        "finish": str(a.planned_finish) if a.planned_finish else None,
                        "progress_pct": float(a.planned_progress)
                    },
                    "weight": 1.0,  # default
                    "status": a.status
                })
            return result

    def get_activity(self, activity_id: str) -> Optional[models.Activity]:
        with self.get_session() as db:
            activities = crud.get_activities(db)
            for a in activities:
                if a.activity_id == activity_id:
                    return a
            return None

    def save_field_update(self, project_id: int, report_text: str, source: str = "text", activity_id: str = None) -> models.FieldUpdate:
        with self.get_session() as db:
            create_data = schemas.FieldUpdateCreate(
                project_id=project_id,
                activity_id=activity_id,
                report_text=report_text,
                source=source,
                status="processed"
            )
            return crud.create_field_update(db, create_data)

    def save_matching_result(self, field_update_id: int, match_dict: dict) -> models.MatchingResult:
        with self.get_session() as db:
            create_data = schemas.MatchingResultCreate(
                field_update_id=field_update_id,
                activity_id=match_dict.get("activity_id"),
                activity_name=match_dict.get("activity_name"),
                semantic_score=match_dict.get("semantic_score", 0.0),
                context_score=match_dict.get("context_score", 0.0),
                visual_score=match_dict.get("visual_score", 0.0),
                final_confidence=match_dict.get("final_confidence", 0.0),
                match_reason=match_dict.get("match_reason"),
                review_required=str(match_dict.get("review_required", "false")).lower()
            )
            return crud.create_matching_result(db, create_data)

    def save_evidence(self, field_update_id: int, evidence_dict: dict) -> models.Evidence:
        with self.get_session() as db:
            create_data = schemas.EvidenceCreate(
                field_update_id=field_update_id,
                evidence_type="image",
                file_reference=evidence_dict.get("source", {}).get("ref"),
                confidence=evidence_dict.get("analysis", {}).get("visual_evidence_score", 0.0),
                verification_status="processed"
            )
            return crud.create_evidence(db, create_data)

    def save_verification_result(self, field_update_id: int, verification_dict: dict) -> models.VerificationResult:
        with self.get_session() as db:
            create_data = schemas.VerificationResultCreate(
                field_update_id=field_update_id,
                final_confidence=verification_dict.get("final_confidence", 0.0),
                decision=verification_dict.get("decision", "review"),
                verified_status=verification_dict.get("status", "pending")
            )
            return crud.create_verification_result(db, create_data)

    def save_schedule_deviation(self, project_id: int, activity_id: str, deviation_dict: dict) -> models.ScheduleDeviation:
        with self.get_session() as db:
            create_data = schemas.ScheduleDeviationCreate(
                project_id=project_id,
                activity_id=activity_id,
                planned_progress=deviation_dict.get("planned_progress_pct", 0.0),
                actual_progress=deviation_dict.get("actual_progress_pct", 0.0),
                progress_variance=deviation_dict.get("variance_pct", 0.0),
                deviation_flag=str(deviation_dict.get("deviation_flag", False)).lower(),
                status="calculated"
            )
            return crud.create_schedule_deviation(db, create_data)
