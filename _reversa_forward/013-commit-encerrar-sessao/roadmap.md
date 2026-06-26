# Roadmap: Versionar o estado da sessão ao encerrar

> Identificador: `013-commit-encerrar-sessao`
> Data: `2026-06-26`
> Requirements: `_reversa_forward/013-commit-encerrar-sessao/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

O delta é cirúrgico e mora em três pontos do `harness-core`. Primeiro, a porta
`GitPort` (`src/core/ports/git.py`) ganha um único método novo — `commit_paths` —,
implementado no `SubprocessGitAdapter` (`src/adapters/git/subprocess.py`) como um
`git add` restrito a caminhos explícitos seguido de `git commit`, devolvendo o hash do
novo HEAD. Segundo, o ramo `encerrar-sessao` de `CommandService.execute_command`
(`src/core/commands/service.py`) passa a, **depois** de `save_session`, commitar
**apenas** o `state_file`, reaproveitando a âncora já capturada com `get_head_commit`
**antes** de qualquer escrita; a falha de commit vira erro nomeado. Como a lógica vive
no serviço, vale igualmente para a CLI (`main.py`) e para a tool MCP (`server.py`), que
chamam o mesmo `execute_command`. Terceiro, os corpos de `session_command_artifact`
nos `HarnessProfile` (`src/core/install/harness_profiles.py`) são reescritos para
descrever o commit real, exigindo bump de versão e rematerialização (lição da feature
012). Nenhum modelo de dados muda.

## 2. Princípios aplicados

> `.reversa/principles.md` não existe neste projeto. Na ausência dele, registro abaixo
> os princípios do core (CLAUDE.md do `harness-core` e domínio extraído) que a feature
> observa. Nenhum princípio é reescrito aqui (isso seria tarefa de `/reversa-principles`).

| Princípio                            | Como a feature se relaciona                                                                                                 | Status   |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- | -------- |
| Baixo acoplamento (Ports & Adapters) | O domínio comita só pela porta `GitPort`; o `git` concreto fica no adapter. Preserva RN-N5.                                 | respeita |
| Falha barulhenta                     | Commit que não pode ser criado levanta erro nomeado, nunca sucesso silencioso. Alinha a RN-N4.                              | respeita |
| Alta coesão / SRP                    | A persistência fica no serviço de comandos; o adapter ganha um método com responsabilidade única (commitar caminhos dados). | respeita |
| Footprint per-projeto                | Toda escrita ocorre sob `repo_path`; o commit não toca config global nem arrasta arquivos alheios (RN-02).                  | respeita |
| Reprodutibilidade temporal           | O fechamento passa a ser um commit no histórico, retomável meses depois sem `git` manual.                                   | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                             | Justificativa                                                                                                          | Alternativas descartadas                                                                                    | Confidência |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ----------- |
| D-01 | Adicionar `commit_paths(repo_path, paths, message) -> str` ao `GitPort` e implementá-lo no `SubprocessGitAdapter`.                                                  | Contrato explícito pedido no requirements (RF-01); mantém o domínio agnóstico ao `git` concreto (RN-N5).               | Chamar `subprocess` direto no serviço (acopla domínio à infra); reusar um método genérico de shell.         | 🟢          |
| D-02 | A persistência vive no ramo `encerrar-sessao` de `CommandService.execute_command`, após `save_session`.                                                             | Reside no serviço compartilhado → vale CLI **e** MCP sem duplicar lógica (RN-01).                                      | Commitar no `main.py`/`server.py` (duplicaria e divergiria entre superfícies).                              | 🟢          |
| D-03 | Âncora = `get_head_commit(repo_path)` capturada **antes** de `close_session`/`save_session`; o commit de encerramento vem **depois**.                               | A âncora deve seguir o último commit de **trabalho**; o de encerramento fica por cima (RN-03/RF-04).                   | Capturar o HEAD após commit (apontaria para o próprio encerramento — bug destacado no requirements).        | 🟢          |
| D-04 | Commitar **somente** `[session_filepath]`; o adapter faz `git add -- <paths>` (pathspec explícito), nunca `git add -A`.                                             | Evita arrastar `AGENTS.md`/`CLAUDE.md`/regras pendentes para o commit (RN-02/RF-03).                                   | `git add -A` / `git commit -a` (contaminaria o commit — bug destacado no requirements).                     | 🟢          |
| D-05 | Falha de `commit_paths` é traduzida em erro nomeado novo `SessionCommitError` (`src/core/commands/errors.py`); o `state_file` salvo é preservado.                   | Falha barulhenta (RN-N4/RN-05/RF-06) sem reverter o registro já gravado.                                               | Deixar vazar `RuntimeError` genérico do adapter (menos legível); reverter o arquivo (perderia a narrativa). | 🟢          |
| D-06 | Mensagem de commit: `chore(sessao): encerrar sessão <feature>; âncora <ancora>`, sem trailer de co-autoria.                                                         | RN-04; padrão de mensagem limpa do projeto.                                                                            | Incluir co-autoria (proibido); mensagem genérica sem âncora.                                                | 🟢          |
| D-07 | Mensagem de retorno reporta os dois hashes (âncora do trabalho + hash do encerramento).                                                                             | RF-05/RN-06; legibilidade do fechamento.                                                                               | Manter só a âncora (estado atual, incompleto).                                                              | 🟡          |
| D-08 | Reescrever a `description`/corpo de `session_command_artifact` (Claude e Antigravity); **bump de versão** 1.2.48 → 1.2.49 e **rematerializar** os artefatos locais. | Texto exibido deve concordar com o efeito (RF-08); mudar materializador sem bump distribui artefato stale (lição 012). | Mudar a string sem bump (upgrade regravaria stale); deixar o texto impreciso.                               | 🟢          |
| D-09 | Testes com **Git fake explícito** que modela a transição de HEAD (antes→depois do commit) em `tests/test_commands.py`, ajustando `test_execute_encerrar_sessao`.    | Permite asserir âncora = HEAD pré-commit, paths commitados e os dois hashes (RF-07).                                   | Só `MagicMock(spec=GitPort)` (não modela a progressão de HEAD com naturalidade).                            | 🟢          |

## 4. Premissas

> Nenhuma premissa pendente. As três dúvidas do requirements foram resolvidas em
> `/reversa-clarify` (Sessão 2026-06-26) e estão fixadas como regras (RN-01, RN-05/RF-06, RF-08).

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
| -------- | -------------------------------- | --------------- |
| n/a      | —                                | —               |

## 5. Delta arquitetural

| Componente                                | Arquivo de origem no legado                                                                          | Tipo de mudança   | Resumo                                                                                      |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------- |
| `GitPort` (porta)                         | `_reversa_sdd/domain.md#RN-N5`; `src/core/ports/git.py`                                              | contrato-alterado | Novo método `commit_paths(repo_path, paths, message) -> str`.                               |
| `SubprocessGitAdapter`                    | `src/adapters/git/subprocess.py`                                                                     | regra-alterada    | Implementa `commit_paths` via `git add -- <paths>` + `git commit -m`, retorna HEAD.         |
| `CommandService` (ramo `encerrar-sessao`) | `_reversa_sdd/comandos-customizados/requirements.md`; `src/core/commands/service.py`                 | regra-alterada    | Após `save_session`, commita só o `state_file`; reporta dois hashes; erro nomeado na falha. |
| Erros de comandos                         | `src/core/commands/errors.py` (novo)                                                                 | componente-novo   | `SessionCommitError` (falha barulhenta de commit).                                          |
| `ClaudeProfile` / `AntigravityProfile`    | `_reversa_sdd/comandos-customizados/requirements.md#✨-f010`; `src/core/install/harness_profiles.py` | regra-alterada    | Reescreve `description`/corpo do `session_command_artifact` para descrever o commit.        |
| Versão do core                            | `src/core/domain/config.py`, `src/core/bootstrap/init_service.py`                                    | regra-alterada    | Bump 1.2.48 → 1.2.49 (gate de rematerialização não-stale).                                  |

