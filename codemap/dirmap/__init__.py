"""Subcomandos do dirmap — registrados no CommandRegistry."""

from codemap.registry import CommandRegistry
from codemap.dirmap.serializer import run_dirmap
from codemap.dirmap.query import run_query_cmd, run_repl_cmd


@CommandRegistry.register("dirmap", "Indexa estrutura física de um codebase", "escaneamento")
def cmd_dirmap(root: str, output: str = "dirmap.json", stdout: bool = False, follow_symlinks: bool = False, **kwargs):
    """Indexa a estrutura física de um codebase e gera JSON."""
    run_dirmap(root, output=output, stdout=stdout, follow_symlinks=follow_symlinks, **kwargs)


@CommandRegistry.register("query", "Consulta dados de um dirmap gerado", "consulta")
def cmd_query(filepath: str, ext: str = None, lang: str = None, path: str = None, type: str = None, count: bool = False, summary: bool = False):
    """Consulta dados de um dirmap gerado."""
    run_query_cmd(filepath, ext=ext, lang=lang, path=path, type=type, count=count, summary=summary)


@CommandRegistry.register("repl", "REPL interativo para consultas", "consulta")
def cmd_repl(filepath: str):
    """REPL interativo para consultas."""
    run_repl_cmd(filepath)


@CommandRegistry.register("version", "Mostra versão atual", "geral")
def cmd_version():
    """Mostra a versão atual do CodeMap."""
    from codemap import __version__
    print(f"codemap v{__version__}")
