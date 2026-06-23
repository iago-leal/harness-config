# C4 Containers Diagram (Nível 2) — harness-config

> Gerado pelo Architect em 2026-06-23
> Nível de Documentação: **Completo**

Este diagrama detalha as aplicações, serviços, scripts e estruturas de persistência em disco que compõem o sistema `harness-config`.

---

```mermaid
graph TB
    %% Atores
    User["Humano (Iago)<br/>[Desenvolvedor]"]
    
    %% Containers
    subgraph harness_containers [Containers do Sistema]
        ClaudeCLI["Claude Code CLI<br/>[Node.js / Editor Sandbox]<br/>Orquestra comandos e hooks de ciclo de vida."]
        
        AutomationScripts["Scripts de Automação<br/>[Bash / CLI em bin/]<br/>bootstrap.sh, sync-check.sh, gerar-index-decisoes.sh."]
        
        FormatterHook["Roteador format-on-edit.sh<br/>[Bash / PostToolUse Hook]<br/>Intercepta edições e despacha para formatadores."]
        
        DiskState["Estrutura de Persistência em Disco<br/>[Arquivos Locais MD/JSON/TOML]<br/>Decisões particionadas, estado de sessão e configs."]
        
        SharedMemory["Pasta de Memória Compartilhada<br/>[~/.agent-memory/]<br/>Contém BASTAO.md e ALICERCE.md."]
    end

    %% Relações Externas e Atores
    User -->|Interage com a CLI| ClaudeCLI
    ClaudeCLI -->|Dispara SessionStart e encerramento| AutomationScripts
    ClaudeCLI -->|Dispara PostToolUse após escrita| FormatterHook
    
    %% Comunicação Interna
    AutomationScripts -->|Lê e grava estado / compila backlinks| DiskState
    FormatterHook -->|Consulta manifestos e .no-autoformat| DiskState
    AutomationScripts -->|Arquiva e recupera bastão| SharedMemory
    
    %% Interação com Host OS (Formatadores)
    FormatterOS["Formatadores do Host OS<br/>[Ruff, Prettier, Rustfmt, Shfmt]<br/>Ferramentas de estilização de código."]
    FormatterHook -->|Executa de forma local ou global| FormatterOS
```

---

## 🏗️ Detalhamento dos Containers

1. **Claude Code CLI:**
   * **Papel:** O container de execução principal que atua como interpretador e sandbox para os agentes de IA. Ele gerencia as configurações locais e dispara os ganchos do ciclo de vida definidos em `settings.json`.
2. **Scripts de Automação (bin/):**
   * **Tecnologia:** Bash puro.
   * **Papel:** Automatiza tarefas de bootstrapping de hosts novos, verificação periódica de sincronia de código (ls-remote com TTL cache) e compilação do índice de microdecisões resolvendo backlinks de relações inversas.
3. **Roteador `format-on-edit.sh`:**
   * **Tecnologia:** Bash puro.
   * **Papel:** Escuta gravações e edições feitas pelo Claude Code e aciona ferramentas de linting/formatting de forma síncrona não-bloqueante (retorna status 0).
4. **Estrutura de Persistência em Disco:**
   * **Tecnologia:** Sistema de arquivos local.
   * **Papel:** Persiste os dados estruturados de estado da sessão (`ESTADO-DA-SESSAO.md`), configurações globais e individuais do Claude (`settings.json`, `.claude/`), e a base de conhecimento de decisões técnicas em arquivos Markdown individuais (`decisoes/MD-NNNN.md`).
5. **Pasta de Memória Compartilhada:**
   * **Tecnologia:** Sistema de arquivos local sob `~/.agent-memory/`.
   * **Papel:** Serve como ponte de comunicação assíncrona entre o Claude e o Gemini, permitindo a troca de bastões sem dependência de rede.
