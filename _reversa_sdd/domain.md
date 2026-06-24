# Modelo de Domínio e Glossário (Domain) — harness-core

> Regenerado pelo Detective em 2026-06-24 (Re-extração após as features 003, 004 e 005)
> Nível de Documentação: **Completo**

Este documento define o glossário semântico e as regras de domínio que regem o comportamento e as restrições do núcleo Python do `harness`. Reflete o estado ATUAL do repositório, após o purge do legado `claude-config/` (commit `5624f78`) e a migração de estado e decisões para `.harness/`.

> ⚠️ **Mudança estrutural vs extração anterior:** os conceitos de **Shadow Mode** e **Corte Definitivo** (modos de bootstrap em coexistência com o legado) **deixaram de existir** — o modo *shadow*, o `test_parity` e o `LegacyDecisionImporter` foram purgados (MD-0001). O estado de sessão saiu de `ESTADO-DA-SESSAO.md`/`.claude/` para `.harness/estado-da-sessao.md` (feature 004), e as microdecisões saíram de `decisoes/` (raiz) para `.harness/decisoes/` (feature 005). Os artefatos de decisão vivem agora em `.harness/decisoes/` e o índice derivado em `.harness/microdecisoes.md`.

---

## 📖 1. Glossário de Domínio

### 🛡️ 1.1 Conceitos e Entidades Chave

* **Sessão do Agente (`SessionState`):** Estado temporal que indica se o assistente de IA está em atividade ativa numa feature. Persistido em `.harness/estado-da-sessao.md` no formato front-matter YAML (header-máquina) + corpo Markdown (a narrativa).
* **Narrativa de Retomada (`SessionNarrative`):** Value-object dentro de `SessionState` com quatro listas — *feito*, *próximos passos*, *pendências/bloqueios*, *ponteiros*. Escrita pelo agente, carregada e reinjetada pela CLI; nunca inventada. Materializa a memória de retomada entre boots (feature 004).
* **Âncora Git de Sessão:** SHA-1 do commit (HEAD) gravado no fechamento da sessão, usado na retomada para detectar se a base local divergiu da revisão sob a qual a sessão anterior foi concluída.
* **Reinjeção de Contexto:** Entrega do estado da última sessão ao contexto do agente no boot, pelo hook `SessionStart` → `./harness cmd resume`. O mecanismo concreto varia por harness (ver *Sink*).
* **Sink de Sessão (`SessionSink`):** Estratégia de entrega do estado ao contexto do agente, escolhida na borda pelo `active_harness`. Duas famílias: *hook* (`HookContextSink`, para Claude e Gemini, via `hookSpecificOutput.additionalContext` no stdout) e *arquivo* (`FileProjectionSink`, para Antigravity, projetando o estado num arquivo estático relido a cada boot).
* **Harness Ativo (`active_harness`):** Agente para o qual o core está configurado — um de `claude`, `gemini`, `antigravity`. Lido de `[harness]` no `harness.toml`. Seleciona tanto o *Sink* (sessão) quanto o *Perfil* (instalação).
* **Perfil de Harness (`HarnessProfile`):** Estratégia que encapsula o bloco de ganchos e as instruções de instalação de um agente (feature 003). Concretas: `ClaudeProfile`, `GeminiProfile`, `AntigravityProfile`.
* **Prompt de Instalação Colável:** Texto Markdown gerado por `install-prompt`, montado por composição (template + perfil do harness + introspecção da CLI), que o usuário cola no agente para instalar o harness passo a passo (feature 003).
* **Microdecisão (`Decision`):** Ficha de decisão arquitetural `MD-NNNN.md` com front-matter YAML e corpo nas quatro seções obrigatórias `D / PORQUÊ / DESCARTADO / ESTADO`. Vive em `.harness/decisoes/`.
* **Grafo de Decisões:** Conjunto das microdecisões e suas relações tipadas (`depende-de`, `substitui`, `refina`, `relaciona`, `estende`, `bloqueia`). O índice `.harness/microdecisoes.md` é DERIVADO dele com backlinks (verbos inversos).
* **Wrapper Executável (`harness`):** Ponto de entrada de conveniência em Bash na raiz que resolve a venv local (`harness-core/.venv/bin/python3`) e encaminha os argumentos para `harness-core/src/main.py`, com falha barulhenta se a venv não existir.
* **Formatador de Arquivos (`Formatter`):** Executável local ou global (`ruff`/`prettier`/`rustfmt`) invocado após a IA editar arquivos para manter a padronização, sempre de modo não-bloqueante.
* **Opt-out de Formatação:** Recusa de formatação automática ativada pela presença do arquivo `.no-autoformat` na pasta do arquivo ou em qualquer diretório superior.
* **Documentação Standalone (`harness-docs.html`):** Arquivo HTML único, autossuficiente e offline, contendo a superfície da CLI, as regras de domínio vigentes e o andamento dos checkpoints do Reversa.

