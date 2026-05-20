"""Subcomandos do dirmap — registrados no CommandRegistry."""

from codemap.registry import CommandRegistry
from codemap.dirmap.serializer import run_dirmap
from codemap.dirmap.query import run_query_cmd, run_repl_cmd
from codemap.dirmap.lookup import run_lookup_cmd


@CommandRegistry.register("dirmap", "Indexa estrutura física de um codebase", "escaneamento")
def cmd_dirmap(root: str, output: str = "dirmap.json", stdout: bool = False, follow_symlinks: bool = False, with_metrics: bool = False, with_uses: bool = False, **kwargs):
    """Indexa a estrutura física de um codebase e gera JSON."""
    run_dirmap(root, output=output, stdout=stdout, follow_symlinks=follow_symlinks, with_metrics=with_metrics, with_uses=with_uses, **kwargs)


@CommandRegistry.register("query", "Consulta dados de um dirmap gerado", "consulta")
def cmd_query(filepath: str = None, ext: str = None, lang: str = None, path: str = None, type: str = None, count: bool = False, summary: bool = False, metrics: bool = False, top: int = None, by: str = None, min_loc: int = None, depends_on: str = None, depended_by: str = None, cycles: bool = False, case_sensitive: bool = False):
    """Consulta dados de um dirmap gerado."""
    run_query_cmd(filepath, ext=ext, lang=lang, path=path, type=type, count=count, summary=summary, metrics=metrics, top=top, by=by, min_loc=min_loc, depends_on=depends_on, depended_by=depended_by, cycles=cycles, case_sensitive=case_sensitive)


@CommandRegistry.register("repl", "REPL interativo para consultas", "consulta")
def cmd_repl(filepath: str = None):
    """REPL interativo para consultas."""
    run_repl_cmd(filepath)


@CommandRegistry.register("lookup", "Busca declarações de tipos/constantes/enums", "análise")
def cmd_lookup(symbol: str, filepath: str = None, lang: str = None):
    """Busca declarações de símbolos (tipos, constantes, enums)."""
    run_lookup_cmd(symbol, filepath, lang=lang)


@CommandRegistry.register("version", "Mostra versão atual", "geral")
def cmd_version():
    """Mostra a versão atual do CodeMap."""
    from codemap import __version__
    print(f"codemap v{__version__}")
