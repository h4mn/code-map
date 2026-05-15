"""Testes de config para seção uses."""

import pytest
from pathlib import Path

from codemap.config import DirmapConfig


class TestUsesConfigDefaults:
    def test_defaults_uses(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = DirmapConfig.load()
        assert config.delphi_search_paths == []
        assert config.python_paths == []
        assert config.js_aliases == {}


class TestUsesConfigCompleto:
    def test_config_uses_completo(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n"
            "  uses:\n"
            "    delphi_search_paths: ['src', 'lib', 'c:\\delphi\\components']\n"
            "    python_paths: ['src']\n"
            "    js_aliases:\n"
            "      '@/*': 'src/*'\n",
            encoding="utf-8",
        )
        config = DirmapConfig.load()
        assert config.delphi_search_paths == ["src", "lib", "c:\\delphi\\components"]
        assert config.python_paths == ["src"]
        assert config.js_aliases == {"@/*": "src/*"}

    def test_config_uses_parcial(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n"
            "  uses:\n"
            "    delphi_search_paths: ['src']\n",
            encoding="utf-8",
        )
        config = DirmapConfig.load()
        assert config.delphi_search_paths == ["src"]
        assert config.python_paths == []
        assert config.js_aliases == {}

    def test_config_sem_uses(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".codemap.yml").write_text(
            "dirmap:\n  walker:\n    max_depth: 3\n",
            encoding="utf-8",
        )
        config = DirmapConfig.load()
        assert config.delphi_search_paths == []
