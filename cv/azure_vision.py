"""
Azure Computer Vision API client for Neural Nexus.

Credentials are loaded securely from environment variables:
  - AZURE_CV_KEY
  - AZURE_CV_ENDPOINT

If credentials are not configured, all functions return None so the
caller can fall back to the heuristic CV pipeline.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Load .env from project root if python-dotenv is available
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass

AZURE_CV_KEY = os.environ.get("AZURE_CV_KEY", "")
AZURE_CV_ENDPOINT = os.environ.get("AZURE_CV_ENDPOINT", "").rstrip("/")


def is_configured() -> bool:
    """Return True if Azure CV credentials are present."""
    return bool(AZURE_CV_KEY and AZURE_CV_ENDPOINT)


def analyze_image_azure(image_path: str) -> dict | None:
    """
    Send an image to Azure Computer Vision and return structured analysis.

    Returns a dict with keys:
        model: str
        objects: list[dict]  — detected objects with label, confidence
        tags: list[str]
        visual_evidence_score: float
        supports_activity: bool

    Returns None if Azure CV is not configured or if the call fails,
    allowing the caller to fall back to heuristic analysis.
    """
    if not is_configured():
        logger.info("Azure CV not configured — skipping cloud analysis")
        return None

    try:
        import httpx
    except ImportError:
        logger.warning("httpx not installed — cannot call Azure CV API")
        return None

    abs_path = Path(image_path)
    if not abs_path.is_absolute():
        abs_path = Path(__file__).resolve().parent.parent / image_path
    if not abs_path.exists():
        logger.warning("Image file not found for Azure analysis: %s", abs_path)
        return None

    url = f"{AZURE_CV_ENDPOINT}/computervision/imageanalysis:analyze"
    params = {
        "api-version": "2024-02-01",
        "features": "tags,objects,caption",
    }
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_CV_KEY,
        "Content-Type": "application/octet-stream",
    }

    try:
        with open(abs_path, "rb") as f:
            image_data = f.read()

        resp = httpx.post(url, params=params, headers=headers,
                          content=image_data, timeout=15.0)
        resp.raise_for_status()
        result = resp.json()

        # Parse Azure response into our standard schema
        objects = []
        pipe_confidence = 0.0

        # Extract detected objects
        for obj in result.get("objectsResult", {}).get("values", []):
            tag_name = obj.get("tags", [{}])[0].get("name", "unknown") if obj.get("tags") else "unknown"
            conf = obj.get("tags", [{}])[0].get("confidence", 0.0) if obj.get("tags") else 0.0
            objects.append({
                "label": tag_name,
                "confidence": round(conf, 2),
                "count": 1,
            })

        # Extract tags and check for construction / pipe related keywords
        construction_keywords = {
            "pipe", "piping", "pipeline", "steel", "construction",
            "industrial", "metal", "structure", "structural", "scaffold",
            "beam", "column", "welding", "flange", "valve", "spool",
            "fabrication", "erection", "engineering", "machinery",
            "equipment", "tube", "duct", "conduit", "building",
        }

        tags = []
        for tag_item in result.get("tagsResult", {}).get("values", []):
            tag_name = tag_item.get("name", "")
            tag_conf = tag_item.get("confidence", 0.0)
            tags.append(tag_name)
            if tag_name.lower() in construction_keywords:
                pipe_confidence = max(pipe_confidence, tag_conf)

        # Also check objects for construction relevance
        for obj_item in objects:
            if obj_item["label"].lower() in construction_keywords:
                pipe_confidence = max(pipe_confidence, obj_item["confidence"])

        # If no specific construction keyword found, use caption analysis
        caption_text = result.get("captionResult", {}).get("text", "").lower()
        caption_conf = result.get("captionResult", {}).get("confidence", 0.0)
        for kw in construction_keywords:
            if kw in caption_text:
                pipe_confidence = max(pipe_confidence, caption_conf * 0.8)
                break

        # Ensure minimum score if *any* objects or tags were found
        if pipe_confidence == 0.0 and (objects or tags):
            pipe_confidence = 0.15  # baseline — something was detected

        supports = pipe_confidence >= 0.60

        return {
            "model": "azure-computer-vision-4.0",
            "objects": objects,
            "tags": tags[:10],
            "caption": result.get("captionResult", {}).get("text"),
            "visual_evidence_score": round(pipe_confidence, 2),
            "supports_activity": supports,
        }

    except httpx.HTTPStatusError as e:
        logger.error("Azure CV API error %s: %s", e.response.status_code, e.response.text[:200])
        return None
    except Exception as e:
        logger.error("Azure CV analysis failed: %s", e)
        return None
