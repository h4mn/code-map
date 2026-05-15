## Context

O code-map já indexa a estrutura física (Passo 1) e coleta métricas quantitativas (Passo 2). O codebase-alvo é um TRUNK Delphi com ~52K arquivos e 4.87 GB, com dependências implícitas espalhadas por cláusulas `uses` em milhares de units. O pipeline atual é: walker → classifier → serializer → (opcional) metrics enricher.

## Goals / Non-Goals

**Goals:**
- Extrair cláusulas `uses` (Delphi), `import` (Python) e `import/require` (JS/TS) de cada arquivo
- Resolver nomes curtos para caminhos físicos usando o dirmap como índice
- Construir grafo dirigido de dependências com detecção de ciclos
- Integrar no pipeline existente sem quebrar compatibilidade
- Manter tudo com stdlib (sem deps externas)

**Non-Goals:**
- Parsing AST completo de classes/métodos (Passo 4)
- Grafo de impacto com propagação de mudanças (Passo 5)
- Hash-based duplicate detection (extensão futura do finder)
- Análise semântica de imports (Passo 6)

## Decisions

### D1: Pipeline sequencial (igual ao metrics)

O módulo `uses` segue o mesmo padrão do `metrics`: parser → resolver → graph → enricher. Isso mantém consistência arquitetural e permite reusar o padrão de enriquecimento do dirmap.

**Alternativa considerada**: Pipeline paralelo com multiprocessing. Rejeitado porque o gargalo é I/O de leitura de arquivos, não CPU. O ganho não justifica a complexidade.

### D2: Regex para Delphi, ast para Python, regex para JS/TS

- **Delphi**: Regex porque a gramática de `uses` é simples e previsível (palavra-chave `uses` seguida de lista separada por vírgula).
- **Python**: `ast` module do stdlib para parsing robusto — lida com edge cases (multiline imports, imports relativos, aliases).
- **JS/TS**: Regex porque a variabilidade de sintaxe é baixa (`import ... from '...'` e `require('...')`).

**Alternativa considerada**: Tree-sitter para todas as linguagens. Rejeitado porque adiciona dep externa pesada e o ganho de precisão não é necessário para extração de imports.

### D3: Dois estágios de resolução (nome → path)

1. **Coleta**: Cada parser extrai nomes/identificadores de import
2. **Resolução**: O resolver mapeia nomes para caminhos usando o dirmap como índice + search paths configuráveis

Separação necessária porque Delphi usa nomes curtos de unit (ex: `Clientes` → `Model/Clientes.pas`) que requerem search paths. Python usa qualified names que mapeiam direto. JS/TS usa paths relativos ou aliases.

### D4: Grafo como dict serializável

O grafo é representado como `dict` com chaves `nodes` (lista de entries com fan-in/fan-out) e `edges` (lista de pares origem→destino). Sem classes complexas — simples de serializar e consultar.

**Alternativa considerada**: networkx. Rejeitado por adicionar dep externa para um caso simples (grafo dirigido sem pesos).

### D5: Imports não resolvidos como referências pendentes

Imports que não podem ser resolvidos para um arquivo do dirmap ficam marcados como `unresolved: true`. Isso é esperado para imports de stdlib (Python `os`, `sys`), third-party (Delphi VCL, npm packages) e units em paths não configurados.

## Risks / Trade-offs

- **[Regex frágil para Delphi multi-linha]** → Mitigar com testes extensivos contra o codebase real (TRUNK). Regex cobre 99% dos casos; o resto fica como `unresolved`.
- **[Search paths Delphi mal configurados]** → Mitigar com defaults sensatos e mensagem clara quando muitos imports ficam unresolved.
- **[Performance em 52K arquivos]** → Mitigar com lazy reading (só lê arquivos de linguagens suportadas) e profile após primeira execução real.
- **[Imports dinâmicos JS/TS]** → Mitigar marcando como `kind: "dynamic"` — detecção best-effort, não exaustiva.
