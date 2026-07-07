---
commit: a34eaca371cdba1f8d2b8c88694d40a02335f4d3
feature: saneamento do T7 (cache de sync com fonte única em layout.py)
start_time: "2026-07-06T18:06:05.079534+00:00"
status: inactive
---

## O que foi feito

- **Sessão de desvio: o trabalho real saiu do repo `harness` e ocorreu no `claude-config` (`~/.claude`).** O HEAD do `harness` **não mudou** (segue em `a34eaca`); esta sessão não tocou o core nem os artefatos do Reversa.
- **Abertura via `/clarificar` da feature "estrutura de pastas advisory".** Destilado por PCCP: o Harness sugerir organização de pastas _dentro de um projeto individual_, em modo **advisory** (só relata, nunca move — compatível com a regra não-negociável de não tocar o legado). Escopo confirmado como extensão do Princípio 5.6 (tornar a erosão estrutural barulhenta), não como decisor de layout. **A feature ficou PAUSADA na clarificação** (ver Próximos passos).
- **Correção da própria skill `/clarificar` (PCCP), no `claude-config`.** Duas mudanças, detalhadas nos itens seguintes.
- **Inversão Queixa↔Demanda desfeita.** O `pccp.md`/`clarificar.md` importavam do Método Clínico Centrado na Pessoa os rótulos trocados; convenção corrigida em todo o texto — **Queixa** = apresentação de superfície (o que se pede), **Demanda** = problema de fundo (o que se quer resolver). `grep` confirmou zero inversão parcial.
- **Contrato de emissão de decisões (§⑩).** Antes dizia só "registre como `MD-NNNN.md`"; agora fixa o miolo invariante (`# MD-NNNN —` + 4 seções `D/PORQUÊ/DESCARTADO/ESTADO`) e **detecta o envelope por consumidor do projeto**: harness → frontmatter YAML + `harness decisions`; claude-config → blockquote + `bin/gerar-index-decisoes.sh`; fallback → espelhar o vizinho.
- **Registro:** `~/.claude/decisoes/MD-0019.md` (refina MD-0011, relaciona MD-0014); índice regenerado; commit `c7e120f` no `claude-config`, já em `origin/main`.

## Próximos passos

- **Retomar a feature "estrutura de pastas advisory"** (repo `harness`): a clarificação parou com alvo=projeto individual, natureza=advisory, **gatilho=no resume** e **saída=artefato em `.harness/`** já escolhidos. Falta **travar o gatilho fino** (limiar exato do "está crescendo") e **os sinais** (arquivo >400L, função >50L, contagem por pasta, profundidade, ausência de camadas) para virar um `reversa-requirements`.
- **Descontinuação de `sync`/`upgrade`/oferta-014:** feature futura não numerada (022+) — não reabrir sem necessidade concreta.
- **`harness migrate` real:** ainda não executado nos ~17 projetos com layout copiado; ação deliberada do mantenedor, execução manual (`!`).
- **Mini-site (`.reversa/documentation/`):** páginas de `sync-check` ainda citam o literal antigo do cache; regenerar via `/reversa-docs` na próxima rodada visual.
- **G-11:** artefatos de `_reversa_sdd/migration/` seguem não auditados — só se o Time de Migração voltar a ser usado.

## Pendências / bloqueios

- Sem bloqueios. A pendência do `~/.claude` apontada na sessão anterior foi resolvida aqui (commit `c7e120f`, pushed).
- Nenhuma nota do Obsidian a atualizar: não há nota-projeto dedicada à skill `clarificar`/`claude-config` no vault (a "Memória longitudinal do harness" aponta para `~/.agent-memory` e trata do projeto `harness`, não desta correção).

## Ponteiros

- Trabalho desta sessão (outro repo): `~/.claude/docs/pccp.md` (§①, §④.1-4.2, §⑤/G4, §⑩), `~/.claude/commands/clarificar.md`, `~/.claude/decisoes/MD-0019.md`; commit `c7e120f`.
- Feature pausada (este repo): decisões de escopo capturadas nas respostas do `/clarificar` — ainda sem artefato em `_reversa_forward/` (não chegou a `requirements`).
