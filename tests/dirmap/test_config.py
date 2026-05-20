"""Testes do DirmapConfig."""

import pytest
from pathlib import Path

from codemap.config import DirmapConfig


class TestDefaults:
    def test_defaults_sem_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = DirmapConfig.load()
        assert config.ignore_files == [".gitignore"]
        assert "__pycache__" in config.extra_dirs
        assert config.format == "json"
        assert config.indent == 2
        assert config.follow_symlinks is False
        assert config.max_depth is None
        assert config.custom_extensions == {}


class TestProjectConfig:
    def test_config_parcial(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n  walker:\n    max_depth: 3\n", encoding="utf-8"
        )
        config = DirmapConfig.load()
        assert config.max_depth == 3
        assert config.follow_symlinks is False  # default

    def test_config_completo(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n"
            "  ignore:\n"
            "    files: ['.gitignore', '.codemap-ignore']\n"
            "    extra_dirs: ['bin', 'obj']\n"
            "  output:\n"
            "    format: 'json'\n"
            "    indent: 4\n"
            "  walker:\n"
            "    follow_symlinks: true\n"
            "    max_depth: 5\n"
            "  classifier:\n"
            "    custom_extensions:\n"
            "      .dpr: delphi-entry\n",
            encoding="utf-8",
        )
        config = DirmapConfig.load()
        assert config.ignore_files == [".gitignore", ".codemap-ignore"]
        assert config.extra_dirs == ["bin", "obj"]
        assert config.indent == 4
        assert config.follow_symlinks is True
        assert config.max_depth == 5
        assert config.custom_extensions == {".dpr": "delphi-entry"}


class TestMerge:
    def test_cli_sobrepoe_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n  walker:\n    max_depth: 3\n", encoding="utf-8"
        )
        config = DirmapConfig.load(cli_overrides={"max_depth": 10})
        assert config.max_depth == 10

    def test_global_e_projeto_merge(self, tmp_path, monkeypatch):
        global_dir = tmp_path / "global"
        global_dir.mkdir()
        global_cfg = global_dir / "config.yml"
        global_cfg.write_text(
            "dirmap:\n  walker:\n    max_depth: 2\n", encoding="utf-8"
        )

        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".codemap.yml").write_text(
            "dirmap:\n  output:\n    indent: 4\n", encoding="utf-8"
        )

        monkeypatch.chdir(project_dir)
        # Patch home para apontar pro dir global
        config = DirmapConfig._merge(
            DirmapConfig(),
            DirmapConfig._read_yaml(global_cfg),
        )
        config = DirmapConfig._merge(
            config,
            DirmapConfig._read_yaml(project_dir / ".codemap.yml"),
        )
        assert config.max_depth == 2
        assert config.indent == 4


class TestChaveDesconhecida:
    def test_chave_invalida_ignorada(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n  foo: bar\n  walker:\n    baz: qux\n", encoding="utf-8"
        )
        config = DirmapConfig.load()
        assert config.max_depth is None  # baz ignorado

    def test_yaml_malformado_retorna_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text("{invalid yaml", encoding="utf-8")
        config = DirmapConfig.load()
        assert config.max_depth is None


class TestMetricsConfig:
    def test_defaults_metrics(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = DirmapConfig.load()
        assert config.metrics_enabled is True
        assert config.metrics_languages == []
        assert config.duplicates_min_group_size == 2
        assert config.orphans_heuristic is True

    def test_config_metrics_completo(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n"
            "  metrics:\n"
            "    enabled: false\n"
            "    loc:\n"
            "      languages: [delphi, python]\n"
            "    duplicates:\n"
            "      min_group_size: 3\n"
            "    orphans:\n"
            "      heuristic: false\n",
            encoding="utf-8",
        )
        config = DirmapConfig.load()
        assert config.metrics_enabled is False
        assert config.metrics_languages == ["delphi", "python"]
        assert config.duplicates_min_group_size == 3
        assert config.orphans_heuristic is False

    def test_config_metrics_parcial(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n"
            "  metrics:\n"
            "    enabled: true\n",
            encoding="utf-8",
        )
        config = DirmapConfig.load()
        assert config.metrics_enabled is True
        assert config.metrics_languages == []
        assert config.duplicates_min_group_size == 2


class TestDefaultDirmap:
    def test_default_dirmap_none_sem_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = DirmapConfig.load()
        assert config.default_dirmap is None

    def test_default_dirmap_via_project_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n"
            "  default_dirmap: dirmap.json\n",
            encoding="utf-8",
        )
        config = DirmapConfig.load()
        assert config.default_dirmap == "dirmap.json"

    def test_default_dirmap_path_completo(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n"
            "  default_dirmap: C:\\_Fontes\\hadsteca.json\n",
            encoding="utf-8",
        )
        config = DirmapConfig.load()
        assert config.default_dirmap == "C:\\_Fontes\\hadsteca.json"

    def test_default_dirmap_nao_afeta_outros_campos(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n"
            "  default_dirmap: dm.json\n"
            "  walker:\n"
            "    max_depth: 5\n",
            encoding="utf-8",
        )
        config = DirmapConfig.load()
        assert config.default_dirmap == "dm.json"
        assert config.max_depth == 5
