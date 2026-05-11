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
) -> list[dict] | int | dict:
    """Filtra as entries do dirmap. Retorna lista de entries, int (count) ou dict (summary)."""
    if summary:
        return data.get("summary", {})

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

    if count:
        return len(filtered)

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
            print("  help               Mostra esta ajuda")
            print("  exit               Sai do REPL")
            continue

        if line == "summary":
            result = query(data, summary=True)
        elif line == "count":
            result = f"{data.get('summary', {}).get('total_files', 0)} arquivos no total"
        else:
            parts = line.split()
            kwargs = {}
            i = 0
            while i < len(parts):
                key = parts[i].lower()
                if key in ("ext", "lang", "path", "type") and i + 1 < len(parts):
                    kwargs[key] = parts[i + 1]
                    i += 2
                elif key == "count":
                    kwargs["count"] = True
                    i += 1
                elif key == "summary":
                    kwargs["summary"] = True
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
                        print(f"  {entry['path']}  ({entry.get('extension', '?')} / {entry.get('language', '?')} / {size} bytes)")
        else:
            print(result)
