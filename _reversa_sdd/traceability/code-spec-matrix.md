# Matriz de Rastreabilidade Código-Especificação (Code-Spec Matrix)

> Regenerado pelo Writer em 2026-06-24 (Re-extração após a feature 009-hooks-antigravity)
> Layout das specs: `feature-folder`, granularity `feature`. Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · n/a (sem unit dedicada).

Liga cada arquivo do legado (estado ATUAL) à pasta de spec que o cobre. As pastas de spec mapeiam capacidades/features do `harness-core`. Arquivos de framework (`.claude/skills/`, `.agents/skills/`) e artefatos do próprio Reversa (`.reversa/`, `_reversa_sdd/`, `_reversa_forward/`) ficam fora do escopo.

> ⚠️ **Mudança vs versão anterior (feature 007):** Além do bootstrap evolucionário (`init`/`upgrade`), a feature 008 adicionou a compilação travada de dependências a partir do `requirements.in` (gerenciado por `uv`) gerando o `requirements.txt`, e a infraestrutura de integração contínua sob `.github/workflows/ci.yml`.
>
> ⚠️ **Mudança vs versão anterior (feature 009):** A feature 009 acrescentou um **terceiro driver de entrada** ao hexágono — `adapters/antigravity/hook_bridge.py` (`AntigravityHookBridge`), irmão da CLI e do servidor MCP —, um materializador de instalação dedicado (`core/install/antigravity_hooks.py`), preencheu o antes-placeholder `AntigravityProfile` e adicionou o subcomando `agy-hook <evento>` à CLI. Nenhuma dependência nova (só stdlib). A unit de spec correspondente é `antigravity-hooks/` (ADR 0016, RN-N26).
>
> ⚠️ **Reconciliação de 2026-07-05 (features 018-021):** esta matriz estava congelada desde 2026-06-24/feature 009. Novos arquivos mapeados: `session/close_flow.py` (f018) e `session/resume_context.py` (f021) → `comandos-customizados/` (unit que já cobre a orquestração de `encerrar-sessao`/`resume`, não `session/`, que fica restrita a serializer/sinks/errors); `install/session_skills.py` (f018, substitui `install/session_commands.py`) → `comandos-customizados/`; `install/claude_settings.py` e `bootstrap/shim.py` (f020) → `bootstrap/`; `core/migrate/service.py` (f020) → nova unit **`migrate/`**.
>
> ⚠️ **Reconciliação de 2026-08-11 (features 024-027; a 024 commitada em `5c4433d`, 025/026/027 apenas na working tree):** novo pacote `core/progress/` (`service.py`/`stages.py`/`render.py` da f026; `kanban.py` da f027) → nova unit **`progress/`**. A f024 (consentimento) e a f025 (advisory no Stop) não criam arquivo novo — refletidas nas linhas de `close_flow.py`/`commands/service.py`/`main.py` e nas units `session/`, `comandos-customizados/` e `microdecisoes/`. Novos artefatos derivados: `.harness/progresso.md` (f026) e `.vscode/vscode-kanban.json` (f027, opt-in).
>
> ⚠️ **Reconciliação de 2026-08-11-b (feature 028, apenas na working tree):** nenhum arquivo novo — a 028 vive em arquivos já mapeados: `decisions/service.py` (`compile_compact_view`/`_extract_title`/`_write_if_changed`) → `microdecisoes/`; `resume_context.py` (parâmetro `compact_file`, precedência compacta→índice) → `comandos-customizados/`; `init_service.py` (`_ensure_decisions_guidance`, write-once por marcador) → `bootstrap/`; `config.py` (`DecisionsSection.compact_file`/`compact_index_size`, `CORE_VERSION` 2.6.0). Novo artefato derivado: `.harness/decisoes-recentes.md`.
> ⚠️ **Reconciliação de 2026-07-15 (MD-0014 + features 022-023):** novo arquivo `core/decisions/gate.py` → `microdecisoes/` (o gate de registro é capacidade da unit de decisões, com o 3º portão também refletido em `session/` e `comandos-customizados/`). O hook `PostToolUse` do Claude foi aposentado (MD-0014) — linha do `.claude/settings.json` atualizada. `GitPort.list_changed_paths_since` (f022) entra na linha de `core/ports/git.py`.

---

## 📁 1. Núcleo de domínio (`.harness/harness-core/src/core/`)

