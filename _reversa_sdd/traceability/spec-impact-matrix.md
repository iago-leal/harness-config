# Matriz de Impacto de Especificações (Spec Impact Matrix) — harness-core

> Regenerado pelo Architect em 2026-06-24 (Re-extração após as features 003, 004 e 005)
> Atualização cirúrgica em 2026-06-24 após a feature 006 (commit `e894c59`): `SessionSection`/`[session]`, caminho de sessão por configuração, via única de config (T5 fechado) e contrato de footprint; reflete também a resolução de T1/T3 no commit `cf73980`.
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO

Correlaciona os componentes lógicos e adaptadores do `harness-core` com as regras de domínio (RN), as features do ciclo forward, os ADRs/microdecisões e os bugs latentes que tocam cada componente. Severidade = impacto de uma mudança nesse componente sobre o sistema.

---

## 📊 1. Matriz por Componente

| Componente                          | Arquivo                            | Regras de Domínio                     | Feature(s)   | ADR / MD                      | Bugs                              | Severidade |
| :---------------------------------- | :--------------------------------- | :------------------------------------ | :----------- | :---------------------------- | :-------------------------------- | :--------- |
| **BootstrapService**                | `core/bootstrap/service.py`        | RN-N15                                | 001          | 0009                          | —                                 | MEDIUM     |
| **FormattingService**               | `core/formatting/service.py`       | RN-03, RN-04, RN-05, RN-06, RN-N7     | 002          | 0002                          | T3, T4                            | **HIGH**   |
| **SyncService**                     | `core/sync/service.py`             | RN-01, RN-02                          | — (só MCP)   | 0003                          | —                                 | **HIGH**   |
| **DecisionService**                 | `core/decisions/service.py`        | RN-N11, RN-N12, RN-N13, RN-N14        | **005**      | 0001, 0012 / MD-0004, MD-0005 | T1 (resolvido `cf73980`)          | **HIGH**   |
| **CommandService**                  | `core/commands/service.py`         | RN-07, RN-N1, RN-N3, RN-N4, RN-N5     | **004**, 006 | 0004, 0010 / MD-0002, MD-0005 | T2 (resolvido via config, f006)   | **HIGH**   |
| **DocumentationService**            | `core/documentation/service.py`    | RN-08, RN-09, RN-10                   | 002          | 0008                          | —                                 | MEDIUM     |
| **InstallPromptService** ✨         | `core/install/service.py`          | RN-N9, RN-N10                         | **003**      | 0011 / MD-0003                | —                                 | MEDIUM     |
| **HarnessProfile (Strategy)** ✨    | `core/install/harness_profiles.py` | RN-N10                                | **003**      | 0011 / MD-0003                | —                                 | MEDIUM     |
| **session/serializer** ✨           | `core/session/serializer.py`       | RN-N1, RN-N2, RN-N4                   | **004**      | 0010 / MD-0002                | —                                 | **HIGH**   |
| **session/sinks** ✨                | `core/session/sinks.py`            | RN-N5, RN-N6, RN-N8                   | **004**      | 0011 / MD-0003                | —                                 | **HIGH**   |
| **domain/config (`load_config`)**   | `core/domain/config.py`            | RN-N11                                | **005**, 006 | 0012, 0013 / MD-0004, MD-0005 | T1 resolvido; T5 fechado (f006)   | **HIGH**   |
| **SessionSection (`[session]`)** ✨ | `core/domain/config.py`            | RN-N1 (caminho de sessão por config)  | **006**      | 0013 / MD-0005                | — (fecha T2)                      | **HIGH**   |
| **domain/models**                   | `core/domain/models.py`            | RN-N13, RN-N14, RN-N1..N4             | 004, 005     | 0001, 0010                    | —                                 | **HIGH**   |
| **LocalFileSystemAdapter**          | `adapters/fs/local.py`             | (atomicidade transversal)             | —            | 0006                          | —                                 | **HIGH**   |
| **SubprocessGitAdapter**            | `adapters/git/subprocess.py`       | RN-01, RN-02, RN-07                   | —            | 0006                          | —                                 | MEDIUM     |
| **HostFormatterAdapter**            | `adapters/process/formatter.py`    | RN-03, RN-05                          | 002          | 0006                          | —                                 | MEDIUM     |
| **CLI driver (`main.py`)**          | `src/main.py`                      | RN-08, RN-N9, RN-N11; orquestra sinks | 001..006     | 0007, 0013                    | T3 e T5 fechados (cf73980/f006)   | **HIGH**   |
| **MCP driver (`server.py`)**        | `adapters/mcp/server.py`           | RN-01, RN-N11; expõe 4 tools          | 006          | 0006, 0013                    | T1 e T2 resolvidos (cf73980/f006) | **HIGH**   |

> Componentes ✨ são **novos** nesta re-extração (features 003/004/006). `SyncService` não tem feature forward dedicada — `sync` é exposto **apenas** via MCP (não há subcomando CLI). O MCP driver, antes sem feature própria, passa a ser tocado pela feature 006 (caminho de sessão por configuração).

---

## 🧩 2. Cobertura por Feature (003 / 004 / 005 / 006)

### Feature 003 — Instalação por Prompt 🟢

- **Componentes:** `InstallPromptService` (orquestra), `HarnessProfile` + `ClaudeProfile`/`GeminiProfile`/`AntigravityProfile` (Strategy), `template.md`; reusa a introspecção do argparse do `DocumentationService`.
- **Regras:** RN-N9 (geração por composição, fonte única), RN-N10 (resolução de perfil fail-fast).
- **Driver:** exposto **apenas pela CLI** (`install-prompt`), não pelo MCP.
- **Rastreabilidade:** ADR 0011 / MD-0003. **Sem bug latente.**

