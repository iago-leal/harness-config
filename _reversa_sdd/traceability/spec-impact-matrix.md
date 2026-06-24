# Matriz de Impacto de Especificações (Spec Impact Matrix) — harness-core

> Regenerado pelo Architect em 2026-06-24 (Re-extração após as features 003, 004 e 005)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO

Correlaciona os componentes lógicos e adaptadores do `harness-core` com as regras de domínio (RN), as features do ciclo forward, os ADRs/microdecisões e os bugs latentes que tocam cada componente. Severidade = impacto de uma mudança nesse componente sobre o sistema.

---

## 📊 1. Matriz por Componente

| Componente | Arquivo | Regras de Domínio | Feature(s) | ADR / MD | Bugs | Severidade |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BootstrapService** | `core/bootstrap/service.py` | RN-N15 | 001 | 0009 | — | MEDIUM |
| **FormattingService** | `core/formatting/service.py` | RN-03, RN-04, RN-05, RN-06, RN-N7 | 002 | 0002 | T3, T4 | **HIGH** |
| **SyncService** | `core/sync/service.py` | RN-01, RN-02 | — (só MCP) | 0003 | — | **HIGH** |
| **DecisionService** | `core/decisions/service.py` | RN-N11, RN-N12, RN-N13, RN-N14 | **005** | 0001, 0012 / MD-0004 | T1 | **HIGH** |
| **CommandService** | `core/commands/service.py` | RN-07, RN-N1, RN-N3, RN-N4, RN-N5 | **004** | 0004, 0010 / MD-0002 | T2 | **HIGH** |
| **DocumentationService** | `core/documentation/service.py` | RN-08, RN-09, RN-10 | 002 | 0008 | — | MEDIUM |
| **InstallPromptService** ✨ | `core/install/service.py` | RN-N9, RN-N10 | **003** | 0011 / MD-0003 | — | MEDIUM |
| **HarnessProfile (Strategy)** ✨ | `core/install/harness_profiles.py` | RN-N10 | **003** | 0011 / MD-0003 | — | MEDIUM |
| **session/serializer** ✨ | `core/session/serializer.py` | RN-N1, RN-N2, RN-N4 | **004** | 0010 / MD-0002 | — | **HIGH** |
| **session/sinks** ✨ | `core/session/sinks.py` | RN-N5, RN-N6, RN-N8 | **004** | 0011 / MD-0003 | — | **HIGH** |
| **domain/config (`load_config`)** | `core/domain/config.py` | RN-N11 | **005** | 0012 / MD-0004 | T1 (no driver) | **HIGH** |
| **domain/models** | `core/domain/models.py` | RN-N13, RN-N14, RN-N1..N4 | 004, 005 | 0001, 0010 | — | **HIGH** |
| **LocalFileSystemAdapter** | `adapters/fs/local.py` | (atomicidade transversal) | — | 0006 | — | **HIGH** |
| **SubprocessGitAdapter** | `adapters/git/subprocess.py` | RN-01, RN-02, RN-07 | — | 0006 | — | MEDIUM |
| **HostFormatterAdapter** | `adapters/process/formatter.py` | RN-03, RN-05 | 002 | 0006 | — | MEDIUM |
| **CLI driver (`main.py`)** | `src/main.py` | RN-08, RN-N9, RN-N11; orquestra sinks | 001..005 | 0007 | **T3**, T5 | **HIGH** |
| **MCP driver (`server.py`)** | `adapters/mcp/server.py` | RN-01, RN-N11; expõe 4 tools | — | 0006 | **T1**, **T2** | **HIGH** |

> Componentes ✨ são **novos** nesta re-extração (features 003/004). `SyncService` e o MCP driver não têm feature forward dedicada — `sync` é exposto **apenas** via MCP (não há subcomando CLI).

---

## 🧩 2. Cobertura por Feature (003 / 004 / 005)

