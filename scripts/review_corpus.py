"""Batch review script for 60 evaluation corpus submissions (P2 Task 11).

Runs review with --skill-status evaluating and k=3 for all 60 corpus submissions.
Persists executions, verdicts, and maintains data/labels/CORPUS_STATE.json.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from compliance_review.db.engine import get_engine
from compliance_review.db.tables import skill_executions
from compliance_review.harness.orchestrator import run_review


def main() -> None:
    manifest_path = Path("data/corpus/CORPUS_MANIFEST.json")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    state_path = Path("data/labels/CORPUS_STATE.json")
    state_path.parent.mkdir(parents=True, exist_ok=True)

    state: dict[str, dict[str, object]] = {}
    if state_path.exists():
        try:
            loaded = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict) and "submissions" in loaded:
                state = loaded["submissions"]
        except Exception:
            state = {}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    subs = manifest.get("submissions", [])
    total = len(subs)

    engine = get_engine()
    # Check already reviewed submission IDs in DB
    with engine.connect() as conn:
        reviewed_db_ids = {
            int(r[0])
            for r in conn.execute(select(skill_executions.c.submission_id).distinct()).fetchall()
        }

    print(f"Starting batch review of {total} submissions...")
    for idx, item in enumerate(subs, 1):
        sub_id = int(item["submission_id"])
        ext_id = str(item["external_id"])

        if (
            sub_id in reviewed_db_ids
            and str(sub_id) in state
            and state[str(sub_id)].get("status") == "reviewed"
        ):
            print(f"[{idx}/{total}] Submission #{sub_id} ({ext_id}): already reviewed, skipping.")
            continue

        print(f"[{idx}/{total}] Reviewing submission #{sub_id} ({ext_id})...", flush=True)
        start = time.perf_counter()
        try:
            run_review(sub_id, k=3, deterministic_only=False, skill_status="evaluating")
            dur = time.perf_counter() - start
            state[str(sub_id)] = {
                "external_id": ext_id,
                "submission_type": item["submission_type"],
                "status": "reviewed",
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": round(dur, 2),
            }
            print(f"[{idx}/{total}] Submission #{sub_id} ({ext_id}) done in {dur:.1f}s", flush=True)
        except Exception as exc:
            dur = time.perf_counter() - start
            state[str(sub_id)] = {
                "external_id": ext_id,
                "status": "error",
                "error": str(exc),
                "duration_seconds": round(dur, 2),
            }
            print(
                f"[{idx}/{total}] Submission #{sub_id} ({ext_id}) FAILED in {dur:.1f}s: {exc}",
                flush=True,
            )

        # Save checkpoint
        state_path.write_text(
            json.dumps({"total": total, "completed": len(state), "submissions": state}, indent=2),
            encoding="utf-8",
        )

    print("Batch review complete.")


if __name__ == "__main__":
    main()
