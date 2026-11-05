"""Ollama Qwen client wrapper conforming to ARCHITECTURE.md §2.3, §5.3, and US-19."""

import time

import ollama

from compliance_review.errors import ModelError

MODEL_NAME = "qwen3:4b"


def resolve_model_digest(client: ollama.Client | None = None) -> str:
    """Resolve the sha256 digest of the qwen3:4b model.

    Refuses execution and raises ModelError if digest cannot be resolved.
    """
    if client is None:
        client = ollama.Client()

    # Attempt 1: client.show()
    try:
        show_info = client.show(MODEL_NAME)
        d = (
            show_info.get("digest")
            if isinstance(show_info, dict)
            else getattr(show_info, "digest", None)
        )
        if d and isinstance(d, str):
            return str(d)
    except Exception:
        pass

    # Attempt 2: client.list()
    try:
        models_data = client.list()
        models = (
            models_data.get("models", [])
            if isinstance(models_data, dict)
            else getattr(models_data, "models", [])
        )
        for m in models:
            m_name = m.get("name", "") if isinstance(m, dict) else getattr(m, "name", "")
            m_model = m.get("model", "") if isinstance(m, dict) else getattr(m, "model", "")
            if m_name == MODEL_NAME or m_model == MODEL_NAME:
                digest = m.get("digest") if isinstance(m, dict) else getattr(m, "digest", "")
                if digest and isinstance(digest, str):
                    return str(digest)
    except Exception as exc:
        raise ModelError(f"Failed to query Ollama for model {MODEL_NAME}: {exc}") from exc

    raise ModelError(
        f"Model digest for '{MODEL_NAME}' could not be resolved from Ollama. "
        f"Ensure 'ollama pull {MODEL_NAME}' has been run."
    )


def call_qwen(
    prompt: str,
    run_index: int = 1,
    client: ollama.Client | None = None,
) -> tuple[str, str, int]:
    """Execute Qwen completion with strictly frozen sampling parameters.

    Sampling constraints (ARCHITECTURE.md §2.3):
      temperature = 0.0
      top_p = 1.0
      seed = run_index
      num_predict = 2048
      format = 'json'

    Returns:
      (raw_output_text, model_digest, latency_ms)
    """
    if client is None:
        client = ollama.Client()

    digest = resolve_model_digest(client)
    opts = ollama.Options(
        temperature=0.0,
        top_p=1.0,
        seed=run_index,
        num_predict=2048,
    )

    start = time.perf_counter()
    try:
        response = client.generate(
            model=MODEL_NAME,
            prompt=prompt,
            stream=False,
            format="json",
            options=opts,
        )
        if isinstance(response, dict):
            raw_text = response.get("response", "")
        else:
            raw_text = getattr(response, "response", "")
    except Exception as exc:
        raise ModelError(f"Ollama execution failed for {MODEL_NAME}: {exc}") from exc

    latency_ms = int((time.perf_counter() - start) * 1000)
    return str(raw_text), digest, latency_ms
