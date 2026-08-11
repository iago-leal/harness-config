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

### Re-extração 2026-08-11 11:26

> Re-verificação dirigida pós-features 024-027 (escopo por diff: `close_flow.py` tocado pela 024, que reescreveu o texto da oferta vigiada aqui). Suíte 372 verde.

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | `pending_work_paths` segue excluindo **apenas** o `state_file` (`p != session_file`, `close_flow.py:30`); a 024 mudou o texto e o protocolo da oferta (consultivo, RN-N48), não o universo de caminhos. |
| W002 | 🟢 verde | `list_dirty_paths` mantém `--porcelain --untracked-files=all`; origem intocada pelo delta. |
| W003 | 🟢 verde | `.gitignore` do alvo segue recebendo `SYNC_CACHE_GITIGNORE_ENTRY` em `init`/`upgrade`; origem intocada. |


### Re-extração 2026-07-15 19:22

> Re-verificação dirigida pós-feature 022: `close_flow.py` mudou (3º portão), mas `pending_work_paths` está intocado — confirmado por leitura direta (`return [p for p in dirty if p != session_file]`, close_flow.py:30).

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | Pré-check exclui apenas o `state_file`; decisões e índice de `.harness/` seguem entrando na oferta. O gate da 022 reforça o arranjo: seu anti-loop vive no próprio estado justamente porque o pré-check não mascara mais `.harness/` (MD-0015). |
| W002 | 🟢 verde | `SYNC_CACHE_GITIGNORE_ENTRY` deriva de `SYNC_CACHE_REL_PATH` (`layout.py`, MD-0013), inalterado. |
| W003 | 🟢 verde | Smoke com git real segue na suíte (`test_git_dirty.py` estendido na 022 com `list_changed_paths_since`, sem alterar os casos do porcelain). |

### Re-extração 2026-07-05 17:00

| ID   | Veredito | Observação                                                                                                                                                                                                     |
| ---- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | `close_flow.py:pending_work_paths` confirmado: `return [p for p in dirty if p != session_file]` — exclui só o arquivo de estado, não `.harness/` inteiro. Reconciliado em `domain.md#2.16` (RN-N34), ADR 0019. |
| W002 | 🟢 verde | `adapters/git/subprocess.py:list_dirty_paths` usa `["git", "status", "--porcelain", "--untracked-files=all"]` (linha 183), com comentário explícito citando a feature 019.                                     |
| W003 | 🟢 verde | `init_service.py` chama `_ensure_gitignore_entry(target_path, SYNC_CACHE_GITIGNORE_ENTRY)` em `initialize_project` (linha 141) e em `upgrade_project` (linha 242).                                             |

> Nota da re-extração: a divergência de nome do cache de sync entre CLI (`sync-cache.json`, hífen) e MCP (`sync_cache.json`, underscore) — já apontada na "Observações" deste arquivo desde a criação — foi promovida a dívida técnica rastreada formalmente (**T7**) em `architecture.md`, `erd-complete.md` e `gaps.md#G-12` nesta reconciliação. Não afeta o veredito de W003 (que cobre o nome com hífen, correto).

## Arquivadas

<!-- Watch items promovidos a estáveis ou aposentados. -->
