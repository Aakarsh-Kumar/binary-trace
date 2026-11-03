# ARCHITECTURE — Grounded, Local-First Skill-Retrieved Compliance Review

| Field | Value |
|---|---|
| Document version | 1.0.0 |
| Status | Frozen for P0 build |
| Conforms to | PRD.md v1.0.0 |
| Source of truth for | Stack, schemas, endpoints, directory layout, algorithms |

This document is the sole authority for what the codebase may import, what tables may exist, what commands may exist, and where files may live. If a coding agent needs a library, table, endpoint, or directory that is not listed here, the agent MUST stop and write the request to `MEMORY.md → Active Roadblocks`.

---

## 1. The Three Design Commitments

These are not optional. They are enforced by the file layout and by INSTRUCTIONS.md rules.

1. **Capability-gated retrieval.** `src/compliance_review/retrieval/capability_gate.py` determines the capability set from deterministic signals before any vector search runs. There is no similarity-first retrieval path.
2. **Evidence-gated flagging.** `src/compliance_review/evidence/verifier.py` is invoked for every verdict before any verdict is surfaced. It cannot be bypassed, disabled by config, or relaxed by test.
3. **Disagreement as a first-class output.** `src/compliance_review/harness/k_run.py` stores every run and computes agreement. The dashboard reads agreement from the DB, not from a recomputation.

## 2. Allowed Tech Stack — Pinned

**Rule:** every dependency below is allowed at the pinned range. No other dependency may be added to `pyproject.toml` without an amendment to this document, a row in `MEMORY.md → Decisions Log`, and a passing `uv lock`.

### 2.1 Runtime and tooling

| Component | Allowed | Banned |
|---|---|---|
| Python | `3.11.x` (exact patch recorded in `.python-version`) | 3.10, 3.12, PyPy |
| Package manager | `uv >= 0.5, < 0.6` | pip, poetry, conda, pipenv |
| Build backend | `hatchling` | setuptools, flit, pdm |
| Linter + formatter | `ruff >= 0.6, < 0.7` | black, flake8, isort, pylint on own code |
| Type checker | `mypy >= 1.11, < 1.12` with `--strict` | pyright, pyre |
| Test runner | `pytest >= 8.3, < 8.4` + `pytest-cov >= 5.0, < 6` | unittest, nose, tox |
| Pre-commit | `pre-commit >= 3.7, < 4` | — |

### 2.2 Data and persistence

| Component | Allowed | Banned |
|---|---|---|
| Database | MySQL `>= 8.0.36, < 8.1` (tested on 8.0.36; dev runs 8.0.39) | Postgres, SQLite, MariaDB, DuckDB for results |
| DB driver | `PyMySQL >= 1.1, < 1.2` | mysql-connector-python, asyncmy, aiomysql |
| DB access | `SQLAlchemy >= 2.0.30, < 2.1` — **Core only** (`Table`, `select`, `insert`, `update`, `text`) | SQLAlchemy ORM (declarative_base, Session.query, mapped_column), Django ORM, Peewee, Tortoise |
| Migrations | `Alembic >= 1.13, < 1.14` | hand-written DDL outside Alembic |
| Config | `pydantic-settings >= 2.5, < 3` reading only environment variables and `.env.local` | PyYAML configs, Hydra, dynaconf, OmegaConf |

### 2.3 Model and inference

| Component | Allowed | Banned |
|---|---|---|
| Inference server | Ollama server ≥ 0.3, model tag `qwen3:4b` | vLLM, TGI, llama-cpp-python, transformers, LM Studio |
| Ollama client | `ollama >= 0.3, < 0.4` (Python) | direct HTTP to Ollama, `requests` |
| Sampling defaults | `temperature=0.0`, `top_p=1.0`, `seed=<run_index>`, `num_predict=2048`, `format="json"` | random sampling, dynamic temperature |
| Digest recording | MUST read `client.show(model).digest` and store in `skill_executions.model_digest` | — |

**Model digest rule:** the harness MUST refuse to execute if `model_digest` cannot be resolved. Silent fallback to another tag is forbidden.

