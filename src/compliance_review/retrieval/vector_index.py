"""FAISS vector index for skill version retrieval conforming to ARCHITECTURE.md §2.4 and §6."""

import json
from pathlib import Path
from typing import Any

import faiss  # type: ignore[import-untyped]
import numpy as np
from sentence_transformers import SentenceTransformer

from compliance_review.errors import RetrievalError
from compliance_review.skills.loader import load_all_skills

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model_cache: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """Lazy-load the sentence transformer model without importing torch in caller namespace."""
    global _model_cache
    if _model_cache is None:
        _model_cache = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model_cache


def format_skill_text(skill: Any) -> str:
    """Format skill metadata into a single text document for embedding."""
    questions = " ".join(c.question for c in skill.checklist)
    inputs_str = ", ".join(skill.inputs)
    return (
        f"Capability: {skill.capability}. "
        f"Version: {skill.version}. "
        f"Status: {skill.eval_status}. "
        f"Description: {skill.description}. "
        f"Inputs: {inputs_str}. "
        f"Checklist: {questions}"
    )


def build_skills_index(
    skills_root: Path | str = "skills",
    index_dir: Path | str = "data/vector_index",
) -> tuple[Path, int]:
    """Build FAISS vector index from all skills under skills_root and persist to index_dir."""
    root = Path(skills_root)
    out_dir = Path(index_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    loaded_skills = load_all_skills(root)
    if not loaded_skills:
        raise RetrievalError(f"No skills found in {skills_root} to index")

    keys: list[tuple[str, str]] = sorted(loaded_skills.keys())
    texts: list[str] = []
    metadata_list: list[dict[str, Any]] = []

    for cap, ver in keys:
        skill = loaded_skills[(cap, ver)]
        text = format_skill_text(skill)
        texts.append(text)
        metadata_list.append(
            {
                "capability": cap,
                "version": ver,
                "eval_status": skill.eval_status,
                "description": skill.description,
                "inputs": list(skill.inputs),
                "checklist_count": len(skill.checklist),
            }
        )

    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    # Cosine similarity requires L2-normalized vectors with IndexFlatIP
    faiss.normalize_L2(embeddings)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    index_path = out_dir / "skills.faiss"
    faiss.write_index(index, str(index_path))

    meta_path = out_dir / "skills_meta.json"
    meta_path.write_text(json.dumps(metadata_list, indent=2), encoding="utf-8")

    return index_path, len(texts)


def load_skills_index(
    index_dir: Path | str = "data/vector_index",
) -> tuple[Any, list[dict[str, Any]]]:
    """Load persisted FAISS index and metadata."""
    out_dir = Path(index_dir)
    index_path = out_dir / "skills.faiss"
    meta_path = out_dir / "skills_meta.json"

    if not index_path.is_file() or not meta_path.is_file():
        # Build index on the fly if missing
        index_path, _ = build_skills_index(index_dir=out_dir)

    index = faiss.read_index(str(index_path))
    meta: list[dict[str, Any]] = json.loads(meta_path.read_text(encoding="utf-8"))
    return index, meta


def query_skills_index(
    query_text: str,
    top_k: int = 10,
    index_dir: Path | str = "data/vector_index",
) -> list[dict[str, Any]]:
    """Query FAISS index and return scored skill metadata."""
    index, metadata_list = load_skills_index(index_dir)
    model = get_embedding_model()
    query_vec = model.encode([query_text], convert_to_numpy=True)
    query_vec = np.array(query_vec, dtype=np.float32)
    faiss.normalize_L2(query_vec)

    k = min(top_k, index.ntotal)
    if k == 0:
        return []

    distances, indices = index.search(query_vec, k)
    results: list[dict[str, Any]] = []

    for dist, idx in zip(distances[0], indices[0], strict=False):
        if idx == -1:
            continue
        entry = dict(metadata_list[idx])
        entry["score"] = float(dist)
        results.append(entry)

    return results
