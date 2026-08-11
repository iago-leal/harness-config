# Actions: Índice de microdecisões leve com consulta sob demanda

> Identificador: `028-indice-decisoes-sob-demanda`
> Data: `2026-08-11`
> Roadmap: `_reversa_forward/028-indice-decisoes-sob-demanda/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 12 |
| Paralelizáveis (`[//]`) | 4 |
| Maior cadeia de dependência | 7 |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Adicionar `compact_file: str = ".harness/decisoes-recentes.md"` e `compact_index_size: int = 10` à `DecisionsSection`, com validação barulhenta na carga (negativo → erro claro; `0` válido) (D-04) | - | - | `.harness/harness-core/src/core/domain/config.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T002 | Testes da derivação da visão compacta no `DecisionService`: composição (cabeçalho de orientação, `Total: N fichas`, K mais recentes por ID em ordem decrescente, só títulos, sem backlinks), K=0 degradando para cabeçalho+contagem+ponteiros, determinismo byte a byte, ficha inválida/órfã abortando antes de derivar (D-01, D-03, contrato `bloco-resume-decisoes.md`) | T001 | - | `.harness/harness-core/tests/test_decisions.py` | 🟢 | `[X]` |
| T003 | Testes de write-only-when-changed para AMBAS as escritas (índice completo e visão compacta): sem mudança nas fichas → nenhuma regravação; com mudança → regrava atômico (D-05, RF-03) | T002 | - | `.harness/harness-core/tests/test_decisions.py` | 🟢 | `[X]` |
| T004 | Testes do `build_decisions_appendix` novo: injeta visão compacta quando existe; fallback para índice integral + aviso em stderr quando ausente; flag `inject_decisions_index = false` → vazio; ambos ausentes → vazio (D-02, RF-02) | T001 | `[//]` | `.harness/harness-core/tests/test_resume_context.py` | 🟢 | `[X]` |
| T005 | Testes do trecho de guidance no init: cria `CLAUDE.md` quando ausente; anexa quando existe sem marcador; re-init com marcador presente não duplica; perfil antigravity escreve no arquivo da engine (D-06, D-07, contrato `trecho-guidance-init.md`) | T001 | `[//]` | `.harness/harness-core/tests/test_init_service.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T006 | Implementar no `DecisionService` a derivação da visão compacta na MESMA passada do `compile_index`, com extração de título fatorada num único ponto compartilhado pelas duas visões, e write-only-when-changed nas duas escritas (D-01, D-03, D-05) | T001, T002, T003 | - | `.harness/harness-core/src/core/decisions/service.py` | 🟢 | `[X]` |
| T007 | Reescrever `build_decisions_appendix` para receber os dois caminhos (compacta e índice) e aplicar a precedência com fallback e aviso em stderr, preservando o contrato "flag false → vazio" (D-02) | T001, T004 | - | `.harness/harness-core/src/core/session/resume_context.py` | 🟢 | `[X]` |
| T008 | Conectar as pontas no `main.py`: ramo `decisions` derivando as duas visões; ramo `cmd resume` passando `compact_file` ao appendix, mantendo gate `active_harness == "claude"` e exit codes intocados (D-08) | T006, T007 | - | `.harness/harness-core/src/main.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Reindexação da bridge Antigravity derivando também a visão compacta (mesma chamada de serviço do T006; nenhuma injeção nova na bridge) (D-01) | T006 | `[//]` | `.harness/harness-core/src/adapters/antigravity/hook_bridge.py` | 🟢 | `[X]` |
| T010 | `init_service` gravando o trecho de guidance idempotente por marcador `<!-- harness:decisoes -->` no `CLAUDE.md` (perfil claude) ou no arquivo de guidance da engine (perfil antigravity, confirmar `AGENTS.md` no código real); `upgrade` não toca (D-06, D-07) | T001, T005 | `[//]` | `.harness/harness-core/src/core/bootstrap/init_service.py` | 🟡 | `[X]` |
| T011 | Suíte completa verde + ruff + smoke real neste repo: `./harness decisions` gera `.harness/decisoes-recentes.md` (21 fichas, MD-0021 no topo), segunda execução não regrava (mtime), `cmd resume` injeta a compacta, fallback com aviso ao remover o arquivo, re-init inócuo em projeto de laboratório (roteiro do `onboarding.md`) | T008, T009, T010 | - | `.harness/harness-core/tests/` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T012 | Bump minor da versão do core (2.5.0 → 2.6.0) e registro da microdecisão da feature (próximo ID livre, MD-0022) com relações ao acervo (estende MD-0002/RN-N12 via 021; relaciona MD-0015) | T011 | - | `.harness/harness-core/pyproject.toml` | 🟢 | `[X]` |

## Notas de execução

- 2026-08-11: as 12 ações executadas numa única rodada de `/reversa-coding`. Suíte em **389 verdes** (372 do baseline + 17 novos). Divergências menores em relação ao previsto: os testes do init (T005) foram escritos em `tests/test_init.py` (o arquivo `test_init_service.py` não existe; o alvo da tabela estava impreciso); o bump de versão (T012) vive no literal de `src/core/domain/config.py`, não no `pyproject.toml` (que não declara versão). A dúvida 🟡 do T010 foi confirmada: o arquivo de guidance do perfil antigravity é `AGENTS.md` (mapa claude→`CLAUDE.md`, antigravity→`AGENTS.md`, gemini→`GEMINI.md`). Nas relações da MD-0022, `estende MD-0002` previsto no T012 virou `refina MD-0002` (a visão compacta refina o conteúdo da reinjeção, não a estende) e `relaciona MD-0015` virou `relaciona MD-0019` (o padrão herdado é o de artefato derivado sem timestamp/WOWC, não o gate). Smoke real: 22 fichas, MD-0022 no topo; WOWC confirmado por mtime; fallback com aviso em stderr; laboratório de init/re-init idempotente aprovado.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-08-11 | Versão inicial gerada por `/reversa-to-do` | reversa |
