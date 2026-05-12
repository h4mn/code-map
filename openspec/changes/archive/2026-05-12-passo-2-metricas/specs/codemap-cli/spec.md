## MODIFIED Requirements

### Requirement: Registry registra comandos dinamicamente
O `CommandRegistry` SHALL permitir registro de comandos via decorator `@registry.register(name, description, category)`.

#### Scenario: Registro de comando
- **WHEN** um módulo usa `@registry.register("metrics", "Gera métricas do codebase", "análise")`
- **THEN** o comando `metrics` aparece no registry com nome, descrição e categoria

## ADDED Requirements

### Requirement: Subcomando metrics
O comando `codemap metrics <dirmap.json>` SHALL gerar métricas sobre um índice Dirmap existente.

#### Scenario: Métricas básicas
- **WHEN** usuário executa `codemap metrics dirmap.json`
- **THEN** gera métricas de LOC, duplicatas e órfãos para todos os arquivos do índice

#### Scenario: Arquivo inexistente
- **WHEN** usuário executa `codemap metrics nao-existe.json`
- **THEN** exibe erro claro no stderr e sai com código 1

### Requirement: Flag --with-metrics no dirmap
O comando `codemap dirmap` SHALL aceitar flag `--with-metrics` para gerar métricas junto com o índice.

#### Scenario: Dirmap com métricas
- **WHEN** usuário executa `codemap dirmap ./projeto --with-metrics`
- **THEN** o JSON de saída inclui campo `metrics` em cada entrada

#### Scenario: Dirmap sem métricas
- **WHEN** usuário executa `codemap dirmap ./projeto`
- **THEN** o JSON de saída NÃO inclui campo `metrics` (comportamento atual preservado)
