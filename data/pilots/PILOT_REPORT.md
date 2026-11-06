# PILOT REPORT — P1 Milestone M1 End-to-End Pilot Execution

**Date:** 2026-11-06 11:26:06 UTC  
**Model:** `qwen3:4b`  
**Harness Configuration:** $k=3$ runs, sampling temp=0.0, top_p=1.0, seed=run_index, format=json, `think=False`  
**Retriever:** FAISS cosine index on `all-MiniLM-L6-v2` (`eval_status: evaluating` -> v2 skills)  
**Evidence Gate:** Frozen verifier (`prefix_len=40`, `fuzzy_threshold=0.92`, NFKC + whitespace collapse + casefold)  

---

## 1. Executive Summary Table

| Pilot Submission | Type | Capabilities Evaluated | Selected Versions | Verified Flags | Downgraded (Unsupported) | Latency (ms) |
|---|---|---|---|---|---|---|
| `pilot_clean_prose.md` | `prose` | citation-integrity, rai-disclosure, report-structure | citation-integrity v2, rai-disclosure v2, report-structure v2 | 0 | 0 | 37554 |
| `pilot_clean_code` | `code` | code-quality | code-quality v2 | 0 | 0 | 9021 |
| `pilot_clean_mixed` | `mixed` | citation-integrity, code-quality, rai-disclosure, report-structure | citation-integrity v2, code-quality v2, rai-disclosure v2, report-structure v2 | 0 | 0 | 36357 |
| `pilot_issue_doi.md` | `prose` | citation-integrity, rai-disclosure, report-structure | citation-integrity v2, rai-disclosure v2, report-structure v2 | 6 | 0 | 29144 |
| `pilot_issue_structure.md` | `prose` | citation-integrity, rai-disclosure, report-structure | citation-integrity v2, rai-disclosure v2, report-structure v2 | 12 | 3 | 29667 |
| `pilot_issue_code` | `code` | code-quality | code-quality v2 | 6 | 0 | 9969 |
| `pilot_rigged_biblio.md` | `prose` | citation-integrity, rai-disclosure, report-structure | citation-integrity v2, rai-disclosure v2, report-structure v2 | 9 | 3 | 34650 |
| `pilot_rigged_disclosure.md` | `prose` | citation-integrity, rai-disclosure, report-structure | citation-integrity v2, rai-disclosure v2, report-structure v2 | 9 | 0 | 27584 |
| `pilot_rigged_code` | `code` | code-quality | code-quality v2 | 0 | 3 | 10452 |
| `pilot_mixed_two_issues` | `mixed` | citation-integrity, code-quality | citation-integrity v2, code-quality v2 | 6 | 3 | 18761 |

**Totals:** 10 pilots | 72 capability executions | 48 verified flags | 12 downgraded flags

---

## 1.5 Before vs. After Evidence Acceptance Comparison by Capability (P1 vs P1.5)

| Capability | P1 Ver | P1 Down | P1 Acc | P1.5 Ver | P1.5 Down | P1.5 Acc | Delta |
|---|---|---|---|---|---|---|---|
| `citation-integrity` | 0 | 0 | N/A | 15 | 0 | 100.0% | +100.0% |
| `code-quality` | 0 | 12 | 0.0% | 9 | 6 | 60.0% | +60.0% |
| `rai-disclosure` | 6 | 21 | 22.2% | 9 | 3 | 75.0% | +52.8% |
| `report-structure` | 14 | 21 | 40.0% | 15 | 3 | 83.3% | +43.3% |
| **Overall Totals** | **20** | **54** | **27.0%** | **48** | **12** | **80.0%** | **+53.0%** |

---

## 2. Gate Conditions Verification

- [x] **Gate Condition (a) — Evidence Grounding:** Every verdict with `verdict='flag'` (48 flags) has a matching row in `evidence_verifications` with `verified=True`.
- [x] **Gate Condition (b) — Evidence Downgrade:** At least one pilot produced `unsupported_evidence` rows (12 occurrences total). Fabricated/unlocated quotes were successfully intercepted and downgraded.
- [x] **Gate Condition (c) — $k=3$ Executions:** Every gated capability for every pilot ran exactly $k=3$ times (72 total execution rows).
- [x] **Gate Condition (d) — Model Digest Recording:** All execution rows record the exact sha256 model digest (`359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7`).

