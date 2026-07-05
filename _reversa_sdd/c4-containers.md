# C4 Container Diagram (Nível 2) — harness-core

> Regenerado pelo Architect em 2026-06-24 (Re-extração após as features 003, 004 e 005)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO
> **Re-extração estrutural de 2026-07-05** (Architect, este documento estava congelado desde 2026-06-24 e não incorporava nem a relocação de 011 nem os drivers/containers de 009-021): ver nota "Mudanças estruturais 010-021" após a nota original, e o split Shim/Upstream no diagrama.

Containers lógicos do `harness-core`, suas tecnologias, a comunicação entre eles e os artefatos versionados em `.harness/`. **Não há banco de dados** — a persistência é em arquivos.

> ⚠️ **Mudanças vs extração anterior:** o container de estado de sessão foi **realocado** de `ESTADO-DA-SESSAO.md` (raiz) para `.harness/estado-da-sessao.md` (f004); surgiu o conjunto `.harness/decisoes/` + `.harness/microdecisoes.md` (f005), lido via `[decisions]` no `harness.toml`; o cache de sincronia passou a `.harness/sync_cache.json` (chumbado no MCP).

> ⚠️ **Mudanças estruturais 010-021 (reconciliação 2026-07-05):** (1) o core inteiro relocou de `harness-core/` para `.harness/harness-core/` (feature 011) — todos os caminhos abaixo foram corrigidos; (2) surgiu o **driver de ganchos do Antigravity** (`AntigravityHookBridge`, `adapters/antigravity/hook_bridge.py`, feature 009), consumido via subcomando `agy-hook`; (3) `.harness/decisoes/` cresceu de 5 para 12 fichas; (4) **a partir da feature 020, o container muda de forma**: o `init` deixa de instalar uma cópia do `CoreCLI`/`Venv` no projeto-alvo — instala só o **Shim** (`./harness`, agora um script fino que executa o core do **upstream**), a árvore `.harness/` e `harness.toml` (com `upstream_path`). `CoreCLI`/`Venv` passam a ser um container **compartilhado, hospedado no repositório upstream**, não mais um container per-projeto — exceto em instalações ainda não convertidas por `migrate` (novo comando, feature 020), que continuam com a cópia local até serem migradas; (5) `session/close_flow.py` (018) e `session/resume_context.py` (021) são novos componentes dentro do `CoreCLI`, detalhados em `c4-components.md`.

---

