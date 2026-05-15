"""Testes do enricher — enrich_dirmap_with_uses() e run_uses()."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from codemap.config import DirmapConfig
from codemap.uses.enricher import enrich_dirmap_with_uses, run_uses


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_DIRMAP = {
    "meta": {
        "tool": "codemap",
        "command": "dirmap",
        "version": "0.1.0",
        "root": "/project",
        "root_name": "project",
    },
    "errors": [],
    "summary": {
        "total_files": 4,
        "total_dirs": 2,
        "total_size_bytes": 1000,
    },
    "tree": [
        {"path": "src/main.py", "type": "file", "extension": ".py", "language": "python", "size_bytes": 200},
        {"path": "src/utils.py", "type": "file", "extension": ".py", "language": "python", "size_bytes": 150},
        {"path": "src/Model/Clientes.pas", "type": "file", "extension": ".pas", "language": "delphi", "size_bytes": 300},
        {"path": "README.md", "type": "file", "extension": ".md", "language": "markdown", "size_bytes": 50},
        {"path": "src", "type": "dir"},
        {"path": "src/Model", "type": "dir"},
    ],
}


def _make_dirmap_with_files(tmp_path, files: dict[str, str]):
    """Helper: cria arquivos físicos e gera dirmap dict."""
    for relpath, content in files.items():
        p = tmp_path / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    return {
        "meta": {"tool": "codemap", "command": "dirmap", "version": "0.1.0",
                 "root": str(tmp_path), "root_name": tmp_path.name},
        "errors": [],
        "summary": {"total_files": len(files), "total_dirs": 0, "total_size_bytes": 0},
        "tree": [
            {
                "path": relpath,
                "type": "file",
                "extension": Path(relpath).suffix,
                "language": _lang_for(Path(relpath).suffix),
                "size_bytes": len(content),
            }
            for relpath, content in files.items()
        ],
    }


def _lang_for(ext: str) -> str:
    return {".py": "python", ".pas": "delphi", ".md": "markdown"}.get(ext, "unknown")


# ---------------------------------------------------------------------------
# 1. enrich_dirmap_with_uses — imports added to file entries
# ---------------------------------------------------------------------------

class TestEnrichDirmapImports:
    def test_adds_imports_to_python_files(self, tmp_path):
        files = {
            "src/main.py": "from src.utils import helper\n",
            "src/utils.py": "def helper(): pass\n",
        }
        data = _make_dirmap_with_files(tmp_path, files)
        config = DirmapConfig()
        result = enrich_dirmap_with_uses(data, str(tmp_path), config)

        file_entries = [e for e in result["tree"] if e["type"] == "file"]
        main_entry = next(e for e in file_entries if "main.py" in e["path"])
        assert "imports" in main_entry
        assert isinstance(main_entry["imports"], list)

    def test_imports_field_contains_resolved_paths(self, tmp_path):
        files = {
            "src/main.py": "import os\nfrom src.utils import helper\n",
            "src/utils.py": "def helper(): pass\n",
        }
        data = _make_dirmap_with_files(tmp_path, files)
        config = DirmapConfig()
        result = enrich_dirmap_with_uses(data, str(tmp_path), config)

        file_entries = [e for e in result["tree"] if e["type"] == "file"]
        main_entry = next(e for e in file_entries if "main.py" in e["path"])
        imports = main_entry["imports"]
        # Deve ter pelo menos 1 import (os ou utils)
        assert len(imports) >= 1
        # Cada import deve ter resolved_path
        for imp in imports:
            assert "resolved_path" in imp
            assert "unresolved" in imp


# ---------------------------------------------------------------------------
# 2. enrich_dirmap_with_uses — dependency_graph at root
# ---------------------------------------------------------------------------

class TestEnrichDirmapGraph:
    def test_adds_dependency_graph_at_root(self, tmp_path):
        files = {
            "src/main.py": "from src.utils import helper\n",
            "src/utils.py": "def helper(): pass\n",
        }
        data = _make_dirmap_with_files(tmp_path, files)
        config = DirmapConfig()
        result = enrich_dirmap_with_uses(data, str(tmp_path), config)

        assert "dependency_graph" in result
        graph = result["dependency_graph"]
        assert "nodes" in graph
        assert "edges" in graph
        assert "cycles" in graph

    def test_dependency_graph_has_edges_for_imports(self, tmp_path):
        files = {
            "src/main.py": "from src.utils import helper\n",
            "src/utils.py": "def helper(): pass\n",
        }
        data = _make_dirmap_with_files(tmp_path, files)
        config = DirmapConfig()
        result = enrich_dirmap_with_uses(data, str(tmp_path), config)

        graph = result["dependency_graph"]
        if graph["edges"]:
            # Se resolveu, main deve ter edge para utils
            edge_pairs = {(e["from"], e["to"]) for e in graph["edges"]}
            assert any("main.py" in e[0] for e in edge_pairs)


# ---------------------------------------------------------------------------
# 3. Retrocompatibility — unsupported languages don't get imports field
# ---------------------------------------------------------------------------

class TestRetrocompatibility:
    def test_unsupported_language_no_imports_field(self, tmp_path):
        """Arquivos com linguagem sem parser não recebem campo imports."""
        data = {
            "meta": {"root": str(tmp_path), "root_name": "test"},
            "summary": {"total_files": 1, "total_dirs": 0, "total_size_bytes": 0},
            "tree": [
                {"path": "README.md", "type": "file", "extension": ".md", "language": "markdown", "size_bytes": 50},
            ],
        }
        config = DirmapConfig()
        result = enrich_dirmap_with_uses(data, str(tmp_path), config)

        file_entries = [e for e in result["tree"] if e["type"] == "file"]
        assert len(file_entries) == 1
        md_entry = file_entries[0]
        assert "imports" not in md_entry

    def test_dir_entries_unchanged(self, tmp_path):
        """Diretórios não são afetados pelo enricher."""
        data = {
            "meta": {"root": str(tmp_path), "root_name": "test"},
            "summary": {"total_files": 0, "total_dirs": 1, "total_size_bytes": 0},
            "tree": [
                {"path": "src", "type": "dir"},
            ],
        }
        config = DirmapConfig()
        result = enrich_dirmap_with_uses(data, str(tmp_path), config)

        dir_entries = [e for e in result["tree"] if e["type"] == "dir"]
        assert len(dir_entries) == 1
        assert "imports" not in dir_entries[0]

    def test_empty_tree_works(self, tmp_path):
        """Dirmap vazio não quebra."""
        data = {
            "meta": {"root": str(tmp_path), "root_name": "test"},
            "summary": {"total_files": 0, "total_dirs": 0, "total_size_bytes": 0},
            "tree": [],
        }
        config = DirmapConfig()
        result = enrich_dirmap_with_uses(data, str(tmp_path), config)
        assert "dependency_graph" in result
        assert result["dependency_graph"]["nodes"] == []
        assert result["dependency_graph"]["edges"] == []


# ---------------------------------------------------------------------------
# 4. run_uses — CLI entry point
# ---------------------------------------------------------------------------

class TestRunUses:
    def test_stdout_outputs_valid_json(self, tmp_path):
        files = {
            "main.py": "import os\n",
        }
        data = _make_dirmap_with_files(tmp_path, files)
        dm_path = tmp_path / "dirmap.json"
        dm_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            run_uses(str(dm_path), stdout=True)

        output = f.getvalue()
        parsed = json.loads(output)
        assert "dependency_graph" in parsed
        assert "tree" in parsed

    def test_run_uses_writes_to_file(self, tmp_path):
        files = {
            "main.py": "import os\n",
        }
        data = _make_dirmap_with_files(tmp_path, files)
        dm_path = tmp_path / "dirmap.json"
        dm_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        out_path = tmp_path / "output.json"
        run_uses(str(dm_path), output=str(out_path))

        assert out_path.exists()
        parsed = json.loads(out_path.read_text(encoding="utf-8"))
        assert "dependency_graph" in parsed

    def test_run_uses_file_not_found(self, tmp_path):
        with pytest.raises(SystemExit):
            run_uses(str(tmp_path / "nonexistent.json"), stdout=True)
