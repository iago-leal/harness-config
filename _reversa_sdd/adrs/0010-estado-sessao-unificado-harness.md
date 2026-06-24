# ADR 0010: Estado de sessão unificado em `.harness/estado-da-sessao.md` com narrativa de retomada

* **Status:** Aceito
* **Data:** 2026-06-23 (decidido) / feature 004 (implementado)
* **Contexto Técnico:** Módulos `core/session` e `core/commands` — commit `e1a2f75`
* **Escala de Confiança:** 🟢 CONFIRMADO
* **Decisões relacionadas:** MD-0002 (refina MD-0001)
* **Supera (parcialmente):** ADR 0004 (localização e formato da âncora)

## Contexto e Problema

O corte dos hooks para a CLI (ADR 0009 / MD-0001) deixou uma regressão aceita: o `SessionStart` via `cmd resume` não reinjetava mais o estado da última sessão no contexto — função que o antigo `carregar-estado-sessao.sh` cumpria emitindo `hookSpecificOutput.additionalContext`. Pior, conviviam **duas** fontes de verdade do estado: um `.claude/ESTADO-DA-SESSAO.md` com narrativa rica (versionado) e um `ESTADO-DA-SESSAO.md` pobre na raiz (gerado pela CLI), gerando *drift*. O estado de sessão é conceito da CLI multi-harness, não do Claude.

## Decisão

Unificar o estado num único artefato canônico e versionado, `.harness/estado-da-sessao.md`, neutro a harness, com **um só parser/renderer**:

1. **Formato:** front-matter YAML (header-máquina: `commit`-âncora, `feature`, `start_time`, `status`) + corpo Markdown em seções (a narrativa).
2. **Modelo:** `SessionState` ganha o value-object `SessionNarrative` — quatro listas (`feito`, `proximos_passos`, `pendencias`, `ponteiros`). Escrita pelo agente; a CLI a carrega e reinjeta, nunca a inventa.
3. **Round-trip:** `load_session`/`save_session` viram `parse`/`render` com a invariante testável `parse(render(x)) == x` (TDD por propriedade). O formato único é a spec executável da sessão.
4. **Comandos pareados:** `cmd resume` reinjeta a narrativa no `SessionStart` e alerta se HEAD divergir da âncora; `cmd encerrar-sessao` é o produtor da narrativa, gravando o commit-âncora do fechamento.
5. **Ausente ≠ malformado:** arquivo ausente é sessão nova normal; arquivo corrompido levanta `MalformedSessionStateError` (falha barulhenta).

## Alternativas Consideradas

* **Dois arquivos por concern (JSON de máquina + MD de narrativa):** descartada — reinstitui as duas fontes de verdade que geraram o *drift* (MD-0002).
* **Persistir nada e derivar tudo (git HEAD + `active-requirements.json`):** descartada — perde o commit-âncora do fechamento (necessário ao alerta de divergência) e acopla o core de sessão ao schema do Reversa.
* **Local na raiz `estado-da-sessao.md`:** preterida — agnóstico, mas polui a raiz e não agrupa futuros artefatos de sessão; `.harness/` os agrupa.
* **Manter em `.claude/ESTADO-DA-SESSAO.md`:** rejeitada pelo mantenedor — acopla ao harness Claude.

## Consequências

* **Positivas:**
  * Uma só fonte de verdade, com um só parser — fim do *drift* entre formatos.
  * Memória de retomada estruturada e versionada, reinjetada no boot.
  * Invariante de round-trip dá lastro de teste (propriedade `parse∘render`).
* **Negativas:**
  * O round-trip precisa cobrir coerções (datas ISO, naive→UTC) sob pena de quebrar a invariante.
  * 🟡 **Dívida latente (T2):** o driver MCP (`server.py`) ainda aponta para `ESTADO-DA-SESSAO.md` na raiz — não migrado junto, diverge da CLI. Bug documentado, não corrigido.
