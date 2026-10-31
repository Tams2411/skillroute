# SkillRoute implementation audit

**Audit baseline:** `06f29bf` (2026-10-31)
**Scope:** Current repository compared with the SkillRoute 2.0 proposal. This is a staged implementation audit, not a production-readiness certification.

## Current implementation

SkillRoute is a local-first Streamlit modular monolith. It already has:

- A Pydantic domain model and deterministic resume/JD analysis pipeline.
- Exact and alias-based skill matching with evidence-level heuristics.
- Explainable gap records and a template-based weekly learning plan.
- Interview question generation, rubric self-evaluation, and optional consent-based Gemini feedback.
- A JSON-backed application tracker and six-page Streamlit interface.
- CI for Python 3.11/3.12, focused Ruff checks, mypy, pytest, and dependency auditing.

The current application is useful as a single-user/local demo. It does not have authenticated profiles, durable analysis history, user-isolated storage, or a full evidence portfolio. The existing JSON tracker is shared by users of one app instance and is not suitable for concurrent multi-user persistence.

## Baseline verification

Checks were run against the audited baseline:

| Check | Result |
|---|---|
| Full pytest suite with coverage | 78 passed; 79% statement coverage |
| CI-configured Ruff selection | Passed |
| mypy | Passed (21 source files) |
| Dependency audit | No known vulnerabilities reported |
| Python compilation | Passed |

These are regression gates, not proof that every feature is correct. The current CI does not enforce a minimum coverage threshold or measure extraction quality against a labeled dataset.

## Findings and priority

| Priority | Finding | Evidence in current code | User impact | Safest first action |
|---|---|---|---|---|
| P0 | Empty extracted JD requirements produce a 100% readiness result. | `src/career_coach/domain/scoring.py:112-122`; service exposes the result in `src/career_coach/services/skill_gap_service.py:136-137`; `tests/unit/test_scoring.py:191-213` expects 100%. | Reports apparent success when no requirements were assessed. | Return an explicit insufficient-data state and cover empty/irrelevant JD input with regression tests. |
| P0 | User-confirmed skills are promoted to `verified`. | `src/career_coach/services/skill_gap_service.py:73-93`; confirmation behavior is asserted in `tests/integration/test_analysis_workflow.py` and `tests/unit/test_skill_extractor.py`. | Self-report can be mistaken for independently supported proficiency and inflate evidence coverage. | Preserve the claim as self-reported/confirmed, separate from demonstrated or corroborated evidence. |
| P0 | Manually entered skills are not consistently resolved through the canonical taxonomy. | Input enters through `src/career_coach/ui/intake.py:108-138`; raw values are used in `src/career_coach/services/skill_gap_service.py:73-94`; taxonomy resolution is separate in `src/career_coach/domain/skill_taxonomy.py:20-31`. | Aliases can miss matches, while unknown input may be treated as a canonical skill. | Normalize known aliases, deduplicate, and return explicit feedback for unknown entries. |
| P1 | Resume extraction confidence/source is lost during conversion to assessment evidence. | `src/career_coach/services/skill_extractor.py:10-18,55-71`; `src/career_coach/domain/schemas.py:39-50`; conversion in `src/career_coach/services/skill_gap_service.py:97-105`. JD confidence does affect priority, but provenance is not consistently carried through. | Users cannot distinguish extraction uncertainty from evidence strength. | Add provenance/confidence fields compatibly and test end-to-end preservation before changing scoring. |
| P1 | JD section handling is partial. Required/preferred sections are distinguished, but other contextual sections are not comprehensively represented as requirement types. | `src/career_coach/services/jd_parser.py:13-21,118-147,207-243`; existing parser tests cover section boundaries, required/preferred distinctions, deduplication, and benefits exclusion. | Requirements can be missed or have importance that does not reflect their context. | Extend section/type coverage only with fixtures and explicit weighting tests. |
| P1 | Some aliases collapse related but distinct tools/concepts. | Examples in `src/career_coach/domain/skill_taxonomy.py:64,72,92-98`; tests cover resolution and short-alias filtering but not all distinctions. | A match for one technology may be misrepresented as evidence for another. | Split canonical concepts and retain only true synonyms, with ambiguity/false-positive tests. |
| P2 | Evidence records, user review, and historical assessments are not first-class workflows. | Current schemas and session-backed analysis do not provide durable evidence-review history; see `ARCHITECTURE.md` and `LIMITATIONS.md`. | Users cannot reliably inspect how assessments change as they add evidence. | Introduce an additive evidence model and review states before wiring persistence or automatic state changes. |
| P2 | Durable profile, plan, and evidence storage is absent. | `src/career_coach/services/tracker_service.py` stores applications in a process-wide JSON tracker; analysis is held in Streamlit session state. | Data is not user-isolated or reliably durable on hosted instances. | Keep the local demo mode; design a repository boundary and a reversible SQLite migration before switching storage. |
| P3 | Extraction quality is not measured on a labeled evaluation set. | The test suite is deterministic but has no `tests/evaluation/` dataset or precision/recall/F1 reporting. | Accuracy claims cannot be quantified across role families. | Build a synthetic or authorized dataset and report measured results with limitations. |

### Verified strengths to preserve

- The existing modular monolith and deterministic scoring pipeline are a suitable foundation; a rewrite or microservices are not justified.
- Required/preferred JD boundaries, duplicate requirements, evidence-context assessment, and short ambiguous aliases already have regression coverage.
- User-uploaded files have size/type limits and temporary files are cleaned up.
- Gemini is an isolated optional adapter, requires explicit consent/request, and does not decide core skill scores.
- Streamlit page navigation and the sample analysis/plan/interview flows have integration coverage.

## Audit limits

This audit verifies the listed code paths and current test/architecture descriptions. It does not certify external hosting, parser sandboxing, production multi-user isolation, hiring outcomes, or the accuracy of the heuristic scoring model. Each item must be rechecked against implementation and tests when its PR is built.
