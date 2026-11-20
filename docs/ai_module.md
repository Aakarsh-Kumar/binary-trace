# AI / ML Module — Developer Guide

This guide describes the AI/ML parts of the compliance review system as they are implemented in `src/compliance_review/`. Where the code differs from `ARCHITECTURE.md`, this guide describes the code.

## 1. Pipeline overview

`harness/orchestrator.py::run_review()` runs one review end to end:

```
submission (DB row)
  -> parse_submission_content()                      ingestion/orchestrator.py
  -> determine_capability_set()   capability gate    retrieval/capability_gate.py
  -> select_skill_version()       FAISS selection    retrieval/selector.py
  -> for each selected capability, k runs:
       run_single_capability_execution()             harness/k_run.py
         deterministic checks                        checks/deterministic/*.py
         model-based checks (Qwen via Ollama)        checks/model_based/*.py
  -> verify_evidence() on every flag                 evidence/verifier.py
  -> apply_severity_cap_to_runs()                    harness/severity_cap.py
  -> compute_k_run_agreement()                       harness/k_run.py
  -> record_skill_execution_run()  persist + downgrade unverified flags   db/repository.py
  -> record_retrieval_event()                        db/repository.py
```

Order note: in the code, evidence verification runs **before** the severity cap. The verifier attaches a `verification_result` to each flag. The cap then adjusts severities. The downgrade of unverified flags to `unsupported_evidence` happens when the verdicts are persisted (`db/repository.py::record_skill_execution_run` → `apply_evidence_downgrade`, which also writes an `evidence_downgrade` row to `audit_log`).

With `--deterministic-only`, the FAISS stage is skipped: every enabled capability gets `v1` with `reason = "deterministic_gate_enabled"`, `score = 1.0`, `stage = "capability_gate"`, and no model call is made.

## 2. Qwen3-4B on Ollama

Implemented in `model/qwen_client.py`.

| Setting | Value in code |
|---|---|
| Model tag | `MODEL_NAME = "qwen3:4b"` (hard-coded) |
| `temperature` | `0.0` |
| `top_p` | `1.0` |
| `seed` | `run_index` (1..k), so each of the k runs uses a different seed |
| `num_predict` | `2048` |
| `format` | `"json"` |
| `think` | `False` (sent on the `/api/generate` request path) |
| `stream` | `False` |

**Model digest rule.** `resolve_model_digest()` is called on every `call_qwen()`. It tries `client.show("qwen3:4b").digest`, then falls back to finding `qwen3:4b` in `client.list()`. If neither returns a digest it raises `ModelError` ("Ensure 'ollama pull qwen3:4b' has been run"). There is no fallback to another model.

**Prompting** (`model/prompts.py::build_evaluation_prompt`): one prompt per capability per run. It contains:
- a system instruction;
- the JSON output schema, with `"<capability_name>"` replaced by the actual capability;
- a canonical check-ID list (D-046) built by `get_canonical_checklist_for_capability()` from `skills/<capability>/<version>/SKILL.md` (model-based items first, then deterministic ones, each group sorted by ID) and formatted by `format_canonical_enumeration()` as "Your response MUST contain a verdict for EACH of these N check_ids …";
- the submission text, truncated to 12,000 characters.

Prose submissions are told to use `page:1` locations. Code submissions are told to use `file:<relative_path>:<line_number>`. `CITATION_CHECK_GUIDANCE` is still defined but is currently not added to the prompt (`citation_guidance = ""`).