### Feature 003 — Instalação por Prompt 🟢
* **Componentes:** `InstallPromptService` (orquestra), `HarnessProfile` + `ClaudeProfile`/`GeminiProfile`/`AntigravityProfile` (Strategy), `template.md`; reusa a introspecção do argparse do `DocumentationService`.
* **Regras:** RN-N9 (geração por composição, fonte única), RN-N10 (resolução de perfil fail-fast).
* **Driver:** exposto **apenas pela CLI** (`install-prompt`), não pelo MCP.
* **Rastreabilidade:** ADR 0011 / MD-0003. **Sem bug latente.**

### Feature 004 — Estado de Sessão Unificado 🟢
* **Componentes:** `session/serializer` (round-trip), `session/sinks` (`HookContextSink`/`FileProjectionSink`), `session/errors` (`MalformedSessionStateError`), `CommandService` (consumidor), `SessionState`/`SessionNarrative` (domínio).
* **Regras:** RN-07, RN-N1 (fonte canônica única em `.harness/`), RN-N2 (round-trip), RN-N3 (narrativa preservada), RN-N4 (ausente ≠ malformado), RN-N5 (core não conhece harness), RN-N6 (reinjeção por família), RN-N8 (teto 10000 chars).
* **Driver:** CLI (`cmd resume`/`encerrar-sessao`, hook `SessionStart`) **e** MCP (`session_command`).
* **Rastreabilidade:** ADR 0010 (supera parcialmente 0004) e 0011 / MD-0002, MD-0003.
* **Bug latente:** **T2** — o MCP aponta para `ESTADO-DA-SESSAO.md` (raiz), divergente da CLI. Estado CLI×MCP não converge.

### Feature 005 — Decisões em `.harness/` 🟢
* **Componentes:** `domain/config` (`DecisionsSection` + `load_config`), `DecisionService` (recebe caminhos por parâmetro), os dois drivers (`main.py`, `server.py`) que derivam os caminhos de `load_config().decisions`.
* **Regras:** RN-N11 (caminhos desacoplados via config — watch item W001), RN-N12 (índice derivado), RN-N13 (integridade do grafo), RN-N14 (front-matter obrigatório).
* **Driver:** CLI (`decisions`, hook `Stop`) **e** MCP (`process_decisions`).
* **Rastreabilidade:** ADR 0012 (supera parcialmente 0001) / MD-0004; também ADR 0009 (purge de `claude-config/`, centralização em `.harness/`) / MD-0001.
* **Bug latente:** **T1** — via MCP, `load_config` quebra por import ausente; o caminho configurável **só é exercido pela CLI**.

---

## 🛠️ 3. Detalhamento de Impacto Crítico

1. **`session/serializer` + `session/sinks` (HIGH):** o coração da feature 004. Quebra no serializer corrompe a memória de retomada entre boots; quebra no sink impede a reinjeção de contexto. A invariante de round-trip (RN-N2) é a salvaguarda — qualquer mudança exige `test_session.py` e `test_session_sinks.py` verdes.
2. **`DecisionService` + `domain/config` (HIGH):** sustentam o grafo de decisões e o desacoplamento de caminhos (feature 005). Mudança aqui afeta a integridade do índice derivado e o watch item W001. **T1** já neutraliza esse caminho via MCP.
3. **`CommandService` (HIGH):** corrupção do `.harness/estado-da-sessao.md` invalida a retomada do ciclo forward; a âncora Git (RN-07) é o detector de divergência. **T2** introduz um estado paralelo via MCP.
4. **`FormattingService` (HIGH):** uma exceção não-blindada travaria a gravação de arquivos do agente (viola RN-03). **T3** já impede o autoformat por hook (caminho real do Claude) silenciosamente; **T4** torna `[formatting]` inerte.
5. **MCP driver `server.py` (HIGH):** concentra **T1 e T2** — as duas tools de decisões e de sessão estão degradadas. A CLI permanece o caminho confiável.

> Todos os bugs (T1–T6) são **documentados como contexto, não corrigidos** nesta extração.
