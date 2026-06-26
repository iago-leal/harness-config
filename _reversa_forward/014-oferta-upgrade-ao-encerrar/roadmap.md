# Roadmap: Ofertas de fim de sessão — push e upgrade

> Identificador: `014-oferta-upgrade-ao-encerrar`
> Data: `2026-06-26`
> Requirements: `_reversa_forward/014-oferta-upgrade-ao-encerrar/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

O fechamento da sessão (feature 013, `CommandService.execute_command`) fica **intocado**.
As ofertas são uma etapa **posterior**, na borda (`main.py`, ramo `cmd`), que só roda após
um `encerrar-sessao` bem-sucedido e sempre sob `try/except` não-bloqueante. A detecção do
que oferecer (há commits a publicar? há versão nova no upstream remoto?) vai para um serviço
de domínio novo e testável; a interação (pergunta `[s/N]` no terminal, ou marcadores
estruturados no modo sem terminal) e o disparo das ações ficam na borda, espelhando o molde
de `offer_git_init`. O `GitPort` ganha as capacidades que faltam — `fetch`, ler versão numa
ref remota, contar commits à frente, descobrir o branch corrente e o principal, sincronizar
o clone do upstream por fast-forward e `push`. O upgrade reusa `upgrade_project` existente; a
sincronização não-destrutiva do upstream acontece **no fluxo da oferta**, antes da chamada, e
não dentro do `upgrade` genérico — isolando a mudança e deixando `./harness upgrade` standalone
como está. Encerra com bump de versão para destravar a rematerialização dos slash commands.

## 2. Princípios aplicados

> `.reversa/principles.md` não existe neste projeto (não houve `/reversa-principles`). Aplicam-se
> os princípios operacionais do mantenedor (CLAUDE.md global) e as regras de negócio confirmadas
> em `_reversa_sdd/domain.md`.

| Princípio                               | Como a feature se relaciona                                                                                  | Status   |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------ | -------- |
| Camadas / SRP (nº5)                     | Detecção no domínio; interação e I/O na borda; fechamento da sessão não é tocado.                            | respeita |
| Baixo acoplamento (RN-N5)               | O domínio fala com git apenas pela porta `GitPort`; nenhum `subprocess` no serviço.                          | respeita |
| Erros barulhentos (RN-N4)               | Sincronização do upstream e falhas de ação avisam de forma explícita; nunca degradam em silêncio enganoso.   | respeita |
| Não-bloqueio / resiliência (RN-02 sync) | Toda a etapa de ofertas é não-bloqueante: jamais trava ou regride o encerramento já feito.                   | respeita |
| Footprint global zero (RN-N17)          | Nenhuma escrita fora do projeto; o push usa remoto e credencial já configurados.                             | respeita |
| Commit sem co-autoria                   | A feature não cria commits novos no push (publica os existentes); o commit de encerramento (013) já é limpo. | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                                                                                                                                | Justificativa                                                                                         | Alternativas descartadas                                                                                     | Confidência |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------- |
| D-01 | As ofertas vivem na **borda** (`main.py`, ramo `cmd`, após `execute_command`), não no `CommandService`.                                                                                                                                                                                | O fechamento (RN-N31) deve permanecer íntegro e o domínio não pode conhecer `stdin`/TTY (RN-N5).      | Embutir no `CommandService` (acopla I/O interativo ao domínio, fere SRP).                                    | 🟢          |
| D-02 | Novo serviço de domínio `EndSessionOffersService` (`src/core/session/offers.py`) detecta as ofertas e devolve modelos (`PushOffer`, `UpgradeOffer`), consumindo `GitPort`, `SyncService` e a config.                                                                                   | Mantém a lógica testável e a borda fina.                                                              | Lógica solta na borda (não testável, repete entre harnesses).                                                | 🟢          |
| D-03 | O `GitPort` ganha métodos novos: `fetch`, `get_file_at_ref`, `get_current_branch`, `get_default_branch`, `count_commits_ahead`, `merge_ff_only`, `is_working_tree_clean`, `push`. O `SubprocessGitAdapter` os implementa no molde atual (`CalledProcessError → RuntimeError`).         | Domínio agnóstico à infraestrutura (RN-N5); coesão no contrato de git.                                | Chamar `subprocess` direto no serviço (quebra RN-N5).                                                        | 🟢          |
| D-04 | Detecção da versão remota do upgrade: `fetch` no upstream + `get_file_at_ref(<remote>/<branch>:<config_rel_path>)` + regex de versão (o mesmo de `check_version_update`); **read-only**, não toca o working tree do upstream.                                                          | Detectar sem efeito colateral; reusa a varredura de `CORE_CONFIG_CANDIDATE_RELPATHS`.                 | `pull` no upstream só para detectar (efeito colateral desnecessário).                                        | 🟢          |
| D-05 | A sincronização do upstream antes do upgrade vive **no fluxo da oferta**: após o `fetch` da detecção, `merge_ff_only(<remote>/<branch>)` no upstream; se não for fast-forward (working tree sujo/divergente), **aborta barulhento** e não chama o upgrade. Só então `upgrade_project`. | Satisfaz RN-09 ao pé da letra, isola a mudança e não altera `./harness upgrade` standalone (007/012). | Embutir a sincronização no `upgrade_project` (muda o comando existente, exige reescrever testes de 007/012). | 🟢          |
| D-06 | Oferta de push só quando há **upstream tracking** e `count_commits_ahead('@{u}..HEAD') > 0`; o push é `git push` (respeita o tracking) **sem `--force`**.                                                                                                                              | RN-04/RN-06/RN-11: só publica quando há o que publicar e nunca reescreve histórico.                   | `git push -u` criando tracking (exige decidir remoto; sem tracking, não oferece).                            | 🟢          |
| D-07 | Branch principal: `get_default_branch` via `git symbolic-ref refs/remotes/origin/HEAD`, com fallback para `{main, master}`. Aviso reforçado quando o corrente é o principal.                                                                                                           | RN-05; heurística robusta o bastante para a salvaguarda.                                              | Lista fixa só de nomes (não cobre default custom).                                                           | 🟡          |
| D-08 | Dupla camada por `sys.stdin.isatty()` (molde `offer_git_init`): com TTY, `input [s/N]` por oferta na ordem **push → upgrade** (RN-10); sem TTY, emite marcadores estruturados estáveis no stdout e **não** lê entrada.                                                                 | RN-03/RN-10; cobre terminal e slash command.                                                          | Sempre interativo (trava o slash command) / sempre automático (remove o "se aceito").                        | 🟢          |
| D-09 | Toda a etapa de ofertas roda sob `try/except` não-bloqueante; falha de rede/push/sync/upgrade vira aviso em `stderr`, nunca propaga nem marca o encerramento como falho. O alerta passivo **local** (`check_version_update`) segue inalterado para os demais comandos.                 | RN-02/RN-07/RN-09; preserva o encerramento e a UX dos outros comandos.                                | Propagar exceções (travaria o fim da sessão).                                                                | 🟢          |
| D-10 | Disparo das ofertas condicionado ao **sucesso** do encerramento: a borda só oferece quando `execute_command('encerrar-sessao')` retornou mensagem de sucesso (não lançou `SessionCommitError` nem devolveu o "Erro: nenhuma sessão ativa").                                            | RN-01 ("ao encerrar com sucesso, e só então").                                                        | Oferecer sempre (ofereceria mesmo sem sessão ativa).                                                         | 🟡          |
| D-11 | Bump de versão (`config.py#version` e `init_service#current_version`) ao final.                                                                                                                                                                                                        | Gate da rematerialização não-stale dos slash commands (padrão das features 010/012/013).              | Não versionar (slash commands materializados ficariam com texto antigo).                                     | 🟢          |

