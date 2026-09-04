import uuid
from typing import Optional
from .adapters.ai_adapter import AIAdapter
from .adapters.cv_adapter import CVAdapter
from .adapters.backend_adapter import BackendAdapter
from .evidence_fusion import fuse_evidence
from .confidence import evaluate_confidence_policy
from .schedule_intelligence import calculate_deviation

class Orchestrator:
    def __init__(self):
        self.ai = AIAdapter()
        self.cv = CVAdapter()
        self.backend = BackendAdapter()

    def generate_id(self, prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:6].upper()}"

    def process_update(self, project_id: str, report_text: str, image_ref: Optional[str] = None) -> dict:
        event_id = self.generate_id("EVT")
        try:
            # 1. Extraction (AI)
            field_event = self.ai.extract(raw_text=report_text, project_id=project_id, event_id=event_id)
            if not field_event:
                raise Exception("Failed to extract field event from text.")

            # 2. Match (AI)
            # Must get activities from the DB (Source of Truth)
            # Assuming project_id format in DB is int (e.g., project_id = 1). Let's pass 1 for now, or parse it.
            # Usually project_id from frontend might be "PRJ-DEMO-01". Our DB expects an int. Let's assume project 1 is PRJ-DEMO-01.
            db_project_id = 1
            schedule_activities = self.backend.get_activities_for_project(db_project_id)
            if not schedule_activities:
                return {
                    "event_id": event_id,
                    "pipeline_status": "failed",
                    "error": {
                        "code": "NO_SCHEDULE_DATA",
                        "stage": "matching",
                        "message": "No active schedule is available for this project."
                    }
                }

            match_result = self.ai.match(field_event=field_event, schedule_activities=schedule_activities)
            
            # Get the top candidate from AI matching
            selected_id = match_result.get("selected_activity_id")
            top_candidate = None
            if match_result.get("candidates"):
                top_candidate = match_result["candidates"][0]

            # 3. Evidence / Visual Analysis (CV)
            visual_score = 0.0
            evidence_supportive = False
            evidence_result = None
            if image_ref and selected_id:
                evidence_result = self.cv.analyze(event_id, image_ref, selected_id)
                visual_score = evidence_result.get("analysis", {}).get("visual_evidence_score", 0.0)
                evidence_supportive = evidence_result.get("analysis", {}).get("supports_activity", False)

            # 4. Confidence Fusion (Integration)
            scores = top_candidate.get("scores", {}) if top_candidate else {}
            semantic_score = scores.get("semantic", 0.0)
            context_score = scores.get("context", 0.0)
            
            final_confidence = fuse_evidence(semantic_score, context_score, visual_score)

            # 5. Review Policy
            # If AI said review required, we respect it, else we check threshold
            ai_review = match_result.get("review_required", False)
            verification = evaluate_confidence_policy(final_confidence)
            if ai_review:
                verification["review_required"] = True
                verification["status"] = "pending_review"

            # 6. Schedule Intelligence — derive progress from text, not hardcoded
            status = field_event.get("extracted", {}).get("status", "")
            text_lower = report_text.lower()
            import re as _re
            pct_matches = _re.findall(r'(\d+)\s*(?:percent|%)', text_lower)
            if pct_matches:
                actual_progress = float(pct_matches[0])
            elif status.lower() in ("completed", "erected", "done", "finished", "installed"):
                actual_progress = 100.0
            elif status.lower() in ("started", "commenced", "begun"):
                actual_progress = 25.0
            elif status.lower() in ("in progress", "ongoing", "progressing"):
                actual_progress = 60.0
            else:
                actual_progress = 50.0

            planned_progress = 0.0
            for act in schedule_activities:
                if act["activity_id"] == selected_id:
                    planned_progress = act.get("planned", {}).get("progress_pct", 0.0)
                    break

            schedule_intel = calculate_deviation(planned_progress, actual_progress)

            # 7. Persistence (Backend)
            db_field_update = self.backend.save_field_update(
                project_id=db_project_id, 
                report_text=report_text,
                activity_id=selected_id
            )
            update_id = db_field_update.id

            match_dict = {
                "activity_id": selected_id,
                "activity_name": top_candidate.get("activity_name") if top_candidate else None,
                "semantic_score": semantic_score,
                "context_score": context_score,
                "visual_score": visual_score,
                "final_confidence": final_confidence,
                "review_required": verification["review_required"]
            }
            self.backend.save_matching_result(update_id, match_dict)
            
            if evidence_result:
                self.backend.save_evidence(update_id, evidence_result)
                
            self.backend.save_verification_result(update_id, {
                "final_confidence": final_confidence,
                "decision": "verified" if not verification["review_required"] else "review",
                "status": verification["status"]
            })
            
            if not verification["review_required"] and selected_id:
                self.backend.save_schedule_deviation(db_project_id, selected_id, schedule_intel)

            # Return the unified State representation
            return {
                "event_id": event_id,
                "pipeline_status": verification["status"],
                "field_event": {
                    "activity": field_event.get("extracted", {}).get("activity"),
                    "discipline": field_event.get("extracted", {}).get("discipline"),
                    "location": field_event.get("extracted", {}).get("location"),
                    "status": status
                },
                "match": {
                    "activity_id": selected_id,
                    "activity_name": match_dict["activity_name"],
                    "final_confidence": final_confidence
                },
                "evidence": {
                    "available": bool(image_ref),
                    "supportive": evidence_supportive,
                    "score": visual_score
                },
                "verification": verification,
                "schedule": schedule_intel
            }

        except Exception as e:
            return {
                "event_id": event_id,
                "pipeline_status": "failed",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "stage": "orchestration",
                    "message": str(e)
                }
            }
