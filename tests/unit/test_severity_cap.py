"""Unit tests for severity cap on model-only flags (US-22)."""

from compliance_review.harness.severity_cap import apply_severity_cap_to_runs


def test_deterministic_severity_never_capped() -> None:
    """Verify deterministic checks retain critical/high severity regardless of run agreement."""
    runs = [
        [
            {
                "check_id": "cite-not-retracted",
                "verdict": "flag",
                "severity": "critical",
                "evidence_text": "Retracted DOI",
            }
        ]
    ]
    checklist_defs = {"cite-not-retracted": {"deterministic_only": True}}
    capped = apply_severity_cap_to_runs(runs, checklist_defs)
    assert capped[0][0]["severity"] == "critical"


def test_model_check_single_run_flag_is_capped() -> None:
    """Verify model-based critical flag is capped to medium if only 1 run flags it (US-22)."""
    runs = [
        [{"check_id": "cite-claim-supported", "verdict": "flag", "severity": "critical"}],
        [{"check_id": "cite-claim-supported", "verdict": "pass", "severity": "low"}],
        [{"check_id": "cite-claim-supported", "verdict": "pass", "severity": "low"}],
    ]
    checklist_defs = {"cite-claim-supported": {"deterministic_only": False}}
    capped = apply_severity_cap_to_runs(runs, checklist_defs)
    # Run 1 flagged as critical, but only 1 run agreed -> capped to medium
    assert capped[0][0]["severity"] == "medium"
    assert capped[1][0]["severity"] == "low"
    assert capped[2][0]["severity"] == "low"


def test_model_check_two_runs_agree_retains_severity() -> None:
    """Verify model-based critical flag retains severity if >= 2 of 3 runs agree."""
    runs = [
        [{"check_id": "cite-claim-supported", "verdict": "flag", "severity": "critical"}],
        [{"check_id": "cite-claim-supported", "verdict": "flag", "severity": "critical"}],
        [{"check_id": "cite-claim-supported", "verdict": "pass", "severity": "low"}],
    ]
    checklist_defs = {"cite-claim-supported": {"deterministic_only": False}}
    capped = apply_severity_cap_to_runs(runs, checklist_defs)
    # Runs 0 and 1 agree with critical flag -> retained
    assert capped[0][0]["severity"] == "critical"
    assert capped[1][0]["severity"] == "critical"
    assert capped[2][0]["severity"] == "low"


def test_model_check_pass_with_high_severity_is_capped() -> None:
    """Verify severity in {high, critical} is capped if verdict is not 'flag'."""
    runs = [
        [{"check_id": "cite-claim-supported", "verdict": "pass", "severity": "high"}],
        [{"check_id": "cite-claim-supported", "verdict": "pass", "severity": "high"}],
    ]
    checklist_defs = {"cite-claim-supported": {"deterministic_only": False}}
    capped = apply_severity_cap_to_runs(runs, checklist_defs)
    # verdict is pass, so high is not allowed -> capped to medium
    assert capped[0][0]["severity"] == "medium"
    assert capped[1][0]["severity"] == "medium"
