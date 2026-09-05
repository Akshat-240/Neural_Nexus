import cv2
import numpy as np


def check_image_quality(image):
    """Checks if the photo is even usable before we try to analyze it."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    brightness = np.mean(gray)
    if brightness < 40:
        return False, "image_too_dark"

    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    if blur_score < 50:
        return False, "image_too_blurry"

    return True, "ok"


def detect_pipe_like_shapes(image):
    """Looks for LONG, mostly-PARALLEL straight lines — pipes run in one
    direction over a long distance, unlike keyboard keys/table edges which
    are short and go in many directions."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=120,
                             minLineLength=250, maxLineGap=5)

    if lines is None:
        return 0.0, 0

    angles = []
    for line in lines:
        x1, y1, x2, y2 = np.ravel(line)
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1)) % 180
        angles.append(angle)

    angles = np.array(angles)
    hist, _ = np.histogram(angles, bins=18, range=(0, 180))
    max_parallel_group = int(hist.max())

    total_lines = len(lines)
    confidence = min(1.0, max_parallel_group / 15)

    return confidence, total_lines

def check_scene_plausibility(image):
    """Rejects obviously non-industrial photos (sunsets, portraits, scenery)
    using color saturation as a proxy. Construction/pipe photos are usually
    muted/grey; vivid artistic photos are usually highly saturated."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    avg_saturation = np.mean(hsv[:, :, 1])  # 0-255 scale

    if avg_saturation > 90:
        return False, "image_too_vivid_unlikely_construction_site"

    return True, "ok"


def score_evidence(image_path, expected_activity):
    """Main function. Give it a photo path, get back a score."""
    if expected_activity and not str(expected_activity).startswith("PIP-"):
        return {
            "analysis": {
                "model": "heuristic_cv",
                "objects": [],
                "visual_evidence_score": 0.0,
                "supports_activity": False,
            },
            "failure_reason": "unsupported_activity"
        }

    image_path = str(image_path)
    if image_path.startswith(("/", "\\")) or ".." in image_path:
        return {
            "analysis": {
                "model": "heuristic_cv",
                "objects": [],
                "visual_evidence_score": 0.0,
                "supports_activity": False,
            },
            "failure_reason": "invalid_image_ref"
        }

    image = cv2.imread(image_path)
    if image is None:
        return {
            "analysis": {
                "model": "heuristic_cv",
                "objects": [],
                "visual_evidence_score": 0.0,
                "supports_activity": False,
            },
            "failure_reason": "image_could_not_be_read"
        }

    usable, reason = check_image_quality(image)
    if not usable:
        return {
            "analysis": {
                "model": "heuristic_cv",
                "objects": [],
                "visual_evidence_score": 0.1,
                "supports_activity": False,
            },
            "failure_reason": reason
        }

    plausible, plaus_reason = check_scene_plausibility(image)
    if not plausible:
        return {
            "analysis": {
                "model": "heuristic_cv",
                "objects": [],
                "visual_evidence_score": 0.05,
                "supports_activity": False,
            },
            "failure_reason": plaus_reason
        }

    confidence, num_lines = detect_pipe_like_shapes(image)

    objects = []
    if num_lines > 0:
        objects.append({
            "label": "pipe_like_structure",
            "confidence": round(confidence, 2),
            "count": num_lines
        })

    supports = confidence >= 0.75

    return {
        "analysis": {
            "model": "heuristic_cv",
            "objects": objects,
            "visual_evidence_score": round(confidence, 2),
            "supports_activity": supports,
        },
        "failure_reason": None
    }