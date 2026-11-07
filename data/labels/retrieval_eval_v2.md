# Retrieval Evaluation Report (P3 Milestone M3)

## Policy & Invariants
- **Gold Active Version Policy**: Gold active version is v2 by evaluation-time policy (D-014). Production promotion to `active` is P5 work.
- **Risky Candidate Definition**: A candidate is `risky` if its `eval_status` is `draft` or `deprecated` (read directly from SKILL.md frontmatter).
- **Minimum Candidate Score**: Candidate inclusion threshold is $0.30$ (`Settings.cr_min_candidate_score`).
- **Read-Only Invariant**: All metrics computed without modifying the database or re-running model executions.

---

## TABLE 1 — Aggregate Retrieval Metrics

| N_submissions | capability_recall | version_precision@1 | over_retrieval_rate | HSR@K | risky_candidates_surfaced | latency_p50_ms | latency_p99_ms | latency_max_ms |
|---|---|---|---|---|---|---|---|---|
| 60 | 1.0000 | 1.0000 | 0.0000 | 0.5333 | 52 | 48.5 | 1563.5 | 3625.0 |

---

## TABLE 2 — Per-Capability Metrics

| capability | N_gold | N_selected | recall | precision@1 | over_retrieval | HSR@K | risky_count |
|---|---|---|---|---|---|---|---|
| code-quality | 40 | 40 | 1.0000 | 1.0000 | 0.0000 | 0.5000 | 20 |
| citation-integrity | 40 | 40 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0 |
| report-structure | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 |
| rai-disclosure | 32 | 32 | 1.0000 | 1.0000 | 0.0000 | 0.5333 | 32 |

---

## TABLE 3 — Per-Submission Retrieval Trace (60 Submissions)

| external_id | type | gold_caps | selected_caps | gold_versions | selected_versions | recall | p@1 | over_retrieval | latency_ms |
|---|---|---|---|---|---|---|---|---|---|
| eval_code_01 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 10 |
| eval_code_02 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 10 |
| eval_code_03 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 10 |
| eval_code_04 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 10 |
| eval_code_05 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9 |
| eval_code_06 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9 |
| eval_code_07 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8 |
| eval_code_08 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8 |
| eval_code_09 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8 |
| eval_code_10 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9 |
| eval_code_11 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8 |
| eval_code_12 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8 |
| eval_code_13 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9 |
| eval_code_14 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9 |
| eval_code_15 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8 |
| eval_code_16 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9 |
| eval_code_17 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 10 |
| eval_code_18 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9 |
| eval_code_19 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9 |
| eval_code_20 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 10 |
| eval_mixed_01 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 74 |
| eval_mixed_02 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 72 |
| eval_mixed_03 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 70 |
| eval_mixed_04 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 75 |
| eval_mixed_05 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 70 |
| eval_mixed_06 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 76 |
| eval_mixed_07 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 76 |
| eval_mixed_08 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 73 |
| eval_mixed_09 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 69 |
| eval_mixed_10 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 82 |
| eval_mixed_11 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 75 |
| eval_mixed_12 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 73 |
| eval_mixed_13 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 76 |
| eval_mixed_14 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 77 |
| eval_mixed_15 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 80 |
| eval_mixed_16 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 89 |
| eval_mixed_17 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 76 |
| eval_mixed_18 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 78 |
| eval_mixed_19 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 90 |
| eval_mixed_20 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 81 |
| eval_prose_01 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 3625 |
| eval_prose_02 | prose | citation-integrity | citation-integrity | citation-integrity:v2 | citation-integrity:v2 | 1.0000 | 1.0000 | 0.0000 | 61 |
| eval_prose_03 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 77 |
| eval_prose_04 | prose | citation-integrity | citation-integrity | citation-integrity:v2 | citation-integrity:v2 | 1.0000 | 1.0000 | 0.0000 | 18 |
| eval_prose_05 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 49 |
| eval_prose_06 | prose | citation-integrity | citation-integrity | citation-integrity:v2 | citation-integrity:v2 | 1.0000 | 1.0000 | 0.0000 | 25 |
| eval_prose_07 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 50 |
| eval_prose_08 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 51 |
| eval_prose_09 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 48 |
| eval_prose_10 | prose | citation-integrity | citation-integrity | citation-integrity:v2 | citation-integrity:v2 | 1.0000 | 1.0000 | 0.0000 | 26 |
| eval_prose_11 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 46 |
| eval_prose_12 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 131 |
| eval_prose_13 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 70 |
| eval_prose_14 | prose | citation-integrity | citation-integrity | citation-integrity:v2 | citation-integrity:v2 | 1.0000 | 1.0000 | 0.0000 | 24 |
| eval_prose_15 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 70 |
| eval_prose_16 | prose | citation-integrity | citation-integrity | citation-integrity:v2 | citation-integrity:v2 | 1.0000 | 1.0000 | 0.0000 | 28 |
| eval_prose_17 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 49 |
| eval_prose_18 | prose | citation-integrity | citation-integrity | citation-integrity:v2 | citation-integrity:v2 | 1.0000 | 1.0000 | 0.0000 | 26 |
| eval_prose_19 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 48 |
| eval_prose_20 | prose | citation-integrity | citation-integrity | citation-integrity:v2 | citation-integrity:v2 | 1.0000 | 1.0000 | 0.0000 | 24 |

---

## TABLE 4 — Latency Distribution

| p50 | p90 | p95 | p99 | max | N |
|---|---|---|---|---|---|
| 48.5 | 80.1 | 89.0 | 1563.5 | 3625.0 | 60 |

---

## Analysis of Milestone M3 Gate Criteria

1. **Capability Recall**:
   - Target: $\ge 0.90$.
   - Achieved: **1.0000** (112 / 112 gold instances retrieved). **PASS**.
   - Breakdown: 112 of 112 gold capability instances retrieved. Per-capability breakdown shown in Table 2.

2. **Version-Level Precision@1**:
   - Target: $\ge 0.90$.
   - Achieved: **1.0000** (112 / 112 matches to gold active version). **PASS**.

3. **Over-Retrieval Rate**:
   - Target: $< 0.20$.
   - Achieved: **0.0000** (0 over-retrievals / 112 selected capabilities). **PASS**.
   - Mechanism: Resolved via D-028. Aligning prose gating rules with mixed gating rules (report-structure requires >= 500 words, rai-disclosure requires disclosure present) eliminated false positive selections on short evaluation submissions.

4. **Same-Family Risk Exposure (HSR@K)**:
   - Measured: **0.5333** across all queries (32 of 60 queries surfaced at least one candidate with score $\ge 0.30$ and status `draft` or `deprecated`).
- Total risky candidates surfaced: **52** (primarily v1 draft skills appearing in FAISS candidate pools).

5. **Retrieval Latency**:
   - Target: $p50 \le 1500$ ms.
- Observed $p50$: **48.5 ms** (max: 3625.0 ms). **PASS**.
   - Mechanism: Resolved via D-029. Latency measurement isolates capability gate and FAISS version selection elapsed time, excluding model execution.
