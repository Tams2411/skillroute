# Contributing to SkillRoute

Thank you for your interest in contributing! This guide covers the development workflow, code style, and PR process.

## Development Setup

```bash
# 1. Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/skillroute.git
cd skillroute

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install with dev dependencies
pip install -e ".[dev]"

# 4. Install pre-commit hooks
pre-commit install

# 5. Verify setup
pytest tests/unit/ -v
ruff check .
mypy src/
```

## Code Style

### Python

- **Formatter:** `ruff format` (Black-compatible)
- **Linter:** `ruff check` (flake8 + isort + more)
- **Type checker:** `mypy --strict` on `src/` (9 modules strict, rest with `ignore_errors`)
- **Line length:** 100 characters
- **Target:** Python 3.11+

### Conventions

- Type hints on all public functions
- Pydantic models for all data structures
- Docstrings: Google style for modules/classes, one-liner for simple functions
- No `print()` in library code — use `structlog` (configured in services)

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
   - Run `ruff check . && mypy src/` before pushing

3. **Push and open PR** against `Tams2411/skillroute:main`:
   - Fill the PR template
   - Link related issues
   - Screenshots for UI changes

4. **Review process**:
   - CI must pass (tests, lint, type check)
   - At least one approval required
   - Maintainer merges (squash preferred)

## Testing

### Unit Tests

```bash
# Run all
pytest tests/unit/ -v

# Specific module
pytest tests/unit/test_scoring.py -v

# With coverage
pytest tests/unit/ --cov=src/career_coach --cov-report=term-missing
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
│   └── ui/                     # Theme + 6 tab implementations
├── tests/
│   ├── conftest.py
│   └── unit/
└── .streamlit/
    └── config.toml
```

## Adding New Skills to Taxonomy

Edit `data/skill_taxonomy.json`:

```json
{
  "canonical": "New Skill Name",
  "aliases": ["alias1", "alias2"],
  "category": "programming",
  "related": ["Related Skill 1", "Related Skill 2"]
}
```

Run tests to verify: `pytest tests/unit/test_skill_taxonomy.py -v`

## Adding New Tab

1. Create `src/career_coach/ui/new_tab.py` with `render_new_tab()` function
2. Import and add to `app.py` tabs list
3. Add theme helpers to `ui/theme.py` if needed
4. Write tests in `tests/unit/test_new_tab.py`

## Reporting Issues

- **Bug:** Use bug report template — include steps to reproduce, expected vs actual, environment
- **Feature:** Use feature request template — describe use case, proposed solution, alternatives
- **Security:** Email maintainers directly — do not open public issue

## License

By contributing, you agree your contributions will be licensed under **AGPL-3.0** (same as the project).
