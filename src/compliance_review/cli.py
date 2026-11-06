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

app.add_typer(skills_app, name="skills")
app.add_typer(audit_app, name="audit")
app.add_typer(index_app, name="index")


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


if __name__ == "__main__":
    app()
