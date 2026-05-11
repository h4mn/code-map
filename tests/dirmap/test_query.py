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
