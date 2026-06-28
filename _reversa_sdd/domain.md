# Modelo de Domínio e Glossário (Domain) — harness-core

> Regenerado pelo Detective em 2026-06-24 (Re-extração após a feature 009-hooks-antigravity)
> Nível de Documentação: **Completo**

Este documento define o glossário semântico e as regras de domínio que regem o comportamento e as restrições do núcleo Python do `harness`. Reflete o estado ATUAL do repositório, após o purge do legado `claude-config/` (commit `5624f78`), a migração de estado e decisões para `.harness/`, o suporte a bootstrapping evolucionário (feature 007), a reprodutibilidade e configuração dinâmica de formatação (feature 008) e os ganchos de ciclo de vida do Antigravity via driver de borda (feature 009).

---

## 📖 1. Glossário de Domínio

### 🛡️ 1.1 Conceitos e Entidades Chave

- **Sessão do Agente (`SessionState`):** Estado temporal que indica se o assistente de IA está em atividade ativa numa feature. Persistido em `.harness/estado-da-sessao.md` no formato front-matter YAML (header-máquina) + corpo Markdown (a narrativa).
- **Narrativa de Retomada (`SessionNarrative`):** Value-object dentro de `SessionState` com quatro listas — _feito_, _próximos passos_, _pendências/bloqueios_, _ponteiros_. Escrita pelo agente, carregada e reinjetada pela CLI; nunca inventada.
- **Âncora Git de Sessão:** SHA-1 do commit (HEAD) gravado no fechamento da sessão, usado na retomada para detectar se a base local divergiu da revisão sob a qual a sessão anterior foi concluída.
- **Reinjeção de Contexto:** Entrega do estado da última sessão ao contexto do agente no boot, pelo hook `SessionStart` → `./harness cmd resume`.
- **Sink de Sessão (`SessionSink`):** Estratégia de entrega do estado ao contexto do agente, escolhida na borda pelo `active_harness` (Claude/Gemini via hook stdout, Antigravity via projeção em arquivo estático).
- **Harness Ativo (`active_harness`):** Agente para o qual o core está configurado — um de `claude`, `gemini`, `antigravity`. Lido de `[harness]` no `harness.toml`.
- **Perfil de Harness (`HarnessProfile`):** Estratégia que encapsula o bloco de ganchos (`hooks_block()`) e as instruções de aplicação (`apply_instructions()`) de um agente. As três concretas estão **plenas**, sem placeholders: `ClaudeProfile` emite o esquema `hooks` do `.claude/settings.json`; `GeminiProfile` orienta a ponte `context.*` do `settings.json` do Gemini; **`AntigravityProfile` emite um `.agents/hooks.json` válido e parseável** (named-hook `harness` cobrindo `PreToolUse`/`PostToolUse`/`Stop`), com o placeholder literal `<ABS>` (`ABS_PLACEHOLDER`) resolvido na materialização e o matcher de tools de escrita `WRITE_MATCHER` (`write_to_file|replace_file_content|multi_replace_file_content`). A nota de escopo por harness ("aplique no projeto, nunca no global") vive em `apply_instructions()` dos três perfis, não mais chumbada no `template.md`.
- **Driver de Borda do Antigravity (`AntigravityHookBridge`):** Terceiro driver de entrada do hexágono, irmão da CLI (`main.py`) e do servidor MCP (`adapters/mcp/server.py`). Traduz o protocolo de ganchos do Antigravity — payload JSON camelCase no `stdin`, um formato de resposta por evento no `stdout` — e **delega aos serviços de domínio já existentes** (`FormattingService`, `DecisionService`), mantendo o core agnóstico ao harness (RN-N5). Invocado pelo subcomando fino `./harness agy-hook <evento>`. Não-bloqueante por contrato: toda exceção é capturada, logada em `stderr` e o stdout exigido por evento é emitido mesmo assim, com saída 0, preservando o laço do agente.
- **`hooks.json` do Antigravity (`.agents/hooks.json`):** Arquivo de configuração declarativo, versionável no projeto-alvo, que registra os ganchos do harness sob o named-hook `harness`. Diferente do `.claude/settings.json` (que mescla com outras chaves), é dedicado e seguro de escrever no `init`. Materializado por `materialize_hooks_json` com **merge por named-hook**: preserva chaves de terceiros e substitui apenas a chave `harness`. O campo `command` aponta para o `./harness` do projeto por **caminho absoluto**, resolvido a partir do `<ABS>` no `init`/`upgrade`.
- **Scratch de Captura (`stepIdx → TargetFile`):** Mapa efêmero, gravado pelo driver de borda sob `artifactDirectoryPath/.harness-agy/pending-format.json`, que relaciona o índice do passo (`stepIdx`) ao caminho do arquivo editado (`TargetFile`). Preenchido no `PreToolUse` e consumido no `PostToolUse` para recuperar, com granularidade por-edição, o alvo da formatação.
- **Prompt de Instalação Colável:** Texto Markdown gerado por `install-prompt`, montado por composição (template + perfil do harness + introspecção da CLI), que o usuário cola no agente para instalar o harness passo a passo.
- **Microdecisão (`Decision`):** Ficha de decisão arquitetural `MD-NNNN.md` com front-matter YAML e corpo nas quatro seções obrigatórias `D / PORQUÊ / DESCARTADO / ESTADO`. Vive em `.harness/decisoes/`.
- **Grafo de Decisões:** Conjunto das microdecisões e suas relações tipadas (`depende-de`, `substitui`, `refina`, `relaciona`, `estende`, `bloqueia`). O índice `.harness/microdecisoes.md` é DERIVADO dele com backlinks.
- **Wrapper Executável (`harness`):** Ponto de entrada de conveniência em Bash na raiz que resolve a venv local (`.harness/harness-core/.venv/bin/python3`) e encaminha os argumentos para `.harness/harness-core/src/main.py`.
- **Formatador de Arquivos (`Formatter`):** Executável local ou global (`ruff`/`prettier`/`rustfmt`) invocado após a IA editar arquivos para manter a padronização, sempre de modo não-bloqueante.
- **Opt-out de Formatação:** Recusa de formatação automática ativada pela presença do arquivo `.no-autoformat` na pasta do arquivo ou em qualquer diretório superior.
- **Documentação Standalone (`harness-docs.html`):** Arquivo HTML único, autossuficiente e offline, contendo a superfície da CLI, as regras de domínio vigentes e o andamento dos checkpoints do Reversa.
- **Repositório Upstream (`upstream_path`):** Caminho físico absoluto ou relativo configurado na seção `[harness]` do repositório de destino que aponta para o diretório original do core, servindo de base para evolução e checagem de atualizações.
- **Versão Local Instalada (`version`):** String contendo o identificador semântico de versão física do Harness instalado no repositório de destino.

