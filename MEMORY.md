# MEMORY — Agent Boot Notebook

| Field | Value |
|---|---|
| Document version | 1.4.0 |
| Updated by | Every agent, after every commit |
| Read by | Every agent, before every task |
| Conforms to | PRD.md v1.0.0, ARCHITECTURE.md v1.0.1, INSTRUCTIONS.md v1.0.0 |

This file is the project's persistent memory. It is the first file an agent reads and the last file an agent writes.

**Rules for this file:**
- Append-only for the history sections (`Verified Implementations`, `Test Failures`, `Schema Changes`, `Decisions Log`).
- `Active Roadblocks` is the only section where entries may be removed, and only when resolved and moved to `Resolved Roadblocks`.
- `Current State` is overwritten each commit.
- No prose without a date and an author identifier (`agent:<task-id>` or `human:<initials>`).

---

## 1. Current State Snapshot (overwritten each commit)

| Field | Value |
|---|---|
| Current phase | P4.7-fix-4 (prompt canonical check_id enumeration) |
| Last completed milestone | P3 Milestone M3 (Retrieval Evaluation v2 - All Targets Met) |
| Active branch | `main` |
| Last green commit | 155740b |
| Unit test count | 80 |
| Integration test count | 18 |
| Skills at `eval_status: active` | 0 |
| Skills at `eval_status: evaluating` | 4 |
| Skills at `eval_status: draft` | 4 |
| Known failing tests | 0 |
| Open roadblocks | 0 |
| Frozen invariants intact | yes |

**Environment (recorded at P0 preflight 2026-11-04):**

| Component | Required | Actual | Status |
|---|---|---|---|
| Python | 3.11.x | 3.11.18 (uv-managed) | PASS |
| uv | 0.5.x | 0.13.7 (on PATH) | PASS |
| MySQL | 8.0.x (D-011) | 8.0.39 (on PATH) | PASS |
| Ollama | ≥ 0.3 | 0.40.13 | PASS |
| qwen3:4b | present | present (`359d7dd4bcda`) | PASS |
| Git | clean tree | main | PASS |

**Frozen invariant checklist (verified each commit):**
- [x] Evidence verifier thresholds unchanged (`prefix_len=40`, `fuzzy_threshold=0.92`)
- [x] Capability gate has no model/vector call
- [x] Model tag is `qwen3:4b`, `model_digest` recorded
- [x] `k = 3` default in `Settings`
- [x] Disagreement not averaged in dashboard
- [x] `unsupported_evidence` not shown as findings
- [x] `audit_log` append-only grant intact
- [x] No cloud call in `tests/integration/test_offline.py`

---

## 2. Verified Implementations

### [2026-11-07] Phase P2-code Implementation (Tasks 1..11, Stopping Point 1)
- Verified by: `agent:p2-code`
- Commits: a47788f, 2eef891, 23b36c2, f40b82e, 871e625, 865b9d5, 42c9447, 34ade35, f1c86a7, fb4a174
- Tests: `tests/unit/test_check_source_tag.py`, `tests/unit/test_labels_schema.py`, `tests/unit/test_insufficient_sample.py`, `tests/unit/test_pre_post_metrics.py`, `tests/unit/test_reviewer_feedback.py`, `tests/unit/test_labels_bootstrap.py`, `tests/integration/test_metrics_readonly.py`
- Behaviour:
  - D-018..D-020: Enacted pre/post verifier precision/recall definitions, check_source tag (`deterministic` vs `model`), and metrics dashboard layout.
  - US-20: Alembic migrations 0003 & 0004 backfilled and migrated `checklist_verdicts.check_source`, tagged across all 12 deterministic checks and model check extractions.
  - docs: Created comprehensive `docs/annotation_guideline.md` v1.0 with 12-column schema, positive & negative worked examples for all 4 capabilities, ambiguity rule (default to not_applicable/no_flag, never flag), inter-annotator procedure, and Modes A & B.
  - US-35: Created `data/labels/TEMPLATE.csv`, `README.md`, and `sample_5.csv`.
  - US-01..US-03: Built 60 evaluation submissions (20 prose, 20 code, 20 mixed with CiteMe correct/corrupted/fabricated DOIs and 5 HALLMARK adversarial prompts) and ingested into MySQL.
  - US-35: Implemented `src/compliance_review/metrics/compute.py` with pre/post verifier split, confusion matrices, consistency metrics, and `< 10` gold items insufficient-sample guard.
  - US-35: Added `compliance-review metrics --labels PATH --out PATH` exporting JSON and CSV.
  - US-31/32: Added `compliance-review reviewer feedback` with atomic audit logging via `record_reviewer_feedback`.
  - US-35: Proved read-only contract for metrics via `test_metrics_readonly.py`.
  - Batch Review & Bootstrap: Reviewed all 60 corpus submissions under k=3 with `--skill-status evaluating`, recorded state in `data/labels/CORPUS_STATE.json`, added `compliance-review labels bootstrap`, and exported 650 provisional labels to `data/labels/provisional_v1.csv` for Mode B human audit.
- Depends on: P1 & P1.5 harness, verifier, schemas, and DB.
- Supersedes: none

### [2026-11-06] src/compliance_review/ - P1.5 Evidence Quality Investigation & Prompt/Grounding Refinements
- Verified by: `agent:p1.5`
- Commits: 8170240, 6ab0997, d88e5fd, cacf2b4, f6003bf
- Tests: `tests/integration/test_evidence_gate_pilot.py`, `scripts/generate_pilot_report.py`
- Behaviour: Grounded deterministic check evidence spans to exact source lines/headings; eliminated schema errors with prompt constraints and mandatory confidence; verified 100% acceptance on pilot_issue_doi and pilot_issue_code; eliminated false positives on pilot_clean_prose and pilot_clean_mixed (0 flags); raised real-defect pilot acceptance rate from 27.0% to 80.0% while keeping verifier thresholds frozen.
- Depends on: `src/compliance_review/checks/deterministic/`, `src/compliance_review/model/prompts.py`, `skills/*/v2/SKILL.md`.
- Supersedes: none

### [2026-11-04] src/compliance_review/ingestion/ — US-01, US-02, US-03, US-04, US-05
- Verified by: `agent:p0`
- Commit: aaf052c
- Tests: `tests/integration/test_ingest_deterministic.py`
- Behaviour: Ingests prose (md, pdf, docx), code repos, and mixed submissions; rejects duplicates by external_id; computes SHA256.
- Depends on: `src/compliance_review/ingestion/`, `src/compliance_review/db/repository.py`, MySQL `submissions` table.
- Supersedes: none

### [2026-11-04] src/compliance_review/skills/ — US-06, US-07
- Verified by: `agent:p0`
- Commit: aaf052c
- Tests: `tests/unit/test_schema_validation.py`, CLI `compliance-review skills validate --root skills/`
- Behaviour: Validates and loads YAML frontmatter and Markdown bodies for 4 seed skills conforming to SkillDefinition.
- Depends on: `src/compliance_review/skills/schema.py`, `skills/`.
- Supersedes: none

### [2026-11-04] src/compliance_review/retrieval/capability_gate.py — US-13
- Verified by: `agent:p0`
- Commit: aaf052c
- Tests: `tests/unit/test_gate_purity.py`
- Behaviour: Deterministically routes submission type and surface features to required capabilities without model or vector calls.
- Depends on: pure python, standard library only.
- Supersedes: none

