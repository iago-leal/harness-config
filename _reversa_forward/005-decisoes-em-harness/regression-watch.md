# Regression-watch: feature `005-decisoes-em-harness`

> Itens que precisam continuar verdadeiros nas próximas extrações reversas.
> Gerado em 2026-06-23 pelo `/reversa-coding`.

## Watch items

| ID | Origem (arquivo, seção) | Regra esperada após a mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|-------------------------------|---------------------|-------------------|
| W001 | `code-analysis.md#2.4` · RN-N1 | Os artefatos de decisão vivem em `.harness/decisoes/` (fichas + `_cabecalho.md`) e `.harness/microdecisoes.md` | presença | Ressurgir `decisoes/` ou `microdecisoes.md` na raiz do repo |
| W002 | `architecture.md` · RN-N2 | CLI (`main.py`) e MCP (`server.py`) leem os caminhos de `load_config().decisions` — sem literal chumbado | ausência | Reaparecer `"decisoes"` / `"microdecisoes.md"` chumbado em `main.py` ou `server.py` |
| W003 | `config.py` · D-01/B | `load_config` é funcional (imports `toml` e `FileSystemPort` presentes) | presença | `NameError`/`UnboundLocalError` ao rodar `./harness decisions`, `install-prompt` ou o tool MCP |
| W004 | `code-analysis.md#2.4` | `./harness decisions` valida o grafo com zero erros e regenera o índice idêntico (mesmos IDs e backlinks) | redação | Diferença semântica no índice ou erro de integridade após reextração |

## Observações (sem peso de regressão)

- **cwd-dependência (🟡):** a seção `[decisions]` do `harness-core/harness.toml` só é lida quando o cwd é `harness-core/`. O wrapper `./harness` roda da raiz do repo (sem `harness.toml` lá), então valem os defaults do `config.py` — que apontam para `.harness/` relativo à raiz. Correto na invocação real (hook `Stop` + `./harness`), mas o override via toml não tem efeito a partir da raiz.
- **Bug latente pré-existente (🔴, fora do escopo):** `json` não é importado em `harness-core/src/main.py`; `resolve_format_target` estoura `NameError` se o `format` for chamado com payload no stdin. Não tocado pela 005; corrigir à parte.

## Histórico de re-extrações

_(vazio — será preenchido pelo agente reverso quando `/reversa` rodar de novo)_

## Arquivadas

_(vazio)_
