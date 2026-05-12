"""Testes do MetricsAggregator."""

import pytest
from codemap.metrics.counter import LocResult
from codemap.metrics.aggregator import aggregate, DirMetrics


class TestAggregator:
    def test_diretorio_com_multiplos_arquivos(self):
        items = [
            {"path": "src/A.pas", "language": "delphi", "loc_result": LocResult(10, 8, 1, 1)},
            {"path": "src/B.pas", "language": "delphi", "loc_result": LocResult(20, 15, 3, 2)},
            {"path": "src/C.pas", "language": "delphi", "loc_result": LocResult(30, 25, 2, 3)},
        ]
        result = aggregate(items)
        assert "src" in result
        dm = result["src"]
        assert dm.loc_code == 48  # 8+15+25
        assert dm.file_count == {"delphi": 3}

    def test_diversidade_multipla(self):
        items = [
            {"path": "proj/A.pas", "language": "delphi", "loc_result": LocResult(5, 3, 1, 1)},
            {"path": "proj/B.py", "language": "python", "loc_result": LocResult(5, 3, 1, 1)},
        ]
        result = aggregate(items)
        assert result["proj"].language_diversity == 2

    def test_diversidade_unica(self):
        items = [
            {"path": "proj/A.pas", "language": "delphi", "loc_result": LocResult(5, 3, 1, 1)},
        ]
        result = aggregate(items)
        assert result["proj"].language_diversity == 1

    def test_ratio_codigo_comentario(self):
        items = [
            {"path": "x/A.pas", "language": "delphi", "loc_result": LocResult(100, 80, 20, 0)},
        ]
        result = aggregate(items)
        assert result["x"].code_comment_ratio == 4.0

    def test_ratio_sem_comentarios(self):
        items = [
            {"path": "x/A.pas", "language": "delphi", "loc_result": LocResult(10, 10, 0, 0)},
        ]
        result = aggregate(items)
        assert result["x"].code_comment_ratio is None

    def test_arquivo_sem_loc(self):
        items = [
            {"path": "x/A.bin", "language": "unknown", "loc_result": None},
        ]
        result = aggregate(items)
        assert result["x"].loc_code == 0
        assert result["x"].file_count == {"unknown": 1}
