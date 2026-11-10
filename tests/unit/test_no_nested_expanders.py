"""Lint-level AST test asserting no nested expanders in dashboard pages (TF-004, TF-008)."""

from __future__ import annotations

import ast
from pathlib import Path


def _is_expander_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and (
        (isinstance(node.func, ast.Attribute) and node.func.attr == "expander")
        or (isinstance(node.func, ast.Name) and node.func.id == "expander")
    )


class NestedExpanderVisitor(ast.NodeVisitor):
    """AST visitor tracking st.expander depth to disallow nesting."""

    def __init__(self) -> None:
        self.depth: int = 0
        self.violations: list[int] = []

    def visit_With(self, node: ast.With) -> None:  # noqa: N802
        has_expander = any(_is_expander_call(item.context_expr) for item in node.items)
        if has_expander:
            if self.depth > 0:
                self.violations.append(node.lineno)
            self.depth += 1
            self.generic_visit(node)
            self.depth -= 1
        else:
            self.generic_visit(node)


def test_no_nested_expanders_in_dashboard_pages() -> None:
    """Assert that zero files in dashboard/pages/ contain nested st.expander blocks."""
    pages_dir = Path("src/compliance_review/dashboard/pages")
    assert pages_dir.exists(), f"Pages directory not found: {pages_dir}"

    all_violations: dict[str, list[int]] = {}

    for page_path in sorted(pages_dir.glob("*.py")):
        source = page_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(page_path))
        visitor = NestedExpanderVisitor()
        visitor.visit(tree)
        if visitor.violations:
            all_violations[page_path.name] = visitor.violations

    assert not all_violations, (
        f"Forbidden nested st.expander() blocks detected: {all_violations}. "
        "Streamlit forbids nested expanders. Render inner content with st.code instead."
    )