---

## 3. Detailed Pilot Findings and Disagreement Traces

### Pilot: `pilot_clean_prose.md`

- **Submission ID:** 75
- **Submission Type:** `prose`
- **SHA-256:** `79217b8f356b6e442d375e175dfeafac0ec790c1d941fec34eba3e3a51a21eac`
- **Execution Latency:** 37554 ms

```text
--- Review Trace for Submission #75 (pilot-run-pilot_clean_prose.md-1e5502) [k=3 Full Review] ---
Submission Type: prose | Latency: 37494 ms

Capabilities Gated:
  [ENABLED]  citation-integrity   : prose submission requires citation integrity check
  [ENABLED]  report-structure     : prose submission requires structural compliance check
  [DISABLED] code-quality         : code-quality disabled for pure prose submissions
  [ENABLED]  rai-disclosure       : prose submission requires AI disclosure check

Selected Skills:
  - citation-integrity v2 (score=0.2915, reason=only_evaluating)
  - report-structure v2 (score=0.1578, reason=only_evaluating)
  - rai-disclosure v2 (score=0.3919, reason=only_evaluating)

Checklist Verdicts (Run 1 / Consistency):
  Capability: citation-integrity
    - cite-doi-resolvable          -> pass                 (medium  ) [agr=1.00] : Found 2 valid DOIs
    - cite-not-retracted           -> pass                 (medium  ) [agr=1.00] : No retracted DOIs located
    - cite-no-duplicates           -> pass                 (low     ) [agr=1.00] : No duplicate references in bibliography
    - cite-claim-supported         -> pass                 (medium  ) [agr=1.00] : None
    - cite-context-accurate        -> pass                 (medium  ) [agr=1.00] : None
  Capability: report-structure
    - struct-required-sections     -> pass                 (medium  ) [agr=1.00] : All required sections present
    - struct-heading-order         -> pass                 (medium  ) [agr=1.00] : Headings follow standard sequence
    - struct-minimum-length        -> pass                 (medium  ) [agr=1.00] : Submission contains 580 words
    - struct-semantic-coherence    -> pass                 (medium  ) [agr=1.00] : None
    - struct-claim-evidence-alignment -> pass                 (medium  ) [agr=1.00] : None
  Capability: rai-disclosure
    - rai-section-present          -> pass                 (medium  ) [agr=1.00] : AI disclosure section present
    - rai-tool-named               -> pass                 (medium  ) [agr=1.00] : Disclosed AI tools: claude
    - rai-task-named               -> pass                 (medium  ) [agr=1.00] : Tasks specified: editing
    - rai-sufficiency-judgment     -> pass                 (medium  ) [agr=1.00] : None
    - rai-human-oversight-described -> pass                 (medium  ) [agr=1.00] : None
```

### Pilot: `pilot_clean_code`

- **Submission ID:** 76
- **Submission Type:** `code`
- **SHA-256:** `c5843f4091df838c935f49d088d2e64e858eb56cd2f9a24a3e08e1c46cf94445`
- **Execution Latency:** 9021 ms

```text
--- Review Trace for Submission #76 (pilot-run-pilot_clean_code-2907a1) [k=3 Full Review] ---
Submission Type: code | Latency: 8967 ms

Capabilities Gated:
  [DISABLED] citation-integrity   : citation-integrity disabled for code submissions per US-13
  [DISABLED] report-structure     : report-structure disabled for code submissions
  [ENABLED]  code-quality         : code submission requires Python code quality static check
  [DISABLED] rai-disclosure       : rai-disclosure disabled for code submissions per US-13

Selected Skills:
  - code-quality v2 (score=0.1726, reason=only_evaluating)

Checklist Verdicts (Run 1 / Consistency):
  Capability: code-quality
    - code-file-loc-limit          -> pass                 (medium  ) [agr=1.00] : All files within 300 LOC limit
    - code-ruff-clean              -> pass                 (medium  ) [agr=1.00] : Ruff E9 and F checks passed
    - code-pylint-clean            -> pass                 (low     ) [agr=1.00] : Basic static structure clean
    - code-error-handling          -> pass                 (medium  ) [agr=1.00] : None
    - code-modularity              -> pass                 (medium  ) [agr=1.00] : None
```