### [2026-11-04] src/compliance_review/evidence/verifier.py — US-23
- Verified by: `agent:p0`
- Commit: aaf052c
- Tests: `tests/unit/test_verifier_invariant.py`
- Behaviour: Normalizes spans with NFKC and whitespace collapsing; verifies exact prefix and fuzzy matches against frozen thresholds (40, 0.92).
- Depends on: standard library `unicodedata`, `difflib`.
- Supersedes: none

### [2026-11-04] src/compliance_review/harness/orchestrator.py — D-009
- Verified by: `agent:p0`
- Commit: aaf052c
- Tests: `tests/integration/test_ingest_deterministic.py`, CLI `compliance-review review --deterministic-only`
- Behaviour: Executes deterministic checks on enabled capabilities and outputs structured trace table.
- Depends on: `src/compliance_review/checks/deterministic/`, `src/compliance_review/db/repository.py`.
- Supersedes: none

### [2026-11-05] src/compliance_review/skills/loader.py, cli.py — US-08
- Verified by: `agent:p1`
- Commit: f809e0a
- Tests: `tests/unit/test_skill_status.py`
- Behaviour: Provides set_skill_status to transition eval_status in SKILL.md; adds CLI command `skills set-status` and `--skill-status` filter to `review`.
- Depends on: `src/compliance_review/skills/loader.py`, `src/compliance_review/cli.py`.
- Supersedes: none

### [2026-11-05] skills/ — US-06, US-07, US-08
- Verified by: `agent:p1`
- Commit: 0591391
- Tests: `tests/unit/test_schema_validation.py`, `compliance-review skills validate --root skills/`
- Behaviour: Authored 4 v2 skills with 2 model items each and location grammar evidence requirements; set status to evaluating via `skills set-status`.
- Depends on: `src/compliance_review/skills/schema.py`, `src/compliance_review/skills/loader.py`.
- Supersedes: none

### [2026-11-05] src/compliance_review/retrieval/ — US-14, US-15, US-16
- Verified by: `agent:p1`
- Commit: a79550f
- Tests: `tests/unit/test_retrieval_index.py`, CLI `compliance-review index rebuild`
- Behaviour: Builds FAISS IndexFlatIP cosine index on L2-normalized sentence embeddings of skill metadata; implements version selection and NoActiveSkillError per ARCHITECTURE.md §6.3.
- Depends on: `sentence-transformers`, `faiss-cpu`, `src/compliance_review/retrieval/vector_index.py`, `src/compliance_review/retrieval/selector.py`.
- Supersedes: none

### [2026-11-05] src/compliance_review/model/ — US-19, US-21, US-23
- Verified by: `agent:p1`
- Commit: 2bbbd54
- Tests: `tests/unit/test_model_digest.py`, `tests/unit/test_schema_retry.py`
- Behaviour: Implements Ollama Qwen3:4b client with frozen sampling parameters (temp=0.0, top_p=1.0, seed=run_index, num_predict=2048, format=json); resolves model_digest or strictly refuses execution; centralizes prompts; enforces ModelOutput schema validation with exactly one retry on failure.
- Depends on: `ollama`, `src/compliance_review/model/`.
- Supersedes: none

### [2026-11-05] src/compliance_review/checks/model_based/ — US-20
- Verified by: `agent:p1`
- Commit: ad5771e
- Tests: `tests/unit/test_model_checks.py`
- Behaviour: Implements model-based checklist evaluation for citation integrity, report structure, code quality, and Responsible-AI disclosure with schema retry integration.
- Depends on: `src/compliance_review/model/`, `src/compliance_review/checks/model_based/`.
- Supersedes: none

### [2026-11-05] src/compliance_review/harness/severity_cap.py — US-22
- Verified by: `agent:p1`
- Commit: 290a88c
- Tests: `tests/unit/test_severity_cap.py`
- Behaviour: Enforces severity cap restricting {high, critical} to flag verdicts on deterministic items or model items with >= 2 of k runs in agreement; caps unverified severities to medium.
- Depends on: `src/compliance_review/harness/severity_cap.py`.
- Supersedes: none

### [2026-11-05] src/compliance_review/evidence/verifier.py — US-24, US-25, US-26
- Verified by: `agent:p1`
- Commit: bdf9bce
- Tests: `tests/unit/test_verifier_invariant.py`, `tests/unit/test_evidence_downgrade.py`
- Behaviour: Validates evidence location grammar and resolves source spans; verifies exact substrings, 40-character prefixes, and difflib SequenceMatcher >= 0.92; returns EvidenceResult with verified boolean and method.
- Depends on: `src/compliance_review/evidence/verifier.py`.
- Supersedes: none

### [2026-11-05] src/compliance_review/harness/ — US-19, US-24, US-25, US-28
- Verified by: `agent:p1`
- Commit: 8465de5
- Tests: `tests/unit/test_k_agreement.py`
- Behaviour: Implements k-run harness with per-check verdict agreement and evidence Jaccard metrics; connects orchestrator pipeline (gate -> FAISS selector -> deterministic & model checks -> evidence verification -> downgrade unsupported flags to unsupported_evidence -> severity cap -> DB persistence); wires CLI `compliance-review review`.
- Depends on: `src/compliance_review/harness/`, `src/compliance_review/db/repository.py`, `src/compliance_review/evidence/verifier.py`.
- Supersedes: none

### [2026-11-05] tests/integration/test_evidence_gate_pilot.py — US-19..US-28
- Verified by: `agent:p1`
- Commit: 54fc898
- Tests: `tests/integration/test_evidence_gate_pilot.py`
- Behaviour: Validates all 4 P1 evidence gate conditions across 10 pilot submissions: (a) every flag verdict has verified=True; (b) >= 1 pilot produces >= 1 unsupported_evidence row; (c) k=3 executions per (pilot, capability); (d) every execution has non-null model_digest. Configures `think=False` via client `_request_stream` to prevent reasoning token budget exhaustion.
- Depends on: `src/compliance_review/harness/`, `src/compliance_review/evidence/verifier.py`, `src/compliance_review/model/`.
- Supersedes: none

### [2026-11-07] data/labels/eval_v1_report.md — US-35
- Verified by: `agent:p2-eval`
- Commit: c18fe11
- Tests: `tests/integration/test_metrics_readonly.py`, `tests/unit/test_pre_post_metrics.py`, `tests/unit/test_insufficient_sample.py`
- Behaviour: Computed P2-eval metrics against initial `data/labels/gold_labels.csv` (75 audited check instances across 15 submissions). Generated `data/labels/eval_v1.json`, `data/labels/eval_v1.csv`, and comprehensive report `data/labels/eval_v1_report.md`.
- Depends on: `src/compliance_review/metrics/compute.py`, `src/compliance_review/cli.py`, `data/labels/gold_labels.csv`.
- Supersedes: none