### 🗂️ 1.2 Locais canônicos (estado atual)

| Artefato            | Local canônico ATUAL              | Local anterior (purgado/migrado)                             | Feature |
| ------------------- | --------------------------------- | ------------------------------------------------------------ | ------- |
| Estado de sessão    | `.harness/estado-da-sessao.md`    | `ESTADO-DA-SESSAO.md` (raiz) / `.claude/ESTADO-DA-SESSAO.md` | 004     |
| Fichas de decisão   | `.harness/decisoes/MD-NNNN.md`    | `decisoes/` (raiz)                                           | 005     |
| Índice de decisões  | `.harness/microdecisoes.md`       | `microdecisoes.md` (raiz)                                    | 005     |
| Cabeçalho do índice | `.harness/decisoes/_cabecalho.md` | `decisoes/_cabecalho.md` (raiz)                              | 005     |

---

## ⚡ 2. Regras de Domínio Fundamentais

> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. As regras com prefixo **RN-N** são novas ou reescritas a partir do ciclo de evolução forward; as **RN-01..RN-10** preservam a numeração histórica.

### 🔄 2.1 Sincronização e Resiliência

- **RN-01: Janela TTL de Sincronia (Cache Local)** 🟢
  - Origem: `.harness/harness-core/src/core/sync/service.py`
  - A verificação de sincronia Git guarda o resultado em cache por `cache_ttl_hours` (default 24). Dentro do TTL retorna `True` sem chamar a rede, evitando `ls-remote` redundante.
