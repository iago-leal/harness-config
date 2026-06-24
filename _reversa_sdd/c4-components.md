# C4 Component Diagram (Nível 3) — harness-core

> Regenerado pelo Architect em 2026-06-24 (Re-extração após a feature 009-hooks-antigravity)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO

Componentes internos de `src/core/` e `src/adapters/` sob arquitetura hexagonal. **Novo** nesta extração: o **terceiro driver de entrada** `AntigravityHookBridge` (`src/adapters/antigravity/hook_bridge.py` ✨f009), que delega a `FormattingService` e `DecisionService`, mais o materializador `install/antigravity_hooks.py` (`materialize_hooks_json` ✨f009). Persistem das extrações anteriores: os serviços `install` ✨f003 e `session` ✨f004, e a leitura de config tipada (`load_config`) pelos drivers ✨f005.

---

```mermaid
graph TB
    subgraph drivers [Drivers de entrada]
        CLI["main.py<br/>[CLI argparse v2.0.0]<br/>10 subcomandos · resolve sink · serve HTTP · agy-hook ✨f009"]
        MCP["adapters/mcp/server.py<br/>[FastMCP]<br/>4 tools · T1/T2 resolvidos (cf73980/f006)"]
        AGY["adapters/antigravity/hook_bridge.py ✨f009<br/>[AntigravityHookBridge]<br/>pre/post-tool-use · stop · stdin/stdout JSON · não-bloqueante"]
    end

    subgraph core [Núcleo da Aplicação src/core/]
        subgraph domain [Domínio src/core/domain/]
            Models["models.py<br/>Decision · Relationship<br/>SessionState · SessionNarrative"]
            Cfg["config.py<br/>HarnessConfig · DecisionsSection · SessionSection ✨f006<br/>load_config()"]
            Cache["cache.py<br/>SyncCache"]
        end

        subgraph ports [Portas src/core/ports/]
            FsPort["FileSystemPort [ABC]"]
            GitPort["GitPort [ABC]"]
            ProcPort["ProcessPort [ABC]"]
        end

        subgraph services [Serviços de capacidade]
            BootServ["BootstrapService<br/>install_hooks (pre-commit/post-merge)"]
            FormatServ["FormattingService<br/>format_file (blindagens, opt-out)"]
            SyncServ["SyncService<br/>check_sync (cache TTL)"]
            DecServ["DecisionService<br/>load / validate_integrity / compile_index"]
            CmdServ["CommandService<br/>resume / encerrar-sessao / handoff / clarificar"]
            DocServ["DocumentationService<br/>introspecção argparse + regras + state"]
            InstServ["InstallPromptService ✨f003<br/>render (composição de template)"]
            SessSer["session/serializer ✨f004<br/>parse / render (round-trip)"]
            SessSink["session/sinks ✨f004<br/>HookContextSink / FileProjectionSink"]
            InstProf["install/harness_profiles ✨f003<br/>Claude/Gemini/Antigravity Profile · hooks_block real ✨f009"]
            AgyHooks["install/antigravity_hooks ✨f009<br/>materialize_hooks_json (merge por named-hook)"]
        end
    end

    subgraph adapters [Adaptadores src/adapters/]
        FsAdap["LocalFileSystemAdapter<br/>write_file_atomic (.tmp + os.replace)"]
        GitAdap["SubprocessGitAdapter<br/>rev-parse / ls-remote"]
        FormatAdap["HostFormatterAdapter<br/>ruff / prettier / rustfmt"]
    end

    %% Drivers -> serviços
    CLI --> BootServ & FormatServ & DecServ & CmdServ & DocServ & InstServ
    CLI --> Cfg
    MCP --> FormatServ & SyncServ & DecServ & CmdServ
    MCP -->|load_config tipada (T1 resolvido cf73980)| Cfg

    %% Terceiro driver: ponte de ganchos do Antigravity ✨f009
    AGY -->|post-tool-use| FormatServ
    AGY -->|stop| DecServ
    AGY -->|load_config tipada| Cfg
    AGY -->|scratch stepIdx→TargetFile| FsPort

    %% Composição interna do domínio
    CmdServ --> SessSer
    CLI -->|resolve sink por active_harness| SessSink
    InstServ --> InstProf
    AgyHooks -->|hooks_block canônico| InstProf
    AgyHooks --> FsPort
    DecServ --> Models
    CmdServ --> Models
    SyncServ --> Cache
    Cfg --> Models

    %% Serviços usam portas (injeção)
    BootServ --> FsPort
    FormatServ --> FsPort
    FormatServ --> ProcPort
    SyncServ --> FsPort
    SyncServ --> GitPort
    DecServ --> FsPort
    CmdServ --> FsPort
    CmdServ --> GitPort
    DocServ --> FsPort
    SessSink --> FsPort

    %% Adaptadores implementam portas
    FsAdap -.->|implementa| FsPort
    GitAdap -.->|implementa| GitPort
    FormatAdap -.->|implementa| ProcPort
```

---

## 🛠️ Descrição dos Componentes

### Portas (fronteira de inversão de dependência) 🟢

- **`FileSystemPort`** — `read_file, write_file, write_file_atomic, exists, list_dir, makedirs, remove`.
- **`GitPort`** — `get_head_commit, get_remote_commit`.
- **`ProcessPort`** — `execute_formatter -> (exit, stdout, stderr)`.

### Serviços de capacidade 🟢

