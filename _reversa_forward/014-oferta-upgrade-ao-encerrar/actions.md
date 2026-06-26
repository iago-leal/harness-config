# Actions: Ofertas de fim de sessão — push e upgrade

> Identificador: `014-oferta-upgrade-ao-encerrar`
> Data: `2026-06-26`
> Roadmap: `_reversa_forward/014-oferta-upgrade-ao-encerrar/roadmap.md`

## Resumo

| Métrica                     | Valor                                                     |
| --------------------------- | --------------------------------------------------------- |
| Total de ações              | 15                                                        |
| Paralelizáveis (`[//]`)     | 4                                                         |
| Maior cadeia de dependência | 8 (T001 → T005 → T009 → T010 → T012 → T013 → T014 → T015) |

## Fase 1, Preparação

| ID   | Descrição                                                                                                                                                                                                                                                                                         | Dependências | Paralelismo | Arquivo alvo                                 | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | -------------------------------------------- | ----------- | ------ |
| T001 | Estender o contrato `GitPort` com os métodos abstratos novos (`fetch`, `get_current_branch`, `get_default_branch`, `count_commits_ahead`, `get_file_at_ref`, `is_working_tree_clean`, `merge_ff_only`, `push`), cada um com docstring de contrato conforme `interfaces/git-port-delta.md` (D-03). | -            | -           | `src/core/ports/git.py`                      | 🟢          | `[X]`  |
| T002 | Atualizar todos os dublês/fakes de `GitPort` nos testes para implementar os novos métodos abstratos (evitar erro de instanciação de classe abstrata); extrair um `FakeGitBase` comum se reduzir repetição.                                                                                        | T001         | -           | `tests/helpers.py`, `tests/test_commands.py` | 🟢          | `[X]`  |

## Fase 2, Testes