### [2026-11-07] data/labels/eval_v2_report.md — US-35
- Verified by: `agent:p2-eval`
- Commit: e8be242
- Tests: `tests/integration/test_metrics_readonly.py`, `tests/unit/test_pre_post_metrics.py`, `tests/unit/test_insufficient_sample.py`
- Behaviour: Computed P2-eval metrics against audit-corrected `data/labels/gold_labels.csv` (75 audited check instances, 20 gold flags, 55 clean). Generated `data/labels/eval_v2.json`, `data/labels/eval_v2.csv`, and report `data/labels/eval_v2_report.md` showing post-verifier precision = 0.5263, post-verifier recall = 0.5000, pre-verifier precision = 0.6897, pre-verifier recall = 1.0000, and FFR = 0.4737 after correcting 10 audit mislabelings in `struct-minimum-length` and `cite-doi-resolvable`.
- Depends on: `src/compliance_review/metrics/compute.py`, `src/compliance_review/cli.py`, `data/labels/gold_labels.csv`.
- Supersedes: `data/labels/eval_v1_report.md`

### [2026-11-08] scripts/compute_retrieval_metrics.py — US-18, D-027
- Verified by: `agent:p3`
- Commit: a43acda
- Tests: `tests/unit/test_retrieval_metrics.py` (formula correctness, HSR@K sensitivity, read-only contract)
- Behaviour: Computes capability recall, version precision@1, over-retrieval rate, HSR@K risk exposure, and retrieval latency distribution across 60 evaluation submissions against gold standard `data/labels/CORPUS_COMPOSITION.md`. Generates `data/labels/retrieval_eval_v1.json` and Markdown report `data/labels/retrieval_eval_v1.md` with 4 evaluation tables.
- Depends on: `data/labels/CORPUS_COMPOSITION.md`, `retrieval_events`, `skills/`.
- Supersedes: none

### [2026-11-08] src/compliance_review/retrieval/capability_gate.py, ingestion/orchestrator.py — US-13, D-028
- Verified by: `agent:p3-fix`
- Commit: dececce
- Tests: `tests/unit/test_gate_purity.py`
- Behaviour: Aligns prose gating rules with mixed gating rules per D-028: report-structure requires >= 500 words, rai-disclosure requires disclosure present, citation-integrity requires references present. Mixed ingestion prefers primary non-disclosure prose files and scans all prose files for bibliography signals.
- Depends on: pure python, standard library only.
- Supersedes: US-13 (2026-11-04)

### [2026-11-08] src/compliance_review/harness/orchestrator.py — US-17, D-029
- Verified by: `agent:p3-fix`
- Commit: 8beb20f
- Tests: `tests/unit/test_orchestrator_latency.py`
- Behaviour: Measures isolated capability gate + FAISS selection time only in `retrieval_events.latency_ms`, strictly excluding model execution runs.
- Depends on: `time.perf_counter`, `src/compliance_review/retrieval/`.
- Supersedes: US-17 (2026-11-05)

### [2026-11-08] scripts/compute_retrieval_metrics.py — US-18 (v2)
- Verified by: `agent:p3-fix`
- Commit: 3d95c5e
- Tests: `tests/unit/test_retrieval_metrics.py`, `tests/integration/test_offline.py`
- Behaviour: Recomputed retrieval metrics against newest retrieval_events; produced `data/labels/retrieval_eval_v2.json` and `data/labels/retrieval_eval_v2.md` confirming 1.0000 recall, 1.0000 precision@1, 0.0000 over-retrieval, 0.5333 HSR@K, and 48.5 ms p50 latency across 60 evaluation submissions.
- Depends on: `data/labels/CORPUS_COMPOSITION.md`, `retrieval_events`.
- Supersedes: US-18 (2026-11-08 v1)

### [2026-11-08] src/compliance_review/db/repository.py — US-29, US-30, US-33, D-030
- Verified by: `agent:p4`
- Commit: 37383b0
- Tests: `tests/unit/test_repository_readonly.py`
- Behaviour: Implements read-only query helpers for dashboard rendering: `get_retrieval_event_for_submission` (ORDER BY id DESC LIMIT 1), `get_skill_executions_for_submission`, `get_verdicts_for_execution`, `get_verdicts_for_submission`, `get_evidence_verifications_for_verdict`, `get_reviewer_feedback_for_submission`, and `list_submissions`. Uses SQLAlchemy Core select() only.
- Depends on: `src/compliance_review/db/tables.py`, `src/compliance_review/db/engine.py`.
- Supersedes: none

### [2026-11-08] src/compliance_review/dashboard/agreement.py — US-29, D-031
- Verified by: `agent:p4`
- Commit: 528b228
- Tests: `tests/unit/test_dashboard_agreement_source.py`
- Behaviour: Implements cached agreement computation wrapper delegating directly to `harness/k_run.compute_agreement` with `@st.cache_data(ttl=60)`. Proves dashboard does not compute agreement inline.
- Depends on: `src/compliance_review/harness/k_run.py`, `streamlit`.
- Supersedes: none

### [2026-11-08] src/compliance_review/dashboard/app.py, queries.py — US-29
- Verified by: `agent:p4`
- Commit: f1d901d
- Tests: `tests/unit/test_dashboard_agreement_source.py`, mypy typecheck
- Behaviour: Implements Streamlit dashboard app shell with wide layout, sidebar submission selector (cached list_submissions), model version and digest display, and cached repository query wrappers with @st.cache_data(ttl=60).
- Depends on: `src/compliance_review/dashboard/queries.py`, `src/compliance_review/config.py`, `streamlit`.
- Supersedes: none

### [2026-11-08] src/compliance_review/dashboard/pages/01_submission.py — US-29, US-30, US-33
- Verified by: `agent:p4`
- Commit: 08c6306
- Tests: `tests/unit/test_dashboard_agreement_source.py`, `tests/integration/test_dashboard_readonly.py`, mypy
- Behaviour: Implements the seven frozen sections of ARCHITECTURE.md §10.2: Header, Retrieval trace, Findings (verified flags, click-through location context, action buttons), Disagreement view (< 0.85 side-by-side runs), Passed checks (collapsed markdown table), Unsupported evidence (collapsed), and Audit footer. Empty states handled explicitly in each section. Factored into standalone render_* functions.
- Depends on: `src/compliance_review/dashboard/queries.py`, `src/compliance_review/dashboard/agreement.py`.
- Supersedes: none

### [2026-11-08] src/compliance_review/dashboard/pages/02_skill_library.py, 03_metrics.py — D-033
- Verified by: `agent:p4`
- Commit: db76948
- Tests: static code inspection, mypy
- Behaviour: Stubs pages 02_skill_library.py and 03_metrics.py with st.info("Deferred to camera-ready (D-033).") per ARCHITECTURE.md §10.1 and D-033.
- Depends on: `streamlit`.
- Supersedes: none

### [2026-11-08] tests/integration/test_dashboard_readonly.py — US-29, D-030, D-032
- Verified by: `agent:p4`
- Commit: ab74d6b
- Tests: `tests/integration/test_dashboard_readonly.py` (3 passed)
- Behaviour: Asserts the read-only contract for the dashboard: verifies all 7 render functions handle empty/mock data without calling st.write(), verifies render_submission_page calls only D-030 repository read helpers and zero write functions, and verifies reviewer feedback button action handler writes atomically exactly one reviewer_feedback row and one audit_log row via isolated SQLite fixture.
- Depends on: `src/compliance_review/dashboard/pages/01_submission.py`, `src/compliance_review/db/repository.py`.
- Supersedes: none

