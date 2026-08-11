# Actions: Medidor de progresso de entregáveis (`harness progress`)

> Identificador: `026-medidor-progresso-entregaveis`
> Data: `2026-08-11`
> Roadmap: `_reversa_forward/026-medidor-progresso-entregaveis/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 14 |
| Paralelizáveis (`[//]`) | 7 |
| Maior cadeia de dependência | 8 |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Adicionar `ProgressSection` à config canônica (campo único `file: str = ".harness/progresso.md"`), plugada em `HarnessConfig` no padrão da `DecisionsSection`; tomls existentes herdam o default sem migração (D-06) | - | `[//]` | `.harness/harness-core/src/core/domain/config.py` | 🟢 | `[X]` |
| T002 | Criar o esqueleto do pacote `src/core/progress/` (`__init__.py` + dataclasses transitórias `Medicao`, `FeatureProgresso`, `Alerta` em `service.py`, stubs de `stages.py` e `render.py`) como décima capacidade do hexágono (D-01) | - | `[//]` | `.harness/harness-core/src/core/progress/` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Testes de `stages.py`: tabela de estágio físico (vazio/requirements/plan/coding-em-progresso/done) e contagem de checkboxes em linhas de tabela, com fixtures no formato real (checkbox envolto em crase, cabeçalhos, linhas livres ignoradas) (D-04, RN-06) | T002 | `[//]` | `.harness/harness-core/tests/test_progress_stages.py` | 🟢 | `[X]` |
| T004 | Testes do serviço e dos renderizadores: medição com fontes fake (ativa + pausadas + concluídas, divergência declarado×físico como alerta `alta`, pendência de regression-watch como `media`, fail-soft com fonte ausente → n/a, exit lógico de fonte corrompida), markdown sem timestamp com idempotência byte a byte e ordenação determinística, JSON com `aferido_em` (RN-01..03, RN-05, D-05, D-07) | T002 | `[//]` | `.harness/harness-core/tests/test_progress_service.py` | 🟢 | `[X]` |
| T005 | Testes da CLI `harness progress` em `test_cli.py`: modo padrão grava e informa `regravado`/`em dia` (segunda execução sem mudança de bytes), `--json` parseável sem tocar arquivo, `--em-hook` nos três desfechos (0 em dia; 1 defasado com regravação e instrução em stderr; 0 com alerta alto e aviso em stderr), exclusividade `--json`/`--em-hook`, exit 2 com fonte ilegível (D-02, D-03) | T002 | `[//]` | `.harness/harness-core/tests/test_cli.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T006 | Implementar `stages.py`: detecção de estágio físico por artefatos e contagem de checkboxes, único ponto de paridade com a tabela do skill `reversa-requirements`, com docstring de referência cruzada (D-04) | T003 | - | `.harness/harness-core/src/core/progress/stages.py` | 🟢 | `[X]` |
| T007 | Implementar `service.py`: medição pura das quatro fontes (`.reversa/active-requirements.json`, artefatos de `_reversa_forward/*`, `regression-watch.md`, sessão/fichas/`evaluate_registration_gate` em leitura pura sem persistir fingerprint) e derivação dos alertas com severidade (D-01, D-05, D-07) | T004, T006 | - | `.harness/harness-core/src/core/progress/service.py` | 🟢 | `[X]` |
| T008 | Implementar `render.py`: renderizador markdown (cabeçalho derivado + seções Ciclo forward, Harness, Alertas; sem timestamp nem caminho absoluto) e renderizador JSON (`ensure_ascii=False`, `aferido_em` injetado pela borda) (RN-02, D-02) | T004, T007 | - | `.harness/harness-core/src/core/progress/render.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Subcomando `progress` em `main.py`: parser com grupo mutuamente exclusivo `--json`/`--em-hook`, despacho fino para o serviço, gravação só-quando-muda em `config.progress.file`, exit codes 0/1/2 conforme o contrato `interfaces/progress-cli.md` (D-02, D-03) | T005, T007, T008 | - | `.harness/harness-core/src/main.py` | 🟢 | `[X]` |
| T010 | Rodar a suíte completa (320 pré-existentes + novos) até verde e `ruff check` limpo nos arquivos novos | T009 | - | `.harness/harness-core/tests/` | 🟢 | `[X]` |
| T011 | Smoke real neste repositório (roteiro do `onboarding.md`): gerar `.harness/progresso.md` medindo 024 pausada / 025 concluída / 026 ativa, conferir idempotência byte a byte, `--json`, os três desfechos do `--em-hook` e o escopo negativo (nenhuma escrita fora do artefato) | T010 | - | `.harness/progresso.md` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T012 | Bump de versão `2.3.0` → `2.4.0` no literal de `config.py` (D-09) | T010 | `[//]` | `.harness/harness-core/src/core/domain/config.py` | 🟢 | `[X]` |
| T013 | Registrar a ficha `MD-0019` (decisões D-01..D-09, relações com as fichas anteriores) e recompilar o índice de microdecisões | T011 | `[//]` | `.harness/decisoes/MD-0019.md` | 🟢 | `[X]` |
| T014 | Reconciliar `interfaces/progress-cli.md` e `onboarding.md` com notas as-built, se o smoke revelar divergência do contrato (lição da 025) | T011 | - | `_reversa_forward/026-medidor-progresso-entregaveis/interfaces/progress-cli.md` | 🟢 | `[X]` |

## Notas de execução

- T011 (smoke real): o medidor pagou-se no primeiro uso — apontou o `current-stage` do `active-requirements.json` parado em `requirements` com físico `coding-em-progresso`; a fonte foi corrigida para `coding` (o achado não foi suprimido). Idempotência, `--json` e `--em-hook` (1 → 0 após regravação) conferidos neste repo.
- T014 (as-built): nenhuma divergência entre o comportamento real e `interfaces/progress-cli.md` / `onboarding.md`; nada a reconciliar.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-08-11 | Versão inicial gerada por `/reversa-to-do` | reversa |
