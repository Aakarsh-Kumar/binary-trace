"""CLI entrypoint for compliance-review conforming to ARCHITECTURE.md §9."""

import sys
from pathlib import Path
from typing import Any

import click.core
import typer
import typer.core

from compliance_review.errors import DuplicateSubmissionError, IngestError, SkillValidationError
from compliance_review.skills.loader import load_all_skills, set_skill_status

# Compatibility shim: Click 8.5+ breaking changes with Typer 0.12:
# 1. Parameter.make_metavar() requires ctx argument.
# 2. Click 8.5 uses UNSET sentinel for flag_value; Typer 0.12 passes flag_value=None causing
#    all options to be inferred as boolean flags.
_orig_make_metavar = click.core.Parameter.make_metavar


def _compat_make_metavar(self: Any, ctx: Any = None) -> str:
    if ctx is None:
        ctx = click.get_current_context(silent=True)
    return (
        str(_orig_make_metavar(self, ctx))
        if ctx is not None
        else (self.type.get_metavar(self) or "")
    )


click.core.Parameter.make_metavar = _compat_make_metavar  # type: ignore[method-assign]

_orig_typer_opt_init = typer.core.TyperOption.__init__


def _compat_typer_opt_init(self: Any, *args: Any, **kwargs: Any) -> None:
    unset_val = getattr(click.core, "UNSET", None)
    if kwargs.get("is_flag") is True:
        if kwargs.get("flag_value") is None or kwargs.get("flag_value") is unset_val:
            kwargs["flag_value"] = True
    elif kwargs.get("is_flag") is False or kwargs.get("is_flag") is None:
        if kwargs.get("flag_value") is None:
            kwargs["flag_value"] = unset_val
            kwargs["is_flag"] = False
    _orig_typer_opt_init(self, *args, **kwargs)


typer.core.TyperOption.__init__ = _compat_typer_opt_init  # type: ignore[method-assign]

app = typer.Typer(help="Grounded, local-first skill-retrieved compliance review.")
skills_app = typer.Typer(help="Manage and validate skills library.")
audit_app = typer.Typer(help="Audit log commands.")
index_app = typer.Typer(help="Vector index operations.")
reviewer_app = typer.Typer(help="Reviewer feedback operations.")
labels_app = typer.Typer(help="Label dataset and bootstrapping operations.")

app.add_typer(skills_app, name="skills")
app.add_typer(audit_app, name="audit")
app.add_typer(index_app, name="index")
app.add_typer(reviewer_app, name="reviewer")
app.add_typer(labels_app, name="labels")


@skills_app.command("validate")
def validate_skills(
    root: Path = typer.Option(Path("skills"), "--root", help="Root skills directory."),
) -> None:
    """Validate all SKILL.md files under root directory (US-07)."""
    try:
        loaded = load_all_skills(root)
        typer.echo(f"Validating {len(loaded)} skills under {root}...")
        for (capability, version), skill in loaded.items():
            typer.echo(
                f"  [PASS] {capability}/{version} ({skill.eval_status}) - "
                f"{len(skill.checklist)} checks"
            )
        typer.echo(f"All {len(loaded)} skills validated successfully.")
    except SkillValidationError as exc:
        typer.echo(f"Validation failed: {exc}", err=True)
        sys.exit(1)


@skills_app.command("set-status")
def set_status_cmd(
    capability: str = typer.Option(..., "--capability", help="Capability name"),
    version: str = typer.Option(..., "--version", help="Version identifier, e.g. v1, v2"),
    status: str = typer.Option(..., "--status", help="draft | evaluating | active | deprecated"),
    root: Path = typer.Option(Path("skills"), "--root", help="Root skills directory."),
) -> None:
    """Set eval_status for a capability version (US-08, D-014)."""
    try:
        updated_path = set_skill_status(root, capability, version, status)
        typer.echo(f"Updated {capability}/{version} status to '{status}' at {updated_path}")
    except SkillValidationError as exc:
        typer.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@skills_app.command("promote")
def promote_skill(
    capability: str = typer.Option(..., help="Capability name"),
    version: str = typer.Option(..., help="Version to promote"),
) -> None:
    """Promote a skill to active after regression suite passes (US-09)."""
    typer.echo("skills promote is not implemented until P5", err=True)
    sys.exit(3)


