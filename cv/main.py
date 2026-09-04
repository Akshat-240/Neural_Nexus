from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from cv.evidence import analyze_evidence

app = FastAPI()

class EvidenceRequest(BaseModel):
    event_id: str
    candidate_activity_id: str
    image_ref: str

@app.post("/evidence/analyze")
def evidence_analyze(req: EvidenceRequest):
    if req.image_ref.startswith(("/", "\\")) or ".." in req.image_ref:
        raise HTTPException(status_code=400, detail="image_ref must be a relative path without '..'")
    return analyze_evidence(req.event_id, req.image_ref, req.candidate_activity_id)