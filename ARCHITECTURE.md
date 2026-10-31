# SkillRoute Architecture

> **Version:** 0.1.0
> **Status:** Active development (hackathon MVP)
> **Last Updated:** 2026-10-31

## System Overview

SkillRoute is a **modular monolith** — a single deployable Streamlit application with clean internal boundaries between domain, services, and UI layers. Designed for hackathon speed with production-grade foundations.

```
┌─────────────────────────────────────────────────────────────────┐
│                      app.py (Streamlit)                         │
│  ┌────────┬──────────┬──────┬──────────┬──────────┬─────────┐  │
│  │ Intake │Assessment│ Plan │ Projects │Interview │ Tracker │  │
│  └────┬───┴────┬─────┴──┬───┴────┬────┴────┬────┴────┬───┘  │
└───────┼────────┼────────┼────────┼────────┼────────┼────────┘
        │        │        │        │        │        │
        ▼        ▼        ▼        ▼        ▼        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SkillGapService (Orchestrator)               │
│  resume_parser → jd_parser → skill_extractor → scoring          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ PlanGenerator │  │ InterviewSvc  │  │ TrackerSvc    │
└───────────────┘  └───────────────┘  └───────────────┘
```

## Layer Responsibilities

### Domain Layer (`src/career_coach/domain/`)

| File | Purpose |
|------|---------|
| `schemas.py` | All Pydantic models — single source of truth for data contracts |
| `skill_taxonomy.py` | `SkillTaxonomy` class — canonical skill catalog with alias resolution |
| `scoring.py` | Pure functions: priority formula, evidence weights, gap ranking, readiness |

**Key invariants:**
- No I/O, no external deps, no side effects
- All functions are pure and deterministic
- Fully testable without mocks

### Services Layer (`src/career_coach/services/`)

| Service | Input | Output | External Deps |
|---------|-------|--------|---------------|
| `ResumeParser` | File bytes | Text + metadata | `pypdf`, `pdfplumber`, `python-docx` |
| `JDParser` | Raw JD text | Structured sections + skills | `difflib` (stdlib) |
| `SkillExtractor` | Text + taxonomy | `SkillMatch[]` with evidence | `SkillTaxonomy` |
| `SkillGapService` | Resume + JD | `GapAnalysisResult` | All above |
| `PlanGenerator` | `GapAnalysisResult` | `WeeklyPlan[]`, `ProjectSpec[]` | — |
| `InterviewService` | `GapAnalysisResult` | `InterviewSession` | — |
| `TrackerService` | User actions | `ApplicationRecord[]` | JSON file I/O |

### UI Layer (`src/career_coach/ui/`)

| File | Responsibility |
|------|----------------|
| `theme.py` | CSS variables, component renderers, SVG icons, design tokens |
| `intake.py` | Resume upload, JD input, analysis trigger, results rendering |
| `plan.py` | Duration selector, weekly tasks, project cards |
| `interview.py` | Session generation, rubric display, self-eval |
| `tracker.py` | CRUD forms, status filter, stats cards |
| `dashboard.py` | Metrics, charts, quick actions |

**UI Principles:**
- No business logic in UI — only presentation
- All data flows through session state
- Theme functions are pure renderers (no `st.*` calls inside theme)

### Config (`src/career_coach/config.py`)

`Settings` class via Pydantic Settings:
- Loads from `.env` (see `.env.example`)
- Type-safe, validated, documented
- Single source for all environment configuration

## Data Models (Core)

### SkillEvidence
```python
canonical_skill: str
evidence_level: EvidenceLevel  # NONE | MENTIONED | DEMONSTRATED | VERIFIED
source: str                    # "resume" | "jd"
supporting_evidence: str       # Quote/context from source
user_confirmed: bool
```

### SkillGap
```python
skill: str
priority: float                # R × (1-E) × C
jd_requirement: JobSkillRequirement
resume_evidence: SkillEvidence | None
gap_type: GapType              # MISSING | WEAK_EVIDENCE | OUTDATED
rationale: str
```

### GapAnalysisResult
```python
gaps: list[SkillGap]
matched_skills: list[str]
missing_skills: list[str]
readiness_score: float         # 0-100
summary: str
```

## Priority Formula

```
priority = relevance × (1 - evidence_weight) × criticality
```

| Evidence Level | Weight |
|----------------|--------|
| NONE           | 0.0    |
| MENTIONED      | 0.2    |
| DEMONSTRATED   | 0.4    |
| VERIFIED       | 0.9    |

- **Relevance (R):** 0-1, how central the skill is to the JD
- **Evidence (E):** Weight from table above
- **Criticality (C):** 0-1, from JD section (REQUIREMENTS=1.0, PREFERRED=0.6)

## Skill Taxonomy

`data/skill_taxonomy.json` — 50+ curated skills across 11 categories:

- `programming` — Python, SQL, JavaScript, TypeScript, Go, Rust
- `data` — Pandas, NumPy, Spark, Airflow, dbt, Snowflake
- `ml` — PyTorch, TensorFlow, scikit-learn, XGBoost, MLOps
- `cloud` — AWS, GCP, Azure, Kubernetes, Terraform
- `devops` — Docker, CI/CD, GitHub Actions, Prometheus, Grafana
- `frontend` — React, Vue, Next.js, Tailwind, CSS
- `backend` — FastAPI, Django, Node.js, PostgreSQL, Redis
- `mobile` — React Native, Flutter, Swift, Kotlin
- `testing` — pytest, Playwright, Cypress, Jest
- `soft_skills` — Communication, Leadership, Problem Solving
- `domain` — FinTech, HealthTech, EdTech, E-commerce

