# Dependências do Projeto — harness

> Gerado pelo Scout em 2026-06-24 (Re-extração após as features 003, 004, 005, 006, 007 e 008)

Mapeamento de dependências do código da aplicação (`.harness/harness-core/` + wrapper), de configuração e de ferramentas de sistema.

---

## 🐍 Dependências do Core Python (`.harness/harness-core/requirements.txt`)

O projeto gerencia suas dependências de alto nível em `.harness/harness-core/requirements.in` e utiliza o **`requirements.txt` como arquivo de lock determinístico**, compilado e travado via `uv pip compile`. Versões abaixo são as **efetivamente instaladas** na venv (`.harness/harness-core/.venv`, Python 3.14.6).

| Pacote | Pin no manifesto | Instalado | Papel |
|---|---|---|---|
| **mcp** | `>=0.1.0` | `1.28.0` | SDK do Model Context Protocol; provê o `FastMCP` que sustenta `adapters/mcp/server.py`. |
| **pydantic** | `>=2.0.0` | `2.13.4` | Modelos de domínio e configuração tipada (`Decision`, `SessionState`, `HarnessConfig`). |
| **pytest** | `>=7.0.0` | `9.1.1` | Framework dos 15 arquivos de teste. |
| **toml** | `>=0.10.2` | `0.10.2` | Parser do `harness.toml` (carga de `HarnessConfig`). |
| **PyYAML** | `>=6.0` | `6.0.3` | Serialização round-trip do front-matter do estado de sessão (`session/serializer.py`). |

**Transitivas relevantes** (puxadas por `mcp`/FastMCP): `httpx 0.28.1`, `starlette 1.3.1`, `uvicorn 0.49.0`.

> 🟢 **Reprodutibilidade Garantida:** A introdução do `requirements.in` compilado via `uv` para `requirements.txt` elimina a dívida técnica T6 de builds não determinísticos. Todos os ambientes locais e de CI utilizam o mesmo conjunto travado.

---

## ⚙️ Dependências de Sistema e Ferramentas CLI

Ferramentas externas invocadas pelo wrapper, pelos ganchos e pelos adaptadores:

* **`bash` (>= 3.2)** 🟢 — Interpretador do wrapper `./harness`.
* **`python3` (>= 3.8; ambiente em 3.14.6)** 🟢 — Executa o core via venv local.
* **`git`** 🟢 — Invocado por `adapters/git/subprocess.py` (bootstrap de ganchos, verificação de sincronia) e usado pelo `CommandService` de sessão e evolução.
* **`uv` (>= 0.1.0)** 🟢 — Gerenciador de pacotes e resolvedor de dependências.
* **`GitHub Actions`** 🟢 — Pipeline de Integração Contínua configurado em `.github/workflows/ci.yml` executando pytest em Python 3.12 e 3.13.

> Sem `Dockerfile` ou `docker-compose.yml`. Pipeline de CI/CD ativo via GitHub Actions.

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
* `core/bootstrap` → `core/ports/{fs,process}` (interfaces `FileSystemPort` com `is_dir` e `ProcessPort` com `run_command` estendidas na feature 007 para viabilizar bootstrapping de novos diretórios).