### Pilot: `pilot_clean_mixed`

- **Submission ID:** 77
- **Submission Type:** `mixed`
- **SHA-256:** `84432ff01775af2fd4286ae088f86bc1cde46716713a8d16163b23b1e619fdb7`
- **Execution Latency:** 36357 ms

```text
--- Review Trace for Submission #77 (pilot-run-pilot_clean_mixed-2e130c) [k=3 Full Review] ---
Submission Type: mixed | Latency: 36314 ms

Capabilities Gated:
  [ENABLED]  citation-integrity   : bibliography detected in mixed submission
  [ENABLED]  report-structure     : prose length 504 >= 500 words
  [ENABLED]  code-quality         : code present in mixed submission
  [ENABLED]  rai-disclosure       : AI disclosure section or DISCLOSURE.md detected

Selected Skills:
  - citation-integrity v2 (score=0.0396, reason=only_evaluating)
  - report-structure v2 (score=0.0276, reason=only_evaluating)
  - code-quality v2 (score=-0.0171, reason=only_evaluating)
  - rai-disclosure v2 (score=0.0146, reason=only_evaluating)

Checklist Verdicts (Run 1 / Consistency):
  Capability: citation-integrity
    - cite-doi-resolvable          -> pass                 (medium  ) [agr=1.00] : Found 2 valid DOIs
    - cite-not-retracted           -> pass                 (medium  ) [agr=1.00] : No retracted DOIs located
    - cite-no-duplicates           -> pass                 (low     ) [agr=1.00] : No duplicate references in bibliography
    - cite-claim-supported         -> pass                 (medium  ) [agr=1.00] : None
    - cite-context-accurate        -> pass                 (medium  ) [agr=1.00] : None
  Capability: report-structure
    - struct-required-sections     -> pass                 (medium  ) [agr=1.00] : All required sections present
    - struct-heading-order         -> pass                 (medium  ) [agr=1.00] : Headings follow standard sequence
    - struct-minimum-length        -> pass                 (medium  ) [agr=1.00] : Submission contains 504 words
    - struct-semantic-coherence    -> pass                 (medium  ) [agr=1.00] : None
    - struct-claim-evidence-alignment -> pass                 (medium  ) [agr=1.00] : None
  Capability: code-quality
    - code-file-loc-limit          -> pass                 (medium  ) [agr=1.00] : All files within 300 LOC limit
    - code-ruff-clean              -> pass                 (medium  ) [agr=1.00] : Ruff E9 and F checks passed
    - code-pylint-clean            -> pass                 (low     ) [agr=1.00] : Basic static structure clean
    - code-error-handling          -> pass                 (medium  ) [agr=1.00] : None
    - code-modularity              -> pass                 (medium  ) [agr=1.00] : None
  Capability: rai-disclosure
    - rai-section-present          -> pass                 (medium  ) [agr=1.00] : AI disclosure section present
    - rai-tool-named               -> pass                 (medium  ) [agr=1.00] : Negative disclosure stating no AI tools utilized
    - rai-task-named               -> pass                 (medium  ) [agr=1.00] : Tasks specified: None
    - rai-sufficiency-judgment     -> pass                 (medium  ) [agr=1.00] : None
    - rai-human-oversight-described -> pass                 (medium  ) [agr=1.00] : None
```

### Pilot: `pilot_issue_doi.md`

- **Submission ID:** 78
- **Submission Type:** `prose`
- **SHA-256:** `3174d218538199ffa5d977ae7885589d135a7ee49c7d3588ed46377947960bba`
- **Execution Latency:** 29144 ms

