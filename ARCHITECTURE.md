# SkillRoute Architecture

> **Version:** 0.1.0
> **Status:** Local-first MVP; optional hosted demo
> **Last updated:** 2026-10-31

## Overview

SkillRoute is a local-first Streamlit application organized as a modular Python package. It has no public API, database service, authentication, or active AI-provider integration. Analysis is deterministic and runs in the app process. Streamlit Community Cloud can host an unauthenticated demo, but it does not make the app a private or persistent multi-user service.

```text
app.py (six sidebar-navigated pages)
  ├─ Intake → ResumeParser + JDParser + SkillExtractor
  │             └─ SkillGapService → ranked gap data
  ├─ Assessment → explainable gap and evidence display
  ├─ Plan → learning tasks and project recommendations
  ├─ Interview → static questions and self-evaluation rubric
  ├─ Tracker → ApplicationTracker → data/applications.json (shared plaintext file)
  └─ Dashboard → analysis summary + tracker statistics
```

## Modules

| Module | Responsibility |
|---|---|
| `domain/schemas.py` | Pydantic contracts for evidence, gaps, tasks, interviews, and applications |
| `domain/skill_taxonomy.py` | Canonical skills and aliases used by extraction |
| `domain/scoring.py` | Evidence weights, gap priority, ranking, and readiness calculation |
| `services/resume_parser.py` | PDF, DOCX, and TXT extraction; PDF fallback; upload size/page checks |
| `services/jd_parser.py` | Job-description section detection and exact taxonomy/alias matching |
| `services/skill_extractor.py` | Skill matching and evidence-level inference |
| `services/skill_gap_service.py` | Parsing/extraction/scoring orchestration |
| `services/plan_generator.py` | Template-based learning tasks and project recommendations |
| `services/interview_service.py` | Static question selection and rubric evaluation |
| `services/tracker_service.py` | Local JSON-backed application CRUD and statistics |
| `ui/*.py` | Intake, assessment, plan, interview, tracker, dashboard, navigation, and shared state |

## Analysis Contract

`SkillGapService.analyze()` returns a dictionary containing:

- `gaps`, `all_gaps`, `top_gaps`, and `actionable_gaps` as serialized skill-gap records
- `matched_skills` and `missing_skills`
- `readiness_score` (0–1) and `readiness_percentage`
- extraction counts and metadata

The Plan and Interview pages validate serialized gap records back into `SkillGap` models before passing them to their services.

### Priority and readiness

```text
priority = role_relevance × (1 − evidence_strength) × extraction_confidence
```

JD importance informs role relevance. Evidence weights are configured as:

| Evidence level | Weight |
|---|---:|
| NONE | 0.0 |
| MENTIONED | 0.2 |
| DEMONSTRATED | 0.4 |
| VERIFIED | 0.9 |

Readiness is a weighted evidence-coverage heuristic. Neither score predicts hiring outcomes or establishes proficiency.

## Persistence and Data Flow

| Data | Storage |
|---|---|
| Skill taxonomy | `data/skill_taxonomy.json` |
| Application records and tracker notes/JD text | `data/applications.json` |
| Current analysis and practice state | Streamlit session memory |
| Uploaded resume during parsing | Temporary file, removed after parsing |

There is no SQL database configured or used. Resume/JD analysis is not persisted as a profile, and the current application workflow makes no external AI requests.

On Streamlit Community Cloud, the JSON tracker remains shared by the app instance and local filesystem persistence is not guaranteed. The app has no authentication, so hosted use is demonstration-only and must not contain sensitive data.

## Configuration and Input Limits

Pydantic Settings reads optional values from `.env`. Defaults include:

- Uploaded resume file: 5 MB maximum; PDF: 10 pages maximum
- Pasted/extracted resume: 50,000 characters maximum
- Job description: 10,000 characters maximum
- Evidence weights: listed above

Streamlit's upload cap is configured to 5 MB in `.streamlit/config.toml`. No separate PDF extraction timeout is implemented.

## Safety Boundaries

- Resume format is restricted to PDF, DOCX, or TXT; file size and PDF page count are bounded.
- Unexpected analysis errors are shown without stack traces; parser logs omit resume filenames and contents.
- Dynamic text interpolated into custom HTML components is HTML-escaped.
- Uploaded files are processed locally and the temporary file is cleaned up after parsing.
- The app has no authentication or rate limiting. Bind it to localhost and do not expose it to untrusted users or networks.
- Tracker JSON is plaintext, shared by app users, and does not provide concurrency locking.

These controls do not sandbox PDF/DOCX parsers. Keep dependencies current and process only files you trust.

## Verification

Run the locked CI checks from the repository root:

```bash
uv sync --extra dev --locked
uv run ruff check --select E4,E7,E9,F src/ tests/
uv run mypy src/
uv run pytest -q --cov=src/career_coach --cov-report=term-missing
uv run pip-audit --progress-spinner off --skip-editable
```

GitHub Actions runs these checks across Python 3.11 and 3.12. Streamlit AppTests cover sample analysis, plans/interviews, sidebar navigation, input state, safety limits, HTML escaping, and tracker persistence; there is no full browser E2E suite.

## Planned Evolution

Hosted persistence, authentication, semantic matching, AI-assisted analysis, and production monitoring are not part of the current MVP. Add them only with explicit data-flow, privacy, and deployment requirements.
