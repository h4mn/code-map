"""Testes do serializer."""

import json
from pathlib import Path

import pytest

from codemap.config import DirmapConfig
from codemap.dirmap.serializer import serialize, run_dirmap
from codemap.dirmap.walker import WalkResult, Entry


class TestSerialize:
    def _make_result(self):
        return WalkResult(
            entries=[
                Entry(path="a.pas", type="file", extension=".pas", size_bytes=100),
                Entry(path="b.pas", type="file", extension=".pas", size_bytes=200),
                Entry(path="c.md", type="file", extension=".md", size_bytes=50),
                Entry(path="src", type="dir"),
            ],
            errors=[],
            total_dirs=1,
        )

    def test_json_valido(self):
        result = self._make_result()
        data = serialize(result, "/project/MyRepo")
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        assert parsed["meta"]["tool"] == "codemap"
        assert parsed["meta"]["root_name"] == "MyRepo"

    def test_meta_completo(self):
        result = self._make_result()
        data = serialize(result, "/project/MyRepo")
        meta = data["meta"]
        assert "tool" in meta
        assert "command" in meta
        assert "version" in meta
        assert "timestamp" in meta
        assert "root" in meta
        assert meta["root_name"] == "MyRepo"

    def test_summary_correto(self):
        result = self._make_result()
        data = serialize(result, "/project/MyRepo")
        s = data["summary"]
        assert s["total_files"] == 3
        assert s["total_dirs"] == 1
        assert s["total_size_bytes"] == 350
        assert s["by_extension"][".pas"] == 2
        assert s["by_extension"][".md"] == 1
        assert s["by_language"]["delphi"] == 2
        assert s["by_language"]["markdown"] == 1

    def test_errors_vazio(self):
        result = self._make_result()
        data = serialize(result, "/project/MyRepo")
        assert data["errors"] == []

    def test_errors_presente(self):
        result = WalkResult(
            entries=[Entry(path="ok.txt", type="file", extension=".txt", size_bytes=10)],
            errors=[{"path": "secret", "reason": "permission_denied"}],
            total_dirs=0,
        )
        data = serialize(result, "/project/MyRepo")
        assert len(data["errors"]) == 1
        assert data["errors"][0]["reason"] == "permission_denied"

    def test_custom_extensions_aplicadas(self):
        result = WalkResult(
            entries=[Entry(path="app.dpr", type="file", extension=".dpr", size_bytes=50)],
            errors=[],
            total_dirs=0,
        )
        config = DirmapConfig(custom_extensions={".dpr": "delphi-entry"})
        data = serialize(result, "/project/MyRepo", config)
        assert data["tree"][0]["language"] == "delphi-entry"


class TestRunDirmap:
    def test_escreve_arquivo(self, tmp_path):
        (tmp_path / "file.pas").write_text("", encoding="utf-8")
        out = tmp_path / "dirmap.json"
        run_dirmap(str(tmp_path), output=str(out))
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["meta"]["tool"] == "codemap"
        assert data["summary"]["total_files"] == 1

    def test_stdout(self, tmp_path, capsys):
        (tmp_path / "file.py").write_text("", encoding="utf-8")
        run_dirmap(str(tmp_path), stdout=True)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["summary"]["total_files"] == 1
        assert not (tmp_path / "dirmap.json").exists()

    def test_indent_customizado(self, tmp_path):
        (tmp_path / "file.txt").write_text("", encoding="utf-8")
        out = tmp_path / "dirmap.json"
        config = DirmapConfig(indent=4)
        from codemap.dirmap.walker import walk
        from codemap.dirmap.serializer import serialize
        result = walk(str(tmp_path), config)
        data = serialize(result, str(tmp_path), config)
        json_str = json.dumps(data, indent=4, ensure_ascii=False)
        out.write_text(json_str, encoding="utf-8")
        # Verifica que usa 4 espaços
        assert "    " in out.read_text(encoding="utf-8")
