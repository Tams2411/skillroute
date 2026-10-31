# Contributing to SkillRoute

Thank you for your interest in contributing! This guide covers the development workflow, code style, and PR process.

## Development Setup

```bash
# 1. Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/skillroute.git
cd skillroute

# 2. Install the locked runtime and development dependencies
uv sync --extra dev --locked

# 3. Install pre-commit hooks
uv run pre-commit install

# 4. Verify setup with the CI checks
uv run pytest -q
uv run ruff check --select E4,E7,E9,F src/ tests/
uv run mypy src/
uv run pip-audit --progress-spinner off --skip-editable
```

## Code Style

### Python

- **Formatter:** `ruff format` (Black-compatible)
- **Linter:** `ruff check` (flake8 + isort + more)
- **Type checker:** `mypy src/` using the project configuration
- **Line length:** 100 characters
- **Target:** Python 3.11+

### Conventions

- Type hints on all public functions
- Pydantic models for all data structures
- Docstrings: Google style for modules/classes, one-liner for simple functions
- No `print()` in library code — use standard logging without resume or JD content

### Commit Messages

Follow Conventional Commits:

```
feat: add interview rubric self-evaluation
fix: handle empty JD sections in parser
docs: update README with architecture diagram
test: add edge cases for evidence weight zero
refactor: extract skill matching to separate function
```

**Never** include internal tooling references (ponytail, karpathy, aeos, hermes, vibe coding, etc.) in commit messages or code comments.

## Pull Request Workflow

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make changes** with tests:
   - Add tests for new functionality
   - Ensure all existing tests pass
   - Run the focused Ruff check, `mypy src/`, and `pip-audit` before pushing

3. **Push and open PR** against `AshayK003/skillroute:main`:
   - Fill the PR template
   - Link related issues
   - Screenshots for UI changes

4. **Review process**:
   - CI must pass (Python 3.11/3.12 tests, lint, type check, dependency audit)
   - At least one approval required
   - Maintainer merges (squash preferred)

## Testing

### Tests

```bash
# Run unit and integration tests
uv run pytest -q

# Specific module
uv run pytest tests/unit/test_scoring.py -v

# With coverage
uv run pytest tests/unit/ --cov=src/career_coach --cov-report=term-missing
```

### Test Guidelines

- Place tests in `tests/unit/` mirroring `src/` structure
- Use `conftest.py` fixtures (`sample_resume_text`, `sample_jd_text`)
- Test edge cases: empty input, boundary values, invalid enums
- Mock external calls (LLM APIs, file I/O)

## Project Structure

```
skillroute/
├── app.py                      # Streamlit entry point
├── pyproject.toml              # Project config, deps, tool settings
├── .env.example                # Environment template
├── .gitignore
├── README.md
├── CONTRIBUTING.md             # This file
├── ARCHITECTURE.md
├── data/
│   ├── skill_taxonomy.json     # Curated skill catalog
│   └── uploads/                # Temp uploads (gitignored)
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
    └── config.toml
```

## Adding Skills to the Taxonomy

Add the canonical skill and aliases to `DEFAULT_TAXONOMY` in `src/career_coach/domain/skill_taxonomy.py`. `data/skill_taxonomy.json` is a legacy snapshot and is not loaded by default.

```json
{
  "canonical": "New Skill Name",
  "aliases": ["alias1", "alias2"],
  "category": "programming",
  "related": ["Related Skill 1", "Related Skill 2"]
}
```

Add or update taxonomy/extraction tests, then run `uv run pytest tests/unit/test_skill_taxonomy.py tests/unit/test_skill_extractor.py -v`.

## Adding a Page

1. Create `src/career_coach/ui/new_page.py` with a `render_new_page()` function
2. Add the page label to `NAVIGATION_ITEMS` and route it in `app.py`
3. Add theme helpers to `ui/theme.py` if needed
4. Add coverage in `tests/integration/test_streamlit_app.py`

## CI and Dependency Updates

The GitHub Actions workflow is `.github/workflows/ci.yml`. It tests Python 3.11 and 3.12, runs lint/type checks and tests, then audits dependencies. When changing dependencies, update `pyproject.toml` and regenerate the lockfile with `uv lock --python 3.12`; verify with `uv lock --check` and `uv sync --extra dev --locked`.

## Reporting Issues

- **Bug:** Use bug report template — include steps to reproduce, expected vs actual, environment
- **Feature:** Use feature request template — describe use case, proposed solution, alternatives
- **Security:** Email maintainers directly — do not open public issue

## License

By contributing, you agree your contributions will be licensed under **MIT** (same as the project).
