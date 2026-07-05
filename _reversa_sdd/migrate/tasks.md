# Migrate (Conversão da Base Instalada para a Fonte Única) — Tarefas de Implementação

> Gerado pelo Writer em 2026-07-05 (feature 020-fonte-unica-e-hooks; unit NOVA)
> Sequência executável para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

## Pré-requisitos

- [ ] `FileSystemPort` com `remove_tree` implementado (adapter local + fakes de teste).
- [ ] `core/bootstrap/shim.render_shim` disponível (unit relacionada: bootstrap).
- [ ] `core/bootstrap/service.BootstrapService.install_hooks` já não-destrutivo (feature 020).
- [ ] `core/install/claude_settings.materialize_claude_settings` implementado (merge por-item).
- [ ] `core/domain/layout.{CORE_REL_PATH, CORE_MAIN_REL_PATH}` definidos.

## Tarefas

- [x] T-01, Implementar `MigrateService.migrate` (varredura da raiz)
  - Origem no legado: `core/migrate/service.py:MigrateService.migrate`
  - Critério de pronto: itera `_safe_list(root)`; ignora subpastas sem `harness.toml`; delega cada instalação encontrada a `_migrate_one`; devolve a lista agregada de resultados.
  - Confiança: 🟢 (já implementado no legado; tarefa registrada para reconstrução fiel)

- [x] T-02, Implementar as guardas de segurança (1, 2, 3)
  - Origem no legado: `core/migrate/service.py:MigrateService._migrate_one` (guardas)
  - Critério de pronto: nunca migra o próprio upstream (`upstream_self`); nunca migra autorreferência nem projeto sem `upstream_path`; recusa migrar se o core do upstream não existir no caminho esperado.
  - Confiança: 🟢

- [x] T-03, Implementar detecção de layout duplo (legado + pós-011)
  - Origem no legado: `core/migrate/service.py:_migrate_one` (`core_dir`, `legacy_dir`, `to_remove`)
  - Critério de pronto: detecta `.harness/harness-core/src/main.py` (pós-011) e `harness-core/src/main.py` (pré-011, raiz) independentemente; inclui os que existirem em `to_remove`.
  - Confiança: 🟢

- [x] T-04, Implementar o modo `--dry-run`
  - Origem no legado: `core/migrate/service.py:_migrate_one` (ramo `if dry_run`)
  - Critério de pronto: retorna `{"status": "would-migrate", "removes": to_remove}` sem nenhuma escrita ou remoção.
  - Confiança: 🟢

- [x] T-05, Implementar a conversão real, na ordem segura
  - Origem no legado: `core/migrate/service.py:_migrate_one` (passos pós-`dry_run`)
  - Critério de pronto: shim escrito e executável → ganchos git instalados (tolera `NotAGitRepositoryError`) → settings do Claude mesclados (se `active_harness == "claude"`) → campo `version` removido do `harness.toml` → cópia(s) do core removidas por último via `_safe_remove_core`.
  - Confiança: 🟢

- [x] T-06, Implementar `_safe_remove_core` (guarda de nome-base)
  - Origem no legado: `core/migrate/service.py:_safe_remove_core`
  - Critério de pronto: levanta `ValueError` se `os.path.basename(os.path.normpath(path)) != "harness-core"`; caso contrário, delega a `fs.remove_tree(path)`.
  - Confiança: 🟢

- [x] T-07, Integrar no driver CLI (`migrate`)
  - Origem no legado: `src/main.py` (subcomando `migrate`, args `root`/`--dry-run`)
  - Critério de pronto: `migrate` pulado do carregamento global de config e do check passivo de sync (junto com `init`/`upgrade`/`agy-hook`/`materialize`); default de `root` é `~/dev`.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Projeto igual a `upstream_self` → `status: "skipped"`, motivo "upstream (fonte do core)".
- [ ] TT-02, Projeto sem `upstream_path` ou com autorreferência → `status: "skipped"`.
- [ ] TT-03, Projeto com `upstream_path` para um caminho sem core → `status: "skipped"`, motivo "core do upstream ausente".
- [ ] TT-04, `--dry-run` sobre instalação elegível → `status: "would-migrate"`, nenhuma escrita/remoção real ocorre (verificar via fake fs que nada foi chamado além de leitura).
- [ ] TT-05, Instalação elegível sem `--dry-run` → shim gravado e executável, hooks git reescritos para o shim, settings mesclados, `version` removida do toml, `.harness/harness-core/` removida por último (ordem verificável no fake fs).
- [ ] TT-06, Caso de layout duplo (`harness-core/` na raiz + `.harness/harness-core/`) → ambos entram em `to_remove` e são removidos.
- [ ] TT-07, `_safe_remove_core` chamado com um caminho que não termina em `harness-core` → levanta `ValueError`, nenhum `remove_tree` é disparado.
- [ ] TT-08, Projeto sem `.git` → `install_hooks` levanta `NotAGitRepositoryError`, capturada; migração do projeto prossegue sem hooks.

## Ordem Sugerida

1. T-01 (varredura) e T-02 (guardas) primeiro — sem eles, nada mais é seguro de testar.
2. T-03 (detecção de layout) antes de T-04/T-05, que dependem de `to_remove` calculado.
3. T-04 (`--dry-run`) antes de T-05 (conversão real) — o modo seco é o caminho mais simples de validar a lógica de decisão sem efeitos colaterais.
4. T-06 (`_safe_remove_core`) pode ser desenvolvido em paralelo a T-05, mas integrado antes de qualquer execução real.
5. T-07 (integração CLI) fecha, depois que o serviço estiver testado isoladamente.

## Lacunas Pendentes (🔴)

- 🔴 **Sem mecanismo de rollback** se a conversão falhar no meio do processo (ver `design.md`, Riscos e Lacunas). Não é uma lacuna de extração — é uma lacuna real do sistema, candidata a ticket de manutenção caso se torne um problema prático.
- 🟡 **Idempotência de reexecução** não coberta por teste dedicado nesta extração — comportamento inferido, não confirmado.
