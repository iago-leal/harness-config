# Inventário do Projeto — harness

> Gerado pelo Scout em 2026-06-24 (Re-extração após as features 003, 004, 005, 006 e 007)
> Atualização cirúrgica em 2026-06-24 após a feature 007: adição do comando `init` e `upgrade` no wrapper de raiz, novos `tests/test_init.py` e `src/core/bootstrap/init_service.py`, caminhos de evolução/bootstrap em CLI e MCP.

Mapeamento da superfície de código e arquivos de configuração do diretório `/Users/iagoleal/dev/harness`.

---

## 📊 Estatísticas Gerais

- **Diretório Alvo:** `/Users/iagoleal/dev/harness`
- **Escopo da contagem:** código da aplicação (`harness-core/`, wrapper de raiz, configs e `.harness/`). Excluídos: `.venv`, `.git`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `tmp/`, os artefatos do próprio Reversa (`.reversa/`, `_reversa_sdd/`, `_reversa_forward/`) e as duas árvores-espelho de **templates de skills do Reversa** (`.claude/skills/` e `.agents/skills/`, ~430 arquivos de framework, não de produto).
- **Linguagens Principais (aplicação):**
  - **Python (`.py`)**: 55 arquivos — 38 em `harness-core/src/` e 17 em `harness-core/tests/` (a feature 007 acrescentou `init_service.py` e `test_init.py`).
  - **Markdown (`.md`)**: 12 arquivos — instruções de agente (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`), as 5 fichas de decisão em `.harness/decisoes/` (`MD-0001`..`MD-0005`) mais o `_cabecalho.md`, o índice `.harness/microdecisoes.md`, o estado de sessão e o template `install/template.md`.
  - **HTML (`.html`)**: 2 arquivos — `harness-core/src/core/documentation/template.html` e o consolidado `harness-docs.html` na raiz.
  - **Shell (`harness`)**: 1 wrapper Bash executável na raiz.
  - **TOML (`.toml`)**: 1 arquivo (`harness-core/harness.toml`).
  - **JSON (`.json`)**: 2 arquivos de configuração de ganchos (`.claude/settings.json`, `.gemini/settings.json`).

> ⚠️ **Mudança estrutural vs extração anterior:** o módulo legado `claude-config/` foi purgado anteriormente. A feature 007 expandiu os arquivos e testes do core, introduzindo novos pontos de entrada para inicialização de repositório (`init`) e upgrade evolucionário (`upgrade`) preservando os metadados locais de engenharia reversa.

---

## 📂 Estrutura de Diretórios e Arquivos

### ⚡ Raiz do Projeto

- **`harness`** 🟢 — Wrapper Bash executável. Resolve a venv local (`harness-core/.venv/bin/python3`) e encaminha todos os argumentos para `harness-core/src/main.py`.
- **`harness-docs.html`** 🟢 — HTML standalone gerado por `doc-gen`, consolidando a superfície da CLI, o domínio (`_reversa_sdd/domain.md`) e o estado do Reversa.
- **`CLAUDE.md` / `GEMINI.md` / `AGENTS.md`** 🟢 — Instruções de ativação do framework Reversa por harness, agora contendo a instrução de uso dos comandos `./harness init` e `./harness upgrade`.

### 📦 Núcleo Python (`harness-core/`) — arquitetura hexagonal

- **`src/main.py`** 🟢 — Entrada da CLI (v2.0.0). Subcomandos: `bootstrap`, `format`, `decisions`, `cmd`, `doc-gen`, `doc-serve`, `install-prompt` e os **novos `init` e `upgrade`** (feature 007). Injeta aviso de nova versão disponível se a versão local for menor que a versão do upstream.
- **`src/core/`** — Regras de negócio (domínio puro), uma pasta por capacidade:
  - **`bootstrap/`** 🟢 — instalação de ganchos Git locais e o **novo `init_service.py`** (feature 007, serviço que orquestra a cópia do core, wrapper, setup da `.venv` e dos ganchos Git no destino).
  - **`formatting/`** 🟢 — formatação de arquivo por linguagem.
  - **`sync/`** 🟢 — verificação de sincronia Git e detecção passiva e comparação rápida de versão local vs upstream.
  - **`decisions/`** 🟢 — carga, validação de integridade do grafo e compilação do índice de microdecisões.
  - **`commands/`** 🟢 — execução de slash commands de sessão (`resume`, `encerrar-sessao`, `handoff`, `clarificar`).
  - **`documentation/`** 🟢 — geração do HTML (`service.py` + `template.html`).
  - **`install/`** 🟢 — render do prompt colável por composição.
  - **`session/`** 🟢 — estado de sessão unificado.
  - **`domain/`** 🟢 — modelos Pydantic, cache e configuração tipada (`HarnessConfig` tipado, agora com suporte a `upstream_path` e `version` na seção `[harness]`).
  - **`ports/`** 🟢 — interfaces (Protocols) `fs.py` (com o método `is_dir`), `git.py` e `process.py` (com o método `run_command`).
- **`src/adapters/`** 🟢 — Infraestrutura física: `fs/local.py` (implementação de `is_dir`), `git/subprocess.py`, `process/formatter.py` (implementação de `run_command`) e `mcp/server.py` (servidor FastMCP expondo `format_file`, `check_repository_sync`, `process_decisions`, `session_command` e alertas passivos de atualização no boot).
- **`tests/`** 🟢 — 15 arquivos `test_*.py` + `helpers.py` / 66 funções de teste (suíte verde), incluindo o **novo `test_init.py`** (feature 007, cobertura do fluxo de bootstrap e upgrade do framework em diretórios de destino).
- **`harness.toml`** 🟢 — Configuração tipada, agora registrando a versão local (`version`) e o caminho para o upstream local (`upstream_path`) na seção `[harness]`.
- **`requirements.txt`** 🟢 — dependências do projeto.

### 🗂️ Estado e Decisões versionados (`.harness/`)

- **`.harness/estado-da-sessao.md`** 🟢 — Estado de sessão unificado.
- **`.harness/decisoes/MD-0001..MD-0005.md`** 🟢 — Fichas de microdecisão.
- **`.harness/microdecisoes.md`** 🟢 — Índice DERIVADO pelo `./harness decisions`.

### ⚙️ Configuração de ganchos por harness

- **`.claude/settings.json`** 🟢 — Hooks Claude Code.
- **`.gemini/settings.json`** 🟢 — Hook Gemini.

### 🔄 Features Forward (`_reversa_forward/`)

- `001-run-harness-core-local/` — execução local do core.
- `002-documentacao-uso-html/` — gerador de documentação HTML.
- `003-instalacao-por-prompt/` — comando `install-prompt`.
- `004-estado-sessao-unificado/` — estado de sessão em `.harness/` com reinjeção.
- `005-decisoes-em-harness/` — migração de decisões e desacoplamento de caminhos.
- `006-harness-core-config-canonica/` — harness-core como módulo per-projeto (footprint zero).
- `007-bootstrap-harness-init/` 🟢 **(NOVO)** — comando `init` e `upgrade` para bootstrap local de novos workspaces.

---

## 🩺 Achados de saúde (para os agentes seguintes)

- 🟢 **Suíte de testes estendida e estável:** A inclusão do `test_init.py` garante a resiliência física do fluxo de cópia recursiva e do processo de atualização evolucionária sem destruir as decisões locais de engenharia reversa.
- 🟢 **Detecção de versão não bloqueante:** O mecanismo passivo de leitura comparativa de versões em relação ao upstream opera de forma eficiente, sem penalizar o tempo de boot da CLI e do servidor MCP.
- 🟢 **Footprint zero preservado:** A criação da venv local e injeção do core nos caminhos de destino obedece às restrições de localidade per-projeto (BR-MIGRAR-007).
