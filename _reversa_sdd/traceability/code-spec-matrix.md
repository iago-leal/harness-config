# Matriz de Rastreabilidade Código-Especificação (Code-Spec Matrix)

> Regenerado pelo Writer em 2026-06-24 (Re-extração após as features 003, 004 e 005)
> Layout das specs: `feature-folder`, granularity `feature`. Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · n/a (sem unit dedicada).

Liga cada arquivo do legado (estado ATUAL) à pasta de spec que o cobre. As pastas de spec mapeiam capacidades/features do `harness-core`. Arquivos de framework (`.claude/skills/`, `.agents/skills/`) e artefatos do próprio Reversa (`.reversa/`, `_reversa_sdd/`, `_reversa_forward/`) ficam fora do escopo.

> ⚠️ **Mudança vs versão anterior:** o módulo `claude-config/` (scripts shell `bootstrap.sh`, `format-on-edit.sh`, `sync-check.sh`, `gerar-index-decisoes.sh`, `commands/*.md`) **não existe mais** (purgado, commit `5624f78`). As specs antes ancoradas nele foram **reescritas** sobre o core Python equivalente. Surgiram as units `install/` (f003) e `session/` (f004).

> ⚠️ **Atualização cirúrgica (feature 006, commit `e894c59`):** `config.py` ganhou `SessionSection` e o `harness.toml` a seção `[session]`; o caminho de sessão passou a ser lido de `config.session.state_file` em CLI e MCP (fim do literal chumbado e da divergência T2). Via única de configuração: `load_harness_config`/`import toml` removidos de `main.py` (T5 fechado). Novo contrato de footprint testado (`tests/test_footprint.py` + `tests/helpers.py`). T1 e T3 resolvidos no commit anterior `cf73980`.

---

## 📁 1. Núcleo de domínio (`harness-core/src/core/`)

| Arquivo do legado                     | Unit correspondente      | Cobertura |
| ------------------------------------- | ------------------------ | --------- |
| `core/bootstrap/service.py`           | `bootstrap/`             | 🟢        |
| `core/formatting/service.py`          | `format-on-edit/`        | 🟢        |
| `core/sync/service.py`                | `sync-check/`            | 🟢        |
| `core/decisions/service.py`           | `microdecisoes/`         | 🟢        |
| `core/commands/service.py`            | `comandos-customizados/` | 🟢        |
| `core/documentation/service.py`       | `documentacao-uso-html/` | 🟢        |
| `core/documentation/template.html`    | `documentacao-uso-html/` | 🟢        |
| `core/install/service.py` ✨          | `install/`               | 🟢        |
| `core/install/harness_profiles.py` ✨ | `install/`               | 🟢        |
| `core/install/template.md` ✨         | `install/`               | 🟢        |
| `core/session/serializer.py` ✨       | `session/`               | 🟢        |
| `core/session/sinks.py` ✨            | `session/`               | 🟢        |
| `core/session/errors.py` ✨           | `session/`               | 🟢        |

## 📁 2. Domínio compartilhado (`core/domain/`, `core/ports/`)

| Arquivo do legado       | Unit correspondente                                                                                                                                        | Cobertura |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `core/domain/models.py` | `session/` + `microdecisoes/` (transversal)                                                                                                                | 🟢        |
| `core/domain/config.py` | `microdecisoes/` (origem de `[decisions]`); `install/` (origem de `active_harness`); `session/` (origem de `[session]` → `SessionSection`, feature 006) 🟢 | 🟢        |
| `core/domain/cache.py`  | `sync-check/`                                                                                                                                              | 🟢        |
| `core/ports/fs.py`      | transversal (todas as units que fazem I/O)                                                                                                                 | 🟡        |
| `core/ports/git.py`     | `sync-check/`, `comandos-customizados/`, `bootstrap/`                                                                                                      | 🟡        |
| `core/ports/process.py` | `format-on-edit/`                                                                                                                                          | 🟡        |

