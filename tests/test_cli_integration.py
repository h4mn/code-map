"""Testes de integração — CLI ponta-a-ponta."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

PYTHON = sys.executable
CLI_MODULE = "codemap.cli"


class TestCLIPontaAPonta:
    def test_help_dinamico(self):
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "CodeMap" in result.stdout
        assert "dirmap" in result.stdout
        assert "query" in result.stdout
        assert "repl" in result.stdout
        assert "version" in result.stdout

    def test_version(self):
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "version"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "codemap v0.1.0" in result.stdout

    def test_dirmap_gera_json(self, tmp_path):
        (tmp_path / "a.pas").write_text("", encoding="utf-8")
        (tmp_path / "b.py").write_text("", encoding="utf-8")
        out = tmp_path / "result.json"
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "dirmap", str(tmp_path), "--output", str(out)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["meta"]["tool"] == "codemap"
        assert data["summary"]["total_files"] == 2

    def test_dirmap_stdout(self, tmp_path):
        (tmp_path / "file.txt").write_text("x", encoding="utf-8")
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "dirmap", str(tmp_path), "--stdout"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["summary"]["total_files"] == 1

    def test_query_filtro(self, tmp_path):
        (tmp_path / "a.pas").write_text("", encoding="utf-8")
        (tmp_path / "b.md").write_text("", encoding="utf-8")
        out = tmp_path / "dm.json"
        subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "dirmap", str(tmp_path), "--output", str(out)],
            capture_output=True,
        )
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "query", str(out), "--ext", ".pas", "--count"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "1" in result.stdout

    def test_comando_desconhecido(self):
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "nao_existe"],
            capture_output=True, text=True,
        )
        assert result.returncode != 0

    def test_metrics_registrado(self):
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "metrics" in result.stdout

    def test_dirmap_com_metrics(self, tmp_path):
        (tmp_path / "a.pas").write_text("codigo;\n// comentario\n", encoding="utf-8")
        out = tmp_path / "dm.json"
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "dirmap", str(tmp_path), "--output", str(out), "--with_metrics"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(out.read_text(encoding="utf-8"))
        file_entries = [e for e in data["tree"] if e["type"] == "file"]
        assert len(file_entries) == 1
        assert file_entries[0]["metrics"]["loc_code"] == 1
        assert file_entries[0]["metrics"]["loc_comment"] == 1

    def test_metrics_comando(self, tmp_path):
        (tmp_path / "x.pas").write_text("codigo;\n// comentario\n", encoding="utf-8")
        dm = tmp_path / "dm.json"
        subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "dirmap", str(tmp_path), "--output", str(dm)],
            capture_output=True,
        )
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "metrics", str(dm), "--stdout"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "metrics_summary" in data
        file_entries = [e for e in data["tree"] if e["type"] == "file"]
        assert file_entries[0]["metrics"]["loc_code"] == 1

    def test_query_com_top_e_by(self, tmp_path):
        (tmp_path / "a.pas").write_text("codigo;\n// comentario\n", encoding="utf-8")
        out = tmp_path / "dm.json"
        subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "dirmap", str(tmp_path), "--output", str(out), "--with_metrics"],
            capture_output=True,
        )
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "query", str(out), "--metrics", "--top", "5", "--by", "loc_code"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) >= 1