- **RN-02: Resiliência Offline** 🟢
  - Origem: `.harness/harness-core/src/core/sync/service.py`
  - Qualquer erro de rede/git na verificação resulta em `True` (imprime aviso e prossegue), nunca travando a inicialização do agente.

### ✍️ 2.2 Integridade e Salvaguarda na Formatação

- **RN-03: Não-Bloqueio de Formatadores (Blindagem)** 🟢
  - Origem: `.harness/harness-core/src/core/formatting/service.py`
  - `format_file` **sempre** retorna `0`, com `try/except Exception` envolvendo todo o corpo, inclusive sob falha das ferramentas ou erro de importação — nunca aborta as tarefas de escrita do agente.
- **RN-04: Proteção de Diretórios Críticos** 🟢
  - Origem: `.harness/harness-core/src/core/formatting/service.py`
  - O formatador aborta sem alterar o arquivo se o caminho absoluto for `~`, começar por `~/Notas` ou por `~/.claude`. Blindagens chumbadas no código.
- **RN-05: Precedência de Executáveis Locais** 🟢
  - Origem: `.harness/harness-core/src/core/formatting/service.py`
  - Prioriza binários do projeto (`.venv/bin/ruff`, `venv/bin/ruff`, `node_modules/.bin/prettier`) antes de delegar ao PATH do host.
- **RN-06: Opt-out do Projeto** 🟢
  - Origem: `.harness/harness-core/src/core/formatting/service.py`
  - A presença de `.no-autoformat` na pasta do arquivo ou em qualquer diretório superior cancela a formatação. Nome do arquivo chumbado no código.
- **RN-N7: Descoberta da Raiz por Manifesto** 🟢
  - Origem: `.harness/harness-core/src/core/formatting/service.py`
  - A raiz do projeto é o primeiro diretório (subindo a árvore a partir do arquivo) que contenha `.git` **ou** `harness.toml`. Fallback: `os.getcwd()`.

### 👥 2.3 Sessão, Âncora e Reinjeção

- **RN-07: Validação da Âncora de Integridade Git** 🟢
  - Origem: `.harness/harness-core/src/core/commands/service.py`
  - Ao retomar (`resume`), se o HEAD atual divergir do `commit_hash` gravado no estado, um alerta `⚠️` de inconsistência de âncora é montado e antecede a narrativa reinjetada; a sessão é reativada mesmo assim.
- **RN-N1: Fonte Canônica Única do Estado de Sessão** 🟢
  - Origem: `.harness/harness-core/src/core/session/serializer.py`, `main.py`, `core/domain/config.py`
  - O estado vive num único artefato versionado `.harness/estado-da-sessao.md`. Tanto a CLI quanto o MCP leem `config.session.state_file` por configuração.
- **RN-N2: Invariante de Round-trip do Serializer** 🟢
  - Origem: `.harness/harness-core/src/core/session/serializer.py`
  - O serializer garante `parse(render(x)) == x`. O corpo é composto por quatro seções fixas que mapeiam a `SessionNarrative`: "O que foi feito"→`feito`, "Próximos passos"→`proximos_passos`, "Pendências / bloqueios"→`pendencias`, "Ponteiros"→`ponteiros`.
- **RN-N3: Narrativa Preservada na Retomada** 🟢
  - Origem: `.harness/harness-core/src/core/commands/service.py`
  - Em `resume` sob sessão existente, `start_session` reativa **preservando a narrativa** escrita pelo agente; a CLI reinjeta o corpo dela, nunca o inventa.
