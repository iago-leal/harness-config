# Inventário do Projeto — harness

> Gerado pelo Scout em 2026-06-24 (Re-extração após as features 003, 004 e 005)

Mapeamento da superfície de código e arquivos de configuração do diretório `/Users/iagoleal/dev/harness`.

---

## 📊 Estatísticas Gerais

* **Diretório Alvo:** `/Users/iagoleal/dev/harness`
* **Escopo da contagem:** código da aplicação (`harness-core/`, wrapper de raiz, configs e `.harness/`). Excluídos: `.venv`, `.git`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `tmp/`, os artefatos do próprio Reversa (`.reversa/`, `_reversa_sdd/`, `_reversa_forward/`) e as duas árvores-espelho de **templates de skills do Reversa** (`.claude/skills/` e `.agents/skills/`, ~430 arquivos de framework, não de produto).
* **Linguagens Principais (aplicação):**
  * **Python (`.py`)**: 52 arquivos — 37 em `harness-core/src/` e 15 em `harness-core/tests/`.
  * **Markdown (`.md`)**: 11 arquivos — instruções de agente (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`), decisões em `.harness/decisoes/`, índice `.harness/microdecisoes.md`, estado de sessão e o template `install/template.md`.
  * **HTML (`.html`)**: 2 arquivos — `harness-core/src/core/documentation/template.html` e o consolidado `harness-docs.html` na raiz.
  * **Shell (`harness`)**: 1 wrapper Bash executável na raiz.
  * **TOML (`.toml`)**: 1 arquivo (`harness-core/harness.toml`).
  * **JSON (`.json`)**: 2 arquivos de configuração de ganchos (`.claude/settings.json`, `.gemini/settings.json`).

> ⚠️ **Mudança estrutural vs extração anterior:** o módulo legado `claude-config/` **não existe mais** — foi PURGADO (commit `5624f78`, "remove legado morto e corta hooks vivos para a CLI") e passou a ser ignorado pelo `.gitignore`. Toda a configuração viva migrou para `harness-core/` (lógica) e para `.harness/` (estado e decisões). A contagem anterior de 101 arquivos incluía o legado e somava as árvores de skills do Reversa; esta extração separa produto de framework.

---

## 📂 Estrutura de Diretórios e Arquivos

### ⚡ Raiz do Projeto
* **`harness`** 🟢 — Wrapper Bash executável. Resolve a venv local (`harness-core/.venv/bin/python3`) e encaminha todos os argumentos para `harness-core/src/main.py`. Falha barulhenta com instrução de setup se a venv não existir.
* **`harness-docs.html`** 🟢 — HTML standalone gerado por `doc-gen`, consolidando a superfície da CLI, o domínio (`_reversa_sdd/domain.md`) e o estado do Reversa.
* **`CLAUDE.md` / `GEMINI.md` / `AGENTS.md`** 🟢 — Instruções de ativação do framework Reversa por harness.

### 📦 Núcleo Python (`harness-core/`) — arquitetura hexagonal
* **`src/main.py`** 🟢 — Entrada da CLI (v2.0.0). Subcomandos: `bootstrap`, `format`, `decisions`, `cmd`, `doc-gen`, `doc-serve` e o **novo `install-prompt`** (feature 003). O `decisions` lê os caminhos de `load_config().decisions` (sem literais chumbados — feature 005).
* **`src/core/`** — Regras de negócio (domínio puro), uma pasta por capacidade:
  * **`bootstrap/`** 🟢 — instalação de ganchos Git locais.
  * **`formatting/`** 🟢 — formatação de arquivo por linguagem.
  * **`sync/`** 🟢 — verificação de sincronia Git com cache TTL.
  * **`decisions/`** 🟢 — carga, validação de integridade do grafo e compilação do índice de microdecisões.
  * **`commands/`** 🟢 — execução de slash commands de sessão (`resume`, `encerrar-sessao`, `handoff`, `clarificar`).
  * **`documentation/`** 🟢 — geração do HTML (`service.py` + `template.html`).
  * **`install/`** 🟢 **(NOVO — feature 003)** — `service.py` (`InstallPromptService`, render do prompt colável por composição), `harness_profiles.py` (estratégias `Claude`/`Gemini`/`Antigravity` para o bloco de ganchos) e `template.md`.
  * **`session/`** 🟢 **(NOVO — feature 004)** — estado de sessão unificado: `serializer.py` (round-trip front-matter YAML + corpo Markdown), `sinks.py` (`HookContextSink` para Claude/Gemini via `additionalContext`; `FileProjectionSink` para Antigravity) e `errors.py` (`MalformedSessionStateError`).
  * **`domain/`** 🟢 — modelos Pydantic (`models.py`: `Decision`, `Relationship`, `SessionState`, `SessionNarrative`), `config.py` (`HarnessConfig` tipado, com a seção `[decisions]`) e `cache.py`.
  * **`ports/`** 🟢 — interfaces (Protocols) `fs.py`, `git.py`, `process.py`.
* **`src/adapters/`** 🟢 — Infraestrutura física: `fs/local.py`, `git/subprocess.py`, `process/formatter.py` e **`mcp/server.py`** (servidor FastMCP expondo `format_file`, `check_repository_sync`, `process_decisions`, `session_command`).
* **`tests/`** 🟢 — 14 arquivos pytest / 55 funções de teste, incluindo os novos `test_install.py`, `test_session.py` e `test_session_sinks.py`.
* **`harness.toml`** 🟢 — Configuração: `[harness]` (`active_harness`), `[formatting]`, `[sync]` e a **nova `[decisions]`** (`dir = .harness/decisoes`, `index_file = .harness/microdecisoes.md`, `header_file = .harness/decisoes/_cabecalho.md`).
* **`requirements.txt`** 🟢 — `mcp`, `pydantic`, `pytest`, `toml`, `PyYAML` (versões em `dependencies.md`).

### 🗂️ Estado e Decisões versionados (`.harness/`) — **NOVO local canônico**
* **`.harness/estado-da-sessao.md`** 🟢 **(feature 004)** — Estado de sessão unificado (front-matter YAML + corpo), reinjetado no contexto a cada boot pelo hook `SessionStart` → `./harness cmd resume`.
* **`.harness/decisoes/MD-0001..MD-0004.md`** 🟢 **(feature 005)** — Fichas de microdecisão (movidas de `decisoes/` na raiz). `_cabecalho.md` é o cabeçalho do índice.
* **`.harness/microdecisoes.md`** 🟢 **(feature 005)** — Índice DERIVADO pelo `./harness decisions` (hook Stop). Movido da raiz.

### ⚙️ Configuração de ganchos por harness
* **`.claude/settings.json`** 🟢 — Hooks Claude Code: `SessionStart` → `harness cmd resume`; `PostToolUse` (Write|Edit) → `harness format`; `Stop` → `harness decisions`.
* **`.gemini/settings.json`** 🟢 — Hook Gemini: `SessionStart` → `./harness cmd resume`.

### 🧩 Framework Reversa (instalado, não é produto)
* **`.claude/skills/` e `.agents/skills/`** 🟢 — Duas árvores-espelho com os templates de todos os agentes do Reversa (scout, archaeologist, architect, etc.). São dependência de tooling, contabilizadas à parte do código da aplicação.

### 🔄 Features Forward (`_reversa_forward/`)
* **`001-run-harness-core-local/`** — execução local do core.
* **`002-documentacao-uso-html/`** — gerador de documentação HTML.
* **`003-instalacao-por-prompt/`** 🟢 **(NOVO)** — comando `install-prompt`.
* **`004-estado-sessao-unificado/`** 🟢 **(NOVO)** — estado de sessão em `.harness/` com reinjeção.
* **`005-decisoes-em-harness/`** 🟢 **(NOVO)** — migração das decisões para `.harness/` e remoção de literais chumbados.

---

## 🩺 Achados de saúde (para os agentes seguintes)

* 🟡 **Divergência MCP × CLI:** `src/adapters/mcp/server.py` chama `load_config(fs)` em `process_decisions` **sem importar `load_config`** (provável `NameError` em runtime) e o `session_command` ainda aponta para `ESTADO-DA-SESSAO.md` na raiz, enquanto a CLU (`main.py`) usa `.harness/estado-da-sessao.md`. Candidato a ticket de manutenção — confirmar com o Archaeologist.
* 🟢 **Caminhos de decisão desacoplados:** após a feature 005, nem `main.py` nem `server.py` chumbam `decisoes/`; ambos derivam de `[decisions]` no `harness.toml`.