### 2.4 Retrieval and embeddings

| Component | Allowed | Banned |
|---|---|---|
| Vector index | `faiss-cpu >= 1.8, < 1.9` with a persisted index file in `data/vector_index/` | Chroma, Qdrant, Pinecone, Weaviate, pgvector, MySQL VECTOR |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2`, pinned by commit hash in `skills/_meta.yaml` | OpenAI embeddings, Cohere, BGE-M3 (in v1) |
| Embedding runtime | `sentence-transformers >= 3.0, < 4` | importing `torch` directly anywhere in `src/` |
| Similarity | cosine, computed on L2-normalized vectors | dot product on unnormalized vectors, Euclidean |

### 2.5 Ingestion and parsing

| Component | Allowed | Banned |
|---|---|---|
| PDF | `pymupdf >= 1.24, < 1.25` | pdfplumber, pypdf, PDFMiner |
| DOCX | `python-docx >= 1.1, < 2` | docx2txt, mammoth |
| Markdown | stdlib + `markdown-it-py >= 3.0, < 4` | mistune, markdown2 |
| HTTP for Crossref/OpenAlex | `httpx >= 0.27, < 0.28` with `http2=True`, timeout 10 s, retries 2 | `requests`, `urllib3`, `aiohttp` |
| Fuzzy match for evidence | stdlib `difflib.SequenceMatcher` | rapidfuzz, fuzzywuzzy, thefuzz |
| Code static analysis | `ruff` invoked as a subprocess, and `pylint` invoked as a subprocess **on student code only** | importing astroid directly, bandit, semgrep |

### 2.6 CLI, logging, dashboard

| Component | Allowed | Banned |
|---|---|---|
| CLI | `typer >= 0.12, < 0.13` | argparse, click directly, docopt |
| Logging | `structlog >= 24.1, < 25` emitting JSON to stdout and to a rotating file in `data/logs/` | `print`, stdlib `logging` used directly |
| Dashboard | `streamlit >= 1.38, < 1.40`, entrypoint `src/compliance_review/dashboard/app.py` | React, Next.js, Vue, FastAPI, Flask, Dash, Gradio, Reflex |
| Dashboard state | Streamlit `session_state` only, cache via `st.cache_data(ttl=60)` | Redis, in-memory global state, pickle caches |

### 2.7 Validation

| Component | Allowed | Banned |
|---|---|---|
| Schemas | `pydantic >= 2.8, < 3` | attrs, dataclasses-json, marshmallow, jsonschema directly |
| Datetime | stdlib `datetime` with `timezone.utc` everywhere | pendulum, arrow, pytz-locals |

```
compliance-review/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
├── .pre-commit-config.yaml
├── alembic.ini
├── README.md
├── PRD.md
├── ARCHITECTURE.md
├── INSTRUCTIONS.md
├── MEMORY.md
├── AGENTS.md
├── src/
│   └── compliance_review/
│       ├── __init__.py
│       ├── config.py                     # pydantic-settings Settings object
│       ├── logging.py                    # structlog configuration
│       ├── errors.py                     # exception taxonomy (§8)
│       ├── db/
│       │   ├── __init__.py
│       │   ├── engine.py                 # SQLAlchemy Engine factory
│       │   ├── tables.py                 # SQLAlchemy Core Table definitions ONLY
│       │   └── repository.py             # insert/select helpers; the ONLY writer to DB
│       ├── skills/
│       │   ├── __init__.py
│       │   ├── schema.py                 # SkillFrontmatter, ChecklistItem (pydantic)
│       │   ├── loader.py                 # discovers skills/, parses SKILL.md
│       │   └── registry.py               # in-memory registry; read-only after load
│       ├── retrieval/
│       │   ├── __init__.py
│       │   ├── capability_gate.py        # deterministic classifier (§6.2)
│       │   ├── vector_index.py           # FAISS wrapper (build, load, query)
│       │   └── selector.py               # version selection within capability
│       ├── model/
│       │   ├── __init__.py
│       │   ├── qwen_client.py            # ollama client wrapper
│       │   ├── prompts.py                # ALL prompt templates; no inline prompts elsewhere
│       │   └── schema_validation.py      # parse + validate ModelOutput
│       ├── checks/
│       │   ├── __init__.py
│       │   ├── deterministic/
│       │   │   ├── __init__.py
│       │   │   ├── citation.py           # DOI resolution, retraction, duplicate detection
│       │   │   ├── structure.py          # section presence, heading order, citation style
│       │   │   ├── code.py               # ruff + pylint subprocess orchestration
│       │   │   └── disclosure.py         # structured field presence
│       │   └── model_based/
│       │       ├── __init__.py
│       │       ├── citation.py           # claim-support judgment
│       │       ├── structure.py          # semantic coherence explanation
│       │       ├── code.py               # explains / prioritises static findings
│       │       └── disclosure.py         # sufficiency judgment
│       ├── evidence/
│       │   ├── __init__.py
│       │   └── verifier.py               # locate-or-discard gate (§7.1); FROZEN
│       ├── harness/
│       │   ├── __init__.py
│       │   ├── orchestrator.py           # run_submission()
│       │   └── k_run.py                  # k-run loop + agreement computation
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── pdf.py
│       │   ├── docx.py
│       │   ├── markdown.py
│       │   └── repo.py
│       ├── metrics/
│       │   ├── __init__.py
│       │   └── compute.py                # precision, recall, FFR, consistency
│       ├── dashboard/
│       │   ├── __init__.py
│       │   ├── app.py                    # Streamlit entrypoint
│       │   └── pages/
│       │       ├── 01_submission.py
│       │       ├── 02_skill_library.py
│       │       └── 03_metrics.py
│       └── cli.py                        # typer app
├── skills/                               # DATA, not code — version-controlled
│   ├── _meta.yaml                        # embedding model pin, index version
│   ├── _graph.yaml                       # adjacency list of capability dependencies
│   ├── citation-integrity/
│   │   └── v1/
│   │       ├── SKILL.md
│   │       └── resources/
│   ├── report-structure/
│   ├── code-quality/
│   └── rai-disclosure/
├── data/                                 # GITIGNORED
│   ├── submissions/
│   ├── labels/
│   ├── vector_index/
│   ├── cache/
│   └── logs/
├── migrations/                           # Alembic only
│   ├── env.py
│   ├── versions/
│   └── manual/                           # admin-run SQL (grants)
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
│   └── annotation_guideline.md
└── scripts/
    ├── ingest.py
    ├── run_review.py
    ├── compute_metrics.py
    └── fetch_datasets.py
