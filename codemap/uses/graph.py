"""Graph — constrói grafo de dependências, detecta ciclos e calcula métricas."""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------


def build_graph(
    resolved_imports: dict[str, list[dict]],  # path → list of resolved imports
) -> dict:
    """Constrói grafo de dependências a partir de imports resolvidos.

    Retorna:
        {
            "nodes": [{"id": str, "fan_in": int, "fan_out": int}, ...],
            "edges": [{"from": str, "to": str}, ...],
            "cycles": [[str, ...], ...],
        }
    """
    if not resolved_imports:
        return {"nodes": [], "edges": [], "cycles": []}

    # Coletar todos os nós (sources + targets resolvidos)
    all_nodes: set[str] = set()
    adjacency: dict[str, set[str]] = {}  # source → set of targets
    edges_set: set[tuple[str, str]] = set()

    for source, imports in resolved_imports.items():
        all_nodes.add(source)
        adjacency.setdefault(source, set())

        for imp in imports:
            target = imp.get("resolved_path")
            if target is None:
                continue  # Skip unresolved imports
            all_nodes.add(target)
            adjacency.setdefault(target, set())
            adjacency[source].add(target)
            edges_set.add((source, target))

    # Garantir que todo nó está no adjacency
    for node in all_nodes:
        adjacency.setdefault(node, set())

    # Construir edges list
    edges = [{"from": src, "to": tgt} for src, tgt in sorted(edges_set)]

    # Calcular fan-in e fan-out
    fan_in: dict[str, int] = {n: 0 for n in all_nodes}
    fan_out: dict[str, int] = {n: 0 for n in all_nodes}

    for src, tgt in edges_set:
        fan_out[src] += 1
        fan_in[tgt] += 1

    nodes = [
        {"id": n, "fan_in": fan_in[n], "fan_out": fan_out[n]}
        for n in sorted(all_nodes)
    ]

    # Detectar ciclos com DFS
    cycles = _detect_cycles(adjacency)

    return {
        "nodes": nodes,
        "edges": edges,
        "cycles": cycles,
    }


# ---------------------------------------------------------------------------
# Cycle detection (DFS)
# ---------------------------------------------------------------------------


def _detect_cycles(adjacency: dict[str, set[str]]) -> list[list[str]]:
    """Detecta ciclos no grafo usando DFS.

    Retorna lista de ciclos, onde cada ciclo é uma lista de node IDs
    representando o caminho do ciclo (ex: ["A", "B", "A"]).
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {n: WHITE for n in adjacency}
    parent: dict[str, str | None] = {n: None for n in adjacency}
    cycles: list[list[str]] = []
    stack: list[str] = []  # Current DFS path

    def _dfs(node: str) -> None:
        color[node] = GRAY
        stack.append(node)

        for neighbor in sorted(adjacency.get(node, set())):
            if color.get(neighbor) == GRAY:
                # Found a cycle — extract it from stack
                cycle_start = stack.index(neighbor)
                cycle = stack[cycle_start:] + [neighbor]
                cycles.append(cycle)
            elif color.get(neighbor, WHITE) == WHITE:
                parent[neighbor] = node
                _dfs(neighbor)

        stack.pop()
        color[node] = BLACK

    for node in sorted(adjacency.keys()):
        if color[node] == WHITE:
            _dfs(node)

    return cycles


# ---------------------------------------------------------------------------
# Hotspots
# ---------------------------------------------------------------------------


def find_hotspots(graph: dict, top: int = 3) -> list[dict]:
    """Retorna os top N nós com maior fan_in (mais dependidos).

    Ordenado por fan_in descendente, desempatando por id ascendente.
    """
    nodes = graph.get("nodes", [])
    if not nodes:
        return []

    sorted_nodes = sorted(
        nodes,
        key=lambda n: (-n["fan_in"], n["id"]),
    )
    return sorted_nodes[:top]