- **RN-N4: Ausente ≠ Malformado (Falha Barulhenta)** 🟢
  - Origem: `.harness/harness-core/src/core/commands/service.py`, `session/serializer.py`, `session/errors.py`
  - Arquivo de estado **ausente** → `None`. Arquivo **malformado** (sem `---`, YAML inválido, campo obrigatório ausente, commit não-SHA1) → `MalformedSessionStateError` — falha explícita, nunca silenciosa.
- **RN-N5: O Core Não Conhece o Harness** 🟢
  - Origem: `.harness/harness-core/src/core/session/sinks.py`, `commands/service.py`
  - A camada de domínio produz texto puro; a seleção do mecanismo de entrega por `active_harness` vive na borda.
- **RN-N6: Reinjeção Multi-Harness por Família** 🟢
  - Origem: `.harness/harness-core/src/core/session/sinks.py`
  - A entrega do estado tem duas famílias: **hook** (`HookContextSink` — Claude e Gemini) e **arquivo** (`FileProjectionSink` — Antigravity, em `.agents/rules/estado-sessao.md`).
- **RN-N8: Teto de Contexto na Reinjeção (Claude)** 🟢
  - Origem: `.harness/harness-core/src/core/session/sinks.py`
  - `HookContextSink` trunca o `additionalContext` em `MAX_CHARS = 10000` (teto do Claude), anexando aviso de truncamento.

### 👥 2.4 Instalação por Prompt

- **RN-N9: Geração do Prompt por Composição (Fonte Única)** 🟢
  - Origem: `.harness/harness-core/src/core/install/service.py`, `template.md`
  - `install-prompt` monta o prompt por substituição de 4 placeholders no `template.md` (`{{ACTIVE_HARNESS}}`, `{{APPLY_HOOKS}}`, `{{HOOKS_BLOCK}}`, `{{COMMANDS}}`) obtendo a lista de comandos pela introspecção do argparse.
- **RN-N10: Resolução de Perfil Fail-Fast** 🟢
  - Origem: `.harness/harness-core/src/core/install/service.py`, `harness_profiles.py`
  - O perfil do harness é resolvido **antes** de qualquer I/O; harness inválido levanta `ValueError` antes de ler o template.

### 📄 2.5 Microdecisões e Grafo

- **RN-N11: Caminhos de Decisão Desacoplados via Config** 🟢
  - Origem: `.harness/harness-core/src/core/domain/config.py`, `main.py`, `adapters/mcp/server.py`
  - Os caminhos de decisão (`dir`, `index_file`, `header_file`) vêm de `[decisions]` no `harness.toml`. Default: `.harness/decisoes`, `.harness/microdecisoes.md`, `.harness/decisoes/_cabecalho.md`.
- **RN-N12: Índice Derivado, Não Editado à Mão** 🟢
  - Origem: `.harness/harness-core/src/core/decisions/service.py`, `.harness/microdecisoes.md`
  - `.harness/microdecisoes.md` é DERIVADO pelo `./harness decisions` (hook `Stop`) a partir das fichas; o cabeçalho do arquivo declara "Não edite à mão".
- **RN-N13: Integridade do Grafo de Decisões** 🟢
  - Origem: `.harness/harness-core/src/core/decisions/service.py`, `domain/models.py`
  - `validate_integrity` agrega erros: validação individual de cada ficha (H1 com o ID + 4 seções), **auto-relação** (`target == self.id`) e **aresta órfã** (alvo fora do grafo).
- **RN-N14: Front-matter Obrigatório nas Fichas** 🟢
  - Origem: `.harness/harness-core/src/core/decisions/service.py`
  - Cada `MD-*.md` exige front-matter YAML (`id`, `gancho`, `estado`, `relacoes`). Cada relação é `"<verbo> MD-XXXX"` (dois tokens), com verbo num conjunto fechado de seis e alvo `^MD-\d{4}$`.

