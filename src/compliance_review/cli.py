"""CLI entrypoint for compliance-review."""

import typer

app = typer.Typer(help="Grounded, local-first skill-retrieved compliance review.")

if __name__ == "__main__":
    app()
