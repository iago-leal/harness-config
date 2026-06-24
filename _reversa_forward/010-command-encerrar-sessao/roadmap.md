# Roadmap: Comando de IDE para encerrar a sessão (materializado pelo `init`)

> Identificador: `010-command-encerrar-sessao`
> Data: `2026-06-24`
> Requirements: `_reversa_forward/010-command-encerrar-sessao/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A feature replica o padrão consolidado na feature 009 (`materialize_hooks_json`): uma **rotina única de materialização**, compartilhada por `init` e `upgrade`, que grava artefatos de comando dentro do repositório-alvo. Aqui ela escreve **dois arquivos de slash command** que disparam o `encerrar-sessao` já existente no `CommandService` — um para o Claude Code (`.claude/commands/encerrar-sessao.md`) e um para o Antigravity (`.agents/workflows/encerrar-sessao.md`). A escrita acontece **sempre para os dois harnesses**, sem o gate `active_harness` que condiciona `materialize_hooks_json`, porque o requirements decidiu cobertura dupla incondicional. O conteúdo de cada arquivo permanece encapsulado no respectivo `HarnessProfile` (estratégia já existente), de modo que a rotina apenas itera os perfis que expõem comando de IDE e grava o que cada um produz — nenhum `if active_harness` novo no serviço. Footprint global zero (RN-N17) e não-destrutividade (RN-N20) são herdados do molde e fixados por teste.

## 2. Princípios aplicados

> `.reversa/principles.md` **não existe** neste projeto. Não há princípios formais versionados a verificar. Aplicam-se os princípios de domínio já confirmados em `_reversa_sdd/` e as preferências globais do mantenedor (footprint zero, baixo acoplamento, longevidade).

| Princípio                                                                      | Como a feature se relaciona                                                                                                                               | Status   |
| ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Footprint global zero (`_reversa_sdd/domain.md#RN-N17`)                        | Toda escrita ocorre sob `project_path`; fixado por teste com `RecordingFileSystem`                                                                        | respeita |
| Baixo acoplamento / core agnóstico ao harness (`_reversa_sdd/domain.md#RN-N5`) | O comando delega ao `./harness cmd encerrar-sessao`; nenhum serviço de domínio ramifica por harness; o conhecimento por-harness vive nos `HarnessProfile` | respeita |
| Evolução não-destrutiva (`_reversa_sdd/domain.md#RN-N20`)                      | A rotina só grava o arquivo `encerrar-sessao` de cada harness; arquivos de comando de terceiros ficam intactos                                            | respeita |
| Rotina única compartilhada (`_reversa_sdd/domain.md#RN-N27`)                   | `init` e `upgrade` chamam a mesma função, sem duplicação                                                                                                  | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                                                 | Justificativa                                                                                                                                                                                                                                                                                                                                                                                                                                 | Alternativas descartadas                                                                                                                                                             | Confidência                                                                                           |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- | --- |
| D-01 | Novo módulo `src/core/install/session_commands.py` com a rotina única `materialize_session_commands(fs, project_path, command_path)`, espelhando `antigravity_hooks.py`                                 | Reaproveita molde testado e o contrato de footprint/atomicidade já validado                                                                                                                                                                                                                                                                                                                                                                   | Embutir a lógica em `init_service.py` (acopla materialização ao bootstrap, dificulta reuso por `upgrade`)                                                                            | 🟢                                                                                                    |
| D-02 | O conteúdo e o caminho de cada arquivo de comando ficam **encapsulados nos `HarnessProfile`** via um novo método de capacidade (ex.: `session_command_artifact(command_path) -> (rel_path, content)     | None`); a rotina itera os perfis e ignora os que devolvem `None`                                                                                                                                                                                                                                                                                                                                                                              | Mantém a estratégia por harness coesa (RN-N5), evita `if`s espalhados e deixa a extensão a outros harnesses aberta; Gemini devolve `None` (sem superfície de slash command definida) | Hardcodar os dois conteúdos dentro do materializador (espalha conhecimento de harness fora do perfil) | 🟢  |
| D-03 | `init`/`upgrade` chamam `materialize_session_commands` **incondicionalmente** (fora do gate `active_harness == "..."`), passando `command_path = os.path.abspath(target_path)`                          | Requirements decidiu "sempre Claude + Antigravity" (Esclarecimentos · 2026-06-24)                                                                                                                                                                                                                                                                                                                                                             | Gate por `active_harness`, como `materialize_hooks_json` (contraria a decisão do requirements)                                                                                       | 🟢                                                                                                    |
| D-04 | Comando do Claude usa `./harness cmd encerrar-sessao` (relativo à raiz) via `!`-bash embutido; comando do Antigravity usa o caminho **absoluto** (`command_path`) resolvido na materialização           | **Revisado pós-implementação (2026-06-24):** `${CLAUDE_PROJECT_DIR}` **não** é expandida no `!`-bash de slash commands — só em hooks — então virava `/harness` e quebrava (`/harness: no such file`; Claude Code issue #33815). O `!`-bash roda com cwd na raiz do projeto, logo `./harness` resolve, sobrevive a repo movido e casa com o `allowed-tools`. O Antigravity segue com absoluto (sem env var garantida); o `upgrade` o reescreve | `${CLAUDE_PROJECT_DIR}/harness` — **descartado**: a premissa de que espelhar os hooks funcionaria em slash commands era falsa (não expande nesse contexto)                           | 🟢                                                                                                    |
| D-05 | A rotina **sobrescreve** apenas o arquivo `encerrar-sessao` de cada harness (idempotente); demais arquivos no diretório de comandos não são lidos nem tocados                                           | Mesma semântica de "own the named key" de `materialize_hooks_json` (que substitui só o named-hook `harness`); não-destrutivo perante terceiros                                                                                                                                                                                                                                                                                                | Merge de conteúdo dentro de um único arquivo (desnecessário: cada comando é arquivo próprio)                                                                                         | 🟢                                                                                                    |
| D-06 | O acionamento do Antigravity é descrito como execução direta de `./harness cmd encerrar-sessao`; se o modelo de workflow do Antigravity não permitir shell embutido, o corpo instrui o agente a rodá-lo | A doc de workflows do Antigravity não confirma execução de shell embutida; o Claude tem `!`-bash determinístico, o Antigravity é inferido                                                                                                                                                                                                                                                                                                     | Assumir paridade total de execução com o Claude sem verificação                                                                                                                      | 🟡                                                                                                    |

## 4. Premissas

| Premissa                                                                                                                                                      | Origem (`requirements.md` seção)                                     | Risco se errada                                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| O Antigravity registra `.agents/workflows/encerrar-sessao.md` como slash command no chat e permite (ou instrui) a execução de `./harness cmd encerrar-sessao` | §2 (contexto Antigravity, 🟡) e Esclarecimentos (acionamento direto) | Se workflows do Antigravity não rodarem shell, o encerramento vira instrução ao agente (não-determinístico) em vez de execução imediata; o arquivo ainda aparece como comando |

## 5. Delta arquitetural

| Componente                      | Arquivo de origem no legado                                               | Tipo de mudança | Resumo                                                                                                      |
| ------------------------------- | ------------------------------------------------------------------------- | --------------- | ----------------------------------------------------------------------------------------------------------- |
| Serviço `install`               | `_reversa_sdd/architecture.md#1` (`src/core/install/`)                    | componente-novo | Novo `session_commands.py` (`materialize_session_commands`), irmão de `antigravity_hooks.py`                |
| Estratégia `HarnessProfile`     | `_reversa_sdd/architecture.md#5` (`src/core/install/harness_profiles.py`) | regra-alterada  | `ClaudeProfile` e `AntigravityProfile` ganham método de artefato de comando; `GeminiProfile` devolve `None` |
| Bootstrap `init`/`upgrade`      | `_reversa_sdd/domain.md#2.9` (`src/core/bootstrap/init_service.py`)       | regra-alterada  | `initialize_project` e `upgrade_project` passam a chamar `materialize_session_commands` (incondicional)     |
| Contrato de arquivos de comando | (novo)                                                                    | contrato-novo   | Formato dos dois arquivos materializados — detalhado em `interfaces/session-command-files.md`               |

## 6. Delta no modelo de dados

- Resumo das mudanças: nenhuma alteração de schema. Não há novo campo em `harness.toml`, nem mudança no estado de sessão (`.harness/estado-da-sessao.md`) ou no grafo de decisões. A "persistência" afetada são **dois novos arquivos de artefato** no disco do projeto-alvo.
- Detalhe completo em: `_reversa_forward/010-command-encerrar-sessao/data-delta.md`

## 7. Delta de contratos externos

| Contrato                                                                 | Tipo    | Arquivo de detalhe                                                                 |
| ------------------------------------------------------------------------ | ------- | ---------------------------------------------------------------------------------- |
| Arquivos de slash command consumidos pelo Claude Code e pelo Antigravity | arquivo | `_reversa_forward/010-command-encerrar-sessao/interfaces/session-command-files.md` |

## 8. Plano de migração

1. Criar `src/core/install/session_commands.py` com `materialize_session_commands`, espelhando `antigravity_hooks.py`.
2. Estender os `HarnessProfile` (Claude e Antigravity expõem o artefato de comando; Gemini devolve `None`).
3. Ligar a chamada incondicional em `initialize_project` e `upgrade_project`.
4. Adicionar testes (materializador, perfis, footprint, idempotência, integração init/upgrade).
5. Sem migração de dados retroativa: projetos já instalados recebem os comandos no próximo `./harness upgrade`.

## 9. Riscos e mitigações

| Risco                                                                | Impacto | Probabilidade | Mitigação                                                                                                                                                                          |
| -------------------------------------------------------------------- | ------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Workflow do Antigravity não executar shell embutido (D-06)           | médio   | médio         | Documentar o mecanismo exato no `interfaces/`; o corpo degrada para instrução ao agente; validar contra o Antigravity real quando disponível (alinha ao watch-item amarelo da 009) |
| Sobrescrever um `encerrar-sessao.md` que o usuário tenha customizado | baixo   | baixo         | A rotina é dona do nome `encerrar-sessao`; documentar que arquivos com esse nome são geridos pelo harness; demais arquivos preservados                                             |
| Caminho absoluto do Antigravity quebrar se o repo for movido         | baixo   | médio         | `upgrade` reescreve o absoluto (mesma mitigação de `materialize_hooks_json`)                                                                                                       |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] `init` em repo limpo cria `.claude/commands/encerrar-sessao.md` e `.agents/workflows/encerrar-sessao.md`
- [ ] Suíte pytest verde, incluindo teste de footprint do novo materializador
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-06-24 | Versão inicial gerada por `/reversa-plan` | reversa |
