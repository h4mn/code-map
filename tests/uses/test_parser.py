"""Testes do dispatcher de parsers — parse_imports()."""

import pytest
from pathlib import Path

from codemap.uses.parser import parse_imports


class TestDispatchDelphi:
    def test_delphi_file(self, tmp_path):
        src = tmp_path / "UnitA.pas"
        src.write_text(
            "unit UnitA;\n\ninterface\n\nuses UnitB;\n\nimplementation\n\nend.\n",
            encoding="utf-8",
        )
        refs = parse_imports(src, "delphi")
        assert len(refs) == 1
        assert refs[0]["name"] == "UnitB"
        assert refs[0]["section"] == "interface"
        assert refs[0]["line"] > 0
        assert refs[0]["unresolved"] is False

    def test_delphi_inexistente(self):
        refs = parse_imports(Path("/nao/existe.pas"), "delphi")
        assert refs == []


class TestDispatchPython:
    def test_python_file(self, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("import os\nfrom pathlib import Path\n", encoding="utf-8")
        refs = parse_imports(src, "python")
        assert len(refs) == 2
        names = {r["name"] for r in refs}
        assert "os" in names
        assert "pathlib" in names

    def test_python_inexistente(self):
        refs = parse_imports(Path("/nao/existe.py"), "python")
        assert refs == []


class TestDispatchJsTs:
    def test_typescript_file(self, tmp_path):
        src = tmp_path / "app.ts"
        src.write_text("import React from 'react';\n", encoding="utf-8")
        refs = parse_imports(src, "typescript")
        assert len(refs) == 1
        assert refs[0]["name"] == "react"
        assert refs[0]["section"] == "import"

    def test_javascript_file(self, tmp_path):
        src = tmp_path / "app.js"
        src.write_text("const path = require('path');\n", encoding="utf-8")
        refs = parse_imports(src, "javascript")
        assert len(refs) == 1
        assert refs[0]["name"] == "path"
        assert refs[0]["section"] == "require"

    def test_js_inexistente(self):
        refs = parse_imports(Path("/nao/existe.js"), "javascript")
        assert refs == []


class TestDispatchSemSuporte:
    def test_markdown_retorna_vazio(self, tmp_path):
        src = tmp_path / "readme.md"
        src.write_text("# Hello\n", encoding="utf-8")
        refs = parse_imports(src, "markdown")
        assert refs == []

    def test_linguagem_desconhecida_retorna_vazio(self, tmp_path):
        src = tmp_path / "data.csv"
        src.write_text("a,b,c\n", encoding="utf-8")
        refs = parse_imports(src, "csv")
        assert refs == []


class TestNormalizedFormat:
    def test_todos_refs_tem_campos_obrigatorios(self, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("import os\n", encoding="utf-8")
        refs = parse_imports(src, "python")
        assert len(refs) == 1
        ref = refs[0]
        # Campos obrigatorios do formato normalizado
        assert "name" in ref
        assert "section" in ref
        assert "line" in ref
        assert "unresolved" in ref
        assert isinstance(ref["name"], str)
        assert isinstance(ref["section"], str)
        assert isinstance(ref["line"], int)
        assert isinstance(ref["unresolved"], bool)
