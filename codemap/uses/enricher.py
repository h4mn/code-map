"""Enricher — enriquece dirmap.json com dados de imports/uses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from codemap.config import DirmapConfig

# Supported languages for import parsing
_SUPPORTED_LANGUAGES = {"delphi", "python", "javascript", "typescript", "js", "ts"}


def enrich_dirmap_with_uses(
    data: dict,
    root: str,
    config: DirmapConfig | None = None,
) -> dict:
    """Enriquece dirmap data com import/uses information.

    Para cada arquivo com linguagem suportada:
      - Parseia imports (parse_imports)
      - Resolve contra o tree (resolve_imports)
      - Adiciona campo "imports" na entry

    No nível raiz, adiciona "dependency_graph" com grafo completo.
    """
    if config is None:
        config = DirmapConfig()

    tree = data.get("tree", [])
    root_path = str(root or data.get("meta", {}).get("root", "."))

    # Coletar paths do tree para resolução
    tree_entries = [e for e in tree if e.get("type") == "file"]

    # Mapa: path da entry -> entry (para lookup rápido)
    all_imports: dict[str, list[dict]] = {}  # path -> resolved imports

    enriched_tree = []
    for entry in tree:
        new_entry = dict(entry)

        if entry.get("type") == "file":
            language = entry.get("language", "").lower()
            if language in _SUPPORTED_LANGUAGES:
                rel_path = entry.get("path", "")
                abs_path = Path(root_path) / rel_path

                from codemap.uses.parser import parse_imports
                from codemap.uses.resolver import resolve_imports

                raw_imports = parse_imports(abs_path, language)
                resolved = resolve_imports(raw_imports, rel_path, tree_entries, config)

                new_entry["imports"] = resolved
                all_imports[rel_path] = resolved

        enriched_tree.append(new_entry)

    # Construir grafo de dependências
    from codemap.uses.graph import build_graph
    graph = build_graph(all_imports)

    # Montar resultado
    result = dict(data)
    result["tree"] = enriched_tree
    result["dependency_graph"] = graph

    return result


def run_uses(
    filepath: str,
    output: str | None = None,
    stdout: bool = False,
    config: DirmapConfig | None = None,
):
    """Ponto de entrada do comando uses."""
    if config is None:
        config = DirmapConfig()

    src = Path(filepath)
    if not src.exists():
        print(f"Arquivo não encontrado: {filepath}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(src.read_text(encoding="utf-8"))
    root = data.get("meta", {}).get("root")
    enriched = enrich_dirmap_with_uses(data, root, config)
    json_str = json.dumps(enriched, indent=config.indent, ensure_ascii=False)

    if stdout:
        print(json_str)
    elif output:
        Path(output).write_text(json_str, encoding="utf-8")
    else:
        src.write_text(json_str, encoding="utf-8")
