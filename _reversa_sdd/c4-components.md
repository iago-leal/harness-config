# C4 Component Diagram (Nível 3) — harness-core

> Regenerado pelo Architect em 2026-06-24 (Re-extração após a feature 009-hooks-antigravity)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO
> **Re-extração estrutural de 2026-07-05** (este documento estava congelado desde 2026-06-24/feature 009): novos componentes `core/migrate` (f020), `install/session_skills` (f018, substitui `install/session_commands`), `install/claude_settings` (merge por-item, f020), `session/close_flow` (f018) e `session/resume_context` (f021). Todos os caminhos confirmados sob `.harness/harness-core/` (relocação da feature 011, já vigente mas não refletida aqui até agora).
> **Reconciliação de 2026-07-15** (pós-MD-0014 e features 022-023): novo componente `decisions/gate` (avaliação pura do gate de registro); `GitPort` + `list_changed_paths_since`; `close_flow` com 3º portão; `AntigravityHookBridge` com `gate_evaluator` injetado; `ClaudeProfile`/`claude_settings` sem o `PostToolUse` (MD-0014), Stop com `--gate`.

Componentes internos de `src/core/` e `src/adapters/` sob arquitetura hexagonal. Persistem da extração anterior: o **terceiro driver de entrada** `AntigravityHookBridge` (`src/adapters/antigravity/hook_bridge.py` ✨f009), que delega a `FormattingService` e `DecisionService`, mais o materializador `install/antigravity_hooks.py` (`materialize_hooks_json` ✨f009); os serviços `install` ✨f003 e `session` ✨f004; e a leitura de config tipada (`load_config`) pelos drivers ✨f005. **Novos nesta reconciliação:** o serviço `core/migrate` (✨f020, converte instalações do layout copiado para a fonte única); os materializadores `install/session_skills` (✨f018, substitui `install/session_commands`) e `install/claude_settings` (merge por-item, ✨f020); e dois módulos novos em `session/` — `close_flow` (✨f018, orquestração do encerramento) e `resume_context` (✨f021, apêndice do índice de decisões).

---

