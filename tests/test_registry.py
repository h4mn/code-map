"""Testes do CommandRegistry."""

import pytest

from codemap.registry import CommandRegistry


@pytest.fixture(autouse=True)
def clear_registry():
    CommandRegistry.clear()
    yield
    CommandRegistry.clear()


def _dummy():
    """Comando dummy."""
    pass


def _dummy2(x: int = 10):
    """Comando dummy2."""
    pass


class TestRegister:
    def test_registra_comando(self):
        CommandRegistry.register("dummy", "Comando de teste")(_dummy)
        cmd = CommandRegistry.get("dummy")
        assert cmd is not None
        assert cmd.name == "dummy"
        assert cmd.description == "Comando de teste"
        assert cmd.category == "geral"

    def test_registra_com_categoria(self):
        CommandRegistry.register("dummy", "Teste", category="escaneamento")(_dummy)
        assert CommandRegistry.get("dummy").category == "escaneamento"

    def test_comando_duplicado_levanta_erro(self):
        CommandRegistry.register("dummy", "Primeiro")(_dummy)
        with pytest.raises(ValueError, match="já registrado"):
            CommandRegistry.register("dummy", "Segundo")(_dummy)

    def test_all_retorna_copia(self):
        CommandRegistry.register("a", "A")(_dummy)
        CommandRegistry.register("b", "B")(_dummy2)
        cmds = CommandRegistry.all()
        assert set(cmds.keys()) == {"a", "b"}
        cmds["c"] = None  # não afeta o original
        assert "c" not in CommandRegistry.all()


class TestHelpText:
    def test_help_conteudo(self):
        CommandRegistry.register("dirmap", "Indexa estrutura física", "escaneamento")(_dummy)
        CommandRegistry.register("query", "Consulta dados", "consulta")(_dummy2)
        text = CommandRegistry.help_text()
        assert "CodeMap" in text
        assert "escaneamento:" in text
        assert "dirmap" in text
        assert "consulta:" in text
        assert "query" in text

    def test_help_vazio(self):
        text = CommandRegistry.help_text()
        assert "CodeMap" in text

    def test_help_agrupa_por_categoria(self):
        CommandRegistry.register("dirmap", "Indexa estrutura física", "escaneamento")(_dummy)
        CommandRegistry.register("query", "Consulta dados", "consulta")(_dummy2)
        CommandRegistry.register("repl", "REPL interativo", "consulta")(_dummy)
        text = CommandRegistry.help_text()
        # 'dirmap' aparece depois de 'escaneamento'
        esc_pos = text.index("escaneamento")
        assert text.index("dirmap", esc_pos) > esc_pos
        # 'query' e 'repl' aparecem depois de 'consulta'
        cons_pos = text.index("consulta")
        assert text.index("query", cons_pos) > cons_pos
        assert text.index("repl", cons_pos) > cons_pos
