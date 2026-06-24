# Matriz de Rastreabilidade Código-Especificação (Code-Spec Matrix)

> Regenerado pelo Writer em 2026-06-24 (Re-extração pós-feature 008-reprodutibilidade-e-config)
> Layout das specs: `feature-folder`, granularity `feature`. Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · n/a (sem unit dedicada).

Liga cada arquivo do legado (estado ATUAL) à pasta de spec que o cobre. As pastas de spec mapeiam capacidades/features do `harness-core`. Arquivos de framework (`.claude/skills/`, `.agents/skills/`) e artefatos do próprio Reversa (`.reversa/`, `_reversa_sdd/`, `_reversa_forward/`) ficam fora do escopo.

> ⚠️ **Mudança vs versão anterior (feature 007):** Além do bootstrap evolucionário (`init`/`upgrade`), a feature 008 adicionou a compilação travada de dependências a partir do `requirements.in` (gerenciado por `uv`) gerando o `requirements.txt`, e a infraestrutura de integração contínua sob `.github/workflows/ci.yml`.

---

## 📁 1. Núcleo de domínio (`harness-core/src/core/`)

| Arquivo do legado                     | Unit correspondente      | Cobertura |
| ------------------------------------- | ------------------------ | --------- |
| `core/bootstrap/service.py`           | `bootstrap/`             | 🟢        |
| `core/bootstrap/init_service.py` ✨  | `bootstrap/`             | 🟢        |
| `core/formatting/service.py`          | `format-on-edit/`        | 🟢        |
| `core/sync/service.py`                | `sync-check/` (aviso ver) | 🟢        |
| `core/decisions/service.py`           | `microdecisoes/`         | 🟢        |
| `core/commands/service.py`            | `comandos-customizados/` | 🟢        |
| `core/documentation/service.py`       | `documentacao-uso-html/` | 🟢        |
| `core/documentation/template.html`    | `documentacao-uso-html/` | 🟢        |
| `core/install/service.py`             | `install/`               | 🟢        |
| `core/install/harness_profiles.py`    | `install/`               | 🟢        |
| `core/install/template.md`            | `install/`               | 🟢        |
| `core/session/serializer.py`          | `session/`               | 🟢        |
| `core/session/sinks.py`               | `session/`               | 🟢        |
| `core/session/errors.py`              | `session/`               | 🟢        |

## 📁 2. Domínio compartilhado (`core/domain/`, `core/ports/`)

| Arquivo do legado       | Unit correspondente                                                                                                                                        | Cobertura |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `core/domain/models.py` | `session/` + `microdecisoes/` (transversal)                                                                                                                | 🟢        |
| `core/domain/config.py` | `microdecisoes/` (`[decisions]`); `install/` (`active_harness`); `session/` (`[session]`); `bootstrap/` (`upstream_path`, `version`, feature 007) ✨       | 🟢        |
| `core/domain/cache.py`  | `sync-check/`                                                                                                                                              | 🟢        |
| `core/ports/fs.py`      | transversal (inclui `is_dir` estendido para `bootstrap/` na feature 007)                                                                                   | 🟡        |
| `core/ports/git.py`     | `sync-check/`, `comandos-customizados/`, `bootstrap/`                                                                                                      | 🟡        |
| `core/ports/process.py` | transversal (inclui `run_command` estendido para `bootstrap/` na feature 007)                                                                              | 🟡        |

## 📁 3. Adaptadores (`harness-core/src/adapters/`)

| Arquivo do legado               | Unit correspondente                                                                                                                                               | Cobertura |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `adapters/fs/local.py`          | transversal (inclui `is_dir` física)                                                                                                                              | 🟡        |
| `adapters/git/subprocess.py`    | `sync-check/`, `comandos-customizados/`                                                                                                                           | 🟢        |
| `adapters/process/formatter.py` | `format-on-edit/` + `bootstrap/` (inclui `run_command` físico)                                                                                                    | 🟢        |
| `adapters/mcp/server.py`        | transversal — `format-on-edit/`, `sync-check/`, `microdecisoes/`, `session/` (inclui alertas passivos de versão na feature 007)                                    | 🟡        |

## 📁 4. Drivers e wrapper

| Arquivo do legado                | Unit correspondente                                                     | Cobertura |
| -------------------------------- | ----------------------------------------------------------------------- | --------- |
| `src/main.py` (CLI v2.0.0)       | `run-harness-core-local/` (wrapper→CLI) + cada unit pelo seu subcomando | 🟢        |
| `harness` (wrapper Bash de raiz) | `run-harness-core-local/`                                               | 🟢        |

## 📁 5. Configuração e artefatos versionados

| Arquivo do legado                             | Unit correspondente                                                                                                                       | Cobertura |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `harness-core/harness.toml`                   | `microdecisoes/` (`[decisions]`), `format-on-edit/` (`[formatting]`), `sync-check/` (`[sync]`), `session/` (`[session]`), `bootstrap/` (`[harness]`) | 🟢        |
| `harness-core/requirements.in` ✨             | n/a (dependências abstratas; ver `dependencies.md`)                                                                                      | n/a       |
| `harness-core/requirements.txt`               | n/a (manifesto de dependências físicas trancadas; ver `dependencies.md`)                                                                 | n/a       |
| `.github/workflows/ci.yml` ✨                 | n/a (workflow de integração contínua; ver `dependencies.md`)                                                                              | n/a       |
| `.harness/estado-da-sessao.md`                | `session/` + `comandos-customizados/`                                                                                                     | 🟢        |
| `.harness/decisoes/MD-*.md`                   | `microdecisoes/`                                                                                                                          | 🟢        |
| `.harness/decisoes/_cabecalho.md`             | `microdecisoes/`                                                                                                                          | 🟢        |
| `.harness/microdecisoes.md` (índice derivado) | `microdecisoes/`                                                                                                                          | 🟢        |
| `.claude/settings.json`                       | transversal (hooks `SessionStart`/`PostToolUse`/`Stop`) — `session/`, `format-on-edit/`, `microdecisoes/`, `install/`                     | 🟡        |
| `.gemini/settings.json`                       | `session/`, `install/` (hook `SessionStart`)                                                                                              | 🟡        |
| `harness-docs.html`                           | `documentacao-uso-html/`                                                                                                                  | 🟢        |

## 📁 6. Instruções de agente (ativação do Reversa)

| Arquivo do legado                       | Unit correspondente                                | Cobertura |
| --------------------------------------- | -------------------------------------------------- | --------- |
| `CLAUDE.md` / `GEMINI.md` / `AGENTS.md` | n/a (ativação do framework Reversa, não é produto) | n/a       |

---

## 📂 7. Pacotes `__init__.py`

Todos os `__init__.py` em `harness-core/src/**` são marcadores de pacote (sem lógica de negócio): cobertura **n/a**, herdam a unit do pacote a que pertencem.

---

## 📊 8. Resumo de cobertura

- **Arquivos de produto com lógica mapeados a uma unit:** todos os `service.py`/módulos de `core/*`, adaptadores físicos, driver MCP, CLI e wrapper → **cobertura completa**.
- **`n/a` (candidatos a análise adicional / não-produto):** `requirements.in`, `requirements.txt`, `.github/workflows/ci.yml`, `CLAUDE.md`/`GEMINI.md`/`AGENTS.md`, os `__init__.py`, e as duas árvores de skills do Reversa (framework).
- **Units de spec ativas (9):** `bootstrap/` (estendido na f007), `format-on-edit/`, `sync-check/`, `microdecisoes/`, `comandos-customizados/`, `documentacao-uso-html/`, `run-harness-core-local/`, `install/`, `session/`.
