"""Testes do resolver — resolve_imports()."""

import pytest

from codemap.config import DirmapConfig
from codemap.uses.resolver import resolve_imports


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tree(entries: list[str], ext: str, language: str) -> list[dict]:
    """Cria tree_entries a partir de lista de paths."""
    return [
        {"path": p, "type": "file", "extension": ext, "language": language}
        for p in entries
    ]


def _delphi_tree(entries: list[str]) -> list[dict]:
    return _tree(entries, ".pas", "delphi")


def _python_tree(entries: list[str]) -> list[dict]:
    return _tree(entries, ".py", "python")


def _ts_tree(entries: list[str]) -> list[dict]:
    return _tree(entries, ".tsx", "typescript")


# ---------------------------------------------------------------------------
# 1. Delphi by name
# ---------------------------------------------------------------------------

class TestDelphiByName:
    def test_resolves_unit_by_basename(self):
        tree = _delphi_tree(["Model/Clientes.pas", "Model/Produtos.pas"])
        imports = [{"name": "Clientes", "section": "interface", "line": 1, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "View/Main.pas", tree, config)
        assert len(result) == 1
        assert result[0]["resolved_path"] == "Model/Clientes.pas"
        assert result[0]["unresolved"] is False
        assert result[0]["category"] == ""


# ---------------------------------------------------------------------------
# 2. Delphi with search paths
# ---------------------------------------------------------------------------

class TestDelphiSearchPaths:
    def test_resolves_with_search_path_prefix(self):
        tree = _delphi_tree(["src/Common/Utils.pas", "Model/Clientes.pas"])
        imports = [{"name": "Utils", "section": "implementation", "line": 5, "unresolved": False}]
        config = DirmapConfig(delphi_search_paths=["src/Common"])
        result = resolve_imports(imports, "View/Main.pas", tree, config)
        assert len(result) == 1
        assert result[0]["resolved_path"] == "src/Common/Utils.pas"
        assert result[0]["unresolved"] is False


# ---------------------------------------------------------------------------
# 3. Python absolute import
# ---------------------------------------------------------------------------

class TestPythonAbsolute:
    def test_resolves_absolute_import(self):
        tree = _python_tree(["codemap/config.py", "codemap/cli.py", "main.py"])
        imports = [{"name": "codemap.config", "section": "import", "line": 1, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "main.py", tree, config)
        assert len(result) == 1
        assert result[0]["resolved_path"] == "codemap/config.py"
        assert result[0]["unresolved"] is False


# ---------------------------------------------------------------------------
# 4. Python relative import
# ---------------------------------------------------------------------------

class TestPythonRelative:
    def test_resolves_relative_import_level1(self):
        tree = _python_tree(["codemap/cli.py", "codemap/utils.py"])
        # Parser emite name=".utils" com level=1 (convenção: dot-prefixed)
        imports = [{"name": ".utils", "section": "from", "line": 1, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "codemap/cli.py", tree, config)
        assert len(result) == 1
        assert result[0]["resolved_path"] == "codemap/utils.py"
        assert result[0]["unresolved"] is False


# ---------------------------------------------------------------------------
# 5. JS relative import
# ---------------------------------------------------------------------------

class TestJsRelative:
    def test_resolves_relative_with_extension_fallback(self):
        tree = [
            {"path": "src/App.tsx", "type": "file", "extension": ".tsx", "language": "typescript"},
            {"path": "src/components/Button.tsx", "type": "file", "extension": ".tsx", "language": "typescript"},
        ]
        imports = [{"name": "./components/Button", "section": "import", "line": 1, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "src/App.tsx", tree, config)
        assert len(result) == 1
        assert result[0]["resolved_path"] == "src/components/Button.tsx"
        assert result[0]["unresolved"] is False

    def test_resolves_ts_fallback(self):
        tree = [
            {"path": "src/App.tsx", "type": "file", "extension": ".tsx", "language": "typescript"},
            {"path": "src/helpers.ts", "type": "file", "extension": ".ts", "language": "typescript"},
        ]
        imports = [{"name": "./helpers", "section": "import", "line": 1, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "src/App.tsx", tree, config)
        assert len(result) == 1
        assert result[0]["resolved_path"] == "src/helpers.ts"


# ---------------------------------------------------------------------------
# 6. JS aliases
# ---------------------------------------------------------------------------

class TestJsAliases:
    def test_resolves_alias(self):
        tree = [
            {"path": "src/App.tsx", "type": "file", "extension": ".tsx", "language": "typescript"},
            {"path": "src/utils/helpers.tsx", "type": "file", "extension": ".tsx", "language": "typescript"},
        ]
        imports = [{"name": "@/utils/helpers", "section": "import", "line": 1, "unresolved": False}]
        config = DirmapConfig(js_aliases={"@/*": "src/*"})
        result = resolve_imports(imports, "src/App.tsx", tree, config)
        assert len(result) == 1
        assert result[0]["resolved_path"] == "src/utils/helpers.tsx"
        assert result[0]["unresolved"] is False


# ---------------------------------------------------------------------------
# 7. Unresolved stdlib
# ---------------------------------------------------------------------------

class TestUnresolvedStdlib:
    def test_python_os_is_stdlib(self):
        tree = _python_tree(["main.py"])
        imports = [{"name": "os", "section": "import", "line": 1, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "main.py", tree, config)
        assert len(result) == 1
        assert result[0]["resolved_path"] is None
        assert result[0]["unresolved"] is True
        assert result[0]["category"] == "stdlib"

    def test_python_sys_is_stdlib(self):
        tree = _python_tree(["main.py"])
        imports = [{"name": "sys", "section": "import", "line": 1, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "main.py", tree, config)
        assert len(result) == 1
        assert result[0]["unresolved"] is True
        assert result[0]["category"] == "stdlib"


# ---------------------------------------------------------------------------
# 8. Unresolved third-party
# ---------------------------------------------------------------------------

class TestUnresolvedThirdParty:
    def test_flask_is_third_party(self):
        tree = _python_tree(["main.py"])
        imports = [{"name": "flask", "section": "import", "line": 1, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "main.py", tree, config)
        assert len(result) == 1
        assert result[0]["resolved_path"] is None
        assert result[0]["unresolved"] is True
        assert result[0]["category"] == "third-party"


# ---------------------------------------------------------------------------
# 9. Unresolved unknown
# ---------------------------------------------------------------------------

class TestUnresolvedUnknown:
    def test_delphi_unknown_unit(self):
        tree = _delphi_tree(["Model/Clientes.pas"])
        imports = [{"name": "SomeUnknownUnit", "section": "interface", "line": 1, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "View/Main.pas", tree, config)
        assert len(result) == 1
        assert result[0]["resolved_path"] is None
        assert result[0]["unresolved"] is True
        assert result[0]["category"] == "unknown"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_imports_list(self):
        tree = _delphi_tree(["Model/Clientes.pas"])
        config = DirmapConfig()
        result = resolve_imports([], "View/Main.pas", tree, config)
        assert result == []

    def test_multiple_imports_mixed(self):
        tree = [
            {"path": "Model/Clientes.pas", "type": "file", "extension": ".pas", "language": "delphi"},
            {"path": "Utils.pas", "type": "file", "extension": ".pas", "language": "delphi"},
        ]
        imports = [
            {"name": "Clientes", "section": "interface", "line": 1, "unresolved": False},
            {"name": "SysUtils", "section": "interface", "line": 2, "unresolved": False},
            {"name": "Utils", "section": "implementation", "line": 5, "unresolved": False},
        ]
        config = DirmapConfig()
        result = resolve_imports(imports, "View/Main.pas", tree, config)
        assert len(result) == 3
        assert result[0]["resolved_path"] == "Model/Clientes.pas"
        assert result[0]["unresolved"] is False
        assert result[1]["resolved_path"] is None
        assert result[1]["unresolved"] is True
        # SysUtils is a Delphi RTL unit — stdlib-like
        assert result[1]["category"] in ("stdlib", "unknown")
        assert result[2]["resolved_path"] == "Utils.pas"
        assert result[2]["unresolved"] is False

    def test_original_fields_preserved(self):
        tree = _delphi_tree(["Clientes.pas"])
        imports = [{"name": "Clientes", "section": "interface", "line": 42, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "Main.pas", tree, config)
        assert result[0]["name"] == "Clientes"
        assert result[0]["section"] == "interface"
        assert result[0]["line"] == 42


# ---------------------------------------------------------------------------
# JS/TS third-party
# ---------------------------------------------------------------------------

class TestJsThirdParty:
    def test_react_is_third_party(self):
        tree = _ts_tree(["src/App.tsx"])
        imports = [{"name": "react", "section": "import", "line": 1, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "src/App.tsx", tree, config)
        assert len(result) == 1
        assert result[0]["resolved_path"] is None
        assert result[0]["unresolved"] is True
        assert result[0]["category"] == "third-party"

    def test_vue_is_third_party(self):
        tree = _ts_tree(["src/main.ts"])
        imports = [{"name": "vue", "section": "import", "line": 1, "unresolved": False}]
        config = DirmapConfig()
        result = resolve_imports(imports, "src/main.ts", tree, config)
        assert result[0]["category"] == "third-party"


# ---------------------------------------------------------------------------
# Python with python_paths config
# ---------------------------------------------------------------------------

class TestPythonPathsConfig:
    def test_python_paths_used(self):
        tree = _python_tree(["src/codemap/config.py", "main.py"])
        imports = [{"name": "codemap.config", "section": "import", "line": 1, "unresolved": False}]
        config = DirmapConfig(python_paths=["src"])
        result = resolve_imports(imports, "main.py", tree, config)
        assert result[0]["resolved_path"] == "src/codemap/config.py"
