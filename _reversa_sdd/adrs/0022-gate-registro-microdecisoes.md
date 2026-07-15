# ADR 0022: Gate de registro obrigatório de microdecisões com enforcement híbrido por borda

- **Status:** Aceito
- **Data:** 2026-07-15 (feature 022-hook-registro-decisoes, MD-0015)
- **Contexto Técnico:** Novo `src/core/decisions/gate.py` (`evaluate_registration_gate`, `compute_fingerprint`, `GateVerdict`); novo método `GitPort.list_changed_paths_since` (+ implementação no `SubprocessGitAdapter`); 3º portão em `src/core/session/close_flow.py` (`render_decisao_pendente_marker`, `conduct_decisao_pendente`, parâmetro `sem_decisao` em `SessionCloseFlow.run`); flag `--gate` no subcomando `decisions` e `--sem-decisao` no `cmd` (`src/main.py`); `gate_evaluator` injetável no `AntigravityHookBridge`; campos opcionais `gate_lembrete_fingerprint`/`gate_encerramento_fingerprint` no `SessionState` (front-matter, serializer); flag `decisions.require_registration` (default `True`); `ClaudeProfile.hooks_block()` passa o Stop de `harness decisions` para `harness decisions --gate`.
- **Escala de Confiança:** 🟢 CONFIRMADO (código as-built; suíte 293 verde no fechamento da feature; smoke real A–F — bloqueio, ficha libera, escape com rastro, anti-loop, JSON único no `--gate`, advisory `{}`).
- **Decisões relacionadas:** MD-0015 (estende MD-0005, relaciona MD-0014); ADR 0001 (particionamento das microdecisões); ADR 0016 (RN-N26, Stop do Antigravity nunca bloqueia); ADR 0019 (RN-N34, pré-check de pendência — o estado de sessão como exceção consagrada); domain.md §2.20 (RN-N43..N46).

## Contexto e Problema

O sistema de microdecisões (`MD-NNNN.md` + índice derivado) só funciona se as decisões forem de fato registradas — e elas eram puladas em algumas sessões: o trabalho terminava, a sessão fechava e o "porquê" evaporava. Para um mantenedor intermitente, cada decisão não registrada é contexto perdido na retomada seguinte. Faltava um mecanismo que **impusesse** o registro sem travar o fluxo do agente.

Duas restrições de plataforma moldaram o desenho: (1) no hook `Stop` do Claude, o único canal que alcança o **modelo** é `{"decision": "block", "reason": ...}` — stdout com exit 0 chega só ao usuário, não é reinjetado no contexto; logo, um "lembrete não-bloqueante" para o agente só existe como *soft-block* controlado. (2) No Antigravity, RN-N26 proíbe bloquear o Stop.

## Decisão

**Avaliação pura no domínio, política nas bordas.** `evaluate_registration_gate` (em `core/decisions/gate.py`) decide *se* há pendência a partir de sinal físico exclusivamente: universo = diff da âncora (`list_changed_paths_since` — enxerga o trabalho já commitado, indispensável porque o pré-check da 019 força commit antes do fechamento) ∪ working tree sujo; excluídos o arquivo de estado, o índice e o cabeçalho; pendente = há mudanças e nenhuma ficha `MD-*.md` tocada. Sem filtro por tipo de arquivo — repositórios documentais (contratos, documentos) contam tanto quanto código, por decisão explícita do clarify.

Três bordas aplicam três políticas sobre o mesmo veredito:

1. **`encerrar-sessao` (garantia dura):** 3º portão da família `COMMIT`/`NARRATIVA_PENDENTE` — aborta (marker `DECISAO_PENDENTE`, protocolo abortar-e-reexecutar) até o agente registrar a ficha ou declarar `--sem-decisao`, que grava rastro auditável na narrativa (não é o core inventando narrativa, RN-N3). Anti-loop: o fingerprint do estado de pendência é persistido no estado de sessão; o mesmo estado nunca bloqueia duas vezes (na reexecução, avisa "não sanada" e libera).
2. **Hook Stop do Claude (`decisions --gate`):** soft-block JSON único por estado de pendência; informativos migram para stderr, stdout reservado ao JSON do hook, exit 0 sempre; sob a flag, nem erros de integridade do grafo derrubam o turno. Sem a flag, o comando permanece byte-idêntico (uso manual e git post-merge, MD-0006).
3. **Antigravity (advisory):** pendência vira aviso em stderr via `gate_evaluator` injetado na borda; `{}` intocado, nunca bloqueia (RN-N26 preservada).

O anti-loop persiste **no estado de sessão** (campos opcionais no front-matter, zerados no fechamento) porque ele é a exceção consagrada do pré-check de pendência (RN-N34): qualquer scratch novo sob `.harness/` viraria `COMMIT_PENDENTE` perpétuo ou exigiria entrada de `.gitignore` em toda a base instalada (lição do T7). Fail-open barulhento: âncora ilegível → `pendente=False` + aviso em stderr; o gate nunca trava o agente por erro interno.

## Alternativas Consideradas

- **Scratch `.harness/decision-gate.json` para o anti-loop:** descartado — vira pendência de commit ou nova entrada de gitignore em toda a base instalada.
- **Lembrete via `systemMessage`/stdout puro no Stop:** descartado — não alcança o modelo, só o usuário.
- **Detecção semântica ("o diff parece decisão?") ou parse do transcript:** descartado — não-determinístico, viola o princípio de sinal físico verificável.
- **Filtrar o sinal a código-fonte:** descartado — o mantenedor tem repositórios documentais cujas alterações são exatamente as decisões a registrar.
- **Bloquear também o Stop do Antigravity:** descartado — RN-N26 proíbe; advisory.
- **Exit 2 no soft-block:** descartado — ambíguo com falha real; o bloqueio é só pelo JSON, exit 0 sempre.

## Consequências

- **Positivas:**
  - Nenhuma sessão com trabalho substantivo termina sem ficha ou declaração explícita — o grafo de decisões deixa de ter buracos silenciosos.
  - Core agnóstico preservado (RN-N5): o módulo de avaliação não conhece harness; cada borda escolhe a pressão adequada ao seu contrato.
  - Retrocompatível: estados de sessão pré-022 parseiam sem os campos novos; o arquivo permanece byte-compatível enquanto o gate não é acionado; `require_registration` ausente herda `True` e é desativável por projeto.
- **Negativas / em aberto:**
  - O fingerprint fino do lembrete rearmava a cada arquivo tocado — ruído corrigido pela feature 023 (ADR 0023).
  - Gemini ficou fora desta iteração (decisão de escopo do clarify).
  - Propagação à base instalada depende de `upgrade`/`migrate` nos projetos-alvo (pendente à data deste ADR).
