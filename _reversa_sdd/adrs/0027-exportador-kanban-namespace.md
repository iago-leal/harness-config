# ADR 0027: Exportador kanban com posse por namespace — board determinístico, manuais como canal de demandas

- **Status:** Aceito
- **Data:** 2026-08-11 (feature 027-exportador-kanban, MD-0020; não commitada na data desta extração)
- **Contexto Técnico:** `core/progress/kanban.py` (único módulo do core que conhece o schema do fork do vscode-kanban); `Medicao` ganha `board_habilitado`/`demandas` e granularidade de ações (`AcaoProgresso` com IDs reais `T00N`, `Demanda`); quinta fonte `_medir_demandas` no `service.py`; `ProgressKanbanSection(enabled=False, file=".vscode/vscode-kanban.json")` aninhada em `ProgressSection`; board escrito só no modo padrão do subcomando `progress`. Core 2.4.0 → 2.5.0.
- **Escala de Confiança:** 🟢 CONFIRMADO (TDD, 20 testes novos, suíte 372; smoke em arquivo integral; conferência visual no fork pendente do mantenedor — ver regression-watch da 027).
- **Decisões relacionadas:** MD-0020 (`refina MD-0019`); ADR 0026 (a `Medicao` de origem); domain.md §2.25 (RN-N53/N54/N55).

## Contexto e Problema

O mantenedor refatorou a interface do seu fork do vscode-kanban e quis a maquinaria dele como visualização do progresso do harness. No clarify, o escopo cresceu numa direção decisiva: o board não seria só saída — cards manuais criados à mão apresentam **demandas novas** sem passar antes pelo processo, e o agente harness deve conduzi-las pelo ciclo forward. O board precisava, portanto, conviver com duas populações de cards (gerados e manuais) sem que uma corrompesse a outra, num arquivo que o fork **executa** parcialmente (`vscode-kanban.js`, `workspaces.ts:769`) — risco de segurança concreto.

## Decisão

**Posse por namespace.** Card `category == "harness"` pertence ao exportador: recomputado do zero a cada exportação, com ids estáveis derivados dos ids reais (`hns:<feature>`, `hns:<feature>:<T00N>`, `hns:alerta:<origem>`; ordinais rejeitados por instabilidade a reordenação). Qualquer outro card é manual: preservado byte a byte, na coluna onde estiver; manuais fora de `done` viram `Medicao.demandas`, a fila de entrada do mantenedor. Mapeamento fixo (`[ ]`→todo, `[X]`→done, ativa→in-progress, pausadas→todo, alertas→todo/bug prio 9/5); `testing` nunca recebe card gerenciado; concluídas não geram card (cresceriam sem limite).

**Determinismo integral.** Nenhum caminho consulta a hora corrente: `creation_time` deriva do primeiro `ts` da ação no `progress.jsonl` com fallback no `started-at`. Mesmo estado + mesmos manuais → bytes idênticos (idempotência pinada por teste); o board versionado só gera diff quando o estado muda, coerente com o ADR 0026.

**Fluxo unidirecional e segurança.** A fonte de verdade é o `actions.md`; cards gerenciados do arquivo jamais são fonte de progresso (edição manual neles é descartada na exportação seguinte). O board só é lido com `[progress.kanban] enabled = true` e só pelos manuais; só é escrito no modo padrão, atômico, write-only-when-changed; board ilegível herda a falha real (exit 2 sem regravar nada). O exportador escreve unicamente o `.json` configurado e **jamais** cria ou toca `.vscode/vscode-kanban.js`.

## Alternativas Consideradas

- **Board como fonte bidirecional (arrastar card move o `actions.md`):** descartado — inverteria a fonte de verdade e criaria conflito de merge entre duas escritas; a leitura restrita aos manuais dá o canal de entrada sem o risco.
- **Ids ordinais (`hns:1`, `hns:2`):** descartado (DESCARTADO-e da MD-0020) — reordenação de ações mudaria a identidade dos cards e quebraria o determinismo.
- **`creation_time = now()` na primeira aparição:** descartado — única fonte de não-determinismo restante; o primeiro `ts` do `progress.jsonl` dá a mesma semântica sem relógio.
- **Cards para features concluídas:** descartado — cresceriam sem limite; a contagem na `Medicao` basta.
- **Board fora do opt-in (sempre ativo):** descartado — nem todo projeto da base usa o fork; sem opt-in, nada sob `.vscode/` é criado.

## Consequências

- **Positivas:**
  - O mantenedor ganha visualização viva no fork e um canal de entrada de demandas que o agente trata como fila (`Medicao.demandas`).
  - Schema do fork confinado a um módulo (`kanban.py`): mudança de formato tem raio de explosão de um arquivo.
  - Segurança codificada: impossível o exportador criar o arquivo executável do fork.
- **Negativas / em aberto:**
  - Conferência visual no fork pendente (ids não numéricos, campos opcionais ausentes, efeito de mover card gerenciado na UI) — 🟡 no regression-watch da 027.
  - O board como canal de demandas é convenção operacional: nada automatiza a condução das demandas pelo ciclo forward; depende do agente ler `Medicao.demandas`.
