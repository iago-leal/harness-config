# Regression-watch: fonte única + hooks não-destrutivos

> Feature: `020-fonte-unica-e-hooks`
> Itens a manter verdadeiros nas próximas extrações reversas. **Rodada parcial** (bloco de materializadores); as próximas rodadas farão append (W003+), sem reciclar IDs.

## Watch items

| ID   | Origem (arquivo, seção)                                                                 | Regra esperada após a mudança                                                                                                                                                                                                                                                                   | Tipo de verificação | Sinal de violação                                                                                                                                                                  |
| ---- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | `src/core/bootstrap/service.py` · `domain.md#2.7` (RN-N15)                              | `install_hooks` é **não-destrutivo**: hook alheio de mesmo nome preservado em `<hook>.local` e encadeado; hook próprio (assinatura `Harness Core`) atualizado no lugar; ausente criado. Hooks de outro nome nunca tocados                                                                       | presença + redação  | Um `pre-commit`/`post-merge` do projeto sobrescrito sem preservar `.local`; ou a instalação apagando/alterando hook de outro nome                                                  |
| W002 | `src/core/bootstrap/service.py` · `domain.md#2.7` (RN-N15)                              | Os scripts de hook invocam o shim `./harness format` / `./harness decisions`, com guarda `[ -x ./harness ]` (não bloqueia se ausente); não referenciam mais o python local do core                                                                                                              | redação             | Hook voltando a chamar `.venv/bin/python3`/`src/main.py`; ou bloqueando o commit quando o shim está ausente                                                                        |
| W003 | `src/core/install/claude_settings.py` · feature 016/RN-05 (sob `domain.md#2.13` RN-N30) | `materialize_claude_settings` mescla **por-item** dentro do array de cada evento do harness, preservando itens próprios do usuário no mesmo evento; idempotente por assinatura                                                                                                                  | presença            | Um hook próprio do usuário em `SessionStart`/`PostToolUse`/`Stop` descartado após `materialize`/`init`; ou item do harness duplicado ao reexecutar                                 |
| W004 | `src/core/bootstrap/init_service.py` · `domain.md#2.9` (RN-N19)                         | `initialize_project` é fonte única: o alvo NÃO recebe `.harness/harness-core/` nem `.venv`; recebe o shim `harness`; `harness.toml` sem `version`; hooks instalados in-process                                                                                                                  | ausência + presença | `init` voltando a copiar o core / criar venv; `harness.toml` gravado com `version`; wrapper copiado em vez do shim                                                                 |
| W005 | `src/core/bootstrap/shim.py` · `domain.md#2.9` (RN-N19)                                 | O wrapper do alvo é o shim: resolve `upstream_path`, `cd` na raiz do projeto, executa o core do upstream; upstream ausente → stderr + exit ≠ 0                                                                                                                                                  | presença + redação  | Wrapper apontando para o core local do próprio alvo; ou execução degradada/silenciosa quando o upstream falta                                                                      |
| W006 | `src/core/migrate/service.py` · RN-08                                                   | `MigrateService.migrate` converte instalações copiadas → fonte única (shim, hooks, settings, `version` removido, `.harness/harness-core/` apagado por último); idempotente; `--dry-run` não escreve; NUNCA migra o upstream nem autoreferência; `remove_tree` só aceita basename `harness-core` | presença + ausência | migrate removendo o core do upstream; removendo árvore fora de `harness-core`; apagando o core antes de instalar shim/hooks; tocando `.harness/decisoes` ou hooks/settings alheios |
| W007 | `src/core/ports/fs.py` + `src/adapters/fs/local.py`                                     | `FileSystemPort` expõe `remove_tree`, implementado no adapter real (`shutil.rmtree`) e em todos os fakes; a validação do alvo é do chamador                                                                                                                                                     | presença            | Um subtipo de `FileSystemPort` sem `remove_tree` (quebra a ABC); ou `remove_tree` sem guarda no chamador                                                                           |
| W008 | `src/core/domain/config.py` · `domain.md#2.10` (RN-N16)                                 | Versão canônica única: o campo `version` de `HarnessSection` mantém o valor como **literal** na própria linha (contrato do regex de `_get_upstream_version`, 012/RN-03) e `CORE_VERSION` deriva dele; help da CLI (`main.py`) e `init_service.current_version` referenciam `CORE_VERSION`       | presença + redação  | Literal de versão duplicado divergente (help/`current_version` chumbados); campo `version` trocado por referência (quebra o regex da 012); teste de lockstep removido              |

## Observações (sem peso de regressão)

