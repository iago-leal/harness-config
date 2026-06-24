# ADR 0009: Abandono do espelho `claude-config/` e centralização de estado e decisões em `.harness/`

- **Status:** Aceito
- **Data:** 2026-06-23
- **Contexto Técnico:** Repositório (estrutura) — commits `5624f78` (purge do legado) e `c548223` (move para `.harness/`)
- **Escala de Confiança:** 🟢 CONFIRMADO (arqueologia Git + estado do repositório)
- **Decisões relacionadas:** MD-0001, MD-0002, MD-0004
- **Revisado parcialmente por:** MD-0005 / ADR 0013 (feature 006) — ver nota de revisão abaixo

## Contexto e Problema

O repositório carregava um espelho `claude-config/` (clonado da config global do Claude Desktop) e referências a um `harness-config/` que **nunca existiu** neste repositório. Em torno deles, o `harness-core` mantinha um modo _shadow_ de bootstrap (CLI Python rodando em segundo plano enquanto ganchos legados rodavam em primeiro plano), um `test_parity` para comparar os dois caminhos e um `LegacyDecisionImporter`. O problema: o legado de referência não tinha oráculo real — o _shadow_ comparava contra algo inexistente e o `test_parity` era **verde-falso** (cenografia que só somava caminhos de falha). Em paralelo, o estado de sessão e as microdecisões viviam acoplados ao harness Claude (`.claude/ESTADO-DA-SESSAO.md`, `decisoes/` na raiz com o sabor da config do Claude), o que os deixaria órfãos se o mantenedor trocasse de agente.

## Decisão

Abandonar definitivamente o espelho `claude-config/` (e o `harness-config/` fantasma) e tornar o `harness-core` a **referência canônica única**, com estado e decisões centralizados num diretório **neutro a harness**, `.harness/`:

> 🟢 **Nota de revisão (MD-0005 / ADR 0013, feature 006):** "referência canônica única" deve ser lida como **canonicidade PER-PROJETO** — `.harness/` é a fonte de verdade _dentro de cada repositório_, não um **substituto global de `~/.claude`**. O MD-0004 chegou a registrar a intenção de tornar o harness-core "substituto da config global"; o MD-0005 reverteu essa premissa: o harness-core é módulo per-projeto autocontido, com footprint global zero (instalar/executar escreve só dentro do repo, nunca em `~/.claude` ou `~/.agent-memory`). A aposentadoria do sync cross-harness (MD-0004) permanece válida; revista é só a canonicidade global. Ver ADR 0013.

1. **Purga (commit `5624f78`):** removidos o modo _shadow_/coexistência do `BootstrapService`, as flags `--shadow`/`--active`, o `test_parity`, o `LegacyDecisionImporter` e o hook shell `carregar-estado-sessao.sh`; `claude-config/` e `harness-config/` saem do `.gitignore` e do versionamento. Os ganchos vivos do agente passam a apontar direto para a CLI Python via `./harness` (`SessionStart`→`cmd resume`, `PostToolUse`→`format`, `Stop`→`decisions`).
2. **Centralização (commits da feature 004/005):** estado de sessão em `.harness/estado-da-sessao.md`; fichas de decisão em `.harness/decisoes/`; índice em `.harness/microdecisoes.md`. `.harness/` é ASCII kebab, neutro, e agrupa os artefatos duráveis de sessão/decisão num só lugar versionável.

## Alternativas Consideradas

- **Migração faseada com coexistência _shadow_ até a CLI replicar o legado:** descartada — sem legado real e sem oráculo, é custo de manutenção sem retorno (dois caminhos de falha por uma paridade fictícia). Ver MD-0001.
- **Manter estado/decisões sob `.claude/`:** descartada — acopla o core ao harness Claude e o deixa órfão na troca de agente. `.harness/` é neutro e durável (baixo acoplamento, longevidade). Ver MD-0002.
- **Apagar também o conteúdo de memória junto com o mecanismo (cross-harness):** não feito — o conteúdo é dado durável; só o mecanismo de sincronização cross-harness foi removido (MD-0004), preservando o conteúdo para migração futura sob o harness-core.

## Consequências

- **Positivas:**
  - Um core _standalone_, mais simples de manter e retomar após pausa (sem caminhos _shadow_ nem importadores legados).
  - Estado e decisões neutros a harness, sobreviventes à troca de agente.
  - Eliminação de testes verde-falsos que mascaravam ausência de cobertura real.
- **Negativas:**
  - Remoção destrutiva e irreversível (recuperável apenas via histórico Git — `claude-config` ignorado a partir de `00b1719`).
  - **Regressão temporária aceita (MD-0001):** o corte dos hooks deixou o `SessionStart` sem reinjetar o estado da última sessão até a feature 004 fechar a lacuna (ver ADR 0010).
