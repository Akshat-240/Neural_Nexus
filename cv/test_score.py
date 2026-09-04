import json

from cv.score import score_evidence


if __name__ == "__main__":
    result = score_evidence("test.jpg", "PIP-1024")
    print(json.dumps(result, indent=2))