# Neural Nexus SIH26122

## Project Structure

```text
NEURAL-NEXUS-SIH26122/
│
├── frontend/
│   └── README.md
│
├── backend/
│   └── README.md
│
├── ai/
│   ├── extraction/
│   │   └── README.md
│   ├── matching/
│   │   └── README.md
│   └── prompts/
│       └── README.md
│
├── cv/
│   └── README.md
│
├── voice_offline/
│   └── README.md
│
├── integration/
│   └── README.md
│
├── data/
│   ├── schedules/
│   ├── field_reports/
│   ├── images/
│   ├── demo/
│   └── manifests/
│
├── contracts/
│   ├── schemas/
│   └── examples/
│
├── tests/
│
├── docs/
│
├── .env.example
├── .gitignore
└── README.md
```

## Folder Assignments

| Person | Owns |
| :--- | :--- |
| Person 1 | `frontend/` |
| Person 2 | `backend/` |
| Person 3 | `ai/` |
| Person 4 | `cv/` |
| Person 5 | `voice_offline/` |
| Person 6 / Me | `integration/` + `contracts/` + final integration |

### Shared Folders

These are not owned by one person alone. I will coordinate these:
- `data/`
- `tests/`
- `docs/`
- `contracts/`

## Central Contract

> **IMPORTANT**: Do not change shared JSON field names casually. If you need a new field, add it as optional and tell me first.

The contracts are available in `contracts/schemas/` and `contracts/examples/`:
- `field_event.json`
- `schedule_activity.json`
- `match_result.json`
- `verification_update.json`
