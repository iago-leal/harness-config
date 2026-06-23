# C4 Context Diagram (Nível 1) — harness-core

> Gerado pelo Architect em 2026-06-23
> Nível de Documentação: **Completo**

Este diagrama apresenta o sistema `harness-core` no centro, ilustrando as fronteiras do sistema, seus usuários (desenvolvedores e agentes) e as integrações externas.

---

```mermaid
graph TB
    %% Atores
    User["Humano (Iago)<br/>[Desenvolvedor / Revisor]"]
    IA_Agent["Agente de IA (Antigravity/Claude)<br/>[Editor / Automação]"]

    %% Sistema Central
    HarnessCore["Sistema harness-core<br/>[Núcleo em Python de ciclo de vida, formatação e decisões]"]

    %% Sistemas Externos
    GitRemote["GitHub / Git Remote<br/>[Repositório de Código e Memória]"]
    HostOS["Ambiente do Host (macOS/Linux)<br/>[Formatadores de terceiros, venv e subprocessos]"]

    %% Relacionamentos Atores -> Sistema
    User -->|Executa comandos via wrapper local| HarnessCore
    IA_Agent -->|Invocado em ganchos SessionStart e PostToolUse| HarnessCore

    %% Relacionamentos Sistema -> Sistemas Externos
    HarnessCore -->|Consulta commits de branch via ls-remote| GitRemote
    HarnessCore -->|Dispara binários locais e globais| HostOS
```

---

## 🛠️ Descrição dos Relacionamentos

1. **Atores e Agentes:**
   * **Humano (Iago):** Interage com o sistema rodando a CLI local via wrapper `./harness` e editando arquivos de microdecisões e documentação.
   * **Agente de IA (Antigravity/Claude):** Interage diretamente com o `harness-core` executando os ganchos do ciclo de vida (como formatar arquivos modificados e atualizar backlinks ao parar).
2. **Integrações de Infraestrutura:**
   * **GitHub / Git Remote:** Usado no `SyncService` para obter o commit HEAD do repositório remoto.
   * **Ambiente do Host:** Fornece o ecossistema Python 3, a pasta virtualenv e os formatadores locais/globais (ruff, prettier, rustfmt).
