"""
Fully wired integration/main.py — all endpoints return live DB data.
"""
from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os, shutil, datetime
from .orchestrator import Orchestrator
from .adapters.voice_adapter import VoiceAdapter

app = FastAPI(title="Neural Nexus — Integration API")

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


def _db():
    return orchestrator.backend.get_session()


# ── Health ────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Neural Nexus Integration API running."}


# ── Process update ────────────────────────────────────────────
@app.post("/api/v1/process-update")
async def process_update(
    project_id: str = Form(...),
    report_text: str = Form(...),
    image: Optional[UploadFile] = File(None),
):
    try:
        image_path = None
        if image and image.filename:
            safe = f"{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{image.filename}"
            image_path = os.path.abspath(f"temp_uploads/{safe}")
            with open(image_path, "wb") as buf:
                shutil.copyfileobj(image.file, buf)

        result = orchestrator.process_update(
            project_id=project_id,
            report_text=report_text,
            image_ref=image_path,
        )
        if image_path:
            result["image_url"] = f"/uploads/{os.path.basename(image_path)}"
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/voice/transcribe")
async def voice_transcribe(
    project_id: str = Form(...),
    audio: UploadFile = File(...)
):
    safe = f"{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{audio.filename}"
    audio_path = os.path.abspath(f"temp_uploads/{safe}")
    with open(audio_path, "wb") as buf:
        shutil.copyfileobj(audio.file, buf)

    voice_res = voice_adapter.transcribe_and_extract(audio_path, project_id)
    return {"transcript": voice_res.get("transcript", "")}

# ── Activities (Schedule) ─────────────────────────────────────
@app.get("/api/v1/activities")
def get_activities():
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
                "activity_id":      a.activity_id,
                "activity_name":    a.activity_name,
                "discipline":       a.discipline or "",
                "location":         a.location or "",
                "planned_progress": a.planned_progress,
                "actual_progress":  actual,
                "variance_pct":     variance,
                "deviation_flag":   variance < -5,
                "status": (
                    "completed"   if actual >= 100
                    else "in_progress" if actual > 0
                    else "planned" if a.planned_progress == 0
                    else "not_started"
                ),
            })
        return result
    finally:
        db.close()


