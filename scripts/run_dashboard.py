"""Convenience wrapper to launch the Streamlit dashboard."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    app_path = Path(__file__).resolve().parent.parent / "src" / "compliance_review" / "dashboard" / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