- A ativação semântica de skills no Antigravity segue como amarelo herdado (RN-N29/009/017), não afetada por este bloco.
- **Achado do smoke T020 (pré-existente, sem peso):** `cmd resume` num repo **sem nenhum commit** estoura traceback cru de `git rev-parse HEAD` (`CommandService.execute_command` → `SubprocessGitAdapter.get_head_commit`), anterior à 020 — viola RN-N4 (barulhento ≠ traceback); candidata a correção em feature futura.
- **Gap da fonte única no executor da skill:** o `_bootstrap.py` da skill `encerrar-sessao` (asset da 018) resolve o core só em `.harness/harness-core` local e não conhece `upstream_path` — em projetos migrados a skill falha e o desvio é `./harness cmd encerrar-sessao`. Registrado como feature candidata (corrigir o `resolve_core` para cair no upstream).

## Histórico de re-extrações

### Re-extração 2026-07-15 19:22

> Re-verificação dirigida pós-MD-0014 e feature 022: o delta tocou `claude_settings.py` (assinaturas) e `harness_profiles.py` (`hooks_block` do Claude). O merge por-item e os ganchos git não-destrutivos permanecem; a mudança de assinaturas é deliberada (MD-0014/022), não regressão.

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | `init` fonte única (shim, sem cópia de core/venv) inalterado. |
| W002 | 🟢 verde | Ganchos git seguem invocando `./harness format`/`./harness decisions` com guarda `[ -x ./harness ]`; `bootstrap/service.py` intocado pelo delta. |
| W003 | 🟢 verde | Merge por-item preservado; itens do usuário no mesmo evento sobrevivem (teste com `meu-notificador.sh` no Stop). Nota deliberada: itens `harness format` legados passam a ser tratados como de terceiros (preservados) — decisão MD-0014, registrada em gaps.md#G-15. |
| W004 | 🟢 verde | Guardas do `migrate` intocadas (upstream/autorreferência/`_safe_remove_core`). |
| W005 | 🟢 verde | `remove_tree` restrito ao migrate, inalterado. |
| W006 | 🟢 verde | `upgrade`/`SyncService` seguem ativos (desescopo documentado, ADR 0020/G-13), inalterado. |
| W007 | 🟢 verde | `CORE_VERSION` segue derivado do literal único (`2.1.1` após a 023 — bump legítimo, o mecanismo é o vigiado). |
| W008 | 🟢 verde | Footprint de escrita per-projeto preservado (`test_footprint.py` na suíte verde). |

### Re-extração 2026-07-05 17:00

| ID   | Veredito | Observação                                                                                                                                                                                                                                                  |
| ---- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | `bootstrap/service.py:_install_one_hook` confirmado: ausente→cria; assinatura `Harness Core` presente→atualiza no lugar; ausente a assinatura→preserva em `<hook>.local` e encadeia. Hooks de outro nome nunca lidos.                                       |
| W002 | 🟢 verde | `_pre_commit_script`/`_post_merge_script` confirmados: encadeiam `.local` primeiro, depois `if [ -x ./harness ]; then ./harness format/decisions; fi`; sem referência a `.venv/bin/python3` local.                                                          |
| W003 | 🟢 verde | `install/claude_settings.py` (`materialize_claude_settings`) confirmado por rastreabilidade em `comandos-customizados/tasks.md` T004 (merge por-item, testado em `test_install_claude_settings.py`).                                                        |
| W004 | 🟢 verde | `init_service.py:initialize_project` confirmado: sem cópia de core/venv; grava shim; `harness.toml` sem `version` para tomls novos; `install_hooks` chamado in-process.                                                                                     |
| W005 | 🟢 verde | `bootstrap/shim.py:render_shim` confirmado: resolve `upstream_path` via `sed` no `harness.toml`, `cd` para a raiz, valida `MAIN`/`PY`, senão `echo ... >&2; exit 1`; nunca degrada silenciosamente.                                                         |
| W006 | 🟢 verde | `migrate/service.py:MigrateService` confirmado: guardas 1/2/3 (upstream/autorreferência/core ausente), ordem shim→hooks→settings→remoção `version`→remoção do core por último, `_safe_remove_core` restrito a basename `harness-core`, `--dry-run` sem I/O. |
| W007 | 🟢 verde | `FileSystemPort.remove_tree` confirmado no port e no adapter (`adapters/fs/local.py`); guarda de uso fica no chamador (`MigrateService._safe_remove_core`), não no port — conforme esperado.                                                                |
| W008 | 🟢 verde | `CORE_VERSION = HarnessSection().version` (literal `"2.0.0"`) confirmado em `domain/config.py`; `main.py` usa `f"... v{CORE_VERSION}"` no parser; `InitializationService.current_version = CORE_VERSION`.                                                   |

> Nota da re-extração: o achado "`cmd resume` em repo sem commit estoura traceback cru" (Observações deste arquivo) permanece **não corrigido** — confirmado ainda presente em `CommandService.execute_command`/`SubprocessGitAdapter.get_head_commit`, sem tratamento novo. Não é regressão desta reconciliação (já era conhecido antes da 020); candidato a ticket de manutenção, registrado também em `_reversa_sdd/inventory.md` (achados de saúde).

## Arquivadas

<!-- Vazio. -->
