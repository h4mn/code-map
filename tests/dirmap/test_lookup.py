"""Testes do lookup de símbolos — tipos, constantes, enums."""

import json
import pytest
from pathlib import Path

from codemap.dirmap.lookup import lookup


def _make_repo(tmp_path: Path) -> dict:
    """Cria estrutura de arquivos Delphi/Python e retorna dirmap data."""
    src = tmp_path / "src" / "Model"
    src.mkdir(parents=True)

    (src / "Tipos.pas").write_text(
        "unit Tipos;\n"
        "interface\n"
        "type\n"
        "  TRelatorioModelo = class\n"
        "    FId: Integer;\n"
        "  end;\n"
        "  TRelatorioDinamicoModelo = (rdmSimples, rdmCompleto);\n"
        "  TRDinTp_Etiqueta = (rdtNormal, rdtEspecial);\n"
        "const\n"
        "  MAX_RETRIES = 3;\n"
        "  APP_NAME = 'CodeMap';\n"
        "implementation\n"
        "end.\n",
        encoding="utf-8",
    )

    (src / "Consts.pas").write_text(
        "unit Consts;\n"
        "interface\n"
        "const\n"
        "  VERSION = '1.0';\n"
        "  MAX_ITEMS = 100;\n"
        "implementation\n"
        "end.\n",
        encoding="utf-8",
    )

    (tmp_path / "src" / "main.py").write_text(
        "class MyClass:\n"
        "    pass\n"
        "MAX_RETRIES = 5\n"
        "APP_NAME = 'test'\n",
        encoding="utf-8",
    )

    return {
        "meta": {"root_name": "TestRepo", "root_path": str(tmp_path)},
        "summary": {"total_files": 3},
        "tree": [
            {"path": "src/Model/Tipos.pas", "type": "file", "extension": ".pas", "language": "delphi"},
            {"path": "src/Model/Consts.pas", "type": "file", "extension": ".pas", "language": "delphi"},
            {"path": "src/main.py", "type": "file", "extension": ".py", "language": "python"},
        ],
    }


class TestLookupSymbol:
    def test_encontra_type_declaration(self, tmp_path):
        data = _make_repo(tmp_path)
        result = lookup(data, "TRelatorioModelo")
        assert len(result) > 0
        assert result[0]["symbol"] == "TRelatorioModelo"
        assert result[0]["kind"] == "type"

    def test_encontra_const(self, tmp_path):
        data = _make_repo(tmp_path)
        result = lookup(data, "MAX_RETRIES")
        assert len(result) > 0
        assert result[0]["symbol"] == "MAX_RETRIES"
        assert result[0]["kind"] == "const"

    def test_encontra_enum(self, tmp_path):
        data = _make_repo(tmp_path)
        result = lookup(data, "TRDinTp_Etiqueta")
        assert len(result) > 0
        assert result[0]["symbol"] == "TRDinTp_Etiqueta"

    def test_case_insensitive(self, tmp_path):
        data = _make_repo(tmp_path)
        result = lookup(data, "trelatoriomodelo")
        assert len(result) > 0

    def test_substring_match(self, tmp_path):
        data = _make_repo(tmp_path)
        result = lookup(data, "Relatorio")
        assert len(result) >= 1

    def test_sem_resultado(self, tmp_path):
        data = _make_repo(tmp_path)
        result = lookup(data, "SimboloInexistente")
        assert result == []

    def test_resultado_tem_caminho_e_linha(self, tmp_path):
        data = _make_repo(tmp_path)
        result = lookup(data, "TRelatorioModelo")
        assert all("path" in r for r in result)
        assert all("line" in r for r in result)

    def test_filtro_por_linguagem(self, tmp_path):
        data = _make_repo(tmp_path)
        result = lookup(data, "class", lang="python")
        assert len(result) > 0
        assert all(r["path"].endswith(".py") for r in result)

    def test_fallback_substring_texto(self, tmp_path):
        """Se regex não acha, fallback pra substring no conteúdo."""
        data = _make_repo(tmp_path)
        result = lookup(data, "implementation")
        assert len(result) > 0
        assert all(r["kind"] == "text" for r in result)