### 📝 2.6 Geração e Exposição de Documentação

- **RN-08: Geração Sob Demanda da Documentação** 🟢
  - Origem: `.harness/harness-core/src/core/documentation/service.py`, `main.py`
  - O HTML `harness-docs.html` é (re)gerado pelo `./harness doc-gen` e servido por `./harness doc-serve` (`http.server` nativo). Consome artefatos do próprio Reversa.
- **RN-09: Autossuficiência e Portabilidade do HTML** 🟢
  - Origem: `.harness/harness-core/src/core/documentation/service.py`
  - A documentação é um único HTML com CSS/JS embutidos, sem dependência de rede.
- **RN-10: Introspecção Dinâmica dos Comandos** 🟢
  - Origem: `.harness/harness-core/src/core/documentation/service.py`, `install/service.py`
  - A lista de comandos e seus argumentos é extraída por introspecção do `argparse.ArgumentParser`.

### 🔧 2.7 Bootstrap de Ganchos Git

- **RN-N15: Bootstrap Idempotente e Não-Bloqueante** 🟢
  - Origem: `.harness/harness-core/src/core/bootstrap/service.py`
  - `install_hooks` grava `pre-commit` (→ `format`) e `post-merge` (→ `decisions`) reescrevendo a cada execução. Cada script só roda se o interpretador existir, senão `exit 0`.

### 🏠 2.8 Módulo Per-Projeto e Footprint Global Zero

- **RN-N16: Configuração por Via Única Tipada** 🟢
  - Origem: `.harness/harness-core/src/core/domain/config.py`, `main.py`
  - Toda a configuração passa por `load_config(fs)`, que devolve um `HarnessConfig` tipado. Não há mais via paralela.
- **RN-N17: Footprint Global Zero (Módulo Per-Projeto)** 🟢
  - Origem: `.harness/harness-core/tests/test_footprint.py`, `.harness/harness-core/tests/helpers.py` (`RecordingFileSystem`)
  - O harness-core é módulo **per-projeto autocontido**: instalá-lo ou executá-lo escreve apenas dentro do repositório, **nunca** em `~/.claude` ou `~/.agent-memory`. A restrição é testada de forma assertiva.

### 🚀 2.9 Bootstrap e Evolução do Tooling (feature 007)

- **RN-N18: Configuração de Upstream e Versão** 🟢
  - Origem: `.harness/harness-core/src/core/domain/config.py`
  - A configuração do workspace local suporta registrar a versão instalada (`version`) e o caminho absoluto do repositório upstream original (`upstream_path`) na seção `[harness]` do `harness.toml`.
- **RN-N19: Inicialização de Repositório Alvo (Bootstrap)** 🟢
  - Origem: `.harness/harness-core/src/core/bootstrap/init_service.py`
  - O comando `init` realiza a replicação física do wrapper e do core para um diretório de destino, ignorando pastas de desenvolvimento local e cache (`.git`, `.venv`, etc.), inicializa uma `.venv` no destino e instala os ganchos locais Git. Se o ambiente host não possuir dependências de setup, gera erros fail-fast amigáveis.
- **RN-N20: Evolução Não-Destrutiva (Upgrade)** 🟢
  - Origem: `.harness/harness-core/src/core/bootstrap/init_service.py`
  - O comando `upgrade` atualiza fisicamente o código e o wrapper no destino a partir de seu upstream, preservando intactas as pastas locais `.reversa/` (dados de engenharia reversa) e `.harness/decisoes/` (metadados arquiteturais). **A partir da feature 012**, a rematerialização dos artefatos de IDE no `upgrade` roda via **subprocesso do python de destino** (subcomando interno `materialize`), com o código recém-copiado e nunca com os módulos antigos em memória (corrige o bug de materialização stale). O `upgrade` aceita `--force`, que ignora a comparação de versão e força recópia + rematerialização.
