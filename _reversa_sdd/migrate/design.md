# Migrate (Conversão da Base Instalada para a Fonte Única) — Design Técnico

> Gerado pelo Writer em 2026-07-05 (feature 020-fonte-unica-e-hooks; unit NOVA)
> Foca no COMO a unit é construída, a partir do código legado lido. Escala: 🟢 / 🟡 / 🔴

## Interface

| Símbolo                                    | Assinatura                                                      | Retorno               | Observação                                                                  |
| ------------------------------------------ | --------------------------------------------------------------- | --------------------- | --------------------------------------------------------------------------- |
| `MigrateService.migrate`                   | `(root: str, dry_run: bool = False, upstream_self: str = None)` | `list`                | Varre `root`, devolve um dict de resultado por instalação encontrada.       |
| `MigrateService._migrate_one`              | `(proj, toml_path, dry_run, self_abs)` (privado)                | `dict`                | Decide guardas, aplica (ou simula) a conversão de uma instalação.           |
| `MigrateService._safe_remove_core`         | `(path: str)` (privado)                                         | `None`                | `remove_tree` só se `basename(path) == "harness-core"`; senão `ValueError`. |
| `MigrateService._safe_list`                | `(root: str)` (privado)                                         | `list`                | `fs.list_dir(root)`; qualquer exceção → `[]` (não propaga).                 |
| `MigrateService._field` / `_strip_version` | `(toml, name)` / `(toml)` (privados, `@staticmethod`)           | `str \| None` / `str` | Regex simples sobre o texto do TOML — não usa um parser TOML completo.      |

**Forma do resultado por instalação:** `{"project": str, "status": "migrated" | "would-migrate" | "skipped", "removed"/"removes": list[str], "reason"?: str}`.

## Fluxo Principal

1. **`migrate(root, dry_run, upstream_self)`:** resolve `root` para caminho absoluto; para cada nome em `_safe_list(root)`, monta `proj = root/name` e `toml_path = proj/harness.toml`; se `harness.toml` não existir, **ignora silenciosamente** (não é uma instalação do harness); senão, delega a `_migrate_one`. 🟢
2. **`_migrate_one(proj, toml_path, dry_run, self_abs)`:**
   a. Lê o `harness.toml` e extrai `upstream_path`/`active_harness` por regex (`_field`). 🟢
   b. **Guarda 1:** `proj_abs == self_abs` → `_skip(proj, "upstream (fonte do core)")`. 🟢
   c. **Guarda 2:** sem `upstream_path`, ou `upstream_path` resolve para dentro do próprio `proj_abs` → `_skip(proj, "upstream (autoreferência)" | "sem upstream_path")`. 🟢
   d. **Guarda 3:** `CORE_MAIN_REL_PATH` não existe sob o `upstream_path` resolvido → `_skip(proj, "core do upstream ausente")`. 🟢
   e. Detecta `core_dir` (`.harness/harness-core`, pós-011) e `legacy_dir` (`harness-core` na raiz, pré-011); monta `to_remove` com os que existirem. 🟢
   f. **Se `dry_run`:** retorna `{"status": "would-migrate", "removes": to_remove}` — **para aqui, nenhuma escrita**. 🟢
   g. **Senão, na ordem:** (i) escreve o shim (`render_shim()`) em `proj/harness` e torna executável; (ii) `BootstrapService(fs).install_hooks(proj)` — tolera `NotAGitRepositoryError` (projeto sem `.git`, segue sem hooks); (iii) se `active_harness == "claude"`, `materialize_claude_settings(fs, proj)`; (iv) reescreve o `harness.toml` sem o campo `version` (`_strip_version`); (v) **por último**, remove cada diretório em `to_remove` via `_safe_remove_core`. 🟢
3. **Retorno agregado:** `migrate` devolve a lista de dicts, um por instalação (elegível ou pulada). 🟢

## Fluxos Alternativos