```

**Frozen rules:**
- No new top-level directories under `src/compliance_review/` without amending this section.
- No `.py` file may be placed at the repo root except `conftest.py` (if needed).
- Dashboard pages must be numbered (`01_`, `02_`, `03_`) and live only under `dashboard/pages/`.
- No prompts may be string literals outside `model/prompts.py`.
- No SQL may be string literals outside `db/tables.py` and `db/repository.py`.

## 4. Database Schema (MySQL 8.0.x — see D-011)

All tables `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`. All timestamps are UTC.

### 4.1 `submissions`

```sql
CREATE TABLE submissions (
  id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  external_id     VARCHAR(128) NOT NULL,
  submission_type ENUM('prose','code','mixed') NOT NULL,
  source_path     VARCHAR(512) NOT NULL,
  content_sha256  CHAR(64)     NOT NULL,
  ingested_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_external (external_id),
  KEY idx_type (submission_type),
  KEY idx_sha (content_sha256)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4.2 `retrieval_events`

```sql
CREATE TABLE retrieval_events (
  id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  submission_id   BIGINT UNSIGNED NOT NULL,
  capability_set  JSON            NOT NULL,
  candidates      JSON            NOT NULL,
  selected        JSON            NOT NULL,
  token_budget    INT             NOT NULL,
  latency_ms      INT             NOT NULL,
  created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_re_sub FOREIGN KEY (submission_id) REFERENCES submissions(id),
  KEY idx_re_sub (submission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4.3 `skill_executions`

```sql
CREATE TABLE skill_executions (
  id               BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  submission_id    BIGINT UNSIGNED NOT NULL,
  skill_capability VARCHAR(64)     NOT NULL,
  skill_version    VARCHAR(32)     NOT NULL,
  run_index        TINYINT UNSIGNED NOT NULL,
  model_name       VARCHAR(128)    NOT NULL,
  model_digest     CHAR(64)        NOT NULL,
  prompt_sha256    CHAR(64)        NOT NULL,
  raw_output       LONGTEXT        NULL,
  parsed_output    JSON            NULL,
  status           ENUM('ok','parse_error','schema_error','timeout','error') NOT NULL,
  latency_ms       INT             NOT NULL,
  created_at       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_se_sub FOREIGN KEY (submission_id) REFERENCES submissions(id),
  UNIQUE KEY uq_se (submission_id, skill_capability, skill_version, run_index),
  KEY idx_se_skill (submission_id, skill_capability)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4.4 `checklist_verdicts`

```sql
CREATE TABLE checklist_verdicts (
  id               BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  execution_id     BIGINT UNSIGNED NOT NULL,
  check_id         VARCHAR(64)     NOT NULL,
  verdict          ENUM('pass','flag','not_applicable','unsupported_evidence','execution_error') NOT NULL,
  severity         ENUM('low','medium','high','critical') NOT NULL,
  evidence_text    TEXT            NULL,
  evidence_location VARCHAR(512)   NULL,
  confidence       DECIMAL(3,2)    NULL,
  created_at       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_cv_exec FOREIGN KEY (execution_id) REFERENCES skill_executions(id),
  KEY idx_cv_exec_check (execution_id, check_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4.5 `evidence_verifications`

```sql
CREATE TABLE evidence_verifications (
  id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  verdict_id     BIGINT UNSIGNED NOT NULL,
  verified       BOOLEAN         NOT NULL,
  located_at     VARCHAR(512)    NULL,
  method         ENUM('substring','normalized','fuzzy','none') NOT NULL,
  failure_reason VARCHAR(256)    NULL,
  created_at     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ev_verdict FOREIGN KEY (verdict_id) REFERENCES checklist_verdicts(id),
  KEY idx_ev_verdict (verdict_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4.6 `reviewer_feedback`

```sql
CREATE TABLE reviewer_feedback (
  id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  submission_id BIGINT UNSIGNED NOT NULL,
  verdict_id    BIGINT UNSIGNED NULL,
  reviewer_id   VARCHAR(64)     NOT NULL,
  action        ENUM('approve','override','request_rerun','escalate') NOT NULL,
  reason_code   ENUM('evidence_insufficient','check_not_applicable','model_misread','policy_exception','severity_mismatch','other') NULL,
  comment       TEXT            NULL,
  created_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_rf_sub FOREIGN KEY (submission_id) REFERENCES submissions(id),
  CONSTRAINT fk_rf_verdict FOREIGN KEY (verdict_id) REFERENCES checklist_verdicts(id),
  KEY idx_rf_sub (submission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4.7 `audit_log` (append-only, enforced by GRANT)

```sql
CREATE TABLE audit_log (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  actor       VARCHAR(64)     NOT NULL,
  action      VARCHAR(64)     NOT NULL,
  table_name  VARCHAR(64)     NOT NULL,
  row_id      BIGINT UNSIGNED NULL,
  before_json JSON            NULL,
  after_json  JSON            NULL,
  created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_al_table_row (table_name, row_id),
  KEY idx_al_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Grant rule (executed once by a DBA, in `migrations/manual/0002_grants.sql`):**

```sql
REVOKE UPDATE, DELETE ON compliance_review.audit_log FROM 'app_user'@'%';
GRANT INSERT, SELECT ON compliance_review.audit_log TO 'app_user'@'%';
```

Alembic does not run this. It is a manual admin step documented in `README.md`. Recorded in `MEMORY.md → Decisions Log` as **D-008**.

## 5. Pydantic Schemas

All schemas live in `src/compliance_review/skills/schema.py` and `src/compliance_review/model/schema_validation.py`. They are the ONLY definition of these shapes.

### 5.1 `SkillFrontmatter`

```python
Capability = Literal["citation-integrity", "report-structure", "code-quality", "rai-disclosure"]
EvalStatus = Literal["draft", "evaluating", "active", "deprecated"]
Severity   = Literal["low", "medium", "high", "critical"]

class ChecklistItem(BaseModel):
    id: str
    question: str
    severity: Severity
    evidence_requirement: str
    deterministic_only: bool = False
    advisory: bool = False
    false_positive_guardrails: list[str] = []

class SkillFrontmatter(BaseModel):
    capability: Capability
    version: str
    description: str
    inputs: list[Literal["prose", "pdf", "code_repo", "disclosure_section"]]
    checklist: list[ChecklistItem] = Field(min_length=1)
    deterministic_preconditions: list[str] = []
    false_positive_guardrails: list[str] = []
    eval_status: EvalStatus
    owner: str
    created_at: date
    model_config = ConfigDict(extra="forbid")
```

### 5.2 `RetrievalSelection`

```python
class SelectionEntry(BaseModel):
    capability: Capability
    version: str
    reason: str
    score: float
    stage: Literal["capability_gate", "faiss"]

class RetrievalDecision(BaseModel):
    capability_set: dict[Capability, bool]
    candidates: list[SelectionEntry]
    selected: list[SelectionEntry]
    token_budget: int
    latency_ms: int
```

### 5.3 `ModelOutput` and `ModelVerdict`

```python
class ModelVerdict(BaseModel):
    check_id: str
    verdict: Literal["pass", "flag", "not_applicable"]
    severity: Severity
    evidence_text: str | None
    evidence_location: str | None
    confidence: float = Field(ge=0.0, le=1.0)

class ModelOutput(BaseModel):
    capability: Capability
    verdicts: list[ModelVerdict]
    model_config = ConfigDict(extra="forbid")
```

**Location grammar** (enforced by `verifier.py`):

```
page:<int>                          e.g. page:12
file:<path>:<line>                  e.g. file:src/foo.py:47
section:<slug>                      e.g. section:references
table:<name>                        e.g. table:results
bbox:<x>,<y>,<w>,<h>                e.g. bbox:120,340,480,20
```

## 6. Retrieval Architecture

### 6.1 Two stages (fixed order)

1. **Capability gate** — deterministic, no model call, no vector call.
2. **Version selection** — FAISS retrieval within the gated capability families, followed by `active`-status filter.

There is no stage where Qwen decides which capability to use. The model is never the router.

### 6.2 Capability gate rules (deterministic)

| Submission type | Capabilities enabled |
|---|---|
| `prose` | `citation-integrity`, `report-structure`, `rai-disclosure` |
| `code` | `code-quality` |
| `mixed` | all four |

Within `mixed`:

- `citation-integrity` requires a bibliography detected by `ingestion/` (`.bib`, `.ris`, or a `References` heading).
- `rai-disclosure` requires a disclosure section by heading keyword (`Disclosure`, `AI Use`, `Responsible AI`) OR a top-level `DISCLOSURE.md`.
- `report-structure` requires prose length ≥ 500 words.

Disabled capabilities are recorded in `retrieval_events.capability_set` as `false` with a `gate_reason` string.

### 6.3 Version selection

- Query FAISS with `SKILL.md` frontmatter text of every candidate version of an enabled capability.
- Filter to `eval_status == 'active'`.
- If multiple `active`, select highest score, `reason = "highest_faiss_score"`.
- If exactly one, select it, `reason = "only_active"`.
- If none, raise `NoActiveSkillError`.

### 6.4 Same-family risk exposure (HSR@K)

Every `retrieval_events.candidates` row includes **all** versions above `MIN_CANDIDATE_SCORE` (default 0.30), including `draft` and `deprecated`. `metrics/compute.py` computes:

```
HSR@K = count(queries where any candidate has eval_status in {draft, deprecated} and score >= MIN_CANDIDATE_SCORE) / count(queries)
```

## 7. Evidence Verifier (FROZEN — do not modify without PRD amendment)

### 7.1 `verify_evidence(evidence_text, evidence_location, submission) -> EvidenceResult`

```
1. Parse evidence_location using the grammar in §5.3. On parse failure: return
   {verified: False, method: "none", failure_reason: "location_grammar_invalid"}.

2. Resolve the source span:
   - page:N      -> PyMuPDF page N text (1-indexed)
   - file:P:L    -> line L of file P in the code repo (1-indexed)
   - section:S   -> text of the section whose slug matches S
   - table:T     -> the rendered table T as text
   - bbox:x,y,w,h -> PDF text within the bounding box

3. Normalize the source span and the evidence_text:
   - Unicode NFKC
   - collapse all whitespace to single space
   - casefold

4. Try exact substring match. If found: return {verified: True, method: "substring"}.

5. Try matching the first 40 normalized characters of evidence_text as a
   prefix of the source span. If found: {verified: True, method: "normalized"}.

6. Try difflib.SequenceMatcher(None, evidence_text, source_span).ratio().
   If ratio >= 0.92: {verified: True, method: "fuzzy"}.

7. Return {verified: False, method: "none", failure_reason: "not_located"}.
```

### 7.2 Downstream effect

```
for verdict in verdicts where verdict.verdict == "flag":
    result = verify_evidence(verdict.evidence_text, verdict.evidence_location, submission)
    write evidence_verifications row
    if not result.verified:
        UPDATE checklist_verdicts SET verdict = 'unsupported_evidence' WHERE id = verdict.id
        write audit_log row (action = "evidence_downgrade")
```

The dashboard MUST NOT display `unsupported_evidence` under the "Findings" heading.

### 7.3 Frozen invariant

The verifier MUST NOT be modified to make a test pass. If a test fails because the verifier rejects evidence, the fix is in the skill's evidence requirement or the model prompt — never in the verifier. Enforced by `tests/unit/test_verifier_invariant.py`, which asserts the signature and the three thresholds (`prefix_len = 40`, `fuzzy_threshold = 0.92`, `normalization = NFKC+collapse+casefold`) are unchanged.

## 8. Error Taxonomy

All exceptions live in `src/compliance_review/errors.py`. No bare `Exception` or `ValueError` may be raised in `src/`. Every exception subclasses `ComplianceError`.

```python
class ComplianceError(Exception): ...
class IngestError(ComplianceError): ...
class DuplicateSubmissionError(IngestError): ...
class SkillValidationError(ComplianceError): ...
class NoActiveSkillError(ComplianceError): ...
class RetrievalError(ComplianceError): ...
class ModelError(ComplianceError): ...
class ModelSchemaError(ModelError): ...
class EvidenceVerificationError(ComplianceError): ...
class DatabaseError(ComplianceError): ...
```

## 9. CLI Reference (the ONLY interface)

```
compliance-review ingest --source PATH --type {prose|code|mixed} [--external-id TEXT]
compliance-review review --submission-id INT [--k INT=3] [--deterministic-only]
compliance-review skills validate --root PATH=skills/
compliance-review skills promote --capability TEXT --version TEXT
compliance-review skills demote  --capability TEXT --version TEXT
compliance-review metrics --labels PATH --out PATH
compliance-review audit export --since YYYY-MM-DD --out PATH
compliance-review index rebuild
```

Exit codes: `0` success · `1` validation/ingestion · `2` runtime · `3` invariant violation.

`--deterministic-only` (D-009) runs the gate + deterministic checks, skips Qwen, and is used for the P0 gate demonstration.

## 10. Streamlit Dashboard

### 10.1 Pages (three only)

| Page | File | Reads |
|---|---|---|
| Submission review | `pages/01_submission.py` | `submissions`, `retrieval_events`, `skill_executions`, `checklist_verdicts`, `evidence_verifications` |
| Skill library | `pages/02_skill_library.py` | `skills/` on disk + `skill_executions` |
| Metrics | `pages/03_metrics.py` | `metrics/compute.py` output cached to `data/cache/` |

### 10.2 Submission page layout (frozen order)

1. **Header** — `external_id`, `submission_type`, `ingested_at`
2. **Retrieval trace** — capability chips, selected versions, latency
3. **Findings** — `verdict == 'flag'` AND verified, grouped by capability, sorted severity desc
4. **Disagreement view** — checks with agreement < 0.85, all `k` runs side by side
5. **Passed checks** — collapsed
6. **Unsupported (not shown to student)** — collapsed
7. **Audit footer** — model tag + digest, skill versions, prompt hashes

### 10.3 Forbidden in dashboard code

- `st.write()` for anything except debug to hidden expander
- Direct SQL (all reads through `db/repository.py`)
- Any recomputation of agreement, FFR, or precision
- Any write to DB except through `db/repository.py::record_reviewer_feedback`

## 11. Structlog JSON Schema

```json
{
  "ts": "ISO-8601 UTC",
  "level": "info|warning|error",
  "event": "snake_case_event_name",
  "component": "cli|ingestion|retrieval|model|evidence|harness|db|dashboard",
  "submission_id": 0,
  "execution_id": null,
  "skill_capability": null,
  "skill_version": null,
  "run_index": null,
  "latency_ms": 0,
  "error": null,
  "detail": {}
}
```

`print()` is banned in `src/`. `logging.getLogger` is banned in `src/`.

## 12. Naming Conventions

| Artefact | Convention | Example |
|---|---|---|
| Python modules | `snake_case.py` | `capability_gate.py` |
| Python classes | `PascalCase` | `SkillFrontmatter` |
| Python functions | `snake_case` | `verify_evidence` |
| Skill capability folders | `kebab-case` | `rai-disclosure/` |
| Skill version folders | `v<major>` | `v1/` |
| DB tables | `snake_case`, plural | `skill_executions` |
| DB columns | `snake_case`, singular | `evidence_location` |
| CLI commands | `kebab-case`, verb-noun | `skills validate` |
| Env vars | `SCREAMING_SNAKE`, prefix `CR_` | `CR_MYSQL_DSN` |
| Streamlit pages | `<NN>_<slug>.py` | `01_submission.py` |
| Branches | `feat/<id>-<slug>`, `fix/<id>-<slug>` | `feat/us-20-evidence-gate` |

## 13. Config Object (`src/compliance_review/config.py`)

```python
class Settings(BaseSettings):
    cr_mysql_dsn: str
    cr_ollama_host: str = "http://127.0.0.1:11434"
    cr_ollama_model: str = "qwen3:4b"
    cr_k_runs: int = 3
    cr_fuzzy_threshold: float = 0.92
    cr_stability_threshold: float = 0.85
    cr_min_candidate_score: float = 0.30
    cr_vector_index_path: Path = Path("data/vector_index/skills.faiss")
    cr_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    cr_log_dir: Path = Path("data/logs")
    cr_cache_dir: Path = Path("data/cache")
    model_config = SettingsConfigDict(env_file=".env.local", extra="forbid")
```

`cr_fuzzy_threshold` and `cr_stability_threshold` MUST match §7.1 and PRD §6.3 respectively. A mismatch is a startup error.

`.env.example` (committed) — the agent will create this from §13:

```
CR_MYSQL_DSN=mysql+pymysql://app_user:CHANGE_ME@localhost:3306/compliance_review
CR_OLLAMA_HOST=http://127.0.0.1:11434
CR_OLLAMA_MODEL=qwen3:4b
CR_K_RUNS=3
```

`.env.local` (gitignored, human-created with real values) — the agent will not create this and will ask you for the DSN.

## 14. What ARCHITECTURE.md does NOT define (and agents must not invent)

- No additional tables. Amend §4 first.
- No additional endpoints. There is no endpoint.
- No additional CLI commands. Amend §9 first.
- No additional dashboard pages. Three only.
- No additional exception classes outside §8.
- No additional capabilities beyond the four in §5.1.
- No additional model tags beyond `qwen3:4b`.

Any of the above requires a PRD amendment, a row in `MEMORY.md → Decisions Log`, and a version bump to this document.