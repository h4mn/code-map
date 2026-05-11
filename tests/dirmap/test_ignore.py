"""Testes do parser de ignore."""

import pytest
from pathlib import Path

from codemap.dirmap.ignore import parse_ignore_file, load_ignore_patterns, is_ignored


class TestParseIgnoreFile:
    def test_arquivo_nao_existe(self, tmp_path):
        result = parse_ignore_file(tmp_path / "nao_existe")
        assert result == []

    def test_arquivo_com_padroes(self, tmp_path):
        f = tmp_path / ".gitignore"
        f.write_text("bin/\n*.tmp\n\n# comentario\nnode_modules/\n", encoding="utf-8")
        result = parse_ignore_file(f)
        assert result == ["bin/", "*.tmp", "node_modules/"]

    def test_linhas_malformadas_ignoradas(self, tmp_path):
        f = tmp_path / ".gitignore"
        f.write_text("valid/\n\n\n!!invalid\n", encoding="utf-8")
        result = parse_ignore_file(f)
        assert "valid/" in result


class TestLoadIgnorePatterns:
    def test_carrega_gitignore_e_extra_dirs(self, tmp_path):
        (tmp_path / ".gitignore").write_text("bin/\n", encoding="utf-8")
        patterns = load_ignore_patterns(tmp_path, [".gitignore"], ["node_modules"])
        assert "bin/" in patterns
        assert "node_modules" in patterns

    def test_codemap_ignore_prioridade(self, tmp_path):
        (tmp_path / ".gitignore").write_text("debug/\n", encoding="utf-8")
        (tmp_path / ".codemap-ignore").write_text("logs/\n", encoding="utf-8")
        patterns = load_ignore_patterns(tmp_path, [".gitignore", ".codemap-ignore"], [])
        assert "debug/" in patterns
        assert "logs/" in patterns


class TestIsIgnored:
    def test_arquivo_ignorado_por_wildcard(self):
        assert is_ignored("file.tmp", ["*.tmp"])

    def test_diretorio_ignorado(self):
        assert is_ignored("bin/app.exe", ["bin/"])
        assert not is_ignored("bin2/app.exe", ["bin/"])

    def test_arquivo_nao_ignorado(self):
        assert not is_ignored("src/main.pas", ["*.tmp"])

    def test_negacao_ignorada(self):
        assert not is_ignored("important.log", ["!important.log"])

    def test_comentario_ignorado(self):
        assert not is_ignored("anything", ["# comment"])
