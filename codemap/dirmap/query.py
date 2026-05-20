"""Motor de consultas — filtros estruturais stateless."""

from __future__ import annotations

import fnmatch
import json
import sys
from pathlib import Path, PurePosixPath


def _match_edges(edges: list[dict], value: str, direction: str) -> set[str]:
    """Match edges com normalização + fallback para substring/basename."""
    key = direction  # "from" ou "to"
    other = "from" if key == "to" else "to"

    # 1. Match exato
    matched = {e[other] for e in edges if e[key] == value}
    if matched:
        return matched

    # 2. Substring (value contido no path da edge)
    matched = {e[other] for e in edges if value in e[key]}
    if matched:
        return matched

    # 3. Basename (stem sem extensão)
    value_stem = PurePosixPath(value).stem.lower()
    matched = {e[other] for e in edges if PurePosixPath(e[key]).stem.lower() == value_stem}
    return matched


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
    case_sensitive: bool = False,
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
        if case_sensitive:
            filtered = [e for e in filtered if e.get("extension") == ext]
        else:
            ext_lower = ext.lower()
            filtered = [e for e in filtered if (e.get("extension") or "").lower() == ext_lower]
    if lang is not None:
        if case_sensitive:
            filtered = [e for e in filtered if e.get("language") == lang]
        else:
            lang_lower = lang.lower()
            filtered = [e for e in filtered if (e.get("language") or "").lower() == lang_lower]
    if path is not None:
        path_norm = path.replace("\\", "/")
        if case_sensitive:
            if any(c in path_norm for c in ("*", "?", "[")):
                filtered = [e for e in filtered if fnmatch.fnmatch(e.get("path", ""), path_norm)]
            else:
                filtered = [e for e in filtered if path_norm in e.get("path", "")]
        else:
            if any(c in path_norm for c in ("*", "?", "[")):
                filtered = [
                    e for e in filtered
                    if fnmatch.fnmatch(e.get("path", "").lower(), path_norm.lower())
                ]
            else:
                filtered = [
                    e for e in filtered
                    if path_norm.lower() in e.get("path", "").lower()
                ]
    if type is not None:
        filtered = [e for e in filtered if e.get("type") == type]

    # Filtro por LOC mínimo
    if min_loc is not None:
        filtered = [
            e for e in filtered
            if (e.get("metrics") or {}).get("loc_code", 0) >= min_loc
        ]

    # Dependency filters — com normalização e matching flexível
    if depends_on is not None:
        graph = data.get("dependency_graph", {})
        edges = graph.get("edges", [])
        target = depends_on.replace("\\", "/")
        source_paths = _match_edges(edges, target, direction="to")
        filtered = [e for e in filtered if e.get("path") in source_paths]

    if depended_by is not None:
        graph = data.get("dependency_graph", {})
        edges = graph.get("edges", [])
        source = depended_by.replace("\\", "/")
        target_paths = _match_edges(edges, source, direction="from")
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
    if not filepath:
        raise FileNotFoundError("Nenhum dirmap especificado. Passe o arquivo ou configure default_dirmap em .codemap.yml")
    data = load_dirmap_json(filepath)
    # Remove stdout do query (não é filtro)
    filters.pop("stdout", None)
    result = query(data, **filters)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def run_repl_cmd(filepath: str):
    """Ponto de entrada do REPL."""
    if not filepath:
        raise FileNotFoundError("Nenhum dirmap especificado. Passe o arquivo ou configure default_dirmap em .codemap.yml")
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
            print("  path <termo>       Busca substring/glob no caminho (ex: path Model, path *.pas)")
            print("  type <file|dir>    Filtra por tipo")
            print("  case-sensitive     Ativa busca case-sensitive")
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
                elif key == "case-sensitive":
                    kwargs["case_sensitive"] = True
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
