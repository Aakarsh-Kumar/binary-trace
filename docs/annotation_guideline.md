# Annotation Guideline & Gold Label Schema (v1.0)

This document defines the ground-truth annotation protocol, 12-column CSV schema, worked examples, and inter-annotator adjudication procedure for gold-standard compliance evaluation in accordance with PRD.md §4.7, PRD.md §6, ARCHITECTURE.md §6, and Decisions D-010 and D-018.

---

## 1. Unit of Annotation

Each gold label represents a ground-truth verdict for a single check tuple:
`($submission_id$, $skill_capability$, $skill_version$, $check_id$)`

- **Granularity**: A submission must have explicit gold rows for every checklist item defined in the evaluated skill version.
- **Allowed Verdict Values (`gold_verdict`)**:
  - `flag`: The submission exhibits a definite, non-compliant defect or violation under the strict criteria of this check.
  - `no_flag`: The submission complies with the requirements of this check (equivalent to `pass`).
  - `not_applicable`: The artifact or section inspected is genuinely absent, out of scope, or uninformative for this specific check (e.g. pure code submission evaluated against prose-only citation formatting, or absence of AI tools legitimately requiring no disclosure).
- **Ambiguity Rule (Absolute Guardrail)**: If the evidence is ambiguous, partial, debatable, or cannot be verified with certainty from the artifact text, annotators **MUST default to `not_applicable` (or `no_flag`), and NEVER to `flag`**. A `flag` label requires incontrovertible proof.

---

## 2. Gold Label 12-Column CSV Schema

The evaluation pipeline consumes gold labels strictly via this 12-column schema in standard UTF-8 CSV:

| Index | Column | Type | Allowed Values / Constraints | Description |
|---|---|---|---|---|
| 1 | `submission_id` | BIGINT | Positive integer matching MySQL DB PK | Database primary key of the submission |
| 2 | `external_id` | VARCHAR | String identifier | Unique external identifier of the submission |
| 3 | `skill_capability` | ENUM | `citation-integrity`, `report-structure`, `code-quality`, `rai-disclosure` | Evaluated capability |
| 4 | `skill_version` | VARCHAR | `v1` | Evaluated skill version |
| 5 | `check_id` | VARCHAR | Valid check ID in skill frontmatter | Specific checklist check ID |
| 6 | `gold_verdict` | ENUM | `flag`, `no_flag`, `not_applicable` | Ground-truth compliance verdict |
| 7 | `gold_evidence_text` | TEXT | Verbatim substring (>= 40 chars when flag) | Exact quoted evidence from artifact, or empty if `no_flag` / `not_applicable` |
| 8 | `gold_evidence_location` | VARCHAR | Location grammar (`section:X`, `file:P:L`, `page:N`) | Exact location within the submission |
| 9 | `annotator_1` | VARCHAR | String identifier | First independent annotator ID (or `agent:bootstrap` in Mode B) |
| 10 | `annotator_2` | VARCHAR | String identifier | Second independent annotator ID (or auditor ID in Mode B) |
| 11 | `adjudicator` | VARCHAR | String identifier or empty | Expert adjudicator resolving disagreements |
| 12 | `adjudication_status` | ENUM | `pending`, `agreed`, `adjudicated` | Inter-annotator consensus status |

### Header Row
```csv
submission_id,external_id,skill_capability,skill_version,check_id,gold_verdict,gold_evidence_text,gold_evidence_location,annotator_1,annotator_2,adjudicator,adjudication_status
```

---

## 3. Worked Examples per Capability

### 3.1. Citation Integrity (`citation-integrity`)

#### Positive Example (True Defect $\rightarrow$ `flag`)
- **Check ID**: `cite-doi-resolvable`
- **Context**: A reference provides a malformed or non-existent DOI: `10.0000/nonexistent.2024.01`.
- **Verdict**: `flag`
- **Gold Evidence Text**: `10.0000/nonexistent.2024.01`
- **Gold Location**: `section:references`
- **Justification**: The DOI syntax prefix or resolution fails deterministic verification against Crossref/DOI resolvers.

#### Negative Example (False-Positive Control $\rightarrow$ `no_flag`)
- **Check ID**: `cite-context-alignment`
- **Context**: Text states: *"Vaswani et al. (2017) introduced the Transformer architecture based entirely on attention mechanisms."* The paper indeed introduced Transformers.
- **Verdict**: `no_flag`
- **Gold Evidence Text**: `""`
- **Gold Location**: `section:related_work`
- **False-Positive Guardrail**: Do not flag citations simply because the citation string is abbreviated or uses colloquial phrasing (e.g. "Vaswani et al.").

---

### 3.2. Report Structure (`report-structure`)

