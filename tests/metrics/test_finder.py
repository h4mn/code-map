"""Testes do MetricsFinder."""

import pytest
from codemap.metrics.finder import find_duplicates, find_orphans, run_finder


class TestDuplicates:
    def test_duplicatas_detectadas(self):
        entries = [
            {"type": "file", "name": "Utils.pas", "path": "src/A/Utils.pas"},
            {"type": "file", "name": "Utils.pas", "path": "src/B/Utils.pas"},
        ]
        groups = find_duplicates(entries)
        assert len(groups) == 1
        assert groups[0].name == "Utils.pas"
        assert groups[0].count == 2

    def test_sem_duplicatas(self):
        entries = [
            {"type": "file", "name": "A.pas", "path": "src/A.pas"},
            {"type": "file", "name": "B.pas", "path": "src/B.pas"},
        ]
        groups = find_duplicates(entries)
        assert len(groups) == 0

    def test_mesmo_diretorio_nao_eh_duplicata(self):
        entries = [
            {"type": "file", "name": "A.pas", "path": "src/A.pas"},
            {"type": "file", "name": "B.pas", "path": "src/B.pas"},
        ]
        groups = find_duplicates(entries)
        assert len(groups) == 0

    def test_min_group_size(self):
        entries = [
            {"type": "file", "name": "X.pas", "path": "a/X.pas"},
            {"type": "file", "name": "X.pas", "path": "b/X.pas"},
        ]
        groups = find_duplicates(entries, min_group_size=3)
        assert len(groups) == 0

    def test_dirs_ignorados(self):
        entries = [
            {"type": "dir", "name": "src", "path": "src"},
            {"type": "file", "name": "A.pas", "path": "src/A.pas"},
        ]
        groups = find_duplicates(entries)
        assert len(groups) == 0


class TestOrphans:
    def test_orfao_detectado(self):
        entries = [
            {"type": "file", "name": "Unit1.pas", "path": "src/Unit1.pas"},
        ]
        orphan_set, dup_groups = find_orphans(entries)
        assert "src/Unit1.pas" in orphan_set

    def test_run_finder_resultado(self):
        entries = [
            {"type": "file", "name": "Utils.pas", "path": "a/Utils.pas"},
            {"type": "file", "name": "Utils.pas", "path": "b/Utils.pas"},
            {"type": "file", "name": "Solo.pas", "path": "c/Solo.pas"},
        ]
        result = run_finder(entries)
        assert len(result.duplicates) == 1
        assert result.duplicates[0].name == "Utils.pas"
        assert "c/Solo.pas" in result.orphan_set
        assert "a/Utils.pas" in result.duplicate_map