@skills_app.command("demote")
def demote_skill(
    capability: str = typer.Option(..., help="Capability name"),
    version: str = typer.Option(..., help="Version to demote"),
) -> None:
    """Demote a skill version to deprecated (US-10)."""
    typer.echo("skills demote is not implemented until P5", err=True)
    sys.exit(3)


@app.command("ingest")
def ingest_submission(
    source: Path = typer.Option(..., help="Source file or directory path"),
    type: str = typer.Option(..., "--type", help="prose | code | mixed"),
    external_id: str | None = typer.Option(None, help="External submission identifier"),
) -> None:
    """Ingest a student submission (US-01..US-05)."""
    from compliance_review.ingestion.orchestrator import ingest_source

    try:
        sub_id, sha256 = ingest_source(source, type, external_id)
        typer.echo(f"Ingested submission id={sub_id} sha256={sha256} source={source}")
    except DuplicateSubmissionError as exc:
        typer.echo(f"Duplicate submission error: {exc}", err=True)
        sys.exit(1)
    except IngestError as exc:
        typer.echo(f"Ingestion error: {exc}", err=True)
        sys.exit(1)
    except Exception as exc:
        typer.echo(f"Runtime error: {exc}", err=True)
        sys.exit(2)


@app.command("review")
def review_submission(
    submission_id: int = typer.Option(..., help="Submission ID to review"),
    k: int = typer.Option(3, help="Number of evaluation runs"),
    deterministic_only: bool = typer.Option(
        False, "--deterministic-only", help="Run gate + deterministic checks only (D-009)"
    ),
    skill_status: str = typer.Option(
        "active",
        "--skill-status",
        help="Filter skills by status: active (default) | evaluating | draft | all (D-012)",
    ),
) -> None:
    """Review an ingested submission."""
    valid_statuses = {"active", "evaluating", "draft", "all"}
    if skill_status not in valid_statuses:
        typer.echo(
            f"Invalid --skill-status '{skill_status}'. Must be one of {valid_statuses}",
            err=True,
        )
        sys.exit(1)

    from compliance_review.harness.orchestrator import run_review

    try:
        trace = run_review(
            submission_id=submission_id,
            k=k,
            deterministic_only=deterministic_only,
            skill_status=skill_status,
        )
        typer.echo(trace)
    except Exception as exc:
        typer.echo(f"Review error: {exc}", err=True)
        sys.exit(2)


@app.command("metrics")
def compute_metrics_cmd(
    labels: Path = typer.Option(..., help="Path to gold labels CSV"),
    out: Path = typer.Option(..., help="Path to write metrics output (JSON and CSV)"),
) -> None:
    """Compute benchmark metrics against gold labels (US-35)."""
    import csv
    import json

    from compliance_review.metrics.compute import compute_metrics

    if not labels.exists():
        typer.echo(f"Error: Labels file not found: {labels}", err=True)
        sys.exit(1)

    try:
        results = compute_metrics(labels)

        # Output JSON path and CSV path
        if out.suffix.lower() == ".csv":
            csv_path = out
            json_path = out.with_suffix(".json")
        else:
            json_path = out
            csv_path = out.with_suffix(".csv")

        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

        # Write per-check CSV report
        csv_rows: list[dict[str, Any]] = []
        for cap, c_data in results.get("capabilities", {}).items():
            for c_id, m in c_data.get("checks", {}).items():
                post_cm = m.get("post_confusion_matrix_2x2", {})
                csv_rows.append(
                    {
                        "capability": cap,
                        "check_id": c_id,
                        "sample_size": m.get("sample_size"),
                        "gold_flags": m.get("gold_flags"),
                        "pre_verifier_precision": m.get("pre_verifier_precision"),
                        "pre_verifier_recall": m.get("pre_verifier_recall"),
                        "post_verifier_precision": m.get("post_verifier_precision"),
                        "post_verifier_recall": m.get("post_verifier_recall"),
                        "post_verifier_ffr": m.get("post_verifier_ffr"),
                        "consistency_agreement": m.get("consistency_agreement"),
                        "consistency_jaccard": m.get("consistency_jaccard"),
                        "tp": post_cm.get("tp"),
                        "fp": post_cm.get("fp"),
                        "tn": post_cm.get("tn"),
                        "fn": post_cm.get("fn"),
                    }
                )

        if csv_rows:
            with csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
                writer.writeheader()
                writer.writerows(csv_rows)

        summary = results.get("summary", {})
        typer.echo("=== Compliance Review Metrics Summary ===")
        typer.echo(f"Total Labels: {summary.get('total_labels')}")
        typer.echo(f"Submissions Evaluated: {summary.get('total_submissions')}")
        post_p = summary.get("overall_post_verifier_precision")
        post_r = summary.get("overall_post_verifier_recall")
        pre_p = summary.get("overall_pre_verifier_precision")
        pre_r = summary.get("overall_pre_verifier_recall")
        ffr = summary.get("overall_post_verifier_ffr")
        agree = summary.get("overall_consistency_agreement")
        typer.echo(f"Overall Post-Verifier Precision: {post_p}")
        typer.echo(f"Overall Post-Verifier Recall: {post_r}")
        typer.echo(f"Overall Pre-Verifier Precision: {pre_p}")
        typer.echo(f"Overall Pre-Verifier Recall: {pre_r}")
        typer.echo(f"Overall False-Flag Rate (FFR): {ffr}")
        typer.echo(f"Overall Verdict Agreement: {agree}")
        typer.echo(f"Metrics written to {json_path} and {csv_path}")
    except (FileNotFoundError, ValueError, KeyError) as exc:
        typer.echo(f"Validation/Input error: {exc}", err=True)
        sys.exit(1)
    except Exception as exc:
        typer.echo(f"Runtime error: {exc}", err=True)
        sys.exit(2)


