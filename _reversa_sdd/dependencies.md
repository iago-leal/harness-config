# Dependências do Projeto — harness

> Gerado pelo Scout em 2026-06-24 (Re-extração após as features 003, 004, 005, 006, 007 e 008)
> Re-extração de reconciliação em 2026-07-05 (Scout, pós-features 010-021): manifesto revisto contra
> `requirements.in`/`requirements.txt` atuais — o pacote direto é **`fastmcp`** (não `mcp`, que é sua
> transitiva); `pydantic-settings` entra como transitiva relevante. Sem mudança na estratégia de lock (uv).

Mapeamento de dependências do código da aplicação (`.harness/harness-core/` + wrapper), de configuração e de ferramentas de sistema.

---

## 🐍 Dependências do Core Python (`.harness/harness-core/requirements.txt`)

O projeto gerencia suas dependências de alto nível em `.harness/harness-core/requirements.in` e utiliza o **`requirements.txt` como arquivo de lock determinístico**, compilado e travado via `uv pip compile`. Versões abaixo são as **efetivamente instaladas** na venv (`.harness/harness-core/.venv`, Python 3.14.6).

| Pacote       | Pin no manifesto | Instalado                    | Papel                                                                                                     |
| ------------ | ---------------- | ---------------------------- | --------------------------------------------------------------------------------------------------------- |
| **fastmcp**  | `>=0.4.1`        | `3.4.2` (via `fastmcp-slim`) | Framework do servidor MCP (`adapters/mcp/server.py`); puxa `mcp` 1.28.0 como SDK de protocolo transitivo. |
| **pydantic** | `>=2.0.0`        | `2.13.4`                     | Modelos de domínio e configuração tipada (`Decision`, `SessionState`, `HarnessConfig`).                   |
| **pytest**   | `>=8.0.0`        | `9.1.1`                      | Framework dos 33 arquivos `test_*.py` (+ `helpers.py`).                                                   |
| **toml**     | `>=0.10.2`       | `0.10.2`                     | Parser do `harness.toml` (carga de `HarnessConfig`).                                                      |

**Transitivas relevantes** (puxadas por `fastmcp`/`mcp`): `httpx 0.28.1`, `starlette 1.3.1`, `uvicorn 0.49.0`, `pydantic-settings 2.14.2`, `cryptography 49.0.0` (via `authlib`, JWT do MCP), `keyring 25.7.0` + `py-key-value-aio 0.4.5` (cache/credenciais do `fastmcp-slim`), `rich`/`cyclopts` (CLI helpers do `fastmcp-slim`, não usados diretamente pelo `main.py` do harness, que usa `argparse`).

> 🟢 **Reprodutibilidade Garantida:** A introdução do `requirements.in` compilado via `uv` para `requirements.txt` elimina a dívida técnica T6 de builds não determinísticos. Todos os ambientes locais e de CI utilizam o mesmo conjunto travado.
> 🟡 **Nota de superfície de dependências:** `fastmcp` (via `fastmcp-slim`) traz uma árvore transitiva consideravelmente mais larga que o `mcp` puro sugerido na extração anterior (JWT/crypto, keyring, cache assíncrono) — nenhuma dessas transitivas é referenciada diretamente pelo código do harness; é custo de manutenção herdado do framework, não do domínio.

---

## ⚙️ Dependências de Sistema e Ferramentas CLI

Ferramentas externas invocadas pelo wrapper, pelos ganchos e pelos adaptadores:

- **`bash` (>= 3.2)** 🟢 — Interpretador do wrapper `./harness`.
- **`python3` (>= 3.8; ambiente em 3.14.6)** 🟢 — Executa o core via venv local.
- **`git`** 🟢 — Invocado por `adapters/git/subprocess.py` (bootstrap de ganchos, verificação de sincronia) e usado pelo `CommandService` de sessão e evolução.
- **`uv` (>= 0.1.0)** 🟢 — Gerenciador de pacotes e resolvedor de dependências.
- **`GitHub Actions`** 🟢 — Pipeline de Integração Contínua configurado em `.github/workflows/ci.yml` executando pytest em Python 3.12 e 3.13.

> Sem `Dockerfile` ou `docker-compose.yml`. Pipeline de CI/CD ativo via GitHub Actions.

---

## 🧩 Framework Reversa (tooling instalado)

Não é dependência de runtime do produto, mas vive no repositório:

- **Reversa** — Framework de engenharia reversa instalado em duas árvores-espelho (`.claude/skills/` e `.agents/skills/`), com **47 agentes/skills** registrados em `.reversa/state.json#agents` (crescimento vs. a extração anterior: times de Migração, Docs e Code-New-Project foram adicionados). Ativado por `CLAUDE.md` / `GEMINI.md` / `AGENTS.md`.

---

## 🔗 Dependências internas (acoplamento do core)

Direção das setas = "depende de". A regra de negócio (`core/`) depende apenas dos `ports/` (interfaces), nunca dos adaptadores concretos — inversão de dependência preservada.

- `main.py` / `adapters/mcp/server.py` → serviços de `core/*` → `core/ports/*` ← implementados por `adapters/*`.
- `core/decisions`, `core/commands`, `core/documentation` → `core/domain/config.load_config` (caminhos de decisão e harness ativo).
- `core/commands` → `core/session/{serializer,sinks,errors}` (estado de sessão e reinjeção).
- `core/session/sinks` → seleção por `active_harness` (Claude/Gemini = hook; Antigravity = arquivo).
- `core/session/resume_context.build_decisions_appendix` (feature 021, novo) → lido pelo ramo `cmd resume`; anexa `.harness/microdecisoes.md` ao contexto reinjetado só quando `active_harness == "claude"` e `SessionSection.inject_decisions_index` (default `True`); não-bloqueante (índice ausente vira aviso em stderr, não exceção).
- `core/bootstrap` → `core/ports/{fs,process}` (interfaces `FileSystemPort` com `is_dir` e `ProcessPort` com `run_command` estendidas na feature 007 para viabilizar bootstrapping de novos diretórios).
- `core/session/close_flow` (feature 018, novo) → fonte única dos helpers de encerramento de sessão (`render_offer_markers`, `conduct_end_session_offers`, `SessionCloseFlow` etc.), reexportado por `main.py` para a CLI e consumido pelos scripts finos da skill `encerrar-sessao`; nenhuma duplicação entre os dois pontos de entrada.
- `core/migrate` (feature 020, novo) → serviço do subcomando `migrate`, converte instalações no layout copiado (core vendored) para a fonte única (shim `./harness` + `.venv` locais apontando para `harness init`/`upgrade` do upstream); independente de `core/bootstrap`, que segue cuidando de `init`/`upgrade` normais.
- `core/sync` (mantido, não removido pela 020) → `SyncService` segue checando versão local vs. upstream de forma passiva no boot da CLI (todo comando exceto `init/upgrade/agy-hook/materialize/migrate`); a 020 endereçou a _fonte_ do core (shim vs. cópia), não o mecanismo de aviso de versão.