### [2026-11-08] scripts/run_dashboard.py, README.md — US-29
- Verified by: `agent:p4`
- Commit: 21a426f
- Tests: static code inspection, README instructions check
- Behaviour: Adds convenient launcher script for running the Streamlit dashboard and documents run commands in README.md.
- Depends on: `src/compliance_review/dashboard/app.py`, `streamlit`.
- Supersedes: none

### [2026-11-08] tests/integration/test_dashboard_real_render.py — US-29
- Verified by: `agent:p4-hotfix`
- Commit: pending
- Tests: `tests/integration/test_dashboard_real_render.py` (4 passed)
- Behaviour: Exercises real Streamlit rendering path against actual DB submission eval_mixed_12 using both AppTest and direct render_* invocations; asserts zero ImportErrors or pyarrow regressions, confirms numeric latency for eval submissions and dash latency for pilot submissions across all seven sections.
- Depends on: `src/compliance_review/dashboard/pages/01_submission.py`, `src/compliance_review/db/repository.py`.
- Supersedes: none

### [2026-11-08] src/compliance_review/ingestion/pdf.py, model/prompts.py, skills/citation-integrity/v2/SKILL.md — US-01, US-20, US-06, D-042
- Verified by: `agent:p4.7`
- Commit: 08df022
- Tests: `tests/unit/test_pdf_footer_strip.py`, `compliance-review skills validate --root skills/`
- Behaviour: Three-layer fix for citation evidence quality: strips common PDF metadata headers/footers (including Turnitin metadata) during text extraction in pdf.py, adds check-specific shape guidance in prompts.py requiring verbatim bibliography entries for cite-no-duplicates, and tightens evidence_requirement in citation-integrity/v2/SKILL.md.
- Depends on: `src/compliance_review/ingestion/pdf.py`, `src/compliance_review/model/prompts.py`, `skills/citation-integrity/v2/SKILL.md`.
- Supersedes: none

---

## 3. Active Roadblocks

*(none)*

---

## 4. Resolved Roadblocks (append-only)

```
### RB-<NNN> (resolved [YYYY-MM-DD])
- Resolution: <one sentence>
- Resolved by: `agent:<task-id>`
- Amendment commit: <sha>
- Follow-up test added: <test file>::<test name>
```

### RB-005 (resolved 2026-11-08)
- Resolution: Resolved over-retrieval (0.2154 -> 0.0000) via D-028 (aligned prose gating rules with mixed gating rules requiring >= 500 words for report-structure and disclosure presence for rai-disclosure) and citation detection fix in ingestion. Resolved latency (p50 24,730 ms -> 48.5 ms) via D-029 (isolated retrieval latency measurement from LLM execution). All 5 M3 retrieval targets achieved.
- Resolved by: `agent:p3-fix`
- Amendment commit: dececce, 8beb20f
- Follow-up test added: tests/unit/test_orchestrator_latency.py::test_retrieval_latency_excludes_model_execution

### RB-001 (resolved 2026-11-04)
- Resolution: Widened MySQL pin to >= 8.0.36, < 8.1 via D-011.
- Resolved by: human:arch / agent
- Amendment commit: 8a341f2
- Follow-up test added: none (driver handles patch compatibility)

### RB-002 (resolved 2026-11-04)
- Resolution: Installed Python 3.11.18 via `uv python install 3.11` and created venv.
- Resolved by: agent
- Amendment commit: c7beff1
- Follow-up test added: none

### RB-003 (resolved 2026-11-04)
- Resolution: uv 0.13.7 present on User PATH.
- Resolved by: human:arch / agent
- Amendment commit: none
- Follow-up test added: none

### RB-004 (resolved 2026-11-04)
- Resolution: Granted DDL privileges on compliance_review.* to app_user; migration 0001_initial applied creating 7 tables.
- Resolved by: human:arch / agent
- Amendment commit: applied via migration 0001_initial
- Follow-up test added: `tests/integration/test_ingest_deterministic.py`, `tests/integration/test_audit_append_only.py`

---

## 5. State Adjustments

### SA-002: Stale HALO derived rows purge
- Changed: 2026-11-10
- From: 84 stale skill_executions, 378 stale checklist_verdicts, 84 evidence_verifications, 1 reviewer_feedback across upload-*Halo_Enhanced* submissions
- To: 0 derived rows for upload-*Halo_Enhanced* submissions
- Reason: One-off remediation: deleted all derived rows for upload-*Halo_Enhanced* submissions to clear stale data from before D-044 revert (1d3906e). Submissions rows preserved. 60-submission eval corpus unaffected.
- Frozen invariant affected: no
- Re-verified by: manual SQL count = 0

---

## 6. Decisions Log (append-only)

### D-001: Python-only, no TypeScript
- Date: 2026-11-03 · Decided by: human:arch
- Decision: zero TypeScript, zero Node, zero frontend framework. Dashboard is Streamlit.
- Alternatives rejected: FastAPI + React — doubles hallucination surface, adds no evaluation value.
- Documents amended: PRD.md §5, ARCHITECTURE.md §2.6
- Reversible: no

### D-002: Streamlit only for dashboard
- Date: 2026-11-03 · Decided by: human:arch
- Decision: all reviewer UI in `dashboard/pages/`, three pages, Streamlit.
- Alternatives rejected: Dash, Gradio, Reflex.
- Documents amended: ARCHITECTURE.md §10
- Reversible: yes (would require new PRD)

### D-003: Ollama + qwen3:4b, digest-pinned
- Date: 2026-11-03 · Decided by: human:arch
- Decision: inference through Ollama, model tag `qwen3:4b`, digest recorded per execution.
- Alternatives rejected: llama-cpp-python, vLLM, transformers.
- Documents amended: PRD.md §6.5, ARCHITECTURE.md §2.3
- Reversible: yes, via PRD amendment

### D-004: SQLAlchemy Core, not ORM
- Date: 2026-11-03 · Decided by: human:arch
- Decision: `db/tables.py` uses `Table` + `Column` only.
- Alternatives rejected: ORM — generates UPDATEs, threatens append-only audit.
- Documents amended: ARCHITECTURE.md §2.2, §4
- Reversible: no

### D-005: FAISS over managed vector DBs
- Date: 2026-11-03 · Decided by: human:arch
- Decision: `faiss-cpu` with a persisted index file.
- Alternatives rejected: Chroma, Qdrant, pgvector.
- Documents amended: ARCHITECTURE.md §2.4
- Reversible: yes

### D-006: Evidence verifier thresholds frozen
- Date: 2026-11-03 · Decided by: human:arch
- Decision: `prefix_len=40`, `fuzzy_threshold=0.92`, NFKC+collapse+casefold. Change requires PRD amendment.
- Alternatives rejected: adaptive threshold — untestable, undermines the invariant.
- Documents amended: PRD.md §4.5, ARCHITECTURE.md §7.3, INSTRUCTIONS.md §8
- Reversible: no

### D-007: Add `scripts/fetch_datasets.py`
- Date: 2026-11-04 · Decided by: human:arch
- Decision: dataset fetcher lives at `scripts/fetch_datasets.py`; manifest at `data/raw/MANIFEST.json`.
- Documents amended: ARCHITECTURE.md §3
- Reversible: yes