| Arquivo do legado                      | Unit correspondente                                                                                                              | Cobertura |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `core/bootstrap/service.py`            | `bootstrap/`                                                                                                                     | 🟢        |
| `core/bootstrap/init_service.py` ✨    | `bootstrap/` (+`_ensure_decisions_guidance`, guidance write-once por marcador, f028)                                             | 🟢        |
| `core/formatting/service.py`           | `format-on-edit/`                                                                                                                | 🟢        |
| `core/sync/service.py`                 | `sync-check/` (aviso ver)                                                                                                        | 🟢        |
| `core/decisions/service.py`            | `microdecisoes/` (+`compile_compact_view`/`_extract_title`/`_write_if_changed`, f028)                                            | 🟢        |
| `core/decisions/gate.py` ✨✨✨ (NOVO) | `microdecisoes/` (gate de registro, f022/f023; 3º portão consumido por `comandos-customizados/`)                                 | 🟢        |
| `core/commands/service.py`             | `comandos-customizados/` (`execute_command(..., versionar_estado=True)` desde a f024; MCP mantém `True`, D-04)                   | 🟢        |
| `core/documentation/service.py`        | `documentacao-uso-html/`                                                                                                         | 🟢        |
| `core/documentation/template.html`     | `documentacao-uso-html/`                                                                                                         | 🟢        |
| `core/install/service.py`              | `install/`                                                                                                                       | 🟢        |
| `core/install/harness_profiles.py`     | `install/` + `antigravity-hooks/` (f009: `AntigravityProfile.hooks_block()`/`apply_instructions()` deixam de ser placeholder) ✨ | 🟢        |
| `core/install/antigravity_hooks.py` ✨ | `antigravity-hooks/` (`materialize_hooks_json`, merge por named-hook; f009)                                                      | 🟢        |
| `core/install/template.md`             | `install/`                                                                                                                       | 🟢        |
| `core/install/session_skills.py` ✨✨  | `comandos-customizados/` (`materialize_session_skills`, substitui `session_commands.py`; f018)                                   | 🟢        |
| `core/install/claude_settings.py` ✨✨ | `bootstrap/` (merge por-item do `.claude/settings.json`; f020)                                                                   | 🟢        |
| `core/session/serializer.py`           | `session/`                                                                                                                       | 🟢        |
| `core/session/sinks.py`                | `session/`                                                                                                                       | 🟢        |
| `core/session/errors.py`               | `session/`                                                                                                                       | 🟢        |
| `core/session/close_flow.py` ✨✨      | `comandos-customizados/` + `session/` (`SessionCloseFlow`, pré-check + 3 portões + ofertas; f018/f019/f022; consentimento para escrita no git com tri-estado e marker `ENCERRAMENTO_NAO_VERSIONADO`, f024)   | 🟢        |
| `core/session/resume_context.py` ✨✨  | `comandos-customizados/` (`build_decisions_appendix`; f021; `compact_file` com fallback compacta→índice, f028)                   | 🟢        |
| `core/bootstrap/shim.py` ✨✨          | `bootstrap/` (`render_shim`; f020, reusado por `init` e `migrate/`)                                                              | 🟢        |
| `core/migrate/service.py` ✨✨ (NOVO)  | `migrate/` (`MigrateService`; f020)                                                                                              | 🟢        |
| `core/progress/service.py` ✨✨✨✨ (NOVO) | `progress/` (`ProgressService.measure`, cinco fontes em leitura pura; f026/f027)                                             | 🟢        |
| `core/progress/stages.py` ✨✨✨✨ (NOVO)  | `progress/` (estágio físico + checkboxes, paridade com o skill; f026)                                                        | 🟢        |
| `core/progress/render.py` ✨✨✨✨ (NOVO)  | `progress/` (markdown sem valor volátil + JSON com `aferido_em`; f026)                                                       | 🟢        |
| `core/progress/kanban.py` ✨✨✨✨ (NOVO)  | `progress/` (exportador do board, posse por namespace; único módulo que conhece o schema do fork; f027)                      | 🟢        |

## 📁 2. Domínio compartilhado (`core/domain/`, `core/ports/`)

