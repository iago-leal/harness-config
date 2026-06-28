# Actions: encerrar-sessao como skill versionável (skill como adaptador)

> Identificador: `018-encerrar-sessao-como-skill`
> Data: `2026-06-28`
> Roadmap: `_reversa_forward/018-encerrar-sessao-como-skill/roadmap.md`

## Resumo

| Métrica                     | Valor                                              |
| --------------------------- | -------------------------------------------------- |
| Total de ações              | 17                                                 |
| Paralelizáveis (`[//]`)     | 12                                                 |
| Maior cadeia de dependência | 7 (T002 → T003 → T008 → T013 → T014 → T015 → T016) |

Decomposição em TDD: os testes de cada frente (serviço de fachada, perfil/árvore, materializador, scripts finos, versão) vêm antes do núcleo correspondente. As três frentes — **core** (extrair orquestração), **materialização** (perfil + materializador) e **skill** (SKILL.md + scripts finos) — rodam em paralelo até convergirem na ligação do `init`/`upgrade`. Confidências herdadas das decisões D-01…D-06 do roadmap.

## Fase 1, Preparação

<!-- Setup, scaffolding, migrações iniciais, configuração de infraestrutura local. -->

| ID   | Descrição                                                                                                                                                        | Dependências | Paralelismo | Arquivo alvo                                                                               | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------------------------------------------------ | ----------- | ------ |
| T001 | Bump da versão do core `1.2.54 → 1.2.55` nas duas constantes sincronizadas: `HarnessSection.version` e `BootstrapService.current_version` (D-06).                | -            | `[//]`      | `.harness/harness-core/src/core/domain/config.py` (+ `src/core/bootstrap/init_service.py`) | 🟢          | `[X]`  |
| T002 | Criar o esqueleto do serviço de fachada `SessionCloseFlow` em `core/session/close_flow.py` (contrato público vazio, sem lógica) para destravar os testes (D-01). | -            | `[//]`      | `.harness/harness-core/src/core/session/close_flow.py`                                     | 🟡          | `[X]`  |

## Fase 2, Testes

<!-- Testes que precisam existir antes ou logo após o núcleo. A equipe pratica TDD (P5.2). -->

| ID   | Descrição                                                                                                                                                                                                                                                                                                                                                   | Dependências | Paralelismo | Arquivo alvo                                           | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------------ | ----------- | ------ |
| T003 | Testes do `SessionCloseFlow`: orquestra regen → pré-check de trabalho pendente (`list_dirty_paths`) → marker `[HARNESS:COMMIT_PENDENTE …]` (016) → gravação do estado + commit isolado (RN-N31/N32). Cobre caminho feliz e caminho com trabalho pendente.                                                                                                   | T002         | `[//]`      | `.harness/harness-core/tests/test_close_flow.py`       | 🟡          | `[X]`  |
| T004 | Testes do `HarnessProfile.skills_dir`: `claude → .claude/skills`, `antigravity → .agents/skills`, `gemini → None`; e da árvore agnóstica da skill (idêntica para os dois harnesses, só o prefixo muda) (D-03).                                                                                                                                              | -            | `[//]`      | `.harness/harness-core/tests/test_harness_profiles.py` | 🟡          | `[X]`  |
| T005 | Testes do materializador de skill: grava a árvore em `.claude/skills/encerrar-sessao/` e `.agents/skills/encerrar-sessao/`; remove os artefatos antigos (`commands/encerrar-sessao.md`, `.agent(s)/workflows/encerrar-sessao.md`) via `stale_session_command_paths`; preserva terceiros; idempotência; paridade byte-a-byte entre os dois harnesses (D-04). | -            | `[//]`      | `.harness/harness-core/tests/test_session_skills.py`   | 🟢          | `[X]`  |
| T006 | Atualizar `tests/test_init.py`: assertar versão `1.2.55` e que o `init` materializa a skill (SKILL.md + scripts/) nos dois harnesses, substituindo a asserção do command/workflow antigo.                                                                                                                                                                   | -            | `[//]`      | `.harness/harness-core/tests/test_init.py`             | 🟢          | `[X]`  |
| T007 | Teste de fumaça do bootstrap dos scripts finos: com o core ausente/não-importável, o entry point falha barulhento (exit ≠ 0 + mensagem orientadora), nunca silencioso (contrato de erros).                                                                                                                                                                  | -            | `[//]`      | `.harness/harness-core/tests/test_skill_scripts.py`    | 🟡          | `[X]`  |

