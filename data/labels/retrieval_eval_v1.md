# Retrieval Evaluation Report v1 (P3 Milestone M3)

## Policy & Invariants
- **Gold Active Version Policy**: Gold active version is v2 by evaluation-time policy (D-014). Production promotion to `active` is P5 work.
- **Risky Candidate Definition**: A candidate is `risky` if its `eval_status` is `draft` or `deprecated` (read directly from SKILL.md frontmatter).
- **Minimum Candidate Score**: Candidate inclusion threshold is $0.30$ (`Settings.cr_min_candidate_score`).
- **Read-Only Invariant**: All metrics computed without modifying the database or re-running model executions.

---

## TABLE 1 — Aggregate Retrieval Metrics

| N_submissions | capability_recall | version_precision@1 | over_retrieval_rate | HSR@K | risky_candidates_surfaced | latency_p50_ms | latency_p99_ms | latency_max_ms |
|---|---|---|---|---|---|---|---|---|
| 60 | 0.9107 | 0.9107 | 0.2154 | 0.6333 | 58 | 24730.5 | 34397.9 | 38686.0 |

---

## TABLE 2 — Per-Capability Metrics

| capability | N_gold | N_selected | recall | precision@1 | over_retrieval | HSR@K | risky_count |
|---|---|---|---|---|---|---|---|
| code-quality | 40 | 40 | 1.0000 | 1.0000 | 0.0000 | 0.3333 | 10 |
| citation-integrity | 40 | 30 | 0.7500 | 0.7500 | 0.0000 | 0.0000 | 0 |
| report-structure | 0 | 20 | 0.0000 | 0.0000 | 1.0000 | 0.2000 | 10 |
| rai-disclosure | 32 | 40 | 1.0000 | 1.0000 | 0.2000 | 0.6552 | 38 |

---

## TABLE 3 — Per-Submission Retrieval Trace (60 Submissions)

| external_id | type | gold_caps | selected_caps | gold_versions | selected_versions | recall | p@1 | over_retrieval | latency_ms |
|---|---|---|---|---|---|---|---|---|---|
| eval_code_01 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9222 |
| eval_code_02 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8833 |
| eval_code_03 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9622 |
| eval_code_04 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 10984 |
| eval_code_05 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9026 |
| eval_code_06 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9004 |
| eval_code_07 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9756 |
| eval_code_08 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8881 |
| eval_code_09 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8912 |
| eval_code_10 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8928 |
| eval_code_11 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8927 |
| eval_code_12 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9067 |
| eval_code_13 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9827 |
| eval_code_14 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8951 |
| eval_code_15 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8890 |
| eval_code_16 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 10952 |
| eval_code_17 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 9111 |
| eval_code_18 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8926 |
| eval_code_19 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8952 |
| eval_code_20 | code | code-quality | code-quality | code-quality:v2 | code-quality:v2 | 1.0000 | 1.0000 | 0.0000 | 8964 |
| eval_mixed_01 | mixed | citation-integrity,code-quality,rai-disclosure | code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | code-quality:v2,rai-disclosure:v2 | 0.6667 | 0.6667 | 0.0000 | 19041 |
| eval_mixed_02 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 27215 |
| eval_mixed_03 | mixed | citation-integrity,code-quality,rai-disclosure | code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | code-quality:v2,rai-disclosure:v2 | 0.6667 | 0.6667 | 0.0000 | 19453 |
| eval_mixed_04 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 27506 |
| eval_mixed_05 | mixed | citation-integrity,code-quality,rai-disclosure | code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | code-quality:v2,rai-disclosure:v2 | 0.6667 | 0.6667 | 0.0000 | 19272 |
| eval_mixed_06 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 27485 |
| eval_mixed_07 | mixed | citation-integrity,code-quality,rai-disclosure | code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | code-quality:v2,rai-disclosure:v2 | 0.6667 | 0.6667 | 0.0000 | 19154 |
| eval_mixed_08 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 28078 |
| eval_mixed_09 | mixed | citation-integrity,code-quality,rai-disclosure | code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | code-quality:v2,rai-disclosure:v2 | 0.6667 | 0.6667 | 0.0000 | 19340 |
| eval_mixed_10 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 27221 |
| eval_mixed_11 | mixed | citation-integrity,code-quality,rai-disclosure | code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | code-quality:v2,rai-disclosure:v2 | 0.6667 | 0.6667 | 0.0000 | 19290 |
| eval_mixed_12 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 27345 |
| eval_mixed_13 | mixed | citation-integrity,code-quality,rai-disclosure | code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | code-quality:v2,rai-disclosure:v2 | 0.6667 | 0.6667 | 0.0000 | 19140 |
| eval_mixed_14 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 27388 |
| eval_mixed_15 | mixed | citation-integrity,code-quality,rai-disclosure | code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | code-quality:v2,rai-disclosure:v2 | 0.6667 | 0.6667 | 0.0000 | 19330 |
| eval_mixed_16 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 27513 |
| eval_mixed_17 | mixed | citation-integrity,code-quality,rai-disclosure | code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | code-quality:v2,rai-disclosure:v2 | 0.6667 | 0.6667 | 0.0000 | 19242 |
| eval_mixed_18 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 28094 |
| eval_mixed_19 | mixed | citation-integrity,code-quality,rai-disclosure | code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | code-quality:v2,rai-disclosure:v2 | 0.6667 | 0.6667 | 0.0000 | 22305 |
| eval_mixed_20 | mixed | citation-integrity,code-quality,rai-disclosure | citation-integrity,code-quality,rai-disclosure | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | citation-integrity:v2,code-quality:v2,rai-disclosure:v2 | 1.0000 | 1.0000 | 0.0000 | 27343 |
| eval_prose_01 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 38686 |
| eval_prose_02 | prose | citation-integrity | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.6667 | 27866 |
| eval_prose_03 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 28058 |
| eval_prose_04 | prose | citation-integrity | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.6667 | 29606 |
| eval_prose_05 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 28209 |
| eval_prose_06 | prose | citation-integrity | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.6667 | 30234 |
| eval_prose_07 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 28303 |
| eval_prose_08 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 31418 |
| eval_prose_09 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 28174 |
| eval_prose_10 | prose | citation-integrity | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.6667 | 29964 |
| eval_prose_11 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 29899 |
| eval_prose_12 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 30551 |
| eval_prose_13 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 29043 |
| eval_prose_14 | prose | citation-integrity | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.6667 | 30298 |
| eval_prose_15 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 29117 |
| eval_prose_16 | prose | citation-integrity | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.6667 | 27843 |
| eval_prose_17 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 27337 |
| eval_prose_18 | prose | citation-integrity | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.6667 | 27358 |
| eval_prose_19 | prose | citation-integrity,rai-disclosure | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2,rai-disclosure:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.3333 | 27225 |
| eval_prose_20 | prose | citation-integrity | citation-integrity,rai-disclosure,report-structure | citation-integrity:v2 | citation-integrity:v2,rai-disclosure:v2,report-structure:v2 | 1.0000 | 1.0000 | 0.6667 | 27156 |