### 🗂️ 1.2 Locais canônicos (estado atual)

| Artefato | Local canônico ATUAL | Local anterior (purgado/migrado) | Feature |
|---|---|---|---|
| Estado de sessão | `.harness/estado-da-sessao.md` | `ESTADO-DA-SESSAO.md` (raiz) / `.claude/ESTADO-DA-SESSAO.md` | 004 |
| Fichas de decisão | `.harness/decisoes/MD-NNNN.md` | `decisoes/` (raiz) | 005 |
| Índice de decisões | `.harness/microdecisoes.md` | `microdecisoes.md` (raiz) | 005 |
| Cabeçalho do índice | `.harness/decisoes/_cabecalho.md` | `decisoes/_cabecalho.md` (raiz) | 005 |

> 🟢 **Rastreabilidade (watch item W001 da feature 005):** os caminhos acima não são chumbados nos serviços — `main.py` e `server.py` os derivam de `[decisions]` no `harness.toml` via `load_config().decisions` (`dir = .harness/decisoes`, `index_file = .harness/microdecisoes.md`, `header_file = .harness/decisoes/_cabecalho.md`).

---

## ⚡ 2. Regras de Domínio Fundamentais

> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. As regras com prefixo **RN-N** são novas ou reescritas nesta re-extração (features 003/004/005); as **RN-01..RN-10** preservam a numeração histórica, ajustadas ao estado atual.

### 🔄 2.1 Sincronização e Resiliência

* **RN-01: Janela TTL de Sincronia (Cache Local)** 🟢
  - Origem: `harness-core/src/core/sync/service.py`
  - A verificação de sincronia Git guarda o resultado em cache por `cache_ttl_hours` (default 24). Dentro do TTL retorna `True` sem chamar a rede, evitando `ls-remote` redundante. Capacidade exposta apenas via MCP (`check_repository_sync`); não há subcomando `sync` na CLI.
* **RN-02: Resiliência Offline** 🟢
  - Origem: `harness-core/src/core/sync/service.py`
  - Qualquer erro de rede/git na verificação resulta em `True` (imprime aviso e prossegue), nunca travando a inicialização do agente.

### ✍️ 2.2 Integridade e Salvaguarda na Formatação

* **RN-03: Não-Bloqueio de Formatadores (Blindagem)** 🟢
  - Origem: `harness-core/src/core/formatting/service.py`
  - `format_file` **sempre** retorna `0`, com `try/except Exception` envolvendo todo o corpo, inclusive sob falha das ferramentas ou erro de importação — nunca aborta as tarefas de escrita do agente.
* **RN-04: Proteção de Diretórios Críticos** 🟢
  - Origem: `harness-core/src/core/formatting/service.py`
  - O formatador aborta sem alterar o arquivo se o caminho absoluto for `~`, começar por `~/Notas` ou por `~/.claude`. Blindagens chumbadas no código.
* **RN-05: Precedência de Executáveis Locais** 🟢
  - Origem: `harness-core/src/core/formatting/service.py`
  - Prioriza binários do projeto (`.venv/bin/ruff`, `venv/bin/ruff`, `node_modules/.bin/prettier`) antes de delegar ao PATH do host.
* **RN-06: Opt-out do Projeto** 🟢
  - Origem: `harness-core/src/core/formatting/service.py`
  - A presença de `.no-autoformat` na pasta do arquivo ou em qualquer diretório superior cancela a formatação. Nome do arquivo chumbado no código.
* **RN-N7: Descoberta da Raiz por Manifesto** 🟢
  - Origem: `harness-core/src/core/formatting/service.py`
  - A raiz do projeto é o primeiro diretório (subindo a árvore a partir do arquivo) que contenha `.git` **ou** `harness.toml`. Fallback: `os.getcwd()`. A seleção do formatador é por extensão: `.py`→ruff; `.js/.ts/.json/.css/.md`→prettier; `.rs`→rustfmt; demais → no-op.

### 👥 2.3 Sessão, Âncora e Reinjeção (feature 004)

* **RN-07: Validação da Âncora de Integridade Git** 🟢
  - Origem: `harness-core/src/core/commands/service.py`
  - Ao retomar (`resume`), se o HEAD atual divergir do `commit_hash` gravado no estado, um alerta `⚠️` de inconsistência de âncora é montado e antecede a narrativa reinjetada; a sessão é reativada mesmo assim.
* **RN-N1: Fonte Canônica Única do Estado de Sessão** 🟢
  - Origem: `harness-core/src/core/session/serializer.py`, `main.py:192`
  - O estado vive num único artefato versionado `.harness/estado-da-sessao.md` (front-matter YAML + corpo Markdown). Liga-se a **MD-0002** (unificação em `.harness/`).
  - 🟡 **Ressalva (T2):** o driver MCP (`server.py:92`) ainda aponta para `ESTADO-DA-SESSAO.md` na raiz, divergente da CLI — bug latente documentado, não corrigido aqui.