### D-008: Audit-log grants run manually, not via Alembic
- Date: 2026-11-04 · Decided by: human:arch
- Decision: grant statements in `migrations/manual/0002_grants.sql`; documented in `README.md`; not executed by Alembic.
- Alternatives rejected: Alembic-run — needs DBA privileges the app user does not have.
- Documents amended: ARCHITECTURE.md §4.7
- Reversible: no

### D-009: Add `--deterministic-only` flag
- Date: 2026-11-04 · Decided by: human:arch
- Decision: `compliance-review review --deterministic-only` runs gate + deterministic checks only; used for P0 gate demonstration.
- Documents amended: ARCHITECTURE.md §9
- Reversible: yes

### D-010: Label CSV schema
- Date: 2026-11-04 · Decided by: human:arch
- Decision: 12-column schema documented in `docs/annotation_guideline.md`; referenced from `ARCHITECTURE.md §3` `data/labels/` note.
- Documents amended: ARCHITECTURE.md §3
- Reversible: no (schema stability required for metrics)

### D-011: MySQL pin is 8.0.x, not 8.0.36
- Date: 2026-11-04 · Decided by: human:arch
- Context: Development environment runs MySQL 8.0.39; PRD §6.5 and ARCHITECTURE.md §2.2 previously pinned 8.0.36.
- Decision: supported range is `MySQL >= 8.0.36, < 8.1`. Tested on 8.0.36 (reference); dev runs 8.0.39. No schema or grant differences between these patch releases.
- Alternatives rejected: downgrade to 8.0.36 — no benefit, risk to dev environment.
- Documents amended: PRD.md §6.5, ARCHITECTURE.md §2.2, §4
- Reversible: yes

### D-012: Add `--skill-status` review filter
- Date: 2026-11-05 · Decided by: human:arch
- Decision: Add `--skill-status {active|evaluating|draft|all}` to `compliance-review review` in ARCHITECTURE.md §9. Default `active`.
- Context: Exists only to let P1 exercise model-based v2 skills while v1 stays the production path.
- Documents amended: ARCHITECTURE.md §9
- Reversible: yes

### D-013: Add `data/pilots/` directory
- Date: 2026-11-05 · Decided by: human:arch
- Decision: Add `data/pilots/` to ARCHITECTURE.md §3 holding 10 hand-authored pilot submissions (<= 50 KB each), committed to git. Rest of `data/` stays gitignored.
- Context: P1 gate is unreproducible without committed pilot submissions.
- Documents amended: ARCHITECTURE.md §3
- Reversible: yes

### D-014: Add `compliance-review skills set-status` command
- Date: 2026-11-05 · Decided by: human:arch
- Decision: Add `compliance-review skills set-status --capability TEXT --version TEXT --status {draft|evaluating|active|deprecated}` to ARCHITECTURE.md §9.
- Context: Only way to transition eval_status prior to P5 promotion.
- Documents amended: ARCHITECTURE.md §9
- Reversible: yes

### D-015: Batched P0 ingestion stories in aaf052c
- Date: 2026-11-05 · Decided by: human:arch / agent
- Decision: Batched P0 ingestion stories in aaf052c; coupling in the ingestion module forced a single commit. P1 will split per story; if coupling forces a batch, a D-0xx entry is required BEFORE the commit.
- Context: PROCESS-FIX-1 from P1 brief.
- Documents amended: MEMORY.md §6
- Reversible: no

### D-016: Ignore UP017 in ruff to uphold ARCHITECTURE.md §2.7
- Date: 2026-11-04 · Decided by: agent
- Context: Ruff rule UP017 flags `timezone.utc` to recommend `datetime.UTC`. However, ARCHITECTURE.md §2.7 strictly specifies `stdlib datetime with timezone.utc everywhere`.
- Decision: add `UP017` to ruff `ignore` list in `pyproject.toml`.
- Alternatives rejected: use `datetime.UTC` (violates frozen requirement in ARCHITECTURE.md §2.7).
- Documents amended: none (configuration only)
- Reversible: yes

### D-017: Prompt and check grounding tightening over verifier softening (P1.5 evidence quality)
- Date: 2026-11-06 · Decided by: human:arch / agent
- Decision: Resolve evidence rejection issues by tightening deterministic check source grounding, model prompts (negative examples, quote-only constraint, mandatory confidence), and v2 skill requirements rather than softening the frozen evidence verifier thresholds (prefix_len=40, fuzzy_threshold=0.92).
- Alternatives rejected: Lowering fuzzy_threshold to 0.70 or adding loose matching modes — violates ARCHITECTURE.md §1 & INSTRUCTIONS.md §8 frozen commitments and introduces ungrounded model hallucinations into the audit log.
- Documents amended: None (frozen verifier invariant strictly upheld)
- Reversible: no

### D-018: Pre-verifier vs post-verifier precision and recall views
- Date: 2026-11-06 · Decided by: human:arch
- Decision: Add pre_verifier_precision (true flags ÷ all flags emitted before verification) and pre_verifier_recall (true flags emitted before verification ÷ gold issues) alongside post-verifier metrics in PRD.md §6.2 and ARCHITECTURE.md §6.5.
- Context: P1.5 showed acceptance rose 27% → 80%; without the pre-verifier view, the evaluation cannot distinguish "model capable, verifier strict" from "model not capable".
- Documents amended: PRD.md §6.2, ARCHITECTURE.md §6.5
- Reversible: no

### D-019: Tag check_source on ModelVerdict and checklist_verdicts table
- Date: 2026-11-06 · Decided by: human:arch
- Decision: ModelVerdict schema and checklist_verdicts DB table gain check_source: Literal["deterministic", "model"].
- Context: P1.5 showed deterministic checks need their own evidence-grounding (commit 8170240); without tagging, P2 cannot compute deterministic-only precision separately.
- Documents amended: ARCHITECTURE.md §5.3
- Reversible: no

### D-020: Pre vs Post Verifier view in dashboard Metrics page
- Date: 2026-11-06 · Decided by: human:arch
- Decision: Dashboard Metrics page gains a "Pre vs Post Verifier" comparison view (read-only).
- Documents amended: ARCHITECTURE.md §10.3
- Reversible: yes

### D-027: Retrieval metrics script and corpus composition gold
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Add `scripts/compute_retrieval_metrics.py` (retrieval metrics evaluation CLI/script) and `data/labels/CORPUS_COMPOSITION.md` (per-submission gold properties across 60 evaluation corpus submissions).
- Context: Required for P3 Milestone M3 retrieval evaluation without modifying capability_gate.py or P2 evaluation outputs.
- Documents amended: ARCHITECTURE.md §3
- Reversible: yes

### D-028: Align prose gating rules with mixed gating rules
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Amend ARCHITECTURE.md §6.2 capability gate table. For prose submissions: citation-integrity requires references_present; report-structure requires prose_length >= 500 words; rai-disclosure requires disclosure_present.
- Context: In P3, unconditional enabling of report-structure and rai-disclosure on short prose submissions (< 500 words, no disclosure) caused over-retrieval rate of 0.2154 (exceeding target < 0.20). Aligning prose preconditions prevents false positive gate activations.
- Documents amended: ARCHITECTURE.md §6.2
- Reversible: no

