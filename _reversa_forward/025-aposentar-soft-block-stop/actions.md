# Actions: Aposentar o soft-block do Stop

> Identificador: `025-aposentar-soft-block-stop`
> Data: `2026-08-11`
> Roadmap: `_reversa_forward/025-aposentar-soft-block-stop/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 11 |
| Paralelizáveis (`[//]`) | 3 |
| Maior cadeia de dependência | 6 (T001→T002→T003→T004→T005→T006) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Rodar a suíte completa e registrar a linha de base verde (320 testes) antes de qualquer edição | - | - | `.harness/harness-core/tests/` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T002 | Retargetar os 10 testes do ramo `--gate` (linhas 841-957): expectativa vira stdout **vazio** + advisory em stderr com prefixo `Aviso:` e marker `DECISAO_PENDENTE`; preservar os cenários de idempotência por sessão, não-rearme com arquivo novo, persistência da identidade grossa e transição do formato antigo; confirmar que a suíte fica vermelha (TDD) | T001 | - | `.harness/harness-core/tests/test_cli.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | No ramo `decisions --gate` de `main.py` (linhas ~399-410), substituir o `print(json.dumps({"decision":"block",...}))` por emissão em stderr (`Aviso:` + `render_decisao_pendente_marker` + frase de ação sem "e conclua o turno"); manter intactos a persistência do fingerprint grosso, a reindexação, o fail-open e o `sys.exit(0)`; **não tocar** `gate.py`, `close_flow.py`, perfis nem assinaturas (D-01/D-06) | T002 | - | `.harness/harness-core/src/main.py` | 🟢 | `[X]` |
| T004 | Rodar a suíte completa e confirmar verde, incluindo o teste-guarda `test_close_flow.py::test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio` sem nenhuma alteração nesse arquivo (D-04) | T003 | - | `.harness/harness-core/tests/` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Bump da versão do core 2.2.0 → 2.3.0 na constante de `config.py` (linha 13) e ajuste de testes que pinam a versão, se houver (D-05) | T004 | - | `.harness/harness-core/src/core/domain/config.py` | 🟢 | `[X]` |
| T006 | Smoke manual em repositório descartável conforme `onboarding.md` §2: stdout vazio, advisory único por sessão, segunda invocação silenciosa, portão do encerramento ainda bloqueando | T005 | - | `onboarding.md` (roteiro) | 🟢 | `[X]` |
| T007 | Varredura por menções stale ao lembrete bloqueante (`decision.*block`, `soft-block`, "conclua o turno") em docs do core, skills geradas e materializadores; corrigir apenas artefatos gerenciados pelo harness, jamais fichas MD históricas | T003 | `[//]` | `.harness/harness-core/` (varredura) | 🟡 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T008 | Registrar a ficha `MD-0018` (reversão parcial das MD-0015/0016: canal advisory em stderr, garantia dura só no portão; citar a evidência viva da interrupção de 2026-08-11) e recompilar o índice derivado de decisões | T004 | `[//]` | `.harness/decisoes/MD-0018.md` | 🟢 | `[X]` |
| T009 | Gerar `regression-watch.md` da feature com as supersessões explícitas dos itens das 022/023 que vigiavam o block JSON (padrão MD-0014) | T004 | `[//]` | `regression-watch.md` (feature-dir) | 🟢 | `[X]` |
| T010 | Gerar `legacy-impact.md` com a lista final de arquivos tocados versus escopo negativo declarado no roadmap §5 | T004, T005, T007 | - | `legacy-impact.md` (feature-dir) | 🟢 | `[X]` |
| T011 | Registrar no `regression-watch.md` a pendência não bloqueante de reconciliação dirigida do `_reversa_sdd/` (`domain.md` §2.20-2.21, RN-N44; `code-analysis.md` §11), conforme RF-06 | T009 | - | `regression-watch.md` (feature-dir) | 🟢 | `[X]` |

## Notas de execução

- T002/T003: descoberta as-built — em modo `--gate` os informativos da reindexação já saíam em stderr; as asserções de "silêncio" verificam a ausência do marker `DECISAO_PENDENTE`, não stderr vazio (contrato atualizado em `interfaces/stop-gate-stdout.md`).
- T006: o smoke confirmou de graça a propagação pela fonte única: o projeto descartável, instalado via shim, reportou v2.3.0 e o comportamento novo sem qualquer reinstalação.
- T007: duas menções stale corrigidas nos helps do argparse (`decisions` e `--gate`) e uma no comentário da `DecisionsSection`; `gate.py` mantém menções genéricas a "lembrete" por desígnio (não conhece canal).
- T008: o vocabulário fixo de relações do grafo não admite `reverte-parcialmente`; a ficha usa `substitui MD-0016` + `refina MD-0015` com a partialidade explicada no corpo.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-08-11 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-08-11 | T001–T011 executadas e concluídas por `/reversa-coding` | reversa |
