"""Testes do walker."""

import os
import pytest
from pathlib import Path

from codemap.config import DirmapConfig
from codemap.dirmap.walker import walk, Entry


class TestWalkSimples:
    def test_arvore_simples(self, tmp_path):
        (tmp_path / "file1.pas").write_text("", encoding="utf-8")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "file2.dfm").write_text("", encoding="utf-8")
        (sub / "file3.md").write_text("x", encoding="utf-8")

        result = walk(tmp_path)
        files = [e for e in result.entries if e.type == "file"]
        assert len(files) == 3
        assert any(e.extension == ".pas" for e in files)
        assert any(e.extension == ".dfm" for e in files)
        assert any(e.extension == ".md" for e in files)

    def test_diretorio_vazio(self, tmp_path):
        result = walk(tmp_path)
        assert len(result.entries) == 0
        assert result.total_dirs == 0

    def test_path_nao_existe(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="não encontrado"):
            walk(tmp_path / "nao_existe")

    def test_path_arquivo_nao_diretorio(self, tmp_path):
        f = tmp_path / "arquivo.txt"
        f.write_text("", encoding="utf-8")
        with pytest.raises(FileNotFoundError, match="não é um diretório"):
            walk(f)


class TestWalkIgnore:
    def test_respeita_gitignore(self, tmp_path):
        (tmp_path / ".gitignore").write_text("bin/\n", encoding="utf-8")
        (tmp_path / "keep.pas").write_text("", encoding="utf-8")
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        (bin_dir / "app.exe").write_bytes(b"\x00")

        config = DirmapConfig(ignore_files=[".gitignore"])
        result = walk(tmp_path, config)
        files = [e for e in result.entries if e.type == "file"]
        assert len(files) == 1
        assert files[0].path == "keep.pas"

    def test_respeita_codemap_ignore(self, tmp_path):
        (tmp_path / ".codemap-ignore").write_text("debug/\n", encoding="utf-8")
        debug = tmp_path / "debug"
        debug.mkdir()
        (debug / "log.txt").write_text("", encoding="utf-8")
        (tmp_path / "main.pas").write_text("", encoding="utf-8")

        config = DirmapConfig(ignore_files=[".codemap-ignore"])
        result = walk(tmp_path, config)
        files = [e for e in result.entries if e.type == "file"]
        assert len(files) == 1

    def test_extra_dirs(self, tmp_path):
        nm = tmp_path / "node_modules"
        nm.mkdir()
        (nm / "pkg.js").write_text("", encoding="utf-8")
        (tmp_path / "app.py").write_text("", encoding="utf-8")

        config = DirmapConfig(extra_dirs=["node_modules"])
        result = walk(tmp_path, config)
        files = [e for e in result.entries if e.type == "file"]
        assert len(files) == 1
        assert files[0].path == "app.py"


class TestWalkMaxDepth:
    def test_limita_profundidade(self, tmp_path):
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "b").mkdir()
        (tmp_path / "a" / "b" / "c").mkdir()
        (tmp_path / "a" / "file1.txt").write_text("", encoding="utf-8")
        (tmp_path / "a" / "b" / "file2.txt").write_text("", encoding="utf-8")
        (tmp_path / "a" / "b" / "c" / "file3.txt").write_text("", encoding="utf-8")

        config = DirmapConfig(max_depth=2)
        result = walk(tmp_path, config)
        files = [e for e in result.entries if e.type == "file"]
        assert len(files) == 2

    def test_sem_limite(self, tmp_path):
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "b").mkdir()
        (tmp_path / "a" / "b" / "file.txt").write_text("", encoding="utf-8")

        config = DirmapConfig(max_depth=None)
        result = walk(tmp_path, config)
        files = [e for e in result.entries if e.type == "file"]
        assert len(files) == 1


class TestWalkSymlink:
    def test_nao_segue_symlink_por_default(self, tmp_path):
        target = tmp_path / "target"
        target.mkdir()
        (target / "secret.txt").write_text("", encoding="utf-8")
        link = tmp_path / "link"
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            pytest.skip("Sem privilégio para criar symlinks neste ambiente")

        config = DirmapConfig(follow_symlinks=False)
        result = walk(tmp_path, config)
        files = [e for e in result.entries if e.type == "file"]
        assert len(files) == 0


class TestWalkPermission:
    def test_diretorio_sem_permissao_registra_erro(self, tmp_path):
        restricted = tmp_path / "restricted"
        restricted.mkdir()
        (tmp_path / "ok.txt").write_text("", encoding="utf-8")

        original_iterdir = Path.iterdir

        def mock_iterdir(self):
            if self == restricted:
                raise PermissionError("Access denied")
            return original_iterdir(self)

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(Path, "iterdir", mock_iterdir)
            result = walk(tmp_path)
            assert len(result.errors) == 1
            assert result.errors[0]["reason"] == "permission_denied"
            files = [e for e in result.entries if e.type == "file"]
            assert len(files) == 1
