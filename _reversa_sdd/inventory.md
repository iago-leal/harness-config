# Inventário do Projeto — harness

> Gerado pelo Scout em 2026-06-24 (Re-extração após as features 003, 004, 005, 006, 007 e 009)
> Atualização cirúrgica em 2026-06-24 após a feature 007: adição do comando `init` e `upgrade` no wrapper de raiz, novos `tests/test_init.py` e `src/core/bootstrap/init_service.py`, caminhos de evolução/bootstrap em CLI e MCP.
> Re-extração após a feature 009-hooks-antigravity: terceiro driver de entrada `src/adapters/antigravity/hook_bridge.py` (`AntigravityHookBridge`), materializador `src/core/install/antigravity_hooks.py`, três novos testes `test_antigravity_*.py`, subcomando `agy-hook` na CLI e ganchos do Antigravity via `.agents/hooks.json`.
> **Re-extração estrutural ampla em 2026-07-05** (Scout, reconciliação pós-features 010-021 — este documento estava desatualizado desde a 009 nas seções abaixo): novos subcomandos `materialize` (012) e `migrate` (020); `src/core/session/close_flow.py` como fonte única do encerramento (018, reexportado por `main.py`); `src/core/session/resume_context.py` com `build_decisions_appendix` ancorando o `resume` no índice de decisões (021); `src/core/migrate/service.py` (020, converte instalações do layout copiado para a fonte única shim+upstream); a dependência direta de MCP mudou de `mcp` para **`fastmcp`** no manifesto. Contagem de testes subiu de 19 para **33 arquivos `test_*.py`** (+ `helpers.py`) e de código em `src/` de 41 para **56 arquivos**.
> **Re-extração incremental em 2026-07-15** (Scout, reconciliação pós-MD-0014 e features 022-023): novo módulo `src/core/decisions/gate.py` (022 — gate de registro obrigatório de microdecisões; 023 — dupla identidade do lembrete via `compute_lembrete_fingerprint`); novo teste `test_decision_gate.py`; o subcomando `decisions` ganhou a flag `--gate` (invocada pelo hook **Stop** do Claude); o gatilho **PostToolUse (format-on-edit) foi aposentado** no perfil Claude (MD-0014) — `.claude/settings.json` deste repo já não o contém. Contagens: `src/` 56 → **57** arquivos; testes 33 → **34 `test_*.py`** (+ `helpers.py`); fichas de decisão 12 → **16** (MD-0013..MD-0016); suíte em **300 testes** (relato da sessão da 023). Core em **2.1.1**.

Mapeamento da superfície de código e arquivos de configuração do diretório `/Users/iagoleal/dev/harness`.

---

## 📊 Estatísticas Gerais

