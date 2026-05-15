"""Testes do motor de consultas."""

import json
import pytest
from pathlib import Path

from codemap.dirmap.query import query


SAMPLE_DATA = {
    "meta": {"root_name": "TestRepo"},
    "summary": {
        "total_files": 5,
        "total_dirs": 2,
        "total_size_bytes": 1000,
        "by_extension": {".pas": 2, ".py": 2, ".md": 1},
        "by_language": {"delphi": 2, "python": 2, "markdown": 1},
    },
    "tree": [
        {"path": "src/Model/Clientes.pas", "type": "file", "extension": ".pas", "language": "delphi", "size_bytes": 500},
        {"path": "src/Model/Utils.pas", "type": "file", "extension": ".pas", "language": "delphi", "size_bytes": 200},
        {"path": "src/main.py", "type": "file", "extension": ".py", "language": "python", "size_bytes": 100},
        {"path": "tests/test_main.py", "type": "file", "extension": ".py", "language": "python", "size_bytes": 150},
        {"path": "README.md", "type": "file", "extension": ".md", "language": "markdown", "size_bytes": 50},
        {"path": "src", "type": "dir"},
        {"path": "src/Model", "type": "dir"},
    ],
}


class TestQueryExt:
    def test_filtro_ext(self):
        result = query(SAMPLE_DATA, ext=".pas")
        assert len(result) == 2
        assert all(e["extension"] == ".pas" for e in result)

    def test_ext_sem_match(self):
        result = query(SAMPLE_DATA, ext=".xyz")
        assert result == []


class TestQueryLang:
    def test_filtro_lang(self):
        result = query(SAMPLE_DATA, lang="python")
        assert len(result) == 2

    def test_lang_sem_match(self):
        result = query(SAMPLE_DATA, lang="java")
        assert result == []


class TestQueryPath:
    def test_filtro_path(self):
        result = query(SAMPLE_DATA, path="src/Model")
        assert len(result) == 3  # 2 files + 1 dir


class TestQueryType:
    def test_filtro_type_file(self):
        result = query(SAMPLE_DATA, type="file")
        assert len(result) == 5

    def test_filtro_type_dir(self):
        result = query(SAMPLE_DATA, type="dir")
        assert len(result) == 2


class TestQueryCount:
    def test_count_simples(self):
        result = query(SAMPLE_DATA, ext=".pas", count=True)
        assert result == 2

    def test_count_com_filtro(self):
        result = query(SAMPLE_DATA, ext=".py", path="src", count=True)
        assert result == 1


class TestQuerySummary:
    def test_summary(self):
        result = query(SAMPLE_DATA, summary=True)
        assert result["total_files"] == 5
        assert result["by_language"]["delphi"] == 2


class TestQueryCombinacao:
    def test_ext_e_path(self):
        result = query(SAMPLE_DATA, ext=".pas", path="src/Model")
        assert len(result) == 2

    def test_lang_e_path(self):
        result = query(SAMPLE_DATA, lang="python", path="src")
        assert len(result) == 1


class TestQueryVazio:
    def test_sem_filtros(self):
        result = query(SAMPLE_DATA)
        assert len(result) == 7  # 5 files + 2 dirs

    def test_data_vazia(self):
        data = {"tree": [], "summary": {"total_files": 0}}
        result = query(data, ext=".pas")
        assert result == []


# ---------------------------------------------------------------------------
# Dependency graph queries (depends_on, depended_by, cycles)
# ---------------------------------------------------------------------------

DATA_WITH_GRAPH = {
    "meta": {"root_name": "TestRepo"},
    "summary": {"total_files": 3, "total_dirs": 0},
    "tree": [
        {"path": "src/A.py", "type": "file", "extension": ".py", "language": "python"},
        {"path": "src/B.py", "type": "file", "extension": ".py", "language": "python"},
        {"path": "src/C.py", "type": "file", "extension": ".py", "language": "python"},
    ],
    "dependency_graph": {
        "nodes": [
            {"id": "src/A.py", "fan_in": 1, "fan_out": 1},
            {"id": "src/B.py", "fan_in": 2, "fan_out": 1},
            {"id": "src/C.py", "fan_in": 0, "fan_out": 1},
        ],
        "edges": [
            {"from": "src/A.py", "to": "src/B.py"},
            {"from": "src/C.py", "to": "src/B.py"},
            {"from": "src/B.py", "to": "src/A.py"},
        ],
        "cycles": [
            ["src/A.py", "src/B.py", "src/A.py"],
        ],
    },
}


class TestQueryDependsOn:
    def test_depends_on_returns_who_imports_target(self):
        """depends_on: encontra quem importa o caminho dado."""
        result = query(DATA_WITH_GRAPH, depends_on="src/B.py")
        assert isinstance(result, list)
        # A e C importam B
        paths = [e["path"] for e in result]
        assert "src/A.py" in paths
        assert "src/C.py" in paths

    def test_depends_on_no_match(self):
        result = query(DATA_WITH_GRAPH, depends_on="nonexistent.py")
        assert result == []

    def test_depends_on_none_is_noop(self):
        result = query(DATA_WITH_GRAPH, depends_on=None)
        # Sem filtro de dependência, retorna entries normais (sem métricas)
        assert len(result) == 3


class TestQueryDependedBy:
    def test_depended_by_returns_what_source_imports(self):
        """depended_by: encontra o que o caminho dado importa."""
        result = query(DATA_WITH_GRAPH, depended_by="src/A.py")
        assert isinstance(result, list)
        paths = [e["path"] for e in result]
        # A importa B
        assert "src/B.py" in paths

    def test_depended_by_no_match(self):
        result = query(DATA_WITH_GRAPH, depended_by="nonexistent.py")
        assert result == []

    def test_depended_by_none_is_noop(self):
        result = query(DATA_WITH_GRAPH, depended_by=None)
        assert len(result) == 3


class TestQueryCycles:
    def test_cycles_returns_cycle_list(self):
        result = query(DATA_WITH_GRAPH, cycles=True)
        assert isinstance(result, list)
        assert len(result) >= 1
        # Pelo menos um ciclo contém A e B
        found = any("src/A.py" in c and "src/B.py" in c for c in result)
        assert found

    def test_cycles_false_returns_entries(self):
        result = query(DATA_WITH_GRAPH, cycles=False)
        # cycles=False é o default, retorna entries
        assert isinstance(result, list)
        assert len(result) == 3

    def test_cycles_empty_when_no_graph(self):
        data = {"tree": [], "summary": {}, "dependency_graph": {"nodes": [], "edges": [], "cycles": []}}
        result = query(data, cycles=True)
        assert result == []

    def test_cycles_missing_dependency_graph(self):
        data = {"tree": [], "summary": {}}
        result = query(data, cycles=True)
        assert result == []
