"""Enforcement of severity cap per US-22 and PRD.md §4.4."""

from typing import Any


def apply_severity_cap_to_runs(
    runs_verdicts: list[list[dict[str, Any]]],
    checklist_items: dict[str, dict[str, Any]],
) -> list[list[dict[str, Any]]]:
    """Enforce severity cap per US-22.

    Severity in {high, critical} is allowed only if:
      verdict == 'flag' AND
      (deterministic_only == True OR >= 2 of k runs agree on the check with same severity)

    Otherwise, severity is capped to 'medium'.
    """
    if not runs_verdicts:
        return []

    # Count agreement across runs: (check_id, severity) -> count where verdict == 'flag'
    agreement_counts: dict[tuple[str, str], int] = {}
    for run in runs_verdicts:
        for v in run:
            c_id = v.get("check_id", "")
            verd = v.get("verdict", "")
            sev = v.get("severity", "")
            if verd == "flag":
                key = (c_id, sev)
                agreement_counts[key] = agreement_counts.get(key, 0) + 1

    capped_runs: list[list[dict[str, Any]]] = []
    for run in runs_verdicts:
        capped_run: list[dict[str, Any]] = []
        for v in run:
            v_copy = dict(v)
            c_id = v_copy.get("check_id", "")
            verd = v_copy.get("verdict", "")
            sev = v_copy.get("severity", "")
            item_def = checklist_items.get(c_id, {})
            is_deterministic = item_def.get("deterministic_only", False)

            if sev in {"high", "critical"}:
                # Allowed only if flag AND (deterministic OR agreement >= 2)
                allowed = False
                if verd == "flag":
                    if is_deterministic:
                        allowed = True
                    else:
                        agreed_count = agreement_counts.get((c_id, sev), 0)
                        if agreed_count >= 2:
                            allowed = True

                if not allowed:
                    v_copy["severity"] = "medium"

            capped_run.append(v_copy)
        capped_runs.append(capped_run)

    return capped_runs