* **RN-N2: Invariante de Round-trip do Serializer** 🟢
  - Origem: `harness-core/src/core/session/serializer.py`
  - O serializer garante `parse(render(x)) == x`. O corpo é composto por quatro seções fixas que mapeiam a `SessionNarrative`: "O que foi feito"→`feito`, "Próximos passos"→`proximos_passos`, "Pendências / bloqueios"→`pendencias`, "Ponteiros"→`ponteiros`.
* **RN-N3: Narrativa Preservada na Retomada** 🟢
  - Origem: `harness-core/src/core/commands/service.py`
  - Em `resume` sob sessão existente, `start_session` reativa **preservando a narrativa** escrita pelo agente; a CLU reinjeta o corpo dela, nunca o inventa.
* **RN-N4: Ausente ≠ Malformado (Falha Barulhenta)** 🟢
  - Origem: `harness-core/src/core/commands/service.py`, `session/serializer.py`, `session/errors.py`
  - Arquivo de estado **ausente** → `None` (sessão nova normal). Arquivo **malformado** (sem `---`, YAML inválido, campo obrigatório ausente, commit não-SHA1) → `MalformedSessionStateError` — falha explícita, nunca silenciosa. Campos obrigatórios: `commit`, `feature`, `start_time`, `status`.
* **RN-N5: O Core Não Conhece o Harness** 🟢
  - Origem: `harness-core/src/core/session/sinks.py`, `commands/service.py`
  - A camada de domínio (`core/commands`, `core/session/serializer`) produz texto puro; a seleção do mecanismo de entrega por `active_harness` vive na borda (`get_sink` + `main.py`). Liga-se a **MD-0002/MD-0003** (baixo acoplamento, neutralidade a harness).
* **RN-N6: Reinjeção Multi-Harness por Família** 🟢
  - Origem: `harness-core/src/core/session/sinks.py`
  - A entrega do estado tem duas famílias: **hook** (`HookContextSink` — Claude e Gemini, mesmo envelope `hookSpecificOutput.additionalContext`) e **arquivo** (`FileProjectionSink` — Antigravity, em `.agents/rules/estado-sessao.md`). Mapeamento `_FAMILY_BY_HARNESS`; harness desconhecido → `ValueError` barulhento. Liga-se a **MD-0003**.
* **RN-N8: Teto de Contexto na Reinjeção (Claude)** 🟢
  - Origem: `harness-core/src/core/session/sinks.py`
  - `HookContextSink` trunca o `additionalContext` em `MAX_CHARS = 10000` (teto do Claude), anexando aviso de truncamento.

### 🧩 2.4 Instalação por Prompt (feature 003)

* **RN-N9: Geração do Prompt por Composição (Fonte Única)** 🟢
  - Origem: `harness-core/src/core/install/service.py`, `template.md`
  - `install-prompt` monta o prompt por substituição de 4 placeholders no `template.md` (`{{ACTIVE_HARNESS}}`, `{{APPLY_HOOKS}}`, `{{HOOKS_BLOCK}}`, `{{COMMANDS}}`). A lista de comandos vem da introspecção do argparse — nada mantido à mão em paralelo. Exposto apenas pela CLI (não MCP).
* **RN-N10: Resolução de Perfil Fail-Fast** 🟢
  - Origem: `harness-core/src/core/install/service.py`, `harness_profiles.py`
  - O perfil do harness é resolvido **antes** de qualquer I/O; harness inválido levanta `ValueError` antes de ler o template. `get_profile` resolve via dict `_PROFILES`; o bloco de ganchos é específico por perfil (Claude com JSON real; Gemini com a ponte `context.*`; Antigravity com aviso de mecanismo não confirmado).

### 📄 2.5 Microdecisões e Grafo (feature 005)

* **RN-N11: Caminhos de Decisão Desacoplados via Config** 🟢
  - Origem: `harness-core/src/core/domain/config.py`, `main.py`, `adapters/mcp/server.py`
  - Os caminhos de decisão (`dir`, `index_file`, `header_file`) vêm de `[decisions]` no `harness.toml`; o `DecisionService` recebe tudo por parâmetro e não chumba `decisoes/`. É a regra esperada pelo watch item **W001** da feature 005 e o efeito de **MD-0004** (harness-core como referência canônica). Default: `.harness/decisoes`, `.harness/microdecisoes.md`, `.harness/decisoes/_cabecalho.md`.
  - 🟡 **Ressalva (T1):** via MCP a chamada `load_config` **quebra** por import ausente (`NameError`), então o caminho configurável nunca é exercido pelo servidor MCP — só pela CLI.
