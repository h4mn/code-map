"""Testes do classifier."""

import pytest

from codemap.dirmap.classifier import classify, DEFAULT_MAP


class TestClassify:
    def test_extensao_conhecida(self):
        assert classify(".pas") == "delphi"
        assert classify(".py") == "python"
        assert classify(".ts") == "typescript"
        assert classify(".md") == "markdown"

    def test_extensao_desconhecida(self):
        assert classify(".xyz") == "unknown"
        assert classify(".foo") == "unknown"

    def test_extensao_vazia(self):
        assert classify("") == "unknown"
        assert classify("   ") == "unknown"

    def test_case_insensitive(self):
        assert classify(".PAS") == "delphi"
        assert classify(".Py") == "python"


class TestCustomExtensions:
    def test_custom_sobrepoe_default(self):
        custom = {".dpr": "delphi-entry"}
        assert classify(".dpr", custom) == "delphi-entry"

    def test_custom_sem_ponto(self):
        custom = {"dpr": "delphi-entry"}
        assert classify(".dpr", custom) == "delphi-entry"

    def test_custom_nao_afeta_outras(self):
        custom = {".dpr": "delphi-entry"}
        assert classify(".pas", custom) == "delphi"

    def test_sem_custom_usa_default(self):
        assert classify(".pas", None) == "delphi"
        assert classify(".pas", {}) == "delphi"


class TestNormalization:
    def test_adiciona_ponto(self):
        assert classify("pas") == "delphi"

    def test_espacos_ignorados(self):
        assert classify("  .pas  ") == "delphi"
