# uses-resolver

Resolucao de imports/uses para caminhos fisicos usando o dirmap como indice.

## Requirements

### Requirement: Resolver mapeia nomes para caminhos usando dirmap
O resolver SHALL receber uma lista de ImportRef e o dirmap, e retornar imports resolvidos com caminhos fisicos.

#### Scenario: Resolucao Delphi por nome de unit
- **WHEN** ImportRef(name="Clientes") e o dirmap contem `Model/Clientes.pas`
- **THEN** resolve para `Model/Clientes.pas`

#### Scenario: Resolucao Delphi com search paths
- **WHEN** ImportRef(name="Utils") e search_paths inclui `src/Common` e o dirmap contem `src/Common/Utils.pas`
- **THEN** resolve para `src/Common/Utils.pas`

#### Scenario: Import Python absoluto
- **WHEN** ImportRef(module="codemap.config") e o dirmap contem `codemap/config.py`
- **THEN** resolve para `codemap/config.py`

#### Scenario: Import Python relativo
- **WHEN** ImportRef(module="utils", level=1) do arquivo `codemap/cli.py`
- **THEN** resolve para `codemap/utils.py` (mesmo diretorio)

#### Scenario: Import JS/TS relativo
- **WHEN** ImportRef(source="./components/Button") do arquivo `src/App.tsx`
- **THEN** resolve para `src/components/Button.tsx`

### Requirement: Resolver marca imports nao resolvidos
O resolver SHALL marcar imports que nao correspondem a nenhum arquivo do dirmap como `unresolved: true`.

#### Scenario: Import de stdlib
- **WHEN** ImportRef(module="os") e nao existe `os.py` no dirmap
- **THEN** retorna ImportRef com `unresolved: True`

#### Scenario: Import de third-party
- **WHEN** ImportRef(source="react") e nao existe `react` no dirmap
- **THEN** retorna ImportRef com `unresolved: True`

### Requirement: Resolver suporta aliases JS/TS
O resolver SHALL expandir aliases configurados (ex: `@/*` para `src/*`) antes da resolucao.

#### Scenario: Alias expansion
- **WHEN** ImportRef(source="@/utils/helpers") e config tem `js_aliases: {"@/*": "src/*"}`
- **THEN** resolve para `src/utils/helpers.ts`

### Requirement: Resolver distingue tipos de import nao resolvido
O resolver SHALL classificar imports nao resolvidos como `stdlib`, `third-party` ou `unknown`.

#### Scenario: Python stdlib
- **WHEN** ImportRef(module="os") nao resolvido em projeto Python
- **THEN** classifica como `stdlib`

#### Scenario: Third-party
- **WHEN** ImportRef(module="flask") nao resolvido
- **THEN** classifica como `third-party`
