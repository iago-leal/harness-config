# Dependências do Projeto — harness-config

> Gerado pelo Scout em 2026-06-23

Mapeamento de dependências internas, externas, plugins e ferramentas de sistema utilizadas pelo framework `harness-config`.

---

## 🔗 Repositórios e Dependências de Configuração (Duras)

Estes repositórios são clonados/reconciliados pelo script `bin/bootstrap.sh` e importados no `CLAUDE.md`:

| Dependência | Repositório Canônico | Caminho Local | Papel no Projeto |
|---|---|---|---|
| **agent-memory** | `https://github.com/iago-leal/agent-memory.git` | `~/.agent-memory` | Contém regras globais, memórias compartilhadas (`ALICERCE.md`, `BASTAO.md`) e utilitários de hooks. |
| **skills** | `https://github.com/iago-leal/skills.git` | `~/dev/github_repos/skills` | Repositório canônico contendo todas as skills disponíveis para ativação. |

---

## 🧩 Plugins Habilitados (`settings.json`)

Plugins carregados pelo Claude Desktop definidos em `settings.json` → `enabledPlugins`:

* **`skill-creator@claude-plugins-official`**
  * **Origem:** Marketplace oficial `anthropics/claude-plugins-official`
  * **Papel:** Criação e manutenção de skills.
* **`swift-lsp@claude-plugins-official`**
  * **Origem:** Marketplace oficial `anthropics/claude-plugins-official`
  * **Papel:** Suporte para Language Server Protocol (LSP) em Swift.

---

## ⚡ Skills Ativas (`skills.active`)

Skills especificadas no manifesto que são montadas como symlinks em `~/.claude/skills/` apontando para o repositório de skills local:

1. **`datestamp`**: Permite gerenciar/inserir timestamps formatados.
2. **`obsidian`**: Integração com notas Obsidian.
3. **`recicla`**: Gestão/limpeza de recursos.
4. **`skill-spec`**: Auxílio na especificação de regras e skills.

---

## ⚙️ Dependências de Sistema e Ferramentas CLI

Ferramentas externas invocadas por ganchos e scripts de automação (`bin/`):

* **`bash` (>= 3.2)**: Interpretador de shell principal (necessário para todos os scripts de `bin/` e `hooks/`).
* **`python3`**: Utilizado para executar scripts de validação de regras e pontes de memória (ex: `microdecisoes-guard.py`).
* **`jq`**: Processador de JSON leve (utilizado no parsing do stdin/cwd do hook `sync-check.sh`).
* **`git`**: Sistema de controle de versão (utilizado em `sync-check.sh`, `bootstrap.sh` e hooks Git).
* **`afplay`** (macOS, opcional): Utilizado em ganchos de parada/notificação para reproduzir alertas sonoros.
* **`lsappinfo`** (macOS, opcional): Utilizado no gancho `Stop` para verificar a janela ativa em foco.
