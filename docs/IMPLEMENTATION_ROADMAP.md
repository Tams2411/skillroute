# SkillRoute implementation roadmap

This roadmap evolves the existing local-first Streamlit application in small, reviewable pull requests. Preserve working behavior, verify every claimed defect before changing it, and do not silently discard existing tracker or profile data.

## Priority matrix

Priority combines user harm, correctness, and dependency order. A P0 issue can mislead assessment output; P1 work establishes trustworthy evidence and assessment foundations; P2 work expands the development loop and persistence; P3 work measures and hardens the broader product.

| Priority | Workstream | User impact | Risk if delayed | Dependencies | PR boundary |
|---|---|---|---|---|---|
| **P0** | Stabilize assessment correctness: insufficient-data result, manual normalization, honest self-report state, confidence/provenance, JD requirement types, taxonomy distinctions. | Prevent misleading matches and scores. | Users may receive false confidence or incorrect gaps. | Existing schemas, parsers, and tests. | Separate PR for each invariant or tightly coupled pair; each adds a regression test. |
| **P1** | Evidence foundation: evidence records, source/provenance, review state, and assessment history contracts. | Make claims traceable and reviewable. | Later features would encode inaccurate evidence semantics. | P0 evidence semantics. | Additive schema PR first; preserve existing serialized records. |
| **P1** | Human-reviewed role assessment. | Users can inspect excerpts, uncertainty, mappings, and correct/reject suggestions. | Unreviewed extraction can be mistaken for user-confirmed fact. | Evidence foundation. | UI/service integration behind explicit review actions; no automatic confirmation. |
| **P2** | Personalized learning and project loop. | Turn prioritized gaps into practical, verifiable work. | Recommendations remain generic and progress does not produce evidence. | Assessment states and reviewable evidence. | Extend existing generator; add one measurable project path and tests before broad catalog expansion. |
| **P2** | Durable local persistence and data lifecycle. | Preserve profile/evidence/assessment history across sessions. | Session state and shared JSON do not provide durable, isolated profile storage. | Evidence and repository contracts. | Introduce SQLite additively, import/export/backup and deletion; switch only after migration/rollback tests. |
| **P3** | Evaluation, security, accessibility, and release validation. | Provide measured confidence and a safer demo/release process. | Accuracy and deployment limits remain unquantified. | Stable assessment and persistence behavior. | Synthetic/authorized dataset, measured metrics, threat-model review, end-to-end and deployment checks. |

## Ordered task list and acceptance gates

### Phase 0 — Stabilize correctness (P0)

- [ ] **0.1 Insufficient data:** replace the empty-requirement 100% result with an explicit insufficient-data state; UI must not display a readiness percentage for that case.
- [ ] **0.2 Manual skill normalization:** resolve canonical names, case/whitespace, and known aliases; deduplicate inputs; surface unknown skills without treating them as canonical.
- [ ] **0.3 Honest evidence levels:** keep self-reported/confirmed skills distinct from demonstrated and independently corroborated evidence; update tests that currently expect confirmation to mean `verified`.
- [ ] **0.4 Confidence and provenance:** preserve resume and JD extraction confidence/source through assessment records without conflating them with evidence strength or requirement importance.
- [ ] **0.5 JD requirement context:** represent required, preferred, and other supported contextual sections explicitly; verify exclusion of benefits and non-requirements.
- [ ] **0.6 Taxonomy distinctions:** remove aliases that merge related-but-distinct tools; add positive, negative, and ambiguous-term tests.

**Phase exit:** full tests, configured lint, type checks, and dependency audit pass; empty inputs and the sample workflow are covered; score labels accurately describe what is measured.

### Phase 1 — Evidence foundation (P1)

- [ ] **1.1 Evidence contract:** add a validated evidence record with skill, source, classification, supporting description/excerpt, provenance, review status, and timestamps.
- [ ] **1.2 Compatibility:** load current analysis/tracker records safely; do not silently upgrade existing self-reported claims or overwrite prior assessments.
- [ ] **1.3 History contract:** define append-only assessment history and explainable state transitions before persistence is switched.

