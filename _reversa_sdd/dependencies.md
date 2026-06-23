# Dependências do Projeto — harness

> Gerado pelo Scout em 2026-06-23 (Re-extração após Feature 002)

Mapeamento de dependências internas, externas, plugins, pacotes e ferramentas de sistema utilizadas pelo framework `harness`.

---

## 🔗 Repositórios e Dependências de Configuração (Duras)

Estes repositórios são configurados e importados no `CLAUDE.md`:

| Dependência | Repositório Canônico | Caminho Local | Papel no Projeto |
|---|---|---|---|
| **agent-memory** | `https://github.com/iago-leal/agent-memory.git` | `~/.agent-memory` | Contém regras globais, memórias compartilhadas (`ALICERCE.md`, `BASTAO.md`) e utilitários de hooks. |
| **skills** | `https://github.com/iago-leal/skills.git` | `~/dev/github_repos/skills` | Repositório canônico contendo todas as skills disponíveis para ativação. |

---

## 🧩 Plugins Habilitados (`claude-config/settings.json`)

Plugins carregados pelo Claude Desktop definidos em `settings.json` → `enabledPlugins`:

* **`skill-creator@claude-plugins-official`**
  - **Origem:** Marketplace oficial `anthropics/claude-plugins-official`
  - **Papel:** Criação e manutenção de skills.
* **`swift-lsp@claude-plugins-official`**
  - **Origem:** Marketplace oficial `anthropics/claude-plugins-official`
  - **Papel:** Suporte para Language Server Protocol (LSP) em Swift.

---

## ⚡ Skills Ativas (`claude-config/skills.active`)

Skills especificadas no manifesto que são montadas como symlinks em `~/.claude/skills/` apontando para o repositório de skills local:

1. **`datestamp`**: Permite gerenciar/inserir timestamps formatados.
2. **`obsidian`**: Integração com notas Obsidian.
3. **`recicla`**: Gestão/limpeza de recursos.
4. **`skill-spec`**: Auxílio na especificação de regras e skills.

---

## 🐍 Dependências do Core Python (`harness-core/requirements.txt`)

Bibliotecas instaladas no ambiente virtual (`harness-core/.venv`) para execução do núcleo Python:

* **`toml` (0.10.2)**: Parser e gerador de arquivos de configuração TOML.
* **`mcp` (1.28.0)**: Biblioteca oficial para integração com o Model Context Protocol.
* **`pytest` (9.1.1)**: Framework de execução de testes automatizados.
* **`pydantic` (2.13.4)**: Validador de dados estruturados e configuração do núcleo.
* **`pyyaml` (6.0.3)**: Manipulador de arquivos YAML.

---

## ⚙️ Dependências de Sistema e Ferramentas CLI

Ferramentas externas invocadas por ganchos, wrapper e scripts de automação:

* **`bash` (>= 3.2)**: Interpretador de shell principal (necessário para o wrapper `harness` e scripts do legado).
* **`python3` (>= 3.8)**: Utilizado para executar o núcleo do sistema (`harness-core/src/main.py`).
* **`git`**: Sistema de controle de versão (utilizado para ganchos Git locais, verificação de sincronia e controle de sessões).
* **`jq`**: Processador de JSON leve (utilizado no legado).
* **`afplay`** (macOS, opcional): Utilizado em ganchos de notificação para reproduzir alertas sonoros.
