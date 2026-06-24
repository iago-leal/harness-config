# Impacto no Legado (Legacy Impact) — Feature 008

> Identificador: `008-reprodutibilidade-e-config`
> Data: `2026-06-24`

Avaliação do impacto físico e conceitual das alterações introduzidas pela feature 008 no ecossistema legado do `harness`.

---

## 🛠️ 1. Arquivos Afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
| :--- | :--- | :--- | :--- | :--- |
| `harness-core/requirements.in` | `infra/dependencies` | `delta-de-dados` | `LOW` | Criação do arquivo de definição de dependências diretas. |
| `harness-core/requirements.txt` | `infra/dependencies` | `delta-de-dados` | `MEDIUM` | Compilação e fixação de versões de dependências transitivas. |
| `harness-core/src/core/formatting/service.py` | `core/formatting` | `regra-alterada` | `MEDIUM` | Implementação de opt-out dinâmico e suporte a exclusões de caminhos com glob patterns. |
| `harness-core/src/main.py` | `adapters/cli` | `regra-alterada` | `LOW` | Carga de configuração e injeção no formatador da CLI. |
| `harness-core/src/adapters/mcp/server.py` | `adapters/mcp` | `regra-alterada` | `LOW` | Carga de configuração e injeção no formatador MCP. |
| `.github/workflows/ci.yml` | `infra/ci-cd` | `componente-novo` | `MEDIUM` | Implementação do pipeline de CI automático com pytest e uv. |

---

## 🔍 2. Diff Conceitual por Componente

### `core/formatting`
O `FormattingService` deixa de ter caminhos de exclusão e arquivos de recusa de autoformatação chumbados em código como única via de controle. Agora, a classe aceita opcionalmente um objeto `HarnessConfig` por injeção de dependência e resolve os nomes de opt-out e regras de exclusão dinamicamente a partir das definições do TOML, respeitando glob patterns (`fnmatch`) e caminhos relativos à raiz do projeto.

### `adapters` (CLI/MCP)
A inicialização de drivers carrega as configurações via `load_config` e as repassa de forma transparente para a instanciação do `FormattingService`, mantendo o isolamento hexagonal e garantindo comportamento consistente entre a execução por console e por Model Context Protocol.

### `infra/dependencies` e `infra/ci-cd`
Adição de reprodutibilidade determinística por compilação estrita de dependências transitivas com `uv`, e verificação contínua automática de saúde do repositório através de GitHub Actions no Python 3.12 e 3.13.

---

## 🟢 3. Regras Preservadas

* **RN-01 (Janela TTL de Sincronia):** Sem alterações na lógica de TTL.
* **RN-02 (Resiliência Offline):** Sem alterações no tratamento de falhas de git/rede.
* **RN-03 (Não-Bloqueio de Formatadores):** O formatador de arquivos continua blindado com `try/except Exception` retornando sempre 0 em falhas, garantindo comportamento não-bloqueante.
* **RN-05 (Precedência de Executáveis Locais):** Resolução de Ruff e Prettier locais no projeto continua prioritária.
* **RN-N17 (Footprint Global Zero):** Nenhuma gravação externa fora do workspace.

---

## ⚠️ 4. Regras Modificadas

* **RN-04 (Proteção de Diretórios Críticos):** Modificada para acomodar a validação dinâmica de `exclude_paths` configurado no TOML, mantendo a blindagem básica incondicional de segurança (`~`, `~/Notas`, `~/.claude`).
* **RN-06 (Opt-out do Projeto):** Modificada para usar o nome de arquivo definido no campo `opt_out_file` de `harness.toml` dinamicamente no loop de subida da árvore do projeto.