```text
--- Review Trace for Submission #78 (pilot-run-pilot_issue_doi.md-0c6ea0) [k=3 Full Review] ---
Submission Type: prose | Latency: 29107 ms

Capabilities Gated:
  [ENABLED]  citation-integrity   : prose submission requires citation integrity check
  [ENABLED]  report-structure     : prose submission requires structural compliance check
  [DISABLED] code-quality         : code-quality disabled for pure prose submissions
  [ENABLED]  rai-disclosure       : prose submission requires AI disclosure check

Selected Skills:
  - citation-integrity v2 (score=0.6, reason=only_evaluating)
  - report-structure v2 (score=0.2945, reason=only_evaluating)
  - rai-disclosure v2 (score=0.3266, reason=only_evaluating)

Checklist Verdicts (Run 1 / Consistency):
  Capability: citation-integrity
    - cite-doi-resolvable          -> pass                 (medium  ) [agr=1.00] : Found 2 valid DOIs
    - cite-not-retracted           -> pass                 (medium  ) [agr=1.00] : No retracted DOIs located
    - cite-no-duplicates           -> flag                 (low     ) [agr=1.00] : 3. Anderson, R. (2021). Foundations of Citation Networks. Journal of Bibliometrics, 10.1234/56789.
    - cite-claim-supported         -> flag                 (high    ) [agr=1.00] : Duplicate citations appeared in 4% of analyzed drafts, while malformed identifiers represented 2% of total references.
    - cite-context-accurate        -> pass                 (medium  ) [agr=1.00] : None
  Capability: report-structure
    - struct-required-sections     -> pass                 (medium  ) [agr=1.00] : All required sections present
    - struct-heading-order         -> pass                 (medium  ) [agr=1.00] : Headings follow standard sequence
    - struct-minimum-length        -> pass                 (medium  ) [agr=1.00] : Submission contains 527 words
    - struct-semantic-coherence    -> pass                 (medium  ) [agr=1.00] : None
    - struct-claim-evidence-alignment -> pass                 (medium  ) [agr=1.00] : None
  Capability: rai-disclosure
    - rai-section-present          -> pass                 (medium  ) [agr=1.00] : AI disclosure section present
    - rai-tool-named               -> pass                 (medium  ) [agr=1.00] : Negative disclosure stating no AI tools utilized
    - rai-task-named               -> pass                 (medium  ) [agr=1.00] : Tasks specified: writing
    - rai-sufficiency-judgment     -> pass                 (medium  ) [agr=1.00] : None
    - rai-human-oversight-described -> pass                 (medium  ) [agr=1.00] : None
```

### Pilot: `pilot_issue_structure.md`

- **Submission ID:** 79
- **Submission Type:** `prose`
- **SHA-256:** `b40716a2190d56ac4fc0a5eba040f0d6defafd7c18ea4226c7bbaf90966a2a4f`
- **Execution Latency:** 29667 ms

```text
--- Review Trace for Submission #79 (pilot-run-pilot_issue_structure.md-0efcce) [k=3 Full Review] ---
Submission Type: prose | Latency: 29624 ms

Capabilities Gated:
  [ENABLED]  citation-integrity   : prose submission requires citation integrity check
  [ENABLED]  report-structure     : prose submission requires structural compliance check
  [DISABLED] code-quality         : code-quality disabled for pure prose submissions
  [ENABLED]  rai-disclosure       : prose submission requires AI disclosure check

Selected Skills:
  - citation-integrity v2 (score=0.1557, reason=only_evaluating)
  - report-structure v2 (score=0.1106, reason=only_evaluating)
  - rai-disclosure v2 (score=0.1393, reason=only_evaluating)

Checklist Verdicts (Run 1 / Consistency):
  Capability: citation-integrity
    - cite-doi-resolvable          -> pass                 (medium  ) [agr=1.00] : Found 1 valid DOIs
    - cite-not-retracted           -> pass                 (medium  ) [agr=1.00] : No retracted DOIs located
    - cite-no-duplicates           -> pass                 (low     ) [agr=1.00] : No duplicate references in bibliography
    - cite-claim-supported         -> pass                 (medium  ) [agr=1.00] : None
    - cite-context-accurate        -> pass                 (medium  ) [agr=1.00] : None
  Capability: report-structure
    - struct-required-sections     -> flag                 (high    ) [agr=1.00] : # Incomplete Report on Distributed Computing Systems
    - struct-heading-order         -> pass                 (medium  ) [agr=1.00] : Headings follow standard sequence
    - struct-minimum-length        -> flag                 (medium  ) [agr=1.00] : # Incomplete Report on Distributed Computing Systems
    - struct-semantic-coherence    -> pass                 (medium  ) [agr=1.00] : None
    - struct-claim-evidence-alignment -> flag                 (high    ) [agr=1.00] : Raft achieved 1200 operations per second under low network latency. When packet loss rose above 10%, throughput dropped to 450 operations per second.
  Capability: rai-disclosure
    - rai-section-present          -> flag                 (high    ) [agr=1.00] : No AI disclosure section or DISCLOSURE.md located
    - rai-tool-named               -> not_applicable       (medium  ) [agr=1.00] : None
    - rai-task-named               -> not_applicable       (medium  ) [agr=1.00] : None
    - rai-sufficiency-judgment     -> flag                 (high    ) [agr=1.00] : This report summarizes distributed consensus protocols and their throughput under network partitions.
    - rai-human-oversight-described -> not_applicable       (medium  ) [agr=1.00] : None
```

