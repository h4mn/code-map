## ADDED Requirements

### Requirement: Query filtra por extensão
O motor de consulta SHALL suportar filtro `--ext` para filtrar arquivos por extensão.

#### Scenario: Filtro por extensão
- **WHEN** o query é executado com `--ext .dpr`
- **THEN** retorna apenas arquivos com `extension` igual a `.dpr`

#### Scenario: Extensão sem match
- **WHEN** o query é executado com `--ext .xyz` e não há arquivos com essa extensão
- **THEN** retorna lista vazia

### Requirement: Query filtra por linguagem
O motor de consulta SHALL suportar filtro `--lang` para filtrar arquivos por linguagem classificada.

#### Scenario: Filtro por linguagem
- **WHEN** o query é executado com `--lang delphi`
- **THEN** retorna apenas arquivos com `language` igual a `"delphi"`

### Requirement: Query filtra por path
O motor de consulta SHALL suportar filtro `--path` para filtrar por prefixo de caminho.

#### Scenario: Filtro por path
- **WHEN** o query é executado com `--path "src/Model"`
- **THEN** retorna apenas entradas cujo `path` começa com `src/Model`

### Requirement: Query filtra por tipo
O motor de consulta SHALL suportar filtro `--type` com valores `file` ou `dir`.

#### Scenario: Filtro por tipo file
- **WHEN** o query é executado com `--type file`
- **THEN** retorna apenas entradas com `type` igual a `"file"`

### Requirement: Query suporta count
O motor de consulta SHALL suportar flag `--count` que retorna apenas o número de resultados.

#### Scenario: Count com filtro
- **WHEN** o query é executado com `--ext .pas --count`
- **THEN** retorna um número inteiro representando a quantidade de arquivos `.pas`

### Requirement: Query suporta summary
O motor de consulta SHALL suportar flag `--summary` que retorna o campo `summary` do JSON.

#### Scenario: Summary
- **WHEN** o query é executado com `--summary`
- **THEN** retorna o objeto `summary` completo

### Requirement: Filtros são combináveis
O motor de consulta SHALL permitir combinação de filtros com operação AND.

#### Scenario: Combinação de filtros
- **WHEN** o query é executado com `--ext .pas --path "src/Model"`
- **THEN** retorna apenas arquivos `.pas` dentro de `src/Model`

### Requirement: Query CLI retorna JSON no stdout
O subcomando `query` SHALL imprimir resultado no stdout em formato JSON, sem texto decorativo.

#### Scenario: Saída pipe-friendly
- **WHEN** o query é executado via CLI
- **THEN** a saída é JSON válido no stdout, consumível por pipe

### Requirement: REPL aceita mesmos filtros em modo interativo
O REPL SHALL aceitar os mesmos filtros do CLI (ext, lang, path, type, count, summary) em formato curto.

#### Scenario: REPL com filtro
- **WHEN** o usuário digita `ext .dpr` no REPL
- **THEN** o REPL exibe a lista de arquivos `.dpr` encontrados

#### Scenario: REPL com count
- **WHEN** o usuário digita `ext .pas path src/Model count` no REPL
- **THEN** o REPL exibe a contagem de arquivos `.pas` em `src/Model`

#### Scenario: Help do REPL
- **WHEN** o usuário digita `help` no REPL
- **THEN** o REPL exibe a lista de filtros disponíveis com descrição

### Requirement: REPL exibe mensagem de boas-vindas
O REPL SHALL exibir mensagem de boas-vindas com o nome do codebase e total de arquivos ao iniciar.

#### Scenario: Início do REPL
- **WHEN** o REPL é iniciado com `codemap repl dirmap.json`
- **THEN** exibe `CodeMap REPL — Hadsteca (1247 arquivos)` e aguarda input