## 📁 3. Adaptadores (`harness-core/src/adapters/`)

| Arquivo do legado               | Unit correspondente                                                                                                                                               | Cobertura |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `adapters/fs/local.py`          | transversal (gravação atômica)                                                                                                                                    | 🟡        |
| `adapters/git/subprocess.py`    | `sync-check/`, `comandos-customizados/`                                                                                                                           | 🟢        |
| `adapters/process/formatter.py` | `format-on-edit/` (contracts.md)                                                                                                                                  | 🟢        |
| `adapters/mcp/server.py`        | transversal — `format-on-edit/`, `sync-check/`, `microdecisoes/`, `session/` (expõe as 4 tools; `session_file` lido de `config.session.state_file` — feature 006) | 🟡        |

## 📁 4. Drivers e wrapper

| Arquivo do legado                | Unit correspondente                                                     | Cobertura |
| -------------------------------- | ----------------------------------------------------------------------- | --------- |
| `src/main.py` (CLI v2.0.0)       | `run-harness-core-local/` (wrapper→CLI) + cada unit pelo seu subcomando | 🟢        |
| `harness` (wrapper Bash de raiz) | `run-harness-core-local/`                                               | 🟢        |

## 📁 5. Configuração e artefatos versionados

| Arquivo do legado                             | Unit correspondente                                                                                                                       | Cobertura |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `harness-core/harness.toml`                   | `microdecisoes/` (`[decisions]`), `format-on-edit/` (`[formatting]`, T4), `sync-check/` (`[sync]`), `session/` (`[session]`, feature 006) | 🟢        |
| `harness-core/requirements.txt`               | n/a (manifesto de dependências; ver `dependencies.md`)                                                                                    | n/a       |
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

- **Arquivos de produto com lógica mapeados a uma unit:** todos os `service.py`/módulos de `core/*`, os 3 adaptadores físicos, o driver MCP, a CLI e o wrapper → **cobertura 🟢/🟡 completa**.
- **`n/a` (candidatos a análise adicional / não-produto):** `requirements.txt`, `CLAUDE.md`/`GEMINI.md`/`AGENTS.md`, os `__init__.py`, e as duas árvores de skills do Reversa (framework).
- **Units de spec ativas (9):** `bootstrap/`, `format-on-edit/`, `sync-check/`, `microdecisoes/`, `comandos-customizados/`, `documentacao-uso-html/`, `run-harness-core-local/`, `install/` ✨, `session/` ✨.
- **Contrato de footprint (feature 006) 🟢:** `harness-core/tests/test_footprint.py` + `harness-core/tests/helpers.py` (`RecordingFileSystem`) fixam por teste a zona protegida BR-MIGRAR-007 — o harness falha barulhento se escrever em `~/.claude`, `~/.agent-memory` ou fora do repositório. Não há unit de spec dedicada; mapeia-se transversalmente a `session/`, `microdecisoes/`, `install/` e aos dois drivers. Confiança 🟡 quanto à cobertura: cobre só os serviços efetivamente exercitados; é teste, não guard de runtime.
- **Bugs antes latentes — situação atual:** T1 (MCP `process_decisions`/`session_command` com `load_config`) **RESOLVIDO** no commit `cf73980` (import de `load_config` em `server.py`). T2 (estado de sessão divergente CLI×MCP) **RESOLVIDO** na feature 006: ambos os drivers leem `session_file` de `config.session.state_file` (sem literal chumbado). T3 (`json` ausente em `main.py`, autoformat por hook) **RESOLVIDO** no commit `cf73980` (import de `json`). T5 (duas vias de config — `load_harness_config` dict legado) **FECHADO** na feature 006: via única tipada `load_config`; `load_harness_config` e `import toml` removidos de `main.py`. Permanece latente apenas **T4** (`format-on-edit/`, `[formatting]` declarado mas não consumido).