### Pilot: `pilot_issue_code`

- **Submission ID:** 80
- **Submission Type:** `code`
- **SHA-256:** `f16d3a368f9018539944bb15d7c8d0e0794d7dc4158c0af3a89959995e5fe0fb`
- **Execution Latency:** 9969 ms

```text
--- Review Trace for Submission #80 (pilot-run-pilot_issue_code-5325f3) [k=3 Full Review] ---
Submission Type: code | Latency: 9929 ms

Capabilities Gated:
  [DISABLED] citation-integrity   : citation-integrity disabled for code submissions per US-13
  [DISABLED] report-structure     : report-structure disabled for code submissions
  [ENABLED]  code-quality         : code submission requires Python code quality static check
  [DISABLED] rai-disclosure       : rai-disclosure disabled for code submissions per US-13

Selected Skills:
  - code-quality v2 (score=0.1726, reason=only_evaluating)

Checklist Verdicts (Run 1 / Consistency):
  Capability: code-quality
    - code-file-loc-limit          -> pass                 (medium  ) [agr=1.00] : All files within 300 LOC limit
    - code-ruff-clean              -> flag                 (critical) [agr=1.00] : x = [1, 2, 3, 4
    - code-pylint-clean            -> pass                 (low     ) [agr=1.00] : Basic static structure clean
    - code-error-handling          -> flag                 (medium  ) [agr=1.00] : x = [1, 2, 3, 4
    - code-modularity              -> not_applicable       (medium  ) [agr=1.00] : None
```

### Pilot: `pilot_rigged_biblio.md`

- **Submission ID:** 81
- **Submission Type:** `prose`
- **SHA-256:** `92acad5e842cd3c41f54411a41928c3e20a6d3fc04c7e56916287ed3b03af5a4`
- **Execution Latency:** 34650 ms