- **RN-N21: Checagem Passiva de Atualização e Detecção Resiliente de Versão** 🟢
  - Origem: `.harness/harness-core/src/core/sync/service.py`, `.harness/harness-core/src/core/bootstrap/init_service.py`, `.harness/harness-core/src/main.py`
  - No boot da CLI e do servidor MCP, realiza-se uma comparação passiva rápida e estritamente local de versão local vs versão do upstream configurado. Se o upstream estiver à frente, exibe um alerta de nova versão disponível, de forma não-bloqueante e tolerante a erros de leitura. **A partir da feature 012**, a leitura da versão do upstream varre caminhos-candidato (`CORE_CONFIG_CANDIDATE_RELPATHS` em `layout.py`: layout canônico `.harness/harness-core/...` + legado da raiz), de modo a sobreviver a relocações do core no upstream. No `upgrade` (diferente do alerta passivo, que é silencioso), uma versão **indeterminada** faz o comando **abortar barulhento** (erro claro + instrução de `init`, exit ≠ 0) em vez de cair num fallback que igualaria a versão local e geraria um upgrade fantasma.

### ⚙️ 2.10 Formatação Dinâmica e Reprodutibilidade (feature 008)

- **RN-N22: Exclusão Dinâmica de Formatação via Configuração** 🟢
  - Origem: `.harness/harness-core/src/core/formatting/service.py`
  - A formatação automática de arquivos suporta caminhos e padrões glob de exclusão configurados na chave `formatting.exclude_paths` no `harness.toml`. Os arquivos que casam com estes caminhos são ignorados.
- **RN-N23: Casamento de Padrões Glob na Exclusão** 🟢
  - Origem: `.harness/harness-core/src/core/formatting/service.py`
  - Os padrões de exclusão que utilizam caracteres curinga (`*`, `?`, `[`, `]`) são resolvidos de forma dinâmica usando `fnmatch` contra o caminho relativo do arquivo em relação à raiz do projeto ou contra o nome base do arquivo.
- **RN-N24: Opt-Out Dinâmico Parametrizado** 🟢
  - Origem: `.harness/harness-core/src/core/formatting/service.py`
  - O arquivo indicador de recusa de formatação (opt-out) é lido a partir da configuração `formatting.opt_out_file` no `harness.toml` (default `.no-autoformat`), permitindo customização do nome por projeto.
- **RN-N25: Lock File e Pinning Determinístico de Dependências** 🟢
  - Origem: `.harness/harness-core/requirements.txt`
  - O projeto do core utiliza `requirements.txt` compilado deterministicamente via `uv pip compile` com base nas dependências abstratas em `requirements.in`, garantindo isolamento reprodutível das instalações.

### 🛰️ 2.11 Ganchos de Ciclo de Vida do Antigravity (feature 009)

- **RN-N26: Ganchos do Antigravity via `hooks.json` Declarativo e Driver de Borda** 🟢
  - Origem: `.harness/harness-core/src/adapters/antigravity/hook_bridge.py`, `.harness/harness-core/src/core/install/antigravity_hooks.py`, `.harness/harness-core/src/core/install/harness_profiles.py`, `.harness/harness-core/src/main.py`, `.harness/harness-core/src/core/bootstrap/init_service.py`
  - O harness integra-se ao Antigravity por um contrato **declarativo + de borda**, sem ramificar nenhum serviço de domínio por harness (RN-N5 reforçada). O `AntigravityProfile` emite o named-hook `harness` num `.agents/hooks.json` válido, cobrindo três eventos: captura em `PreToolUse`, formatação em `PostToolUse` e decisões em `Stop` (matcher de escrita `write_to_file|replace_file_content|multi_replace_file_content` nos dois primeiros; sem matcher no `Stop`). O `command` invoca `./harness agy-hook <evento>` por caminho absoluto resolvido na materialização.
  - O subcomando `agy-hook <evento>` constrói o `AntigravityHookBridge`, que lê o payload JSON camelCase no `stdin`, age via `FormattingService`/`DecisionService` e emite o stdout exigido por evento: `{"decision": "allow"}` no `pre-tool-use` (nunca bloqueia), `{}` no `post-tool-use`, `{}` no `stop` (jamais `{"decision": "continue"}`, para não reentrar no laço). O caminho do arquivo editado é recuperado por **captura no `PreToolUse` + formatação no `PostToolUse`**, usando um scratch `stepIdx → TargetFile` sob `artifactDirectoryPath`, preservando a granularidade por-edição da RN-03.
  - Não-bloqueio reforçado (RN-03): no `agy-hook`, todo o ramo — carga de config, leitura do stdin, construção dos serviços e a delegação — roda sob `try/except`, com o fallback exigido pelo evento pré-computado a partir do argumento já validado, de modo que `harness.toml` corrompido ou stdin ilegível ainda emite o stdout correto e encerra com 0.
