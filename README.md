# Neural Nexus (SIH26122)

Neural Nexus is an intelligent, multi-modal Field Capture & Schedule Orchestration platform designed for complex engineering and construction projects (EPC). It bridges the gap between unstructured field reality (voice notes, text, site photos) and rigid project schedules by using AI, Computer Vision, and Speech-to-Text to autonomously extract, match, verify, and track construction progress.

## 🌟 Key Features

* **🎙️ Voice & Text Field Capture:** Report site updates natively using text or voice (with Hinglish support) without needing activity codes.
* **🧠 AI Extraction:** Intelligently extracts activity, discipline, location, and status from unstructured natural language.
* **🔗 Schedule Matching:** Semantic similarity matching against L5/L6 DB activities to automatically figure out which schedule item is being reported.
* **👁️ Computer Vision Verification:** Validates physical progress by analyzing uploaded site photos for structural evidence (e.g., pipe-like structures) using OpenCV.
* **🚦 Confidence Gating:** High-confidence updates are automatically verified and persisted; ambiguous updates are flagged for human review.
* **📊 Live Dashboard & Insights:** Real-time visibility into project deviations, progress variance, and pending reviews.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* Node.js & npm (for Vite frontend)

### Installation & Setup

1. **Clone the repository** and ensure you're in the project root:
   ```bash
   git clone <repository_url>
   cd NEURAL-NEXUS-SIH26122
   ```

2. **Install Python Dependencies**:
   Ensure you install the dependencies required for the backend, AI, and CV modules. (We recommend using a virtual environment).
   ```bash
   pip install -r requirements.txt # (or install via your preferred package manager)
   ```

3. **Install Frontend Dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API keys (e.g., OpenAI API Key for the AI extraction, Azure Speech keys for online STT). 

### Running the Unified Stack

Start the entire application (Backend API + Frontend Vite Server) with a single command from the project root:

```bash
python run.py
```

* **Frontend UI:** `http://localhost:5173`
* **Integration API:** `http://localhost:8000`

---

## 🏗️ System Architecture & Workflow

1. **Input:** Field user provides an update via Voice/Text and an optional Image.
2. **Orchestrator:** `/api/v1/process-update` receives the payload.
3. **AI Extraction:** Natural language is parsed into structured JSON (Activity, Status, Location, % Progress).
4. **Matching:** The AI matches the parsed event against active schedule items in the database.
5. **Computer Vision:** If an image is provided, `cv/score.py` analyzes the image for corroborating evidence.
6. **Decision Engine:** Confidence scores from Semantic matching, Context, and Visual evidence are fused. 
7. **Result:** The system returns a decision: **Verified** (auto-updates schedule) or **Pending Review** (requires human-in-the-loop).

---

## 📂 Project Structure & Team Assignments

This repository is built as a micro-module monolith, allowing team members to independently develop their AI/CV components before unified orchestration.

| Directory | Owner | Focus Area |
| :--- | :--- | :--- |
| `frontend/` | **Person 1** | React/Vite UI, Dashboards, Field Capture screens |
| `backend/` | **Person 2** | FastAPI, SQLite DB, CRUD operations, core models |
| `ai/` | **Person 3** | LLM Extraction, Semantic Embeddings, Schedule Matching |
| `cv/` | **Person 4** | Image analysis, OpenCV pipelines, Visual Evidence Scoring |
| `voice_offline/` | **Person 5** | Speech-to-Text (Azure/Whisper), Hinglish translation |
| `integration/` | **Person 6 (Integration)** | Unified Orchestrator, Adapters, API endpoints |

### Additional Directories
* `data/` - Benchmark datasets, demo files, schedule CSVs, and field report logs.
* `contracts/` - Shared JSON schema definitions (e.g., `field_event.json`, `match_result.json`).
* `tests/` - Integration and unit tests for pipelines.

> ⚠️ **IMPORTANT CONTRACT RULE**: The schemas inside `contracts/schemas/` act as the absolute source of truth between modules. Do not change shared JSON field names without cross-team coordination.

---

## 🤝 Contributing

When contributing to your respective modules, ensure that:
- You do not break the unified API contracts.
- You provide local test files for your module.
- Any new environment variable is documented in `.env.example`.
