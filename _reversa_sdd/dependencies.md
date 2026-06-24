# Dependências do Projeto — harness

> Gerado pelo Scout em 2026-06-24 (Re-extração após as features 003, 004 e 005)

Mapeamento de dependências do código da aplicação (`harness-core/` + wrapper), de configuração e de ferramentas de sistema.

> ⚠️ **Mudança vs extração anterior:** a fonte legada `claude-config/settings.json` (com `enabledPlugins`) e o manifesto `claude-config/skills.active` **não existem mais** — foram purgados junto com o resto de `claude-config/`. As seções de plugins do Claude Desktop e de skills ativas descritas na extração anterior foram **removidas** deste documento por não corresponderem ao estado atual do repositório.

---

## 🐍 Dependências do Core Python (`harness-core/requirements.txt`)

Manifesto com versões **mínimas** (`>=`); versões abaixo são as **efetivamente instaladas** na venv (`harness-core/.venv`, Python 3.14.6).

| Pacote | Pin no manifesto | Instalado | Papel |
|---|---|---|---|
| **mcp** | `>=0.1.0` | `1.28.0` | SDK do Model Context Protocol; provê o `FastMCP` que sustenta `adapters/mcp/server.py`. |
| **pydantic** | `>=2.0.0` | `2.13.4` | Modelos de domínio e configuração tipada (`Decision`, `SessionState`, `HarnessConfig`). |
| **pytest** | `>=7.0.0` | `9.1.1` | Framework dos 14 arquivos de teste. |
| **toml** | `>=0.10.2` | `0.10.2` | Parser do `harness.toml` (carga de `HarnessConfig`). |
| **PyYAML** | `>=6.0` | `6.0.3` | Serialização round-trip do front-matter do estado de sessão (`session/serializer.py`). |

**Transitivas relevantes** (puxadas por `mcp`/FastMCP): `httpx 0.28.1`, `starlette 1.3.1`, `uvicorn 0.49.0`.

> 🔴 **Lacuna de reprodutibilidade:** não há lock file (`requirements.lock`, `poetry.lock`, etc.) commitado; os pins são apenas pisos `>=`. Build determinístico não está garantido — candidato a ticket (Princípio nº 5.3 do mantenedor).

---

## ⚙️ Dependências de Sistema e Ferramentas CLI

Ferramentas externas invocadas pelo wrapper, pelos ganchos e pelos adaptadores:

* **`bash` (>= 3.2)** 🟢 — Interpretador do wrapper `./harness`.
* **`python3` (>= 3.8; ambiente em 3.14.6)** 🟢 — Executa o core via venv local.
* **`git`** 🟢 — Invocado por `adapters/git/subprocess.py` (bootstrap de ganchos, verificação de sincronia) e usado pelo `CommandService` de sessão.
* **`ruff` (0.15.17)** 🟡 — Linter/formatter Python presente via `.ruff_cache/`; provável guardrail de qualidade, não declarado no `requirements.txt`.

> Sem `Dockerfile`, `docker-compose.yml` nem pipeline de CI/CD detectado.

---

## 🧩 Framework Reversa (tooling instalado)

Não é dependência de runtime do produto, mas vive no repositório:

* **Reversa** — Framework de engenharia reversa instalado em duas árvores-espelho (`.claude/skills/` e `.agents/skills/`), com ~30 agentes/skills (scout, archaeologist, architect, etc.). Ativado por `CLAUDE.md` / `GEMINI.md` / `AGENTS.md`.

---

## 🔗 Dependências internas (acoplamento do core)

Direção das setas = "depende de". A regra de negócio (`core/`) depende apenas dos `ports/` (interfaces), nunca dos adaptadores concretos — inversão de dependência preservada.

* `main.py` / `adapters/mcp/server.py` → serviços de `core/*` → `core/ports/*` ← implementados por `adapters/*`.
* `core/decisions`, `core/commands`, `core/documentation` → `core/domain/config.load_config` (caminhos de decisão e harness ativo).
* `core/commands` → `core/session/{serializer,sinks,errors}` (estado de sessão e reinjeção).
* `core/session/sinks` → seleção por `active_harness` (Claude/Gemini = hook; Antigravity = arquivo).