## 4. Premissas

> Nenhuma premissa pendente: o `requirements.md` está sem `[DÚVIDA]`. As decisões 🟡 (D-07, D-10)
> são escolhas de implementação com fallback, não premissas sobre requisitos em aberto.

## 5. Delta arquitetural

| Componente                | Arquivo de origem no legado                                                                  | Tipo de mudança   | Resumo                                                                                              |
| ------------------------- | -------------------------------------------------------------------------------------------- | ----------------- | --------------------------------------------------------------------------------------------------- |
| Porta de Git              | `.harness/harness-core/src/core/ports/git.py` (`_reversa_sdd/sync-check/contracts.md#3`)     | contrato-alterado | Novos métodos: fetch, ler ref, branch corrente/default, ahead, ff-only, working-tree limpo, push.   |
| Adapter de Git            | `.harness/harness-core/src/adapters/git/subprocess.py`                                       | regra-alterada    | Implementa os novos métodos no molde `subprocess`→`RuntimeError`.                                   |
| Serviço de ofertas (novo) | `src/core/session/offers.py` (não existe hoje)                                               | componente-novo   | Detecta `PushOffer`/`UpgradeOffer` a partir de `GitPort`+`SyncService`+config.                      |
| Serviço de sincronia      | `.harness/harness-core/src/core/sync/service.py` (`_reversa_sdd/domain.md#2.1/2.9`)          | regra-alterada    | Ganha comparação de versão **remota** (fetch+ref) ao lado da local existente.                       |
| Borda CLI                 | `.harness/harness-core/src/main.py` (`_reversa_sdd/domain.md#2.9` RN-N21)                    | regra-alterada    | Após `cmd encerrar-sessao` com sucesso, conduz as ofertas (TTY/estruturado) e dispara push/upgrade. |
| Perfis de harness         | `.harness/harness-core/src/core/install/harness_profiles.py` (`_reversa_sdd/domain.md#2.12`) | regra-alterada    | Texto dos slash commands menciona as ofertas de fim de sessão (RF-12).                              |
| Versão/config             | `src/core/domain/config.py`, `src/core/bootstrap/init_service.py`                            | regra-alterada    | Bump de versão (gate de rematerialização).                                                          |
| `CommandService`          | `.harness/harness-core/src/core/commands/service.py` (`_reversa_sdd/domain.md#2.14`)         | **inalterado**    | O fechamento permanece como na 013; registrado para deixar explícito que não muda.                  |

