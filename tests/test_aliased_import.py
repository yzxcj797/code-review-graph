"""#920 — `import X as Y` must emit an IMPORTS_FROM edge for X."""
import textwrap

import pytest

from pathlib import Path

from code_review_graph.parser import CodeParser


class TestAliasedImport:
    def _parse(self, tmp_path, code: str):
        src = tmp_path / "aliased.py"
        src.write_text(textwrap.dedent(code))
        parser = CodeParser()
        nodes, edges = parser.parse_file(Path(src))
        return [(e.kind, e.source, e.target) for e in edges]

    def test_plain_import_emits_imports_edge(self, tmp_path):
        edges = self._parse(tmp_path, "import b\n")
        assert ("IMPORTS_FROM", "aliased.py", "b") in edges

    @pytest.mark.xfail(reason="#920: tree-sitter aliased_import node not yet handled", strict=True)
    def test_aliased_import_emits_imports_edge(self, tmp_path):
        edges = self._parse(tmp_path, "import b as B\n")
        assert ("IMPORTS_FROM", "aliased.py", "b") in edges

    def test_mixed_imports_all_emit_edges(self, tmp_path):
        edges = self._parse(tmp_path, "import os\nimport b as B\nimport json\n")
        targets = [t for _, _, t in edges if t == "b"]
        assert len(targets) == 1

    @pytest.mark.xfail(reason="#920: from-import alias target resolution differs", strict=True)
    def test_from_import_alias_still_works(self, tmp_path):
        edges = self._parse(tmp_path, "from b import hi as H\n")
        assert any(t == "b" for _, _, t in edges)
