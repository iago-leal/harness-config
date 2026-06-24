# Inventário do Projeto — harness

> Gerado pelo Scout em 2026-06-24 (Re-extração após as features 003, 004, 005, 006, 007 e 009)
> Atualização cirúrgica em 2026-06-24 após a feature 007: adição do comando `init` e `upgrade` no wrapper de raiz, novos `tests/test_init.py` e `src/core/bootstrap/init_service.py`, caminhos de evolução/bootstrap em CLI e MCP.
> Re-extração após a feature 009-hooks-antigravity: terceiro driver de entrada `src/adapters/antigravity/hook_bridge.py` (`AntigravityHookBridge`), materializador `src/core/install/antigravity_hooks.py`, três novos testes `test_antigravity_*.py`, subcomando `agy-hook` na CLI e ganchos do Antigravity via `.agents/hooks.json`.

Mapeamento da superfície de código e arquivos de configuração do diretório `/Users/iagoleal/dev/harness`.

---

## 📊 Estatísticas Gerais

- **Diretório Alvo:** `/Users/iagoleal/dev/harness`
- **Escopo da contagem:** código da aplicação (`harness-core/`, wrapper de raiz, configs e `.harness/`). Excluídos: `.venv`, `.git`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `tmp/`, os artefatos do próprio Reversa (`.reversa/`, `_reversa_sdd/`, `_reversa_forward/`) e as duas árvores-espelho de **templates de skills do Reversa** (`.claude/skills/` e `.agents/skills/`, ~430 arquivos de framework, não de produto).
- **Linguagens Principais (aplicação):**
  - **Python (`.py`)**: 60 arquivos — 41 em `harness-core/src/` e 19 em `harness-core/tests/`. A feature 007 acrescentou `init_service.py` e `test_init.py`; a feature 009 acrescentou `src/adapters/antigravity/__init__.py`, `src/adapters/antigravity/hook_bridge.py`, `src/core/install/antigravity_hooks.py` e os três testes `test_antigravity_hook_bridge.py`, `test_antigravity_hooks_materializer.py` e `test_antigravity_profile.py`.
  - **Markdown (`.md`)**: 12 arquivos — instruções de agente (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`), as 5 fichas de decisão em `.harness/decisoes/` (`MD-0001`..`MD-0005`) mais o `_cabecalho.md`, o índice `.harness/microdecisoes.md`, o estado de sessão e o template `install/template.md`.
  - **HTML (`.html`)**: 2 arquivos — `harness-core/src/core/documentation/template.html` e o consolidado `harness-docs.html` na raiz.
  - **Shell (`harness`)**: 1 wrapper Bash executável na raiz.
  - **TOML (`.toml`)**: 1 arquivo (`harness-core/harness.toml`).
  - **JSON (`.json`)**: arquivos de configuração de ganchos por harness (`.claude/settings.json`, `.gemini/settings.json` e, para o Antigravity, `.agents/hooks.json` materializado no projeto-alvo pelo `init`/`upgrade`).

> ⚠️ **Mudança estrutural vs extração anterior:** o módulo legado `claude-config/` foi purgado anteriormente. A feature 007 expandiu os arquivos e testes do core, introduzindo novos pontos de entrada para inicialização de repositório (`init`) e upgrade evolucionário (`upgrade`) preservando os metadados locais de engenharia reversa. A feature 009 adicionou um **terceiro driver de entrada** no anel de adaptadores (o `AntigravityHookBridge`), simétrico à CLI e ao servidor MCP, que fala o protocolo de ganchos do Antigravity e delega aos serviços de domínio sem ramificar o core por harness.

---

## 📂 Estrutura de Diretórios e Arquivos

### ⚡ Raiz do Projeto

- **`harness`** 🟢 — Wrapper Bash executável. Resolve a venv local (`harness-core/.venv/bin/python3`) e encaminha todos os argumentos para `harness-core/src/main.py`.
- **`harness-docs.html`** 🟢 — HTML standalone gerado por `doc-gen`, consolidando a superfície da CLI, o domínio (`_reversa_sdd/domain.md`) e o estado do Reversa.
- **`CLAUDE.md` / `GEMINI.md` / `AGENTS.md`** 🟢 — Instruções de ativação do framework Reversa por harness, agora contendo a instrução de uso dos comandos `./harness init` e `./harness upgrade`.

### 📦 Núcleo Python (`harness-core/`) — arquitetura hexagonal

- **`src/main.py`** 🟢 — Entrada da CLI (v2.0.0). Subcomandos: `bootstrap`, `format`, `decisions`, `cmd`, `doc-gen`, `doc-serve`, `install-prompt`, `init`, `upgrade` (feature 007) e o **novo `agy-hook <evento>`** (feature 009), subcomando fino que instancia o `AntigravityHookBridge`, lê o payload do `stdin` e escreve a resposta no `stdout`. O `agy-hook` é exceção ao check passivo de sync e ao carregamento global de config (carrega a config dentro do próprio try/except). Injeta aviso de nova versão disponível se a versão local for menor que a versão do upstream.
- **`src/core/`** — Regras de negócio (domínio puro), uma pasta por capacidade:
  - **`bootstrap/`** 🟢 — instalação de ganchos Git locais e o **novo `init_service.py`** (feature 007, serviço que orquestra a cópia do core, wrapper, setup da `.venv` e dos ganchos Git no destino).
  - **`formatting/`** 🟢 — formatação de arquivo por linguagem.
  - **`sync/`** 🟢 — verificação de sincronia Git e detecção passiva e comparação rápida de versão local vs upstream.
  - **`decisions/`** 🟢 — carga, validação de integridade do grafo e compilação do índice de microdecisões.
  - **`commands/`** 🟢 — execução de slash commands de sessão (`resume`, `encerrar-sessao`, `handoff`, `clarificar`).
  - **`documentation/`** 🟢 — geração do HTML (`service.py` + `template.html`).
  - **`install/`** 🟢 — render do prompt colável por composição. Inclui `harness_profiles.py` (Strategy por harness: `ClaudeProfile`, `GeminiProfile` e o `AntigravityProfile`, que deixou de ser placeholder — `hooks_block()` emite o `.agents/hooks.json` válido e `apply_instructions()` aponta `.agents/hooks.json`; o escopo por harness migrou para os `apply_instructions()` dos três perfis) e o **novo `antigravity_hooks.py`** (feature 009, `materialize_hooks_json(fs, project_path, command_path)` — escrita única com merge por named-hook `harness`, compartilhada por `init` e `upgrade`).
  - **`session/`** 🟢 — estado de sessão unificado.
  - **`domain/`** 🟢 — modelos Pydantic, cache e configuração tipada (`HarnessConfig` tipado, agora com suporte a `upstream_path` e `version` na seção `[harness]`).
  - **`ports/`** 🟢 — interfaces (Protocols) `fs.py` (com o método `is_dir`), `git.py` e `process.py` (com o método `run_command`).
- **`src/adapters/`** 🟢 — Infraestrutura física: `fs/local.py` (implementação de `is_dir`), `git/subprocess.py`, `process/formatter.py` (implementação de `run_command`), `mcp/server.py` (servidor FastMCP expondo `format_file`, `check_repository_sync`, `process_decisions`, `session_command` e alertas passivos de atualização no boot) e o **novo `antigravity/hook_bridge.py`** (feature 009, `AntigravityHookBridge` — terceiro driver de entrada que traduz o protocolo de ganchos do Antigravity: `hooks.json` declarativo e stdin/stdout JSON camelCase por evento `PreToolUse`/`PostToolUse`/`Stop`, delegando a `FormattingService` e `DecisionService`; sempre não-bloqueante, jamais `"deny"`/`"continue"`).
- **`tests/`** 🟢 — 19 arquivos `test_*.py` + `helpers.py` / 110 funções de teste (suíte verde), incluindo o `test_init.py` (feature 007, cobertura do fluxo de bootstrap e upgrade do framework em diretórios de destino) e os **três novos da feature 009**: `test_antigravity_hook_bridge.py` (payloads-fixture no stdin e stdout exigido por evento), `test_antigravity_hooks_materializer.py` (escrita/merge por named-hook do `.agents/hooks.json`) e `test_antigravity_profile.py` (`hooks_block()` parseável e `apply_instructions()` sem aviso de placeholder).
- **`harness.toml`** 🟢 — Configuração tipada, agora registrando a versão local (`version`) e o caminho para o upstream local (`upstream_path`) na seção `[harness]`.
- **`requirements.txt`** 🟢 — dependências do projeto.

### 🗂️ Estado e Decisões versionados (`.harness/`)

- **`.harness/estado-da-sessao.md`** 🟢 — Estado de sessão unificado.
- **`.harness/decisoes/MD-0001..MD-0005.md`** 🟢 — Fichas de microdecisão.
- **`.harness/microdecisoes.md`** 🟢 — Índice DERIVADO pelo `./harness decisions`.

### ⚙️ Configuração de ganchos por harness

- **`.claude/settings.json`** 🟢 — Hooks Claude Code.
- **`.gemini/settings.json`** 🟢 — Hook Gemini.
- **`.agents/hooks.json`** 🟢 **(NOVO — feature 009)** — Ganchos do Antigravity, no esquema `hooks.json` declarativo (named-hook `harness`, eventos `PreToolUse`/`PostToolUse`/`Stop`). Materializado no projeto-alvo pelo `init`/`upgrade` via `materialize_hooks_json`, com `command` por caminho absoluto e merge por named-hook (preserva chaves de terceiros).

### 🔄 Features Forward (`_reversa_forward/`)

- `001-run-harness-core-local/` — execução local do core.
- `002-documentacao-uso-html/` — gerador de documentação HTML.
- `003-instalacao-por-prompt/` — comando `install-prompt`.
- `004-estado-sessao-unificado/` — estado de sessão em `.harness/` com reinjeção.
- `005-decisoes-em-harness/` — migração de decisões e desacoplamento de caminhos.
- `006-harness-core-config-canonica/` — harness-core como módulo per-projeto (footprint zero).
- `007-bootstrap-harness-init/` 🟢 — comando `init` e `upgrade` para bootstrap local de novos workspaces.
- `009-hooks-antigravity/` 🟢 **(NOVO)** — ganchos de ciclo de vida para o Antigravity: terceiro driver de entrada `AntigravityHookBridge`, subcomando `agy-hook`, `AntigravityProfile` real e materialização de `.agents/hooks.json` por `init`/`upgrade`.

---

## 🩺 Achados de saúde (para os agentes seguintes)

- 🟢 **Suíte de testes estendida e estável:** A inclusão do `test_init.py` garante a resiliência física do fluxo de cópia recursiva e do processo de atualização evolucionária sem destruir as decisões locais de engenharia reversa.
- 🟢 **Detecção de versão não bloqueante:** O mecanismo passivo de leitura comparativa de versões em relação ao upstream opera de forma eficiente, sem penalizar o tempo de boot da CLI e do servidor MCP.
- 🟢 **Footprint zero preservado:** A criação da venv local e injeção do core nos caminhos de destino obedece às restrições de localidade per-projeto (BR-MIGRAR-007). A feature 009 mantém a restrição: `materialize_hooks_json` escreve apenas `.agents/hooks.json` dentro do projeto-alvo, via `FileSystemPort`, nunca em diretório global do usuário.
- 🟢 **Core agnóstico ao harness reforçado (RN-N5):** confirmado por leitura — a lógica do Antigravity vive no adaptador, no perfil e no materializador; nenhum serviço de domínio foi ramificado por harness, e o `agy-hook` reusa `FormattingService`/`DecisionService` intactos.
- 🟢 **Suíte verde em 110 testes:** os três testes de contrato da feature 009 cobrem o protocolo por payloads-fixture (sem runtime real do Antigravity), sem regressão nos caminhos Claude/Gemini.
