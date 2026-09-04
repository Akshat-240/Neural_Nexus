

from backend.database import SessionLocal, engine, Base
from backend import crud, schemas, models
from ai.pipeline import get_demo_schedule_activities

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Create Demo Project
    try:
        proj = crud.create_project(db, schemas.ProjectCreate(name="Demo Project PRJ-DEMO-01", location="Unit 3"))
        project_id = proj.id
        
        # Get Demo Activities
        activities = get_demo_schedule_activities()
        for act in activities:
            crud.create_activity(db, schemas.ActivityCreate(
                project_id=project_id,
                activity_id=act["activity_id"],
                activity_name=act["activity_name"],
                wbs_code=act["wbs"]["code"],
                level=act["wbs"]["level"],
                discipline=act["discipline"],
                location=act["location"],
                planned_progress=act["planned"]["progress_pct"],
                status=act["status"]
            ))
            
        print("Database seeded successfully with Demo Project and Schedule Activities.")
    except Exception as e:
        print(f"Failed to seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