```mermaid
graph TB
    %% Atores
    User["Humano (Iago)"]
    IA["Agente de IA<br/>(Claude / Gemini / Antigravity)"]

    subgraph Upstream [Repositório Upstream — fonte compartilhada, f020]
        UpCoreCLI["CLI (.harness/harness-core/src/main.py)<br/>[Python 3 / argparse]<br/>12 subcomandos; orquestra serviços; resolve sink; serve doc."]
        UpVenv["Ambiente Virtual (.venv)<br/>[Python 3.14 venv]<br/>fastmcp, pydantic, pytest, toml."]
        MCPServer["Servidor MCP (adapters/mcp/server.py)<br/>[FastMCP / JSON-RPC stdio]<br/>4 tools: format_file, check_repository_sync, process_decisions, session_command."]
        AgyDriver["Driver Antigravity (adapters/antigravity/hook_bridge.py)<br/>[AntigravityHookBridge, f009]<br/>stdin/stdout JSON por evento; sempre exit 0."]
    end

    subgraph ProjectRoot [Diretório de um Projeto-Alvo — pós f020]
        Shim["Shim (./harness)<br/>[Bash, render_shim()]<br/>cd na raiz + exec do CLI do upstream, repassa argumentos e exit code."]
        Migrate["harness migrate --dry-run<br/>[core/migrate/service.py, f020]<br/>Converte instalação do layout copiado p/ o Shim."]

        subgraph HarnessDir [.harness/ — estado e decisões versionados, per-projeto]
            SessionFile["estado-da-sessao.md<br/>[Markdown front-matter YAML + corpo]<br/>Âncora Git + narrativa de retomada (f004)."]
            DecisionsDir["decisoes/MD-NNNN.md + _cabecalho.md<br/>[Markdown front-matter]<br/>12 fichas do grafo de decisões (f005; cresceu de 5)."]
            IndexFile["microdecisoes.md<br/>[Markdown DERIVADO]<br/>Índice com backlinks (hook Stop); lido também pelo resume (f021)."]
            CacheFileCli["sync-cache.json (hífen)<br/>[JSON]<br/>Cache do check passivo da CLI; coberto pelo .gitignore do init."]
            CacheFileMcp["sync_cache.json (underscore)<br/>[JSON — DIVIDA TECNICA]<br/>Cache chumbado no MCP server; nome diverge do .gitignore."]
        end

        Config["harness.toml<br/>[TOML]<br/>harness.active_harness+upstream_path; formatting; sync; decisions; session.state_file+inject_decisions_index (f021)."]
        DocHTML["harness-docs.html<br/>[HTML/CSS/JS estático autossuficiente]<br/>Superfície da CLI + regras de domínio + checkpoints."]
        AgyFile[".agents/rules/estado-sessao.md<br/>[Markdown projetado]<br/>Sink de arquivo p/ Antigravity (f004)."]
        SkillsDir[".claude/skills/ ou .agents/skills/encerrar-sessao/<br/>[SKILL.md + scripts/, f018]<br/>Consome SessionCloseFlow do upstream."]
    end

    %% Bordas do Host
    Formatters["Formatadores<br/>[ruff / prettier / rustfmt]<br/>Subprocessos não-bloqueantes."]
    GitCli["Git CLI<br/>[git rev-parse / ls-remote / commit_paths]"]
    HttpSrv["HTTP local<br/>[http.server :8000]"]

    %% Fluxos humano
    User -->|Executa subcomandos| Shim
    User -->|Roda avulso p/ converter a base| Migrate
    User -->|Edita decisões / config| Config
    User -->|Consulta doc| HttpSrv
    Shim -->|cd + exec com upstream_path| UpCoreCLI
    Migrate -->|Escreve Shim + hooks + settings; remove core local por ultimo| ProjectRoot

    %% Fluxos IA
    IA -->|Hooks de ciclo de vida| Shim
    IA -->|Consome 4 tools| MCPServer
    IA -->|Ganchos .agents/hooks.json p/ agy-hook| AgyDriver

    %% Drivers -> servicos / config
    UpCoreCLI -->|load_config do PROJETO, via cwd| Config
    MCPServer -->|load_config tipada| Config
    UpCoreCLI -->|Le/grava estado via config.session.state_file| SessionFile
    MCPServer -->|Le/grava estado via config.session.state_file| SessionFile
    UpCoreCLI -->|resume: + apendice do indice, f021, Claude only| IndexFile
    UpCoreCLI -->|Compila indice| IndexFile
    UpCoreCLI -->|Le fichas| DecisionsDir
    MCPServer -->|Le fichas| DecisionsDir
    UpCoreCLI -->|Le/grava cache| CacheFileCli
    MCPServer -->|Le/grava cache| CacheFileMcp
    UpCoreCLI -->|Projeta estado p/ Antigravity| AgyFile
    UpCoreCLI -->|materialize: grava skill| SkillsDir
    AgyDriver -->|format_file / decisions| Formatters
    AgyDriver -->|reindexacao Stop| DecisionsDir

    %% Drivers -> bordas
    UpCoreCLI -->|format_file| Formatters
    MCPServer -->|format_file / sync| Formatters
    UpCoreCLI -->|Ancora / sincronia / commit_paths| GitCli
    MCPServer -->|Ancora / sincronia| GitCli
    UpCoreCLI -->|doc-gen / doc-serve| DocHTML
    DocHTML --> HttpSrv
```

---

## 🛠️ Descrição dos Containers

