# ADR 0026: Medidor de progresso inteiramente derivado — leitura pura, artefato sem valor volátil

- **Status:** Aceito
- **Data:** 2026-08-11 (feature 026-medidor-progresso-entregaveis, MD-0019; não commitada na data desta extração)
- **Contexto Técnico:** módulo novo `core/progress/` (`service.py`, `stages.py`, `render.py`); subcomando `progress` no `main.py` (13º da CLI) com modos padrão, `--json` e `--em-hook`; `ProgressSection` no `HarnessConfig` (`[progress].file`, default `.harness/progresso.md`); modelo transitório `Medicao`. Core 2.3.0 → 2.4.0.
- **Escala de Confiança:** 🟢 CONFIRMADO (TDD; invariante de leitura pura pinada por teste `fs.writes == []`; suíte verde).
- **Decisões relacionadas:** MD-0019 (`relaciona MD-0018`, `refina MD-0013`); domain.md §2.24 (RN-N50/N51/N52); ADR 0025 (o medidor não cria terceira política de bloqueio); ADR 0027 (segunda projeção da mesma `Medicao`).

## Contexto e Problema

O harness respondia "o quê" (estado de sessão) e "por quê" (microdecisões), mas não "quanto falta": progresso das ações do ciclo forward, features por estágio físico, pendências de reconciliação e alertas derivados viviam espalhados em artefatos que só o olho humano agregava. O mantenedor pediu a reprodução do padrão do `make estado` de `comentarios-concursos`: um termômetro read-only, sem estado próprio, cujo artefato versionado só gera diff quando o estado muda.

## Decisão

**Medição como derivação pura.** `ProgressService.measure()` agrega cinco fontes de verdade (ciclo forward por artefatos físicos + `active-requirements.json`; regression-watch, cuja marca literal "pendência de reconciliação" vira alerta média; microdecisões com o gate reavaliado em leitura pura, sem persistir fingerprint; estado de sessão; e, com opt-in, os cards manuais do board) num modelo transitório `Medicao`, jamais persistido. Fonte ausente é `n/a` legítimo; fonte ilegível é falha real (`Erro de leitura:` em stderr, exit 2, nenhum artefato regravado). Divergência entre estágio declarado e físico é achado (alerta alta), nunca corrigida silenciosamente.

**Artefato sem valor volátil.** O markdown derivado não carrega timestamp nem caminho absoluto; a regravação é atômica e write-only-when-changed. `--json` (stdout, não versionado) pode carimbar `aferido_em`. `--em-hook` sai 1 **apenas** por artefato defasado; alerta grave vira aviso em stderr sem bloquear — o exit 3 do medidor original de `comentarios-concursos` não foi transplantado (D-03), coerente com o enforcement em duas políticas da 025.

**Paridade em ponto único.** `stages.py` codifica a tabela de estágio físico e a contagem de checkboxes que o skill `reversa-requirements` descreve em prosa; `contar_checkboxes` e `listar_acoes` compartilham o mesmo critério de linha. Alertas persistem enquanto o sinal físico existir, sem mecanismo de ack.

## Alternativas Consideradas

- **Estado próprio do medidor (cache/snapshot):** descartado — duplicaria fontes de verdade e criaria o problema de invalidação; derivação pura é o padrão comprovado no `make estado`.
- **Viver em `tools/` do projeto em vez do core:** descartado — no core propaga pela fonte única a toda a base migrada (RN-N36).
- **Timestamp no markdown:** descartado — todo run geraria diff, poluindo o histórico; a hora vive só no `--json`.
- **`--em-hook` com exit 3 para alerta grave (como o original):** descartado (D-03) — seria uma terceira política de bloqueio, recém-eliminada pela 025.

## Consequências

- **Positivas:**
  - "Quanto falta" vira resposta de um comando, com artefato versionável cujo diff é sinal, não ruído.
  - Alertas sem ack não podem ser silenciados por engano: só a remoção do sinal físico (ex.: re-extração resolvendo a pendência) os apaga.
  - A `Medicao` transitória abriu caminho, na mesma semana, para a segunda projeção (kanban, ADR 0027) sem retrabalho.
- **Negativas / em aberto:**
  - A paridade `stages.py` ↔ prosa do skill é convenção vigiada por teste, não derivação automática: mudar o skill exige mudar o código junto.
  - Nenhum hook dispara o medidor por padrão; a defasagem do artefato só é detectada quando alguém roda `--em-hook` ou o comando manual.