### D-029: Define retrieval_events.latency_ms as retrieval-only time
- Date: 2026-11-08 · Decided by: human:arch
- Decision: retrieval_events.latency_ms is defined as milliseconds elapsed in capability gate + FAISS version selection ONLY, not the entire review execution or LLM inference.
- Context: In P3, latency was recorded as total review duration (p50 = 24,730 ms), conflating model execution with retrieval latency. The target (p50 <= 1500 ms) measures retrieval efficiency as specified in PRD §6.1.
- Documents amended: ARCHITECTURE.md §4.2
- Reversible: no

### D-030: Read-only query helpers in db/repository.py
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Add read-only query helpers to db/repository.py: get_submission_by_external_id, get_submission_by_id, get_retrieval_event_for_submission (ORDER BY id DESC LIMIT 1), get_skill_executions_for_submission, get_verdicts_for_execution, get_verdicts_for_submission, get_evidence_verifications_for_verdict, get_reviewer_feedback_for_submission, list_submissions (paged for sidebar). All use SQLAlchemy Core SELECT only. No direct SQL or INSERT/UPDATE/DELETE.
- Context: Required for dashboard rendering while enforcing read-only contract. get_retrieval_event_for_submission picks newest row after P3-fix refresh.
- Documents amended: ARCHITECTURE.md §3, §10.4
- Reversible: no

### D-031: Agreement values in dashboard from harness/k_run.compute_k_run_agreement
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Agreement values in the dashboard MUST come from harness/k_run.compute_k_run_agreement() — NOT recomputed inline. The dashboard calls the function and caches via st.cache_data(ttl=60).
- Context: Prevents divergence between dashboard display and harness evaluation metrics.
- Documents amended: ARCHITECTURE.md §10.4
- Reversible: no

### D-032: Reviewer actions write through db/repository.py::record_reviewer_feedback ONLY
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Reviewer action handler writes through db/repository.py::record_reviewer_feedback ONLY. One feedback row + one audit_log row per action, one transaction.
- Context: Preserves audit logging and schema invariants for all reviewer overrides.
- Documents amended: ARCHITECTURE.md §10.4
- Reversible: no

### D-033: Defer dashboard pages 02_skill_library and 03_metrics to camera-ready
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Dashboard pages 02_skill_library and 03_metrics are deferred to camera-ready. Implement them as stubs with a st.info() message.
- Context: Focuses P4-code entirely on the Submission review page (seven frozen sections). Rescinded by D-038.
- Documents amended: ARCHITECTURE.md §10.1
- Reversible: yes

### D-035: Wrap override controls in st.popover
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Replace inline reason selectbox in 01_submission.py findings with st.popover("Override") containing selectbox (index=None, placeholder), comment input, and confirm button.
- Context: Prevents default selectbox reason code ("evidence_insufficient") from appearing inline as an ambiguous badge on un-overridden findings.
- Documents amended: src/compliance_review/dashboard/pages/01_submission.py
- Reversible: yes

### D-036: Calibrate confidence prompt instructions
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Update prompts.py JSON example confidence to 0.87 and instruct model to assign confidence in [0.5, 0.99] reflecting evidence support clarity (> 0.95 reserved for literal matches).
- Context: Eliminates collapse to 1.0 caused by 1.0 worked-example priming and explicit pass/not_applicable default instruction.
- Documents amended: src/compliance_review/model/prompts.py
- Reversible: yes

### D-038: Skill Library and Metrics pages implemented (D-033 rescinded)
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Implement 02_skill_library.py (4 capability tabs, version expanders, execution stats) and 03_metrics.py (5 frozen sections); D-033 is rescinded.
- Context: Closes P4.5 dashboard story across all 3 pages per ARCHITECTURE.md §10.1-10.3.
- Documents amended: ARCHITECTURE.md §10.1
- Reversible: no

### D-041: Sidebar upload-and-review widget
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Add sidebar upload-and-review widget to dashboard/app.py as app chrome (preserving the three-page rule of §10.1). Writes uploads to data/incoming/, runs ingest and review with evaluating skills, and sets the newly created submission active in session_state.
- Context: Provides user-facing upload-to-review demo for DO5.
- Documents amended: ARCHITECTURE.md §3, §10.5
- Reversible: yes

### D-042: Citation evidence-quality fix
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Strip common page headers and footers during PDF text extraction in `ingestion/pdf.py`. Tighten citation prompts in `model/prompts.py` to mandate quoting verbatim bibliography entries for `cite-no-duplicates`, DOI-bearing lines for `cite-doi-resolvable`, and retraction notices for `cite-not-retracted`. Update `skills/citation-integrity/v2/SKILL.md` evidence requirements accordingly.
- Context: Prevents PDF page metadata ("Page 8 of 9 - AI Writing Submission") from being cited as evidence for citation duplicates.
- Documents amended: ARCHITECTURE.md §2.5, §3, skills/citation-integrity/v2/SKILL.md
- Reversible: yes

### D-043: Location context resolver integration
- Date: 2026-11-08 · Decided by: human:arch / agent:p4.7-hotfix
- Decision: Expose `resolve_source_span` in `evidence/verifier.py` to accept high-level `(evidence_location, submission)` inputs and resolve parsed spans across prose/pdf/code (Option a). Update dashboard `01_submission.py` to use `resolve_source_span` instead of raw file reading.
- Context: Prevents PDF binary bytes (`%PDF-1.5`) from being displayed in Location Context expander; ensures dashboard displays exact parsed text seen by the verifier.
- Documents amended: ARCHITECTURE.md §3, MEMORY.md §6
- Reversible: yes

### D-044: Skill v2 checklist scope violation and revert
- Date: 2026-11-08 · Decided by: human:arch
- Decision: Skill v2 checklist scope violation and revert. Between commits c5d8e85..HEAD, the v2 checklist for citation-integrity and report-structure was modified out of scope (removed cite-context-accurate, struct-claim-evidence-alignment; added cite-using-numeric-notation, struct-using-figures). This violated version-identity: eval_v2.json was computed against the pre-change checklist. Reverted to the e8be242 checklist state while retaining D-042's evidence_requirement change for cite-no-duplicates.
- Context: Preserves version-identity with eval_v2.json so production and evaluation runs evaluate the identical 10 check IDs (cite-claim-supported, cite-context-accurate, cite-doi-resolvable, cite-no-duplicates, cite-not-retracted, struct-claim-evidence-alignment, struct-heading-order, struct-minimum-length, struct-required-sections, struct-semantic-coherence).
- Documents amended: skills/citation-integrity/v2/SKILL.md, skills/report-structure/v2/SKILL.md
- Reversible: no

### D-045: Validate model check_id against skill checklist
- Date: 2026-11-10 · Decided by: human:arch
- Decision: Enforce checklist membership in `schema_validation.py`. After `ModelOutput` parses successfully, each verdict's `check_id` is validated against the skill's canonical check IDs. Any hallucinated or out-of-scope `check_id` raises `ModelSchemaError`, triggering the single schema retry (US-21).
- Context: Prevents LLM hallucinations (e.g. `cite-using-numeric-notation`, `struct-using-figures`) from entering `checklist_verdicts`.
- Documents amended: `src/compliance_review/model/schema_validation.py`, `src/compliance_review/checks/model_based/`
- Reversible: no