- **RN-N27: Materialização Única do `hooks.json` Compartilhada por `init` e `upgrade`** 🟢
  - Origem: `.harness/harness-core/src/core/install/antigravity_hooks.py`, `.harness/harness-core/src/core/bootstrap/init_service.py`
  - `materialize_hooks_json(fs, project_path, command_path)` é a **rotina única** de escrita do `.agents/hooks.json`, chamada por `initialize_project` e por `upgrade_project` **apenas** quando `active_harness == "antigravity"` (RN-N19/RN-N20 estendidas). Faz **merge por named-hook**: lê o `hooks.json` existente (dict vazio se ausente, vazio ou inválido), substitui só a chave `harness` pelo bloco canônico do `AntigravityProfile` com `<ABS>` resolvido para o caminho absoluto do projeto, e grava de forma atômica via `FileSystemPort.write_file_atomic`. Toda escrita ocorre sob `project_path` — footprint global zero preservado (RN-N17). O `upgrade` reescreve o `command` com o caminho absoluto correto, mitigando a quebra do gancho se o repositório for movido.

### 🩹 2.12 Comandos de IDE Materializados no Bootstrap (feature 010)

- **RN-N28: Materialização Incondicional dos Slash Commands de Sessão** 🟢
  - Origem: `.harness/harness-core/src/core/install/session_commands.py`, `.harness/harness-core/src/core/bootstrap/init_service.py`
  - `materialize_session_commands(fs, project_path, command_path, profiles=None)` é a **rotina única** que grava os arquivos de slash command que acionam `./harness cmd encerrar-sessao` na IDE do agente. É chamada por `initialize_project` e por `upgrade_project` **sempre** — diferente de `materialize_hooks_json`, **não** há gate por `active_harness` (D-03): o comando deve aparecer para o Claude **e** para o Antigravity em qualquer instalação. Itera os perfis que expõem comando, grava cada artefato de forma atômica via `write_file_atomic` e cria os diretórios alvo; toda escrita ocorre sob `project_path` — footprint global zero preservado (RN-N17, e o novo materializador foi incluído no teste de footprint conforme a ressalva de 006/W003). Não-destrutivo: cada comando é arquivo próprio (`encerrar-sessao`), de modo que arquivos de terceiros nos diretórios não são lidos nem tocados; reexecutar `init`/`upgrade` converge ao mesmo resultado. O comando **não reimplementa** a lógica de fechamento — delega ao `CommandService` via wrapper, preservando RN-N5.
