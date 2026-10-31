# SkillRoute — Career Pivot Coach

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/AshayK003/skillroute/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AshayK003/skillroute/actions/workflows/ci.yml)

**A local-first career-pivot coach that compares resume evidence with a job description, prioritizes skill gaps, and supports learning plans, interview practice, and application tracking. Core analysis is deterministic; optional Gemini feedback can help users review mock-interview answers.**

---

## Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/AshayK003/skillroute.git
cd skillroute

# 2. Install the locked runtime and development dependencies
uv sync --extra dev --locked

# 3. Optional: copy the settings template
# PowerShell: Copy-Item .env.example .env
# macOS/Linux: cp .env.example .env

# 4. Run
uv run streamlit run app.py --server.address=127.0.0.1
```

Open http://localhost:8501. Upload a resume (PDF/DOCX/TXT), paste a job description, and select **Analyze Skill Gaps**. The default workflow needs no API key and makes no external AI requests; Gemini is called only for explicitly requested, consented interview feedback.

> **Hosted demo warning:** The app has no authentication. Tracker entries are plaintext JSON shared by users of the same app instance, and Streamlit Community Cloud does not guarantee persistence of local files. Do not enter real or sensitive resume, job-description, or application data in a hosted demo. Optional Gemini feedback sends the selected interview answer, question, target role, and skill to Google only after explicit consent and a request; it does not send resume/JD text.

---

## Features

| Page | What It Does |
|-----|--------------|
| **Intake** | Upload resume (PDF/DOCX/TXT) + paste JD → instant skill extraction with evidence levels |
| **Assessment** | Gap analysis with priority scoring: `Relevance × (1 − Evidence) × Extraction Confidence` |
| **Plan** | Weekly learning tasks, curated resources, and project recommendations |
| **Interview** | Rubric-based mock questions (technical + behavioral), self-evaluation scoring, and optional Gemini feedback |
| **Tracker** | Application CRUD — company, role, URL, status, notes + response/interview/offer rates |
| **Dashboard** | Readiness score, gap distribution, application stats, quick-action cards |

### Core Design Principles

- **Deterministic analysis** — Taxonomy-based matching and explicit evidence levels (NONE/MENTIONED/DEMONSTRATED/VERIFIED), with a transparent priority score.
- **Deterministic by default** — Core resume/JD analysis and scoring run locally without an AI provider.
- **Optional AI feedback** — Gemini can provide advisory interview-answer feedback after the user enters a key, explicitly consents, and requests it. No resume/JD text is sent.
- **Validated inputs** — Upload size/page limits and pasted-text limits are enforced.
- **Local persistence** — Application records are stored in `data/applications.json`.
- **Six-page Streamlit UI** — Sidebar navigation for intake, assessment, learning plan, interview practice, tracker, and dashboard.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        app.py (Streamlit)                       │
│  Sidebar pages: Intake │ Assessment │ Plan │ Interview │ Tracker │ Dashboard │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
    │ ResumeParser │ │ JDParser    │ │ SkillExtractor│
    │ (PDF/DOCX/   │ │ (regex +    │ │ (taxonomy +  │
    │  TXT)        │ │  aliases)   │ │  evidence)   │
    └──────┬───────┘ └──────┬──────┘ └──────┬───────┘
           │                │               │
           └────────────────┼───────────────┘
                            ▼
                   ┌──────────────────┐
                   │ SkillGapService  │
                   │ (orchestrates    │
                   │  full pipeline)  │
                   └────────┬─────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
    ┌────────────┐    ┌──────────────┐  ┌─────────────┐
    │ PlanGen    │    │ InterviewSvc │  │ TrackerSvc  │
    │ (weekly    │    │ (rubric Qs,  │  │ (JSON apps  │
    │  tasks,    │    │  self-eval)  │  │  + stats)   │
    │  projects) │    └──────────────┘  └─────────────┘
    └────────────┘
```

### Key Modules

