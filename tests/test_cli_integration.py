"""Testes de integração — CLI ponta-a-ponta."""

import json
import os
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

    def test_query_sem_filepath_com_config(self, tmp_path, monkeypatch):
        """codemap query --ext .pas funciona sem filepath se config tiver default_dirmap."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "a.pas").write_text("", encoding="utf-8")
        (tmp_path / "b.py").write_text("", encoding="utf-8")
        out = tmp_path / "dm.json"
        env = {**os.environ, "PYTHONPATH": str(Path(__file__).parent.parent)}
        subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "dirmap", str(tmp_path), "--output", str(out)],
            capture_output=True, env=env,
        )
        (tmp_path / ".codemap.yml").write_text(
            f"dirmap:\n  default_dirmap: {out}\n", encoding="utf-8"
        )
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "query", "--ext", ".pas", "--count"],
            capture_output=True, text=True, cwd=str(tmp_path), env=env,
        )
        assert result.returncode == 0
        assert "1" in result.stdout

    def test_query_sem_filepath_sem_config_erro(self, tmp_path, monkeypatch):
        """codemap query sem filepath e sem config deve dar erro claro."""
        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "query", "--ext", ".pas"],
            capture_output=True, text=True, cwd=str(tmp_path),
        )
        assert result.returncode != 0


class TestUsesCLI:
    """Testes de integração do comando uses e flags de dependência."""

    def _make_python_project(self, tmp_path):
        """Cria projeto Python com imports para testes."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "__init__.py").write_text("", encoding="utf-8")
        (src / "main.py").write_text("from src.utils import helper\n", encoding="utf-8")
        (src / "utils.py").write_text("def helper(): pass\n", encoding="utf-8")
        return src.parent

    def _make_dirmap(self, tmp_path, extra_flags=None):
        """Gera dirmap JSON e retorna o path."""
        out = tmp_path / "dirmap.json"
        cmd = [PYTHON, "-m", CLI_MODULE, "dirmap", str(tmp_path), "--output", str(out)]
        if extra_flags:
            cmd.extend(extra_flags)
        subprocess.run(cmd, capture_output=True, text=True)
        return out

    def test_uses_comando(self, tmp_path):
        """codemap uses dirmap.json --stdout produz JSON com dependency_graph."""
        self._make_python_project(tmp_path)
        dm = self._make_dirmap(tmp_path)
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "uses", str(dm), "--stdout"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "dependency_graph" in data
        assert "nodes" in data["dependency_graph"]
        assert "edges" in data["dependency_graph"]

    def test_dirmap_com_uses(self, tmp_path):
        """codemap dirmap ./path --with-uses produz dirmap enriquecido."""
        self._make_python_project(tmp_path)
        out = tmp_path / "dm_uses.json"
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "dirmap", str(tmp_path), "--output", str(out), "--with_uses"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "dependency_graph" in data
        file_entries = [e for e in data["tree"] if e["type"] == "file"]
        py_files = [e for e in file_entries if e.get("language") == "python"]
        # Pelo menos os .py com imports devem ter o campo
        main_entry = next((e for e in py_files if "main" in e.get("path", "")), None)
        if main_entry:
            assert "imports" in main_entry

    def test_query_cycles(self, tmp_path):
        """codemap query dirmap.json --cycles retorna ciclos."""
        self._make_python_project(tmp_path)
        dm = self._make_dirmap(tmp_path, extra_flags=["--with_uses"])
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "query", str(dm), "--cycles"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)

    def test_query_depends_on(self, tmp_path):
        """codemap query dirmap.json --depends-on filtra dependências."""
        self._make_python_project(tmp_path)
        dm = self._make_dirmap(tmp_path, extra_flags=["--with_uses"])
        # Busca quem importa src/utils.py
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "query", str(dm), "--depends_on", "src/utils.py"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)

    def test_dirmap_with_metrics_and_uses(self, tmp_path):
        """codemap dirmap --with-metrics --with-uses gera ambos enriquecimentos."""
        self._make_python_project(tmp_path)
        out = tmp_path / "dm_both.json"
        result = subprocess.run(
            [PYTHON, "-m", CLI_MODULE, "dirmap", str(tmp_path),
             "--output", str(out), "--with_metrics", "--with_uses"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "dependency_graph" in data
        file_entries = [e for e in data["tree"] if e["type"] == "file"]
        py_main = next((e for e in file_entries if "main" in e.get("path", "")), None)
        if py_main:
            assert "metrics" in py_main
            assert "imports" in py_main
