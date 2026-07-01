# Investigação: fonte única de execução + hooks não-destrutivos

> Feature: `020-fonte-unica-e-hooks` · Data: `2026-07-01`

## 1. Auditoria RF-08 — resolução de caminho por comando (pilar de viabilidade)

Pergunta: sob a fonte única (main.py roda do upstream, cwd = raiz do projeto), algum comando resolve **dado do projeto** pelo local do script (`__file__`) em vez do cwd? Se sim, a fonte única exigiria refatorar o core.

Método: varredura de `os.getcwd`, `__file__`, `abspath('.')` em `src/`, seguida de leitura dos pontos suspeitos.

| Comando                                          | Como resolve o projeto                                                                                           | Uso de `__file__`                     | Veredito                                                           |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------------ |
| `bootstrap`                                      | `os.getcwd()` (main.py:225)                                                                                      | —                                     | ✅ cwd                                                             |
| `format`                                         | `FormattingService` com `project_root = os.getcwd()` (service.py:55) + `file_path` do arg/stdin                  | —                                     | ✅ cwd                                                             |
| `decisions`                                      | `config.decisions.*` (paths relativos do `harness.toml`)                                                         | —                                     | ✅ cwd                                                             |
| `cmd` (resume/encerrar/handoff/clarificar/regen) | `os.getcwd()` (main.py:299,307,314)                                                                              | —                                     | ✅ cwd                                                             |
| `doc-gen` / `doc-serve`                          | `domain_path`/`state_path`/`output_path` **relativos ao cwd**; `base_dir=__file__` **só** para o `template.html` | `__file__` → template do core (asset) | ✅ cwd p/ dados; `__file__` p/ asset do core (correto no upstream) |
| `materialize`                                    | `target = os.getcwd()` (main.py:456); assets lidos de `session_skills._ASSETS_DIR` (do core)                     | `__file__` → assets do core           | ✅ cwd p/ escrita; asset do core no upstream                       |
| `install-prompt`                                 | `template.md` do core (`install/service.py:17`)                                                                  | `__file__` → asset do core            | ✅ (sem estado de projeto)                                         |
| `init` / `upgrade`                               | recebem `target_path`; `init_service.py:62` usa `__file__` p/ autodetectar o **upstream**                        | `__file__` → raiz do upstream         | ✅ (é justamente o upstream)                                       |
| MCP server                                       | `os.getcwd()` (server.py:40,101)                                                                                 | —                                     | ✅ cwd (herda contrato do shim)                                    |

**Conclusão 🟢:** nenhum comando resolve dado do projeto por `__file__`. Todos os `__file__` apontam para **assets do próprio core** (template da doc, `template.md`, `assets/skills/`, `sys.path` do `src`, autodetecção do upstream) — que devem vir do upstream. A fonte única é **viável sem tocar o core**; a mudança se concentra no wrapper, no `init_service`, nos dois materializadores e num serviço novo de migração.

## 2. Espaço de solução avaliado (recap do PCCP)

Três arquiteturas colapsam a duplicação de venv (medida: 17 × ~108 MB ≈ 1,83 GB, ~97 % em venvs):

- **A — venv central por symlink, scripts copiados.** Mínima, reversível, mas mantém a redundância dos scripts e um ponto único de falha frágil (symlink). Disco final ~160 MB.
- **B — fonte única total (escolhida).** Nem venv nem scripts no alvo; shim aponta para o upstream. Disco ~108 MB fixos, zero por projeto novo; elimina também `upgrade`/`sync`/`version` (menos maquinaria). Custo: acopla todos à HEAD do upstream (trade-off aceito) e depende do upstream local (H1).
- **C — `uv` com cache global (hardlink).** Preserva pin por-projeto sem pagar disco, mas introduz dependência nova (`uv`) no setup, contra "estabilidade > novidade".

B vence pelos critérios do mantenedor: menor pegada, menos código, zero dependência nova; H1 (mesma máquina) anula o único contra estrutural.

## 3. Precedentes internos aproveitados

- **Merge por named-hook (RN-N27, `antigravity_hooks.materialize_hooks_json`):** já lê o arquivo existente, substitui só a chave própria e grava atômico, preservando terceiros. É o **molde** para o merge por-item do `settings.json` do Claude (D-03) — a diferença é descer um nível (item dentro do array do evento, não a chave do evento).
- **Materialização não-destrutiva por nome próprio (RN-N28/N29, `session_skills`):** já preserva artefatos de terceiros ao materializar a skill. Reforça o padrão de D-04 (preservar hook alheio).
- **Footprint global zero (ADR-0013 / RN-N17):** a feature relaxa a autocontenção **física** (o core sai do projeto), mas preserva o invariante testado: nada é escrito fora do repo do projeto. O upstream é repo versionado, não `~/.claude` — a preocupação original do ADR (não acoplar a diretório de fornecedor; não criar estado global invisível) segue atendida.

## 4. Pontos de atenção técnicos

- **Shim e cwd:** git executa hooks com cwd na raiz do repo; o shim faz `cd "$SCRIPT_DIR"` (o wrapper vive na raiz) para garantir o cwd também em invocações manuais de subpastas. Alinhado à memória `claude-project-dir-slash-commands` (o `${CLAUDE_PROJECT_DIR}`/cwd não é confiável sem `cd`).
- **Parse do `upstream_path` em bash:** `sed -n 's/^upstream_path = "\(.*\)"/\1/p' harness.toml | head -1`. Simples e suficiente (o valor é um caminho absoluto entre aspas).
- **`.pyc` compartilhado:** múltiplos projetos executam o mesmo `src` do upstream; o CPython escreve `__pycache__` no diretório do upstream. Determinístico e inócuo; se incomodar, `PYTHONDONTWRITEBYTECODE=1` no shim.
- **MCP server:** ponto de entrada alternativo que também usa `os.getcwd()`; se algum projeto o expõe, deve ser iniciado com cwd na raiz — mesmo contrato do shim.

## 5. Fontes

- Código: `bootstrap/init_service.py`, `bootstrap/service.py`, `install/claude_settings.py`, `install/harness_profiles.py`, `install/local_apply.py`, `main.py`, `core/domain/config.py`, `adapters/mcp/server.py`, wrapper `harness`.
- Extração reversa: `domain.md#2.7,#2.8,#2.9,#2.11,#2.13`; `adrs/0013-harness-core-modulo-per-projeto-footprint.md`.
- Medição de disco: varredura de `~/dev` (17 `harness.toml` + `harness-core/.venv`).