#### Positive Example (True Defect $\rightarrow$ `flag`)
- **Check ID**: `struct-required-sections`
- **Context**: A formal empirical paper submission has only `# Introduction` and `# Conclusion`, completely omitting `# Methods` and `# Results`.
- **Verdict**: `flag`
- **Gold Evidence Text**: `# Introduction\n[Prose]\n# Conclusion\n[Prose]`
- **Gold Location**: `section:headings`
- **Justification**: Mandated structural sections are missing from top-level headings.

#### Negative Example (False-Positive Control $\rightarrow$ `no_flag`)
- **Check ID**: `struct-heading-order`
- **Context**: A paper has `# Background & Related Work` before `# System Architecture` before `# Evaluation`.
- **Verdict**: `no_flag`
- **Gold Evidence Text**: `""`
- **Gold Location**: `section:headings`
- **False-Positive Guardrail**: Allow reasonable synonyms for standard sections (e.g. "Related Work" or "Literature Review" for background, "Evaluation" or "Experiments" for results). Do not flag non-standard headings if core logical flow is intact.

---

### 3.3. Code Quality (`code-quality`)

#### Positive Example (True Defect $\rightarrow$ `flag`)
- **Check ID**: `code-syntax-valid`
- **Context**: `calc.py` has an unclosed bracket or unindented block: `def add(a, b):\nreturn a + b`.
- **Verdict**: `flag`
- **Gold Evidence Text**: `def add(a, b):\nreturn a + b`
- **Gold Location**: `file:calc.py:1-2`
- **Justification**: Python AST parser raises `IndentationError` / `SyntaxError`.

#### Negative Example (False-Positive Control $\rightarrow$ `no_flag`)
- **Check ID**: `code-secrets-absent`
- **Context**: `config.py` contains `API_KEY = os.getenv("API_KEY", "")` or dummy placeholders like `SECRET = "your-api-key-here"`.
- **Verdict**: `no_flag`
- **Gold Evidence Text**: `""`
- **Gold Location**: `file:config.py:5`
- **False-Positive Guardrail**: Generic placeholders and standard environment variable fallbacks are not leaked credentials. Do not flag placeholder values.

---

### 3.4. RAI Disclosure (`rai-disclosure`)

#### Positive Example (True Defect $\rightarrow$ `flag`)
- **Check ID**: `rai-tool-named`
- **Context**: The text includes: *"We utilized commercial large language models to rephrase our survey results and format tables."* but does not name any specific model or tool.
- **Verdict**: `flag`
- **Gold Evidence Text**: `We utilized commercial large language models to rephrase our survey results and format tables.`
- **Gold Location**: `section:methodology`
- **Justification**: The submission acknowledges AI assistance but violates the requirement to specify tool name and version.

#### Negative Example (False-Positive Control $\rightarrow$ `no_flag`)
- **Check ID**: `rai-section-present`
- **Context**: A pure theoretical mathematics or proofs paper with zero generative AI usage includes no AI disclosure section.
- **Verdict**: `no_flag` (or `not_applicable`)
- **Gold Evidence Text**: `""`
- **Gold Location**: `section:all`
- **False-Positive Guardrail**: Do not flag absence of AI disclosure in papers that did not employ AI tools. When in doubt whether AI was used, default to `no_flag` or `not_applicable`.

---

## 4. Annotation Modes & Protocol

Annotation may be performed under either of two sanctioned modes:

### Mode A: Full Dual Human Annotation
1. **Independent Labeling**: Two human annotators independently annotate all $N$ submissions across all checks.
2. **Agreement Calculation**: Calculate inter-annotator agreement (Cohen's $\kappa$) across binary flag/no-flag decisions. Target $\kappa \ge 0.70$.
3. **Adjudication**: Any disagreement between Annotator 1 and Annotator 2 is resolved by an independent Adjudicator. Rows with consensus become `agreed`; resolved rows become `adjudicated`.

### Mode B: Agent-First-Pass with Human Audit (25% Stratified Sample)
1. **Bootstrap Pass**: Run the baseline compliance review pipeline (`compliance-review labels bootstrap`) to generate provisional labels with `annotator_1 = "agent:bootstrap"`.
2. **Human Audit**: A qualified human annotator independently audits and labels a stratified 25% sample of submissions across all 4 capabilities, covering:
   - All flagged checks in the bootstrap pass (high sensitivity checks)
   - A random sample of clean passes
   - All known edge cases and rigged pilot controls
3. **Adjudication & Finalization**: The human audit either confirms or overrides the provisional verdict. If confirmed, `annotator_2 = "<human_id>"` and `adjudication_status = "agreed"`. If adjusted, `adjudicator = "<human_id>"` and `adjudication_status = "adjudicated"`.

---

## 5. Metrics Ingestion Contract

The evaluation CLI (`compliance-review metrics --labels PATH --out PATH`) reads this CSV:
- Only rows with `adjudication_status IN ('agreed', 'adjudicated')` are included in ground-truth metrics.
- Checks with fewer than 10 gold-flag instances emit `"insufficient_sample"` to avoid unrepresentative sample noise.
