"""Python code repository ingestion conforming to ARCHITECTURE.md §2.5 and US-02."""

import hashlib
import zipfile
from pathlib import Path

from compliance_review.errors import IngestError


def ingest_repo(repo_path: Path | str) -> tuple[dict[str, str], str, int]:
    """Ingest Python code submission (directory or .zip).

    Returns:
      (files_dict, sha256_of_concatenated_hashes, total_loc)
    """
    path = Path(repo_path)
    if not path.exists():
        raise IngestError(f"Repository path not found: {path}")

    files: dict[str, str] = {}
    file_hashes: list[str] = []

    if path.is_file() and path.suffix == ".zip":
        try:
            with zipfile.ZipFile(path, "r") as zf:
                for name in sorted(zf.namelist()):
                    if name.endswith(".py") and not name.startswith("__MACOSX"):
                        content = zf.read(name).decode("utf-8", errors="replace")
                        files[name] = content
                        file_hashes.append(hashlib.sha256(content.encode("utf-8")).hexdigest())
        except Exception as exc:
            raise IngestError(f"Failed to read zip archive {path}: {exc}") from exc
    elif path.is_dir():
        try:
            for py_file in sorted(path.rglob("*.py")):
                rel_name = py_file.relative_to(path).as_posix()
                content = py_file.read_text(encoding="utf-8", errors="replace")
                files[rel_name] = content
                file_hashes.append(hashlib.sha256(content.encode("utf-8")).hexdigest())
        except Exception as exc:
            raise IngestError(f"Failed to read directory {path}: {exc}") from exc
    else:
        raise IngestError(f"Expected Python directory or .zip archive, got: {path}")

    if not files:
        raise IngestError(f"No Python source files found in {path}")

    concat_hashes = "".join(file_hashes)
    overall_sha256 = hashlib.sha256(concat_hashes.encode("utf-8")).hexdigest()
    total_loc = sum(len(c.splitlines()) for c in files.values())

    return files, overall_sha256, total_loc