| Container                                                  | Tecnologia                         | Papel                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ---------------------------------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Shim (`./harness`, projeto-alvo)**                       | Bash (`render_shim()`)             | **Desde a f020**: não é mais o wrapper que invoca uma venv local — resolve `upstream_path` do `harness.toml` do projeto, `cd` para a raiz e executa o CLI do **upstream**, repassando argumentos e exit code. Erro barulhento se upstream ausente. 🟢                                                                                                                                                                                                    |
| **CLI (`main.py`, upstream)**                              | Python / argparse                  | Driver de entrada primário, agora **compartilhado** entre todos os projetos convertidos. 12 subcomandos: `bootstrap`, `format`, `decisions`, `cmd`, `doc-gen`, `doc-serve`, `install-prompt`, `init`, `upgrade`, `agy-hook`, `materialize`, `migrate`. 🟢                                                                                                                                                                                                |
| **Venv (`.venv`, upstream)**                               | Python 3.14 venv                   | Runtime + dependências isoladas (`fastmcp`, `pydantic`, `pytest`, `toml`) — **uma só cópia**, no upstream, não mais uma por projeto (f020). 🟢                                                                                                                                                                                                                                                                                                           |
| **Servidor MCP (`server.py`, upstream)**                   | FastMCP (JSON-RPC stdio)           | Driver de entrada secundário; 4 tools. T1 (cf73980) e T2 (f006) resolvidos. 🟢                                                                                                                                                                                                                                                                                                                                                                           |
| **Driver Antigravity (`hook_bridge.py`, upstream)**        | Python (stdin/stdout JSON)         | Terceiro driver de entrada (f009): captura/formatação/decisões por evento, sempre exit 0. 🟢                                                                                                                                                                                                                                                                                                                                                             |
| **`harness migrate` (projeto-alvo, avulso)**               | Python (`core/migrate/service.py`) | Converte instalações no layout copiado (Venv+CoreCLI locais) para o Shim; guardas contra autodestruição; `--dry-run`. **Novo (f020).** 🟢                                                                                                                                                                                                                                                                                                                |
| **`.harness/estado-da-sessao.md`**                         | Markdown (front-matter + corpo)    | Estado de sessão unificado + narrativa de retomada ✨f004. 🟢                                                                                                                                                                                                                                                                                                                                                                                            |
| **`.harness/decisoes/` + `_cabecalho.md`**                 | Markdown front-matter              | Fichas do grafo de microdecisões ✨f005 — **12 fichas** (cresceu de 5). 🟢                                                                                                                                                                                                                                                                                                                                                                               |
| **`.harness/microdecisoes.md`**                            | Markdown derivado                  | Índice com backlinks, gerado pelo hook `Stop`; **desde f021**, também lido pelo `resume` (Claude) para ancorar a busca do agente. 🟢                                                                                                                                                                                                                                                                                                                     |
| **`.harness/sync-cache.json`** (hífen)                     | JSON                               | Cache TTL do check passivo de versão feito pela **CLI** (`main.py`); coberto pelo `.gitignore` que o `init` grava. 🟢                                                                                                                                                                                                                                                                                                                                    |
| **`.harness/sync_cache.json`** (underscore)                | JSON                               | Cache TTL chumbado no **servidor MCP** (`server.py:42`) — nome diferente do da CLI. 🟡 **Dívida técnica (achada nesta reconciliação):** o `.gitignore` gravado pelo `init` cobre só `sync-cache.json` (hífen); se o servidor MCP rodar, cria um arquivo com nome distinto que a oferta de commit pendente (f019, que parou de mascarar `.harness/` inteiro) passaria a **oferecer para commit** por engano. Ver `architecture.md` §5 (dívidas técnicas). |
| **`harness.toml`**                                         | TOML                               | Configuração; `[decisions]` desacopla os caminhos ✨f005; `[session].state_file`+`inject_decisions_index` (f021); `[harness].upstream_path` como âncora de execução (f020). 🟢                                                                                                                                                                                                                                                                           |
| **`harness-docs.html`**                                    | HTML/CSS/JS estático               | Documentação standalone offline, gerada por introspecção. 🟢                                                                                                                                                                                                                                                                                                                                                                                             |
| **`.agents/rules/estado-sessao.md`**                       | Markdown projetado                 | Sink de arquivo para Antigravity ✨f004. 🟡                                                                                                                                                                                                                                                                                                                                                                                                              |
| **`.claude/skills/` ou `.agents/skills/encerrar-sessao/`** | `SKILL.md` + `scripts/`            | Capacidade de encerramento materializada como skill (f018, substitui slash-command/workflow `.md` da f010/017); scripts consomem `SessionCloseFlow` do upstream. 🟢                                                                                                                                                                                                                                                                                      |

> **Sem banco de dados / sem container de fila ou cache distribuído.** 🟢 Toda a persistência é em arquivos locais versionados (Markdown/JSON/TOML). O servidor MCP **não** mantém estado de sessão próprio: opera sobre os mesmos arquivos da CLI (embora com um cache de sync próprio e desalinhado, ver dívida acima). O desvio T2 (MCP apontando para `ESTADO-DA-SESSAO.md` na raiz) foi **corrigido** na feature 006 — CLI e MCP leem o mesmo caminho de `config.session.state_file`, sem máquina de estado paralela.
>
> **🟡 Nota de topologia (f020):** instalações **ainda não convertidas** por `harness migrate` continuam no layout antigo — `CoreCLI`/`Venv` per-projeto, sem o Shim. O diagrama acima retrata o estado **pós-conversão** (o alvo da feature 020); o layout antigo é o que este documento descrevia até esta reconciliação.