### D-046: Enumerate canonical check_ids in capability review prompts
- Date: 2026-11-10 · Decided by: human:arch / agent:p4.7-fix-4
- Decision: Dynamically inject canonical checklist item enumeration directly into `CHECKLIST ITEMS TO EVALUATE:` within capability review prompts from `SkillFrontmatter` on disk. Format strictly specifies: "Your response MUST contain a verdict for EACH of these {count} check_ids, using these exact strings (do not invent new check_ids): - <check_id>: <question>. Do not return any other check_id. If you cannot assess a check, return it with verdict 'not_applicable' and confidence < 0.5." Deduplicate model verdict entries before combining with deterministic verdicts.
- Context: Small language models (Qwen 4B) generate hallucinated check IDs or copy terms from the submission text when check IDs are not prominently enumerated or when conflicting checklist blocks (e.g. separate citation guidance) compete in the prompt.
- Documents amended: `src/compliance_review/model/prompts.py`, `src/compliance_review/checks/model_based/`
- Reversible: no

---

## 7. Test Failures and Resolutions (append-only)

### TF-001: test_evidence_gate_four_conditions & test_ingest_mixed_and_deterministic_review
- Date: 2026-11-06
- Test: `tests/integration/test_evidence_gate_pilot.py`, `tests/integration/test_ingest_deterministic.py`
- Error: Ollama prediction aborted token repeat limit on schema retry; Assertion failure on trace header
- Suspected cause: Schema retry loop caused by missing confidence field in model output; trace header missing "Deterministic" prefix in deterministic-only mode.
- Alternatives considered: 1. Soften schema validation — rejected (breaks US-21); 2. Tighten prompt to mandate confidence on all verdicts and add trace header branching — passed.
- Resolution: Added mandatory confidence instruction and negative examples to prompt; ensured trace table uses Deterministic Review Trace header when deterministic_only=True.
- Frozen invariant touched: no
- Resolved by: `agent:p1.5`
- Commits: 8170240, 6ab0997, f6003bf

### TF-002: manual streamlit render of 01_submission.py
- Date: 2026-11-08
- Test: manual streamlit render of 01_submission.py
- Error: ImportError: pyarrow requires NumPy 2.0 or newer, found 1.26.4
- Suspected cause: st.dataframe triggers pyarrow; venv has numpy 1.26.4 (pinned by faiss-cpu / sentence-transformers)
- Resolution: replaced st.dataframe with st.table (no pyarrow dep)
- Frozen invariant touched: no
- Resolved by: `agent:p4-hotfix`
- Commits: 9eedabd, 8819c32, 31a8da1, 4456c12

### TF-003: disagreement view on pilot submission test-pilot-pilot_mixed_two_issues-56c253
- Date: 2026-11-08
- Test: manual streamlit render of 01_submission.py
- Error: Informational (not a bug): Disagreement view displayed "No disagreement across runs".
- Suspected cause: Suspected missing data or UI bug, but investigation confirmed agreement is 1.0000 across all k=3 runs for this pilot submission.
- Alternatives considered: Display mock variance — rejected (falsifies review data).
- Resolution: No fix needed. Display logic is mathematically correct. Real multi-run variance correctly renders for the 8 submissions in the DB with distinct_verdicts > 1 (e.g. eval_mixed_19, eval_prose_12).
- Frozen invariant touched: no
- Resolved by: `agent:p4.5`
- Commits: none (informational diagnosis)

### TF-004: manual streamlit render of 02_skill_library.py
- Date: 2026-11-08
- Test: manual streamlit render of 02_skill_library.py
- Error: StreamlitAPIException: Expanders may not be nested
- Suspected cause: Line 99 of 02_skill_library.py opened st.expander inside the version expander. Existing unit tests mocked Streamlit runtime and did not exercise the real nesting rule.
- Alternatives considered: Tabs or popover inside expander — rejected (Streamlit limits nested containers).
- Resolution: Replaced inner expander with inline st.caption and st.code blocks for each checklist item's evidence requirement. Added AppTest real-render tests in tests/integration/test_dashboard_real_render.py to catch UI container violations automatically.
- Frozen invariant touched: no
- Resolved by: `agent:p4.5-hotfix`
- Commits: 9ed1d0e, 0de71ae

### TF-005: manual streamlit render of Location Context on PDF upload
- Date: 2026-11-08
- Test: manual streamlit render of Location Context on PDF upload
- Error: viewer showed %PDF-1.5 and PDF objects instead of extracted text
- Cause: dashboard viewer read raw file bytes; verifier used parsed text
- Resolution: exposed shared source resolver in evidence/verifier.py; both components now use the same extraction path
- Frozen invariant touched: no
- Resolved by: `agent:p4.7-hotfix`
- Commits: 49c4040

### TF-006: check IDs discrepancy between HALO reviews and empty Location Context in Section 3
- Date: 2026-11-08
- Test: manual streamlit render of 01_submission.py on uploaded HALO PDF
- Trigger: Discrepancy in check IDs between two HALO uploads in the dashboard (Run 1 had cite-context-accurate and struct-claim-evidence-alignment; Run 2 had cite-using-numeric-notation and struct-using-figures).
- Impact: Paper-blocking if undetected: eval_v2.json claims metrics for one checklist while production runs evaluate a different one.
- Fix: Reverted both v2 SKILL.md checklists to e8be242 baseline, keeping only D-042's cite-no-duplicates evidence_requirement. Unified render_findings and render_unsupported to call resolve_source_span directly.
- Frozen invariant touched: no
- Resolved by: `agent:p4.7-fix`
- Commits: 1d3906e, ac5f43a

### TF-007: resolve_source_span signature mismatch in finding render path
- Date: 2026-11-08
- Test: manual streamlit render of Location Context on HALO upload
- Error: TypeError: resolve_source_span() got an unexpected keyword argument 'evidence_location'
- Cause: finding render path called resolver with keyword args that did not match the function's actual positional signature.
- Resolution: unified both call sites to the actual positional signature `resolve_source_span(location, submission)`. Added signature-identity test `test_finding_and_unsupported_use_same_resolver_signature`.
- Frozen invariant touched: no
- Resolved by: `agent:p4.7-fix-2`
- Commits: d68b2e5

### TF-008: nested expander in unsupported section
- Date: 2026-11-10
- Test: manual streamlit render of Unsupported Evidence section
- Error: StreamlitAPIException: Expanders may not be nested
- Cause: inner st.expander at line 452 of 01_submission.py inside outer Unsupported Evidence expander. Same class as TF-004 but different location; the P4.7-fix-2 unification of resolvers reintroduced an expander wrapper on the new call site.
- Resolution: replaced inner expander with inline st.code. Added a lint-level AST test tests/unit/test_no_nested_expanders.py to assert no nested expanders exist.
- Frozen invariant touched: no
- Resolved by: `agent:p4.7-fix-3`
- Commits: 367810f, 8e0a38a

### TF-009: Qwen check-ID hallucination on HALO upload submission
- Date: 2026-11-10
- Test: manual streamlit / CLI review of HALO PDF upload (`submission_id=294`)
- Error: Model emitted hallucinated check IDs (`cite-using-numeric-citations`, etc.) causing Phase 1.5 schema validation rejection (`ModelSchemaError: Unknown check_ids for citation-integrity: {'cite-using-numeric-citations'}`).
- Cause: `prompts.py` did not enumerate canonical check IDs in the prompt template, and a separate `CITATION_CHECK_GUIDANCE` block confused Qwen 4B into generating ungrounded checklist identifiers.
- Resolution: Updated `prompts.py` to load canonical checklist items from `SkillFrontmatter` on disk and format an explicit enumeration mandate in every prompt. Removed distracting secondary checklist blocks. Added verdict deduplication in model-based check handlers. Added unit tests `tests/unit/test_prompt_check_id_enumeration.py`.
- Frozen invariant touched: no
- Resolved by: `agent:p4.7-fix-4`
- Commits: d56de24, ed8ead6, 560aeb1

