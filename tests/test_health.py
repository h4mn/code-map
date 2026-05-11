"""Testes do validador de dependências."""

import sys
import pytest
from unittest.mock import patch

from codemap.health import check_dependencies, REQUIRED


class TestCheckDependencies:
    def test_todas_presentes_nao_faz_nada(self):
        # pyyaml deve estar instalado no ambiente de dev
        check_dependencies()  # não deve levantar

    def test_dep_faltando_mostra_mensagem_e_sai(self):
        with patch.dict(REQUIRED, {"pacote-inexistente": ("modulo_fake", "Instale: pip install fake")}):
            with patch("builtins.__import__", side_effect=ImportError):
                with pytest.raises(SystemExit) as exc_info:
                    check_dependencies()
                assert exc_info.value.code == 1