- **RN-N29: Superfície de Comando Encapsulada no Perfil** 🟢
  - Origem: `.harness/harness-core/src/core/install/harness_profiles.py`
  - O artefato de comando de cada harness vive no respectivo `HarnessProfile`, via `session_command_artifact(command_path) -> (rel_path, content) | None`, sem `if active_harness` no serviço (RN-N5 reforçada). `ClaudeProfile` devolve `.claude/commands/encerrar-sessao.md` (corpo com `!`-bash em `${CLAUDE_PROJECT_DIR}/harness`, portátil); `AntigravityProfile` devolve `.agent/workflows/encerrar-sessao.md` (singular, reconhecido pelo Antigravity — ✨f017; o plural `.agents/workflows/` era ignorado; caminho **absoluto** do wrapper resolvido na materialização, espelhando o `<ABS>` dos ganchos; frontmatter só com `description`, sem `name`; a materialização remove o órfão legado `.agents/workflows/encerrar-sessao.md` de forma não-destrutiva via `stale_session_command_paths`); `GeminiProfile` devolve `None` (sem superfície de slash command definida — ponto de extensão aberto). 🟡 O comportamento exato do workflow do Antigravity (execução de shell embutida vs instrução ao agente) não é verificável localmente; validar contra o Antigravity real quando disponível (alinha ao amarelo herdado de 009/W009).

### 🔁 2.13 Upgrade Resiliente e Materialização com Código Novo (feature 012)

- **RN-N30: Materialização Local por Função Única, com Código Recém-Copiado no Upgrade** 🟢
  - Origem: `.harness/harness-core/src/core/install/local_apply.py`, `.harness/harness-core/src/core/bootstrap/init_service.py`, `.harness/harness-core/src/main.py`
  - `apply_local_materializers(fs, project_path, command_path, active_harness)` é a **função única** que aplica os materializadores de IDE: `materialize_session_commands` sempre (RN-N28) e `materialize_hooks_json` só quando `active_harness == "antigravity"` (RN-N27). O `init` a chama **in-process** (o código em execução já é o do upstream, fresco); o `upgrade` a invoca via **subprocesso do python de destino** pelo subcomando interno `materialize` — garantindo que a materialização rode com o código recém-copiado, nunca com os módulos antigos em memória. Antes do subprocesso, o `upgrade` guarda a presença da venv e do `main.py` de destino, abortando barulhento com instrução de `init` se o core estiver incompleto. Toda escrita segue sob `project_path` (RN-N17 preservada).
  - **Janela conhecida (🟡):** o primeiro `upgrade` de um alvo ainda na versão anterior materializa com o código antigo (em execução), porque o fix só passa a valer com o código novo já carregado; do bump em diante o mecanismo é correto.

### 🔖 2.14 Versionamento do Encerramento de Sessão (feature 013)

- **RN-N31: Encerramento Versiona o Estado num Commit Isolado** 🟢
  - Origem: `.harness/harness-core/src/core/commands/service.py`, `.harness/harness-core/src/adapters/git/subprocess.py`
  - Ao `encerrar-sessao`, o comando captura a âncora (HEAD de **trabalho**) **antes** de qualquer escrita (RN-07), grava o estado e então cria um commit contendo **exclusivamente** o `state_file`, por cima do trabalho — via `GitPort.commit_paths(repo_path, [state_file], msg)`, que faz `git add -- <paths>` (nunca `git add -A`) e `git commit`. A âncora segue apontando para o trabalho; o commit de encerramento fica por cima e nunca se torna a âncora. A mensagem é `chore(sessao): encerrar sessão <feature>; âncora <ancora>` (limpa, sem co-autoria) e a saída do comando reporta os **dois** hashes. Vale para CLI **e** MCP, que compartilham o `CommandService`. Antes da 013 o registro de encerramento ficava como mudança pendente no working tree.
- **RN-N32: Commit pela Porta e Falha Barulhenta** 🟢
  - Origem: `.harness/harness-core/src/core/ports/git.py`, `.harness/harness-core/src/core/commands/errors.py`
  - O domínio versiona apenas pela porta `GitPort.commit_paths` (RN-N5 preservada; nenhum `subprocess`/`git` direto no serviço de comandos). Se o commit não puder ser criado, o comando levanta `SessionCommitError` (erro nomeado, exit ≠ 0), sem devolver sucesso e **sem reverter** o `state_file` já salvo (RN-N4 estendida ao fechamento).
