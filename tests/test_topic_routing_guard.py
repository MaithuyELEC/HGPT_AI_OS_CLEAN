from __future__ import annotations

import ast
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src" / "hgpt_ai_os"
ROUTING_PATHS = (
    SRC / "content",
    SRC / "topic_engine",
)


def _routing_files() -> list[Path]:
    return [
        path
        for root in ROUTING_PATHS
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
    ]


def _string_literals(node: ast.AST) -> list[str]:
    return [
        item.value
        for item in ast.walk(node)
        if isinstance(item, ast.Constant) and isinstance(item.value, str)
    ]


class TopicRoutingGuardTests(unittest.TestCase):
    def test_topic_routing_does_not_branch_on_literal_topic_terms(self):
        violations: list[str] = []

        for path in _routing_files():
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.If):
                    continue

                condition = ast.unparse(node.test)
                literals = _string_literals(node.test)
                branches_on_topic = "topic" in condition or "playbook.key" in condition
                if branches_on_topic and literals:
                    relpath = path.relative_to(SRC.parents[1])
                    violations.append(f"{relpath}:{node.lineno}: {condition}")

        self.assertFalse(violations, "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