* **RN-N12: Índice Derivado, Não Editado à Mão** 🟢
  - Origem: `harness-core/src/core/decisions/service.py`, `.harness/microdecisoes.md`
  - `.harness/microdecisoes.md` é DERIVADO pelo `./harness decisions` (hook `Stop`) a partir das fichas; o cabeçalho do arquivo declara "Não edite à mão". Backlinks compilados por verbos inversos, ordenados por ID de origem (determinismo).
* **RN-N13: Integridade do Grafo de Decisões** 🟢
  - Origem: `harness-core/src/core/decisions/service.py`, `domain/models.py`
  - `validate_integrity` agrega erros: validação individual de cada ficha (H1 com o ID + 4 seções `D/PORQUÊ/DESCARTADO/ESTADO`), **auto-relação** (`target == self.id`) e **aresta órfã** (alvo fora do grafo). Lista vazia = grafo válido.
* **RN-N14: Front-matter Obrigatório nas Fichas** 🟢
  - Origem: `harness-core/src/core/decisions/service.py`
  - Cada `MD-*.md` exige front-matter YAML (`id`, `gancho`, `estado`, `relacoes`). Diretório ausente → lista vazia; front-matter ausente ou YAML inválido → `ValueError` barulhento. Cada relação é `"<verbo> MD-XXXX"` (dois tokens), com verbo num conjunto fechado de seis e alvo `^MD-\d{4}$`.

### 📝 2.6 Geração e Exposição de Documentação

* **RN-08: Geração Sob Demanda da Documentação** 🟢
  - Origem: `harness-core/src/core/documentation/service.py`, `main.py`
  - O HTML `harness-docs.html` é (re)gerado pelo `./harness doc-gen` e servido por `./harness doc-serve` (`http.server` nativo). Consome artefatos do próprio Reversa (`_reversa_sdd/domain.md`, `.reversa/state.json`).
* **RN-09: Autossuficiência e Portabilidade do HTML** 🟢
  - Origem: `harness-core/src/core/documentation/service.py`
  - A documentação é um único HTML com CSS/JS embutidos, sem dependência de rede. Dados injetados substituindo `/* INJECTED_DATA_PLACEHOLDER */`.
* **RN-10: Introspecção Dinâmica dos Comandos** 🟢
  - Origem: `harness-core/src/core/documentation/service.py`, `install/service.py`
  - A lista de comandos e seus argumentos é extraída por introspecção do `argparse.ArgumentParser` (fonte única com a CLI real), reusada tanto pela documentação quanto pelo `install-prompt`. Reclassificada 🟡→🟢: o mecanismo está confirmado em dois consumidores.

### 🔧 2.7 Bootstrap de Ganchos Git

* **RN-N15: Bootstrap Idempotente e Não-Bloqueante** 🟢
  - Origem: `harness-core/src/core/bootstrap/service.py`
  - `install_hooks` grava `pre-commit` (→ `format`) e `post-merge` (→ `decisions`) reescrevendo a cada execução. Cada script só roda se o interpretador existir, senão `exit 0`.
  - 🟡 **Observação:** estes ganchos (pre-commit/post-merge) são um mecanismo **distinto** dos hooks de ciclo de vida do agente (`SessionStart`/`PostToolUse`/`Stop`) configurados nos `settings.json`. Coexistem dois mecanismos de gancho.

---

## 🔴 3. Lacunas e Dívidas (contexto, não correções)

| ID | Local | Sintoma | Confiança |
|---|---|---|---|
| **T1** | `adapters/mcp/server.py:60` | `load_config` usado sem import → `NameError` em `process_decisions` (ferramenta MCP de decisões quebra) | 🟢 |
| **T2** | `adapters/mcp/server.py:92` | `session_command` aponta para `ESTADO-DA-SESSAO.md` (raiz) — divergente da CLI (`.harness/estado-da-sessao.md`); estado de sessão CLI×MCP não convergem | 🟢 |
| **T3** | `main.py:63` | `json.loads` sem `import json` → `NameError` no `format` via stdin (hook `PostToolUse`); mascarado por `except`, autoformat por hook não ocorre | 🟢 |
| **T4** | `formatting/service.py` | `[formatting]` do `harness.toml` não alimenta o serviço; blindagens e opt-out chumbados | 🟡 |
| **T5** | `main.py` 21–41/213 | `load_harness_config` (dict legado) coexiste com `load_config` (tipada) — duas vias de configuração | 🟡 |
| **T6** | repositório | Sem lock file; pins apenas `>=` — build não determinístico | 🟡 |

> Os bugs T1–T3 não impedem o uso primário pela CLI (sessão, decisões e instalação funcionam pela CLI), mas degradam silenciosamente os caminhos MCP (T1/T2) e o autoformat por hook (T3). Documentados como contexto; **não corrigidos** nesta extração.
