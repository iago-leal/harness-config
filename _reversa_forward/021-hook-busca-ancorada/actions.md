# Actions: Hook de busca ancorada no estado da sessão e no índice de decisões

> Identificador: `021-hook-busca-ancorada`
> Data: `2026-07-05`
> Roadmap: `_reversa_forward/021-hook-busca-ancorada/roadmap.md`

## Resumo

| Métrica                     | Valor                                |
| --------------------------- | ------------------------------------ |
| Total de ações              | 8                                    |
| Paralelizáveis (`[//]`)     | 4                                    |
| Maior cadeia de dependência | 5 (T003 → T005 → T006 → T007 → T008) |

## Fase 1, Preparação

<!-- Setup, scaffolding, migrações iniciais, configuração de infraestrutura local. -->

| ID   | Descrição                                                                                                                                          | Dependências | Paralelismo | Arquivo alvo                                      | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------- | ----------- | ------ |
| T001 | Adicionar o campo `inject_decisions_index: bool = True` a `SessionSection` (config tipada, D-05). Retrocompatível: tomls sem o campo herdam `True` | -            | `[//]`      | `.harness/harness-core/src/core/domain/config.py` | 🟢          | `[X]`  |

## Fase 2, Testes

<!-- Testes que precisam existir antes ou logo após o núcleo. Omitir se a equipe não pratica TDD. -->

| ID   | Descrição                                                                                                                                                                                                                                                                        | Dependências | Paralelismo | Arquivo alvo                                                | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ----------------------------------------------------------- | ----------- | ------ |
| T002 | Teste (red) do parse do flag: `[session] inject_decisions_index=false` → `False`; campo ausente → `True`; seção `[session]` ausente → `True` (default retrocompatível, `data-delta.md#5`)                                                                                        | T001         | `[//]`      | `.harness/harness-core/tests/test_config.py`                | 🟢          | `[X]`  |
| T003 | Teste (red) de `build_decisions_appendix(fs, index_file, enabled)`: (a) `enabled=True` + índice presente → bloco com cabeçalho de orientação **e** o conteúdo do índice; (b) `enabled=False` → `""`; (c) `enabled=True` + índice ausente → `""`. Função pura, sem I/O de stderr  | -            | `[//]`      | `.harness/harness-core/tests/test_resume_context.py` (novo) | 🟢          | `[X]`  |
| T004 | Teste (red) da fiação do `cmd resume` na borda: com `active_harness=claude` + flag on, o `additionalContext` emitido contém o índice; com flag off, não contém; com `active_harness=gemini`, não contém (gate D-04); índice ausente → aviso em `stderr` e exit 0 com só o estado | T001         | `[//]`      | `.harness/harness-core/tests/test_cli.py`                   | 🟡          | `[X]`  |

## Fase 3, Núcleo

<!-- Lógica central da feature. -->

| ID   | Descrição                                                                                                                                                                                                                                                                                                               | Dependências | Paralelismo | Arquivo alvo                                                      | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ----------------------------------------------------------------- | ----------- | ------ |
| T005 | Implementar `build_decisions_appendix(fs, index_file, enabled) -> str` (D-03): `not enabled` → `""`; `not fs.exists(index_file)` → `""`; senão devolve `"\n\n---\n## Índice de decisões (consulte antes de buscas amplas)\n\n"` + conteúdo do índice. Pura, agnóstica ao harness (não escreve stderr). Torna T003 verde | T003         | -           | `.harness/harness-core/src/core/session/resume_context.py` (novo) | 🟢          | `[X]`  |

## Fase 4, Integração

<!-- Cola com outras partes do sistema, contratos externos, ganchos. -->

| ID   | Descrição                                                                                                                                                                                                                                                                                                                                                                                                                                             | Dependências | Paralelismo | Arquivo alvo                        | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ----------------------------------- | ----------- | ------ |
| T006 | Fiar no ramo `cmd resume` de `main.py` (D-01/D-04/D-06): calcular `enabled = (config.harness.active_harness == "claude") and config.session.inject_decisions_index`; se `enabled and not fs.exists(config.decisions.index_file)`, avisar em `stderr`; obter o apêndice via `build_decisions_appendix(fs, config.decisions.index_file, enabled)` e concatená-lo a `result_msg` (estado primeiro, índice depois) antes de `sink.emit`. Torna T004 verde | T001, T005   | -           | `.harness/harness-core/src/main.py` | 🟢          | `[X]`  |

## Fase 5, Polimento

<!-- Logs, telemetria, mensagens de erro, documentação curta. -->

| ID   | Descrição                                                                                                                                                                                                                                                     | Dependências                             | Paralelismo | Arquivo alvo                            | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ----------- | --------------------------------------- | ----------- | ------ |
| T007 | Atualizar o `help` do subcomando `cmd` em `main.py` para registrar que, no Claude, o `resume` também reinjeta o índice de decisões (desativável por `session.inject_decisions_index`); conferir que o `doc-gen` (introspecção do parser) reflete o texto novo | T006                                     | -           | `.harness/harness-core/src/main.py`     | 🟢          | `[X]`  |
| T008 | Verificação final: suíte do core verde + **smoke real** de `./harness cmd resume` pelos cenários A–D do `onboarding.md` (anexa o índice; desliga por flag; índice ausente não trava com exit 0; volume ~índice, não ~fichas)                                  | T001, T002, T003, T004, T005, T006, T007 | -           | `.harness/harness-core/tests/` + manual | 🟢          | `[X]`  |

## Notas de execução

<!--
Reservado para /reversa-coding registrar avisos ou observações que surgiram durante a execução.
Não use isso para corrigir ações, edits manuais ficam fora desse arquivo, vão direto no código.
-->

## Histórico de alterações

| Data       | Alteração                                  | Autor   |
| ---------- | ------------------------------------------ | ------- |
| 2026-07-05 | Versão inicial gerada por `/reversa-to-do` | reversa |
