# Limitations & Known Constraints

SkillRoute is an early local MVP. These constraints describe the current implementation, not a production-readiness claim.

## Analysis

- **Deterministic matching only:** The application uses exact skill names and taxonomy aliases. It does not call an LLM or use semantic similarity.
- **Narrow taxonomy:** The curated catalog is strongest for data, software, and engineering roles; many other occupations have limited coverage.
- **Heuristic parsing:** Resume evidence and job-description sections are inferred with text rules. Unusual layouts or wording can be missed or classified incorrectly.
- **English-focused:** The taxonomy and extraction patterns are designed for English text.
- **Heuristic scores:** Priority and weighted evidence coverage are decision-support signals, not measures of hiring probability or a validated assessment of competence. Manually entered skills are self-reported, not independently verified. Coverage is omitted when no assessable job requirements are extracted.
- **Static interview content:** Questions come from templates. Deterministic interview scoring is self-reported. Optional Gemini feedback is advisory, may be inaccurate, and is not an independently validated assessment.
- **Generic learning recommendations:** Plans and projects are template-based and may need adjustment for a user's schedule, budget, or available resources.

## Files, Storage, and Privacy

- **No authentication or access control:** Anyone who can reach the app can use it. Run locally on a trusted machine; the hosted version is an unauthenticated demo, not a private workspace.
- **Shared plaintext tracker:** Application records, notes, and saved job-description text are stored in plaintext JSON at `data/applications.json`. Users of the same running app instance share this file. It is not safe for concurrent writers and has no built-in export/import screen.
- **Hosted storage is ephemeral:** Streamlit Community Cloud may discard local files when the app restarts or rebuilds. Do not rely on it for durable tracker data.
- **User-supplied AI credentials:** Gemini keys are session-only from the app's perspective, but a hosted app operator can access server memory. The UI provides a clear-key action; keys are not stored in files or application logs.
- **Transient analysis state:** Resume/JD analysis is kept in Streamlit session state while the session is active; it is not saved as a persistent profile.
- **Resume handling:** Uploaded files are processed from a temporary file that is removed after parsing. Extracted text remains in process memory for the session.
- **Optional external AI processing:** The app's deterministic analysis does not call an AI provider. If a user enters a Gemini key, checks the consent box, and requests feedback, the interview answer, question, target role, and skill are sent through the app server to Google. Resume and JD text are not included. The app does not persist or log the key, but it resides in server-side Streamlit session memory; use this only on a host you trust. Provider terms, quota, retention, and charges are outside the app's control.
- **No deletion/export workflow for all data:** Remove tracker records in the app or delete the local JSON file; clearing the browser session does not remove tracker data.

## Parsing and Resource Limits

- **Supported resume formats:** PDF, DOCX, and TXT. Scanned/image-only PDFs are not OCR'd.
- **Configured limits:** Uploaded files are capped at 5 MB by default; PDFs are capped at 10 pages; pasted/extracted resume text is capped at 50,000 characters; job descriptions at 10,000 characters.
- **Not a parser sandbox:** Size/page limits and safe text rendering reduce risk but do not isolate third-party PDF/DOCX parser code. Keep parser dependencies updated and only process files you trust.
- **No enforced extraction timeout:** The `MAX_PDF_SIZE_MB` and `MAX_PDF_PAGES` bounds apply, but there is no separate parser timeout.

## CI, Deployment, and Accessibility

- **CI configured, deployment not provisioned:** GitHub Actions checks Python 3.11/3.12, focused lint, mypy, tests, and dependency vulnerabilities. The repository has setup instructions for Streamlit Community Cloud, but no live Cloud app has been created or validated here.
- **Demo hosting only:** After initial Cloud setup, pushes to the selected branch trigger rebuilds. There is no separate deployment workflow, managed persistence, authentication, rate limiting, or production monitoring.
- **Reproducible lockfile:** `uv.lock` pins the resolved dependency graph; update it whenever project dependencies change.
- **No load/performance benchmarks:** The app is designed for local, single-user use.
- **No formal accessibility audit:** Keyboard and screen-reader behavior have not been audited.
- **No mobile-specific validation:** The layout has not been tested across mobile devices.

## Demo Checklist

- [ ] Run the sample resume + job-description flow from intake through assessment.
- [ ] Generate a learning plan/project and an interview practice session.
- [ ] Add and update a tracker entry, then verify it survives an app restart.
- [ ] Confirm uploads over the configured size/page limits are rejected.
- [ ] Prepare screenshots or a backup recording.

The automated tests cover deterministic analysis, plan/interview generation, sidebar navigation and state resets, tracker persistence, input bounds, prompt-like text, malformed PDFs, and HTML escaping. They do not replace a full live demo rehearsal or a formal accessibility audit.
