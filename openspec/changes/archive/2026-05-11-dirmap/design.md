## Context

Projeto CodeMap em estado greenfield (zero código Python). O Dirmap é o Passo 1 do roadmap — construir um índice físico consultável de codebases. O laboratório inicial é a Hadsteca (repo Delphi), mas a ferramenta deve ser genérica multi-linguagem. Stack definida: Python >=3.11, JSON como storage, CLI standalone.

## Goals / Non-Goals

**Goals:**

- Caminhar árvore de diretórios e coletar metadados de cada arquivo
- Gerar JSON estruturado com meta, summary e tree
- Permitir consulta via CLI (pipe-friendly pra LLMs) e REPL (pra humanos)
- Help dinâmico via registry de auto-descoberta
- Config centralizada com hierarquia de 4 camadas
- Fail fast na validação de dependências

**Non-Goals:**

- Leitura de conteúdo de arquivos (somente metadados)
- Busca semântica/embeddings (ChromaDB entra no Passo 4)
- Suporte a MCP server (futuro, não esta change)
- Análise de dependências entre units (Passo 3)
- Parser AST (Passo 4)

## Decisions

### D1: Flat Walker com pathlib

**Escolha:** `pathlib.rglob()` com filtro customizado.

**Alternativas:**
- `pathspec` (parser robusto de .gitignore) — rejeitado por adicionar dependência; parser simples cobre 95% dos casos
- `ripgrep` subprocess — rejeitado por depender de ferramenta externa instalada; overkill pra metadados

**Racional:** Zero dependências extras, stdlib completa, evolui naturalmente. Se edge cases de .gitignore surgirem, `pathspec` entra como dependência opcional.

### D2: CLI com argparse + Registry de auto-descoberta

**Escolha:** argparse (stdlib) com decorator `@registry.register()`.

**Alternativas:**
- `click` — rejeitado por ser dependência externa; argparse resolve
- Help estático — rejeitado por ficar defasado conforme comandos crescem

**Racional:** Help dinâmico sem dependência. Novo módulo registra seu comando e já aparece no help. Zero manutenção manual.

### D3: JSON como formato único de output

**Escolha:** JSON no disco por default, `--stdout` como flag.

**Alternativas:**
- YAML — rejeitado por ambiguidade (tipos, multiline)
- Markdown — rejeitado por ser difícil de consumir programaticamente

**Racional:** JSON é nativo, portável, consumível por LLMs e scripts. Summary pré-computado evita processamento downstream.

### D4: Config via `.codemap.yml` com merge de 4 camadas

**Escolha:** YAML lido e mergeado: defaults → global (`~/.codemap/config.yml`) → projeto (`.codemap.yml`) → CLI flags.

**Racional:** Centraliza toda config num lugar. Evita poluição de flags CLI. Evolui junto com os próximos passos (regex patterns, max_edges, etc.).

### D5: pytest com tmp_path

**Escolha:** pytest + `tmp_path` nativo, sem fixtures em disco.

**Racional:** Mais limpo, sem estado residual, assertions legíveis, parametrize, ecossistema de plugins.

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Parser simples de .gitignore não cobre 100% dos edge cases (negação `!`, escapes) | `pathspec` entra como dependência opcional se necessário |
| Repositórios muito grandes (>100k arquivos) podem ser lentos | `max_depth` limita escopo; paralelização é possível no futuro |
| Extensões duplicadas entre linguagens (ex: `.h` = C ou C++) | Primeiro match vence; custom_extensions no config permite override |
| Encoding de paths com acentos/unicode | `pathlib` no Python 3 lida nativamente |

## Open Questions

(nenhuma — design travado após brainstorm)
