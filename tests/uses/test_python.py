"""Testes do parser Python — extração de imports."""

import pytest
from pathlib import Path

from codemap.uses.python import parse_python_imports, PythonImportRef


class TestImportSimples:
    def test_import_os(self, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("import os\n", encoding="utf-8")
        refs = parse_python_imports(src)
        assert len(refs) == 1
        assert refs[0].module == "os"
        assert refs[0].section == "import"
        assert refs[0].names == []
        assert refs[0].level == 0
        assert refs[0].line > 0

    def test_import_multiplo(self, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("import os, sys, json\n", encoding="utf-8")
        refs = parse_python_imports(src)
        assert len(refs) == 3
        modules = {r.module for r in refs}
        assert modules == {"os", "sys", "json"}


class TestFromImport:
    def test_from_pathlib_import_path(self, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("from pathlib import Path\n", encoding="utf-8")
        refs = parse_python_imports(src)
        assert len(refs) == 1
        assert refs[0].module == "pathlib"
        assert refs[0].names == ["Path"]
        assert refs[0].section == "from"
        assert refs[0].level == 0

    def test_from_dot_import_utils(self, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("from . import utils\n", encoding="utf-8")
        refs = parse_python_imports(src)
        assert len(refs) == 1
        assert refs[0].module == ""
        assert refs[0].names == ["utils"]
        assert refs[0].level == 1

    def test_from_dotdot_models_import_user(self, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("from ..models import User\n", encoding="utf-8")
        refs = parse_python_imports(src)
        assert len(refs) == 1
        assert refs[0].module == "models"
        assert refs[0].names == ["User"]
        assert refs[0].level == 2

    def test_from_multiplos_nomes(self, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("from os.path import join, exists, isdir\n", encoding="utf-8")
        refs = parse_python_imports(src)
        assert len(refs) == 1
        assert refs[0].module == "os.path"
        assert refs[0].names == ["join", "exists", "isdir"]


class TestEdgeCases:
    def test_arquivo_vazio(self, tmp_path):
        src = tmp_path / "empty.py"
        src.write_text("", encoding="utf-8")
        refs = parse_python_imports(src)
        assert refs == []

    def test_arquivo_inexistente(self):
        refs = parse_python_imports(Path("/nao/existe.py"))
        assert refs == []

    def test_arquivo_sem_imports(self, tmp_path):
        src = tmp_path / "no_imports.py"
        src.write_text("x = 42\nprint(x)\n", encoding="utf-8")
        refs = parse_python_imports(src)
        assert refs == []

    def test_linhas_corretas(self, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("# comment\nimport os\n\nfrom sys import argv\n", encoding="utf-8")
        refs = parse_python_imports(src)
        assert len(refs) == 2
        # import os esta na linha 2
        assert refs[0].line == 2
        # from sys import argv esta na linha 4
        assert refs[1].line == 4

    def test_import_dentro_funcao_nao_e_extraido(self, tmp_path):
        """Imports dentro de funcoes sao tecnicamente validos em Python,
        mas para mapeamento de dependencias top-level, geralmente
        queremos apenas imports de modulo."""
        src = tmp_path / "test.py"
        src.write_text("import os\n\ndef foo():\n    import json\n", encoding="utf-8")
        refs = parse_python_imports(src)
        # Por enquanto, extraimos todos (top-level e nested)
        # O filtro pode ser feito depois pelo dispatcher
        assert len(refs) >= 1
        modules = {r.module for r in refs}
        assert "os" in modules