# ── Events ────────────────────────────────────────────────────
@app.get("/api/v1/events")
def get_events():
    from backend import models
    db = _db()
    try:
        updates = db.query(models.FieldUpdate).order_by(models.FieldUpdate.id.desc()).all()
        result = []
        for u in updates:
            mr = db.query(models.MatchingResult).filter(
                models.MatchingResult.field_update_id == u.id
            ).first()
            vr = db.query(models.VerificationResult).filter(
                models.VerificationResult.field_update_id == u.id
            ).first()
            result.append({
                "event_id":       f"EVT-{u.id:04d}",
                "db_id":          u.id,
                "report_text":    u.report_text,
                "activity_id":    mr.activity_id if mr else None,
                "activity_name":  mr.activity_name if mr else None,
                "confidence":     mr.final_confidence if mr else None,
                "review_required":(mr.review_required == "true") if mr else False,
                "pipeline_status":vr.verified_status if vr else "unknown",
                "decision":       vr.decision if vr else None,
                "source":         u.source,
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
        mr = db.query(models.MatchingResult).filter(models.MatchingResult.field_update_id == u.id).first()
        vr = db.query(models.VerificationResult).filter(models.VerificationResult.field_update_id == u.id).first()
        ev = db.query(models.Evidence).filter(models.Evidence.field_update_id == u.id).first()
        sd = None
        if mr and mr.activity_id:
            sd = db.query(models.ScheduleDeviation).filter(
                models.ScheduleDeviation.activity_id == mr.activity_id
            ).order_by(models.ScheduleDeviation.id.desc()).first()
        return {
            "event_id":    f"EVT-{u.id:04d}",
            "db_id":       u.id,
            "report_text": u.report_text,
            "source":      u.source,
            "match": {
                "activity_id":      mr.activity_id if mr else None,
                "activity_name":    mr.activity_name if mr else None,
                "semantic_score":   mr.semantic_score if mr else 0,
                "context_score":    mr.context_score if mr else 0,
                "visual_score":     mr.visual_score if mr else 0,
                "final_confidence": mr.final_confidence if mr else 0,
                "review_required":  (mr.review_required == "true") if mr else False,
            } if mr else None,
            "evidence": {
                "available":     True,
                "evidence_id":   f"EVD-{ev.id:04d}",
                "file_reference": ev.file_reference,
                "image_url": f"/uploads/{os.path.basename(ev.file_reference)}" if ev and ev.file_reference else None,
                "confidence":    ev.confidence,
                "visual_signal": "supportive" if ev and ev.confidence and ev.confidence > 0.5 else "weak",
                "status":        ev.verification_status,
            } if ev else {"available": False},
            "verification": {
                "final_confidence": vr.final_confidence if vr else 0,
                "decision":         vr.decision if vr else None,
                "status":           vr.verified_status if vr else None,
            } if vr else None,
            "schedule": {
                "planned_progress": sd.planned_progress if sd else None,
                "actual_progress":  sd.actual_progress if sd else None,
                "variance_pct":     sd.progress_variance if sd else None,
            } if sd else None,
        }
    finally:
        db.close()


# ── Reviews ───────────────────────────────────────────────────
@app.get("/api/v1/reviews")
def get_reviews():
    from backend import models
    db = _db()
    try:
        # All matching results that flagged review AND whose verification is still pending
        mrs = db.query(models.MatchingResult).filter(
            models.MatchingResult.review_required == "true"
        ).all()
        result = []
        for mr in mrs:
            vr = db.query(models.VerificationResult).filter(
                models.VerificationResult.field_update_id == mr.field_update_id
            ).first()
            # Skip already-decided events
            if vr and vr.decision in ("verified", "rejected"):
                continue
            u = db.query(models.FieldUpdate).filter(
                models.FieldUpdate.id == mr.field_update_id
            ).first()
            result.append({
                "event_id":               f"EVT-{mr.field_update_id:04d}",
                "db_id":                  mr.field_update_id,
                "report_text":            u.report_text if u else "",
                "proposed_activity_id":   mr.activity_id,
                "proposed_activity_name": mr.activity_name,
                "confidence":             mr.final_confidence,
                "reason":                 "Confidence below verification threshold — ambiguous match",
            })
        return result
    finally:
        db.close()


class ReviewDecision(BaseModel):
    db_id: int
    decision: str           # approve | correct | reject
    activity_id: Optional[str] = None

@app.post("/api/v1/review")
def submit_review(req: ReviewDecision):
    from backend import models
    import re as _re
    db = _db()
    try:
        vr = db.query(models.VerificationResult).filter(
            models.VerificationResult.field_update_id == req.db_id
        ).first()
        mr = db.query(models.MatchingResult).filter(
            models.MatchingResult.field_update_id == req.db_id
        ).first()
        u = db.query(models.FieldUpdate).filter(
            models.FieldUpdate.id == req.db_id
        ).first()
        if not vr or not mr or not u:
            raise HTTPException(status_code=404, detail="Event not found")

        if req.decision == "reject":
            vr.decision = "rejected"
            vr.verified_status = "rejected"
            mr.review_required = "false"
            db.commit()
            return {"status": "ok", "decision": "rejected"}

        # approve or correct
        act_id = req.activity_id if (req.decision == "correct" and req.activity_id) else mr.activity_id
        act = db.query(models.Activity).filter(models.Activity.activity_id == act_id).first()
        if req.decision == "correct" and act:
            mr.activity_id   = act_id
            mr.activity_name = act.activity_name
        mr.review_required = "false"
        vr.decision         = "verified"
        vr.verified_status  = "verified"
        db.commit()

        # Derive progress from report text
        text_lower = u.report_text.lower()
        pct = _re.findall(r'(\d+)\s*(?:percent|%)', text_lower)
        if pct:
            actual = float(pct[0])
        elif any(k in text_lower for k in ("complet", "erected", "done", "finish", "install")):
            actual = 100.0
        elif any(k in text_lower for k in ("in progress", "ongoing", "progress")):
            actual = 60.0
        else:
            actual = act.planned_progress if act else 50.0

        planned = act.planned_progress if act else 0.0
        variance = actual - planned
        db.add(models.ScheduleDeviation(
            project_id=u.project_id,
            activity_id=act_id,
            planned_progress=planned,
            actual_progress=actual,
            progress_variance=variance,
            deviation_flag=str(variance < -5).lower(),
            status="calculated",
        ))
        db.commit()
        return {"status": "ok", "decision": req.decision, "activity_id": act_id}
    finally:
        db.close()


# ── Dashboard ─────────────────────────────────────────────────
@app.get("/api/v1/dashboard")
def get_dashboard():
    from backend import models
    db = _db()
    try:
        acts  = db.query(models.Activity).all()
        total = len(acts)
        devs  = db.query(models.ScheduleDeviation).all()

        # Latest actual per activity
        actual_map: dict = {}
        for d in devs:
            cur = actual_map.get(d.activity_id)
            if cur is None or d.id > cur[0]:
                actual_map[d.activity_id] = (d.id, d.actual_progress)

        in_progress = sum(1 for a in acts if 0 < actual_map.get(a.activity_id, (0, 0))[1] < 100)
        completed   = sum(1 for a in acts if actual_map.get(a.activity_id, (0, 0))[1] >= 100)
        overall_pct = round(sum(actual_map.get(a.activity_id, (0, 0.0))[1] for a in acts) / total, 1) if total else 0.0

        deviations  = len({d.activity_id for d in devs if d.progress_variance < -5})

        # Pending reviews (not yet decided)
        mrs_review = db.query(models.MatchingResult).filter(
            models.MatchingResult.review_required == "true"
        ).all()
        pending_reviews = 0
        for mr in mrs_review:
            vr = db.query(models.VerificationResult).filter(
                models.VerificationResult.field_update_id == mr.field_update_id
            ).first()
            if not vr or vr.decision not in ("verified", "rejected"):
                pending_reviews += 1

        verified = db.query(models.VerificationResult).filter(
            models.VerificationResult.decision == "verified"
        ).count()

        # Attention items
        seen_dev = set()
        attention = []
        for d in sorted(devs, key=lambda x: x.progress_variance):
            if d.activity_id in seen_dev or d.progress_variance >= -5:
                continue
            seen_dev.add(d.activity_id)
            act = next((a for a in acts if a.activity_id == d.activity_id), None)
            attention.append({
                "activity_id":   d.activity_id,
                "activity_name": act.activity_name if act else d.activity_id,
                "planned":       d.planned_progress,
                "actual":        d.actual_progress,
                "variance":      round(d.progress_variance, 1),
            })

        # Recent verified
        recent_vrs = db.query(models.VerificationResult).filter(
            models.VerificationResult.decision == "verified"
        ).order_by(models.VerificationResult.id.desc()).limit(5).all()
        recent = []
        for vr in recent_vrs:
            mr = db.query(models.MatchingResult).filter(
                models.MatchingResult.field_update_id == vr.field_update_id
            ).first()
            recent.append({
                "event_id":      f"EVT-{vr.field_update_id:04d}",
                "db_id":         vr.field_update_id,
                "activity_id":   mr.activity_id if mr else None,
                "activity_name": mr.activity_name if mr else None,
                "confidence":    mr.final_confidence if mr else None,
            })

        return {
            "total_activities":    total,
            "in_progress":         in_progress,
            "completed":           completed,
            "overall_progress_pct": overall_pct,
            "pending_reviews":     pending_reviews,
            "deviations":          deviations,
            "verified_events":     verified,
            "attention_items":     attention[:5],
            "recent_verified":     recent,
        }
    finally:
        db.close()


# ── Insights ──────────────────────────────────────────────────
@app.get("/api/v1/insights")
def get_insights():
    from backend import models
    db = _db()
    try:
        devs = db.query(models.ScheduleDeviation).filter(
            models.ScheduleDeviation.progress_variance < -5
        ).all()
        seen, result = set(), []
        for d in sorted(devs, key=lambda x: x.progress_variance):
            if d.activity_id in seen:
                continue
            seen.add(d.activity_id)
            act = db.query(models.Activity).filter(
                models.Activity.activity_id == d.activity_id
            ).first()
            result.append({
                "activity_id":      d.activity_id,
                "activity_name":    act.activity_name if act else d.activity_id,
                "discipline":       act.discipline if act else "",
                "location":         act.location if act else "",
                "planned_progress": d.planned_progress,
                "actual_progress":  d.actual_progress,
                "variance_pct":     round(d.progress_variance, 1),
                "severity":         "high" if d.progress_variance < -20 else "medium",
            })
        return result
    finally:
        db.close()


# ── Evidence ──────────────────────────────────────────────────
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
            "available":     True,
            "evidence_id":   f"EVD-{ev.id:04d}",
            "image_url":     f"/uploads/{fname}" if fname else None,
            "confidence":    ev.confidence,
            "visual_signal": "supportive" if ev.confidence and ev.confidence > 0.5 else "weak",
            "status":        ev.verification_status,
        }
    finally:
        db.close()
