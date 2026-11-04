# Annotation Guideline & Gold Label Schema (Decision D-010)

This document defines the 12-column CSV schema for human-adjudicated gold labels per PRD.md §4.7 and Decision D-010.

## Label CSV Schema

Columns must appear in this exact order:

| Column | Type | Allowed Values / Constraints | Description |
|---|---|---|---|
| `submission_id` | BIGINT | Positive integer | Database primary key of the submission |
| `external_id` | VARCHAR | String | Unique external identifier of the submission |
| `skill_capability` | ENUM | `citation-integrity`, `report-structure`, `code-quality`, `rai-disclosure` | The capability being evaluated |
| `skill_version` | VARCHAR | e.g. `v1`, `v2` | Specific skill version under evaluation |
| `check_id` | VARCHAR | Matches ChecklistItem id | Specific check identifier |
| `gold_verdict` | ENUM | `flag`, `no_flag`, `not_applicable` | Ground-truth compliance verdict |
| `gold_evidence_text` | TEXT | String or empty | Quoted verbatim text supporting the verdict |
| `gold_evidence_location` | VARCHAR | Location grammar (`page:N`, `file:P:L`, etc.) | Exact location of the evidence |
| `annotator_1` | VARCHAR | String identifier | First independent annotator |
| `annotator_2` | VARCHAR | String identifier | Second independent annotator |
| `adjudicator` | VARCHAR | String identifier or empty | Tie-breaker / expert adjudicator |
| `adjudication_status` | ENUM | `pending`, `agreed`, `adjudicated` | Status of dual annotation and adjudication |

## CSV Header

```csv
submission_id,external_id,skill_capability,skill_version,check_id,gold_verdict,gold_evidence_text,gold_evidence_location,annotator_1,annotator_2,adjudicator,adjudication_status
```
*(Document only; no data rows populated in P0).*
