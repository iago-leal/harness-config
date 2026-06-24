# C4 Container Diagram (Nível 2) — harness-core

> Regenerado pelo Architect em 2026-06-24 (Re-extração após as features 003, 004 e 005)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO

Containers lógicos do `harness-core`, suas tecnologias, a comunicação entre eles e os artefatos versionados em `.harness/`. **Não há banco de dados** — a persistência é em arquivos.

> ⚠️ **Mudanças vs extração anterior:** o container de estado de sessão foi **realocado** de `ESTADO-DA-SESSAO.md` (raiz) para `.harness/estado-da-sessao.md` (f004); surgiu o conjunto `.harness/decisoes/` + `.harness/microdecisoes.md` (f005), lido via `[decisions]` no `harness.toml`; o cache de sincronia passou a `.harness/sync_cache.json` (chumbado no MCP).

---

```mermaid
graph TB
    %% Atores
    User["Humano (Iago)"]
    IA["Agente de IA<br/>(Claude / Gemini / Antigravity)"]

    subgraph ProjectRoot [Diretório do Projeto: harness]
        Wrapper["Wrapper (./harness)<br/>[Bash]<br/>Resolve a venv e despacha p/ main.py; falha barulhenta sem venv."]
        Venv["Ambiente Virtual (.venv)<br/>[Python 3.14 venv]<br/>mcp, pydantic, pytest, toml, PyYAML."]
        CoreCLI["CLI (src/main.py)<br/>[Python 3 / argparse v2.0.0]<br/>7 subcomandos; orquestra serviços; resolve sink; serve doc."]
        MCPServer["Servidor MCP (adapters/mcp/server.py)<br/>[FastMCP / JSON-RPC stdio]<br/>4 tools: format_file, check_repository_sync, process_decisions, session_command."]

        subgraph HarnessDir [.harness/ — estado e decisões versionados]
            SessionFile["estado-da-sessao.md<br/>[Markdown front-matter YAML + corpo]<br/>Âncora Git + narrativa de retomada (f004)."]
            DecisionsDir["decisoes/MD-NNNN.md + _cabecalho.md<br/>[Markdown front-matter]<br/>Fichas do grafo de decisões (f005)."]
            IndexFile["microdecisoes.md<br/>[Markdown DERIVADO]<br/>Índice com backlinks (hook Stop)."]
            CacheFile["sync_cache.json<br/>[JSON]<br/>Timestamp + commit_hash do último check."]
        end

        Config["harness.toml<br/>[TOML]<br/>[harness] active_harness · [formatting] · [sync] · [decisions] (f005)."]
        DocHTML["harness-docs.html<br/>[HTML/CSS/JS estático autossuficiente]<br/>Superfície da CLI + regras de domínio + checkpoints."]
        AgyFile[".agents/rules/estado-sessao.md<br/>[Markdown projetado]<br/>Sink de arquivo p/ Antigravity (f004)."]
    end

    %% Bordas do Host
    Formatters["Formatadores<br/>[ruff / prettier / rustfmt]<br/>Subprocessos não-bloqueantes."]
    GitCli["Git CLI<br/>[git rev-parse / ls-remote]"]
    HttpSrv["HTTP local<br/>[http.server :8000]"]

    %% Fluxos humano
    User -->|Executa subcomandos| Wrapper
    User -->|Edita decisões / config| Config
    User -->|Consulta doc| HttpSrv
    Wrapper -->|Invoca interpretador| Venv
    Venv -->|Executa| CoreCLI

    %% Fluxos IA
    IA -->|Hooks de ciclo de vida| Wrapper
    IA -->|Consome 4 tools| MCPServer

    %% Drivers -> serviços / config
    CoreCLI -->|load_config| Config
    MCPServer -->|load_config T1| Config
    CoreCLI -->|Lê/grava estado| SessionFile
    MCPServer -.->|T2: aponta p/ ESTADO-DA-SESSAO.md raiz| SessionFile
    CoreCLI -->|Compila índice| IndexFile
    CoreCLI -->|Lê fichas| DecisionsDir
    MCPServer -->|Lê fichas| DecisionsDir
    MCPServer -->|Lê/grava cache| CacheFile
    CoreCLI -->|Projeta estado p/ Antigravity| AgyFile

    %% Drivers -> bordas
    CoreCLI -->|format_file| Formatters
    MCPServer -->|format_file / sync| Formatters
    CoreCLI -->|Âncora / sincronia| GitCli
    MCPServer -->|Âncora / sincronia| GitCli
    CoreCLI -->|doc-gen / doc-serve| DocHTML
    DocHTML --> HttpSrv
```

---

## 🛠️ Descrição dos Containers

| Container | Tecnologia | Papel |
|---|---|---|
| **Wrapper (`./harness`)** | Bash | Resolve `harness-core/.venv/bin/python3` e encaminha argumentos; falha barulhenta sem venv. 🟢 |
| **Venv (`.venv`)** | Python 3.14 venv | Runtime + dependências isoladas (`mcp`, `pydantic`, `pytest`, `toml`, `PyYAML`). 🟢 |
| **CLI (`main.py`)** | Python / argparse | Driver de entrada primário. 7 subcomandos: `bootstrap`, `format`, `decisions`, `cmd`, `doc-gen`, `doc-serve`, `install-prompt` ✨f003. 🟢 |
| **Servidor MCP (`server.py`)** | FastMCP (JSON-RPC stdio) | Driver de entrada secundário; 4 tools. Contém T1 e T2. 🟢 |
| **`.harness/estado-da-sessao.md`** | Markdown (front-matter + corpo) | Estado de sessão unificado + narrativa de retomada ✨f004. 🟢 |
| **`.harness/decisoes/` + `_cabecalho.md`** | Markdown front-matter | Fichas do grafo de microdecisões ✨f005. 🟢 |
| **`.harness/microdecisoes.md`** | Markdown derivado | Índice com backlinks, gerado pelo hook `Stop`. 🟢 |
| **`.harness/sync_cache.json`** | JSON | Cache TTL da verificação de sincronia (chumbado no MCP). 🟢 |
| **`harness.toml`** | TOML | Configuração; seção `[decisions]` desacopla os caminhos ✨f005. 🟢 |
| **`harness-docs.html`** | HTML/CSS/JS estático | Documentação standalone offline, gerada por introspecção. 🟢 |
| **`.agents/rules/estado-sessao.md`** | Markdown projetado | Sink de arquivo para Antigravity ✨f004. 🟡 |

> **Sem banco de dados / sem container de fila ou cache distribuído.** 🟢 Toda a persistência é em arquivos locais versionados (Markdown/JSON/TOML). O servidor MCP **não** mantém estado próprio: opera sobre os mesmos arquivos da CLI (exceto pelo desvio T2, que aponta para `ESTADO-DA-SESSAO.md` na raiz).
