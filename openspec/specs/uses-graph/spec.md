# uses-graph

Construcao de grafo dirigido de dependencias a partir dos imports resolvidos.

## Requirements

### Requirement: Graph constroi grafo dirigido de dependencias
O `build_graph(entries, imports)` SHALL construir um grafo dirigido onde nodos sao arquivos e arestas sao dependencias.

#### Scenario: Grafo simples
- **WHEN** `A.pas` importa `B.pas` e `C.pas`
- **THEN** o grafo tem arestas `A.pas -> B.pas` e `A.pas -> C.pas`

#### Scenario: Multiplos arquivos
- **WHEN** `A.pas` importa `B.pas`, `B.pas` importa `C.pas`
- **THEN** o grafo tem arestas `A->B` e `B->C`, e `A` nao depende diretamente de `C`

### Requirement: Graph detecta ciclos
O graph SHALL detectar ciclos no grafo de dependencias e reporta-los.

#### Scenario: Ciclo direto
- **WHEN** `A.pas` importa `B.pas` e `B.pas` importa `A.pas`
- **THEN** detecta ciclo `[A.pas -> B.pas -> A.pas]`

#### Scenario: Ciclo transitivo
- **WHEN** `A->B`, `B->C`, `C->A`
- **THEN** detecta ciclo `[A->B->C->A]`

#### Scenario: Sem ciclos
- **WHEN** o grafo e aciclico
- **THEN** retorna lista vazia de ciclos

### Requirement: Graph calcula fan-in e fan-out
O graph SHALL calcular fan-in (quantos dependem do nodo) e fan-out (de quantos o nodo depende) para cada arquivo.

#### Scenario: Fan-in/fan-out
- **WHEN** `A.pas` e `B.pas` importam `C.pas`, e `C.pas` importa `D.pas`
- **THEN** `C.pas` tem fan-in=2, fan-out=1; `D.pas` tem fan-in=1, fan-out=0

### Requirement: Graph serializa em JSON
O graph SHALL serializar o grafo como dict com chaves `nodes` e `edges`.

#### Scenario: Serializacao
- **WHEN** `build_graph` e chamado com dados validos
- **THEN** retorna `{"nodes": [...], "edges": [...], "cycles": [...]}` onde cada node tem `path`, `fan_in`, `fan_out` e cada edge tem `from`, `to`

### Requirement: Graph identifica hotspots
O graph SHALL identificar os N arquivos com maior fan-in como hotspots de dependencia.

#### Scenario: Top hotspots
- **WHEN** `find_hotspots(graph, top=5)` e chamado
- **THEN** retorna os 5 arquivos mais dependidos, ordenados por fan-in decrescente
