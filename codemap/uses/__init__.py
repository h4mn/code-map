"""Subcomandos do uses — registrados no CommandRegistry."""

from codemap.registry import CommandRegistry


@CommandRegistry.register("uses", "Extrai dependências de imports/uses de um dirmap", "análise")
def cmd_uses(filepath: str, output: str = None, stdout: bool = False, **kwargs):
    """Extrai dependências (uses/imports) de um dirmap gerado."""
    from codemap.uses.enricher import run_uses
    run_uses(filepath, output=output, stdout=stdout)
