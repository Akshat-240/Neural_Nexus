from datetime import datetime, timezone

from cv.score import score_evidence


def analyze_evidence(event_id, image_path, candidate_activity_id, evidence_id="EVD-AUTO"):
    result = score_evidence(image_path, candidate_activity_id)

    return {
        "evidence_id": evidence_id,
        "event_id": event_id,
        "source": {
            "type": "image",
            "ref": image_path
        },
        "analysis": result["analysis"],
        "annotation_ref": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }