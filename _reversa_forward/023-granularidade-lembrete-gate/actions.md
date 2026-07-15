# Actions: Granularidade do lembrete do gate de registro (rearme estável por pendência)

> Identificador: `023-granularidade-lembrete-gate`
> Data: `2026-07-15`
> Roadmap: `_reversa_forward/023-granularidade-lembrete-gate/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 9 |
| Paralelizáveis (`[//]`) | 5 |
| Maior cadeia de dependência | 5 (T001 → T004 → T005 → T006 → T007) |

## Fase 1, Preparação

n/a — a feature não exige setup, scaffolding nem migração: o delta é sobre módulos existentes, sem dependência nova (roadmap D-03/D-04).

## Fase 2, Testes

<!-- TDD: estas ações nascem VERMELHAS por exigência da meta da sessão; nenhuma implementação antes delas. -->

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Teste (red) da identidade grossa em `gate.py`: `compute_lembrete_fingerprint(anchor)` é determinística, sensível à âncora, estável sob variação de HEAD e do conjunto sujo; âncora vazia/`None` → constante; `GateVerdict.fingerprint_lembrete` preenchido pelo avaliador e ≠ `fingerprint` fino (D-02) | - | `[//]` | `.harness/harness-core/tests/test_decision_gate.py` | 🟢 | `[X]` |
| T002 | Teste (red) do ramo `--gate` em `main.py`: (a) 1º bloqueio persiste a identidade grossa em `gate_lembrete_fingerprint`; (b) **teste-queixa**: arquivo sujo novo após o 1º bloqueio → stdout vazio; (c) valor no formato antigo (fino) gravado → exatamente 1 bloqueio e campo regravado (RF-05); (d) ficha `MD-*.md` presente → silêncio; (e) contrato do stdout inalterado (D-01/D-05) | - | `[//]` | `.harness/harness-core/tests/test_cli.py` | 🟢 | `[X]` |
| T003 | Teste-guarda do portão (D-06, pode nascer verde — pina comportamento): após um bloqueio do 3º portão, trabalho novo sem ficha (dirty diferente) → portão bloqueia DE NOVO; estado idêntico → anti-loop libera com aviso; portão segue comparando `verdict.fingerprint` fino (RF-03) | - | `[//]` | `.harness/harness-core/tests/test_close_flow.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T004 | Implementar `compute_lembrete_fingerprint(anchor)` (função pura, `sha1(âncora)`) e o campo `fingerprint_lembrete` no `GateVerdict`, preenchido por `evaluate_registration_gate`; docstrings registram a dupla identidade (lembrete grosso × portão fino). Torna T001 verde | T001 | - | `.harness/harness-core/src/core/decisions/gate.py` | 🟢 | `[X]` |
| T005 | Trocar a identidade consumida pelo ramo `--gate` de `main.py`: comparar e persistir `verdict.fingerprint_lembrete` em `gate_lembrete_fingerprint`; resto do ramo byte-idêntico (mensagem, stderr, exit 0). Torna T002 verde | T002, T004 | - | `.harness/harness-core/src/main.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T006 | Rodar a suíte completa: casos novos verdes, T003 verde, zero regressões na suíte da 022 (portão, advisory Antigravity, serializer, CLI sem `--gate`) | T003, T004, T005 | - | `.harness/harness-core/tests/` | 🟢 | `[X]` |
| T007 | Smoke real dos cenários A–E do `onboarding.md` com git real (lição da memória: mock esconde porcelain) — A: 1 lembrete e só um; B: silêncio pós-ficha; C: portão rearma com trabalho novo; D: transição de formato; E: opt-out | T006 | - | manual (raiz do repo) | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T008 | Bump do core 2.1.0 → 2.1.1 (patch, D-05); confirmar que nenhum materializador muda (hook command idêntico — nada a regenerar em `.claude/settings.json`/snippet) | T006 | `[//]` | `.harness/harness-core/src/core/version.py` (ou onde `CORE_VERSION` viver) | 🟢 | `[X]` |
| T009 | Registrar a ficha `MD-0016` (política do lembrete: única por sessão, âncora como identidade; estende MD-0015; alternativas b/c/d descartadas com porquês do clarify) e regenerar o índice via `./harness decisions` | T005 | `[//]` | `.harness/decisoes/MD-0016.md` | 🟢 | `[X]` |

## Notas de execução

<!--
Reservado para /reversa-coding registrar avisos ou observações que surgiram durante a execução.
Não use isso para corrigir ações, edits manuais ficam fora desse arquivo, vão direto no código.
-->

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-07-15 | Versão inicial gerada por `/reversa-to-do` | reversa |