| Arquivo do legado       | Unit correspondente                                                                                                                                                                                                              | Cobertura |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `core/domain/models.py` | `session/` + `microdecisoes/` (transversal)                                                                                                                                                                                      | 🟢        |
| `core/domain/config.py` | `microdecisoes/` (`[decisions]`); `install/` (`active_harness`); `session/` (`[session]`); `bootstrap/` (`upstream_path`, `version`, feature 007); `comandos-customizados/` (`SessionSection.inject_decisions_index`, f021); `progress/` (`ProgressSection` f026 + `ProgressKanbanSection` opt-in f027); `microdecisoes/` (`DecisionsSection.compact_file`/`compact_index_size` f028; `CORE_VERSION` 2.6.0) ✨✨ | 🟢        |
| `core/domain/cache.py`  | `sync-check/`                                                                                                                                                                                                                    | 🟢        |
| `core/domain/layout.py` | `bootstrap/`, `migrate/` (`CORE_REL_PATH`, `CORE_MAIN_REL_PATH`, caminhos-candidato)                                                                                                                                             | 🟢        |
| `core/ports/fs.py`      | transversal (inclui `is_dir` estendido para `bootstrap/` na feature 007; `remove_tree` novo, usado só por `migrate/`, f020) ✨✨                                                                                                 | 🟡        |
| `core/ports/git.py`     | `sync-check/`, `comandos-customizados/`, `bootstrap/`, `microdecisoes/` (inclui `commit_paths` f013, `list_dirty_paths` f016 e `list_changed_paths_since` f022 — este último alimenta o gate de registro)                        | 🟡        |
| `core/ports/process.py` | transversal (inclui `run_command` estendido para `bootstrap/` na feature 007)                                                                                                                                                    | 🟡        |

## 📁 3. Adaptadores (`.harness/harness-core/src/adapters/`)

| Arquivo do legado                        | Unit correspondente                                                                                                                                                         | Cobertura |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `adapters/fs/local.py`                   | transversal (inclui `is_dir` física)                                                                                                                                        | 🟡        |
| `adapters/git/subprocess.py`             | `sync-check/`, `comandos-customizados/`                                                                                                                                     | 🟢        |
| `adapters/process/formatter.py`          | `format-on-edit/` + `bootstrap/` (inclui `run_command` físico)                                                                                                              | 🟢        |
| `adapters/mcp/server.py`                 | transversal — `format-on-edit/`, `sync-check/`, `microdecisoes/`, `session/` (inclui alertas passivos de versão na feature 007; desde a MD-0023/core 2.6.1, `process_decisions` também deriva a visão compacta na mesma passada — fix do G-20/T8, RN-N56)                                             | 🟡        |
| `adapters/antigravity/hook_bridge.py` ✨ | `antigravity-hooks/` (`AntigravityHookBridge`: terceiro driver de entrada; traduz `PreToolUse`/`PostToolUse`/`Stop` e delega a `FormattingService`/`DecisionService`; f009) | 🟢        |

## 📁 4. Drivers e wrapper

| Arquivo do legado                | Unit correspondente                                                                                                                                                                                                                                                                                                                               | Cobertura |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `src/main.py` (CLI)              | `run-harness-core-local/` (wrapper→CLI) + cada unit pelo seu subcomando; inclui o subcomando fino `agy-hook <evento>` que instancia o `AntigravityHookBridge` → `antigravity-hooks/` (f009); `materialize` (f012) → `bootstrap/`; `migrate` (f020) → `migrate/`; apêndice de decisões no ramo `cmd resume` (f021) → `comandos-customizados/`; `decisions --gate` e `cmd --sem-decisao` (f022/f023) → `microdecisoes/` + `comandos-customizados/`; flags de consentimento do `cmd encerrar-sessao` (f024) → `session/` + `comandos-customizados/`; ramo `--gate` advisory (f025) → `microdecisoes/`; subcomando `progress` (13º; padrão/`--json`/`--em-hook`, f026/f027) → `progress/` ✨✨✨ | 🟢        |
| `harness` (wrapper Bash de raiz) | `run-harness-core-local/` (fonte única desde f020: agora renderizado por `render_shim`, ver `bootstrap/`) ✨✨                                                                                                                                                                                                                                    | 🟢        |

## 📁 5. Configuração e artefatos versionados

