# MEMORY — Agent Boot Notebook

| Field | Value |
|---|---|
| Document version | 1.2.3 |
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
| Current phase | P3 (Milestone M3 Retrieval Metrics Computation) |
| Last completed milestone | P2-eval (Milestone M2 evaluation on audit-corrected labels) |
| Active branch | `main` |
| Last green commit | e8be242 |
| Unit test count | 57 |
| Integration test count | 9 |
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
- Commit: pending
- Tests: `tests/integration/test_metrics_readonly.py`, `tests/unit/test_pre_post_metrics.py`, `tests/unit/test_insufficient_sample.py`
- Behaviour: Computed P2-eval metrics against audit-corrected `data/labels/gold_labels.csv` (75 audited check instances, 20 gold flags, 55 clean). Generated `data/labels/eval_v2.json`, `data/labels/eval_v2.csv`, and report `data/labels/eval_v2_report.md` showing post-verifier precision = 0.5263, post-verifier recall = 0.5000, pre-verifier precision = 0.6897, pre-verifier recall = 1.0000, and FFR = 0.4737 after correcting 10 audit mislabelings in `struct-minimum-length` and `cite-doi-resolvable`.
- Depends on: `src/compliance_review/metrics/compute.py`, `src/compliance_review/cli.py`, `data/labels/gold_labels.csv`.
- Supersedes: `data/labels/eval_v1_report.md`

---

## 3. Active Roadblocks

(No active roadblocks.)

---

## 4. Resolved Roadblocks (append-only)

```
### RB-<NNN> (resolved [YYYY-MM-DD])
- Resolution: <one sentence>
- Resolved by: `agent:<task-id>`
- Amendment commit: <sha>
- Follow-up test added: <test file>::<test name>
```

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

```
### SA-<NNN>: <parameter>
- Changed: [YYYY-MM-DD]
- From: <old value>
- To: <new value>
- Reason: <one sentence>
- Frozen invariant affected: yes / no
- If yes, PRD amendment: <commit sha>
- Re-verified by: <test file>::<test name>
```

(No entries yet.)

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
- [ ] Capability recall ≥ 0.90 · over-retrieval < 0.20 · HSR@K measured · latency ≤ 1500 ms

### P4 gate
- [ ] Streamlit Submission page renders all seven frozen sections
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