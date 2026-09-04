# AI Matching & Re-ranking Module (Person 3)

The `ai/matching/` module maps structured `FieldEvent` records against L5/L6 project schedule activities (`schedule_activity.json`) to find candidate activities, re-rank them using contextual engineering signals, and emit explainable `match_result.json` outputs.

## Architecture

```text
Structured Field Event (contracts/schemas/field_event.json)
                         │
                         ▼
        [L5L6Retriever + SemanticEmbedder]
      ├── Remote Embeddings (OpenAI / compatible)
      └── Local Embeddings (Subword n-gram hashing in NumPy)
                         │
                         ▼
             Top-K Candidate Activities
                         │
                         ▼
             [ContextualReranker]
      ├── 1. Semantic Similarity Score (Action / verb correspondence)
      ├── 2. Context Score:
      │      ├── Discipline Alignment (0.25)
      │      ├── Location Alignment   (0.25)
      │      ├── Asset Specificity    (0.35)
      │      └── WBS Level Weight     (0.15)
      ├── 3. Visual Score (Neutral 0.0 default, fused later by Person 6)
      └── 4. Ambiguity Detection & Confidence Policy Enforcement
                         │
                         ▼
               [MatchExplainer]
      ├── Human-readable match_reason bullet points
      └── Disambiguation review_reason
                         │
                         ▼
         Match Result (contracts/schemas/match_result.json)
```

## Scoring Approach & Weights

### 1. Component Scores
Each candidate in `candidates` contains transparent component scores:
```json
"scores": {
  "semantic": 0.92,
  "context": 0.96,
  "visual": 0.0
}
```
- **Semantic Score**: Evaluates correspondence between field action verbs (e.g., "erected", "spool erection") and schedule activity names (e.g., "Erect Line 24-XX").
- **Context Score**: Multi-signal EPC compatibility score:
  $$\text{Context} = 0.25 \cdot \text{Discipline} + 0.25 \cdot \text{Location} + 0.35 \cdot \text{Asset} + 0.15 \cdot \text{WBS}$$
- **Visual Score**: Kept neutral (0.0) by default. Person 3 does not allow visual evidence alone to prove completion; Person 6 performs evidence fusion.

### 2. Confidence Calculation & Policy
$$\text{Confidence} = 0.45 \cdot \text{Semantic} + 0.55 \cdot \text{Context}$$

Policy rules (`contracts/policies/confidence_policy.json`):
- $\ge 0.90 \implies \text{Fast Track} \implies \text{review\_required: false}, \text{review\_reason: null}$
- $< 0.90 \implies \text{Planner Review} \implies \text{review\_required: true}, \text{review\_reason: string}$

### 3. Ambiguity Handling (Case B)
When the field note is generic (e.g., *"Line 24 work completed"*), multiple schedule activities relate to the line (`PIP-1024`, `PIP-1025`, `PIP-1026`, `PIP-1027`). The engine detects this ambiguity, caps confidence at $\le 0.89$, and provides an explicit `review_reason`:
> *"Multiple schedule activities relate to Line 24 but the field statement does not identify the exact work type."*

## Fallback & Offline Behavior

- `SemanticEmbedder` requires no heavy ML packages (Torch, HuggingFace, Transformers).
- Uses a local subword character 3-gram and 4-gram hashing vectorizer with sublinear term-frequency scaling and L2 normalization implemented purely in `numpy`.
- Fully deterministic, millisecond latency, and operable in air-gapped site deployments.

## Example Usage

```python
from ai.matching import ScheduleMatcher
from ai.pipeline import get_demo_schedule_activities

matcher = ScheduleMatcher()
activities = get_demo_schedule_activities()

field_event = {
    "event_id": "EVT-0001",
    "raw_text": "24-XX spool erected today at Unit 3.",
    "extracted": {
        "activity": "24-XX spool erection",
        "discipline": "Piping",
        "location": "Unit 3",
        "asset_or_reference": "24-XX",
        "context": "Spool erection"
    }
}

result = matcher.match(field_event, activities)
print(result["selected_activity_id"])  # PIP-1024
print(result["review_required"])       # False
print(result["candidates"][0]["match_reason"])
```