- **Diretório Alvo:** `/Users/iagoleal/dev/harness`
- **Escopo da contagem:** código da aplicação (`.harness/harness-core/`, wrapper de raiz, configs e `.harness/`). Excluídos: `.venv`, `.git`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `tmp/`, os artefatos do próprio Reversa (`.reversa/`, `_reversa_sdd/`, `_reversa_forward/`) e as duas árvores-espelho de **templates de skills do Reversa** (`.claude/skills/` e `.agents/skills/`, ~430 arquivos de framework, não de produto).
- **Linguagens Principais (aplicação):**
  - **Python (`.py`)**: **92 arquivos** — **57** em `.harness/harness-core/src/` e **35** em `.harness/harness-core/tests/` (34 `test_*.py` + `helpers.py`). Acréscimo desde a 021: `src/core/decisions/gate.py` e `tests/test_decision_gate.py` (022/023). Acréscimo desde a 009: `src/core/migrate/{__init__,service}.py` (020), `src/core/session/{close_flow,resume_context}.py` (018/021), e os testes correspondentes `test_migrate.py`, `test_close_flow.py`, `test_resume_context.py`, `test_session_sinks.py`, `test_session_skills.py`, `test_skill_scripts.py`, `test_shim.py`, `test_local_apply.py`, `test_git_dirty.py`, `test_gitignore_entry.py`, `test_regen.py`, `test_offers.py`, `test_wrapper.py`, `test_footprint.py`, `test_harness_profiles.py`, `test_install_claude_settings.py` (o crescimento reflete as features 010-021, não só uma).
  - **Markdown (`.md`)**: ~22 arquivos no escopo de aplicação — instruções de agente (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`), as **16 fichas de decisão** em `.harness/decisoes/` (`MD-0001`..`MD-0016`, cresceu de 12 para 16: MD-0013 caminho do cache de sync em `layout.py`, MD-0014 aposentadoria do PostToolUse, MD-0015 gate de registro, MD-0016 identidade grossa do lembrete) mais o `_cabecalho.md`, o índice `.harness/microdecisoes.md`, o estado de sessão (`.harness/estado-da-sessao.md`) e o brief solto na raiz `BRIEF-oferta-commit-pendente-ao-encerrar.md` (registro de intenção pré-feature, não normativo).
  - **HTML (`.html`)**: 2 arquivos — `.harness/harness-core/src/core/documentation/template.html` e o consolidado `harness-docs.html` na raiz.
  - **Shell (`harness`)**: 1 wrapper Bash executável na raiz. Semântica do wrapper inalterada (resolve `.venv` local e delega a `main.py`); o que mudou é o que `init`/`migrate` colocam nesse destino (fonte única — feature 020).
  - **TOML (`.toml`)**: 1 arquivo (`.harness/harness-core/harness.toml`), agora com seção `[session]` (`inject_decisions_index`, feature 021) além de `[harness]`/`[sync]`/`[decisions]`.
  - **JSON (`.json`)**: `.claude/settings.json` e `.gemini/settings.json` no repositório do harness em si; `.agents/hooks.json` **não está presente aqui** (é materializado apenas em projetos-alvo pelo `init`/`upgrade`, o harness upstream não roda o Antigravity sobre si mesmo neste repo).

> ⚠️ **Mudança estrutural vs extração anterior (009 → 021):** o módulo legado `claude-config/` foi purgado anteriormente; a feature 011 (posterior a esta extração original) relocou o core de `harness-core/` para `.harness/harness-core/` — os caminhos deste documento já refletiam essa relocação, mas `surface.json` estava desatualizado (corrigido nesta re-extração). A feature 018 extraiu a orquestração de encerramento de sessão para `core/session/close_flow.py`, fonte única reexportada por `main.py` e pelos scripts finos da skill `encerrar-sessao`. A feature 020 introduziu o subcomando `migrate` e mudou a semântica de `init`: deixou de copiar o core para o destino e passou a materializar um **shim** que executa o core do upstream (fonte única, `RN-08`/`RN-N15` do domain.md). A feature 021 acrescentou `resume_context.build_decisions_appendix`, que ancora o `cmd resume` no índice de microdecisões quando o harness ativo é o Claude. Em nenhum desses pontos o `core/` passou a depender de um adaptador concreto — a inversão de dependência hexagonal permanece intacta.

---

## 📂 Estrutura de Diretórios e Arquivos

### ⚡ Raiz do Projeto

- **`harness`** 🟢 — Wrapper Bash executável. Resolve a venv local (`.harness/harness-core/.venv/bin/python3`) e encaminha todos os argumentos para `.harness/harness-core/src/main.py`.
- **`harness-docs.html`** 🟢 — HTML standalone gerado por `doc-gen`, consolidando a superfície da CLI, o domínio (`_reversa_sdd/domain.md`) e o estado do Reversa.
- **`CLAUDE.md` / `GEMINI.md` / `AGENTS.md`** 🟢 — Instruções de ativação do framework Reversa por harness, agora contendo a instrução de uso dos comandos `./harness init` e `./harness upgrade`.

### 📦 Núcleo Python (`.harness/harness-core/`) — arquitetura hexagonal

- **`src/main.py`** 🟢 — Entrada da CLI. **12 subcomandos**: `bootstrap`, `format`, `decisions`, `cmd`, `doc-gen`, `doc-serve`, `install-prompt`, `init`, `upgrade`, `agy-hook <evento>` (009), e os **dois novos desde a última extração estrutural**: `materialize` (012, interno — rematerializa slash commands/skills e `hooks.json` com o código local; o `upgrade` o invoca via subprocesso do Python de destino para nunca rematerializar com módulos antigos em memória) e `migrate <root> [--dry-run]` (020, converte instalações no layout copiado — core vendored no destino — para a fonte única: shim `./harness` + `.venv` locais que executam o core do upstream). `init` mudou de semântica na 020: **não copia mais o core**, materializa um shim (fonte única, `RN-08`). `config = load_config(fs)` e o aviso passivo de nova versão seguem pulados para `{init, upgrade, agy-hook, materialize, migrate}`.
- **`src/core/`** — Regras de negócio (domínio puro), uma pasta por capacidade:
  - **`bootstrap/`** 🟢 — instalação de ganchos Git locais e `init_service.py` (007, orquestra a cópia do core/wrapper/venv/ganchos no destino — pré-020; a 020 introduziu o caminho alternativo de shim, ver `core/migrate`).
  - **`formatting/`** 🟢 — formatação de arquivo por linguagem.
  - **`sync/`** 🟢 — **mantido pela feature 020** (não removido, ao contrário do que a nota de fechamento de sessão anterior sugeria como possível): `SyncService` segue fazendo a checagem passiva de versão local vs. upstream no boot da CLI. A 020 mudou a _fonte_ do core (shim vs. cópia), não este mecanismo de aviso.
  - **`decisions/`** 🟢 — carga, validação de integridade do grafo e compilação do índice de microdecisões (`.harness/microdecisoes.md`), agora também consumido por `session/resume_context.py` (021). **Novo módulo `gate.py` (022/023)**: `GateVerdict`, `compute_fingerprint` (identidade fina — âncora+HEAD+sujos, usada pelo 3º portão do `encerrar-sessao`) e `compute_lembrete_fingerprint` (identidade grossa — só a âncora, usada pelo lembrete do hook Stop; garante no máximo 1 soft-block por sessão).
  - **`commands/`** 🟢 — execução de slash commands de sessão (`resume`, `encerrar-sessao`, `handoff`, `clarificar`).
  - **`documentation/`** 🟢 — geração do HTML (`service.py` + `template.html`).
  - **`install/`** 🟢 — render do prompt colável por composição. `harness_profiles.py` (Strategy por harness: `ClaudeProfile`, `GeminiProfile`, `AntigravityProfile`) e `antigravity_hooks.py` (009, `materialize_hooks_json` — escrita única com merge por named-hook `harness`, compartilhada por `init`/`upgrade`/`materialize`).
  - **`session/`** 🟢 — estado de sessão unificado, com **dois módulos novos desde a 009**: `close_flow.py` (018 — fonte única da orquestração de encerramento: `render_offer_markers`, `conduct_end_session_offers`, `pending_work_paths`, `render_commit_pendente_marker`, `conduct_commit_pendente`, `SessionCloseFlow`; reexportado por `main.py` para a CLI e pelos scripts finos da skill `encerrar-sessao`, sem duplicação) e `resume_context.py` (021 — `build_decisions_appendix`, função pura que monta o apêndice do índice de decisões anexado ao `cmd resume`; fiado em `main.py` só quando `active_harness == "claude"` e `SessionSection.inject_decisions_index` — default `True` — está ligado; não-bloqueante: índice ausente vira aviso em `stderr`, exit 0).
  - **`domain/`** 🟢 — modelos Pydantic, cache e configuração tipada (`HarnessConfig`, com `upstream_path`/`version` em `[harness]` e o **novo campo `SessionSection.inject_decisions_index`**, feature 021, default `True`, retrocompatível).
  - **`migrate/`** 🟢 **(NOVO — feature 020)** — `service.py` do subcomando `migrate`: varre uma raiz (padrão `~/dev`) por instalações no layout copiado e as converte para a fonte única, com modo `--dry-run` que só relata espaço a liberar e ações, sem escrever/remover nada.
  - **`ports/`** 🟢 — interfaces (`ABC`, `abstractmethod`) `fs.py` (`is_dir`, `remove_tree` ✨f020), `git.py` (`commit_paths` ✨f013, `list_dirty_paths` ✨f016) e `process.py` (`run_command`).
- **`src/adapters/`** 🟢 — Infraestrutura física: `fs/local.py`, `git/subprocess.py`, `process/formatter.py`, `mcp/server.py` (servidor FastMCP expondo `format_file`, `check_repository_sync`, `process_decisions`, `session_command`) e `antigravity/hook_bridge.py` (009, `AntigravityHookBridge` — terceiro driver de entrada, protocolo de ganchos do Antigravity via stdin/stdout JSON, sempre não-bloqueante). Nenhum adaptador novo desde a 009; o crescimento do período 010-021 concentrou-se em `core/` e `cli/`.
- **`tests/`** 🟢 — **33 arquivos `test_*.py` + `helpers.py`** (suíte verde — 256 testes por relato da sessão que fechou a feature 021, não recontado individualmente nesta re-extração estrutural). Novos desde a 009: `test_migrate.py` (020), `test_close_flow.py` (018), `test_resume_context.py` (021), `test_session_sinks.py`, `test_session_skills.py`, `test_skill_scripts.py` (materialização de skills — 018), `test_shim.py`, `test_local_apply.py`, `test_git_dirty.py`, `test_gitignore_entry.py` (smoke real de git — 019), `test_regen.py`, `test_offers.py` (014/016), `test_wrapper.py`, `test_footprint.py`, `test_harness_profiles.py`, `test_install_claude_settings.py`.
- **`harness.toml`** 🟢 — Configuração tipada; seções `[harness]`, `[formatting]`, `[sync]`, `[decisions]` e **`[session]`** (`state_file`, e o novo `inject_decisions_index` da 021).
- **`requirements.txt`** 🟢 — dependência direta de MCP é **`fastmcp`** (não mais listada como `mcp` puro — ver `dependencies.md`).

### 🗂️ Estado e Decisões versionados (`.harness/`)

- **`.harness/estado-da-sessao.md`** 🟢 — Estado de sessão unificado.
- **`.harness/decisoes/MD-0001..MD-0012.md`** 🟢 — **Cresceu de 5 para 12 fichas** de microdecisão desde a extração anterior (cobrindo, entre outras, a purga do legado, a reinjeção multi-harness, a remoção da sincronização cross-harness, o footprint per-projeto, o bootstrap git-aware e o núcleo de `encerrar-sessao` sob fonte única).
- **`.harness/microdecisoes.md`** 🟢 — Índice DERIVADO pelo `./harness decisions`; agora também **lido em runtime** por `resume_context.build_decisions_appendix` (021) para ancorar o `cmd resume` no Claude.

### ⚙️ Configuração de ganchos por harness

- **`.claude/settings.json`** 🟢 — Hooks Claude Code. **Mudou no período 022-023:** o gatilho `PostToolUse` (format-on-edit) foi **aposentado** (MD-0014) e o evento **`Stop`** passou a invocar `harness decisions --gate` (lembrete/soft-block do gate de microdecisões, 022). Permanece o `SessionStart` (`cmd resume`).
- **`.gemini/settings.json`** 🟢 — Hook Gemini.
- **`.agents/hooks.json`** — Ganchos do Antigravity (009); **não presente neste repositório** (é materializado apenas em projetos-alvo pelo `init`/`upgrade`/`materialize`, via `materialize_hooks_json`). O harness upstream não se auto-instrumenta com hooks do Antigravity.

### 🔄 Features Forward (`_reversa_forward/`)

- `001-run-harness-core-local/` — execução local do core.
- `002-documentacao-uso-html/` — gerador de documentação HTML.
- `003-instalacao-por-prompt/` — comando `install-prompt`.
- `004-estado-sessao-unificado/` — estado de sessão em `.harness/` com reinjeção.
- `005-decisoes-em-harness/` — migração de decisões e desacoplamento de caminhos.
- `006-harness-core-config-canonica/` — harness-core como módulo per-projeto (footprint zero).
- `007-bootstrap-harness-init/` — comando `init` e `upgrade` para bootstrap local de novos workspaces.
- `009-hooks-antigravity/` — ganchos de ciclo de vida para o Antigravity: terceiro driver de entrada `AntigravityHookBridge`, subcomando `agy-hook`, `AntigravityProfile` real e materialização de `.agents/hooks.json` por `init`/`upgrade`.
- `010-command-encerrar-sessao/` — primeira versão do comando/skill `encerrar-sessao`.
- `011-harness-core-em-dot-harness/` — relocação do core de `harness-core/` para `.harness/harness-core/`.
- `012-corrige-upgrade-stale/` — subcomando `materialize` interno; rematerialização via subprocesso do código novo (corrige `upgrade` regravando artefatos com código antigo em memória).
- `013-commit-encerrar-sessao/` — commit de registro do fechamento ao final de `encerrar-sessao`.
- `014-oferta-upgrade-ao-encerrar/` — oferta de `upgrade` embutida no fluxo de encerramento.
- `015-corrige-encerrar-sessao-noop/` — correção de um caso no-op do `encerrar-sessao`.
- `016-encerrar-sessao-autonomo/` — `encerrar-sessao` autônomo (menos prompts intermediários).
- `017-caminho-workflow-antigravity/` — tentativa de caminho via workflow para o Antigravity, depois substituída pela ativação por skill (018).
- `018-encerrar-sessao-como-skill/` 🟢 — `encerrar-sessao` versionado como skill (não mais command/workflow); `SessionCloseFlow` extraído para `core/session/close_flow.py`, fonte única entre CLI e skill; materialização de skills nos dois harnesses.
- `019-oferta-commit-cobre-harness/` 🟢 — oferta de commit do `encerrar-sessao` passa a cobrir também mudanças dentro de `.harness/`; smoke test com git real (não mockado) expôs que o porcelain colapsa subdiretório untracked.
- `020-fonte-unica-e-hooks/` 🟢 — `init` deixa de copiar o core; passa a materializar um shim que executa o core do upstream (fonte única); novo subcomando `migrate` para converter instalações antigas (layout copiado → shim).
- `021-hook-busca-ancorada/` 🟢 — `cmd resume` no Claude passa a anexar o índice `.harness/microdecisoes.md` ao contexto reinjetado, ancorando a busca do agente antes de varreduras amplas; `resume_context.build_decisions_appendix` (novo, agnóstico ao harness) e campo `SessionSection.inject_decisions_index` (default `True`).
- `022-hook-registro-decisoes/` 🟢 — gate de registro obrigatório de microdecisões: novo `core/decisions/gate.py` (fingerprint do trabalho da sessão), 3º portão no `close_flow.py` (garantia dura no `encerrar-sessao`, escape `--sem-decisao`), ramo `decisions --gate` no `main.py` invocado pelo hook **Stop** do Claude (soft-block de lembrete), fingerprint persistido no estado de sessão (MD-0015).
- `023-granularidade-lembrete-gate/` 🟢 **(NOVO — mais recente)** — dupla identidade anti-loop do gate: o lembrete do Stop passa a usar identidade **grossa** (`compute_lembrete_fingerprint`, `sha1(âncora)` → no máximo 1 soft-block por sessão), enquanto o 3º portão mantém a identidade **fina** (`sha1(âncora+HEAD+sujos)`, pinada por teste-guarda); novo campo `GateVerdict.fingerprint_lembrete` (MD-0016). Transição autoresolvente, sem schema novo nem flag.

---

## 🩺 Achados de saúde (para os agentes seguintes)

- 🟢 **Suíte de testes estendida e estável:** A inclusão do `test_init.py` garante a resiliência física do fluxo de cópia recursiva e do processo de atualização evolucionária sem destruir as decisões locais de engenharia reversa.
- 🟢 **Detecção de versão não bloqueante:** O mecanismo passivo de leitura comparativa de versões em relação ao upstream opera de forma eficiente, sem penalizar o tempo de boot da CLI e do servidor MCP.
- 🟢 **Footprint zero preservado:** A criação da venv local e injeção do core nos caminhos de destino obedece às restrições de localidade per-projeto (BR-MIGRAR-007). A feature 009 mantém a restrição: `materialize_hooks_json` escreve apenas `.agents/hooks.json` dentro do projeto-alvo, via `FileSystemPort`, nunca em diretório global do usuário.
- 🟢 **Core agnóstico ao harness reforçado (RN-N5):** confirmado por leitura — a lógica do Antigravity vive no adaptador, no perfil e no materializador; nenhum serviço de domínio foi ramificado por harness, e o `agy-hook` reusa `FormattingService`/`DecisionService` intactos.
- 🟢 **Suíte em 300 testes** (relato da sessão de fechamento da 023: 293 → 300 com os 7 testes do TDD da granularidade do lembrete; não recontada individualmente por este Scout). O crescimento 256 → 300 reflete as features 022-023 e o saneamento intermediário, acumulação orgânica.
- 🟢 **Fonte única consolidada (020) sem quebrar o footprint per-projeto:** `init`/`migrate` passaram a materializar shim + core do upstream em vez de copiar; a restrição de nunca escrever fora do projeto-alvo (BR-MIGRAR-007) permanece — o `migrate` só varre e reescreve dentro da raiz que o usuário informa, e tem `--dry-run` para inspeção sem efeito.
- 🟢 **Fechamento de sessão sem duplicação de lógica (018):** `close_flow.py` no core é a única fonte da orquestração de encerramento; a CLI e a skill compartilham os mesmos helpers, evitando o padrão de "duas implementações que divergem com o tempo".
- 🟡 **Achado pré-existente ainda não corrigido (herdado da sessão da 021):** `cmd resume` em um repositório sem nenhum commit ainda estoura um traceback cru de `git rev-parse HEAD` — viola a regra de não vazar exceções não tratadas para o usuário final (RN-N4 do domain.md). Não verificado por este Scout (é achado de comportamento, fora do escopo de mapeamento estrutural); ver `regression-watch.md` da feature 020 e a reconciliação do Detective para status atualizado.
- 🟡 **Dívida tolerada, não regressão:** `ruff` não está instalado na venv local (o CI roda só `pytest`, não lint) — cosmético, registrado como dívida conhecida e aceita, não achado novo desta re-extração.
