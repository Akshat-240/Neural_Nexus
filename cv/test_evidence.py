from evidence import analyze_evidence
import json

output = analyze_evidence("EVT-0001", "test.jpg", "PIP-1024")
print(json.dumps(output, indent=2))