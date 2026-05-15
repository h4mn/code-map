"""Testes do parser JS/TS — extração de imports."""

import pytest
from pathlib import Path

from codemap.uses.js_ts import parse_js_ts_imports, JsImportRef


class TestEsModuleImport:
    def test_import_default(self, tmp_path):
        src = tmp_path / "app.tsx"
        src.write_text("import React from 'react';\n", encoding="utf-8")
        refs = parse_js_ts_imports(src)
        assert len(refs) == 1
        assert refs[0].source == "react"
        assert refs[0].section == "import"
        assert refs[0].line > 0

    def test_import_named(self, tmp_path):
        src = tmp_path / "app.ts"
        src.write_text("import { useState, useEffect } from 'react';\n", encoding="utf-8")
        refs = parse_js_ts_imports(src)
        assert len(refs) == 1
        assert refs[0].source == "react"
        assert refs[0].section == "import"

    def test_import_namespace(self, tmp_path):
        src = tmp_path / "app.ts"
        src.write_text("import * as fs from 'fs';\n", encoding="utf-8")
        refs = parse_js_ts_imports(src)
        assert len(refs) == 1
        assert refs[0].source == "fs"
        assert refs[0].section == "import"

    def test_import_side_effect(self, tmp_path):
        src = tmp_path / "app.ts"
        src.write_text("import './styles.css';\n", encoding="utf-8")
        refs = parse_js_ts_imports(src)
        assert len(refs) == 1
        assert refs[0].source == "./styles.css"
        assert refs[0].section == "import"

    def test_import_default_e_named(self, tmp_path):
        src = tmp_path / "app.ts"
        src.write_text("import React, { useState } from 'react';\n", encoding="utf-8")
        refs = parse_js_ts_imports(src)
        assert len(refs) == 1
        assert refs[0].source == "react"


class TestCommonJsRequire:
    def test_require_simples(self, tmp_path):
        src = tmp_path / "app.js"
        src.write_text("const path = require('path');\n", encoding="utf-8")
        refs = parse_js_ts_imports(src)
        assert len(refs) == 1
        assert refs[0].source == "path"
        assert refs[0].section == "require"

    def test_require_com_template_string(self, tmp_path):
        """Template strings nao sao o caso comum, mas require com aspas simples e duplas sim."""
        src = tmp_path / "app.js"
        src.write_text('const fs = require("fs");\n', encoding="utf-8")
        refs = parse_js_ts_imports(src)
        assert len(refs) == 1
        assert refs[0].source == "fs"
        assert refs[0].section == "require"


class TestDynamicImport:
    def test_dynamic_import(self, tmp_path):
        src = tmp_path / "app.ts"
        src.write_text("import('./module').then(m => m.init());\n", encoding="utf-8")
        refs = parse_js_ts_imports(src)
        assert len(refs) == 1
        assert refs[0].source == "./module"
        assert refs[0].section == "dynamic"


class TestMixed:
    def test_multiplos_imports(self, tmp_path):
        src = tmp_path / "app.ts"
        src.write_text(
            "import React from 'react';\n"
            "import { useState } from 'react';\n"
            "const path = require('path');\n"
            "import('./lazy').then(m => m.init());\n",
            encoding="utf-8",
        )
        refs = parse_js_ts_imports(src)
        assert len(refs) == 4
        sections = [r.section for r in refs]
        assert sections.count("import") == 2
        assert sections.count("require") == 1
        assert sections.count("dynamic") == 1


class TestEdgeCases:
    def test_arquivo_vazio(self, tmp_path):
        src = tmp_path / "empty.ts"
        src.write_text("", encoding="utf-8")
        refs = parse_js_ts_imports(src)
        assert refs == []

    def test_arquivo_inexistente(self):
        refs = parse_js_ts_imports(Path("/nao/existe.ts"))
        assert refs == []

    def test_arquivo_sem_imports(self, tmp_path):
        src = tmp_path / "no_imports.js"
        src.write_text("const x = 42;\nconsole.log(x);\n", encoding="utf-8")
        refs = parse_js_ts_imports(src)
        assert refs == []

    def test_linhas_corretas(self, tmp_path):
        src = tmp_path / "app.ts"
        src.write_text(
            "// comment\n"
            "import React from 'react';\n"
            "\n"
            "const path = require('path');\n",
            encoding="utf-8",
        )
        refs = parse_js_ts_imports(src)
        assert len(refs) == 2
        # import na linha 2
        assert refs[0].line == 2
        # require na linha 4
        assert refs[1].line == 4

    def test_export_from(self, tmp_path):
        """export { foo } from 'bar' tambem e uma dependencia."""
        src = tmp_path / "reexport.ts"
        src.write_text("export { MyComponent } from './components';\n", encoding="utf-8")
        refs = parse_js_ts_imports(src)
        assert len(refs) == 1
        assert refs[0].source == "./components"
        assert refs[0].section == "import"
