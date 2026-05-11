## Why

O sistema legado Delphi da empresa não se descreve — não existe índice de arquivos, dependências ou impacto de mudança. Novatos levam semanas pra entender o codebase, LLMs ficam cegos sem contexto massivo, e atualizar uma biblioteca compartilhada é um risco calculado por instinto. O Dirmap é o Passo 1 do CodeMap: construir o índice físico que torna o codebase consultável.

## What Changes

- Novo CLI `codemap` com subcomandos `dirmap`, `query`, `repl` e `version`
- Walker de árvore de diretórios que coleta metadados (path, extensão, tamanho, linguagem)
- Parser de `.gitignore` e `.codemap-ignore` para exclusão de diretórios/arquivos
- Classificador de arquivos por extensão → linguagem (genérico, com customização via config)
- Serialização para JSON com meta, summary (por extensão e linguagem) e tree
- Subcomando `query` com filtros estruturados (ext, lang, path, type, count, summary)
- REPL interativo para consultas humanas
- Registry de comandos com help dinâmico (auto-descoberta)
- Config centralizada via `.codemap.yml` com hierarquia de 4 camadas (defaults → global → projeto → CLI)
- Validação de dependências no entrypoint (fail fast)
- Empacotamento via `pyproject.toml` com `pip install -e .`

## Capabilities

### New Capabilities

- `dirmap-walker`: Caminhamento de árvore de diretórios com respeito a regras de exclusão (.gitignore, .codemap-ignore, max_depth, symlinks)
- `dirmap-classifier`: Classificação de arquivos por extensão em linguagens, com suporte a extensões customizadas via config
- `dirmap-serializer`: Serialização da coleta de metadados em JSON com meta, summary e tree
- `dirmap-query`: Motor de consultas estruturadas via CLI (pipe-friendly) e REPL interativo
- `codemap-cli`: Registry de comandos com auto-descoberta, help dinâmico e validação de dependências
- `codemap-config`: Config centralizada via `.codemap.yml` com merge de 4 camadas

### Modified Capabilities

(nenhuma — este é o primeiro deliverable do projeto)

## Impact

- **Novo código:** pacote `codemap/` com 6 módulos + subpacote `dirmap/` com 5 módulos
- **Dependências:** pyyaml (única dependência externa)
- **Python:** requer >=3.11
- **Instalação:** `pip install -e .` disponibiliza o comando `codemap` no PATH
- **Downstream:** os próximos passos (Métricas, `uses`, AST, Grafo) consomem o JSON gerado pelo Dirmap