Each skill has:
- `canonical` — Display name
- `aliases` — Alternate names for fuzzy matching
- `category` — For resource mapping
- `related` — For project recommendations

## Fuzzy Matching

`difflib.SequenceMatcher` with threshold **0.85** for alias matching.

Flow:
1. Extract tokens from text (split on non-alphanumeric)
2. For each token, find best match in taxonomy aliases
3. If ratio ≥ 0.85 → map to canonical skill
4. Infer evidence level from context patterns

## Persistence

| Data | Storage | Location |
|------|---------|----------|
| Applications | JSON file | `data/applications.json` |
| Skill taxonomy | JSON file | `data/skill_taxonomy.json` |
| Session state | Streamlit session | In-memory |
| Resume uploads | Temp files | `data/uploads/` (auto-cleanup) |
| Database (future) | SQLite/PostgreSQL | `DATABASE_URL` |

**No migrations needed** — JSON is schema-less, Pydantic validates on load.

## Configuration Reference

All via `.env` (loaded by Pydantic Settings):

```bash
# App
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///./data/app.db

# Optional AI
OPENROUTER_API_KEY=
OPENAI_API_KEY=
AI_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_MODEL=openai/gpt-4o-mini

# Limits
MAX_PDF_PAGES=10
MAX_PDF_SIZE_MB=5

# Streamlit
STREAMLIT_PORT=8501
```

## Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Streamlit Cloud (Free)
1. Push to GitHub
2. Connect repo at https://share.streamlit.io
3. Set `SECRET_KEY` in secrets
4. Deploy — auto-detects `app.py`

### Docker (Production)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Render / Fly.io / Railway
- Same Dockerfile works
- Set `DATABASE_URL` to managed PostgreSQL
- Add `SECRET_KEY` as env var

## Security

- **No hardcoded secrets** — all via `.env`
- **File upload validation** — MIME type + size + page count limits
- **Path traversal protection** — temp files in dedicated upload dir
- **SQL injection** — SQLAlchemy ORM only, no raw SQL
- **XSS** — Streamlit auto-escapes; `unsafe_allow_html` only for trusted theme CSS

## Performance

| Operation | Target | Current |
|-----------|--------|---------|
| Resume parse (PDF, 5MB) | < 2s | ~1.2s |
| JD parse | < 500ms | ~200ms |
| Gap analysis | < 1s | ~600ms |
| Plan generation | < 500ms | ~300ms |
| Cold start (Streamlit) | < 10s | ~8s |

**Optimizations:**
- LRU cache on `ResumeParser` (max 32 entries)
- Taxonomy loaded once at startup (singleton)
- No redundant computations in UI render loop

## Testing Strategy

```
tests/
├── conftest.py                 # Shared fixtures
├── unit/
│   ├── test_scoring.py         # Pure functions — 20 tests
│   ├── test_skill_taxonomy.py  # Taxonomy lookup — 10 tests
│   └── (planned: test_extractors, test_services)
└── integration/                # (planned: full pipeline)
```

- **Unit:** Domain + scoring (pure functions, no mocks needed)
- **Integration:** Service orchestration with sample data
- **E2E:** Streamlit script runner (planned)

## Extensibility Points

| Extension | How |
|-----------|-----|
| New skill category | Add to `data/skill_taxonomy.json` + `SkillCategory` enum |
| New evidence level | Extend `EvidenceLevel` enum + add weight in `scoring.py` |
| New parser format | Implement `BaseParser` protocol in `resume_parser.py` |
| New JD section | Add to `JDSectionType` enum + regex in `jd_parser.py` |
| New tab | Create `ui/new_tab.py` + register in `app.py` |
| AI enhancement | Implement `LLMExtractor` protocol in `skill_extractor.py` |

## Decision Log (Key ADRs)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-10-31 | Modular monolith | Hackathon MVP, single-user, simpler deploy |
| 2026-10-31 | SQLite local | Zero-config dev; PostgreSQL later for demo |
| 2026-10-31 | Deterministic core + optional AI | Works without API keys; pluggable enhancement |
| 2026-10-31 | Pydantic Settings + .env | Never hardcode secrets; type-safe config |
| 2026-10-31 | In-memory LRU cache | MVP simplicity; disk cache optional later |
| 2026-10-31 | Taxonomy-driven normalization | OSS pattern from resume-matcher |
| 2026-10-31 | Fuzzy threshold 0.85 | Balances recall/precision per OSS pattern |
| 2026-10-31 | Evidence levels 4-tier | Guide requirement for transparent rationale |
| 2026-10-31 | Professional dark theme | "Doesn't look like AI slop" — intentional design |
| 2026-10-31 | Dual-column intake | Clear separation resume vs JD |
| 2026-10-31 | JSON file storage for tracker | Zero-config persistence for hackathon |

## Future Architecture Evolution

| Phase | Change | Trigger |
|-------|--------|---------|
| Post-hackathon | Extract services to FastAPI | Multi-user, mobile app, webhooks |
| Scale | PostgreSQL + Alembic | Concurrent users, data durability |
| AI | LangGraph/LangChain orchestration | Complex multi-step reasoning |
| Enterprise | Auth (Auth0/Clerk), RBAC, audit logs | Team/org features |
| Mobile | React Native / Flutter | Native mobile experience |
