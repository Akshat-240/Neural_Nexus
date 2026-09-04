from score import score_evidence
import json

result = score_evidence("test.jpg", "PIP-1024")
print(json.dumps(result, indent=2))