```text
--- Review Trace for Submission #81 (pilot-run-pilot_rigged_biblio.md-6c87d7) [k=3 Full Review] ---
Submission Type: prose | Latency: 34562 ms

Capabilities Gated:
  [ENABLED]  citation-integrity   : prose submission requires citation integrity check
  [ENABLED]  report-structure     : prose submission requires structural compliance check
  [DISABLED] code-quality         : code-quality disabled for pure prose submissions
  [ENABLED]  rai-disclosure       : prose submission requires AI disclosure check

Selected Skills:
  - citation-integrity v2 (score=-0.0491, reason=only_evaluating)
  - report-structure v2 (score=-0.0154, reason=only_evaluating)
  - rai-disclosure v2 (score=-0.0235, reason=only_evaluating)

Checklist Verdicts (Run 1 / Consistency):
  Capability: citation-integrity
    - cite-doi-resolvable          -> pass                 (medium  ) [agr=1.00] : Found 2 valid DOIs
    - cite-not-retracted           -> pass                 (medium  ) [agr=1.00] : No retracted DOIs located
    - cite-no-duplicates           -> pass                 (low     ) [agr=1.00] : No duplicate references in bibliography
    - cite-claim-supported         -> flag                 (high    ) [agr=1.00] : Hawking (1988) proved that DNA replication is directly mediated by microscopic black hole evaporation within the cell nucleus (Hawking, 1988)
    - cite-context-accurate        -> flag                 (medium  ) [agr=1.00] : Hawking (1988) proved that DNA replication is directly mediated by microscopic black hole evaporation within the cell nucleus (Hawking, 1988)
  Capability: report-structure
    - struct-required-sections     -> pass                 (medium  ) [agr=1.00] : All required sections present
    - struct-heading-order         -> pass                 (medium  ) [agr=1.00] : Headings follow standard sequence
    - struct-minimum-length        -> flag                 (medium  ) [agr=1.00] : # Critical Analysis of Quantum Gravity in Cellular Biology
    - struct-semantic-coherence    -> pass                 (medium  ) [agr=1.00] : None
    - struct-claim-evidence-alignment -> flag                 (high    ) [agr=1.00] : Hawking (1988) proved that DNA replication is directly mediated by microscopic black hole evaporation within the cell nucleus (Hawking, 1988).
  Capability: rai-disclosure
    - rai-section-present          -> pass                 (medium  ) [agr=1.00] : AI disclosure section present
    - rai-tool-named               -> pass                 (medium  ) [agr=1.00] : Negative disclosure stating no AI tools utilized
    - rai-task-named               -> pass                 (medium  ) [agr=1.00] : Tasks specified: None
    - rai-sufficiency-judgment     -> pass                 (medium  ) [agr=1.00] : None
    - rai-human-oversight-described -> pass                 (medium  ) [agr=1.00] : None
```

### Pilot: `pilot_rigged_disclosure.md`

- **Submission ID:** 82
- **Submission Type:** `prose`
- **SHA-256:** `ca821ba5679ab1410de5dd7b183b31193dd5cc54c402eef279a39528d5e8a090`
- **Execution Latency:** 27584 ms

```text
--- Review Trace for Submission #82 (pilot-run-pilot_rigged_disclosure.md-2274d4) [k=3 Full Review] ---
Submission Type: prose | Latency: 27515 ms

Capabilities Gated:
  [ENABLED]  citation-integrity   : prose submission requires citation integrity check
  [ENABLED]  report-structure     : prose submission requires structural compliance check
  [DISABLED] code-quality         : code-quality disabled for pure prose submissions
  [ENABLED]  rai-disclosure       : prose submission requires AI disclosure check

Selected Skills:
  - citation-integrity v2 (score=0.1083, reason=only_evaluating)
  - report-structure v2 (score=0.1169, reason=only_evaluating)
  - rai-disclosure v2 (score=0.123, reason=only_evaluating)

Checklist Verdicts (Run 1 / Consistency):
  Capability: citation-integrity
    - cite-doi-resolvable          -> pass                 (medium  ) [agr=1.00] : Found 2 valid DOIs
    - cite-not-retracted           -> pass                 (medium  ) [agr=1.00] : No retracted DOIs located
    - cite-no-duplicates           -> pass                 (low     ) [agr=1.00] : No duplicate references in bibliography
    - cite-claim-supported         -> pass                 (medium  ) [agr=1.00] : None
    - cite-context-accurate        -> pass                 (medium  ) [agr=1.00] : None
  Capability: report-structure
    - struct-required-sections     -> pass                 (medium  ) [agr=1.00] : All required sections present
    - struct-heading-order         -> pass                 (medium  ) [agr=1.00] : Headings follow standard sequence
    - struct-minimum-length        -> flag                 (medium  ) [agr=1.00] : # Advanced Neural Architectures for Multimodal Understanding
    - struct-semantic-coherence    -> pass                 (medium  ) [agr=1.00] : None
    - struct-claim-evidence-alignment -> pass                 (medium  ) [agr=1.00] : None
  Capability: rai-disclosure
    - rai-section-present          -> pass                 (medium  ) [agr=1.00] : AI disclosure section present
    - rai-tool-named               -> flag                 (medium  ) [agr=1.00] : Disclosure
We acknowledge using AI tools to assist in drafting this paper.

## References
1. Radford, A., et al. (2021).
    - rai-task-named               -> pass                 (medium  ) [agr=1.00] : Tasks specified: drafting
    - rai-sufficiency-judgment     -> pass                 (medium  ) [agr=1.00] : None
    - rai-human-oversight-described -> flag                 (medium  ) [agr=1.00] : We acknowledge using AI tools to assist in drafting this paper.
```