### Feature 004 — Estado de Sessão Unificado 🟢

- **Componentes:** `session/serializer` (round-trip), `session/sinks` (`HookContextSink`/`FileProjectionSink`), `session/errors` (`MalformedSessionStateError`), `CommandService` (consumidor), `SessionState`/`SessionNarrative` (domínio).
- **Regras:** RN-07, RN-N1 (fonte canônica única em `.harness/`), RN-N2 (round-trip), RN-N3 (narrativa preservada), RN-N4 (ausente ≠ malformado), RN-N5 (core não conhece harness), RN-N6 (reinjeção por família), RN-N8 (teto 10000 chars).
- **Driver:** CLI (`cmd resume`/`encerrar-sessao`, hook `SessionStart`) **e** MCP (`session_command`).
- **Rastreabilidade:** ADR 0010 (supera parcialmente 0004) e 0011 / MD-0002, MD-0003.
- **Bug T2 — RESOLVIDO (feature 006):** o MCP apontava para `ESTADO-DA-SESSAO.md` (raiz), divergente da CLI. Desde a feature 006, ambos os drivers leem `session_file` de `config.session.state_file`; não há mais literal de caminho chumbado nem divergência CLI×MCP.

### Feature 005 — Decisões em `.harness/` 🟢

- **Componentes:** `domain/config` (`DecisionsSection` + `load_config`), `DecisionService` (recebe caminhos por parâmetro), os dois drivers (`main.py`, `server.py`) que derivam os caminhos de `load_config().decisions`.
- **Regras:** RN-N11 (caminhos desacoplados via config — watch item W001), RN-N12 (índice derivado), RN-N13 (integridade do grafo), RN-N14 (front-matter obrigatório).
- **Driver:** CLI (`decisions`, hook `Stop`) **e** MCP (`process_decisions`).
- **Rastreabilidade:** ADR 0012 (supera parcialmente 0001) / MD-0004; também ADR 0009 (purge de `claude-config/`, centralização em `.harness/`) / MD-0001.
- **Bug T1 — RESOLVIDO (commit `cf73980`):** via MCP, `load_config` quebrava por import ausente. `server.py` agora importa `from src.core.domain.config import load_config`; `process_decisions` e `session_command` exercem o caminho configurável também via MCP. Não há mais `NameError`.

### Feature 006 — Módulo per-projeto / footprint global zero 🟢

- **Componentes:** `SessionSection` em `domain/config` (caminho de sessão por configuração), `harness.toml` `[session]`, os dois drivers (`main.py`, `server.py`) que leem `config.session.state_file`, o contrato de footprint (`tests/test_footprint.py` + `tests/helpers.py` com `RecordingFileSystem`). Via única de configuração tipada: `load_harness_config`/`import toml` removidos de `main.py` (T5 fechado); `cmd` lê `config.harness.active_harness`.
- **Regras:** RN-N1 (fonte canônica única de sessão, agora por config), BR-MIGRAR-007 (zona protegida `~/.claude`/`~/.agent-memory`, fixada por teste).
- **Driver:** CLI **e** MCP — ambos derivam o caminho de sessão de `config.session.state_file`.
- **Rastreabilidade:** ADR 0013 / MD-0005 (refina MD-0004; reverte a premissa de "config canônica global", afirma o módulo per-projeto autocontido com footprint global zero; NÃO substitui `~/.claude`). A aposentadoria do sync cross-harness (MD-0004) permanece válida.
- **Bugs:** fecha T2 (config) e T5 (via única); herda a resolução de T1/T3 do commit `cf73980`. **Sem bug latente.** Confiança 🟡 só quanto à cobertura do contrato de footprint (cobre os serviços exercitados; é teste, não guard de runtime).

---

## 🛠️ 3. Detalhamento de Impacto Crítico

1. **`session/serializer` + `session/sinks` (HIGH):** o coração da feature 004. Quebra no serializer corrompe a memória de retomada entre boots; quebra no sink impede a reinjeção de contexto. A invariante de round-trip (RN-N2) é a salvaguarda — qualquer mudança exige `test_session.py` e `test_session_sinks.py` verdes.
2. **`DecisionService` + `domain/config` (HIGH):** sustentam o grafo de decisões e o desacoplamento de caminhos (feature 005). Mudança aqui afeta a integridade do índice derivado e o watch item W001. **T1 foi resolvido** no commit `cf73980` (import de `load_config` no MCP); o caminho configurável é hoje exercido tanto pela CLI quanto pelo MCP.
3. **`CommandService` (HIGH):** corrupção do `.harness/estado-da-sessao.md` invalida a retomada do ciclo forward; a âncora Git (RN-07) é o detector de divergência. **T2 foi resolvido** na feature 006 — CLI e MCP convergem para `config.session.state_file`, sem estado paralelo.
4. **`FormattingService` (HIGH):** uma exceção não-blindada travaria a gravação de arquivos do agente (viola RN-03). **T3 foi resolvido** no commit `cf73980` (import de `json` em `main.py`): o autoformat por hook `PostToolUse` (caminho real do Claude) volta a operar. Permanece **T4** — `[formatting]` declarado mas não consumido (config inerte).
5. **MCP driver `server.py` (HIGH):** antes concentrava T1 e T2, **ambos hoje resolvidos** (`cf73980` e feature 006). As duas tools de decisões e de sessão derivam os caminhos de `load_config`; CLI e MCP são caminhos equivalentes.

> Situação dos bugs nesta atualização: **T1 e T3 resolvidos** (commit `cf73980`); **T2 e T5 fechados** (feature 006). Permanece **T4** (config de formatação inerte), documentado como contexto. T6 segue documentado conforme a extração anterior.
