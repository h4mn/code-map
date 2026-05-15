## ADDED Requirements

### Requirement: Query filtra por dependência
O motor de consulta SHALL suportar filtro `--depends-on <path>` para listar arquivos que dependem do arquivo especificado.

#### Scenario: Depends-on
- **WHEN** query é executado com `--depends-on "Model/Clientes.pas"`
- **THEN** retorna apenas arquivos que importam `Model/Clientes.pas`

#### Scenario: Depends-on sem resultados
- **WHEN** query é executado com `--depends-on "arquivo/isolado.pas"`
- **THEN** retorna lista vazia

### Requirement: Query lista dependências de um arquivo
O motor de consulta SHALL suportar filtro `--depended-by <path>` para listar de quais arquivos o arquivo especificado depende.

#### Scenario: Depended-by
- **WHEN** query é executado com `--depended-by "Controller/Main.pas"`
- **THEN** retorna apenas arquivos que `Controller/Main.pas` importa

### Requirement: Query detecta ciclos
O motor de consulta SHALL suportar flag `--cycles` para listar ciclos de dependência.

#### Scenario: Ciclos encontrados
- **WHEN** query é executado com `--cycles`
- **THEN** retorna lista de ciclos detectados no grafo de dependências

#### Scenario: Sem ciclos
- **WHEN** query é executado com `--cycles` e o grafo é acíclico
- **THEN** retorna lista vazia

### Requirement: REPL suporta filtros de dependência
O REPL SHALL aceitar comandos `depends-on`, `depended-by`, `cycles`.

#### Scenario: REPL depends-on
- **WHEN** usuário digita `depends-on Model/Clientes.pas`
- **THEN** REPL exibe arquivos que dependem de Clientes.pas

#### Scenario: REPL cycles
- **WHEN** usuário digita `cycles`
- **THEN** REPL exibe ciclos detectados ou "Nenhum ciclo encontrado"

#### Scenario: Help atualizado
- **WHEN** usuário digita `help`
- **THEN** exibe lista incluindo `depends-on`, `depended-by`, `cycles`
