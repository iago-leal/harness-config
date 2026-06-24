# Actions: Comando de IDE para encerrar a sessão (materializado pelo `init`)

> Identificador: `010-command-encerrar-sessao`
> Data: `2026-06-24`
> Roadmap: `_reversa_forward/010-command-encerrar-sessao/roadmap.md`

## Resumo

| Métrica                     | Valor                                |
| --------------------------- | ------------------------------------ |
| Total de ações              | 8                                    |
| Paralelizáveis (`[//]`)     | 3                                    |
| Maior cadeia de dependência | 5 (T001 → T002 → T006 → T007 → T008) |

## Fase 1, Preparação

<!-- Setup, scaffolding, migrações iniciais, configuração de infraestrutura local. -->

| ID   | Descrição                                                                                                                                                                                                                                                     | Dependências | Paralelismo | Arquivo alvo                                        | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | --------------------------------------------------- | ----------- | ------ |
| T001 | Criar o módulo `session_commands.py` com a assinatura `materialize_session_commands(fs, project_path, command_path, profiles=None)` como stub (corpo `raise NotImplementedError`), abrindo o ponto de import para os testes — irmão de `antigravity_hooks.py` | -            | -           | `harness-core/src/core/install/session_commands.py` | 🟢          | `[X]`  |

## Fase 2, Testes

<!-- Testes que precisam existir antes ou logo após o núcleo. -->

| ID   | Descrição                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Dependências | Paralelismo | Arquivo alvo                                               | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ---------------------------------------------------------- | ----------- | ------ |
| T002 | Escrever os testes do materializador: grava `.claude/commands/encerrar-sessao.md` e `.agents/workflows/encerrar-sessao.md` em projeto vazio; Claude referencia `${CLAUDE_PROJECT_DIR}/harness cmd encerrar-sessao` e Antigravity referencia `command_path` absoluto; escrita atômica via `write_file_atomic`; idempotência na reexecução; preserva arquivos de terceiros nos diretórios de comando; **nada escrito fora do `project_path`** (`RecordingFileSystem`/`FootprintViolation`) | T001         | `[//]`      | `harness-core/tests/test_session_commands_materializer.py` | 🟢          | `[X]`  |
| T003 | Escrever os testes dos perfis: `ClaudeProfile` e `AntigravityProfile` devolvem o artefato de comando (caminho relativo + conteúdo que invoca `./harness cmd encerrar-sessao`); `GeminiProfile` devolve `None`; o placeholder de caminho do Antigravity é resolvido por `command_path`                                                                                                                                                                                                    | -            | `[//]`      | `harness-core/tests/test_session_command_profiles.py`      | 🟡          | `[X]`  |
| T004 | Escrever/estender os testes de integração: `initialize_project` e `upgrade_project` chamam `materialize_session_commands` com `command_path = abspath(target)` **incondicionalmente** (em qualquer `active_harness`), materializando os dois arquivos                                                                                                                                                                                                                                    | T001         | `[//]`      | `harness-core/tests/test_init.py`                          | 🟢          | `[X]`  |

## Fase 3, Núcleo

<!-- Lógica central da feature. -->

| ID   | Descrição                                                                                                                                                                                                                                                                                                                                                                           | Dependências | Paralelismo | Arquivo alvo                                        | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | --------------------------------------------------- | ----------- | ------ |
| T005 | Implementar nos `HarnessProfile` o método de artefato de comando: `ClaudeProfile` → (`.claude/commands/encerrar-sessao.md`, corpo com `!`-bash em `${CLAUDE_PROJECT_DIR}/harness cmd encerrar-sessao`); `AntigravityProfile` → (`.agents/workflows/encerrar-sessao.md`, corpo que executa/instrui `<ABS>/harness cmd encerrar-sessao`); `GeminiProfile` → `None` (D-02, D-04, D-06) | T003         | -           | `harness-core/src/core/install/harness_profiles.py` | 🟡          | `[X]`  |
| T006 | Implementar `materialize_session_commands`: itera os perfis que expõem comando, resolve o caminho absoluto (substitui o placeholder por `command_path`), `makedirs` do diretório de cada harness e grava cada arquivo via `write_file_atomic`, ignorando perfis que devolvem `None`; toda escrita sob `project_path` (D-01, D-05)                                                   | T002, T005   | -           | `harness-core/src/core/install/session_commands.py` | 🟢          | `[X]`  |

## Fase 4, Integração

<!-- Cola com outras partes do sistema, contratos externos, ganchos. -->

| ID   | Descrição                                                                                                                                                                                              | Dependências | Paralelismo | Arquivo alvo                                      | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ----------- | ------------------------------------------------- | ----------- | ------ |
| T007 | Ligar a chamada a `materialize_session_commands(fs, target, abspath(target))` em `initialize_project` e em `upgrade_project`, **fora** do gate `active_harness == "antigravity"` (incondicional, D-03) | T006, T004   | -           | `harness-core/src/core/bootstrap/init_service.py` | 🟢          | `[X]`  |

## Fase 5, Polimento

<!-- Logs, telemetria, mensagens de erro, documentação curta. -->

| ID   | Descrição                                                                                                                                                           | Dependências     | Paralelismo | Arquivo alvo    | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------- | --------------- | ----------- | ------ |
| T008 | Rodar a suíte pytest completa e confirmar verde, incluindo o footprint do novo materializador e os caminhos Claude/Gemini/Antigravity já existentes (sem regressão) | T005, T006, T007 | -           | `harness-core/` | 🟢          | `[X]`  |

## Notas de execução

<!--
Reservado para /reversa-coding registrar avisos ou observações que surgiram durante a execução.
Não use isso para corrigir ações, edits manuais ficam fora desse arquivo, vão direto no código.
-->

- **Correção pós-T008 (bug em uso real, 2026-06-24):** o corpo do comando do Claude (T002/T005) passou de `${CLAUDE_PROJECT_DIR}/harness cmd encerrar-sessao` para `./harness cmd encerrar-sessao`. `${CLAUDE_PROJECT_DIR}` não é expandida no `!`-bash de slash commands — só em hooks — então virava `/harness` e quebrava (Claude Code issue #33815). O `!`-bash roda com cwd na raiz do projeto, então `./harness` resolve e casa com o `allowed-tools`. D-04 do roadmap revisado. Verificado de dentro de `dev/TECH+` (caminho feliz encerra e grava o âncora). Hooks seguem com `${CLAUDE_PROJECT_DIR}` (lá expande — verificado nos logs 2.1.191).

## Histórico de alterações

| Data       | Alteração                                  | Autor   |
| ---------- | ------------------------------------------ | ------- |
| 2026-06-24 | Versão inicial gerada por `/reversa-to-do` | reversa |
