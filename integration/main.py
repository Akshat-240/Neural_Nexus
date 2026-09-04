"""
Fully wired integration/main.py
All endpoints return live DB data. No hardcoded arrays.
"""
from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os, shutil, datetime
from .orchestrator import Orchestrator
from .adapters.voice_adapter import VoiceAdapter

app = FastAPI(title="Neural Nexus - Integration API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded images so the frontend can display them
os.makedirs("temp_uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="temp_uploads"), name="uploads")

orchestrator = Orchestrator()
voice_adapter = VoiceAdapter()


# ─────────────────────────────────────────────
# Helper: DB session shortcut
# ─────────────────────────────────────────────
def _db():
    return orchestrator.backend.get_session()


# ─────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Neural Nexus Integration API is running."}


# ─────────────────────────────────────────────
# Process update  (text + optional image)
# ─────────────────────────────────────────────
@app.post("/api/v1/process-update")
async def process_update(
    project_id: str = Form(...),
    report_text: str = Form(...),
    image: Optional[UploadFile] = File(None),
):
    try:
        image_path = None
        if image and image.filename:
            safe_name = f"{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{image.filename}"
            image_path = os.path.abspath(f"temp_uploads/{safe_name}")
            with open(image_path, "wb") as buf:
                shutil.copyfileobj(image.file, buf)

        result = orchestrator.process_update(
            project_id=project_id,
            report_text=report_text,
            image_ref=image_path,
        )
        # Expose image URL so frontend can render it
        if image_path:
            fname = os.path.basename(image_path)
            result["image_url"] = f"/uploads/{fname}"
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# Voice transcribe → same pipeline
# ─────────────────────────────────────────────
class VoiceTranscribeRequest(BaseModel):
    project_id: str
    audio_ref: str
    image_ref: Optional[str] = None

@app.post("/api/v1/voice/transcribe")
def voice_transcribe(req: VoiceTranscribeRequest):
    voice_res = voice_adapter.transcribe_and_extract(req.audio_ref, req.project_id)
    transcript = voice_res.get("transcript", "")
    return orchestrator.process_update(
        project_id=req.project_id,
        report_text=transcript,
        image_ref=req.image_ref,
    )


# ─────────────────────────────────────────────
# Activities  (Schedule page)
# ─────────────────────────────────────────────
@app.get("/api/v1/activities")
def get_all_activities():
    from backend import models
    db = _db()
    try:
        acts = db.query(models.Activity).all()
        result = []
        for a in acts:
            devs = db.query(models.ScheduleDeviation).filter(
                models.ScheduleDeviation.activity_id == a.activity_id
            ).all()
            actual = max((d.actual_progress for d in devs), default=0.0)
            variance = round(actual - a.planned_progress, 1)
            result.append({
                "activity_id":    a.activity_id,
                "activity_name":  a.activity_name,
                "discipline":     a.discipline or "",
                "location":       a.location or "",
                "planned_progress": a.planned_progress,
                "actual_progress":  actual,
                "variance_pct":   variance,
                "deviation_flag": variance < -5,
                "status": (
                    "completed" if actual >= 100
                    else "in_progress" if actual > 0
                    else "planned"
                ),
            })
        return result
    finally:
        db.close()


# ─────────────────────────────────────────────
# Field Events  (event history)
# ─────────────────────────────────────────────
@app.get("/api/v1/events")
def get_events():
    from backend import models
    db = _db()
    try:
        updates = db.query(models.FieldUpdate).order_by(models.FieldUpdate.id.desc()).all()
        result = []
        for u in updates:
            # Matching
            mr = db.query(models.MatchingResult).filter(
                models.MatchingResult.field_update_id == u.id
            ).first()
            # Verification
            vr = db.query(models.VerificationResult).filter(
                models.VerificationResult.field_update_id == u.id
            ).first()
            result.append({
                "event_id":      f"EVT-{u.id:04d}",
                "db_id":         u.id,
                "report_text":   u.report_text,
                "activity_id":   mr.activity_id if mr else None,
                "activity_name": mr.activity_name if mr else None,
                "confidence":    mr.final_confidence if mr else None,
                "review_required": (mr.review_required == "true") if mr else False,
                "pipeline_status": vr.verified_status if vr else "unknown",
                "decision":      vr.decision if vr else None,
                "source":        u.source,
            })
        return result
    finally:
        db.close()


@app.get("/api/v1/events/{db_id}")
def get_event_detail(db_id: int):
    from backend import models
    db = _db()
    try:
        u = db.query(models.FieldUpdate).filter(models.FieldUpdate.id == db_id).first()
        if not u:
            raise HTTPException(status_code=404, detail="Event not found")
        mr = db.query(models.MatchingResult).filter(
            models.MatchingResult.field_update_id == u.id
        ).first()
        vr = db.query(models.VerificationResult).filter(
            models.VerificationResult.field_update_id == u.id
        ).first()
        ev = db.query(models.Evidence).filter(
            models.Evidence.field_update_id == u.id
        ).first()
        # Schedule deviation
        sd = None
        if mr and mr.activity_id:
            sd = db.query(models.ScheduleDeviation).filter(
                models.ScheduleDeviation.activity_id == mr.activity_id
            ).order_by(models.ScheduleDeviation.id.desc()).first()
        return {
            "event_id":        f"EVT-{u.id:04d}",
            "db_id":           u.id,
            "report_text":     u.report_text,
            "source":          u.source,
            "match": {
                "activity_id":   mr.activity_id if mr else None,
                "activity_name": mr.activity_name if mr else None,
                "semantic_score": mr.semantic_score if mr else 0,
                "context_score":  mr.context_score if mr else 0,
                "visual_score":   mr.visual_score if mr else 0,
                "final_confidence": mr.final_confidence if mr else 0,
                "review_required": (mr.review_required == "true") if mr else False,
            } if mr else None,
            "evidence": {
                "evidence_id":   f"EVD-{ev.id:04d}",
                "file_reference": ev.file_reference,
                "image_url": f"/uploads/{os.path.basename(ev.file_reference)}" if ev and ev.file_reference else None,
                "confidence":    ev.confidence,
                "status":        ev.verification_status,
            } if ev else None,
            "verification": {
                "final_confidence": vr.final_confidence if vr else 0,
                "decision":        vr.decision if vr else None,
                "status":          vr.verified_status if vr else None,
            } if vr else None,
            "schedule": {
                "planned_progress": sd.planned_progress if sd else None,
                "actual_progress":  sd.actual_progress if sd else None,
                "variance_pct":     sd.progress_variance if sd else None,
                "deviation_flag":   sd.deviation_flag if sd else None,
            } if sd else None,
        }
    finally:
        db.close()


# ─────────────────────────────────────────────
# Reviews
# ─────────────────────────────────────────────
@app.get("/api/v1/reviews")
def get_reviews():
    from backend import models
    db = _db()
    try:
        # All matching results where review_required = "true"
        mrs = db.query(models.MatchingResult).filter(
            models.MatchingResult.review_required == "true"
        ).all()
        result = []
        for mr in mrs:
            u = db.query(models.FieldUpdate).filter(
                models.FieldUpdate.id == mr.field_update_id
            ).first()
            vr = db.query(models.VerificationResult).filter(
                models.VerificationResult.field_update_id == mr.field_update_id
            ).first()
            # Only show items still pending review (not yet decided)
            if vr and vr.decision not in ("pending_review", "review", None, ""):
                continue
            result.append({
                "event_id":       f"EVT-{mr.field_update_id:04d}",
                "db_id":          mr.field_update_id,
                "report_text":    u.report_text if u else "",
                "proposed_activity_id":   mr.activity_id,
                "proposed_activity_name": mr.activity_name,
                "confidence":     mr.final_confidence,
                "reason":         "Confidence below threshold or ambiguous text match",
            })
        return result
    finally:
        db.close()


class ReviewDecisionRequest(BaseModel):
    db_id: int          # field_update id
    decision: str       # approve | correct | reject
    activity_id: Optional[str] = None  # for correct

@app.post("/api/v1/review")
def submit_review(req: ReviewDecisionRequest):
    from backend import models, crud, schemas
    db = _db()
    try:
        vr = db.query(models.VerificationResult).filter(
            models.VerificationResult.field_update_id == req.db_id
        ).first()
        mr = db.query(models.MatchingResult).filter(
            models.MatchingResult.field_update_id == req.db_id
        ).first()
        u  = db.query(models.FieldUpdate).filter(
            models.FieldUpdate.id == req.db_id
        ).first()

        if not vr or not mr or not u:
            raise HTTPException(status_code=404, detail="Event not found")

        if req.decision == "approve":
            vr.decision = "verified"
            vr.verified_status = "verified"
            # Save schedule deviation
            act_id = mr.activity_id
        elif req.decision == "correct":
            if not req.activity_id:
                raise HTTPException(status_code=400, detail="activity_id required for correct")
            # Update matching result with corrected activity
            act = db.query(models.Activity).filter(
                models.Activity.activity_id == req.activity_id
            ).first()
            mr.activity_id   = req.activity_id
            mr.activity_name = act.activity_name if act else req.activity_id
            mr.review_required = "false"
            vr.decision = "verified"
            vr.verified_status = "verified"
            act_id = req.activity_id
        elif req.decision == "reject":
            vr.decision = "rejected"
            vr.verified_status = "rejected"
            mr.review_required = "false"
            db.commit()
            return {"status": "rejected"}
        else:
            raise HTTPException(status_code=400, detail="Invalid decision")

        db.commit()

        # Save schedule deviation for the approved activity
        act_row = db.query(models.Activity).filter(
            models.Activity.activity_id == act_id
        ).first()
        planned = act_row.planned_progress if act_row else 0.0
        # Determine actual progress from report text heuristic
        text_lower = u.report_text.lower()
        if "100" in text_lower or "complet" in text_lower or "erect" in text_lower:
            actual = 100.0
        elif "50" in text_lower or "half" in text_lower:
            actual = 50.0
        else:
            actual = planned  # default: on track

        variance = actual - planned
        sd = models.ScheduleDeviation(
            project_id=u.project_id,
            activity_id=act_id,
            planned_progress=planned,
            actual_progress=actual,
            progress_variance=variance,
            deviation_flag=str(variance < -5).lower(),
            status="calculated",
        )
        db.add(sd)
        db.commit()

        return {"status": "ok", "decision": req.decision, "activity_id": act_id}
    finally:
        db.close()


# ─────────────────────────────────────────────
# Dashboard summary
# ─────────────────────────────────────────────
@app.get("/api/v1/dashboard")
def get_dashboard():
    from backend import models
    db = _db()
    try:
        acts = db.query(models.Activity).all()
        total = len(acts)

        all_devs = db.query(models.ScheduleDeviation).all()
        # Actual per activity (latest deviation record)
        actual_map = {}
        for d in all_devs:
            if d.activity_id not in actual_map or d.id > actual_map[d.activity_id][0]:
                actual_map[d.activity_id] = (d.id, d.actual_progress)

        in_progress = sum(1 for a in acts if actual_map.get(a.activity_id, (0,0))[1] > 0 and actual_map.get(a.activity_id, (0,0))[1] < 100)
        completed   = sum(1 for a in acts if actual_map.get(a.activity_id, (0,0))[1] >= 100)

        overall_pct = 0.0
        if total:
            total_actual = sum(actual_map.get(a.activity_id, (0, 0.0))[1] for a in acts)
            overall_pct = round(total_actual / total, 1)

        # Deviations
        deviation_ids = set(d.activity_id for d in all_devs if d.progress_variance < -5)
        deviations = len(deviation_ids)

        # Reviews pending
        pending_reviews = db.query(models.MatchingResult).filter(
            models.MatchingResult.review_required == "true"
        ).count()
        # subtract already decided
        decided = db.query(models.VerificationResult).filter(
            models.VerificationResult.decision.in_(["verified", "rejected"])
        ).count()
        pending_reviews = max(0, pending_reviews - decided)

        # Verified events
        verified = db.query(models.VerificationResult).filter(
            models.VerificationResult.decision == "verified"
        ).count()

        # Attention items: activities with deviations
        attention = []
        for d in all_devs:
            if d.progress_variance < -5:
                act = db.query(models.Activity).filter(
                    models.Activity.activity_id == d.activity_id
                ).first()
                attention.append({
                    "activity_id":   d.activity_id,
                    "activity_name": act.activity_name if act else d.activity_id,
                    "planned":       d.planned_progress,
                    "actual":        d.actual_progress,
                    "variance":      d.progress_variance,
                })

        # Recent verified events
        recent_vrs = db.query(models.VerificationResult).filter(
            models.VerificationResult.decision == "verified"
        ).order_by(models.VerificationResult.id.desc()).limit(5).all()
        recent = []
        for vr in recent_vrs:
            mr = db.query(models.MatchingResult).filter(
                models.MatchingResult.field_update_id == vr.field_update_id
            ).first()
            recent.append({
                "event_id":       f"EVT-{vr.field_update_id:04d}",
                "db_id":          vr.field_update_id,
                "activity_id":    mr.activity_id if mr else None,
                "activity_name":  mr.activity_name if mr else None,
                "confidence":     mr.final_confidence if mr else None,
            })

        return {
            "total_activities":  total,
            "in_progress":       in_progress,
            "completed":         completed,
            "overall_progress_pct": overall_pct,
            "pending_reviews":   pending_reviews,
            "deviations":        deviations,
            "verified_events":   verified,
            "attention_items":   attention[:5],
            "recent_verified":   recent,
        }
    finally:
        db.close()


# ─────────────────────────────────────────────
# Insights  (deviations only)
# ─────────────────────────────────────────────
@app.get("/api/v1/insights")
def get_insights():
    from backend import models
    db = _db()
    try:
        devs = db.query(models.ScheduleDeviation).filter(
            models.ScheduleDeviation.progress_variance < -5
        ).all()
        result = []
        seen = set()
        for d in devs:
            if d.activity_id in seen:
                continue
            seen.add(d.activity_id)
            act = db.query(models.Activity).filter(
                models.Activity.activity_id == d.activity_id
            ).first()
            result.append({
                "activity_id":    d.activity_id,
                "activity_name":  act.activity_name if act else d.activity_id,
                "location":       act.location if act else "",
                "planned_progress": d.planned_progress,
                "actual_progress":  d.actual_progress,
                "variance_pct":     d.progress_variance,
                "severity": "high" if d.progress_variance < -20 else "medium",
            })
        return result
    finally:
        db.close()


# ─────────────────────────────────────────────
# Evidence for a specific event
# ─────────────────────────────────────────────
@app.get("/api/v1/evidence/{db_id}")
def get_evidence(db_id: int):
    from backend import models
    db = _db()
    try:
        ev = db.query(models.Evidence).filter(
            models.Evidence.field_update_id == db_id
        ).first()
        if not ev:
            return {"available": False}
        fname = os.path.basename(ev.file_reference) if ev.file_reference else None
        return {
            "available":      True,
            "evidence_id":    f"EVD-{ev.id:04d}",
            "image_url":      f"/uploads/{fname}" if fname else None,
            "confidence":     ev.confidence,
            "visual_signal":  "supportive" if ev.confidence and ev.confidence > 0.5 else "weak",
            "status":         ev.verification_status,
        }
    finally:
        db.close()