```mermaid
graph TB
    subgraph drivers [Drivers de entrada]
        CLI["main.py<br/>[CLI argparse]<br/>12 subcomandos · resolve sink · serve HTTP · agy-hook ✨f009 · migrate ✨f020"]
        MCP["adapters/mcp/server.py<br/>[FastMCP]<br/>4 tools · T1/T2 resolvidos (cf73980/f006)"]
        AGY["adapters/antigravity/hook_bridge.py ✨f009<br/>[AntigravityHookBridge]<br/>pre/post-tool-use · stop · stdin/stdout JSON · não-bloqueante"]
    end

    subgraph core [Núcleo da Aplicação src/core/]
        subgraph domain [Domínio src/core/domain/]
            Models["models.py<br/>Decision · Relationship<br/>SessionState · SessionNarrative"]
            Cfg["config.py<br/>HarnessConfig · DecisionsSection · SessionSection (+inject_decisions_index ✨f021)<br/>load_config()"]
            Cache["cache.py<br/>SyncCache"]
        end

        subgraph ports [Portas src/core/ports/]
            FsPort["FileSystemPort [ABC]<br/>+ remove_tree ✨f020"]
            GitPort["GitPort [ABC]<br/>+ commit_paths, list_dirty_paths, list_changed_paths_since ✨f022"]
            ProcPort["ProcessPort [ABC]"]
        end

        subgraph services [Serviços de capacidade]
            BootServ["BootstrapService<br/>install_hooks (não-destrutivo por assinatura ✨f020)"]
            FormatServ["FormattingService<br/>format_file (blindagens, opt-out)"]
            SyncServ["SyncService<br/>check_sync (cache TTL) — ainda ATIVO (desescopo f020)"]
            DecServ["DecisionService<br/>load / validate_integrity / compile_index"]
            Gate["decisions/gate ✨f022/f023<br/>evaluate_registration_gate · fingerprints fino/grosso"]
            CmdServ["CommandService<br/>resume / encerrar-sessao / handoff / clarificar"]
            DocServ["DocumentationService<br/>introspecção argparse + regras + state"]
            InstServ["InstallPromptService ✨f003<br/>render (composição de template)"]
            MigServ["core/migrate ✨f020<br/>MigrateService: shim+hooks+settings → remove core local"]
            SessSer["session/serializer ✨f004<br/>parse / render (round-trip)"]
            SessSink["session/sinks ✨f004<br/>HookContextSink / FileProjectionSink"]
            CloseFlow["session/close_flow ✨f018<br/>SessionCloseFlow: pré-check → fechamento → ofertas"]
            ResumeCtx["session/resume_context ✨f021<br/>build_decisions_appendix (pura)"]
            InstProf["install/harness_profiles ✨f003<br/>Claude/Gemini/Antigravity Profile · skills_dir() ✨f018"]
            AgyHooks["install/antigravity_hooks ✨f009<br/>materialize_hooks_json (merge por named-hook)"]
            SessSkills["install/session_skills ✨f018<br/>materialize_session_skills (substitui session_commands)"]
            ClaudeSettings["install/claude_settings ✨f020<br/>merge por-item dentro do array de cada evento"]
        end
    end

    subgraph adapters [Adaptadores src/adapters/]
        FsAdap["LocalFileSystemAdapter<br/>write_file_atomic (.tmp + os.replace) · remove_tree ✨f020"]
        GitAdap["SubprocessGitAdapter<br/>rev-parse / ls-remote / commit_paths"]
        FormatAdap["HostFormatterAdapter<br/>ruff / prettier / rustfmt"]
    end

    %% Drivers -> serviços
    CLI --> BootServ & FormatServ & DecServ & CmdServ & DocServ & InstServ & MigServ
    CLI --> CloseFlow
    CLI --> ResumeCtx
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
    CloseFlow --> CmdServ
    CloseFlow --> GitPort
    CloseFlow -->|3º portão ✨f022| Gate
    CLI -->|decisions --gate ✨f022| Gate
    AGY -->|advisory via gate_evaluator ✨f022| Gate
    Gate --> GitPort
    ResumeCtx --> FsPort
    CLI -->|resolve sink por active_harness| SessSink
    InstServ --> InstProf
    AgyHooks -->|hooks_block canônico| InstProf
    AgyHooks --> FsPort
    SessSkills --> InstProf
    SessSkills --> FsPort
    ClaudeSettings --> FsPort
    MigServ --> FsPort
    MigServ --> BootServ
    MigServ --> ClaudeSettings
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

- **`FileSystemPort`** — `read_file, write_file, write_file_atomic, exists, list_dir, makedirs, remove, is_dir` + **`remove_tree` (✨f020, novo — usado só por `MigrateService._safe_remove_core`, com guarda de nome-base)**.
- **`GitPort`** — `get_head_commit, get_remote_commit` + **`commit_paths` (✨f013), `list_dirty_paths` (✨f016, usado por `pending_work_paths`) e `list_changed_paths_since` (✨f022, `git diff --name-only <ref> HEAD` — o diff da âncora que alimenta o gate de registro)**.
- **`ProcessPort`** — `execute_formatter -> (exit, stdout, stderr)`, `run_command` (✨f007).

### Serviços de capacidade 🟢

- **BootstrapService** — grava `pre-commit`(→`format`) e `post-merge`(→`decisions`); **✨f020: deixou de reescrever incondicionalmente** — hook ausente cria, hook do harness (por assinatura) atualiza, hook alheio sem assinatura é preservado e encadeado.
- **FormattingService** — `format_file` **sempre retorna 0**; blindagem de `~`/`~/Notas`/`~/.claude`, opt-out por `.no-autoformat`, precedência de binário local, raiz por manifesto (`.git`/`harness.toml`). Consome `[formatting]` (`exclude_paths` com glob/`fnmatch`, `opt_out_file`) dinamicamente do `HarnessConfig` ✨f008 (T4 resolvido). Reusado pela ponte do Antigravity no `PostToolUse` ✨f009.
- **SyncService** — `check_sync` com cache TTL; resiliente (erro → `True`). Exposto **só via MCP** (não há subcomando `sync`). **Ainda ATIVO** apesar do plano da f020 prever sua remoção — sustenta a `UpgradeOffer` de `session/close_flow` (ver domain.md, nota de reconciliação).
- **DecisionService** — `load_decisions`, `validate_integrity` (auto-relação e aresta órfã), `compile_index` (backlinks por verbos inversos). Caminhos vêm por parâmetro ✨f005.
- **decisions/gate ✨f022/f023 (NOVO)** — `evaluate_registration_gate(git, repo_path, session, config) -> GateVerdict`: avaliação **pura** de pendência de registro de microdecisão (diff da âncora ∪ sujos, sem ficha `MD-*.md` tocada → pendente; fail-open barulhento). Duas identidades anti-loop: `compute_fingerprint` (fina, `sha1(âncora+HEAD+sujos)` — portão do encerramento, trabalho novo rearma) e `compute_lembrete_fingerprint` (grossa, `sha1(âncora)` ✨f023 — lembrete do Stop, máx. 1 por sessão). Consumido por três bordas com três políticas: `CloseFlow` (bloqueio + escape `--sem-decisao`), CLI `decisions --gate` (soft-block JSON no hook Stop do Claude) e `AntigravityHookBridge` (advisory em stderr via `gate_evaluator` injetado). Agnóstico ao harness (RN-N5).
- **CommandService** — slash commands agnósticos à IDE; âncora Git no `resume`; distingue ausente (`None`) de malformado (`MalformedSessionStateError`). Não conhece harness (RN-N5). **✨f018: consumido por `session/close_flow`**, que orquestra em volta dele (pré-check + ofertas), sem alterar seu contrato.
- **DocumentationService** — introspecção do argparse + regex sobre `domain.md` + `state.json` → injeta JSON no `template.html`.
- **InstallPromptService ✨f003** — `render(active_harness, parser)` por composição (4 placeholders no `template.md`); resolve perfil fail-fast.
- **core/migrate ✨f020 (NOVO)** — `MigrateService.migrate(root, dry_run, upstream_self)`: varre uma raiz por instalações no layout copiado; converte cada uma para a fonte única na ordem shim → hooks (`BootstrapService`) → settings (`ClaudeSettings`) → remoção de `version` → remoção da cópia do core **por último**, via `FileSystemPort.remove_tree` com guarda de nome-base. Exceção consciente ao footprint per-projeto (RN-N17): atua sobre outros projetos por design.
- **session/serializer ✨f004** — round-trip `parse(render(x)) == x`; 4 seções fixas mapeiam `SessionNarrative`.
- **session/sinks ✨f004** — `get_sink` por `active_harness`: `HookContextSink` (Claude/Gemini, `additionalContext`, trunca em 10000) ou `FileProjectionSink` (Antigravity). Família por `_FAMILY_BY_HARNESS`; desconhecido → `ValueError`.
- **session/close_flow ✨f018 (NOVO)** — `SessionCloseFlow.run(repo_path, config, ..., sem_decisao=False) -> int`: fonte única da orquestração de `encerrar-sessao`, consumida pela CLI e pelos scripts finos da skill. Sequência: pré-check de pendência (`pending_work_paths`, restrito ao `session_file` desde ✨f019) → gate de narrativa viva → **3º portão de registro de microdecisões (✨f022: marker `DECISAO_PENDENTE`, anti-loop por fingerprint fino, escape `--sem-decisao` com rastro na narrativa)** → `CommandService.execute_command("encerrar-sessao")` → ofertas de fim de sessão (push → upgrade, via `EndSessionOffersService`). I/O injetável (markers sem TTY, `[s/N]` com TTY).
- **session/resume_context ✨f021 (NOVO)** — `build_decisions_appendix(fs, index_file, enabled) -> str`: função pura que compõe o apêndice do índice de decisões anexado ao `cmd resume`; o gate (`active_harness == "claude" and inject_decisions_index`) é calculado na borda (`main.py`) e passado como parâmetro.
- **install/harness_profiles ✨f003** — Strategy (`ABC`) `ClaudeProfile`/`GeminiProfile`/`AntigravityProfile` com `hooks_block()` + `apply_instructions()`. ✨f009 `AntigravityProfile` deixou de ser placeholder: `hooks_block()` emite o named-hook `harness` em JSON válido (`PreToolUse`/`PostToolUse`/`Stop`, `<ABS>` literal até a materialização) e `apply_instructions()` aponta `.agents/hooks.json`; a nota de escopo por harness migrou do `template.md` para o `apply_instructions()` dos três perfis. **✨f018:** `session_command_artifact(command_path)` removido; adicionado `skills_dir() -> str | None` (`.claude/skills`, `.agents/skills`, `None` no Gemini).
- **install/antigravity_hooks ✨f009** — `materialize_hooks_json(fs, project_path, command_path)`: lê o `.agents/hooks.json` existente, substitui o named-hook `harness` pelo bloco canônico do `AntigravityProfile` (com `<ABS>` resolvido para o caminho absoluto) e grava por escrita atômica, preservando chaves de terceiros. Rotina única compartilhada por `init` e `upgrade`. Escreve só sob `project_path` via `FileSystemPort` (RN-N17, footprint zero).
- **install/session_skills ✨f018 (NOVO, substitui `install/session_commands`)** — `materialize_session_skills(fs, project_path, profiles)`: grava a árvore agnóstica da skill `encerrar-sessao` (`SKILL.md` + `scripts/`, mesmos bytes) sob `<skills_dir>/encerrar-sessao/` de cada perfil, incondicionalmente (Claude + Antigravity, sem gate por `active_harness`). Remove os órfãos legados (`stale_session_command_paths`) preservando terceiros.
- **install/claude_settings ✨f020 (NOVO)** — materializa `.claude/settings.json` com **merge por-item dentro do array de cada evento** (identifica o item do harness pela assinatura no `command`, substitui/insere, preserva os demais itens do mesmo evento) — corrige o bug anterior de substituição do array inteiro por evento. **✨MD-0014/f022:** gerencia só `SessionStart` e `Stop` (o `PostToolUse → harness format` foi aposentado; a assinatura `"harness format"` saiu do conjunto, itens legados ficam preservados como de terceiros); a assinatura `"harness decisions"` casa com e sem `--gate`, então instalações pré-022 são substituídas pelo item novo sem duplicar.

### Driver de borda do Antigravity ✨f009 🟢

- **AntigravityHookBridge** (`adapters/antigravity/hook_bridge.py`) — terceiro driver de entrada, simétrico à CLI e ao servidor MCP. `handle(event, stdin_text)` despacha por evento e devolve o stdout JSON exigido pelo contrato, **nunca levantando** (toda exceção é logada em `stderr` e o fallback do evento é emitido com exit 0; não-bloqueante, RN-03). `pre-tool-use` grava `stepIdx → TargetFile` num scratch sob `artifactDirectoryPath` e emite `{"decision": "allow"}`; `post-tool-use` resolve o caminho pelo `stepIdx` e delega a `FormattingService.format_file` (que honra opt-out/exclusões e retorna 0), emitindo `{}`; `stop` delega a `DecisionService` (`load_decisions` → `validate_integrity` → `compile_index`), emitindo `{}` sem `"continue"` — **✨f022:** após a reindexação, consulta o `gate_evaluator` injetado (callable montado na borda; `None` quando o gate não se aplica) e, havendo pendência, **avisa** em stderr (advisory, nunca bloqueia, RN-N26; falha do avaliador não descarta a reindexação). Recebe `fs`, os dois serviços, os caminhos de decisão e o `gate_evaluator` por injeção; a instanciação dos adaptadores concretos e a leitura de `load_config` ficam na borda (`main.py`, subcomando `agy-hook`). Core agnóstico ao harness preservado (RN-N5).

### Domínio 🟢

- **models.py** — `Decision`, `Relationship`, `SessionState`, `SessionNarrative` (Pydantic v2, com validadores de regex/enum). **✨f022:** `SessionState` ganhou os campos anti-loop opcionais `gate_lembrete_fingerprint`/`gate_encerramento_fingerprint`, zerados por `close_session`.
- **config.py** — `HarnessConfig` (`[harness]/[formatting]/[sync]/[decisions]/[session]`) e `load_config(fs)`. ✨ `[decisions]` é a chave da feature 005; ✨ `SessionSection` (`[session].state_file`, default `.harness/estado-da-sessao.md`) é a chave da feature 006, fonte única do caminho de sessão lida por CLI e MCP. **✨f022:** `DecisionsSection.require_registration` (default `True`) liga o gate de registro; **literal de versão em `2.1.1`**.
- **cache.py** — `SyncCache`.

### Adaptadores 🟢

- **LocalFileSystemAdapter** — I/O UTF-8; escrita atômica `.tmp` + `os.replace`.
- **SubprocessGitAdapter** — `git rev-parse HEAD`, `git ls-remote origin main`, `git status --porcelain`, `git diff --name-only <ref> HEAD` (✨f022); erro → `RuntimeError`.
- **HostFormatterAdapter** — mapeia formatador→args; binário ausente → `(127, …)`.

> ✅ **Bugs de driver corrigidos (memória histórica):** **T1** — `server.py` chamava `load_config` sem import (NameError na tool de decisões via MCP); **RESOLVIDO** em `cf73980` (import na linha 12). **T2** — `server.py` apontava a sessão para `ESTADO-DA-SESSAO.md` (raiz), divergindo da CLI; **RESOLVIDO** na feature 006: o caminho agora vem de `config.session.state_file` (`SessionSection`), lido igualmente por CLI (`main.py:169`) e MCP (`server.py:94`). **T3** — `main.py` usava `json.loads` sem `import json` (autoformat por hook silenciosamente não ocorria); **RESOLVIDO** em `cf73980` (import na linha 5).