@audit_app.command("export")
def export_audit(
    since: str = typer.Option(..., help="Date YYYY-MM-DD"),
    out: Path = typer.Option(..., help="Output JSON path"),
) -> None:
    """Export audit log since given date (US-36)."""
    typer.echo("audit export is not implemented until P5", err=True)
    sys.exit(3)


@index_app.command("rebuild")
def rebuild_index(
    skills_root: Path = typer.Option(Path("skills"), "--skills-root", help="Root skills directory"),
    index_dir: Path = typer.Option(
        Path("data/vector_index"), "--index-dir", help="Output directory for index"
    ),
) -> None:
    """Rebuild the FAISS skills vector index (US-14/15/16)."""
    from compliance_review.retrieval.vector_index import build_skills_index

    try:
        index_path, count = build_skills_index(skills_root, index_dir)
        typer.echo(f"Built FAISS index with {count} skill versions at {index_path}")
    except Exception as exc:
        typer.echo(f"Error rebuilding index: {exc}", err=True)
        sys.exit(2)


@reviewer_app.command("feedback")
def reviewer_feedback_cmd(
    submission_id: int = typer.Option(..., "--submission-id", help="Submission ID"),
    verdict_id: int | None = typer.Option(None, "--verdict-id", help="Checklist verdict ID"),
    reviewer_id: str = typer.Option(..., "--reviewer-id", help="Reviewer identifier"),
    action: str = typer.Option(
        ..., "--action", help="approve | override | request_rerun | escalate"
    ),
    reason_code: str | None = typer.Option(
        None,
        "--reason-code",
        help=(
            "evidence_insufficient | check_not_applicable | model_misread | "
            "policy_exception | severity_mismatch | other"
        ),
    ),
    comment: str | None = typer.Option(None, "--comment", help="Reviewer comment"),
) -> None:
    """Record reviewer feedback on a submission or verdict (US-31/32)."""
    valid_actions = {"approve", "override", "request_rerun", "escalate"}
    if action not in valid_actions:
        typer.echo(f"Invalid action '{action}'. Must be one of {valid_actions}", err=True)
        sys.exit(1)

    valid_reasons = {
        "evidence_insufficient",
        "check_not_applicable",
        "model_misread",
        "policy_exception",
        "severity_mismatch",
        "other",
    }
    if reason_code is not None and reason_code not in valid_reasons:
        typer.echo(
            f"Invalid reason_code '{reason_code}'. Must be one of {valid_reasons}",
            err=True,
        )
        sys.exit(1)

    from compliance_review.db.repository import record_reviewer_feedback

    try:
        feedback_id = record_reviewer_feedback(
            submission_id=submission_id,
            verdict_id=verdict_id,
            reviewer_id=reviewer_id,
            action=action,
            reason_code=reason_code,
            comment=comment,
        )
        typer.echo(
            f"Recorded reviewer feedback id={feedback_id} action={action} "
            f"submission={submission_id} reviewer={reviewer_id}"
        )
    except Exception as exc:
        typer.echo(f"Error recording reviewer feedback: {exc}", err=True)
        sys.exit(2)


