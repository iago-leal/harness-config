# C4 Components Diagram (Nível 3) — Scripts e Hooks (Shell)

> Gerado pelo Architect em 2026-06-23
> Nível de Documentação: **Completo**

Este diagrama detalha a estrutura interna do container de **Scripts de Automação e Hooks** do `harness-config`.

---

```mermaid
graph TB
    %% Inputs
    PostToolUseEvent["Gatilho PostToolUse<br/>(Write|Edit)"]
    SessionStartEvent["Gatilho SessionStart<br/>(startup|resume|clear)"]
    SessionEndEvent["Comando /encerrar-sessao"]

    subgraph harness_components [Componentes Internos]
        %% Componentes format-on-edit
        RouterFmt["Roteador format-on-edit.sh<br/>[Função run_fmt / resolve]<br/>Roteia a formatação e resolve binários."]
        
        RootFinder["find_project_root<br/>[Função de busca recursiva]<br/>Sobe diretórios validando contra denylist e HOME."]

        %% Componentes sync-check
        SyncCheck["sync-check.sh<br/>[Função check_repo]<br/>Verifica hashes remotos via ls-remote e valida cache TTL."]
        
        PushCheck["check_local<br/>[Função de checagem local]<br/>Avalia commits locais não integrados."]

        %% Componentes index
        IndexGenerator["gerar-index-decisoes.sh<br/>[Script Bash]<br/>Lê microdecisões e compila microdecisoes.md."]
        
        GraphInversion["Processador de Backlinks<br/>[Filtro awk/sed]<br/>Inverte relações direcionais para gerar backlinks."]

        %% Componente bootstrap
        Bootstrapper["bootstrap.sh<br/>[Script Bash]<br/>Configura ganchos e valida dependências de hosts."]
    end

    %% Arquivos e Caches
    CacheSync["Cache de Hashes Remotos<br/>[~/.claude/.sync-check/*]"]
    MDIndex["Índice Geral de Decisões<br/>[microdecisoes.md]"]
    MDFiles["Microdecisões Físicas<br/>[decisoes/MD-*.md]"]
    
    %% Relações format-on-edit
    PostToolUseEvent --> RouterFmt
    RouterFmt -->|Sobe diretórios| RootFinder
    
    %% Relações sync-check
    SessionStartEvent --> SyncCheck
    SyncCheck -->|Lê/Grava cache se TTL expirado| CacheSync
    SessionStartEvent --> PushCheck
    
    %% Relações index
    SessionEndEvent --> IndexGenerator
    IndexGenerator -->|Lê arquivos de decisão| MDFiles
    IndexGenerator -->|Calcula backlinks| GraphInversion
    GraphInversion -->|Gera índice consolidado| MDIndex
    
    %% Relações bootstrap
    Bootstrapper -->|Instala/Valida ganchos no Git| GitHooks[".git/hooks/"]
```

---

## 🛠️ Descrição dos Componentes

1. **Roteador `format-on-edit.sh` (`RouterFmt`):**
   * **Responsabilidade:** Extrai a entrada JSON via `jq`, normaliza o caminho absoluto, verifica a presença de `.no-autoformat` e despacha para os formatadores do sistema utilizando caminhos estáveis (`$HOME/.local/bin`, `/opt/homebrew/bin`, etc.).
2. **Detector de Raiz de Projeto (`RootFinder`):**
   * **Responsabilidade:** Executa busca linear e recursiva ascendente. Possui um vetor de bloqueio (`NON_ROOT_DIRS` e `DENY_PREFIXES`) que blinda o diretório principal do usuário de formatações acidentais.
3. **Verificador de Hashes Remotos (`SyncCheck`):**
   * **Responsabilidade:** Executa `git ls-remote` em modo read-only e compara o hash retornado com a base local. Controla o throttle de requisições web por meio de um TTL em cache.
4. **Verificador de Alterações Locais (`PushCheck`):**
   * **Responsabilidade:** Executa análises locais por commits à frente do upstream ou arquivos modificados, alertando se houver trabalho não pushado nos repositórios críticos.
5. **Compilador de Índice (`IndexGenerator`):**
   * **Responsabilidade:** Vence o particionamento compilando o arquivo de índice navegável geral das microdecisões no repositório local.
6. **Processador de Backlinks (`GraphInversion`):**
   * **Responsabilidade:** Inverte as arestas direcionadas declaradas nos metadados das microdecisões (ex: se A refina B, B ganha automaticamente um backlink `refinado-por A` no índice compilado).
7. **Inicializador (`Bootstrapper`):**
   * **Responsabilidade:** Garante reprodutibilidade do ambiente ao clonar ou subir o projeto em um host novo, vinculando os ganchos locais ao Git.