---

## TABLE 4 — Latency Distribution

| p50 | p90 | p95 | p99 | max | N |
|---|---|---|---|---|---|
| 24730.5 | 29905.5 | 30310.6 | 34397.9 | 38686.0 | 60 |

---

## Analysis of Milestone M3 Gate Criteria

1. **Capability Recall**:
   - Target: $\ge 0.90$.
   - Achieved: **0.9107** (102 / 112 gold capability instances correctly retrieved). **PASS**.
   - Breakdown: Perfect 1.0000 recall on `code-quality` and `rai-disclosure`. Recall on `citation-integrity` was 0.7500 (30 / 40) because in 10 mixed submissions (`eval_mixed_01, 03, 05, 07, 09, 11, 13, 15, 17, 19`), the ingestion parser evaluated `DISCLOSURE.md` instead of `paper.md`, suppressing the references detector.

2. **Version-Level Precision@1**:
   - Target: $\ge 0.90$.
   - Achieved: **0.9107** (102 / 112 matches to gold active version `v2`). **PASS**.

3. **Over-Retrieval Rate**:
   - Target: $< 0.20$.
   - - Achieved: **0.2154** (28 over-retrievals / 130 selected capabilities). **MISSED TARGET** ($0.2154 \ge 0.20$).
   - Mechanism: The deterministic capability gate in `capability_gate.py` unconditionally enabled `report-structure` on all 20 prose submissions regardless of word count, whereas ARCHITECTURE §6.2 specifies that structural conformance requires `word_count >= 500`. Since all 20 prose submissions in the evaluation corpus contain fewer than 500 words (50–187 words), `report-structure` was over-retrieved 20 times. Additionally, `rai-disclosure` was unconditionally enabled on 8 prose submissions that lacked an AI disclosure section.

4. **Same-Family Risk Exposure (HSR@K)**:
   - Measured: **0.6333** across all queries (38 of 60 queries surfaced at least one candidate with score $\ge 0.30$ and status `draft` or `deprecated`).
- Total risky candidates surfaced: **58** (primarily v1 draft skills appearing in FAISS candidate pools).

5. **Retrieval Latency**:
   - Target: $p50 \le 1500$ ms.
   - Observed $p50$: **24,730.5 ms** (max: 38,686.0 ms). **MISSED TARGET**.
   - Mechanism: During Phase P2 orchestrator runs, `retrieval_events.latency_ms` recorded elapsed wall-clock time from the submission review entrypoint (`time.perf_counter() - start_time`), capturing the cumulative duration of all $k=3$ LLM Ollama inference executions across gated capabilities, rather than isolating FAISS vector lookup and deterministic gate evaluation latency.
