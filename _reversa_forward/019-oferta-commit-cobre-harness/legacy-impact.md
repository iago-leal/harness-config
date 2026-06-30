# Legacy-impact: oferta de commit pendente cobre o vão de `.harness/`

> Identificador: `019-oferta-commit-cobre-harness`
> Data: `2026-06-30`
> Extração de referência: `_reversa_sdd/` (domain.md, architecture.md)

## 1. Arquivos afetados

| Arquivo afetado                                                    | Componente (`_reversa_sdd/`)                                       | Tipo            | Severidade | Justificativa                                                                                                                      |
| ------------------------------------------------------------------ | ------------------------------------------------------------------ | --------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/session/close_flow.py`                                   | `SessionCloseFlow` / pré-check (`domain.md#2.15`, RN-N33)          | regra-alterada  | MEDIUM     | `pending_work_paths` passa a excluir só o `state_file`, não o diretório `.harness/`; muda o conjunto oferecido antes do fechamento |
| `src/adapters/git/subprocess.py`                                   | Adapter de `GitPort` (`architecture.md`, camada de infraestrutura) | regra-alterada  | MEDIUM     | `list_dirty_paths` passa a usar `--untracked-files=all`, expandindo subdiretórios não rastreados em arquivos                       |
| `src/core/bootstrap/init_service.py`                               | `BootstrapInitService` / materialização (`domain.md#2.13`, RN-N30) | regra-nova      | LOW        | `init` e `upgrade` garantem `.harness/sync-cache.json` no `.gitignore` do alvo                                                     |
| `src/core/domain/layout.py`                                        | Fonte única de caminhos do core (`domain.md#2.7`/`2.13`)           | componente-novo | LOW        | Nova constante `SYNC_CACHE_GITIGNORE_ENTRY`                                                                                        |
| `src/core/domain/config.py` + `src/core/bootstrap/init_service.py` | `HarnessConfig` / versão do core                                   | regra-alterada  | LOW        | Bump `1.2.55 → 1.2.56` em lockstep                                                                                                 |

## 2. Diff conceitual por componente

- **`SessionCloseFlow` / pré-check.** Antes, `pending_work_paths` derivava `harness_dir = session_file.split("/",1)[0]` e excluía todo `p == harness_dir or p.startswith(harness_dir + "/")` — o diretório `.harness/` inteiro. Agora exclui apenas `p == session_file`. Consequência: decisões (`.harness/decisoes/MD-*.md`) e o índice (`.harness/microdecisoes.md`) entram na oferta de commit pendente; só o `estado-da-sessao.md` (que o marcador de fechamento versiona) fica de fora. A orquestração de `run` (sequência pré-check → fechamento → ofertas) e o passo de fechamento permanecem idênticos.
- **Adapter de `GitPort` (`list_dirty_paths`).** Antes, `git status --porcelain` colapsava subdiretórios não rastreados numa linha-diretório (ex.: `.harness/`), tornando impossível separar o `state_file` do resto. Agora, `--untracked-files=all` lista cada arquivo, preservando a omissão de ignorados (o cache de sync não aparece). É a granularidade de que o pré-check depende.
- **`BootstrapInitService`.** A função `_ensure_gitignore_entry` (idempotente, footprint zero) passa a ser chamada também com `SYNC_CACHE_GITIGNORE_ENTRY`, nos mesmos dois pontos onde já registrava `CORE_GITIGNORE_ENTRY` (init in-process, upgrade via subprocesso). Protege o cache de runtime que o novo filtro, de outro modo, exporia.
- **Versão.** Bump de marca para propagação por `./harness upgrade`; sem mudança de comportamento própria.

## 3. Preservadas (regras 🟢 do `_reversa_sdd/domain.md` intactas)

- **RN-N31 (`#2.14`):** o commit de fechamento versiona **exclusivamente** o `state_file`, por cima do trabalho, via `commit_paths` (`git add -- <paths>`, nunca `-A`). Não tocado — verificado por `test_caminho_feliz_fecha_e_conduz_ofertas` (commit contém só `[STATE_FILE]`) e `test_adapters.py` (arquivo alheio permanece untracked).
- **RN-N32 (`#2.14`):** commit pela porta e falha barulhenta (`SessionCommitError`, exit ≠ 0). Intacto — `test_falha_de_commit_do_estado_aborta_barulhento`.
- **RN-N5 (`#2.3`):** o core **lista** o pendente (`list_dirty_paths`) mas nunca faz `git add` do trabalho; quem commita é agente/usuário. Preservado.
- **RN-N17 (`#2.8`):** footprint global zero — toda escrita de gitignore ocorre sob `target_path`. Preservado.
- **RN-N30 (`#2.13`):** `apply_local_materializers` e a materialização do `.gitignore` seguem o mesmo mecanismo (init in-process, upgrade com código novo); apenas uma entrada a mais.

## 4. Modificadas (regras 🟢 alteradas)

- **RN-N33 (`#2.15`), parte do pré-check de pendência (016):** a definição do conjunto "trabalho pendente" muda de _"fora de `.harness/`"_ para _"tudo exceto o `state_file`"_. O fluxo único e seus invariantes de fechamento permanecem; o que muda é o predicado do helper `pending_work_paths` e os textos de borda que o descrevem. Reconcilia o código com `016/interfaces/commit-pendente-marker.md#5`, que já declarava essa intenção.
