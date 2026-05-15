"""Testes do graph — build_graph() e find_hotspots()."""

import pytest

from codemap.uses.graph import build_graph, find_hotspots


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _imports_map(data: dict[str, list[str]]) -> dict[str, list[dict]]:
    """Converte {path: [resolved_paths]} em formato resolved_imports."""
    result: dict[str, list[dict]] = {}
    for source, targets in data.items():
        result[source] = [
            {"name": t, "resolved_path": t, "unresolved": False, "category": ""}
            for t in targets
        ]
    return result


# ---------------------------------------------------------------------------
# 1. Simple graph
# ---------------------------------------------------------------------------

class TestSimpleGraph:
    def test_a_imports_b_and_c(self):
        data = _imports_map({"A": ["B", "C"]})
        graph = build_graph(data)
        edges = {(e["from"], e["to"]) for e in graph["edges"]}
        assert ("A", "B") in edges
        assert ("A", "C") in edges
        assert len(graph["edges"]) == 2

    def test_nodes_include_all_paths(self):
        data = _imports_map({"A": ["B", "C"]})
        graph = build_graph(data)
        node_ids = {n["id"] for n in graph["nodes"]}
        assert "A" in node_ids
        assert "B" in node_ids
        assert "C" in node_ids


# ---------------------------------------------------------------------------
# 2. Transitive
# ---------------------------------------------------------------------------

class TestTransitive:
    def test_transitive_does_not_create_direct_edge(self):
        data = _imports_map({"A": ["B"], "B": ["C"]})
        graph = build_graph(data)
        edges = {(e["from"], e["to"]) for e in graph["edges"]}
        assert ("A", "B") in edges
        assert ("B", "C") in edges
        # A does NOT directly connect to C
        assert ("A", "C") not in edges


# ---------------------------------------------------------------------------
# 3. Direct cycle
# ---------------------------------------------------------------------------

class TestDirectCycle:
    def test_a_b_cycle(self):
        data = _imports_map({"A": ["B"], "B": ["A"]})
        graph = build_graph(data)
        cycles = graph["cycles"]
        assert len(cycles) >= 1
        # Pelo menos um ciclo contém A e B
        found = any("A" in c and "B" in c for c in cycles)
        assert found

    def test_cycle_format_is_list_of_paths(self):
        data = _imports_map({"A": ["B"], "B": ["A"]})
        graph = build_graph(data)
        assert len(graph["cycles"]) >= 1
        cycle = graph["cycles"][0]
        assert isinstance(cycle, list)
        assert len(cycle) >= 2


# ---------------------------------------------------------------------------
# 4. Transitive cycle
# ---------------------------------------------------------------------------

class TestTransitiveCycle:
    def test_a_b_c_cycle(self):
        data = _imports_map({"A": ["B"], "B": ["C"], "C": ["A"]})
        graph = build_graph(data)
        cycles = graph["cycles"]
        assert len(cycles) >= 1
        # Pelo menos um ciclo contém A, B, C
        found = any(set(c) >= {"A", "B", "C"} for c in cycles)
        assert found


# ---------------------------------------------------------------------------
# 5. No cycles
# ---------------------------------------------------------------------------

class TestNoCycles:
    def test_acyclic_graph(self):
        data = _imports_map({"A": ["B"], "B": ["C"], "D": ["C"]})
        graph = build_graph(data)
        assert graph["cycles"] == []


# ---------------------------------------------------------------------------
# 6. Fan-in / Fan-out
# ---------------------------------------------------------------------------