---

## 8. Schema Changes (append-only)

```
### SC-<NNN>: <table>.<column or index>
- Date: [YYYY-MM-DD]
- Migration: `migrations/versions/<file>.py`
- Change: <add column | add index | add table | rename | drop (forbidden)>
- Rationale: <one sentence>
- Backfill required: yes / no
- Architect review: `human:<initials>`
- Commit: <sha>
```

(No entries yet.)

---

## 9. Phase Gate Checklist

### P0 gate
- [x] `submissions` table created via Alembic migration `0001_initial.py` (verified via SHOW TABLES: submissions, retrieval_events, skill_executions, checklist_verdicts, evidence_verifications, reviewer_feedback, audit_log, alembic_version)
- [x] `compliance-review ingest` works on prose, code, mixed submissions (`tests/integration/test_ingest_deterministic.py`)
- [x] `compliance-review skills validate` passes on four seed `SKILL.md` (draft) (`skills/*/v1/SKILL.md`)
- [x] `compliance-review review --deterministic-only` prints trace: capability_set, gate_reason, deterministic verdicts, latency_ms (`tests/integration/test_ingest_deterministic.py`, `src/compliance_review/harness/orchestrator.py`)
- [x] `capability_gate.py` imports no model or faiss module (`tests/unit/test_gate_purity.py`)
- [x] `audit_log` rejects UPDATE and DELETE at MySQL grant level (`tests/integration/test_audit_append_only.py`)
- [x] `test_offline.py` passes with egress blocked (`tests/integration/test_offline.py`)
- [x] `test_verifier_invariant.py` passes, asserting frozen thresholds (`tests/unit/test_verifier_invariant.py`)
- [x] `ruff`, `ruff format --check`, `mypy --strict`, unit and integration tests all green (30 source files checked, 20 tests pass)
- [x] `data/raw/MANIFEST.json` exists and lists all seven datasets (or roadblocks) (`scripts/fetch_datasets.py`)
- [x] Frozen invariant checklist (§1) all ticked

### P1 gate
- [x] Ollama reachable, `qwen3:4b` digest recorded in `skill_executions` (`359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7` verified in `skill_executions` via `tests/integration/test_evidence_gate_pilot.py` Gate Condition (d))
- [x] `ModelOutput` schema validation with one retry (`src/compliance_review/model/schema_validation.py`, verified in `tests/unit/test_schema_retry.py`)
- [x] Evidence verifier downgrades fabricated evidence on 10 pilot submissions (verified across 10 pilots in `tests/integration/test_evidence_gate_pilot.py` Gate Condition (b) and `data/pilots/PILOT_REPORT.md`: 54 flags downgraded to `unsupported_evidence`)
- [x] Every surfaced `flag` has a verified `evidence_verifications` row (verified in `tests/integration/test_evidence_gate_pilot.py` Gate Condition (a): 100% of the 20 surfaced flags match `verified=True` rows in `evidence_verifications`)
- [x] k=3 stored per skill per submission (verified in `tests/integration/test_evidence_gate_pilot.py` Gate Condition (c): exactly 3 runs per gated capability across all 10 pilots, 69 total execution rows in `skill_executions`)

### P1.5 gate (Evidence Quality Investigation)
- [x] Frozen verifier confirmed 100% intact (`prefix_len=40`, `fuzzy_threshold=0.92`, NFKC + whitespace collapse + casefold)
- [x] Diagnostic inspection completed: all 54 initial downgraded rows classified into 4 buckets (0 grammar_invalid, 1 not_located, 30 paraphrase, 23 genuinely_wrong)
- [x] Deterministic check evidence spans grounded to verbatim source lines (`citation.py`, `code.py`, `disclosure.py`, `structure.py`)
- [x] Model prompt tightened with negative examples, mandatory confidence field, and quote-only constraint (`prompts.py`)
- [x] V2 skills updated with explicit evidence requirements (`skills/*/v2/SKILL.md`)
- [x] Pilot preconditions satisfied: clean prose and mixed reports meet 500-word threshold; issue pilot contains broken DOI
- [x] Target met: `pilot_issue_doi.md` verified acceptance rate >= 50% (achieved: 100%, 6/6)
- [x] Target met: `pilot_issue_code` verified acceptance rate >= 50% (achieved: 100%, 6/6)
- [x] Target met: `pilot_clean_prose.md` verified flags = 0 (achieved: 0)
- [x] Target met: `pilot_clean_mixed` verified flags = 0 (achieved: 0)
- [x] Target met: overall verified acceptance rate on real-defect pilots >= 50% (achieved: 83.3%, 30/36)
- [x] `PILOT_REPORT.md` regenerated with before vs. after comparison table by capability (overall acceptance increased from 27.0% to 80.0%)

### P2 gate
- [x] Labelled set audited subset (15 submissions, 75 checks, dual-annotated & adjudicated under Mode B fast-path in `data/labels/gold_labels.csv`; full 60-submission set pending)
- [x] `docs/annotation_guideline.md` published
- [x] `compliance-review metrics` produces per-check precision/recall/FFR/consistency (`data/labels/eval_v1.json`, `eval_v1_report.md`)
- [ ] FFR < 0.15 per check (Mode B audit subset observed high FFR due to verifier downgrading valid model flags lacking verbatim quotes; target < 0.10 before promotion)

### P3 gate
- [x] Capability recall ≥ 0.90 (1.0000 achieved)
- [x] Over-retrieval < 0.20 (0.0000 achieved)
- [x] HSR@K measured (0.5333 aggregate; reported per capability)
- [x] Latency ≤ 1500 ms (p50 = 48.5 ms achieved)

### P4 gate
- [x] Streamlit Submission page renders all seven frozen sections (verify with eval_mixed_12 - see TF-002 for fix that made this true)
- [ ] Two reviewers complete 20 submissions · reason codes ≥ 90 % · rework time measured

### P5 gate
- [ ] Every `active` skill passes clean-submission regression (FFR < 0.10)
- [ ] Consistency ≥ 0.85 on `active` checks
- [ ] `metrics --labels` reproduces paper numbers from published test-set hash
- [ ] `audit_log` grant verified by test
- [ ] `test_offline.py` passes with egress blocked

---

## 10. How to Update This File

After every commit:

1. Overwrite §1 `Current State Snapshot`.
2. Append to §2 if the commit completes a user story.
3. Move resolved blockers from §3 to §4.
4. Append to §5 if a threshold or config changed.
5. Append to §6 if a design constraint changed.
6. Append to §7 if a failing test was resolved.
7. Append to §8 if `db/tables.py` or `migrations/versions/` changed.
8. Tick §9 items as they become true.
9. Bump `Document version` (semver minor per entry, patch per state overwrite).

An agent MUST NOT commit without updating this file.