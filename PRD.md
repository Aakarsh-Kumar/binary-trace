# PRD — Grounded, Local-First Skill-Retrieved Compliance Review

| Field | Value |
|---|---|
| Document version | 1.0.0 |
| Status | Frozen for P0 build |
| Owner | Principal Architect |
| Source of truth for | Scope, user stories, out-of-scope boundaries, success metrics |
| Must be read before | ARCHITECTURE.md, INSTRUCTIONS.md, MEMORY.md |
| Amendments | Require a version bump and a row in `MEMORY.md → Decisions Log` |

---

## 1. Core Value Proposition

Student submissions must satisfy four independent compliance conditions — citation integrity, report structure, code quality, and Responsible-AI disclosure sufficiency. Today these are checked by different people, with different tools, under different evidence standards, producing inconsistent feedback that students cannot act on. Existing automation addresses one dimension, assumes cloud inference that moves student data off-institution, and produces plausible flags that reviewers cannot verify. This product is a **single local-first review system** in which each compliance dimension is a retrievable, versioned skill; the agent loads only the skills a submission actually requires, every flag must carry a locatable evidence quotation or it is downgraded rather than surfaced, and run-to-run disagreement is shown to the reviewer instead of being averaged away.

## 2. Single Sentence Objective

> Build a local-first Python system that ingests a student submission, retrieves only the capability-specific skills it needs from a versioned on-disk skill library, executes each skill against a locally hosted Qwen model under an evidence-verification gate, persists every verdict with a full audit trail to MySQL, and exposes the results to a reviewer through a Streamlit dashboard so that precision, recall, false-flag rate, run-to-run consistency, and reviewer time can be measured against a labelled test set.

## 3. Problem Statement (one paragraph, for the paper abstract)

Current practice fragments four checks across different reviewers and tools. Automated helpers address one dimension each, depend on cloud inference, or produce unverifiable flags. No existing system retrieves capability-specific skills to perform all four checks inside one local harness with a shared evidence standard, a shared audit trail, and measured false-positive control.

## 4. Functional Scope — User Stories

The system has **eight capability groups**. Every user story below is in scope for v1. Anything not listed here is out of scope (§5). Each story has an ID used by tests and by `MEMORY.md`.

### 4.1 Ingestion (US-01 to US-05)

- **US-01** — As an operator, I can ingest a prose submission (`.pdf`, `.docx`, `.md`, `.txt`) via CLI and receive a `submission_id`, a SHA-256 of normalized text, and a stored `source_path`.
- **US-02** — As an operator, I can ingest a Python code submission (directory or `.zip`) via CLI and receive a `submission_id`, a SHA-256 of the concatenated file hashes, and a stored `source_path`.
- **US-03** — As an operator, I can ingest a mixed submission (prose + code) and the system records `submission_type = 'mixed'`.
- **US-04** — As an operator, I can re-ingest a submission with the same `external_id`; the system rejects the write with `DuplicateSubmissionError` and does not create a second row.
- **US-05** — As an operator, I can list ingested submissions filtered by `submission_type` and date range via CLI.

### 4.2 Skill Library Management (US-06 to US-12)

- **US-06** — As a skill author, I can add a new skill folder under `skills/<capability>/<version>/` with a `SKILL.md` that conforms to the `SkillFrontmatter` Pydantic schema (ARCHITECTURE.md §5.1). The system rejects any skill whose `capability` does not match the parent folder name.
- **US-07** — As a skill author, I can run `compliance-review skills validate --root skills/` and receive a per-skill pass/fail with the exact Pydantic validation error on failure.
- **US-08** — As a skill author, I can set `eval_status` to `draft`, `evaluating`, or `active` in the frontmatter. Only `active` skills are used in production review (US-15).
- **US-09** — As a maintainer, I can promote a skill version to `active` via `compliance-review skills promote --capability <name> --version <ver>` only if the clean-submission regression suite passes at the threshold in §6 (FFR < 10 % per check). The promotion is written to `audit_log`.
- **US-10** — As a maintainer, I can demote an `active` skill version to `deprecated` via the same CLI; the system keeps historical executions referable.
- **US-11** — As a reviewer, I can view the full `SKILL.md` for any version through the Streamlit `Skill Library` page.
- **US-12** — As a maintainer, the system rejects any skill that declares a `capability` value outside the fixed enum `{citation-integrity, report-structure, code-quality, rai-disclosure}`.