## Fase 3, Núcleo

<!-- Lógica central da feature. -->

| ID   | Descrição                                                                                                                                                                                                                     | Dependências | Paralelismo | Arquivo alvo                                                 | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------------------ | ----------- | ------ |
| T008 | Implementar `SessionCloseFlow`: orquestra o fluxo reusando `CommandService` / `GitPort` / `DecisionService` (lógica movida de `main.py`), sem reimplementar regra. Faz T003 passar (D-01).                                    | T002, T003   | -           | `.harness/harness-core/src/core/session/close_flow.py`       | 🟡          | `[X]`  |
| T009 | Reapontar a borda CLI `cmd encerrar-sessao` em `main.py` (L418–475) para `SessionCloseFlow`, removendo a orquestração duplicada e preservando o comportamento (incl. fluxo 016). Mantém os testes da 016 verdes (D-01, D-05). | T008         | `[//]`      | `.harness/harness-core/src/main.py`                          | 🟡          | `[X]`  |
| T010 | Implementar `HarnessProfile.skills_dir` por harness e a definição da árvore agnóstica da skill; retirar/substituir `session_command_artifact`. Faz T004 passar (D-03).                                                        | T004         | `[//]`      | `.harness/harness-core/src/core/install/harness_profiles.py` | 🟡          | `[X]`  |

## Fase 4, Integração

<!-- Cola com outras partes do sistema, contratos externos, ganchos. -->

| ID   | Descrição                                                                                                                                                                                                                                                | Dependências           | Paralelismo | Arquivo alvo                                                                                      | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ----------- | ------------------------------------------------------------------------------------------------- | ----------- | ------ |
| T011 | Criar o `SKILL.md` fonte da skill: front-matter `name` + `description` rica em gatilhos de ativação + cláusula NÃO ative + `version: "1.0.0"`; corpo descrevendo a sequência e apontando os scripts (D-02, contrato).                                    | -                      | `[//]`      | `.harness/harness-core/src/core/install/assets/skills/encerrar-sessao/SKILL.md`                   | 🟢          | `[X]`  |
| T012 | Criar o bootstrap fino `scripts/_bootstrap.py`: resolve a raiz via git, localiza `.harness/harness-core`, configura venv/PYTHONPATH e importa o core; erro barulhento se ausente. Faz T007 passar (D-02).                                                | T007                   | `[//]`      | `.harness/harness-core/src/core/install/assets/skills/encerrar-sessao/scripts/_bootstrap.py`      | 🟡          | `[X]`  |
| T013 | Criar o entry point fino `scripts/encerrar_sessao.py`: via bootstrap, instancia e chama `SessionCloseFlow`; não reimplementa lógica (D-02).                                                                                                              | T008, T012             | `[//]`      | `.harness/harness-core/src/core/install/assets/skills/encerrar-sessao/scripts/encerrar_sessao.py` | 🟢          | `[X]`  |
| T014 | Implementar o materializador de skill (estender `session_commands.py` ou novo `session_skills.py`): grava a árvore nos dois `skills_dir` (atômico) e remove os antigos via `stale_session_command_paths`, preservando terceiros. Faz T005 passar (D-04). | T005, T010, T011, T013 | -           | `.harness/harness-core/src/core/install/session_commands.py`                                      | 🟢          | `[X]`  |
| T015 | Ligar a materialização da skill no `init` e no `upgrade` (`init_service.py` + caminho de `apply_local_materializers`, feature 012), substituindo a materialização do command/workflow antigo. Faz T006 passar (D-04, D-06).                              | T001, T006, T014       | -           | `.harness/harness-core/src/core/bootstrap/init_service.py`                                        | 🟡          | `[X]`  |

