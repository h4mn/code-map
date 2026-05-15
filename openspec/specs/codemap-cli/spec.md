## ADDED Requirements

### Requirement: Registry registra comandos dinamicamente
O `CommandRegistry` SHALL permitir registro de comandos via decorator `@registry.register(name, description, category)`.

#### Scenario: Registro de comando
- **WHEN** um módulo usa `@registry.register("metrics", "Gera métricas do codebase", "análise")`
- **THEN** o comando `metrics` aparece no registry com nome, descrição e categoria

#### Scenario: Comando duplicado
- **WHEN** dois módulos registram o mesmo nome de comando
- **THEN** o registry levanta `ValueError` informando o conflito

### Requirement: Help é gerado dinamicamente
O registry SHALL gerar texto de help a partir dos comandos registrados, agrupados por categoria.

#### Scenario: Help sem argumentos
- **WHEN** o usuário executa `codemap` sem argumentos
- **THEN** exibe help com todos os comandos registrados, agrupados por categoria

#### Scenario: Help com novo comando registrado
- **WHEN** um novo módulo registra um comando via decorator
- **THEN** o help atualizado inclui esse comando sem nenhuma alteração manual

### Requirement: Help por comando é dinâmico
O help individual de cada comando SHALL ser gerado a partir do signature da função e docstring.

#### Scenario: Help do dirmap
- **WHEN** o usuário executa `codemap dirmap --help`
- **THEN** exibe descrição, argumentos e flags extraídos automaticamente da função

### Requirement: Subcomando version exibe versão
O comando `codemap version` SHALL exibir a versão atual do pacote.

#### Scenario: Version
- **WHEN** o usuário executa `codemap version`
- **THEN** exibe `codemap v0.1.0`

### Requirement: Validação de dependências no entrypoint
O entrypoint SHALL validar dependências obrigatórias antes de qualquer execução, falhando rápido com mensagem clara.

#### Scenario: Dependência presente
- **WHEN** pyyaml está instalado e o usuário executa `codemap dirmap`
- **THEN** a execução prossegue normalmente

#### Scenario: Dependência faltando
- **WHEN** pyyaml não está instalado e o usuário executa `codemap dirmap`
- **THEN** exibe no stderr `Dependências faltando: pyyaml: PyYAML é necessário. Instale: pip install pyyaml` e sai com código 1

### Requirement: Entrypoint via pyproject.toml
O comando `codemap` SHALL ser disponibilizado no PATH via entrypoint em `pyproject.toml`.

#### Scenario: Instalação e uso
- **WHEN** o usuário executa `pip install -e .`
- **THEN** o comando `codemap` está disponível no terminal

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
