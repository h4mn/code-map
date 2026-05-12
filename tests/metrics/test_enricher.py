"""Testes do MetricsEnricher."""

import json
import pytest
from pathlib import Path

from codemap.metrics.enricher import enrich_dirmap


def _make_dirmap(entries, root="/tmp/test"):
    return {
        "meta": {"tool": "codemap", "root": root},
        "tree": entries,
        "summary": {},
    }


class TestEnricher:
    def test_retrocompatibilidade(self, tmp_path):
        entry = {"path": "test.pas", "type": "file", "extension": ".pas", "language": "delphi", "size_bytes": 100}
        p = tmp_path / "test.pas"
        p.write_text("codigo;\n// comentario\n", encoding="utf-8")

        data = _make_dirmap([entry], str(tmp_path))
        result = enrich_dirmap(data, tmp_path)

        # Campos originais preservados
        r = result["tree"][0]
        assert r["path"] == "test.pas"
        assert r["type"] == "file"
        assert r["extension"] == ".pas"
        assert r["size_bytes"] == 100
        # Métricas adicionadas
        assert "metrics" in r
        assert r["metrics"]["loc_code"] == 1
        assert r["metrics"]["loc_comment"] == 1

    def test_arquivo_sem_metricas(self, tmp_path):
        entry = {"path": "test.exe", "type": "file", "extension": ".exe", "language": "unknown", "size_bytes": 100}
        data = _make_dirmap([entry], str(tmp_path))
        result = enrich_dirmap(data, tmp_path)
        assert result["tree"][0]["metrics"] is None

    def test_flags_duplicata(self, tmp_path):
        entries = [
            {"path": "a/Utils.pas", "type": "file", "extension": ".pas", "language": "delphi", "size_bytes": 50},
            {"path": "b/Utils.pas", "type": "file", "extension": ".pas", "language": "delphi", "size_bytes": 50},
        ]
        (tmp_path / "a").mkdir()
        (tmp_path / "b").mkdir()
        (tmp_path / "a" / "Utils.pas").write_text("code;\n", encoding="utf-8")
        (tmp_path / "b" / "Utils.pas").write_text("code;\n", encoding="utf-8")

        data = _make_dirmap(entries, str(tmp_path))
        result = enrich_dirmap(data, tmp_path)

        for entry in result["tree"]:
            assert entry.get("duplicate_candidate") is True
            assert entry["duplicate_group"] == "Utils.pas"

    def test_metrics_summary(self, tmp_path):
        entries = [
            {"path": "Solo.pas", "type": "file", "extension": ".pas", "language": "delphi", "size_bytes": 50},
        ]
        p = tmp_path / "Solo.pas"
        p.write_text("code;\n", encoding="utf-8")

        data = _make_dirmap(entries, str(tmp_path))
        result = enrich_dirmap(data, tmp_path)

        assert "metrics_summary" in result
        assert result["metrics_summary"]["orphan_count"] == 1

    def test_dir_com_metricas(self, tmp_path):
        entries = [
            {"path": "src/A.pas", "type": "file", "extension": ".pas", "language": "delphi", "size_bytes": 50},
            {"path": "src", "type": "dir"},
        ]
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "A.pas").write_text("codigo;\n// comentario\n", encoding="utf-8")

        data = _make_dirmap(entries, str(tmp_path))
        result = enrich_dirmap(data, tmp_path)

        dir_entry = [e for e in result["tree"] if e["type"] == "dir"][0]
        assert "metrics" in dir_entry
        assert dir_entry["metrics"]["loc_code"] == 1

    def test_metrics_disabled(self, tmp_path):
        from codemap.config import DirmapConfig
        config = DirmapConfig(metrics_enabled=False)
        data = _make_dirmap([{"path": "x.pas", "type": "file", "extension": ".pas", "language": "delphi"}], str(tmp_path))
        result = enrich_dirmap(data, tmp_path, config)
        assert "metrics" not in result["tree"][0]
