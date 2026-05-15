"""Testes do parser Delphi — extração de uses."""

import pytest
from pathlib import Path

from codemap.uses.delphi import parse_delphi_uses, ImportRef


class TestUsesInterface:
    def test_uses_interface_simples(self, tmp_path):
        src = tmp_path / "UnitA.pas"
        src.write_text(
            "unit UnitA;\n\ninterface\n\nuses\n  UnitB, UnitC;\n\nimplementation\n\nend.\n",
            encoding="utf-8",
        )
        refs = parse_delphi_uses(src)
        assert len(refs) == 2
        names = {r.name for r in refs if r.section == "interface"}
        assert "UnitB" in names
        assert "UnitC" in names

    def test_uses_interface_ponto_virgula_inline(self, tmp_path):
        src = tmp_path / "UnitA.pas"
        src.write_text(
            "unit UnitA;\n\ninterface\n\nuses UnitB;\n\nimplementation\n\nend.\n",
            encoding="utf-8",
        )
        refs = parse_delphi_uses(src)
        assert len(refs) == 1
        assert refs[0].name == "UnitB"
        assert refs[0].section == "interface"


class TestUsesImplementation:
    def test_uses_implementation(self, tmp_path):
        src = tmp_path / "UnitA.pas"
        src.write_text(
            "unit UnitA;\n\ninterface\n\nimplementation\n\nuses UnitD;\n\nend.\n",
            encoding="utf-8",
        )
        refs = parse_delphi_uses(src)
        assert len(refs) == 1
        assert refs[0].name == "UnitD"
        assert refs[0].section == "implementation"

    def test_uses_interface_e_implementation(self, tmp_path):
        src = tmp_path / "UnitA.pas"
        src.write_text(
            "unit UnitA;\n\ninterface\n\nuses UnitB;\n\nimplementation\n\nuses UnitD;\n\nend.\n",
            encoding="utf-8",
        )
        refs = parse_delphi_uses(src)
        assert len(refs) == 2
        sections = {r.section for r in refs}
        assert sections == {"interface", "implementation"}


class TestUsesMultiLinha:
    def test_uses_multi_linha(self, tmp_path):
        src = tmp_path / "UnitA.pas"
        src.write_text(
            "unit UnitA;\n\ninterface\n\nuses\n  UnitB,\n  UnitC,\n  UnitD;\n\nimplementation\n\nend.\n",
            encoding="utf-8",
        )
        refs = parse_delphi_uses(src)
        names = {r.name for r in refs}
        assert names == {"UnitB", "UnitC", "UnitD"}

    def test_uses_multi_linha_com_espacos(self, tmp_path):
        src = tmp_path / "UnitA.pas"
        src.write_text(
            "unit UnitA;\n\ninterface\n\n  uses UnitA, UnitB, UnitC ;\n\nimplementation\n\nend.\n",
            encoding="utf-8",
        )
        refs = parse_delphi_uses(src)
        assert len(refs) == 3


class TestUsesDpr:
    def test_dpr_uses_com_in(self, tmp_path):
        src = tmp_path / "Project1.dpr"
        src.write_text(
            "program Project1;\n\nuses\n  UnitA in 'Model\\UnitA.pas',\n  UnitB,\n  Vcl.Forms;\n\nbegin\nend.\n",
            encoding="utf-8",
        )
        refs = parse_delphi_uses(src)
        names = {r.name for r in refs}
        assert "UnitA" in names
        assert "UnitB" in names
        assert "Vcl.Forms" in names
        # "in 'path'" deve ser ignorado — nome deve ser limpo
        for r in refs:
            assert "in " not in r.name
            assert "'" not in r.name

    def test_dpr_section_program(self, tmp_path):
        src = tmp_path / "Project1.dpr"
        src.write_text(
            "program Project1;\n\nuses UnitA;\n\nbegin\nend.\n",
            encoding="utf-8",
        )
        refs = parse_delphi_uses(src)
        assert refs[0].section == "program"


class TestEdgeCases:
    def test_sem_uses(self, tmp_path):
        src = tmp_path / "UnitA.pas"
        src.write_text(
            "unit UnitA;\n\ninterface\n\nimplementation\n\nend.\n",
            encoding="utf-8",
        )
        refs = parse_delphi_uses(src)
        assert refs == []

    def test_arquivo_vazio(self, tmp_path):
        src = tmp_path / "Empty.pas"
        src.write_text("", encoding="utf-8")
        refs = parse_delphi_uses(src)
        assert refs == []

    def test_arquivo_inexistente(self):
        refs = parse_delphi_uses(Path("/nao/existe.pas"))
        assert refs == []

    def test_uses_com_comentario_linha(self, tmp_path):
        src = tmp_path / "UnitA.pas"
        src.write_text(
            "unit UnitA;\n\ninterface\n\nuses\n  UnitB, // comentario\n  UnitC;\n\nimplementation\n\nend.\n",
            encoding="utf-8",
        )
        refs = parse_delphi_uses(src)
        names = {r.name for r in refs}
        assert names == {"UnitB", "UnitC"}

    def test_uses_comentario_bloco_na_lista(self, tmp_path):
        src = tmp_path / "UnitA.pas"
        src.write_text(
            "unit UnitA;\n\ninterface\n\nuses\n  UnitB {ignore}, UnitC;\n\nimplementation\n\nend.\n",
            encoding="utf-8",
        )
        refs = parse_delphi_uses(src)
        names = {r.name for r in refs}
        assert "UnitB" in names
        assert "UnitC" in names
