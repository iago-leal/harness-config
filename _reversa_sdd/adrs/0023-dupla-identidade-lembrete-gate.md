# ADR 0023: Dupla identidade anti-loop do gate — lembrete grosso (1/sessão), portão fino (rearma)

- **Status:** Aceito
- **Data:** 2026-07-15 (feature 023-granularidade-lembrete-gate, MD-0016)
- **Contexto Técnico:** Nova função pura `compute_lembrete_fingerprint(anchor)` e campo `fingerprint_lembrete` no `GateVerdict` (`src/core/decisions/gate.py`); o ramo `decisions --gate` do `main.py` passa a comparar/persistir a identidade grossa no mesmo campo `gate_lembrete_fingerprint` do estado; o 3º portão do `close_flow.py` permanece na identidade fina, agora pinada por teste-guarda (`test_close_flow.py::test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio`). Sem schema novo, sem flag nova, sem migração. Core 2.1.0 → 2.1.1.
- **Escala de Confiança:** 🟢 CONFIRMADO (TDD red→green; suíte 300 verde — 7 testes novos, incluindo o teste-queixa; smoke real A–E 9/9 em repos git descartáveis).
- **Decisões relacionadas:** MD-0016 (estende MD-0015); ADR 0022 (o gate em si); domain.md §2.21 (RN-N47).

## Contexto e Problema

Queixa do mantenedor pós-022: "cada mudança de arquivo está rodando o hook". O diagnóstico descartou a hipótese óbvia — não há hook por-edição no Claude (MD-0014 já o aposentara). O rearme vinha do próprio gate: o lembrete do Stop usava o fingerprint **fino** (`sha1(âncora+HEAD+sujos)`), então cada arquivo tocado mudava o conjunto sujo, mudava a identidade do estado de pendência e rearmava o soft-block — ruidoso a ponto de atrapalhar o trabalho. O gate demonstrou o sintoma ao vivo durante a própria sessão de correção.

A raiz é que o fingerprint fino serve a **dois consumidores com necessidades opostas**: o portão do encerramento PRECISA da finura (trabalho novo sem ficha deve re-bloquear; estado idêntico libera com aviso), enquanto o lembrete do fim de turno precisa de estabilidade (avisar uma vez, não perseguir).

## Decisão

**Dar a cada consumidor a identidade da sua semântica, em vez de "consertar" o fingerprint na origem.** O lembrete do Stop passa a usar a identidade **grossa** `sha1(âncora)` — estável do início ao encerramento da sessão, logo no máximo **um soft-block por sessão** com pendência. O 3º portão mantém a identidade **fina** `sha1(âncora+HEAD+sujos)` — trabalho novo continua rearmando a garantia dura, comportamento agora protegido por teste-guarda. A grossa espelha a definição de pendência que o avaliador já aplica: uma ficha registrada desde a âncora satisfaz a sessão inteira, então "um lembrete por pendência" ≡ "um por sessão".

A política é **fixa no core** (sem flag no toml — YAGNI; configurável depois sem quebrar contrato) e a transição é **autoresolvente**: o valor antigo persistido (fino) nunca coincide com a composição nova (grossa), então há no máximo um lembrete espúrio pós-atualização e o estado converge — sem código de migração.

## Alternativas Consideradas

- **Mudar `compute_fingerprint` globalmente:** descartado — enfraqueceria o portão (mais trabalho sem ficha deixaria de rearmá-lo).
- **Rearmar o lembrete a cada commit sem ficha (`sha1(âncora+HEAD)`):** descartado — subgranularidade que o domínio não tem; com commits pequenos, continuaria ruidoso.
- **Carência de N turnos:** descartado — contador com sabor de relógio (a 022 decidiu "sem relógio") e N arbitrário.
- **Remover o lembrete e confiar só no portão:** descartado — reverte o enforcement híbrido da 022 e perde o aviso com contexto fresco.
- **Flag de política no toml:** descartado — YAGNI.
- **Armazenar a âncora crua no estado:** descartado — quebraria a uniformidade com o campo-fingerprint irmão.

## Consequências

- **Positivas:**
  - O ruído desaparece: no máximo um soft-block por sessão, fácil de relembrar ("um lembrete por sessão; a garantia real é no encerramento").
  - A garantia dura fica **mais** protegida do que antes: o rearme do portão com trabalho novo agora tem teste-guarda dedicado.
  - Patch sem quebra de contrato (2.1.1): materializadores intocados, hook command idêntico, sem schema novo.
- **Negativas / em aberto:**
  - Pendências que surgem *depois* do primeiro lembrete na mesma sessão não geram novo aviso no Stop — por design; a captura fica a cargo do portão do encerramento.
  - Propagação à base instalada segue o fluxo pendente da MD-0015 (`upgrade`/`migrate` + core-raiz de `~/dev`).