| Module | Responsibility |
|--------|----------------|
| `domain/schemas.py` | Pydantic contracts for skill evidence/gaps, learning tasks, interview sessions, and application records |
| `domain/skill_taxonomy.py` | `SkillTaxonomy` — canonical skill catalog with aliases, categories, related skills |
| `domain/scoring.py` | Priority formula, evidence weights, gap ranking, readiness calculation |
| `services/resume_parser.py` | Multi-format parser (PDF/DOCX/TXT), LRU cache, 5MB/10-page limits |
| `services/jd_parser.py` | JD section detection and exact taxonomy/alias matching |
| `services/skill_extractor.py` | Evidence-level inference from context, taxonomy normalization |
| `services/skill_gap_service.py` | Full analysis pipeline orchestration |
| `services/plan_generator.py` | Learning plan + project recommendations from top gaps |
| `services/interview_service.py` | Skill-focused technical/behavioral questions + deterministic self-evaluation rubrics |
| `services/gemini_interview_service.py` | Optional Gemini interview feedback, bounded requests, and strict response validation |
| `services/tracker_service.py` | Application tracking with JSON persistence |
| `ui/theme.py` | Professional dark theme (550 lines, CSS variables, SVG icons) |
| `ui/*.py` | Page implementations, sidebar navigation, and shared theme |

### Data Flow

1. **Intake** → `ResumeParser` extracts text → `SkillExtractor` finds skills with evidence
2. **JD Parse** → `JDParser` splits into sections → `SkillExtractor` maps to taxonomy
3. **Gap Analysis** → `SkillGapService` computes `matched_skills`, `missing_skills`, `gaps`, and a heuristic readiness score
4. **Plan** → `plan_generator` creates weekly tasks and project recommendations from prioritized gaps
5. **Interview** → `InterviewService` creates questions + deterministic rubrics; an explicit, consented request can send the answer/question/role/skill to Gemini for advisory feedback
6. **Tracker** → `ApplicationTracker` persists applications to `data/applications.json`
7. **Dashboard** → Aggregates readiness, stats, recent activity

---

## Configuration

Settings are optional; defaults are listed below. Copy `.env.example` to `.env` to override them. Gemini does not require server configuration: a user may enter their own key in the sidebar for optional interview feedback. The key is held in Streamlit session memory, not persisted to app files or logged.

**Key and data handling:** Enter a key only when you trust the app host. The browser sends the key to the Streamlit server, which uses it in an HTTPS request to Google. The app does not save or log the key. An answer is sent only after the user checks the consent box and presses **Get Gemini feedback**; only the answer, interview question, target role, and skill are included. Resume and JD text are not sent. Google account terms, quotas, and charges may apply. If Gemini fails, deterministic self-evaluation remains available.

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment name |
| `DEBUG` | `true` | Debug mode |
| `MAX_PDF_SIZE_MB` | `5` | Maximum uploaded resume size |
| `MAX_PDF_PAGES` | `10` | Maximum PDF page count |
| `MAX_RESUME_LENGTH` | `50000` | Maximum pasted or extracted resume characters |
| `MAX_JD_LENGTH` | `10000` | Maximum job-description characters |
| `EVIDENCE_NONE` | `0.0` | Evidence weight for no evidence |
| `EVIDENCE_MENTIONED` | `0.2` | Evidence weight for a mention |
| `EVIDENCE_DEMONSTRATED` | `0.4` | Evidence weight for demonstrated experience |
| `EVIDENCE_VERIFIED` | `0.9` | Evidence weight for verified experience |

Use Streamlit CLI options to change the server port, for example `streamlit run app.py --server.port=8502`.

---

## Testing

```bash
# Run all tests
uv run pytest -q

# Run with coverage
uv run pytest -q --cov=src/career_coach --cov-report=term-missing
```

The suite includes unit and Streamlit integration tests for sample analysis, plan and interview generation, optional Gemini request validation and failure handling, navigation, input safety, and tracker persistence.

### Test Structure