### Pilot: `pilot_rigged_code`

- **Submission ID:** 83
- **Submission Type:** `code`
- **SHA-256:** `47e114373d83262f04db5f14d580a372e39205127d078d9e79b32ca5b11b144d`
- **Execution Latency:** 10452 ms

```text
--- Review Trace for Submission #83 (pilot-run-pilot_rigged_code-697496) [k=3 Full Review] ---
Submission Type: code | Latency: 10393 ms

Capabilities Gated:
  [DISABLED] citation-integrity   : citation-integrity disabled for code submissions per US-13
  [DISABLED] report-structure     : report-structure disabled for code submissions
  [ENABLED]  code-quality         : code submission requires Python code quality static check
  [DISABLED] rai-disclosure       : rai-disclosure disabled for code submissions per US-13

Selected Skills:
  - code-quality v2 (score=0.1726, reason=only_evaluating)

Checklist Verdicts (Run 1 / Consistency):
  Capability: code-quality
    - code-file-loc-limit          -> pass                 (medium  ) [agr=1.00] : All files within 300 LOC limit
    - code-ruff-clean              -> pass                 (medium  ) [agr=1.00] : Ruff E9 and F checks passed
    - code-pylint-clean            -> pass                 (low     ) [agr=1.00] : Basic static structure clean
    - code-error-handling          -> flag                 (medium  ) [agr=1.00] : query = f"SELECT * FROM users WHERE id = '{user_id}'"
    - code-modularity              -> not_applicable       (medium  ) [agr=1.00] : None
```

### Pilot: `pilot_mixed_two_issues`

- **Submission ID:** 84
- **Submission Type:** `mixed`
- **SHA-256:** `1ac0878d4c6e41900f1b42031315bd991e417ab662d07a39a20827d38dca33b1`
- **Execution Latency:** 18761 ms

```text
--- Review Trace for Submission #84 (pilot-run-pilot_mixed_two_issues-b6727d) [k=3 Full Review] ---
Submission Type: mixed | Latency: 18700 ms

Capabilities Gated:
  [ENABLED]  citation-integrity   : bibliography detected in mixed submission
  [DISABLED] report-structure     : prose length 64 < 500 words
  [ENABLED]  code-quality         : code present in mixed submission
  [DISABLED] rai-disclosure       : no disclosure section or DISCLOSURE.md present

Selected Skills:
  - citation-integrity v2 (score=0.1566, reason=only_evaluating)
  - code-quality v2 (score=0.1208, reason=only_evaluating)

Checklist Verdicts (Run 1 / Consistency):
  Capability: citation-integrity
    - cite-doi-resolvable          -> pass                 (medium  ) [agr=1.00] : Found 2 valid DOIs
    - cite-not-retracted           -> pass                 (medium  ) [agr=1.00] : No retracted DOIs located
    - cite-no-duplicates           -> flag                 (low     ) [agr=1.00] : 2. Lamport, L. (1998). The Part-Time Parliament. ACM TOCS, 10.1145/279227.279229.
    - cite-claim-supported         -> pass                 (medium  ) [agr=1.00] : None
    - cite-context-accurate        -> pass                 (medium  ) [agr=1.00] : None
  Capability: code-quality
    - code-file-loc-limit          -> pass                 (medium  ) [agr=1.00] : All files within 300 LOC limit
    - code-ruff-clean              -> flag                 (critical) [agr=1.00] : values = [10, 20, 30
    - code-pylint-clean            -> pass                 (low     ) [agr=1.00] : Basic static structure clean
    - code-error-handling          -> flag                 (medium  ) [agr=1.00] : values = [10, 20, 30
    - code-modularity              -> not_applicable       (medium  ) [agr=1.00] : None
```
