# INSTRUCTIONS — Agent Operational Guardrails

| Field | Value |
|---|---|
| Document version | 1.0.0 |
| Applies to | Every coding agent operating on this repository |
| Conforms to | PRD.md v1.0.0, ARCHITECTURE.md v1.0.0 |
| Enforcement | Pre-commit hooks + CI + human review |

These are not suggestions. A commit that violates any rule below MUST be rejected, even if it makes tests pass.

---

## 1. Pre-Flight Reading (before writing any code)

Before writing or modifying any file, the agent MUST read, in this order:

1. `PRD.md` — to confirm the change maps to an in-scope user story.
2. `ARCHITECTURE.md` — to confirm the file, table, endpoint, dependency, or directory already exists.
3. `MEMORY.md` — to confirm the change does not repeat a logged roadblock or contradict a logged decision.
4. The specific files the change touches, and their immediate importers/importees.

If the change requires anything not defined in these documents, **stop**. Write the request to `MEMORY.md → Active Roadblocks` with the proposed amendment, and do not write code.

## 2. Source-of-Truth Hierarchy

When two documents disagree, resolve in this order:

1. `PRD.md` (scope and metrics)
2. `ARCHITECTURE.md` (stack, schema, layout, algorithms)
3. `INSTRUCTIONS.md` (process)
4. `MEMORY.md` (history and decisions)
5. Existing code

If the existing code contradicts (1)–(3), the code is wrong. Fix the code, do not amend the documents unless (1) or (2) explicitly authorises it.

## 3. Mandatory Verification Loop

After **every file write or edit**, run the following commands in this exact order, from the repo root:

```bash
uv run ruff check src/ tests/ scripts/
uv run ruff format --check src/ tests/ scripts/
uv run mypy --strict src/
uv run pytest -q tests/unit
```

For changes that touch `db/`, `harness/`, `evidence/`, or `retrieval/`, additionally run:

```bash
uv run pytest -q tests/integration
```

If any command fails:

1. Read the failure output in full.
2. Fix the smallest possible surface that resolves it.
3. Re-run the full loop from step 1.

Do not run the next command in the loop until the previous one passes. Do not commit while any command fails. Do not "fix" a failing test by weakening the test unless §8 (Frozen Invariants) allows it.

## 4. Schema-Verification Rule (no hallucinated tables or columns)

Before writing any code that reads or writes a table:

1. Open `src/compliance_review/db/tables.py`. Confirm the table and column exist as SQLAlchemy `Column` objects.
2. Open `migrations/versions/`. Confirm a migration exists that creates the table with the expected columns and types.
3. If either check fails, **do not write the query**. Amend `ARCHITECTURE.md §4`, add an Alembic migration, run `alembic upgrade head` against a local test DB, and only then write the query.

The same rule applies to:

- Pydantic schemas: confirm the field exists in `skills/schema.py` or `model/schema_validation.py` before referencing it.
- CLI commands: confirm the command exists in `cli.py` before documenting or invoking it.
- Streamlit pages: confirm the page exists in `dashboard/pages/` before linking to it.

## 5. Dependency Rule

A dependency may be added to `pyproject.toml` only if:

1. It appears in `ARCHITECTURE.md §2` with a pinned range.
2. The pin matches the range in §2 exactly.
3. `uv lock` succeeds and the diff to `uv.lock` is committed in the same commit.
4. `MEMORY.md → Decisions Log` has a row recording the addition.

Adding a dependency not in §2 requires a PRD amendment. Adding a banned dependency is a rejected commit regardless of justification.

## 6. Skill Folder Rule

- A new skill MUST live at `skills/<capability>/v<major>/SKILL.md`.
- `<capability>` MUST be one of the four enum values in `PRD.md §4.2 US-12`.
- `SKILL.md` frontmatter MUST validate against `SkillFrontmatter` via `uv run compliance-review skills validate`.
- A new skill MUST start at `eval_status: draft`. It MUST NOT be committed with `eval_status: active`.
- Promotion to `active` happens only via `uv run compliance-review skills promote ...` after the clean-submission regression suite passes. Editing the frontmatter to `active` directly is a rejected commit.

## 7. Audit-Log Rule

- No code outside `db/repository.py::append_audit` may write to `audit_log`.
- No code may contain `UPDATE audit_log` or `DELETE FROM audit_log`.
- Every mutation of `submissions`, `skill_executions`, `checklist_verdicts`, `evidence_verifications`, or `reviewer_feedback` MUST be accompanied by exactly one `append_audit` call in the same transaction.
- A test in `tests/integration/test_audit_append_only.py` MUST verify that an `UPDATE` or `DELETE` attempted against `audit_log` fails at the MySQL grant level.

## 8. Frozen Invariants (never weakened by an agent)

The following are frozen. An agent MUST NOT change them to make a test pass. If a test fails against a frozen invariant, the test is wrong or the surrounding code is wrong — never the invariant.

1. **Evidence verifier thresholds** (`ARCHITECTURE.md §7.1`):
   - `prefix_len = 40`
   - `fuzzy_threshold = 0.92`
   - normalization = NFKC + whitespace collapse + casefold
