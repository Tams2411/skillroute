# SkillRoute — Career Pivot Coach

[![CI](https://github.com/Tams2411/skillroute/actions/workflows/ci.yml/badge.svg)](https://github.com/Tams2411/skillroute/actions/workflows/ci.yml)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL_3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/coverage-30%25-yellow.svg)](https://github.com/Tams2411/skillroute)

**An AI-powered career pivot coach that analyzes your resume against job descriptions, identifies skill gaps with evidence-based prioritization, and generates personalized learning plans, interview prep, and application tracking — all in one Streamlit app.**

---

## Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/Tams2411/skillroute.git
cd skillroute

# 2. Create virtual environment and install
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys (optional — core works without them)

# 4. Run
streamlit run app.py
```

Open http://localhost:8501 — you'll see the **Intake** tab. Upload a resume (PDF/DOCX/TXT), paste a job description, click **Analyze Gap**, and explore the 6 tabs.

---

## Features

| Tab | What It Does |
|-----|--------------|
| **Intake** | Upload resume (PDF/DOCX/TXT) + paste JD → instant skill extraction with evidence levels |
| **Assessment** | Gap analysis with priority scoring: `Relevance × (1 − Evidence) × Criticality` |
| **Plan** | Weekly learning tasks + curated resources (docs, videos, practice) + project recommendations |
| **Interview** | Rubric-based mock questions (technical + behavioral) with self-evaluation scoring |
| **Tracker** | Application CRUD — company, role, URL, status, notes + response/interview/offer rates |
| **Dashboard** | Readiness score, gap distribution, application stats, quick-action cards |

### Core Design Principles

- **Deterministic core** — Taxonomy-driven normalization, explicit evidence levels (NONE/MENTIONED/DEMONSTRATED/VERIFIED), transparent priority formula. Works without any API keys.
- **Optional AI enhancement** — Pluggable LLM layer for richer extraction (OpenRouter/OpenAI via `.env`).
- **Zero hardcoded secrets** — Pydantic Settings + `.env` for all configuration.
- **Premium UI** — Dark theme with CSS variables, semantic design tokens, WCAG-compliant contrast, Lucide SVG icons.
- **Hackathon-ready** — Single-file run, no external services required for core flow.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        app.py (Streamlit)                       │
│  7 Tabs: Intake │ Assessment │ Plan │ Projects │ Interview │  │
│         Tracker  │ Dashboard                                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
    │ ResumeParser │ │ JDParser    │ │ SkillExtractor│
    │ (pypdf +     │ │ (regex +    │ │ (taxonomy +  │
    │  pdfplumber) │ │  fuzzy)     │ │  evidence)   │
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
| `domain/schemas.py` | All Pydantic models: `SkillEvidence`, `SkillGap`, `GapAnalysisResult`, `LearningResource`, `ProjectSpec`, `WeeklyPlan`, `InterviewQuestion`, `InterviewRubric`, `ApplicationRecord`, `ResumeAnalysis`, `UserProfile` |
| `domain/skill_taxonomy.py` | `SkillTaxonomy` — canonical skill catalog with aliases, categories, related skills |
| `domain/scoring.py` | Priority formula, evidence weights, gap ranking, readiness calculation |
| `services/resume_parser.py` | Multi-format parser (PDF/DOCX/TXT), LRU cache, 5MB/10-page limits |
| `services/jd_parser.py` | JD section detection (regex), skill extraction with fuzzy matching (threshold 0.85) |
| `services/skill_extractor.py` | Evidence-level inference from context, taxonomy normalization |
| `services/skill_gap_service.py` | Full analysis pipeline orchestration |
| `services/plan_generator.py` | Learning plan + project recommendations from top gaps |
| `services/interview_service.py` | Question templates by category + rubric evaluation |
| `services/tracker_service.py` | Application tracking with JSON persistence |
| `ui/theme.py` | Professional dark theme (550 lines, CSS variables, SVG icons) |
| `ui/*.py` | Tab implementations (Intake, Plan, Interview, Tracker, Dashboard) |

### Data Flow

1. **Intake** → `ResumeParser` extracts text → `SkillExtractor` finds skills with evidence
2. **JD Parse** → `JDParser` splits into sections → `SkillExtractor` maps to taxonomy
3. **Gap Analysis** → `SkillGapService` computes `matched_skills`, `missing_skills`, `gaps[]`, `readiness_score`
4. **Plan** → `LearningPlanService` generates weekly tasks + project specs from top gaps
5. **Interview** → `InterviewService` creates questions + rubrics per gap category
6. **Tracker** → `ApplicationTracker` persists applications to `data/applications.json`
7. **Dashboard** → Aggregates readiness, stats, recent activity

---

## Configuration

All settings via `.env` (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment name |
| `DEBUG` | `true` | Debug mode |
| `SECRET_KEY` | *required* | Session secret |
| `DATABASE_URL` | `sqlite:///./data/app.db` | SQLAlchemy connection |
| `OPENROUTER_API_KEY` | — | Optional AI enhancement |
| `OPENAI_API_KEY` | — | Optional AI enhancement |
| `AI_MODEL` | `anthropic/claude-3.5-sonnet` | Primary model |
| `FALLBACK_MODEL` | `openai/gpt-4o-mini` | Fallback model |
| `MAX_PDF_PAGES` | `10` | Resume page limit |
| `MAX_PDF_SIZE_MB` | `5` | Resume size limit |
| `STREAMLIT_PORT` | `8501` | Server port |

---

## Testing

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src/career_coach --cov-report=term-missing

# Current status: 30 tests passing (20 scoring + 10 taxonomy)
```

### Test Structure

```
tests/
├── conftest.py              # Fixtures: sample_resume_text, sample_jd_text
├── unit/
│   ├── test_scoring.py      # 20 tests: weights, priority, evidence, gaps, ranking, readiness
│   └── test_skill_taxonomy.py # 10 tests: loading, canonical/alias lookup, case insensitivity
└── integration/             # (planned)
```

---

## Development

### Prerequisites

- Python 3.11+ (3.12 recommended)
- `uv` or `pip` for dependency management

### Setup

```bash
# Using uv (faster)
uv pip install -e ".[dev]"

# Or pip
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format
ruff format .

# Lint
ruff check .

# Type check
mypy src/

# Pre-commit (install once)
pre-commit install
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
├── data/
│   ├── skill_taxonomy.json     # Curated skill catalog (50+ skills)
│   └── uploads/                # Temp resume uploads (gitignored)
├── internals/                  # Gitignored: build manual, research, decisions
├── src/career_coach/
│   ├── __init__.py
│   ├── config.py               # Pydantic Settings
│   ├── domain/                 # Schemas, taxonomy, scoring
│   ├── services/               # Parsers, extractors, gap analysis, plan, interview, tracker
│   └── ui/                     # Theme + 6 tab implementations
├── tests/
│   ├── conftest.py
│   └── unit/
└── .streamlit/
    └── config.toml             # Streamlit server config
```

---

## Screenshots

| Intake & Analysis | Plan & Interview |
|-------------------|------------------|
| ![Intake](docs/screenshots/intake.png) | ![Plan](docs/screenshots/plan.png) |

| Tracker & Dashboard |
|---------------------|
| ![Dashboard](docs/screenshots/dashboard.png) |

*(Add screenshots to `docs/screenshots/` after running the app)*

---

## Roadmap

- [ ] Integration tests (full pipeline with sample data)
- [ ] AI-enhanced extraction (LLM fallback when taxonomy misses skills)
- [ ] PostgreSQL support for hosted demo
- [ ] Export analysis to PDF/Markdown
- [ ] LinkedIn profile import
- [ ] Multi-user support with auth
- [ ] CI/CD pipeline (GitHub Actions)

---

## License

**AGPL-3.0** — Free for open-source use. Commercial use requires source disclosure.

See [LICENSE](LICENSE) for full text.

---

## Acknowledgments

- **OSS patterns from:** [Walid-Khalfa/resume-matcher](https://github.com/Walid-Khalfa/resume-matcher), [gerald1124-code/ai-analyze](https://github.com/gerald1124-code/ai-analyze), [najmabakdach/smart-career-matching-system](https://github.com/najmabakdach/smart-career-matching-system)
- **Icons:** [Lucide](https://lucide.dev/)
- **Built for:** Hackathon MVP — Career Pivot Coach end-to-end build
