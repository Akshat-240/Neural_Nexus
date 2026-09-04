import json

from cv.evidence import analyze_evidence


if __name__ == "__main__":
    output = analyze_evidence("EVT-0001", "test.jpg", "PIP-1024")
    print(json.dumps(output, indent=2))