### 4.3 Retrieval (US-13 to US-18)

- **US-13** — As the agent, I classify the submission into a **capability set** before any vector search, using only deterministic signals (see ARCHITECTURE.md §6.2). If `submission_type = 'code'`, the set MUST NOT contain `citation-integrity` or `rai-disclosure`.
- **US-14** — As the agent, for each capability in the set, I retrieve candidate skill versions from the FAISS index and record every candidate with its score in `retrieval_events.candidates`.
- **US-15** — As the agent, I select exactly one `active` version per capability. If no `active` version exists for a needed capability, the submission review aborts with `NoActiveSkillError` and the abort is logged.
- **US-16** — As the agent, I record `retrieval_events.selected` as a list of `{capability, version, reason}` with a one-sentence reason per selection.
- **US-17** — As the agent, I record `token_budget` and `latency_ms` for every retrieval event.
- **US-18** — As a researcher, I can compute **capability-level recall**, **version-level precision@1**, **over-retrieval rate**, and **same-family risk exposure (HSR@K)** from the `retrieval_events` table against gold labels (§6).

### 4.4 Execution (US-19 to US-23)

- **US-19** — As the agent, I execute each selected skill `k` times per submission (default `k = 3`), each run persisted as a distinct row in `skill_executions` with `run_index` 1..k.
- **US-20** — As the agent, for every checklist item I emit a structured verdict `{check_id, verdict, severity, evidence_text, evidence_location, confidence}` conforming to the `ModelVerdict` schema (ARCHITECTURE.md §5.3).
- **US-21** — As the agent, if the model output fails JSON parsing or schema validation, I retry exactly once with the validation error appended to the prompt. On second failure, I persist `status = 'schema_error'` and no verdicts for that execution.
- **US-22** — As the agent, I enforce a severity cap: a verdict with `severity ∈ {high, critical}` is allowed only if `verdict.verdict == 'flag'` AND (`checklist_item.deterministic_only == true` OR at least two of the `k` runs agree on the same check with the same severity).
- **US-23** — As the agent, I record `model_name`, `model_digest`, and `prompt_sha256` for every execution. `model_name` MUST be `qwen3:4b` (Ollama tag). `model_digest` MUST be the resolved SHA-256 returned by the Ollama client.

### 4.5 Evidence Gating (US-24 to US-27)

- **US-24** — As the harness, before any verdict is surfaced to the reviewer, I verify `evidence_location` against the submission source using the algorithm in ARCHITECTURE.md §7.1.
- **US-25** — As the harness, if verification fails, I change `checklist_verdicts.verdict` from `flag` to `unsupported_evidence`, write one row to `evidence_verifications` with `verified = false` and a `failure_reason`, and the Streamlit dashboard MUST NOT display this verdict as a finding.
- **US-26** — As the harness, if verification succeeds, I write one row to `evidence_verifications` with `verified = true`, `located_at`, and `method`.
- **US-27** — As the harness, I MUST NOT relax the evidence verifier to make a test pass. The verifier is a frozen invariant (§8 of INSTRUCTIONS.md).

### 4.6 Consistency (US-28 to US-30)

- **US-28** — As a researcher, I can compute per-check verdict agreement and evidence Jaccard similarity across the `k` runs from `skill_executions` joined to `checklist_verdicts`.
- **US-29** — As the dashboard, when `k` runs disagree on a check (agreement < `STABILITY_THRESHOLD`, default 0.85), the `Submission` page displays all `k` verdicts side by side and marks the check `requires_adjudication`.
- **US-30** — As the dashboard, I MUST NOT majority-vote disagreeing runs into a single displayed verdict. The mode may be shown as a secondary "most common" label but never as the only label.

### 4.7 Reviewer Feedback (US-31 to US-34)

