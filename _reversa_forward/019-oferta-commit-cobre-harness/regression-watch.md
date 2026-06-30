# Regression-watch: oferta de commit pendente cobre o vão de `.harness/`

> Identificador: `019-oferta-commit-cobre-harness`
> Gerado por `/reversa-coding` em 2026-06-30. Itens a reconferir nas próximas re-extrações (`/reversa`).

## Watch items

| ID   | Origem (arquivo, seção)                                                                      | Regra esperada após a mudança                                                                                                                                          | Tipo de verificação | Sinal de violação                                                                                                                        |
| ---- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | `_reversa_sdd/domain.md#2.15` (RN-N33); `src/core/session/close_flow.py#pending_work_paths`  | O pré-check exclui **apenas** o `state_file` (`p != session_file`), não o diretório `.harness/`; decisões e índice de `.harness/` entram na oferta                     | redação + presença  | Descrição "exclui `.harness/`" reaparece; código volta a usar `harness_dir`/`startswith(harness_dir + "/")`                              |
| W002 | `src/adapters/git/subprocess.py#list_dirty_paths`                                            | `list_dirty_paths` usa `git status --porcelain --untracked-files=all`, listando arquivos individuais em subdiretórios não rastreados (mantendo a omissão de ignorados) | presença            | Comando volta a `--porcelain` sem `--untracked-files=all`; subdiretório novo colapsa numa linha-diretório                                |
| W003 | `src/core/bootstrap/init_service.py`; `src/core/domain/layout.py#SYNC_CACHE_GITIGNORE_ENTRY` | `init` e `upgrade` garantem `.harness/sync-cache.json` no `.gitignore` do alvo (idempotente, footprint zero)                                                           | presença            | `_ensure_gitignore_entry` deixa de ser chamado com `SYNC_CACHE_GITIGNORE_ENTRY` em qualquer um dos dois pontos → cache exposto na oferta |

## Observações (sem peso de regressão)

- **Divergência pré-existente, fora do escopo da 019:** `.harness/sync-cache.json` (hífen) em `close_flow.py`/`main.py` vs `.harness/sync_cache.json` (underscore) em `adapters/mcp/server.py`. Se a faxina futura unificar o nome, alinhar W003 ao nome canônico escolhido.
- **Invariantes preservados (RN-N31/N32/N5):** não são watch de regressão desta feature (não foram modificados), mas a suíte os cobre — qualquer quebra apareceria em `test_close_flow.py`/`test_adapters.py`.

## Histórico de re-extrações

<!-- Preenchido pelo agente reverso ao rodar /reversa novamente. -->

## Arquivadas

<!-- Watch items promovidos a estáveis ou aposentados. -->