**Output validation** (`model/schema_validation.py`):
- Markdown code fences are stripped. The text is parsed as JSON and validated against `ModelOutput` (`capability`, `verdicts: list[ModelVerdict]`, `extra="forbid"`). A capability mismatch is an error.
- When `canonical_check_ids` is passed (as every model-based check does, with all check IDs of the skill's checklist), any verdict whose `check_id` is not in that set raises `ModelSchemaError("Hallucinated check_id …")` (D-045). `validate_model_output()` wraps this.
- On a JSON or schema failure, the model is retried **exactly once** with `build_retry_prompt(validation_error, raw_output)`.
- A second failure returns `status = "schema_error"` with no verdicts. An Ollama call failure on the first attempt returns `status = "error"`.

`ModelVerdict` fields (`skills/schema.py`): `check_id`, `verdict ∈ {pass, flag, not_applicable}`, `severity ∈ {low, medium, high, critical}`, `evidence_text`, `evidence_location`, `confidence ∈ [0, 1]`, `check_source ∈ {deterministic, model}`.

Note: in `harness/k_run.py`, the stored `prompt_sha256` for a model run is the SHA-256 of the **raw model output** text. For deterministic-only runs it is `sha256(b"deterministic_only")`.

## 3. Embeddings and FAISS

Implemented in `retrieval/vector_index.py`.

| Item | Value |
|---|---|
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` (loaded lazily and cached; pinned to commit `a52431d044e99f1ab84bfa4f971c26b91c498305` in `skills/_meta.yaml`) |
| Similarity | cosine: vectors are L2-normalized with `faiss.normalize_L2`, and the index is `faiss.IndexFlatIP` (inner product) |
| Index files | `data/vector_index/skills.faiss` and `data/vector_index/skills_meta.json` |
| Granularity | one vector per skill version (`skills/<capability>/<version>/SKILL.md`) |

Text embedded per skill version (`format_skill_text`):

```
Capability: <capability>. Version: <version>. Status: <eval_status>. Description: <description>. Inputs: <inputs, comma-joined>. Checklist: <all checklist questions, space-joined>
```

`skills_meta.json` stores `capability`, `version`, `eval_status`, `description`, `inputs` and `checklist_count` per vector.

**Query text** (built in `orchestrator.py`): `"Submission type: <type>. Content: <first 1000 chars of extracted text>"`. It is embedded and normalized the same way, and searched with `top_k=20`.

If the index files are missing, `load_skills_index()` builds them on the fly. To rebuild explicitly after editing skills:

```bash
uv run compliance-review index rebuild
```

Options: `--skills-root` (default `skills`) and `--index-dir` (default `data/vector_index`).

## 4. Skill retrieval and selection

### 4.1 Capability gate (`retrieval/capability_gate.py`)

This step is deterministic only. The module must not import model code, `sentence_transformers`, `torch` or `faiss`. It returns a `capability_set` (capability → bool) and a reason string per capability.

| Submission type | citation-integrity | report-structure | code-quality | rai-disclosure |
|---|---|---|---|---|
| `prose` | on if bibliography signal* | on if `word_count >= 500` | **off** | on if disclosure signal** |
| `code` | **off** | **off** | **on** | **off** |
| `mixed` | on if bibliography signal* | on if `word_count >= 500` | **on** | on if disclosure signal** |

\* Bibliography signal: `references_present`, or the lower-cased text contains `references`, `bibliography`, `.bib` or `.ris`.
\** Disclosure signal: `disclosure_present`, `has_disclosure_file`, or the text contains `disclosure`, `ai use` or `responsible ai`.

An unknown submission type raises `ValueError`.

### 4.2 Version selection (`retrieval/selector.py::select_skill_version`)

1. Query FAISS (`top_k=20`) and keep the results for this capability.
2. **Candidates**: every result with `score >= MIN_CANDIDATE_SCORE` (`0.30`), of **any** status, recorded with `reason = "faiss_candidate_status_<status>"`. These go to `retrieval_events.candidates`.
3. **Matching**: results whose `eval_status` equals the requested `skill_status` (CLI `--skill-status`, default `active`; `all` matches everything). Note: matching is not limited to candidates above the score threshold.
4. If nothing matches, raise `NoActiveSkillError`.
5. Sort by score, descending. If exactly one matches, choose it with `reason = "only_active"` (or `only_<status>` when `--skill-status` is not `active`). If several match, choose the top one with `reason = "highest_faiss_score"`.

**Current skill status.** Every `v1` is `draft` and every `v2` is `evaluating`. No version is `active`, so a default `review` (without `--deterministic-only`) raises `NoActiveSkillError`. Use `--skill-status evaluating` to run the v2 hybrid skills.

`skills promote` and `skills demote` are not implemented yet (both exit with code 3, "not implemented until P5"). Use `skills set-status`:

```bash
uv run compliance-review skills set-status --capability code-quality --version v2 --status active
```

## 5. The four compliance skills

Skills are defined by `SKILL.md` frontmatter (validated by `SkillFrontmatter` in `skills/schema.py`, loaded by `skills/loader.py`). The `v1` versions contain only the three deterministic checks per capability. The `v2` versions add two model-based checks each:

| Capability | Deterministic checks (`deterministic_only: true`) | Model-based checks (v2 only) |
|---|---|---|
| `citation-integrity` | `cite-doi-resolvable` (high), `cite-not-retracted` (critical), `cite-no-duplicates` (low) | `cite-claim-supported` (high), `cite-context-accurate` (medium) |
| `report-structure` | `struct-required-sections` (high), `struct-heading-order` (medium), `struct-minimum-length` (medium) | `struct-semantic-coherence` (medium), `struct-claim-evidence-alignment` (high) |
| `code-quality` | `code-ruff-clean` (critical), `code-file-loc-limit` (medium), `code-pylint-clean` (low) | `code-error-handling` (medium), `code-modularity` (medium) |
| `rai-disclosure` | `rai-section-present` (high), `rai-tool-named` (medium), `rai-task-named` (medium) | `rai-sufficiency-judgment` (high), `rai-human-oversight-described` (medium) |

Severities shown are the checklist defaults from `skills/*/v2/SKILL.md`.

What the deterministic checks do today:

| Check | Implementation |
|---|---|
| `cite-doi-resolvable` | Finds DOIs with a regex (`10.\d{4,9}/...`). Flags a DOI only if it contains `invalid` or starts with `10.0000/`. No network lookup. |
| `cite-not-retracted` | Always returns `pass` (placeholder). |
| `cite-no-duplicates` | Flags repeated reference entries. |
| `struct-required-sections` | Looks for `introduction`, `method`, `result` and `discussion` in the lower-cased text. |
| `struct-heading-order` | Checks that those keywords first appear in that order. |
| `struct-minimum-length` | Flags `word_count < 500`. |
| `code-file-loc-limit` | Flags any file over 300 lines. |
| `code-ruff-clean` | Runs `python -m ruff check --select E9,F <repo_dir>` as a subprocess and quotes the offending line. |
| `code-pylint-clean` | Always returns `pass` (pylint is not invoked). |
| `rai-section-present` | Looks for the headings `disclosure`, `ai use`, `responsible ai` or `ai assistance`, or a `DISCLOSURE.md` file. |
| `rai-tool-named` | Matches known tool names (`chatgpt`, `copilot`, `claude`, `gemini`, `gpt-4`, `qwen`, `llama`), or a negative disclosure ("no AI", "did not use", …). |
| `rai-task-named` | Extracts the tasks described in the disclosure. |

Deterministic verdicts are filtered to the check IDs in the selected skill's checklist.

## 6. Deterministic vs model-based checks

| | Deterministic | Model-based |
|---|---|---|
| Location | `checks/deterministic/{citation,structure,code,disclosure}.py` | `checks/model_based/{citation,structure,code,disclosure}.py` |
| Engine | Python rules, regex, `ruff` subprocess | `qwen3:4b` via Ollama, one prompt per capability per run |
| Selected by | checklist items with `deterministic_only: true` | checklist items with `deterministic_only: false` |
| `check_source` | `deterministic` | `model` |
| Runs with `--deterministic-only` | yes | no |
| Run-to-run variation | none (identical across k runs) | possible (`seed = run_index`) |
| Input | extracted text, word count, file dict, repo dir | prose text (citation, structure, disclosure), or up to 10 files × 2,000 chars (code), truncated to 12,000 chars in the prompt |
| Failure mode | — | `schema_error` after one retry; `error` if Ollama fails |
| Severity cap | high/critical always allowed on a flag | high/critical allowed only if ≥ 2 runs agree |
| Evidence verification | yes, on every flag | yes, on every flag |

Each model-based check module keeps only model verdicts whose `check_id` is one of that skill's model-based items, and only the first verdict per `check_id`. Model verdicts for deterministic IDs are dropped. In a run, `combined_verdicts = deterministic verdicts + model verdicts`.

## 7. Three-run evaluation (k-runs)

`k` defaults to 3 through the CLI option `review --k`. `Settings.cr_k_runs` exists in `config.py` but the review path does not read it. Each run gets `run_index = previous max for that capability/version + 1..k` and is stored as its own `skill_executions` row.

### 7.1 Agreement (`harness/k_run.py::compute_k_run_agreement`)

For each `check_id`:

```
agreement = (count of the most common verdict across runs) / k
```

### 7.2 Evidence Jaccard

For runs that **flagged** the check and have `evidence_text`, each evidence string is normalized with `normalize_span` (NFKC, collapsed whitespace, casefold) and split into a word set. The score is the mean pairwise Jaccard similarity:

```
J(A, B) = |A ∩ B| / |A ∪ B|
```

If fewer than 2 runs flagged the check, `evidence_jaccard = 1.0`.

Checks whose agreement is below `cr_stability_threshold` (0.85) are shown in the dashboard's Disagreement view.

### 7.3 Severity cap (`harness/severity_cap.py::apply_severity_cap_to_runs`)

A verdict with severity `high` or `critical` keeps it only if:

```
verdict == "flag" AND (checklist item deterministic_only == true
                       OR at least 2 of the k runs flagged this check_id with the same severity)
```

Otherwise its severity is set to `medium`.

### 7.4 Evidence verifier (`evidence/verifier.py`, frozen)

Applied to every `flag`:
1. Parse `evidence_location` (`page:`, `file:<path>:<line>`, `section:`, `table:`, `bbox:`). If parsing fails, the result is `location_grammar_invalid`.
2. Resolve the source span and normalize both texts (NFKC + whitespace collapse + casefold).
3. Exact substring match → `method = "substring"`.
4. Prefix match on the first `PREFIX_LEN = 40` characters → `"normalized"`.
5. `difflib.SequenceMatcher` ratio `>= FUZZY_THRESHOLD = 0.92` → `"fuzzy"`.
6. Otherwise, not verified (`not_located`). The flag is persisted as `unsupported_evidence`.

### 7.5 Metrics (`metrics/compute.py::compute_metrics`)

Run with:

```bash
uv run compliance-review metrics --labels data/labels/gold_labels.csv --out data/labels/eval_v2.json
```

- Gold rows with `adjudication_status` of `agreed`, `adjudicated` or empty are used.
- The prediction for each (submission, check) is taken from `run_index = 1` (or the first run if there is no run 1).
- **Pre-verifier flag**: the verdict is `flag` or `unsupported_evidence`. **Post-verifier flag**: the verdict is `flag`.
- Per check: `pre_verifier_precision`, `pre_verifier_recall`, `post_verifier_precision`, `post_verifier_recall`, `post_verifier_ffr`, 2×2 confusion matrices (pre and post), `consistency_agreement`, and evidence Jaccard.
  - precision = TP / (TP + FP)
  - recall = TP / (TP + FN)
  - FFR = FP / (FP + TP)
- If a check has fewer than `MIN_GOLD_FLAG_SAMPLE = 10` gold flags, its precision, recall and FFR values are reported as `"insufficient_sample"`.
- Summary values include overall pre/post precision and recall, overall post-verifier FFR, overall consistency agreement and overall Jaccard.

Retrieval metrics (capability recall, version precision@1, over-retrieval rate, HSR@K and latency percentiles) are computed by `scripts/compute_retrieval_metrics.py`, not `metrics/compute.py`. HSR@K counts the queries where any candidate has status `draft` or `deprecated` with a score of at least 0.30.

## 8. File map

| Concern | File |
|---|---|
| Review orchestration | `src/compliance_review/harness/orchestrator.py` |
| k-run loop, agreement, Jaccard | `src/compliance_review/harness/k_run.py` |
| Severity cap | `src/compliance_review/harness/severity_cap.py` |
| Capability gate | `src/compliance_review/retrieval/capability_gate.py` |
| FAISS index build/load/query, embeddings | `src/compliance_review/retrieval/vector_index.py` |
| Version selection, `MIN_CANDIDATE_SCORE` | `src/compliance_review/retrieval/selector.py` |
| Ollama client, sampling, digest | `src/compliance_review/model/qwen_client.py` |
| Prompt templates | `src/compliance_review/model/prompts.py` |
| JSON parsing, schema validation, retry | `src/compliance_review/model/schema_validation.py` |
| Skill schemas (`SkillFrontmatter`, `ChecklistItem`, `ModelVerdict`, `ModelOutput`, `SelectionEntry`) | `src/compliance_review/skills/schema.py` |
| Skill loading / registry | `src/compliance_review/skills/loader.py`, `src/compliance_review/skills/registry.py` |
| Deterministic checks | `src/compliance_review/checks/deterministic/` |
| Model-based checks | `src/compliance_review/checks/model_based/` |
| Evidence verifier (frozen) | `src/compliance_review/evidence/verifier.py` |
| Persistence, evidence downgrade | `src/compliance_review/db/repository.py` |
| Checklist metrics | `src/compliance_review/metrics/compute.py` |
| Retrieval metrics | `scripts/compute_retrieval_metrics.py` |
| CLI | `src/compliance_review/cli.py` |
| Skill definitions | `skills/<capability>/<version>/SKILL.md` |
| Embedding pin, index version | `skills/_meta.yaml` |
| FAISS index artifacts | `data/vector_index/skills.faiss`, `data/vector_index/skills_meta.json` |

## Relevant CLI commands

```bash
uv run compliance-review review --submission-id 5 --deterministic-only
uv run compliance-review review --submission-id 5 --k 3 --skill-status evaluating
uv run compliance-review index rebuild
uv run compliance-review skills validate --root skills
uv run compliance-review skills set-status --capability rai-disclosure --version v2 --status evaluating
uv run compliance-review metrics --labels data/labels/gold_labels.csv --out data/labels/eval_v2.json
```
