# Brainstorm — Sessão 01

**Data:** 2026-05-11
**Participantes:** .dobrador (Hadston Nunes), Sky

---

## O que é o CodeMap

Indexador de codebases multi-linguagem que constrói um índice consultável de arquivos, dependências, classes e cadeias de impacto.

**Nome principal:** CodeMap
**Convenção de alias:** `[Repo]Atlas` (ex: HadstecaAtlas, DelphiAtlas, FuturaAtlas)

---

## Motivações (Dores)

### 1. Onboarding (humanos e LLMs)
- Novatos levam semanas pra entender o codebase
- LLMs precisam de contexto massivo pra serem úteis no Delphi
- Sem índice, o LLM é cego

### 2. Navegação/Estudo (plenos/seniors)
- "Onde fica a regra de X?" → grep + abertura de 10 arquivos
- "Quem usa essa unit?" → não tem resposta rápida
- Conhecimento fica nas cabeças, não no sistema

### 3. Impacto de Mudança (arquiteto)
- Atualiza a lib → quebra 3 projetos que ninguém sabia que dependiam
- Refactoring sem rede de segurança → medo de mudar
- Não existe "o que essa classe afeta?"

**Raiz comum:** "O sistema não se descreve"

---

## Contexto da Empresa

- Sistema legado Delphi gigante
- Bibliotecas compartilhadas + vários projetos dependentes
- Arquiteto com dificuldade em estimar impacto de mudanças
- Stack: Delphi, Java, Kotlin, Flutter
- Laboratório inicial: Hadsteca (repo GitHub próprio)

---

## Arquitetura — 3 Camadas

```
┌─────────────────────────────────────────┐
│           QUERY LAYER                   │  CLI / MCP — faz perguntas
├─────────────────────────────────────────┤
│           INDEX LAYER                   │  Armazena o que foi descoberto
├─────────────────────────────────────────┤
│           SCAN LAYER                    │  Descobre o codebase
└─────────────────────────────────────────┘
```

A Query Layer existe desde o Passo 1. Quanto mais passos, mais rica a consulta.

---

## Roadmap Detalhado

### Passo 1 — Dirmap (Estrutura Física)

- Caminha árvore de diretórios, identifica tipos de arquivo
- Entende o contexto Delphi: `.dpr` (entry point), `.dpk` (pacote), `.pas` (unit), `.dfm` (form)
- Zero dependências (só `pathlib`)

| Tipo | Exemplo consulta | Resposta |
|------|-----------------|----------|
| Raw | "quais .dpr existem?" | Lista de entry points |
| Raw | "quantas units em src/Model?" | Contagem + lista |
| Semântica | "quais são os entry points?" | .dpr mapeados |
| Semântica | "quais units têm form associado?" | .pas com .dfm |

### Passo 2 — Métricas

- Conta linhas, detecta órfãos, duplicatas, vazios
- Hash de arquivos pra detectar duplicatas

| Tipo | Exemplo consulta | Resposta |
|------|-----------------|----------|
| Raw | "qual a unit maior?" | Ranking por linhas |
| Semântica | "quais units são candidatas a remoção?" | Vazias + sem referência |

### Passo 3 — Extração de `uses` (Dependências)

- Regex: `uses\s+([\w,\s]+);` — separa interface de implementation
- Mapa de dependência entre units

| Tipo | Exemplo consulta | Resposta |
|------|-----------------|----------|
| Raw | "quais units a unit X usa?" | Lista de dependências |
| Raw | "quem inclui unit Y?" | Lista reversa |
| Semântica | "se eu remover unit X, o que quebra?" | Dependentes diretos |
| Semântica | "qual a chain de X até o entry point?" | Caminho no grafo |

### Passo 4 — Parser AST (Semântica)

- Extrai classes, métodos, propriedades, herança, events
- Base: DelphiAST ou parser próprio
- Identifica padrões: `class(TForm)`, `class(TDataModule)`

| Tipo | Exemplo consulta | Resposta |
|------|-----------------|----------|
| Raw | "quais classes existem na unit X?" | Lista estruturada |
| Semântica | "quem herda de TBaseModel?" | Hierarquia |
| Semântica | "onde está a regra de cálculo de ICMS?" | Busca por padrão |
| Semântica | "quais forms existem?" | Herda de TForm |

### Passo 5 — Grafo de Impacto

- Grafo direcionado (networkx ou similar)
- Impacto direto + indireto
- Diagramas Mermaid

| Tipo | Exemplo consulta | Resposta |
|------|-----------------|----------|
| Raw | "draw o grafo do projeto X" | Diagrama Mermaid |
| Semântica | "impacto de mudar a classe X?" | Classes + arquivos afetados |
| Semântica | "quais libs são mais arriscadas?" | Ranking por acoplamento |
| Semântica | "quais módulos são independentes?" | Componentes desconectados |

---

## Decisões

| Decisão | Escolha | Motivo |
|---------|---------|--------|
| Linguagem principal | PT-BR | Comunidade destino é brasileira |
| Output primário | Markdown | Nativo em GitHub/Obsidian |
| Integração | CLI + MCP | Uso humano + agentes de IA |
| Primeira linguagem | Python | Laboratório Hadsteca |
| Storage | JSON inicial | Simplicidade, evolui pra SQLite se necessário |
| Approach | Incremental | Começar simples, mostrar resultado aos poucos |

---

## Comparação com Mercado

| Ferramenta | Similar | Diferencial do CodeMap |
|------------|---------|----------------------|
| `tree` (CLI) | Estrutura | Genérico, não entende Delphi |
| `cloc` | Métricas | Genérico |
| DelphiAST | Parser completo | Precisa de wrapping |
| Understand (SciTools) | Tudo | Comercial, pesado |
| CodeQL (GitHub) | Queries complexas | Curva de aprendizado alta |
| SonarQube | Métricas | Precisa de infra |
| Doxygen | Documentação | Foco em docs, não mapa |

**Diferencial CodeMap:** Leve, Delphi-aware, saída pensada pra LLMs, CLI + MCP, evolutivo.

---

## Links

- **Repositório:** https://github.com/h4mn/code-map (privado)
- **Linear:** https://linear.app/skybridge/project/codemap-d8146cd515d3
- **Time Linear:** Skybridge
