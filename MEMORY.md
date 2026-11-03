# MEMORY — Agent Boot Notebook

| Field | Value |
|---|---|
| Document version | 1.0.0 |
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
| Current phase | P0 |
| Last completed milestone | — |
| Active branch | `main` |
| Last green commit | — |
| Unit test count | 0 |
| Integration test count | 0 |
| Skills at `eval_status: active` | 0 |
| Skills at `eval_status: draft` | 0 |
| Known failing tests | 0 |
| Open roadblocks | 2 (RB-001, RB-002) |
| Frozen invariants intact | yes |

**Environment (recorded at P0 preflight 2026-11-04):**

| Component | Required | Actual | Status |
|---|---|---|---|
| Python | 3.11.x | 3.12.5 (system); uv-managed 3.11 pending | RB-002 |
| uv | 0.5.x | not installed at preflight | RB-003 |
| MySQL | 8.0.x (D-011) | 8.0.39 | RB-001 closed via D-011; PATH pending |
| Ollama | ≥ 0.3 | 0.40.13 | PASS |
| qwen3:4b | present | present (`359d7dd4bcda`) | PASS |
| Git | clean tree | no commits yet | initial commit pending |

**Frozen invariant checklist (verified each commit):**
- [ ] Evidence verifier thresholds unchanged (`prefix_len=40`, `fuzzy_threshold=0.92`)
- [ ] Capability gate has no model/vector call
- [ ] Model tag is `qwen3:4b`, `model_digest` recorded
- [ ] `k = 3` default in `Settings`
- [ ] Disagreement not averaged in dashboard
- [ ] `unsupported_evidence` not shown as findings
- [ ] `audit_log` append-only grant intact
- [ ] No cloud call in `tests/integration/test_offline.py`

---

## 2. Verified Implementations

Template:

```
### [YYYY-MM-DD] <component path> — <user story>
- Verified by: `agent:<task-id>` | `human:<initials>`
- Commit: <sha>
- Tests: <test file>::<test name>
- Behaviour: <one sentence>
- Depends on: <list of modules / tables>
- Supersedes: <entry-id or "none">
```

(No entries yet.)

---

## 3. Active Roadblocks

```
### RB-<NNN>: <short title>
- Opened: [YYYY-MM-DD]
- Opened by: `agent:<task-id>`
- Phase / user story: P<n> / US-<id>
- What is blocked: <one sentence>
- What the agent wanted to invent: <schema / dependency / endpoint / directory / tag>
- Alternatives considered:
  1. <alternative> — rejected because <reason>
  2. <alternative> — rejected because <reason>
- Amendment required: <PRD.md §x.y | ARCHITECTURE.md §x.y>
- Status: open
```

### RB-001: MySQL patch version differs from pin
- Opened: 2026-11-04
- Opened by: `agent:preflight`
- Phase / user story: P0 / setup
- What is blocked: nothing (resolution is D-011)
- What the agent wanted to invent: nothing
- Alternatives considered: downgrade to 8.0.36 (rejected — no schema impact), amend pin (chosen)
- Amendment required: ARCHITECTURE.md §2.2
- Status: **closed via D-011**

### RB-002: Python 3.11.x not installed
- Opened: 2026-11-04
- Opened by: `agent:preflight`
- Phase / user story: P0 / setup
- What is blocked: P0 task 1 (repo skeleton) cannot create `.python-version` or venv
- What the agent wanted to invent: use Python 3.12 (rejected — ARCHITECTURE.md §2.1 bans 3.12)
- Alternatives considered:
  1. Amend pin to 3.12 — rejected; downgrades reproducibility, 3.12 has wheel gaps for pinned deps
  2. `uv python install 3.11` — chosen; preserves the pin, no amendment needed
- Amendment required: none
- Status: open — resolution: agent runs `uv python install 3.11` after uv is installed (RB-003)

### RB-003: uv not on PATH
- Opened: 2026-11-04
- Opened by: `agent:preflight`
- Phase / user story: P0 / setup
- What is blocked: all of P0
- What the agent wanted to invent: pip (rejected — ARCHITECTURE.md §2.1 bans pip)
- Alternatives considered:
  1. pip install uv — allowed as bootstrap; uv governs thereafter
  2. official installer — `irm https://astral.sh/uv/install.ps1 | iex`
- Amendment required: none
- Status: open — human to install

---

## 4. Resolved Roadblocks (append-only)

```
### RB-<NNN> (resolved [YYYY-MM-DD])
- Resolution: <one sentence>
- Resolved by: `agent:<task-id>`
- Amendment commit: <sha>
- Follow-up test added: <test file>::<test name>
```

(RB-001 resolved by D-011 on 2026-11-04; awaiting ARCHITECTURE.md amendment commit.)

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

---

## 7. Test Failures and Resolutions (append-only)

```
### TF-<NNN>: <test name>
- Date: [YYYY-MM-DD]
- Test: `tests/<path>::<name>`
- Error: <first line of failure>
- Suspected cause: <one sentence>
- Alternatives considered: 1. <fix> — <outcome>; 2. <fix> — <outcome>
- Resolution: <one sentence>
- Frozen invariant touched: yes / no
- Resolved by: `agent:<task-id>`
- Commit: <sha>
```

(No entries yet.)

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
- [ ] `submissions` table created via Alembic migration `0001_initial.py`
- [ ] `compliance-review ingest` works on prose, code, mixed submissions
- [ ] `compliance-review skills validate` passes on four seed `SKILL.md` (draft)
- [ ] `compliance-review review --deterministic-only` prints trace: capability_set, gate_reason, deterministic verdicts, latency_ms
- [ ] `capability_gate.py` imports no model or faiss module (`test_gate_purity.py`)
- [ ] `audit_log` rejects UPDATE and DELETE at MySQL grant level (`test_audit_append_only.py`)
- [ ] `test_offline.py` passes with egress blocked
- [ ] `test_verifier_invariant.py` passes, asserting frozen thresholds
- [ ] `ruff`, `ruff format --check`, `mypy --strict`, unit and integration tests all green
- [ ] `data/raw/MANIFEST.json` exists and lists all seven datasets (or roadblocks)
- [ ] Frozen invariant checklist (§1) all ticked

### P1 gate
- [ ] Ollama reachable, `qwen3:4b` digest recorded in `skill_executions`
- [ ] `ModelOutput` schema validation with one retry
- [ ] Evidence verifier downgrades fabricated evidence on 10 pilot submissions
- [ ] Every surfaced `flag` has a verified `evidence_verifications` row
- [ ] k=3 stored per skill per submission

### P2 gate
- [ ] Labelled set 60–80 submissions, dual-annotated, adjudicated
- [ ] `docs/annotation_guideline.md` published
- [ ] `compliance-review metrics` produces per-check precision/recall/FFR/consistency
- [ ] FFR < 0.15 per check (target < 0.10 before promotion)

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