| ID   | Descrição                                                                                                                                                                                                                                                                                  | Dependências | Paralelismo | Arquivo alvo                                  | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ----------- | --------------------------------------------- | ----------- | ------ |
| T003 | Testes do `SubprocessGitAdapter` para os métodos novos num repo git temporário (e remoto bare local): branch corrente/default, `count_commits_ahead` com e sem tracking, `get_file_at_ref`, working tree limpo/sujo, `merge_ff_only` (FF aplica; não-FF não aplica), `push` sem `--force`. | T001         | `[//]`      | `tests/test_adapters.py`                      | 🟢          | `[X]`  |
| T004 | Testes da comparação de versão remota do `SyncService` com git fake: versão remota > local → devolve alvo; igual → `None`; `fetch` falha → `None` sem exceção (resiliência).                                                                                                               | T002         | `[//]`      | `tests/test_sync.py`                          | 🟢          | `[X]`  |
| T005 | Testes do `EndSessionOffersService.detect` com git fake: ahead>0 → `PushOffer`; sem tracking ou em dia → push `None`; branch principal → `is_default_branch=True`; upstream à frente → `UpgradeOffer`; sem `upstream_path` → upgrade `None`; falha de git → degrada sem exceção.           | T002         | `[//]`      | `tests/test_offers.py` (novo)                 | 🟢          | `[X]`  |
| T006 | Testes da borda das ofertas no ramo `cmd encerrar-sessao`: com TTY simulado, `s`/`n` executa/pula na ordem push→upgrade; sem TTY, emite os marcadores e não lê entrada; falha de detecção/ação não trava o encerramento; "nenhuma sessão ativa" não dispara ofertas (D-10).                | T002         | -           | `tests/test_cli.py`, `tests/test_commands.py` | 🟡          | `[X]`  |

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                                                                                                                                                 | Dependências     | Paralelismo | Arquivo alvo                        | Confidência | Status |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------- | ----------------------------------- | ----------- | ------ |
| T007 | Implementar os métodos novos no `SubprocessGitAdapter` no molde atual (`CalledProcessError → RuntimeError`): `count_commits_ahead` devolve `0` sem tracking; `push` nunca usa `--force`; `merge_ff_only` sinaliza não-FF sem aplicar; `get_default_branch` com fallback `{main,master}` (D-03/D-06/D-07). | T001, T003       | -           | `src/adapters/git/subprocess.py`    | 🟢          | `[X]`  |
| T008 | Estender `SyncService` com a comparação de versão **remota**: `fetch` no upstream + `get_file_at_ref(<remote>/<branch>:<config>)` + regex de versão reusado, varrendo `CORE_CONFIG_CANDIDATE_RELPATHS`; read-only e resiliente (D-04).                                                                    | T001, T004       | -           | `src/core/sync/service.py`          | 🟢          | `[X]`  |
| T009 | Criar `EndSessionOffersService` e os modelos `PushOffer`/`UpgradeOffer`/`EndSessionOffers`; `detect(repo_path, config)` agrega push (via `GitPort`) e upgrade (via `SyncService`), devolvendo campos `None` quando não se aplicam (D-02).                                                                 | T001, T005, T008 | -           | `src/core/session/offers.py` (novo) | 🟢          | `[X]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                                                                                                                                                                                                                                                                                             | Dependências     | Paralelismo | Arquivo alvo                           | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------- | -------------------------------------- | ----------- | ------ |
| T010 | Na borda (`main.py`, ramo `cmd`), após `encerrar-sessao` com sucesso (D-10), conduzir as ofertas: detectar via `EndSessionOffersService`; dupla camada por `sys.stdin.isatty()` (TTY `input [s/N]`; sem TTY, marcadores de `interfaces/session-end-offers.md`); ordem push→upgrade; push via `GitPort.push`; upgrade via `merge_ff_only` do upstream + `upgrade_project`; tudo sob `try/except` não-bloqueante (D-01/D-05/D-08/D-09). | T006, T007, T009 | -           | `src/main.py`                          | 🟢          | `[X]`  |
| T011 | Reescrever o corpo/`description` de `session_command_artifact` (Claude e Antigravity) para mencionar que o encerramento pode oferecer publicar o trabalho e atualizar o núcleo, consistente entre os perfis (RF-12).                                                                                                                                                                                                                  | -                | `[//]`      | `src/core/install/harness_profiles.py` | 🟡          | `[X]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                                                                                                                  | Dependências           | Paralelismo | Arquivo alvo                                                                  | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------- | ----------- | ----------------------------------------------------------------------------- | ----------- | ------ |
| T012 | Bump de versão (`config.py#version` e `init_service#current_version`), gate da rematerialização não-stale (D-11).                                                                                                                          | T007, T008, T009, T010 | -           | `src/core/domain/config.py`, `src/core/bootstrap/init_service.py`             | 🟢          | `[X]`  |
| T013 | Rodar a suíte `pytest` completa e confirmar verde sem regressão (adapters, sync, offers, commands, cli, footprint, e os fakes atualizados).                                                                                                | T010, T011, T012       | -           | `tests/`                                                                      | 🟢          | `[X]`  |
| T014 | Rematerializar os artefatos locais (`.claude/commands/encerrar-sessao.md`, `.agents/workflows/encerrar-sessao.md`) com o código pós-bump e confirmar que o texto novo aparece (não confiar na cópia em memória).                           | T012, T013             | -           | `.claude/commands/encerrar-sessao.md`, `.agents/workflows/encerrar-sessao.md` | 🟡          | `[X]`  |
| T015 | Smoke conforme `onboarding.md`: oferta de push (ahead) e na branch principal, branch em dia sem oferta, oferta de upgrade com sincronização ff-only, ordem push→upgrade, modo sem TTY (marcadores), degradação sob falha de rede e recusa. | T013, T014             | -           | (verificação)                                                                 | 🟢          | `[X]`  |

## Notas de execução

- **Reordenação técnica (T007 antecipado):** adicionar os métodos como `@abstractmethod`
  ao `GitPort` (T001) torna `SubprocessGitAdapter` abstrato e quebra a instanciação em
  `test_adapters.py`. Para manter a suíte sempre instanciável, o T007 (implementação no
  adapter) foi executado logo após T001/T002, antes dos testes de comportamento — testes
  "junto ao" núcleo em vez de estritamente antes. Os IDs e o conteúdo das ações não mudaram.
- **Fakes de `GitPort`:** o único dublê concreto era `FakeGit` em `tests/test_commands.py`
  (atualizado em T002); os demais usam `MagicMock(spec=GitPort)`, que absorve os métodos novos.
- **Bump:** `1.2.49 → 1.2.50` (T012); `tests/test_init.py` foi ajustado para a nova versão.
- **Verificação (T015):** smoke real em sandbox derivado — encerramento + `[HARNESS:PUSH_DISPONIVEL
ahead=2 principal=true]` em modo não-TTY (exit 0) e degradação com upstream inalcançável
  (sem oferta de upgrade enganosa, push preservado). Suíte: 178 passed.

## Histórico de alterações

| Data       | Alteração                                  | Autor   |
| ---------- | ------------------------------------------ | ------- |
| 2026-06-26 | Versão inicial gerada por `/reversa-to-do` | reversa |