## 6. Delta no modelo de dados

- Resumo das mudanças: não há novo estado **persistido**. As ofertas são efêmeras (calculadas
  no encerramento, não gravadas). Sem uso de cache/TTL (RN-07). A única gravação é o bump de
  `version` no `harness.toml` (config, não modelo de domínio).
- Detalhe completo em: `_reversa_forward/014-oferta-upgrade-ao-encerrar/data-delta.md`

## 7. Delta de contratos externos

| Contrato                                                  | Tipo                               | Arquivo de detalhe                                                                 |
| --------------------------------------------------------- | ---------------------------------- | ---------------------------------------------------------------------------------- |
| Porta de Git (`GitPort`)                                  | arquivo (contrato interno central) | `_reversa_forward/014-oferta-upgrade-ao-encerrar/interfaces/git-port-delta.md`     |
| Saída de ofertas de fim de sessão (consumida pelo agente) | arquivo (contrato de borda)        | `_reversa_forward/014-oferta-upgrade-ao-encerrar/interfaces/session-end-offers.md` |

> Integrações externas tocadas: o remoto do **projeto** (`git push`/ahead) e o remoto do
> **upstream do harness** (`git fetch`/`merge --ff-only`/ler ref), ambas via `subprocess` git
> no adapter. Não há HTTP/fila/gRPC/GraphQL.

## 8. Plano de migração

1. Estender `GitPort` e `SubprocessGitAdapter` com os métodos novos (D-03) e **atualizar todos os
   dublês/fakes de `GitPort`** nos testes para implementarem os novos métodos abstratos.
2. Estender `SyncService` com a comparação de versão remota (fetch + ler ref + regex), reusando
   `CORE_CONFIG_CANDIDATE_RELPATHS` (D-04).
3. Criar `EndSessionOffersService` (D-02) com modelos `PushOffer`/`UpgradeOffer` e testes.
4. Conduzir as ofertas na borda (`main.py`, D-01/D-08/D-09/D-10), incluindo a sincronização
   ff-only do upstream antes do `upgrade_project` (D-05).
5. Atualizar o texto dos slash commands (RF-12) e fazer o bump de versão (D-11).
6. Rodar a suíte, rematerializar os artefatos de IDE com o código pós-bump e smoke conforme o
   `onboarding.md`.

## 9. Riscos e mitigações

| Risco                                                                      | Impacto | Probabilidade | Mitigação                                                                                               |
| -------------------------------------------------------------------------- | ------- | ------------- | ------------------------------------------------------------------------------------------------------- |
| Novos `@abstractmethod` no `GitPort` quebram os fakes de teste existentes. | médio   | alto          | Atualizar todos os dublês na mesma mudança; teste da suíte como gate (D-03, passo 1).                   |
| Latência de rede (`fetch`/`push`) no fim da sessão.                        | baixo   | médio         | Etapa pontual e não-bloqueante; nunca trava o encerramento (D-09).                                      |
| Credencial/token do upstream ou do origin expirada.                        | médio   | médio         | Falha resiliente com aviso claro; sem oferta enganosa (RN-07/D-09).                                     |
| Detecção do branch principal por heurística falha em default custom.       | baixo   | baixo         | `symbolic-ref` + fallback `{main,master}`; só afeta o aviso reforçado, não o push em si (D-07).         |
| Detectar "sucesso" do encerramento por inspeção da mensagem é frágil.      | médio   | baixo         | Teste cobrindo "sem sessão ativa não oferece"; refactor futuro para resultado tipado registrado (D-10). |
| `merge --ff-only` no upstream falha por working tree sujo.                 | baixo   | médio         | Aborta barulhento sem sobrescrever; upgrade não roda (RN-09/D-05).                                      |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Suíte `pytest` verde, incluindo os novos testes de domínio e os fakes de `GitPort` atualizados
- [ ] Slash commands rematerializados com o texto pós-bump (Claude e Antigravity)
- [ ] Smoke do `onboarding.md`: oferta de push (ahead) e de upgrade (upstream à frente), recusa, e degradação sob falha de rede
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-06-26 | Versão inicial gerada por `/reversa-plan` | reversa |
