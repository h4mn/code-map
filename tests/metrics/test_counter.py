"""Testes do MetricsCounter — LOC por linguagem."""

import pytest
from pathlib import Path

from codemap.metrics.counter import count_loc, LocResult


@pytest.fixture
def tmp_file(tmp_path):
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p
    return _write


class TestDelphi:
    def test_comentario_linha(self, tmp_file):
        f = tmp_file("test.pas", "// comentario\ncodigo;\n")
        r = count_loc(f)
        assert r == LocResult(loc_total=2, loc_code=1, loc_comment=1, loc_blank=0)

    def test_comentario_chaves(self, tmp_file):
        f = tmp_file("test.pas", "{ comentario }\ncodigo;\n")
        r = count_loc(f)
        assert r == LocResult(loc_total=2, loc_code=1, loc_comment=1, loc_blank=0)

    def test_comentario_parentese_asterisco(self, tmp_file):
        f = tmp_file("test.pas", "(* comentario *)\ncodigo;\n")
        r = count_loc(f)
        assert r == LocResult(loc_total=2, loc_code=1, loc_comment=1, loc_blank=0)

    def test_misto_com_blank(self, tmp_file):
        content = "unit Test;\n\n// header\n\nimplementation\n\nend.\n"
        f = tmp_file("test.pas", content)
        r = count_loc(f)
        assert r.loc_total == 7  # splitlines descarta trailing newline
        assert r.loc_blank == 3
        assert r.loc_comment == 1
        assert r.loc_code == 3


class TestPython:
    def test_comentario_hash(self, tmp_file):
        f = tmp_file("test.py", "# comentario\ncodigo = 1\n")
        r = count_loc(f)
        assert r == LocResult(loc_total=2, loc_code=1, loc_comment=1, loc_blank=0)

    def test_docstring(self, tmp_file):
        content = '"""docstring"""\ncodigo = 1\n'
        f = tmp_file("test.py", content)
        r = count_loc(f)
        assert r.loc_comment == 1
        assert r.loc_code == 1

    def test_multiline_docstring(self, tmp_file):
        content = '"""\nlinha1\nlinha2\n"""\ncodigo = 1\n'
        f = tmp_file("test.py", content)
        r = count_loc(f)
        # Opening """ is comment, inner lines are code until closing """
        assert r.loc_comment >= 2  # at least opening and closing lines
        assert r.loc_code >= 1


class TestJavaScript:
    def test_comentario_linha(self, tmp_file):
        f = tmp_file("test.js", "// comment\ncode();\n")
        r = count_loc(f)
        assert r == LocResult(loc_total=2, loc_code=1, loc_comment=1, loc_blank=0)

    def test_comentario_bloco(self, tmp_file):
        content = "/* block\ncomment */\ncode();\n"
        f = tmp_file("test.js", content)
        r = count_loc(f)
        assert r.loc_comment == 2
        assert r.loc_code == 1


class TestTypeScript:
    def test_comentario_linha(self, tmp_file):
        f = tmp_file("test.ts", "// comment\nconst x = 1;\n")
        r = count_loc(f)
        assert r.loc_comment == 1
        assert r.loc_code == 1


class TestEdgeCases:
    def test_extensao_desconhecida(self, tmp_file):
        f = tmp_file("test.xyz", "conteudo\n")
        r = count_loc(f)
        assert r is None

    def test_arquivo_binario(self, tmp_path):
        p = tmp_path / "test.exe"
        p.write_bytes(b"\x00\x01\x02")
        r = count_loc(p)
        assert r is None

    def test_arquivo_inexistente(self):
        r = count_loc("/caminho/que/nao/existe.pas")
        assert r is None

    def test_arquivo_vazio(self, tmp_file):
        f = tmp_file("test.pas", "")
        r = count_loc(f)
        assert r == LocResult(loc_total=0, loc_code=0, loc_comment=0, loc_blank=0)

    def test_somente_blanks(self, tmp_file):
        f = tmp_file("test.pas", "\n\n\n")
        r = count_loc(f)
        assert r == LocResult(loc_total=3, loc_code=0, loc_comment=0, loc_blank=3)

    def test_language_explicita(self, tmp_file):
        f = tmp_file("test.custom", "// comentario\ncodigo;\n")
        r = count_loc(f, language="delphi")
        assert r is not None
        assert r.loc_comment == 1
