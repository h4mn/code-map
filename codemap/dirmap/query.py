"""Motor de consultas — filtros estruturais stateless."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def query(
    data: dict,
    ext: str | None = None,
    lang: str | None = None,
    path: str | None = None,
    type: str | None = None,
    count: bool = False,
    summary: bool = False,
    metrics: bool = False,
    top: int | None = None,
    by: str | None = None,
    min_loc: int | None = None,
    depends_on: str | None = None,
    depended_by: str | None = None,
    cycles: bool = False,
) -> list[dict] | int | dict:
    """Filtra as entries do dirmap. Retorna lista de entries, int (count) ou dict (summary)."""
    if summary:
        return data.get("summary", {})

    # Cycles — retorna lista de ciclos do dependency_graph
    if cycles:
        graph = data.get("dependency_graph", {})
        return graph.get("cycles", [])

    entries = data.get("tree", [])
    filtered = entries

    if ext is not None:
        filtered = [e for e in filtered if e.get("extension") == ext]
    if lang is not None:
        filtered = [e for e in filtered if e.get("language") == lang]
    if path is not None:
        path_norm = path.replace("\\", "/")
        filtered = [e for e in filtered if e.get("path", "").startswith(path_norm)]
    if type is not None:
        filtered = [e for e in filtered if e.get("type") == type]

    # Filtro por LOC mínimo
    if min_loc is not None:
        filtered = [
            e for e in filtered
            if (e.get("metrics") or {}).get("loc_code", 0) >= min_loc
        ]

    # Dependency filters
    if depends_on is not None:
        graph = data.get("dependency_graph", {})
        edges = graph.get("edges", [])
        # Encontra quem importa o path dado (edges onde to == depends_on)
        source_paths = {e["from"] for e in edges if e["to"] == depends_on}
        filtered = [e for e in filtered if e.get("path") in source_paths]

    if depended_by is not None:
        graph = data.get("dependency_graph", {})
        edges = graph.get("edges", [])
        # Encontra o que o path dado importa (edges onde from == depended_by)
        target_paths = {e["to"] for e in edges if e["from"] == depended_by}
        filtered = [e for e in filtered if e.get("path") in target_paths]

    # Ordenação por métrica
    if by is not None:
        valid_fields = {"loc_total", "loc_code", "loc_comment", "loc_blank", "size_bytes"}
        if by not in valid_fields:
            raise ValueError(f"Campo inválido: '{by}'. Campos disponíveis: {', '.join(sorted(valid_fields))}")
        filtered.sort(
            key=lambda e: (e.get("metrics") or {}).get(by, e.get(by, 0)),
            reverse=True,
        )

    # Top N
    if top is not None:
        filtered = filtered[:top]

    if count:
        return len(filtered)

    # Remove métricas se não solicitado
    if not metrics:
        filtered = [
            {k: v for k, v in e.items() if k != "metrics"}
            for e in filtered
        ]

    return filtered


def load_dirmap_json(filepath: str) -> dict:
    """Carrega um JSON de dirmap do disco."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: '{filepath}'")
    return json.loads(path.read_text(encoding="utf-8"))


def run_query_cmd(filepath: str, **filters):
    """Ponto de entrada do subcomando query."""
    data = load_dirmap_json(filepath)
    # Remove stdout do query (não é filtro)
    filters.pop("stdout", None)
    result = query(data, **filters)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def run_repl_cmd(filepath: str):
    """Ponto de entrada do REPL."""
    data = load_dirmap_json(filepath)
    root_name = data.get("meta", {}).get("root_name", filepath)
    total = data.get("summary", {}).get("total_files", "?")

    print(f"\nCodeMap REPL — {root_name} ({total} arquivos)")
    print("Exemplos: ext .pas | lang delphi | path src/ | type dir | count | summary")
    print("Digite 'help' para detalhes, 'exit' ou Ctrl+C para sair\n")

    while True:
        try:
            line = input("codemap> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line or line.lower() == "exit":
            break

        if line.lower() == "help":
            print("  ext <extensão>     Filtra por extensão (ex: ext .pas)")
            print("  lang <linguagem>   Filtra por linguagem (ex: lang delphi)")
            print("  path <prefixo>     Filtra por caminho (ex: path src/Model)")
            print("  type <file|dir>    Filtra por tipo")
            print("  count              Conta resultados do último filtro")
            print("  summary            Mostra resumo do codebase")
            print("  metrics            Inclui métricas na saída")
            print("  top <N> by <campo> Top N resultados por métrica (ex: top 5 by loc_code)")
            print("  min-loc <N>        Filtra arquivos com LOC mínimo")
            print("  depends-on <path>  Quem importa o arquivo dado")
            print("  depended-by <path> O que o arquivo dado importa")
            print("  cycles             Lista ciclos de dependência")
            print("  help               Mostra esta ajuda")
            print("  exit               Sai do REPL")
            continue

        if line == "summary":
            result = query(data, summary=True)
        elif line == "count":
            result = f"{data.get('summary', {}).get('total_files', 0)} arquivos no total"
        elif line == "cycles":
            result = query(data, cycles=True)
            if not result:
                print("Nenhum ciclo encontrado.")
            else:
                print(f"{len(result)} ciclo(s) encontrado(s):")
                for cycle in result:
                    print(f"  {' -> '.join(cycle)}")
            continue
        else:
            parts = line.split()
            kwargs = {}
            i = 0
            while i < len(parts):
                key = parts[i].lower()
                if key in ("ext", "lang", "path", "type", "by") and i + 1 < len(parts):
                    kwargs[key] = parts[i + 1]
                    i += 2
                elif key in ("top", "min-loc") and i + 1 < len(parts):
                    kwargs[key.replace("-", "_")] = int(parts[i + 1])
                    i += 2
                elif key in ("depends-on", "depended-by") and i + 1 < len(parts):
                    kwargs[key.replace("-", "_")] = parts[i + 1]
                    i += 2
                elif key == "count":
                    kwargs["count"] = True
                    i += 1
                elif key == "summary":
                    kwargs["summary"] = True
                    i += 1
                elif key == "metrics":
                    kwargs["metrics"] = True
                    i += 1
                elif key == "cycles":
                    kwargs["cycles"] = True
                    i += 1
                else:
                    i += 1

            if not kwargs:
                print("Comando não reconhecido. Digite 'help' para ver os filtros.")
                continue

            result = query(data, **kwargs)

        if isinstance(result, int):
            print(f"{result} resultado(s)")
        elif isinstance(result, dict):
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif isinstance(result, list):
            if not result:
                print("Nenhum resultado.")
            else:
                for entry in result:
                    if entry.get("type") == "dir":
                        print(f"  [DIR]  {entry['path']}")
                    else:
                        size = entry.get("size_bytes", 0)
                        m = entry.get("metrics")
                        base = f"  {entry['path']}  ({entry.get('extension', '?')} / {entry.get('language', '?')} / {size} bytes)"
                        if m:
                            base += f"  [LOC: {m.get('loc_code', '?')}/{m.get('loc_total', '?')}]"
                            if entry.get("duplicate_candidate"):
                                base += f"  dup={entry['duplicate_group']}"
                            if entry.get("orphan_candidate"):
                                base += "  ORFÃO"
                        imports = entry.get("imports")
                        if imports:
                            resolved = [imp.get("resolved_path") or imp.get("name", "?") for imp in imports]
                            base += f"  imports=[{', '.join(resolved)}]"
                        print(base)
        else:
            print(result)