## Fase 5, Polimento

<!-- Logs, telemetria, mensagens de erro, documentação curta. -->

| ID   | Descrição                                                                                                                                                                           | Dependências | Paralelismo | Arquivo alvo                                                                                 | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | -------------------------------------------------------------------------------------------- | ----------- | ------ |
| T016 | Remover o caminho/material morto do artefato antigo (`session_command_artifact` e referências ao `.md` que delegava ao binário), agora substituído pela skill, sem quebrar a suíte. | T014, T015   | -           | `.harness/harness-core/src/core/install/harness_profiles.py`                                 | 🟡          | `[X]`  |
| T017 | Afinar mensagens e erros barulhentos dos scripts/serviço (core não encontrado, falha de commit do estado): texto orientador + exit ≠ 0 conforme o contrato de erros e bordas.       | T012, T013   | -           | `.harness/harness-core/src/core/install/assets/skills/encerrar-sessao/scripts/_bootstrap.py` | 🟡          | `[X]`  |

## Notas de execução

<!--
Reservado para /reversa-coding registrar avisos ou observações que surgiram durante a execução.
Não use isso para corrigir ações, edits manuais ficam fora desse arquivo, vão direto no código.
-->

- Nomes/caminhos com confidência 🟡 a confirmar no coding: `close_flow.py` vs método em `CommandService` (D-01); `session_skills.py` vs estender `session_commands.py` (D-04); `assets/skills/` como diretório-fonte da árvore (D-02/D-03). A estrutura de ações vale para qualquer uma das variantes.
- Critério de pronto do roadmap inclui `regression-watch.md` e o smoke nos dois harnesses: ambos são responsabilidade do `/reversa-coding` (gera `legacy-impact.md` + `regression-watch.md` e conduz a verificação), não ações de código deste plano.
- **Execução (2026-06-28):** confirmadas as escolhas 🟡 — D-01 virou serviço `SessionCloseFlow` em `core/session/close_flow.py` (não método em `CommandService`); D-04 virou novo `core/install/session_skills.py` (não extensão de `session_commands.py`, que foi removido); a árvore-fonte vive em `core/install/assets/skills/encerrar-sessao/`.
- **Acoplamento da migração:** remover `session_command_artifact` cruzou vários testes; a troca do materializador, a fiação e as atualizações de teste foram feitas no mesmo passo para manter a suíte verde. Testes da API antiga removidos (`test_session_command_profiles.py`, `test_session_commands_materializer.py`); `test_antigravity_profile.py`/`test_local_apply.py`/`test_init.py`/`test_cli.py` atualizados.
- **Fix além do plano (T017):** o re-exec do `_bootstrap` passou a testar `sys.prefix` (ambiente ativo), não o binário — um venv e seu Python-base resolvem para o mesmo executável, o que fazia o re-exec não disparar (descoberto no smoke real).
- **Dogfood:** `materialize` rodado na raiz deste repo regenerou a skill nos dois harnesses, removeu o `.claude/commands/encerrar-sessao.md` órfão e preservou o `SPEC.md` de terceiro.
- **Pré-existentes fora de escopo (não tocados):** `ruff` aponta `parser_decisions` não usado e `NotAGitRepositoryError` indefinido (F821, bug latente) em `main.py`; o CI não roda `ruff` (só `pytest`).

## Histórico de alterações

| Data       | Alteração                                  | Autor   |
| ---------- | ------------------------------------------ | ------- |
| 2026-06-28 | Versão inicial gerada por `/reversa-to-do` | reversa |
