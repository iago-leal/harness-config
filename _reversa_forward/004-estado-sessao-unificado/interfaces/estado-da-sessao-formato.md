# Contrato: formato do arquivo `.harness/estado-da-sessao.md`

> Tipo: arquivo (contrato entre `cmd encerrar-sessao` e `cmd resume`, e entre sessões/harnesses).
> Fonte única e canônica do estado de sessão. Versionado em git.

## Estrutura

```
---
commit: <SHA-1, 40 hex>          # âncora git do fechamento da sessão
feature: <string>                # feature ativa
start_time: <ISO 8601 UTC>       # início da sessão corrente
status: active | inactive
---

## O que foi feito
- ...

## Próximos passos
- ...

## Pendências / bloqueios
- ...

## Ponteiros
- ...
```

## Regras do contrato

1. **Header-máquina** = front-matter YAML delimitado por `---`. Campos `commit`, `feature`, `start_time`, `status` são obrigatórios. Parse com `pyyaml`; validação com `pydantic` (reusa a validação SHA-1 de `commit`).
2. **Corpo** = Markdown livre em seções `##`. As quatro seções acima são o esqueleto da narrativa; ausência de uma seção é tolerada (narrativa parcial é válida).
3. **Round-trip**: `parse(render(state)) == state` para o header-máquina; o corpo é preservado verbatim no que toca à narrativa estruturada.
4. **Ausente vs malformado** (RN-N4):
   - Arquivo ausente → não é erro; `cmd resume` cria sessão nova.
   - Arquivo presente com front-matter inválido/ausente → erro nomeado, exit ≠ 0 (não degrada para "sem sessão").
5. **Escrita atômica** (tempfile + rename), UTF-8 sem BOM.
6. **Autoria**: o corpo (narrativa) é escrito pelo agente; o header-máquina é selado por `cmd encerrar-sessao` via `GitPort`. A CLI não inventa prosa.

## Teto de tamanho

Manter a narrativa enxuta: o conteúdo reinjetado no Claude respeita 10.000 caracteres (ver `interfaces/reinjecao-por-harness.md`). Sob estouro, priorizar `## Próximos passos` > `## Pendências` > `## O que foi feito`.
