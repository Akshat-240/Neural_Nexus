from fastapi import FastAPI
from pydantic import BaseModel
from evidence import analyze_evidence

app = FastAPI()

class EvidenceRequest(BaseModel):
    event_id: str
    candidate_activity_id: str
    image_ref: str

@app.post("/evidence/analyze")
def evidence_analyze(req: EvidenceRequest):
    return analyze_evidence(req.event_id, req.image_ref, req.candidate_activity_id)