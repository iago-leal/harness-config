# C4 Context Diagram (Nível 1) — harness-config

> Gerado pelo Architect em 2026-06-23
> Nível de Documentação: **Completo**

Este diagrama apresenta o sistema `harness-config` no centro, ilustrando as fronteiras do sistema, seus usuários (desenvolvedores e agentes) e as integrações externas.

---

```mermaid
graph TB
    %% Atores
    User["Humano (Iago)<br/>[Desenvolvedor / Revisor]"]
    Claude["Claude Code<br/>[Agente de IA Primário]"]
    Gemini["Gemini CLI / Antigravity<br/>[Agente de IA Secundário]"]

    %% Sistema Central
    Harness["Sistema harness-config<br/>[Ganchos, automação e decisões de infraestrutura]"]

    %% Sistemas Externos
    GitRemote["GitHub / Git Remote<br/>[Repositório de Código e Memória]"]
    HostOS["Ambiente macOS / Linux<br/>[Interpretador Bash & Ferramentas locais]"]
    Obsidian["Vault Obsidian / Notas<br/>[Repositório pessoal de documentação]"]

    %% Relacionamentos Atores -> Sistema
    User -->|Executa comandos, edita e valida| Harness
    Claude -->|Executa slash-commands, lê memórias e edita| Harness
    Gemini -->|Lê bastão e executa tarefas de engenharia reversa| Harness

    %% Relacionamentos Sistema -> Sistemas Externos
    Harness -->|Consulta hashes de branch via ls-remote| GitRemote
    Harness -->|Roda formatadores e resolve PATH| HostOS
    Harness -->|Lê e grava notas ONDE PAREI| Obsidian
```

---

## 🛠️ Descrição dos Relacionamentos

1. **Atores e Agentes:**
   * **Humano (Iago):** Interage com o sistema editando arquivos, escrevendo decisões e aprovando/travando propostas de IAs.
   * **Claude Code:** CLI executada no host local que interage diretamente com o `harness-config` executando os ganchos (SessionStart, PostToolUse) e slash commands customizados.
   * **Gemini CLI:** Agente alternativo que entra no fluxo de trabalho via handoff consumindo dados de memória compartilhada.
2. **Integrações de Infraestrutura:**
   * **GitHub / Git Remote:** Usado no `sync-check.sh` para verificar de forma read-only se o estado local está defasado em relação ao remote.
   * **Host OS:** Sistema que fornece o ambiente Unix, shebang bash e binários de formatação (ruff, prettier, rustfmt, shfmt).
   * **Vault Obsidian / Notas:** Pasta de documentos de texto que servem de histórico cross-host e registro de pendências de atividades.
