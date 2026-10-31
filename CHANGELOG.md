# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-31

### Added
- **Core Domain Models**: Complete Pydantic schemas for skills, gaps, evidence levels, applications, and learning plans
- **Skill Taxonomy**: Curated skills across 11 categories with canonical names and aliases
- **Resume Parser**: Multi-format PDF extraction (pypdf + pdfplumber fallback) with LRU caching
- **Job Description Parser**: Section-aware parsing with regex detection and skill extraction
- **Skill Extractor**: Taxonomy-driven extraction with evidence-level inference (NONE/MENTIONED/DEMONSTRATED/VERIFIED)
- **Scoring Engine**: Priority formula `R × (1-E) × C` with transparent gap ranking and readiness scoring
- **Gap Analysis Service**: End-to-end pipeline orchestrating parsing → extraction → scoring
- **Learning Plan Generator**: Weekly task breakdown with estimated hours, resources, and project recommendations
- **Interview Prep Service**: Behavioral + technical questions with rubric-based evaluation
- **Application Tracker**: CRUD operations, status workflow, notes, and statistics (JSON file storage)
- **Streamlit UI**: 6-tab interface (Intake, Assessment, Plan, Interview, Tracker, Dashboard)
- **Professional Theme**: 550-line dark theme with CSS variables, semantic tokens, responsive layout
- **Configuration**: Pydantic Settings with .env support, zero hardcoded secrets
- **Testing**: 45 unit and integration tests covering services, app startup, and safety
- **Documentation**: README (badges, quick-start, architecture), CONTRIBUTING, ARCHITECTURE, THIRD_PARTY_NOTICES
- **CI/CD Ready**: Ruff, mypy, pytest configured in pyproject.toml

### Infrastructure
- Git repository initialized with comprehensive .gitignore (includes `internals/`)
- GitHub repository created at `github.com/Tams2411/skillroute`
- Fork workflow established (`AshayK003/skillroute`)
- Two PRs opened: #1 (features), #2 (documentation)

### Internal (gitignored)
- Build manual (78K chars) copied to `internals/BUILD_MANUAL.md`
- OSS research summary and pattern references
- Engineering memory with ADRs and component map
- Task tracker with 12-phase plan
- Decision log with 6-column table

## [Unreleased]

### Added
- GitHub Actions CI for Python 3.11/3.12, focused linting, type checking, coverage-enabled tests, and dependency auditing
- Optional Gemini interview feedback with explicit consent, session-only user keys, strict response validation, and deterministic fallback
- `uv.lock` for reproducible app and development dependency installs
- Streamlit Community Cloud setup and branch-protection guidance
- Integration coverage for analysis, learning plans, interview practice, tracker persistence, and input safety
- Upload and pasted-text limits with a 5 MB Streamlit upload cap
- HTML escaping for dynamic text rendered in custom UI components

### Changed
- Raised the supported Streamlit minimum to 1.49 for the current widget width API
- Updated the dark theme accent to match the app's cyan UI tokens
- Moved primary navigation above status/actions in the sidebar and widened the resume text editor
- Sidebar sample/reset actions now clear stale generated results safely; editing intake inputs invalidates derived analysis
- Added a visible warning that hosted tracker records are plaintext and shared by the app instance
- Configuration and documentation now reflect deterministic local analysis and plaintext JSON storage
- README, architecture, and limitations now document Gemini's data flow, key handling, provider costs, and fallback behavior
- Added the MIT license and declared the PDF/DOCX parser dependencies
- Replaced non-programmatic tabs with working sidebar page navigation and preserved intake values across pages
- Added skill-specific learning resources and merged duplicate project recommendations

### Fixed
- Report insufficient data instead of 100% coverage when no assessable JD requirements are extracted
- Improved primary button label contrast, including the disabled Analyze Skill Gaps state
- Exposed the analysis `gaps` data consumed by the plan, interview, and dashboard tabs
- Avoided logging resume filenames/content or displaying unexpected exception tracebacks
- Fixed skill-card HTML rendering and applied the CSS theme after Streamlit page setup
- Prevented multiline HTML helpers from rendering as indented code blocks
- Preserved JD section boundaries, deduplicated required/preferred skills, and corrected alias/evidence scoring
- Corrected tracker response/interview rates and aligned saved JD limits with parser limits
- Made interview questions skill-focused, distinguished behavioral rubrics, and persisted validated rubric scores
- Replaced deprecated Streamlit `use_container_width` arguments with `width="stretch"`
- Updated README, contributor guidance, architecture, and limitations for CI and demo hosting