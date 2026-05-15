## ADDED Requirements

### Requirement: Config suporta seção uses
O `.codemap.yml` SHALL aceitar a seção `uses` com subchaves: `delphi_search_paths`, `python_paths`, `js_aliases`.

#### Scenario: Config de uses completo
- **WHEN** `.codemap.yml` contém `uses: { delphi_search_paths: ["src", "lib"], python_paths: ["src"], js_aliases: {"@/*": "src/*"} }`
- **THEN** as search paths e aliases são usados na resolução de imports

#### Scenario: Config de uses parcial
- **WHEN** `.codemap.yml` contém apenas `uses: { delphi_search_paths: ["src"] }`
- **THEN** apenas Delphi search paths são configurados, demais usam defaults

#### Scenario: Defaults de uses
- **WHEN** `.codemap.yml` não contém seção `uses`
- **THEN** search paths são vazios e aliases são vazios