> O `GitPort` é contrato **interno** (porta hexagonal), não um contrato externo
> HTTP/fila/gRPC/GraphQL — por isso não há diretório `interfaces/` nesta feature.

## 6. Delta no modelo de dados

- Resumo das mudanças: **nenhuma**. `SessionState`/`SessionNarrative` e o formato do
  artefato `.harness/estado-da-sessao.md` permanecem idênticos. O que muda é o
  **ciclo de vida git** do arquivo: deixa de ficar pendente no working tree e passa a
  ser versionado por um commit dedicado.
- Detalhe completo em: `_reversa_forward/013-commit-encerrar-sessao/data-delta.md`

## 7. Delta de contratos externos

| Contrato                                          | Tipo | Arquivo de detalhe |
| ------------------------------------------------- | ---- | ------------------ |
| n/a (sem contrato externo HTTP/fila/gRPC/GraphQL) | —    | —                  |

## 8. Plano de migração

1. Adicionar `commit_paths` à porta `GitPort` e implementá-lo no `SubprocessGitAdapter`.
2. Criar `src/core/commands/errors.py` com `SessionCommitError`.
3. Alterar o ramo `encerrar-sessao` do `CommandService`: capturar âncora antes, commitar só o `state_file` após `save_session`, reportar dois hashes, traduzir falha em `SessionCommitError`.
4. Reescrever a `description`/corpo dos `session_command_artifact` (Claude e Antigravity).
5. Bump de versão 1.2.48 → 1.2.49 em `config.py` e `init_service.py`.
6. Rematerializar os artefatos locais (`.claude/commands/encerrar-sessao.md`, `.agents/workflows/encerrar-sessao.md`) a partir do código já corrigido pós-bump.
7. Rodar a suíte `pytest` completa e o smoke do `onboarding.md`; confirmar verde sem regressão.

