# ADR 0021: `cmd resume` ancora a busca do agente anexando o índice de decisões (Claude-first)

- **Status:** Aceito
- **Data:** 2026-07-05 (feature 021-hook-busca-ancorada)
- **Contexto Técnico:** Novo `src/core/session/resume_context.py` (`build_decisions_appendix`, função pura); novo campo `SessionSection.inject_decisions_index` (`src/core/domain/config.py`, default `True`, retrocompatível); fiação em `src/main.py` no ramo `cmd resume`, gated a `active_harness == "claude"`. `CommandService.execute_command` (compartilhado com o MCP) permanece intocado — o apêndice é composto **depois** de `execute_command` retornar, não dentro dele.
- **Escala de Confiança:** 🟢 CONFIRMADO (código as-built; suíte 256 verde relatada no fechamento da sessão da feature; smoke real dos 4 cenários — índice presente/ausente × flag ligado/desligado).
- **Decisões relacionadas:** ADR 0011 (reinjeção multi-harness por Strategy/sink); domain.md §2.3 (RN-07 reinjeção de contexto, RN-N8 teto de 10.000 chars do `HookContextSink`, RN-N5 core agnóstico ao harness); domain.md §2.5 (RN-N11/RN-N12, índice de decisões derivado e com caminho configurável); domain.md §2.18 (RN-N41, nova).

## Contexto e Problema

O hook `SessionStart` → `cmd resume` já reinjeta a narrativa da última sessão no contexto do agente no boot, mas nada além dela. Para se orientar sobre **decisões arquiteturais já tomadas** neste projeto (por que um caminho foi escolhido, o que já foi descartado e por quê), o agente precisaria varrer `.harness/decisoes/` ou o `domain.md` inteiro — uma busca ampla e cara em tokens logo no início da sessão, especialmente relevante para um mantenedor **intermitente** que reabre o projeto após semanas e cujo agente começa "frio". O harness já mantém um **índice derivado** e compacto dessas decisões (`.harness/microdecisoes.md`, regenerado pelo hook `Stop` a partir do grafo de `.harness/decisoes/`) — mas nada o entrega proativamente ao agente.

Medição que embasou o corte de escopo (2026-07-05): `estado-da-sessao.md` = 4,2 KB, `microdecisoes.md` = 1,7 KB, `decisoes/` (12 fichas) = 31,2 KB — o índice é **~18× menor** que a pasta inteira, e cabe, somado ao estado, dentro do teto de 10.000 caracteres que o `HookContextSink` já impõe à reinjeção no Claude (RN-N8). Injetar a pasta inteira estouraria esse teto com folga.

## Decisão

**Estender o `cmd resume`, não criar um mecanismo novo.** `build_decisions_appendix(fs, index_file, enabled) -> str`, em `resume_context.py`, é uma função pura, agnóstica ao harness: dado `enabled` (calculado na borda) e o caminho do índice (`config.decisions.index_file`, já configurável desde a feature 005/RN-N11), devolve `""` se desligado, se o índice não existir ou estiver vazio (RN-N4 — não-bloqueante), ou um cabeçalho fixo + o conteúdo do índice caso contrário. Em `main.py`, no ramo `cmd resume`, depois que `CommandService.execute_command` já produziu o corpo da narrativa: `enabled = active_harness == "claude" and config.session.inject_decisions_index`; o apêndice é concatenado **depois** do estado (`result_msg += build_decisions_appendix(...)`), de modo que, sob truncamento pelo teto do sink, é o índice que cede, nunca o estado da sessão — a informação mais crítica (onde a sessão parou) tem precedência sobre a mais acessória (o que já foi decidido).

Duas decisões de escopo, tomadas via `/reversa-clarify` na mesma sessão:

- **Mecanismo:** estender o `cmd resume` existente (uma injeção por sessão, reusa o sink e o teto já existentes) — não criar um segundo ponto de reinjeção nem um novo hook.
- **Escopo de harness:** **Claude-first**. Gemini usa o mesmo `HookContextSink`, então a extensão seria trivial (trocar o gate `claude` por uma checagem de família de sink) — adiado por decisão explícita do mantenedor, não por dificuldade técnica. Antigravity usa `FileProjectionSink`, sem o teto de 10.000 caracteres do Claude — teria que ter a própria projeção desenhada (o índice provavelmente caberia inteiro, sem pressão de espaço, mas isso é trabalho de desenho ainda não feito); também adiado.
- **Granularidade do conteúdo:** injeta o **índice derivado**, nunca a pasta `decisoes/` inteira. As fichas `MD-NNNN` individuais ficam para aprofundamento **sob demanda**, seguindo os ponteiros que o próprio índice já lista — o padrão "resumo condensado primeiro, detalhe só se necessário" que o Reversa já aplica em outras partes (ex.: escala de confiança 🟢/🟡/🔴).

## Alternativas Consideradas

- **Injetar a pasta `decisoes/` inteira em vez do índice:** descartado — ~18× maior, estouraria o teto de 10.000 caracteres do Claude já na primeira sessão de um projeto com poucas dezenas de decisões.
- **Novo hook/subcomando dedicado (ex.: `cmd decisions-context`) em vez de estender o `resume`:** descartado — duplicaria a entrega no boot (duas chamadas, dois sinks) sem ganho; o `resume` já é o ponto único de reinjeção de contexto (RN-07).
- **Habilitar para todos os harnesses desde já:** descartado nesta iteração — Antigravity exigiria desenhar a projeção em arquivo sob um teto (ou ausência dele) ainda não especificado; ampliar o escopo teria adiado a entrega do valor imediato para o Claude.
- **Opt-in (default desligado) em vez de opt-out:** descartado — o valor (orientar o agente antes de buscas amplas) é considerado alto o bastante para nascer ligado por padrão; quem não quiser desativa via `harness.toml`.

## Consequências

- **Positivas:**
  - O agente Claude, ao retomar uma sessão, recebe o "porquê" do projeto junto com o "onde parei", sem custo de busca ampla — ganho direto para o mantenedor intermitente.
  - Nenhuma mudança de contrato em `CommandService.execute_command` (compartilhado com o MCP): o apêndice é uma composição na borda, não uma mudança de domínio.
  - Retrocompatível por padrão de campo (`inject_decisions_index = True` implícito em `harness.toml`s existentes sem a chave) e não-bloqueante (índice ausente vira aviso em `stderr`, nunca falha o `resume`).
- **Negativas / em aberto:**
  - Gemini e Antigravity não recebem o apêndice nesta iteração — extensão futura, provavelmente barata para o Gemini, mais trabalhosa para o Antigravity (exige desenho de projeção).
  - Sob crescimento do grafo de decisões, o índice de 1,7 KB pode crescer o bastante para pressionar o teto de 10.000 chars junto com o estado — não há hoje um mecanismo de sumarização ou paginação do índice; é um limite latente, não uma falha atual.
