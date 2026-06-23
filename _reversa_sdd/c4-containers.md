# C4 Container Diagram (Nível 2) — harness-core

> Gerado pelo Architect em 2026-06-23 (Re-extração após Feature 002)
> Nível de Documentação: **Completo**

Este diagrama detalha a divisão em containers lógicos do `harness-core`, ilustrando a comunicação, tecnologias e armazenamento.

---

```mermaid
graph TB
    %% Atores
    User["Humano (Iago)<br/>[Desenvolvedor / Revisor]"]
    IA_Agent["Agente de IA (Antigravity/Claude)<br/>[Editor / Automação]"]

    subgraph ProjectRoot [Diretório do Projeto: harness]
        %% Containers Lógicos
        Wrapper["Script Wrapper (harness)<br/>[Bash Script]<br/>Interface simplificada de raiz que localiza a venv Python."]
        
        Venv["Ambiente Virtual (.venv)<br/>[Python 3 venv]<br/>Isolamento local de dependências (toml, mcp, pytest, yaml)."]
        
        CoreCLI["Harness Core CLI (main.py)<br/>[Python 3 CLI]<br/>Ponto de entrada que carrega os serviços e trata parâmetros."]
        
        MCPServer["Servidor MCP (server.py)<br/>[Python 3 / Starlette]<br/>Protocolo de comunicação local para integração direta com a IDE."]
        
        %% Armazenamento / Visualização
        SessionFile["Arquivo de Sessão<br/>[ESTADO-DA-SESSAO.md]<br/>Markdown registrando a hash âncora Git e status da feature."]
        
        CacheFile["Cache de Sincronia<br/>[JSON Cache]<br/>Arquivo registrando timestamp e commit hash do remote origin."]

        DocHTML["Documentação Consolidada (harness-docs.html)<br/>[HTML/CSS/JS Estático]<br/>Documentação de comandos, regras de domínio e checkpoints do Reversa."]
    end

    %% Integrações do Host
    Formatters["Formatadores Locais/Globais<br/>[Ruff / Prettier / Rustfmt]<br/>Binários compilados disparados em subprocesso."]
    GitCli["Git CLI Subprocess<br/>[Subprocess Git]<br/>Sistema de arquivos Git local."]

    %% Fluxos Humano
    User -->|Executa comandos| Wrapper
    User -->|Consulta documentação local| DocHTML
    Wrapper -->|Invoca interpretador com dependências| Venv
    Venv -->|Executa script principal| CoreCLI

    %% Fluxos IA
    IA_Agent -->|Chama ganchos do ciclo de vida| Wrapper
    IA_Agent -->|Consome ferramentas e contexto| MCPServer
    MCPServer -->|Chama serviços locais| CoreCLI

    %% Fluxos do Core CLI
    CoreCLI -->|Lê/Grava estado| SessionFile
    CoreCLI -->|Lê/Grava cache local| CacheFile
    CoreCLI -->|Formata arquivos modificados| Formatters
    CoreCLI -->|Verifica commits locais e remote| GitCli
    CoreCLI -->|Gera HTML standalone| DocHTML
    CoreCLI -->|Inicia servidor HTTP local para expor| User
```

---

## 🛠️ Descrição dos Containers

1. **Script Wrapper (harness):** Utilitário simples e idempotente que localiza o executável correto da venv Python local e despacha chamadas.
2. **Ambiente Virtual (.venv):** Contém o runtime Python 3 e as dependências isoladas instaladas a partir de `requirements.txt`.
3. **Harness Core CLI:** Container contendo os serviços principais de ciclo de vida, decisões, sincronia, formatação e o novo serviço de documentação.
4. **Servidor MCP (Model Context Protocol):** Comunicação baseada em JSON-RPC via `stdin`/`stdout` que disponibiliza ganchos e comandos diretamente ao editor.
5. **ESTADO-DA-SESSAO.md:** Persistência em arquivo Markdown do estado da sessão da feature ativa.
6. **harness-docs.html:** Arquivo consolidado HTML standalone que serve como central informativa e interativa de comandos CLI, regras legadas e progresso do Reversa.
