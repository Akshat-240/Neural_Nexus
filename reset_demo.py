"""
Demo Reset + Reseed Script
Run this before every demo to get a clean, perfect starting state.
"""
from backend.database import SessionLocal, engine, Base
from backend import models

def reset_and_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # ── 1. Wipe all transient demo data (keep project + activities) ──
        db.query(models.ScheduleDeviation).delete()
        db.query(models.VerificationResult).delete()
        db.query(models.MatchingResult).delete()
        db.query(models.Evidence).delete()
        db.query(models.FieldUpdate).delete()
        db.query(models.Activity).delete()
        db.query(models.Project).delete()
        db.commit()
        print("Cleared all records.")

        # ── 2. Create project ──────────────────────────────────────────
        proj = models.Project(
            name="North Processing Unit — Line 24-XX",
            location="Unit 3",
            status="active"
        )
        db.add(proj)
        db.commit()
        db.refresh(proj)
        pid = proj.id
        print(f"Created project id={pid}")

        # ── 3. Seed 12 realistic activities ───────────────────────────
        activities = [
            # WBS 1.1 — Civil & Structural
            dict(activity_id="CIV-1001", activity_name="Excavation & earthworks", wbs_code="1.1.1", level="L5", discipline="Civil",     location="Unit 3", planned_progress=100.0, status="completed"),
            dict(activity_id="CIV-1002", activity_name="Foundation preparation",  wbs_code="1.1.2", level="L5", discipline="Civil",     location="Unit 3", planned_progress=100.0, status="completed"),
            dict(activity_id="STR-1003", activity_name="Structural steel erection",wbs_code="1.1.3", level="L5", discipline="Structural",location="Unit 3", planned_progress=90.0,  status="in_progress"),
            # WBS 1.2 — Piping (Line 24-XX core)
            dict(activity_id="PIP-1021", activity_name="Spool fabrication — Line 24-XX",      wbs_code="1.2.1", level="L5", discipline="Piping",    location="Unit 3", planned_progress=100.0, status="completed"),
            dict(activity_id="PIP-1022", activity_name="Pipe support installation",            wbs_code="1.2.2", level="L5", discipline="Mechanical", location="Unit 3", planned_progress=80.0,  status="in_progress"),
            dict(activity_id="PIP-1024", activity_name="Erect Line 24-XX",                    wbs_code="1.2.4", level="L5", discipline="Piping",    location="Unit 3", planned_progress=100.0, status="in_progress"),
            dict(activity_id="PIP-1025", activity_name="Fit-up Line 24-XX",                   wbs_code="1.2.5", level="L5", discipline="Piping",    location="Unit 3", planned_progress=100.0, status="completed"),
            dict(activity_id="PIP-1026", activity_name="Weld Line 24-XX",                     wbs_code="1.2.6", level="L5", discipline="Piping",    location="Unit 3", planned_progress=80.0,  status="in_progress"),
            dict(activity_id="PIP-1027", activity_name="Hydrotest Line 24-XX",                wbs_code="1.2.7", level="L5", discipline="Piping",    location="Unit 3", planned_progress=0.0,   status="not_started"),
            dict(activity_id="PIP-1028", activity_name="Valve installation — Line 24-XX",     wbs_code="1.2.8", level="L5", discipline="Piping",    location="Unit 3", planned_progress=60.0,  status="in_progress"),
            # WBS 1.3 — Instrumentation & Electrical
            dict(activity_id="INS-1031", activity_name="Instrument hook-up",                  wbs_code="1.3.1", level="L5", discipline="Instrumentation", location="Unit 3", planned_progress=50.0,  status="in_progress"),
            dict(activity_id="ELE-1041", activity_name="Electrical cabling — Unit 3",         wbs_code="1.4.1", level="L5", discipline="Electrical",       location="Unit 3", planned_progress=70.0,  status="in_progress"),
        ]

        for a in activities:
            db.add(models.Activity(project_id=pid, **a))
        db.commit()
        print(f"Seeded {len(activities)} activities.")

        # ── 4. Pre-seed realistic deviations for Insights page ─────────
        # These represent the current project state before any demo events
        deviations = [
            # PIP-1022: pipe supports behind schedule (this is Case C target)
            dict(activity_id="PIP-1022", planned_progress=80.0, actual_progress=40.0, progress_variance=-40.0, deviation_flag="true", status="calculated"),
            # STR-1003: slightly behind
            dict(activity_id="STR-1003", planned_progress=90.0, actual_progress=75.0, progress_variance=-15.0, deviation_flag="true", status="calculated"),
            # PIP-1028: valve installation behind
            dict(activity_id="PIP-1028", planned_progress=60.0, actual_progress=42.0, progress_variance=-18.0, deviation_flag="true", status="calculated"),
            # On-track activities with actual = planned
            dict(activity_id="CIV-1001", planned_progress=100.0, actual_progress=100.0, progress_variance=0.0, deviation_flag="false", status="calculated"),
            dict(activity_id="CIV-1002", planned_progress=100.0, actual_progress=100.0, progress_variance=0.0, deviation_flag="false", status="calculated"),
            dict(activity_id="PIP-1021", planned_progress=100.0, actual_progress=100.0, progress_variance=0.0, deviation_flag="false", status="calculated"),
            dict(activity_id="PIP-1025", planned_progress=100.0, actual_progress=100.0, progress_variance=0.0, deviation_flag="false", status="calculated"),
        ]
        for d in deviations:
            db.add(models.ScheduleDeviation(project_id=pid, **d))
        db.commit()
        print(f"Seeded {len(deviations)} schedule deviations.")

        print("\nDemo reset complete. Database is in clean starting state.")
        print("Activities: 12 | Pre-seeded deviations: 3 (STR-1003, PIP-1022, PIP-1028)")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed()