- **Raiz ilegível (`_safe_list` falha):** devolve lista vazia — `migrate` retorna `[]`, sem traceback. 🟢
- **Projeto sem `.git` (guarda 2 do `BootstrapService`):** `install_hooks` levanta `NotAGitRepositoryError`, capturada e ignorada — o projeto segue migrado, só sem ganchos Git instalados. 🟢
- **Projeto com os dois layouts simultâneos (`livro-mfc`):** `to_remove` inclui `core_dir` **e** `legacy_dir`; ambos são removidos na mesma passada, por último. 🟢
- **`_safe_remove_core` recebe um caminho que não termina em `harness-core`:** levanta `ValueError` — interrompe a migração daquele projeto **antes** de qualquer `remove_tree`, sinalizando bug de chamada (nunca deveria ocorrer com os `to_remove` calculados no passo e; é uma segunda camada de defesa). 🟢

## Dependências

- `FileSystemPort` — `exists`, `read_file`, `write_file`, `make_executable`, `list_dir`, `remove_tree` (novo método, feature 020).
- `core/bootstrap/shim.render_shim` — conteúdo do shim escrito.
- `core/bootstrap/service.BootstrapService` — instalação não-destrutiva dos ganchos Git (reusada, não duplicada).
- `core/install/claude_settings.materialize_claude_settings` — merge por-item do `.claude/settings.json` (reusada).
- `core/domain/layout.{CORE_REL_PATH, CORE_MAIN_REL_PATH}` — caminhos canônicos do core pós-011.
- Nenhuma dependência de `GitPort`/`ProcessPort` — a migração não invoca `git` nem subprocessos, só o `FileSystemPort`.

## Decisões de Design Identificadas

| Decisão                                                                                                              | Evidência no código                                    | Confiança                                                                                   |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| Ordem "escreve o novo antes de remover o velho" — nunca deixa o projeto sem executor                                 | `_migrate_one` (passos i-v na ordem literal do código) | 🟢                                                                                          |
| Reuso de `BootstrapService`/`materialize_claude_settings` em vez de duplicar a lógica de merge                       | `_migrate_one` chama os dois serviços existentes       | 🟢                                                                                          |
| Guarda de nome-base como segunda camada de defesa, independente das guardas 1/2/3                                    | `_safe_remove_core`                                    | 🟢                                                                                          |
| Parse do TOML por regex simples (`_field`/`_strip_version`), não um parser TOML completo                             | `MigrateService._field`, `_strip_version`              | 🟡 (funciona para o formato atual do `harness.toml`; frágil a formatações exóticas do TOML) |
| Exceção deliberada ao footprint per-projeto (RN-N17): a única ferramenta que escreve/remove fora do projeto corrente | Docstring do módulo + guardas 1/2                      | 🟢                                                                                          |

## Estado Interno

`MigrateService` não guarda estado entre chamadas de `migrate` — cada invocação varre `root` do zero e opera sobre o `harness.toml` de cada projeto encontrado naquele momento. Nenhum cache, nenhuma memória de execuções anteriores.

## Observabilidade

- O retorno estruturado (`list[dict]`) é a única saída — quem chama (`main.py`) decide como reportar ao usuário (a CLI imprime; não há logging estruturado dedicado nesta unit).
- Falhas em `_safe_list` são engolidas silenciosamente (retorna `[]`) — 🟡 trade-off entre resiliência (não travar a varredura por uma raiz parcialmente ilegível) e visibilidade (uma raiz totalmente errada não gera nenhum aviso, só uma lista vazia).

## Riscos e Lacunas

- 🟡 **Parser de TOML por regex:** `_field`/`_strip_version` operam sobre o texto bruto do `harness.toml` via regex, não um parser TOML real. Funciona para o formato hoje gerado pelo próprio harness, mas não é robusto a comentários/formatação incomuns no mesmo campo.
- 🟡 **Idempotência não coberta por teste explícito nesta extração:** rodar `migrate` duas vezes sobre o mesmo projeto já convertido deveria ser no-op (sem `harness-core` local, os passos de remoção não encontram nada) — comportamento inferido da estrutura do código, não confirmado por um teste dedicado de dupla execução.
- 🔴 **Sem mecanismo de rollback:** se a escrita do shim ou dos hooks falhar no meio do processo (ex.: permissão negada), não há transação nem reversão — o projeto pode ficar num estado intermediário (shim escrito, mas settings não mesclados, por exemplo). Não verificado se isso é tratado em algum nível superior.
