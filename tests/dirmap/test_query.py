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

    def test_depends_on_backslash_normalized(self):
        """depends_on: normaliza backslashes para forward slashes."""
        result = query(DATA_WITH_GRAPH, depends_on="src\\B.py")
        paths = [e["path"] for e in result]
        assert "src/A.py" in paths
        assert "src/C.py" in paths

    def test_depends_on_basename_match(self):
        """depends_on: fallback para basename quando path exato não match."""
        result = query(DATA_WITH_GRAPH, depends_on="B")
        paths = [e["path"] for e in result]
        assert "src/A.py" in paths
        assert "src/C.py" in paths

    def test_depends_on_substring_match(self):
        """depends_on: fallback para substring quando exato não match."""
        result = query(DATA_WITH_GRAPH, depends_on="B.py")
        paths = [e["path"] for e in result]
        assert "src/A.py" in paths
        assert "src/C.py" in paths


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

    def test_depended_by_backslash_normalized(self):
        """depended_by: normaliza backslashes para forward slashes."""
        result = query(DATA_WITH_GRAPH, depended_by="src\\A.py")
        paths = [e["path"] for e in result]
        assert "src/B.py" in paths

    def test_depended_by_basename_match(self):
        """depended_by: fallback para basename quando path exato não match."""
        result = query(DATA_WITH_GRAPH, depended_by="A")
        paths = [e["path"] for e in result]
        assert "src/B.py" in paths


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


# ---------------------------------------------------------------------------
# Substring path matching (melhoria #1)
# ---------------------------------------------------------------------------

class TestQueryPathSubstring:
    def test_path_substring_match(self):
        """--path deve fazer substring match, não só prefixo."""
        result = query(SAMPLE_DATA, path="Model")
        paths = [e["path"] for e in result]
        assert "src/Model/Clientes.pas" in paths
        assert "src/Model/Utils.pas" in paths
        assert "src/Model" in paths

    def test_path_substring_nome_arquivo(self):
        """--path deve buscar no nome do arquivo também, não só diretório."""
        result = query(SAMPLE_DATA, path="Clientes")
        paths = [e["path"] for e in result]
        assert "src/Model/Clientes.pas" in paths

    def test_path_substring_sem_match(self):
        result = query(SAMPLE_DATA, path="Inexistente")
        assert result == []

    def test_path_preserva_compat_prefixo(self):
        """--path com prefixo de diretório continua funcionando."""
        result = query(SAMPLE_DATA, path="src/Model")
        assert len(result) == 3  # 2 files + 1 dir


# ---------------------------------------------------------------------------
# Case-insensitive (melhoria #3)
# ---------------------------------------------------------------------------

class TestQueryCaseInsensitive:
    def test_path_case_insensitive_default(self):
        """Busca de path deve ser case-insensitive por padrão."""
        result_lower = query(SAMPLE_DATA, path="model")
        result_upper = query(SAMPLE_DATA, path="Model")
        paths_lower = {e["path"] for e in result_lower}
        paths_upper = {e["path"] for e in result_upper}
        assert paths_lower == paths_upper

    def test_ext_case_insensitive_default(self):
        """ext deve ser case-insensitive por padrão."""
        result = query(SAMPLE_DATA, ext=".PAS")
        assert len(result) == 2

    def test_lang_case_insensitive_default(self):
        """lang deve ser case-insensitive por padrão."""
        result = query(SAMPLE_DATA, lang="Delphi")
        assert len(result) == 2

    def test_case_sensitive_override_path(self):
        """Com case_sensitive=True, path respeita case."""
        result = query(SAMPLE_DATA, path="model", case_sensitive=True)
        assert result == []

    def test_case_sensitive_override_ext(self):
        """Com case_sensitive=True, ext respeita case."""
        result = query(SAMPLE_DATA, ext=".PAS", case_sensitive=True)
        assert result == []


# ---------------------------------------------------------------------------
# Glob/wildcard no --path (melhoria #5)
# ---------------------------------------------------------------------------

class TestQueryPathGlob:
    def test_path_glob_asterisco(self):
        """--path com * deve fazer glob matching."""
        result = query(SAMPLE_DATA, path="*Clientes*")
        paths = [e["path"] for e in result]
        assert "src/Model/Clientes.pas" in paths

    def test_path_glob_segmento_diretorio(self):
        """--path com glob de segmento de diretório."""
        result = query(SAMPLE_DATA, path="*/Model/*")
        paths = [e["path"] for e in result]
        assert "src/Model/Clientes.pas" in paths
        assert "src/Model/Utils.pas" in paths

    def test_path_glob_extensao(self):
        """--path com glob de extensão."""
        result = query(SAMPLE_DATA, path="*.pas")
        paths = [e["path"] for e in result]
        assert len(paths) == 2
        assert all(p.endswith(".pas") for p in paths)

    def test_path_glob_sem_match(self):
        result = query(SAMPLE_DATA, path="*Inexistente*")
        assert result == []

    def test_path_glob_case_insensitive(self):
        """Glob também deve ser case-insensitive por padrão."""
        result = query(SAMPLE_DATA, path="*clientes*")
        paths = [e["path"] for e in result]
        assert "src/Model/Clientes.pas" in paths
