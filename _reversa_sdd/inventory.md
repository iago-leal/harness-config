# Inventário do Projeto — harness

> Gerado pelo Scout em 2026-06-23 (Re-extração após Feature 002)

Mapeamento da superfície de código e arquivos de configuração do diretório `/Users/iagoleal/dev/harness`.

---

## 📊 Estatísticas Gerais

* **Diretório Alvo:** `/Users/iagoleal/dev/harness`
* **Total de Arquivos:** 101 arquivos (excluindo `.venv`, `.git`, `node_modules` e pastas temporárias)
* **Linguagens Principais:**
  * **Python (`.py`)**: 45 arquivos (núcleo, testes do `harness-core` e novos módulos de documentação)
  * **Markdown (`.md`)**: 43 arquivos (documentação, decisões e features forward)
  * **Shell Script (`.sh`, `harness`)**: 6 arquivos (scripts legados e wrapper de raiz)
  * **HTML (`.html`)**: 2 arquivos (template de documentação e o consolidado `harness-docs.html` na raiz)
  * **TOML (`.toml`)**: 1 arquivo (`harness-core/harness.toml`)
  * **JSON (`.json`, `.snippet`)**: 4 arquivos (configurações, snippets de regras e estado de sessões)

---

## 📂 Estrutura de Diretórios e Arquivos

### ⚡ Wrapper de conveniência (Raiz do Projeto)
* **`harness`**: Script Bash executável que invoca o interpretador Python da venv local e encaminha argumentos para `harness-core/src/main.py`.
* **`harness-docs.html`**: Arquivo HTML standalone consolidando a documentação e uso do Harness CLI, regras de negócio e progresso do Reversa.

### 📦 Núcleo Python (`harness-core/`)
* **`harness-core/src/main.py`**: Ponto de entrada principal da CLI do núcleo. Adicionado os subcomandos `doc-gen` e `doc-serve`.
* **`harness-core/src/core/`**: Regras de negócio do Harness (bootstrap, formatação, sincronia, decisões, comandos, e o novo serviço de documentação).
* **`harness-core/src/core/documentation/`**: Novo módulo de documentação contendo `service.py` e o template visual `template.html`.
* **`harness-core/src/adapters/`**: Implementações de infraestrutura física (sistema de arquivos, subprocessos Git, integradores de formato).
* **`harness-core/tests/`**: Suite de testes pytest cobrindo adaptadores, comandos, ganchos, wrapper e documentação (`test_documentation.py`).
* **`harness-core/harness.toml`**: Arquivo de configurações do ciclo de vida e formatação.

### 📋 Mapeamento de Configuração Legado (`claude-config/`)
* **`claude-config/settings.json`**: Arquivo de ganchos Git e configurações do Claude Code legado.
* **`claude-config/bin/`**: Scripts Bash de bootstrap, validação e sincronia legados.
* **`claude-config/hooks/format-on-edit.sh`**: Hook legado de pós-edição de arquivos.
* **`claude-config/decisoes/`**: Fichas de microdecisões de design arquitetural numeradas de `MD-0001` a `MD-0017`.
* **`claude-config/commands/`**: Definições de comandos customizados (clarificar, handoff, resume, etc.).

### ⚙️ Metadados de Controle do Reversa (`.reversa/`)
* **`.reversa/state.json`**: Estado atual do pipeline de engenharia reversa.
* **`.reversa/setup.json`**: Configurações gerais do Reversa (formatos de ID, regras de proteção).
* **`.reversa/active-requirements.json`**: Registro da feature em andamento no ciclo forward.
* **`.reversa/settings.json.snippet`**: Snippet de ganchos sugeridos para o agente de IA local.

### 🔄 Features Forward (`_reversa_forward/`)
* **`_reversa_forward/001-run-harness-core-local/`**: Pasta de artefatos de requisitos, plano técnico e tarefas da execução local.
* **`_reversa_forward/002-documentacao-uso-html/`**: Pasta de requisitos, plano técnico e tarefas do gerador de documentação HTML.
