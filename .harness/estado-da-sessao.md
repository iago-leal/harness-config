---
commit: 0c561f89aa9075ec21234f8b52bde5da487d9a55
feature: reversa-forward (roteamento) + brief da feature 015
start_time: '2026-07-01T14:12:36.864628+00:00'
status: inactive
---

## O que foi feito
- **Feature 020 (`fonte-unica-e-hooks`) partida do PCCP e conduzida pelo pipeline forward completo** (clarify → requirements → clarify → plan → to-do → coding em 3 blocos). Origem: queixa de **SSD** — cada `harness init` replicava o core e criava uma `.venv` de ~108 MB por projeto (medição: 17 instalações, ~1,6 GB, ~97% em venvs). Clarificado no PCCP que o gargalo era a **venv**, não os scripts; escolhida a **Opção B (fonte única total)**: o alvo passa a executar o core do **upstream** via shim.
- **Auditoria RF-08 (pilar de viabilidade):** varredura confirmou que **todos** os comandos resolvem os dados do projeto pelo `cwd` (`os.getcwd`, `load_config("harness.toml")`); os `__file__` apontam só para assets do core → a fonte única **não exige refatorar o core** (é troca de wrapper).
- **Bloco 1 — materializadores não-destrutivos** (`235cecd`): merge do `.claude/settings.json` por-**item** por assinatura no `command` (preserva hooks próprios do usuário no mesmo evento); `install_hooks` não-destrutivo (cria/atualiza/encadeia via `<hook>.local`) e via shim.
- **Bloco 2 — shim + init fonte única** (`6451a49`): `render_shim()` (novo `bootstrap/shim.py`); `initialize_project` deixa de copiar o core e de criar venv, grava o shim, instala hooks in-process, `harness.toml` **sem `version`**.
- **Bloco 3 — `migrate`** (`105905c`): `MigrateService` + subcomando `migrate` (`--dry-run`) que converte a base; `remove_tree` novo no `FileSystemPort`; guardas fortes (nunca o upstream/autoreferência; `remove_tree` só aceita basename `harness-core`; core removido por último). Corrigido de passagem um F821 latente (`except NotAGitRepositoryError` sem import no `main.py`).
- **Verificação:** suíte do core **238 passed**; smoke real do shim (bash) e do `migrate --dry-run` OK. Meus arquivos novos passam no ruff (o CI roda só `pytest`).

## Próximos passos
- **PENDENTE CRÍTICO — rodar a migração real:** `cd ~/dev/harness && ./harness migrate ~/dev` (dry-run confirmou 13 projetos; upstream/raiz/`recicla-library` ficam de fora; `livro-mfc` remove os 2 layouts). Recupera **~1,5 GB**. **NÃO executado** — a salvaguarda de auto-mode bloqueou a destruição em massa fora do repo; o mantenedor deve disparar manualmente.
- **Feature 021 (descontinuação de `sync`/`upgrade`/oferta-014):** desescopada da 020. A varredura mostrou que `SyncService`/`upgrade_project` sustentam a **oferta de upgrade ao encerrar** (014) via `offers.py`/`close_flow.py`/MCP; removê-los desmancha parte do fluxo de encerramento — merece ciclo próprio. T008/T009/T013/T015/T016 seguem `[ ]`.
- **T018/T019/T020 da 020:** T018/T019 ficaram parcialmente obsoletos pelo desescopo; resta o **T020 — smoke end-to-end com git real** do `init` fonte única e do `migrate` em sandbox.
- **Re-extração** (`/reversa`) para reconciliar o `_reversa_sdd/` com a 020 (RN-N15/N17/N19 modificadas; RN-08 nova; `remove_tree` no port).
- **Dívida pré-existente registrada:** 5 avisos de ruff cosméticos (F401/F841 em `cache.py`, `main.py`, testes) — o CI não roda ruff; `current_version` órfão em `init_service` (sai com a 021).

## Pendências / bloqueios
- **Migração real bloqueada pela salvaguarda de auto-mode** — pendente de execução manual pelo mantenedor (comando acima). O disco ainda **não** foi recuperado.
- Sem bloqueios técnicos no código: 238 verdes, tudo commitado.

## Ponteiros
- Trilha forward da 020: `_reversa_forward/020-fonte-unica-e-hooks/` (requirements, roadmap, investigation, data-delta, onboarding, interfaces, actions, progress.jsonl, legacy-impact, regression-watch).
- Contratos: `interfaces/shim-execution.md`, `interfaces/claude-settings-merge.md`, `interfaces/git-hooks-merge.md`.
- Código novo: `src/core/bootstrap/shim.py`, `src/core/migrate/service.py`; `FileSystemPort.remove_tree`.
- Commits desta sessão: `235cecd`+`da107fd` (materializadores), `6451a49`+`e456eab` (shim+init), `105905c`+`0c561f8` (migrate).
- Âncora desta sessão: `0c561f8` (último commit de trabalho da 020).