- **BootstrapService** — grava `pre-commit`(→`format`) e `post-merge`(→`decisions`) idempotentemente; cada script roda só se o interpretador existir.
- **FormattingService** — `format_file` **sempre retorna 0**; blindagem de `~`/`~/Notas`/`~/.claude`, opt-out por `.no-autoformat`, precedência de binário local, raiz por manifesto (`.git`/`harness.toml`). Consome `[formatting]` (`exclude_paths` com glob/`fnmatch`, `opt_out_file`) dinamicamente do `HarnessConfig` ✨f008 (T4 resolvido). Reusado pela ponte do Antigravity no `PostToolUse` ✨f009.
- **SyncService** — `check_sync` com cache TTL; resiliente (erro → `True`). Exposto **só via MCP** (não há subcomando `sync`).
- **DecisionService** — `load_decisions`, `validate_integrity` (auto-relação e aresta órfã), `compile_index` (backlinks por verbos inversos). Caminhos vêm por parâmetro ✨f005.
- **CommandService** — slash commands agnósticos à IDE; âncora Git no `resume`; distingue ausente (`None`) de malformado (`MalformedSessionStateError`). Não conhece harness (RN-N5).
- **DocumentationService** — introspecção do argparse + regex sobre `domain.md` + `state.json` → injeta JSON no `template.html`.
- **InstallPromptService ✨f003** — `render(active_harness, parser)` por composição (4 placeholders no `template.md`); resolve perfil fail-fast.
- **session/serializer ✨f004** — round-trip `parse(render(x)) == x`; 4 seções fixas mapeiam `SessionNarrative`.
- **session/sinks ✨f004** — `get_sink` por `active_harness`: `HookContextSink` (Claude/Gemini, `additionalContext`, trunca em 10000) ou `FileProjectionSink` (Antigravity). Família por `_FAMILY_BY_HARNESS`; desconhecido → `ValueError`.
- **install/harness_profiles ✨f003** — Strategy (`ABC`) `ClaudeProfile`/`GeminiProfile`/`AntigravityProfile` com `hooks_block()` + `apply_instructions()`. ✨f009 `AntigravityProfile` deixou de ser placeholder: `hooks_block()` emite o named-hook `harness` em JSON válido (`PreToolUse`/`PostToolUse`/`Stop`, `<ABS>` literal até a materialização) e `apply_instructions()` aponta `.agents/hooks.json`; a nota de escopo por harness migrou do `template.md` para o `apply_instructions()` dos três perfis.
- **install/antigravity_hooks ✨f009** — `materialize_hooks_json(fs, project_path, command_path)`: lê o `.agents/hooks.json` existente, substitui o named-hook `harness` pelo bloco canônico do `AntigravityProfile` (com `<ABS>` resolvido para o caminho absoluto) e grava por escrita atômica, preservando chaves de terceiros. Rotina única compartilhada por `init` e `upgrade`. Escreve só sob `project_path` via `FileSystemPort` (RN-N17, footprint zero).

### Driver de borda do Antigravity ✨f009 🟢

- **AntigravityHookBridge** (`adapters/antigravity/hook_bridge.py`) — terceiro driver de entrada, simétrico à CLI e ao servidor MCP. `handle(event, stdin_text)` despacha por evento e devolve o stdout JSON exigido pelo contrato, **nunca levantando** (toda exceção é logada em `stderr` e o fallback do evento é emitido com exit 0; não-bloqueante, RN-03). `pre-tool-use` grava `stepIdx → TargetFile` num scratch sob `artifactDirectoryPath` e emite `{"decision": "allow"}`; `post-tool-use` resolve o caminho pelo `stepIdx` e delega a `FormattingService.format_file` (que honra opt-out/exclusões e retorna 0), emitindo `{}`; `stop` delega a `DecisionService` (`load_decisions` → `validate_integrity` → `compile_index`), emitindo `{}` sem `"continue"`. Recebe `fs`, os dois serviços e os caminhos de decisão por injeção; a instanciação dos adaptadores concretos e a leitura de `load_config` ficam na borda (`main.py`, subcomando `agy-hook`). Core agnóstico ao harness preservado (RN-N5).

### Domínio 🟢

- **models.py** — `Decision`, `Relationship`, `SessionState`, `SessionNarrative` (Pydantic v2, com validadores de regex/enum).
- **config.py** — `HarnessConfig` (`[harness]/[formatting]/[sync]/[decisions]/[session]`) e `load_config(fs)`. ✨ `[decisions]` é a chave da feature 005; ✨ `SessionSection` (`[session].state_file`, default `.harness/estado-da-sessao.md`) é a chave da feature 006, fonte única do caminho de sessão lida por CLI e MCP.
- **cache.py** — `SyncCache`.

### Adaptadores 🟢

- **LocalFileSystemAdapter** — I/O UTF-8; escrita atômica `.tmp` + `os.replace`.
- **SubprocessGitAdapter** — `git rev-parse HEAD`, `git ls-remote origin main`; erro → `RuntimeError`.
- **HostFormatterAdapter** — mapeia formatador→args; binário ausente → `(127, …)`.

> ✅ **Bugs de driver corrigidos (memória histórica):** **T1** — `server.py` chamava `load_config` sem import (NameError na tool de decisões via MCP); **RESOLVIDO** em `cf73980` (import na linha 12). **T2** — `server.py` apontava a sessão para `ESTADO-DA-SESSAO.md` (raiz), divergindo da CLI; **RESOLVIDO** na feature 006: o caminho agora vem de `config.session.state_file` (`SessionSection`), lido igualmente por CLI (`main.py:169`) e MCP (`server.py:94`). **T3** — `main.py` usava `json.loads` sem `import json` (autoformat por hook silenciosamente não ocorria); **RESOLVIDO** em `cf73980` (import na linha 5).
