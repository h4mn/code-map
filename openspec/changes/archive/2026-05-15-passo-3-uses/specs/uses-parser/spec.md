## ADDED Requirements

### Requirement: Parser dispatcher seleciona parser por linguagem
O `parse_imports(filepath, language)` SHALL selecionar o parser correto com base na linguagem e retornar uma lista de `ImportRef`.

#### Scenario: Arquivo Delphi
- **WHEN** `parse_imports("Clientes.pas", "delphi")` é chamado
- **THEN** usa o parser Delphi e retorna lista de ImportRef com cláusulas uses

#### Scenario: Arquivo Python
- **WHEN** `parse_imports("utils.py", "python")` é chamado
- **THEN** usa o parser Python (ast) e retorna lista de ImportRef

#### Scenario: Linguagem não suportada
- **WHEN** `parse_imports("readme.md", "markdown")` é chamado
- **THEN** retorna lista vazia sem erro

#### Scenario: Arquivo inexistente
- **WHEN** `parse_imports("nao_existe.pas", "delphi")` é chamado
- **THEN** retorna lista vazia sem levantar exceção

### Requirement: Parser Delphi extrai uses de interface e implementation
O parser Delphi SHALL extrair cláusulas `uses` das seções `interface` e `implementation`, distinguindo-as.

#### Scenario: Uses na interface
- **WHEN** um arquivo `.pas` contém `uses UnitA, UnitB;` na seção interface
- **THEN** retorna ImportRef para `UnitA` e `UnitB` com `section="interface"`

#### Scenario: Uses na implementation
- **WHEN** um arquivo `.pas` contém `uses UnitC;` na seção implementation
- **THEN** retorna ImportRef para `UnitC` com `section="implementation"`

#### Scenario: Uses multi-linha
- **WHEN** um arquivo `.pas` contém `uses\n  UnitA,\n  UnitB,\n  UnitC;`
- **THEN** retorna ImportRef para todas as 3 units

#### Scenario: Uses na unit statement (dpr/lpr)
- **WHEN** um arquivo `.dpr` contém `uses UnitA in 'path/UnitA.pas', UnitB;`
- **THEN** retorna ImportRef para `UnitA` e `UnitB`, ignorando o `in 'path'`

#### Scenario: Sem uses
- **WHEN** um arquivo `.pas` não contém cláusula `uses`
- **THEN** retorna lista vazia

### Requirement: Parser Python extrai imports via ast
O parser Python SHALL usar o módulo `ast` para extrair imports de forma robusta.

#### Scenario: Import simples
- **WHEN** arquivo contém `import os`
- **THEN** retorna ImportRef(module="os", level=0, kind="import")

#### Scenario: From import
- **WHEN** arquivo contém `from pathlib import Path`
- **THEN** retorna ImportRef(module="pathlib", names=["Path"], level=0, kind="from")

#### Scenario: Import relativo
- **WHEN** arquivo contém `from . import utils`
- **THEN** retorna ImportRef(module="", names=["utils"], level=1, kind="from")

#### Scenario: From import multi-level relativo
- **WHEN** arquivo contém `from ..models import User`
- **THEN** retorna ImportRef(module="models", names=["User"], level=2, kind="from")

### Requirement: Parser JS/TS extrai imports e requires
O parser JS/TS SHALL extrair `import` statements e `require()` calls.

#### Scenario: Import default
- **WHEN** arquivo contém `import React from 'react'`
- **THEN** retorna ImportRef(source="react", kind="import")

#### Scenario: Import named
- **WHEN** arquivo contém `import { useState } from 'react'`
- **THEN** retorna ImportRef(source="react", kind="import")

#### Scenario: Require
- **WHEN** arquivo contém `const path = require('path')`
- **THEN** retorna ImportRef(source="path", kind="require")

#### Scenario: Import dinâmico
- **WHEN** arquivo contém `import('./module')`
- **THEN** retorna ImportRef(source="./module", kind="dynamic")