| Arquivo do legado                             | Unit correspondente                                                                                                                                                                                                                  | Cobertura |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| `.harness/harness-core/harness.toml`          | `microdecisoes/` (`[decisions]`), `format-on-edit/` (`[formatting]`), `sync-check/` (`[sync]`), `session/` (`[session].state_file`), `comandos-customizados/` (`[session].inject_decisions_index`, f021), `bootstrap/` (`[harness]`), `progress/` (`[progress].file` f026 + `[progress.kanban].enabled`/`file` f027) | 🟢        |
| `.harness/harness-core/requirements.in` ✨    | n/a (dependências abstratas; ver `dependencies.md`)                                                                                                                                                                                  | n/a       |
| `.harness/harness-core/requirements.txt`      | n/a (manifesto de dependências físicas trancadas; ver `dependencies.md`)                                                                                                                                                             | n/a       |
| `.github/workflows/ci.yml` ✨                 | n/a (workflow de integração contínua; ver `dependencies.md`)                                                                                                                                                                         | n/a       |
| `.harness/estado-da-sessao.md`                | `session/` + `comandos-customizados/`                                                                                                                                                                                                | 🟢        |
| `.harness/decisoes/MD-*.md`                   | `microdecisoes/`                                                                                                                                                                                                                     | 🟢        |
| `.harness/decisoes/_cabecalho.md`             | `microdecisoes/`                                                                                                                                                                                                                     | 🟢        |
| `.harness/microdecisoes.md` (índice derivado) | `microdecisoes/`                                                                                                                                                                                                                     | 🟢        |
| `.harness/progresso.md` (derivado, f026) ✨✨✨✨ | `progress/` (regravado pelo `./harness progress`, write-only-when-changed, sem timestamp)                                                                                                                                     | 🟢        |
| `.vscode/vscode-kanban.json` (derivado + ilha manual, f027, opt-in) ✨✨✨✨ | `progress/` (cards `harness` recomputados; manuais preservados byte a byte; o `.js` do fork jamais é tocado)                                                                                       | 🟢        |
| `.claude/settings.json`                       | transversal (hooks `SessionStart`/`Stop --gate`; o `PostToolUse` foi aposentado por MD-0014) — `session/`, `microdecisoes/`, `install/`                                                                                              | 🟡        |
| `.gemini/settings.json`                       | `session/`, `install/` (hook `SessionStart`)                                                                                                                                                                                         | 🟡        |
| `harness-docs.html`                           | `documentacao-uso-html/`                                                                                                                                                                                                             | 🟢        |

## 📁 6. Instruções de agente (ativação do Reversa)

| Arquivo do legado                       | Unit correspondente                                | Cobertura |
| --------------------------------------- | -------------------------------------------------- | --------- |
| `CLAUDE.md` / `GEMINI.md` / `AGENTS.md` | n/a (ativação do framework Reversa, não é produto) | n/a       |

---

## 📂 7. Pacotes `__init__.py`

Todos os `__init__.py` em `.harness/harness-core/src/**` são marcadores de pacote (sem lógica de negócio): cobertura **n/a**, herdam a unit do pacote a que pertencem.

---

## 📊 8. Resumo de cobertura

- **Arquivos de produto com lógica mapeados a uma unit:** todos os `service.py`/módulos de `core/*`, adaptadores físicos, driver MCP, CLI e wrapper → **cobertura completa**.
- **`n/a` (candidatos a análise adicional / não-produto):** `requirements.in`, `requirements.txt`, `.github/workflows/ci.yml`, `CLAUDE.md`/`GEMINI.md`/`AGENTS.md`, os `__init__.py`, e as duas árvores de skills do Reversa (framework).
- **Units de spec ativas (12):** `bootstrap/` (estendido na f007, f009 e **f020** — `render_shim`, `claude_settings.py` por-item, ganchos git não-destrutivos), `format-on-edit/` (gatilho revisto por **MD-0014** — on-edit aposentado no Claude), `sync-check/`, `microdecisoes/` (estendido na **f022/f023** — `gate.py`, gate de registro com dupla identidade), `comandos-customizados/` (estendido na **f018/f019/f021/f022** — `SessionCloseFlow` com 3 portões, pré-check restrito ao estado, apêndice de decisões no resume, `--sem-decisao`), `documentacao-uso-html/`, `run-harness-core-local/`, `install/`, `session/` (estendido na **f022** — campos anti-loop no serializer), `antigravity-hooks/` (nova na f009; estendida na f022 com o advisory via `gate_evaluator`), **`migrate/`** (nova na reconciliação de 2026-07-05 — feature **020**). **Na reconciliação de 2026-08-11 a contagem vai a 12 units:** nova **`progress/`** (features **026/027** — medidor read-only + exportador kanban); `session/` e `comandos-customizados/` estendidas na **f024** (consentimento para escrita no git ao encerrar); `microdecisoes/` estendida na **f025** (Stop advisory, soft-block aposentado).