2. **Capability gate is deterministic** (`§6.2`). No model call, no vector call, before the capability set is decided.
3. **Model tag is `qwen3:4b`** (`PRD.md §6.5`). `model_digest` must be recorded per execution.
4. **`k = 3`** default (`PRD.md §4.4 US-19`). Lowering `k` for tests is allowed only via explicit fixture override, never in `Settings`.
5. **Disagreement is shown, not averaged** (`PRD.md §4.6 US-30`).
6. **`unsupported_evidence` verdicts are never shown as findings** (`PRD.md §4.5 US-25`).
7. **`audit_log` is append-only** (`PRD.md §4.8 US-38`).
8. **No cloud call at runtime** (`PRD.md §6.5`).

## 9. Error Handling Protocol

When any of the following occurs, follow the stated protocol exactly.

### 9.1 Assertion failure in a test

1. Reproduce the failure locally with `uv run pytest -q tests/path::test_name -x -vv`.
2. Determine whether the test is correct against the PRD/ARCHITECTURE. If the test is correct, fix the code.
3. If the test asserts a frozen invariant (§8), do not touch the invariant. Log the failure to `MEMORY.md → Test Failures` with: test name, error, suspected cause, and the two alternatives you considered.
4. If the test is wrong (asserts behaviour not in the PRD), amend the test and note the amendment in `MEMORY.md → Decisions Log`.

### 9.2 Model output fails schema validation

1. Do NOT relax the Pydantic schema. Do NOT add `Optional` fields to make parsing succeed.
2. Confirm `schema_validation.py` retries exactly once with the validation error appended to the prompt (US-21).
3. If both attempts fail, confirm `skill_executions.status = 'schema_error'` was written and no verdicts were persisted for that execution.
4. Log the raw output to `MEMORY.md → Roadblocks` with the skill, version, and prompt hash.

### 9.3 Evidence verifier rejects a flag that "looks correct"

1. Do NOT modify the verifier.
2. Inspect `evidence_verifications.failure_reason`. If `location_grammar_invalid`, fix the prompt in `model/prompts.py` so the model emits a valid location. If `not_located`, the model fabricated or paraphrased the quote — this is the failure mode the verifier exists to catch. Log it to `MEMORY.md → Roadblocks`.
3. Strengthen the skill's `evidence_requirement` text in `SKILL.md` if the model repeatedly paraphrases.

### 9.4 MySQL migration fails

1. Do NOT edit an applied migration in `migrations/versions/`. Alembic migrations are immutable once applied.
2. Create a new migration that corrects the schema.
3. Record the correction in `MEMORY.md → Schema Changes`.

### 9.5 Ollama not reachable or model tag missing

1. Do NOT substitute a different model tag.
2. Do NOT fall back to a cloud provider.
3. Emit `ModelError` with a clear message; the CLI exits with code `2`.
4. Log to `MEMORY.md → Roadblocks`.

## 10. Forbidden Patterns (rejected on sight)

- `print()` anywhere in `src/`.
- `logging.getLogger` in `src/`.
- `requests`, `urllib3`, `aiohttp` imports in `src/`.
- `torch` imported in `src/`.
- `openai`, `anthropic`, `google.generativeai`, `cohere`, `transformers` imports anywhere.
- `import json` used to parse model output — use `model/schema_validation.py` only.
- Raw SQL string literals outside `db/tables.py` and `db/repository.py`.
- Prompt string literals outside `model/prompts.py`.
- `# type: ignore` without a `# reason: ...` comment and a row in `MEMORY.md → Decisions Log`.
- `except Exception:` without re-raising as a `ComplianceError` subclass.
- `try: ... except: pass`.
- `TODO`, `FIXME`, `XXX` in committed code. These belong in `MEMORY.md → Active Roadblocks`.
- `eval_status: active` set directly in `SKILL.md` (must go through `skills promote`).
- Any `.ts`, `.tsx`, `.js`, `.jsx`, `package.json`, `node_modules/`, `Dockerfile`, `docker-compose.yml`.
- Any change to `audit_log` schema or grants without a PRD amendment.
- Any change to `evidence/verifier.py` without a PRD amendment.

## 11. Commit Discipline

- One user story per commit. Commit message prefix: `US-<id>: <short description>`.
- Every commit runs the verification loop (§3) locally; the pre-commit hook enforces `ruff` and `mypy`.
- Every commit that touches `db/tables.py` also touches `migrations/versions/` and `ARCHITECTURE.md §4`.
- Every commit that touches `skills/` also updates `MEMORY.md → Verified Implementations`.
- Every commit that adds a dependency touches `pyproject.toml`, `uv.lock`, `ARCHITECTURE.md §2`, and `MEMORY.md → Decisions Log`.

## 12. When Stuck

If the agent cannot proceed without inventing something (a table, a dependency, an endpoint, a directory, a model tag, a prompt technique):

1. Stop.
2. Write the blocker to `MEMORY.md → Active Roadblocks` with:
   - What is blocked.
   - What the agent wanted to invent.
   - The two alternative approaches considered.
   - The amendment to PRD.md or ARCHITECTURE.md that would unblock it.
3. Do not write code.
4. Do not "temporarily" implement the invention behind a feature flag.

Hallucination is a failure mode. Logging the blocker and waiting is the correct behaviour.

## 13. Escalation

If a rule in this document appears to conflict with a user instruction, the user instruction wins only if it is accompanied by an explicit amendment to `PRD.md` or `ARCHITECTURE.md`. Verbal or in-chat override of a rule in §8 (Frozen Invariants) is not accepted.