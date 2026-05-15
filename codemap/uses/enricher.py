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
    supported_files = [e for e in tree if e.get("type") == "file" and e.get("language", "").lower() in _SUPPORTED_LANGUAGES]
    total = len(supported_files)
    processed = 0

    from codemap.uses.parser import parse_imports
    from codemap.uses.resolver import resolve_imports

    supported_set = set(_SUPPORTED_LANGUAGES)

    for entry in tree:
        new_entry = dict(entry)

        if entry.get("type") == "file" and entry.get("language", "").lower() in supported_set:
            rel_path = entry.get("path", "")
            abs_path = Path(root_path) / rel_path

            raw_imports = parse_imports(abs_path, entry.get("language", "").lower())
            resolved = resolve_imports(raw_imports, rel_path, tree_entries, config)

            new_entry["imports"] = resolved
            all_imports[rel_path] = resolved

            processed += 1
            if processed % 50 == 0 or processed == total:
                print(f"\r  uses: {processed}/{total} arquivos processados ({processed * 100 // total}%)", end="", file=sys.stderr)

        enriched_tree.append(new_entry)

    if total > 0:
        print(file=sys.stderr)  # newline after progress

    # Construir grafo de dependências
    print("  uses: construindo grafo de dependências...", file=sys.stderr)
    from codemap.uses.graph import build_graph
    graph = build_graph(all_imports)
    print(f"  uses: grafo pronto — {len(graph.get('nodes', []))} nodos, {len(graph.get('edges', []))} arestas, {len(graph.get('cycles', []))} ciclos", file=sys.stderr)

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