@labels_app.command("bootstrap")
def bootstrap_labels_cmd(
    submissions: Path = typer.Option(..., help="Path to submissions manifest JSON"),
    out: Path = typer.Option(..., help="Output CSV path for provisional labels"),
) -> None:
    """Export provisional labels for evaluation corpus from model review runs (US-35, Mode B)."""
    import csv
    import json

    from sqlalchemy import select

    from compliance_review.db.engine import get_engine
    from compliance_review.db.tables import checklist_verdicts, skill_executions
    from compliance_review.db.tables import submissions as subs_tbl

    if not submissions.exists():
        typer.echo(f"Error: Manifest file not found: {submissions}", err=True)
        sys.exit(1)

    try:
        data = json.loads(submissions.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "submissions" in data:
            sub_list = data["submissions"]
        elif isinstance(data, list):
            sub_list = data
        else:
            typer.echo("Error: Invalid submissions JSON format", err=True)
            sys.exit(1)

        sub_ids = [int(s["submission_id"]) for s in sub_list if "submission_id" in s]
        if not sub_ids:
            typer.echo("No submission_id entries found in manifest", err=True)
            sys.exit(1)

        engine = get_engine()
        with engine.connect() as conn:
            # Query external_ids
            sub_rows = conn.execute(
                select(subs_tbl.c.id, subs_tbl.c.external_id).where(subs_tbl.c.id.in_(sub_ids))
            ).fetchall()
            ext_map: dict[int, str] = {int(r[0]): str(r[1]) for r in sub_rows}

            # Query verdicts for run_index 1
            stmt = (
                select(
                    skill_executions.c.submission_id,
                    skill_executions.c.skill_capability,
                    skill_executions.c.skill_version,
                    checklist_verdicts.c.check_id,
                    checklist_verdicts.c.verdict,
                    checklist_verdicts.c.evidence_text,
                    checklist_verdicts.c.evidence_location,
                )
                .select_from(
                    checklist_verdicts.join(
                        skill_executions,
                        checklist_verdicts.c.execution_id == skill_executions.c.id,
                    )
                )
                .where(
                    skill_executions.c.submission_id.in_(sub_ids),
                    skill_executions.c.run_index == 1,
                )
                .order_by(
                    skill_executions.c.submission_id,
                    skill_executions.c.skill_capability,
                    checklist_verdicts.c.check_id,
                )
            )
            v_rows = conn.execute(stmt).fetchall()

        fieldnames = [
            "submission_id",
            "external_id",
            "skill_capability",
            "skill_version",
            "check_id",
            "gold_verdict",
            "gold_evidence_text",
            "gold_evidence_location",
            "annotator_1",
            "annotator_2",
            "adjudicator",
            "adjudication_status",
        ]

        csv_rows: list[dict[str, Any]] = []
        for r in v_rows:
            sid = int(r.submission_id)
            verd = str(r.verdict)
            if verd == "flag":
                prov_verdict = "flag"
                ev_text = str(r.evidence_text or "")
                ev_loc = str(r.evidence_location or "")
            elif verd == "not_applicable":
                prov_verdict = "not_applicable"
                ev_text = ""
                ev_loc = ""
            else:
                prov_verdict = "no_flag"
                ev_text = ""
                ev_loc = ""

            csv_rows.append(
                {
                    "submission_id": sid,
                    "external_id": ext_map.get(sid, f"sub_{sid}"),
                    "skill_capability": str(r.skill_capability),
                    "skill_version": str(r.skill_version),
                    "check_id": str(r.check_id),
                    "gold_verdict": prov_verdict,
                    "gold_evidence_text": ev_text,
                    "gold_evidence_location": ev_loc,
                    "annotator_1": "agent:bootstrap",
                    "annotator_2": "",
                    "adjudicator": "",
                    "adjudication_status": "pending",
                }
            )

        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

        flags_count = sum(1 for r in csv_rows if r["gold_verdict"] == "flag")
        typer.echo(
            f"Bootstrapped {len(csv_rows)} provisional labels "
            f"({flags_count} flags, {len(csv_rows) - flags_count} non-flags) across "
            f"{len(sub_ids)} submissions to {out}"
        )
    except Exception as exc:
        typer.echo(f"Error bootstrapping labels: {exc}", err=True)
        sys.exit(2)


if __name__ == "__main__":
    app()