class TestFanInOut:
    def test_fan_in_fan_out_counts(self):
        # A→C, B→C, C→D
        data = _imports_map({"A": ["C"], "B": ["C"], "C": ["D"]})
        graph = build_graph(data)
        node_map = {n["id"]: n for n in graph["nodes"]}
        assert node_map["C"]["fan_in"] == 2
        assert node_map["C"]["fan_out"] == 1
        assert node_map["D"]["fan_in"] == 1
        assert node_map["D"]["fan_out"] == 0
        assert node_map["A"]["fan_in"] == 0
        assert node_map["A"]["fan_out"] == 1

    def test_node_with_no_edges(self):
        # E is isolated
        data = _imports_map({"A": ["B"]})
        # B has no outgoing edges, E is not even in the map
        graph = build_graph(data)
        node_map = {n["id"]: n for n in graph["nodes"]}
        assert node_map["B"]["fan_in"] == 1
        assert node_map["B"]["fan_out"] == 0


# ---------------------------------------------------------------------------
# 7. Serialization
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_graph_has_required_keys(self):
        data = _imports_map({"A": ["B"]})
        graph = build_graph(data)
        assert "nodes" in graph
        assert "edges" in graph
        assert "cycles" in graph

    def test_nodes_have_required_fields(self):
        data = _imports_map({"A": ["B"]})
        graph = build_graph(data)
        for node in graph["nodes"]:
            assert "id" in node
            assert "fan_in" in node
            assert "fan_out" in node

    def test_edges_have_required_fields(self):
        data = _imports_map({"A": ["B"]})
        graph = build_graph(data)
        for edge in graph["edges"]:
            assert "from" in edge
            assert "to" in edge


# ---------------------------------------------------------------------------
# 8. Hotspots
# ---------------------------------------------------------------------------

class TestHotspots:
    def test_find_hotspots_top3(self):
        # A→C, B→C, C→D, D→E, F→E
        data = _imports_map({
            "A": ["C"],
            "B": ["C"],
            "C": ["D"],
            "D": ["E"],
            "F": ["E"],
        })
        graph = build_graph(data)
        hotspots = find_hotspots(graph, top=3)
        assert len(hotspots) <= 3
        # C has fan_in=2, E has fan_in=2, D has fan_in=1
        hotspot_ids = [h["id"] for h in hotspots]
        # C e E devem estar no top (fan_in=2 cada)
        assert "C" in hotspot_ids
        assert "E" in hotspot_ids

    def test_hotspots_ordered_by_fan_in_desc(self):
        data = _imports_map({
            "A": ["X"],
            "B": ["X"],
            "C": ["X"],
            "D": ["Y"],
            "E": ["Y"],
        })
        graph = build_graph(data)
        hotspots = find_hotspots(graph, top=3)
        fan_ins = [h["fan_in"] for h in hotspots]
        assert fan_ins == sorted(fan_ins, reverse=True)

    def test_hotspots_empty_graph(self):
        graph = build_graph({})
        hotspots = find_hotspots(graph, top=3)
        assert hotspots == []

    def test_find_hotspots_respects_top_parameter(self):
        data = _imports_map({
            "A": ["X"],
            "B": ["X"],
            "C": ["Y"],
            "D": ["Y"],
            "E": ["Z"],
        })
        graph = build_graph(data)
        hotspots = find_hotspots(graph, top=2)
        assert len(hotspots) <= 2


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestGraphEdgeCases:
    def test_empty_imports_map(self):
        graph = build_graph({})
        assert graph["nodes"] == []
        assert graph["edges"] == []
        assert graph["cycles"] == []

    def test_self_import_creates_cycle(self):
        data = _imports_map({"A": ["A"]})
        graph = build_graph(data)
        assert len(graph["cycles"]) >= 1

    def test_unresolved_imports_are_skipped(self):
        # Imports with resolved_path=None should not create edges
        resolved_imports = {
            "A": [
                {"name": "B", "resolved_path": "B", "unresolved": False, "category": ""},
                {"name": "os", "resolved_path": None, "unresolved": True, "category": "stdlib"},
            ]
        }
        graph = build_graph(resolved_imports)
        assert len(graph["edges"]) == 1
        edges = {(e["from"], e["to"]) for e in graph["edges"]}
        assert ("A", "B") in edges
