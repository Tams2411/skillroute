# SkillRoute Architecture

> **Version:** 0.1.0
> **Status:** Local-first MVP; optional hosted demo
> **Last updated:** 2026-10-31

## Overview

SkillRoute is a local-first Streamlit application organized as a modular Python package. It has no public API, database service, or authentication. Core analysis is deterministic and runs in the app process. An optional Gemini adapter provides advisory interview feedback only after a user supplies a key, consents to sharing the answer, and requests feedback. Streamlit Community Cloud can host an unauthenticated demo, but it does not make the app a private or persistent multi-user service.

```text
app.py (six sidebar-navigated pages)
  ├─ Intake → ResumeParser + JDParser + SkillExtractor
  │             └─ SkillGapService → ranked gap data
  ├─ Assessment → explainable gap and evidence display
  ├─ Plan → learning tasks and project recommendations
  ├─ Interview → static questions and deterministic self-evaluation
  │               └─ explicit user request → Gemini advisory feedback
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
| `services/gemini_interview_service.py` | Optional Gemini request, timeout/size bounds, and strict response validation |
| `services/tracker_service.py` | Local JSON-backed application CRUD and statistics |
| `ui/*.py` | Intake, assessment, plan, interview, tracker, dashboard, navigation, and shared state |

## Analysis Contract

`SkillGapService.analyze()` returns a dictionary containing:

- `gaps`, `all_gaps`, `top_gaps`, and `actionable_gaps` as serialized skill-gap records
- `matched_skills` and `missing_skills`
- `unrecognized_user_skills` for manually entered skills excluded from analysis
- `readiness_state` (`available` or `insufficient_data`)
- `readiness_score` (0–1) and `readiness_percentage`, both `null` when state is `insufficient_data`
- extraction counts and metadata

The Plan and Interview pages validate serialized gap records back into `SkillGap` models before passing them to their services.

### Priority and evidence coverage

```text
priority = role_relevance × (1 − evidence_strength) × extraction_confidence
```

JD importance informs role relevance. Evidence weights are configured as:

| Evidence level | Weight |
|---|---:|
| NONE | 0.0 |
| MENTIONED | 0.2 |
| SELF_REPORTED | 0.3 |
| DEMONSTRATED | 0.4 |
| VERIFIED | 0.9 |

Manually entered skills are normalized through the taxonomy. Recognized claims use the `SELF_REPORTED` level unless resume evidence is stronger; unknown entries are excluded and returned for UI feedback. A self-report is not represented as independently verified evidence.

Weighted evidence coverage is a heuristic summary of evidence against extracted requirements. If no requirements with positive total importance are extracted, the state is `insufficient_data` and no score or percentage is returned. The UI shows an explanatory message instead of presenting a perfect score or claiming the user is prepared. This metric does not predict hiring outcomes or establish proficiency.

Resume evidence records preserve their source and extraction confidence separately from evidence strength. Extraction confidence describes the system's certainty that it found a skill mention; it does not verify the user's proficiency and does not change the evidence weight or readiness calculation.

## Persistence and Data Flow

| Data | Storage |
|---|---|
| Skill taxonomy | `data/skill_taxonomy.json` |
| Application records and tracker notes/JD text | `data/applications.json` |
| Current analysis, practice state, and user-entered Gemini key | Streamlit session memory |
| Uploaded resume during parsing | Temporary file, removed after parsing |

There is no SQL database configured or used. Resume/JD analysis is not persisted as a profile. No AI request occurs unless the user enters a Gemini key, checks the consent box, and explicitly requests feedback. Only the interview answer, question, target role, and skill are sent; resume/JD text is excluded. The key is sent to the app server and held in session memory, not written to files or logged; a hosted server operator can access its process memory. API requests use an HTTPS header, a 30-second timeout, and bounded response reads. Provider errors are surfaced while deterministic self-evaluation remains usable.

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
- Optional Gemini feedback never changes core analysis or saved self-evaluation scores; model output is schema-validated and displayed as advisory.
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

Hosted persistence, authentication, semantic matching, AI-assisted resume/JD analysis, and production monitoring are not part of the current MVP. Add them only with explicit data-flow, privacy, and deployment requirements.