## 9. Riscos e mitigações

| Risco                                                                                        | Impacto | Probabilidade | Mitigação                                                                                               |
| -------------------------------------------------------------------------------------------- | ------- | ------------- | ------------------------------------------------------------------------------------------------------- |
| `git add -A` acidental arrasta arquivos alheios para o commit.                               | alto    | baixo         | Lista de caminhos explícita + `--` pathspec; teste que asserta um único arquivo no commit (RF-03).      |
| Âncora capturada após o commit apontaria para o próprio encerramento.                        | alto    | baixo         | Capturar `get_head_commit` antes de qualquer escrita; teste âncora = HEAD pré-commit (RF-04).           |
| Mudar o materializador sem bump/rematerialização distribui texto stale no `upgrade`.         | médio   | médio         | Bump 1.2.48→1.2.49 + rematerializar (D-08); alinhado à trilha não-stale da feature 012.                 |
| Commit falha por identidade git ausente ou repo sem commits (`get_head_commit` falha antes). | médio   | baixo         | Erro nomeado barulhento; estado salvo preservado (RN-05/RF-06); decisão registrada nos Esclarecimentos. |
| `test_execute_encerrar_sessao` atual quebra (mensagem muda; spec sem `commit_paths`).        | baixo   | alto          | Atualizar o teste para o Git fake explícito e a nova mensagem (D-09).                                   |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] `commit_paths` na porta + adapter, com teste do isolamento (só o `state_file`)
- [ ] Âncora pré-commit e dois hashes na saída cobertos por teste (Git fake)
- [ ] Falha de commit levanta `SessionCommitError` e preserva o estado salvo (teste)
- [ ] Texto dos slash commands reescrito (Claude e Antigravity), versão bumpada e artefatos rematerializados
- [ ] Suíte `pytest` verde sem regressão
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-06-26 | Versão inicial gerada por `/reversa-plan` | reversa |