- **US-31** — As a reviewer, on the `Submission` page I can approve, override, request re-run, or escalate any surfaced verdict.
- **US-32** — As a reviewer, an override MUST record a `reason_code` from the fixed enum `{evidence_insufficient, check_not_applicable, model_misread, policy_exception, severity_mismatch, other}`.
- **US-33** — As a reviewer, I can click any verdict and jump to the exact `evidence_location` in the submission viewer.
- **US-34** — As a researcher, I can export reviewer feedback with reason-code distribution from the `Metrics` page.

### 4.8 Metrics and Audit (US-35 to US-38)

- **US-35** — As a researcher, I can run `compliance-review metrics --labels <csv> --out <json>` and receive precision, recall, F1, false-flag rate (per check, per skill), consistency, and confusion matrices.
- **US-36** — As an auditor, I can export `audit_log` rows since a given date via `compliance-review audit export`.
- **US-37** — As an auditor, I can reconstruct for any `submission_id`: which skills were retrieved and why, which model and prompt produced each verdict, what evidence was quoted, and whether the evidence was verified.
- **US-38** — As an auditor, `audit_log` MUST be append-only. No UPDATE or DELETE path in application code MAY target it.

## 5. Out of Scope (STRICT — do not implement, do not stub, do not "prepare for")

This list is a hard boundary against agent feature creep. Any PR implementing an item below MUST be rejected.

- **Cloud inference of any kind.** No OpenAI, Anthropic, Google, Mistral, Cohere, Bedrock, Azure OpenAI, Hugging Face Inference API, or any remote endpoint.
- **TypeScript, JavaScript, Node.js, React, Next.js, Vue, Svelte, or any frontend framework.** The dashboard is Streamlit only. There is no `package.json`. There is no `node_modules`. There is no HTTP API.
- **REST, GraphQL, gRPC, or WebSocket APIs.** The system is a CLI + Streamlit process reading MySQL directly.
- **Authentication, authorization, SSO, multi-tenancy, session management, or RBAC.**
- **Docker, Kubernetes, Helm, Terraform, or cloud deployment manifests.**
- **Message queues:** RabbitMQ, Kafka, Redis pub/sub, Celery, Dramatiq.
- **Non-Python code checking.** Student code quality is in scope **only for Python 3.10+** submissions. No Java, JavaScript, C, C++, Go, Rust, or SQL checking in v1.
- **Non-English submissions.** English only.
- **Writing assistance, rewriting, paraphrasing, or auto-fix of flagged issues.**
- **Plagiarism or similarity detection beyond reference verification.**
- **Annotation user interface.** Labels are authored in a CSV template and imported via CLI. No annotation UI.
- **Graph database** (Neo4j, ArangoDB, Neptune). Skill dependency edges live in `skills/_graph.yaml` and are read as a plain YAML adjacency list.
- **Fine-tuning, LoRA, RLHF, or prompt-tuning** of Qwen.
- **Web scraping** of live sources at request time. Bibliographic resolution uses Crossref and OpenAlex over HTTP with caching.
- **Model output free-form for reviewer-visible text.** All reviewer-visible strings are either deterministic harness strings or quotations from the submission.
- **`torch` imported directly in any harness module.** Transitive dependency only (via `sentence-transformers`).
- **`requests`, `urllib3` direct use, `flask`, `fastapi`, `django`, `aiohttp`, `langchain`, `llama-index`, `chromadb`, `qdrant-client`, `pinecone-client`, `weaviate-client`, `openai`, `anthropic`, `transformers`.**

## 6. Success Metrics and Constraints

Every metric below is measured at the phase gate indicated. No metric is a "nice to have".

### 6.1 Retrieval metrics (measured at P3 gate)

| Metric | Definition | Target |
|---|---|---|
| Capability-level recall | Fraction of gold capabilities present in `retrieval_events.selected` | ≥ 0.90 |
| Version-level precision@1 | Fraction of capabilities where selected version == gold active version | ≥ 0.90 |
| Over-retrieval rate | Fraction of gold-absent capabilities present in `selected` | < 0.20 |
| Same-family risk exposure (HSR@K) | Fraction of queries where a `draft` or `deprecated` version appears in `selected` | Reported per capability; target = 0 |
| Retrieval latency | Wall-clock time for capability gate + version selection | ≤ 1500 ms per submission |