```
tests/
├── conftest.py              # Fixtures: sample_resume_text, sample_jd_text
├── unit/
│   ├── test_scoring.py
│   ├── test_skill_taxonomy.py
│   ├── test_skill_extractor.py
│   ├── test_jd_parser.py
│   ├── test_interview_service.py
│   ├── test_plan_recommendations.py
│   ├── test_tracker_stats.py
│   ├── test_resume_parser.py
│   ├── test_ui_escape.py
│   └── test_upload_validation.py
└── integration/
    ├── test_analysis_workflow.py
    ├── test_input_safety.py
    ├── test_streamlit_app.py
    └── test_tracker_workflow.py
```

---

## Development

### Prerequisites

- Python 3.11+ (3.12 recommended)
- `uv` or `pip` for dependency management

### Setup

```bash
# Reproduce the locked development environment
uv sync --extra dev --locked

# Or pip
pip install -e ".[dev]"
```

### Code Quality

```bash
# Run the same focused lint gate as CI
uv run ruff check --select E4,E7,E9,F src/ tests/

# Type check
uv run mypy src/

# Dependency audit
uv run pip-audit --progress-spinner off --skip-editable
```

### Project Structure

```
skillroute/
├── app.py                      # Streamlit entry point
├── pyproject.toml              # Project config, deps, tool settings
├── .env.example                # Environment template
├── .gitignore
├── README.md                   # This file
├── CONTRIBUTING.md             # Contribution guide
├── ARCHITECTURE.md             # System architecture docs
├── uv.lock                     # Reproducible dependency resolution
├── .github/workflows/ci.yml    # Tests, type check, lint, dependency audit
├── data/
│   ├── skill_taxonomy.json     # Legacy 40-skill snapshot; not loaded by default
│   └── uploads/                # Temp resume uploads (gitignored)
├── internals/                  # Gitignored: build manual, research, decisions
├── src/career_coach/
│   ├── __init__.py
│   ├── config.py               # Pydantic Settings
│   ├── domain/                 # Schemas, taxonomy, scoring
│   ├── services/               # Parsers, extractors, gap analysis, plan, interview, tracker
│   └── ui/                     # Theme, sidebar navigation, and page implementations
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
└── .streamlit/
    └── config.toml             # Streamlit upload-size limit
```

See [LIMITATIONS.md](LIMITATIONS.md) for known constraints and demo status.

---

## Roadmap

- [x] GitHub Actions CI and dependency audit
- [ ] Configure the initial Streamlit Community Cloud app
- [ ] Demo screenshots or recording
- [ ] Semantic matching (optional; not part of current analysis pipeline)
- [ ] Hosted persistence and multi-user support
- [ ] Export analysis to PDF/Markdown
- [ ] LinkedIn profile import

---

## CI and Streamlit Community Cloud

GitHub Actions runs on pushes, pull requests targeting `main`, and manual dispatch. The workflow tests Python 3.11 and 3.12, runs focused Ruff checks and mypy, executes the test suite with coverage, and audits dependencies. `uv.lock` keeps CI and local installs reproducible.

To enable deployment, create an app in [Streamlit Community Cloud](https://share.streamlit.io/) and select this repository, the `main` branch, and `app.py` as the entry point. Choose Python 3.12. After the initial setup, Community Cloud rebuilds the app when the selected branch changes; this repository does not include a separate deployment workflow or Cloud credentials.

For safer merges, configure GitHub branch protection to require **Tests (Python 3.11)**, **Tests (Python 3.12)**, and **Dependency audit**. Hosted deployment is for demonstrations only; see [LIMITATIONS.md](LIMITATIONS.md) before sharing the app.

---

## License

**MIT**.

See [LICENSE](LICENSE) for full text.

---

## Acknowledgments

- **OSS patterns from:** [Walid-Khalfa/resume-matcher](https://github.com/Walid-Khalfa/resume-matcher), [gerald1124-code/ai-analyze](https://github.com/gerald1124-code/ai-analyze), [najmabakdach/smart-career-matching-system](https://github.com/najmabakdach/smart-career-matching-system)
- **Icons:** [Lucide](https://lucide.dev/)
- **Built for:** Hackathon MVP — Career Pivot Coach end-to-end build
