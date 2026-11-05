"""Unit tests for k-run agreement computation (US-28)."""

from compliance_review.harness.k_run import compute_k_run_agreement


def test_empty_runs() -> None:
    assert compute_k_run_agreement([]) == {}


def test_perfect_verdict_and_evidence_agreement() -> None:
    run1 = [
        {"check_id": "c1", "verdict": "flag", "evidence_text": "sample text from paper"},
        {"check_id": "c2", "verdict": "pass", "evidence_text": ""},
    ]
    run2 = [
        {"check_id": "c1", "verdict": "flag", "evidence_text": "sample text from paper"},
        {"check_id": "c2", "verdict": "pass", "evidence_text": ""},
    ]
    run3 = [
        {"check_id": "c1", "verdict": "flag", "evidence_text": "sample text from paper"},
        {"check_id": "c2", "verdict": "pass", "evidence_text": ""},
    ]

    metrics = compute_k_run_agreement([run1, run2, run3])
    assert metrics["c1"]["agreement"] == 1.0
    assert metrics["c1"]["evidence_jaccard"] == 1.0
    assert metrics["c2"]["agreement"] == 1.0
    assert metrics["c2"]["evidence_jaccard"] == 1.0


def test_majority_verdict_agreement() -> None:
    # 2 flag, 1 pass -> max verdict freq is 2/3 = 0.6667
    run1 = [{"check_id": "c1", "verdict": "flag", "evidence_text": "word1 word2 word3"}]
    run2 = [{"check_id": "c1", "verdict": "flag", "evidence_text": "word1 word2 word4"}]
    run3 = [{"check_id": "c1", "verdict": "pass", "evidence_text": ""}]

    metrics = compute_k_run_agreement([run1, run2, run3])
    assert metrics["c1"]["agreement"] == round(2.0 / 3.0, 4)
    # Evidence Jaccard between run1 & run2:
    # words1: {word1, word2, word3}, words2: {word1, word2, word4}
    # intersection: 2, union: 4 -> 0.5
    assert metrics["c1"]["evidence_jaccard"] == 0.5


def test_split_evidence_jaccard() -> None:
    # 3 flags with different word overlaps
    run1 = [{"check_id": "c1", "verdict": "flag", "evidence_text": "apple banana"}]
    run2 = [{"check_id": "c1", "verdict": "flag", "evidence_text": "banana cherry"}]
    run3 = [{"check_id": "c1", "verdict": "flag", "evidence_text": "banana date"}]

    metrics = compute_k_run_agreement([run1, run2, run3])
    assert metrics["c1"]["agreement"] == 1.0
    # Pairwise:
    # (1, 2): {banana} / {apple, banana, cherry} = 1/3
    # (1, 3): {banana} / {apple, banana, date} = 1/3
    # (2, 3): {banana} / {banana, cherry, date} = 1/3
    # Average: 1/3 ~ 0.3333
    assert metrics["c1"]["evidence_jaccard"] == 0.3333