**Phase exit:** domain tests cover validation, serialization, provenance, and legacy compatibility; evidence remains user-reviewable.

### Phase 2 — Human-reviewed assessment (P1)

- [ ] **2.1 Review workflow:** show extracted skill, source excerpt, uncertainty, and mapping; allow confirm, reject, correct, or add user context.
- [ ] **2.2 Separate dimensions:** expose requirement importance, extraction confidence, evidence strength, and review state as distinct values.
- [ ] **2.3 Insufficient-data UX:** render a clear explanation and next step rather than a misleading readiness value.

**Phase exit:** browser/integration tests cover review decisions and demonstrate that uncertain extraction does not become confirmed evidence on its own.

### Phase 3 — Development loop (P2)

- [ ] **3.1 Learning-task lifecycle:** extend current tasks with status, objective, rationale, effort, practical activity, deliverable, and acceptance criteria.
- [ ] **3.2 Project evidence:** completing work creates a reviewable evidence candidate; completion alone does not assert verified proficiency.
- [ ] **3.3 Curated resources:** recommend only maintained, checked catalog entries; never synthesize resource URLs.

**Phase exit:** a sample gap can be followed through a testable project deliverable to a reviewable evidence item.

### Phase 4 — Durable local persistence (P2)

- [ ] **4.1 Repository boundary:** keep domain logic independent of storage; retain the JSON tracker adapter during migration.
- [ ] **4.2 SQLite migration:** introduce schema/versioning and an explicit import path; preserve existing JSON data and offer backup/restore.
- [ ] **4.3 Data lifecycle:** test export, deletion, restart persistence, and migration rollback.
- [ ] **4.4 Deployment boundary:** do not enable shared multi-user personal data without authentication and per-user authorization/isolation.

**Phase exit:** migration/import/rollback tests pass and existing user data has a documented recovery path.

### Phase 5 — Evaluation and release validation (P3)

- [ ] **5.1 Labeled examples:** build a small synthetic or properly authorized resume/JD set with requirements, evidence, and ambiguous cases.
- [ ] **5.2 Metrics:** measure precision, recall, F1, false positives, and correction rates; document dataset limits and do not claim unmeasured performance.
- [ ] **5.3 Security and UX:** exercise file handling, XSS, secrets, AI data disclosure, deletion/isolation, accessibility, mobile layout, and complete workflows.
- [ ] **5.4 Release docs:** update README, architecture, data model, scoring, evidence, security, testing, and changelog only as the corresponding features actually ship.

**Phase exit:** CI is green; operational boundaries and known limitations are accurate; a new user can complete the main workflow with AI disabled.

## Regression controls and rollback

For every implementation PR:

1. Reproduce the behavior first and add a focused regression test before changing it.
2. Keep the diff scoped to one behavior; do not bundle unrelated refactors.
3. Run focused tests, then the full CI-equivalent checks before merge.
4. Preserve old data with additive schemas/adapters and explicit migrations; back up before any storage conversion.
5. Keep optional behavior opt-in. Use a feature switch for changes that cannot be introduced compatibly.
6. Merge only after required checks pass. If a regression appears, revert the focused PR or disable its switch; do not reset shared branches or discard user data.

## Current execution status

- [x] Establish baseline and verify the existing mainline PR.
- [x] Audit the six Phase 0 correctness areas and record code/test evidence in `IMPLEMENTATION_AUDIT.md`.
- [x] Open the audit/roadmap PR.
- [ ] Start Phase 0.1 as the first correctness PR after the roadmap is reviewable.
- [ ] Continue one scoped PR per Phase 0 invariant, then proceed through later phases only after each exit gate passes.

## Baseline

At audit commit `06f29bf`, the full suite had 78 passing tests and 79% statement coverage; CI-configured Ruff, mypy, Python compilation, and dependency auditing passed. These checks are a starting point, not a guarantee of zero regressions or product accuracy.