### 6.2 Checklist metrics (measured at P2 and re-measured at P5 gate)

| Metric | Definition | Target |
|---|---|---|
| Per-check precision | True flags / all flags raised | ≥ 0.85 |
| Per-check recall | True flags / all true issues | ≥ 0.80 |
| **False-flag rate (FFR)** per check | Flags raised on clean submissions ÷ (flags raised on clean + flags raised on dirty) | **< 0.10 before any skill is promoted to `active`** |
| Execution error rate | Executions with `status = schema_error` after retry ÷ total executions | < 0.05 |

### 6.3 Consistency metrics (measured at P5 gate)

| Metric | Definition | Target |
|---|---|---|
| Verdict agreement | Fraction of checks where all `k` runs return the same verdict | ≥ 0.85 for `active` skills |
| Evidence Jaccard | Mean Jaccard similarity of quoted evidence spans across runs | ≥ 0.70 |

### 6.4 Review time metrics (measured at P4 pilot)

| Metric | Definition | Target |
|---|---|---|
| Reviewer active time | Median wall-clock time with the Submission page open | ≤ 4 minutes per submission |
| Rework time | Reviewer time on submissions with ≥ 1 override or re-run request | Reported, no hard target in v1 |
| End-to-end execution latency | Ingest → all k runs complete → evidence verified | ≤ 120 s per submission on reference hardware |

### 6.5 Constraints

- **Hardware reference:** RTX 3060 12 GB VRAM, 32 GB RAM, or CPU-only with 16 GB RAM and `num_thread` = 8.
- **Data limits per submission:** PDF ≤ 200 pages, ≤ 50 MB; Python repo ≤ 5,000 LOC, ≤ 500 files; ≤ 500 references in a bibliography.
- **Concurrency:** single-worker execution only. The harness MUST NOT spawn parallel Ollama calls in v1.
- **Network:** the system MUST run fully offline after a one-time model pull and Crossref/OpenAlex cache warm. A test in `tests/integration/test_offline.py` MUST verify this by blocking egress.
- **Storage:** MySQL 8.0.36. `skills/` is version-controlled in Git. `data/` is gitignored.
- **Model:** Ollama tag `qwen3:4b`. The tag MUST NOT change without an amendment to this PRD.

## 7. Milestones (mapped to the implementation plan)

| Milestone | Phase | PRD stories closed | Gate criterion |
|---|---|---|---|
| M0 | P0 | US-01, US-05, US-06, US-07, US-12, US-35 (partial) | Submission ingested; deterministic checks stored; trace view renders |
| M1 | P1 | US-13–US-27, US-19–US-22 | Evidence gate passes on 10 pilot submissions; every flag has a verified location |
| M2 | P2 | US-08, US-31–US-34, US-35 | Dual-annotated set of 60–80 submissions; per-check metrics computed |
| M3 | P3 | US-14–US-18 | Capability recall ≥ 0.90; over-retrieval < 0.20; HSR@K measured |
| M4 | P4 | US-29, US-30, US-33 | Two reviewers complete 20 submissions; reason codes captured |
| M5 | P5 | US-09, US-10, US-36–US-38 | All `active` skills pass clean-submission regression; consistency ≥ 0.85 |

## 8. Non-Functional Requirements

- **Determinism of the harness (not the model).** Given identical inputs and identical model digests, `retrieval_events` and `evidence_verifications` rows MUST be byte-identical across runs. Model output may vary; the gate around it may not.
- **Reproducibility.** Every metric reported in the paper MUST be reconstructible from a `metrics --labels` invocation against a published test-set hash.
- **Auditability.** Every reviewer-visible finding MUST be traceable to exactly one `checklist_verdicts` row, one `evidence_verifications` row, and one `skill_executions` row.
- **Explainability.** Every `flag` MUST carry non-null `evidence_text` and `evidence_location`. There is no "model explains itself" pathway.

## 9. Documents that override this PRD

None. ARCHITECTURE.md, INSTRUCTIONS.md, and MEMORY.md MUST conform to this document. If any of them contradicts this PRD, this PRD wins and the other document must be amended.