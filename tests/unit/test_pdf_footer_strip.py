"""Unit test for PDF page footer/header stripping conforming to US-01 and D-042."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pymupdf  # type: ignore[import-untyped]

from compliance_review.ingestion.pdf import ingest_pdf


def test_pdf_footer_strip() -> None:
    """Verify that common PDF page metadata like 'Page 1 of 2' is stripped during ingestion."""
    doc = pymupdf.open()
    page = doc.new_page()

    sample_content = (
        "References\n"
        "[1] Foo. DOI: 10.1000/182\n"
        "Page 1 of 2\n"
        "trn:oid:::1:3700872727\n"
        "[2] Bar. DOI: 10.1000/183\n"
    )
    page.insert_text((50, 72), sample_content, fontsize=11)

    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "test_footer.pdf"
        doc.save(str(pdf_path))
        doc.close()

        extracted_text, sha256_hash, pages = ingest_pdf(pdf_path)

        assert "Page 1 of 2" not in extracted_text
        assert "trn:oid:::1:3700872727" not in extracted_text
        assert "[1] Foo" in extracted_text
        assert "[2] Bar" in extracted_text

        assert 1 in pages
        assert "Page 1 of 2" not in pages[1]
        assert "trn:oid:::1:3700872727" not in pages[1]
        assert "[1] Foo" in pages[1]
        assert "[2] Bar" in pages[1]
