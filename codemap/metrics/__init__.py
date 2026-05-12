"""Subcomandos do metrics — registrados no CommandRegistry."""

from codemap.registry import CommandRegistry
from codemap.metrics.enricher import run_enrich


@CommandRegistry.register("metrics", "Gera métricas sobre um dirmap existente", "análise")
def cmd_metrics(filepath: str, output: str = None, stdout: bool = False, **kwargs):
    """Gera métricas (LOC, duplicatas, órfãos) sobre um dirmap.json existente."""
    run_enrich(filepath, output=output, stdout=stdout)
