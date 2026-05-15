## ADDED Requirements

### Requirement: Subcomando uses
O comando `codemap uses <dirmap.json>` SHALL extrair dependências de imports/uses e enriquecer o dirmap.

#### Scenario: Uses básico
- **WHEN** usuário executa `codemap uses dirmap.json`
- **THEN** lê o dirmap, extrai imports de cada arquivo, resolve dependências e gera grafo

#### Scenario: Uses com output
- **WHEN** usuário executa `codemap uses dirmap.json --output enriched.json`
- **THEN** escreve o dirmap enriquecido no arquivo especificado

#### Scenario: Uses com stdout
- **WHEN** usuário executa `codemap uses dirmap.json --stdout`
- **THEN** imprime o dirmap enriquecido no stdout

#### Scenario: Arquivo inexistente
- **WHEN** usuário executa `codemap uses nao-existe.json`
- **THEN** exibe erro no stderr e sai com código 1

### Requirement: Flag --with-uses no dirmap
O comando `codemap dirmap` SHALL aceitar flag `--with-uses` para extrair dependências junto com o índice.

#### Scenario: Dirmap com uses
- **WHEN** usuário executa `codemap dirmap ./projeto --with-uses`
- **THEN** o JSON de saída inclui campo `imports` e `dependency_graph` em cada entrada

#### Scenario: Dirmap sem uses
- **WHEN** usuário executa `codemap dirmap ./projeto`
- **THEN** o JSON de saída NÃO inclui campo `imports` (comportamento atual preservado)

#### Scenario: Dirmap com metrics e uses
- **WHEN** usuário executa `codemap dirmap ./projeto --with-metrics --with-uses`
- **THEN** o JSON de saída inclui `metrics`, `imports` e `dependency_graph`
