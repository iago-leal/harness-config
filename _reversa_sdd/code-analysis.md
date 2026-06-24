# Análise de Código — harness-core

> Regenerado pelo Archaeologist em 2026-06-24 (re-extração após as features 003, 004 e 005).
> Projeto: `/Users/iagoleal/dev/harness`. Módulo único: **harness-core** — CLI Python + servidor MCP em arquitetura hexagonal (ports & adapters). `doc_level = completo`.

Categoria (Princípio nº 4): **Aplicação** — ferramenta com usuário (o próprio mantenedor), evolui no tempo, organizada em camadas.

## Visão geral da arquitetura

Hexágono clássico em três anéis:

- **Núcleo de domínio** (`src/core/`): regras de negócio puras, uma pasta por capacidade. Depende apenas de `core/ports/` (interfaces `ABC`), nunca de adaptadores concretos.
- **Portas** (`src/core/ports/`): contratos abstratos `FileSystemPort`, `GitPort`, `ProcessPort`.
- **Adaptadores** (`src/adapters/`): implementações físicas — `fs/local.py`, `git/subprocess.py`, `process/formatter.py` — e os dois drivers de entrada: a CLI (`src/main.py`) e o servidor MCP (`src/adapters/mcp/server.py`).

Inversão de dependência preservada: os serviços recebem as portas por injeção no construtor; quem as instancia (`main.py`, `server.py`, testes) escolhe a implementação concreta.

São **11 unidades** analisadas: 8 serviços de capacidade (`bootstrap`, `formatting`, `sync`, `decisions`, `commands`, `documentation`, `install`, `session`), o pacote `domain` (modelos + config + cache), o pacote `ports` e o pacote `adapters`.

```mermaid
graph TD
    CLI[main.py — CLI v2.0.0] --> Services
    MCP[adapters/mcp/server.py — FastMCP] --> Services
    subgraph Services[core/* — serviços de domínio]
        boot[bootstrap]
        fmt[formatting]
        sync[sync]
        dec[decisions]
        cmd[commands]
        doc[documentation]
        inst[install]
        sess[session]
    end
    Services --> Ports[core/ports — fs/git/process]
    Ports -.implementadas por.-> Adapters[adapters — fs/git/process]
    cmd --> sess
    CLI --> Config[core/domain/config.load_config]
    MCP --> Config
```

---

## 1. `core/bootstrap` — instalação de ganchos Git locais 🟢

**Arquivo:** `src/core/bootstrap/service.py` (57 linhas).

`BootstrapService.install_hooks(repo_path)` cria `.git/hooks/` e grava dois scripts Bash **idempotentemente** (reescreve a cada execução):

- `pre-commit` → invoca `harness-core/.venv/bin/python3 harness-core/src/main.py format "$@"`.
- `post-merge` → invoca o mesmo binário com `decisions "$@"`.

Os caminhos do interpretador e da CLI são literais chumbados dentro dos scripts (`_pre_commit_script`/`_post_merge_script`, `@staticmethod`). Cada script só executa se `$PYTHON_CLI` existir, senão `exit 0` (não bloqueia). Retorna a lista de caminhos instalados.

- **Fluxo:** linear, sem condicionais de negócio. Único efeito colateral: I/O em `.git/hooks/`.
- 🟡 **Observação:** os ganchos gravados por `bootstrap` (pre-commit/post-merge) são um caminho de instalação **diferente** dos hooks de ciclo de vida do agente (`SessionStart`/`PostToolUse`/`Stop`) descritos em `harness_profiles.py` e nos `settings.json`. Coexistem dois mecanismos de gancho. Nota: a versão anterior deste documento descrevia um "shadow log" / coexistência paralela com o legado `claude-config` — **não existe mais** no código atual (purgado no commit `5624f78`).

## 2. `core/formatting` — formatação por linguagem com blindagens 🟢

**Arquivo:** `src/core/formatting/service.py` (93 linhas). Serviço mais denso em regras de negócio.

`FormattingService.format_file(file_path) -> int` **sempre retorna 0** (no-op silencioso/não bloqueia — BR-MIGRAR-006), com `try/except Exception` envolvendo todo o corpo. Etapas:

1. **Blindagem de diretórios pessoais** (BR-MIGRAR-007): se `abs_path == ~`, ou começa por `~/Notas` ou `~/.claude`, retorna 0 sem formatar.
2. **Descoberta da raiz do projeto + opt-out** (BR-MIGRAR-009): sobe a árvore a partir do arquivo; em cada nível, se existir `.no-autoformat`, aborta (retorna 0); marca como raiz o nível que contiver `.git` **ou** `harness.toml`. Fallback: `os.getcwd()`.
3. **Seleção do formatador por extensão:** `.py`→`ruff`; `.js/.ts/.json/.css/.md`→`prettier`; `.rs`→`rustfmt`; extensão não suportada → retorna 0.
4. **Precedência de executável local** (BR-MIGRAR-008): para `ruff` procura `<root>/.venv/bin/ruff` e depois `venv/bin/ruff`; para `prettier`, `<root>/node_modules/.bin/prettier`. Se achar, passa o caminho; senão deixa o adaptador resolver no PATH.
5. **Execução** via `ProcessPort.execute_formatter(...)`, ignorando o código de retorno.

- **Loop não-trivial:** subida da árvore com parada quando `parent == current` (raiz do FS).
- ⚠️ **Divergência de configuração:** `format_file` **não** consulta `FormattingSection` (`exclude_paths`, `opt_out_file`). As blindagens (`~/Notas`, `~/.claude`) e o nome do opt-out (`.no-autoformat`) estão chumbados no código, embora `harness.toml` declare `[formatting]` com esses mesmos valores. A config existe no domínio mas não alimenta o serviço — mudar o `harness.toml` não muda o comportamento. 🟡 (dívida, candidato a ticket T4).

## 3. `core/sync` — verificação de sincronia Git com cache TTL 🟢

**Arquivo:** `src/core/sync/service.py` (69 linhas).

`SyncService.check_sync(repo_path) -> bool` decide se o repo local está em sincronia com o remoto, **resiliente a falhas** (BR-MIGRAR-005): retorna `True` em qualquer erro de rede/git (imprime aviso e prossegue).

Algoritmo:
1. **Cache** (BR-MIGRAR-003): se `cache_filepath` existe, lê JSON, parseia `last_checked_time` (ISO, coerção tz → UTC se naive). Dentro do TTL (`cache_ttl_hours`, default 24): retorna `True` — se o `commit_hash` do cache bate com o HEAD local, por consistência; mas **mesmo divergindo, retorna `True`** dentro do TTL (política de evitar excesso de rede). Falha no parse → cai para checagem de rede.
2. **Rede:** `git rev-parse HEAD` (local) e `git ls-remote origin main` (remoto).
3. **Atualiza cache** atomicamente via `SyncCache(...).model_dump_json()` + `write_file_atomic`.
4. Retorna `local_commit == remote_commit`.

- **Estrutura:** `SyncCache` (Pydantic): `last_checked_time: datetime`, `commit_hash` validado por regex SHA1.
- 🟢 **Exposição:** consumido apenas pelo MCP (`check_repository_sync` lê `cache_filepath=".harness/sync_cache.json"`, `cache_ttl=24` chumbados na ferramenta). **Não há subcomando `sync` na CLI** — capacidade só acessível via servidor MCP.

## 4. `core/decisions` — grafo de microdecisões e índice derivado 🟢

**Arquivo:** `src/core/decisions/service.py` (147 linhas). Três responsabilidades:

**`load_decisions(directory) -> List[Decision]`:** lista ordenada de `MD-*.md`; para cada, split por `---` (front-matter YAML, máx. 3 partes). Extrai `id`, `gancho`, `estado` (default `ativo`); parseia `relacoes` (cada string = `<verbo> <MD-XXXX>`, dois tokens). Diretório ausente → lista vazia. Front-matter ausente ou YAML inválido → `ValueError` barulhento.

**`validate_integrity(decisions) -> List[str]`:** agrega erros (lista vazia = grafo válido):
- Validação individual de cada ficha (`Decision.validate_integrity` — ver §9).
- **Auto-relação** (`target == self.id`): erro.
- **Aresta órfã** (alvo fora do `decision_map`): erro.

**`compile_index(decisions, output, header)`:** deriva backlinks e grava o índice consolidado:
- Tabela de **verbos inversos**: `refina→refinado-por`, `depende-de→requerido-por`, `estende→estendido-por`, `substitui→substituído-por`, `relaciona→relacionado-com`, `bloqueia→bloqueado-por`. Verbo fora da tabela → `inverso-de-<verbo>`.
- Backlinks ordenados por ID de origem (determinismo).
- Título de cada item extraído do H1 `# MD-XXXX — <título>` por regex.
- Sub-linha `↳ <saídas> · <entradas>` montada por composição.
- Cabeçalho opcional concatenado no topo. Gravação **atômica**.

- 🟢 **Caminhos desacoplados (feature 005):** `directory`, `output` e `header` são parâmetros; o serviço **não chumba** `decisoes/`. Quem fornece é `main.py`/`server.py` lendo `load_config().decisions`.

## 5. `core/commands` — slash commands de sessão agnósticos à IDE 🟢

**Arquivo:** `src/core/commands/service.py` (92 linhas).

`CommandService.execute_command(command, args, repo_path, session_filepath) -> str` normaliza o comando (`strip().lower().lstrip("/")`) e despacha:

- **`encerrar-sessao`:** carrega sessão; se ausente/inativa → erro. Senão lê HEAD (`git`), `session.close_session(commit)`, salva atomicamente. (BR-MIGRAR-014/015: âncora Git + isolamento).
- **`resume`:** sem sessão → cria `SessionState` com HEAD atual e feature `args[0]` (ou `"default_feature"`), salva, retorna "Nova sessão". Com sessão → compara `session.commit_hash` com HEAD; se divergir, monta `⚠️ ALERTA` de âncora; `start_session` reativa **preservando a narrativa** escrita pelo agente; salva; retorna `<warning><corpo da narrativa>\n<footer>`. O corpo vem de `serializer.render_narrative`.
- **`clarificar`:** texto fixo (limite de 2 rodadas de diálogo).
- **`handoff`:** monta bloco Markdown com feature ativa + HEAD.
- Desconhecido → `"Comando desconhecido: <command>"`.

`load_session` distingue **arquivo ausente** (→ `None`, sessão nova normal) de **arquivo malformado** (→ `MalformedSessionStateError`, RN-N4: falha barulhenta). `save_session` serializa via `serializer.render` atomicamente.

- **Acoplamento:** depende de `GitPort`, `FileSystemPort`, do domínio `SessionState`/`SessionNarrative` e do `session.serializer`. Não conhece harness — a seleção do sink fica em `main.py` (RN-N5).

## 6. `core/documentation` — geração do HTML por introspecção 🟢

**Arquivo:** `src/core/documentation/service.py` (114 linhas).

`DocumentationService` compõe um HTML estático injetando dados num template:

- **`extract_commands(parser)`:** varre `parser._actions`, acha o `_SubParsersAction`, lê `help` das pseudo-ações (`_choices_actions`) como fallback de `subparser.description`, e coleta args de cada subparser (flags, help, required, default). Introspecção do argparse — fonte única com a CLI real.
- **`parse_markdown_rules(domain_filepath)`:** regex extrai regras `**RN-XX: título** detalhes <emoji-confiança>` de `_reversa_sdd/domain.md`.
- **`load_checkpoints(state_filepath)`:** lê `.reversa/state.json` como dict (erro → `{}`).
- **`generate_html(...)`:** lê o template (ausente → `FileNotFoundError`), monta `{commands, rules, state}`, serializa em JSON e substitui o placeholder `/* INJECTED_DATA_PLACEHOLDER */` por `const HARNESS_DOC_DATA = {...};`. Grava atomicamente.

- **Acoplamento de leitura:** caminhos `_reversa_sdd/domain.md` e `.reversa/state.json` são passados por `main.py` (chumbados lá). O HTML consome artefatos **do próprio Reversa** — dependência do produto sobre o tooling de análise.

## 7. `core/install` — prompt de instalação colável (feature 003) 🟢 **NOVO**

**Arquivos:** `service.py` (45), `harness_profiles.py` (98), `template.md`.

Papel: gerar, por **composição**, um prompt Markdown que o usuário cola no agente para instalar o harness passo a passo, idempotente. Fonte única — nada mantido à mão em paralelo.

**`InstallPromptService.render(active_harness, parser) -> str`:**
1. Resolve o perfil **primeiro** (`get_profile`) — harness inválido falha antes de qualquer I/O (fail-fast).
2. Lê `template.md` e substitui 4 placeholders: `{{ACTIVE_HARNESS}}`, `{{APPLY_HOOKS}}` (instrução do perfil), `{{HOOKS_BLOCK}}` (bloco de ganchos do perfil), `{{COMMANDS}}` (introspecção do argparse, reaproveitando o padrão de `DocumentationService`).

**Estratégia por harness (`HarnessProfile`, padrão Strategy/OOP):** `ABC` com `hooks_block()` + `apply_instructions()`. Três concretas:
- `ClaudeProfile`: bloco JSON `hooks` real (`SessionStart`→`harness cmd resume`; `PostToolUse` Write|Edit→`harness format`; `Stop`→`harness decisions`, com `${CLAUDE_PROJECT_DIR}` e timeouts).
- `GeminiProfile`: comentário orientando a ponte `context.*` do settings do Gemini.
- `AntigravityProfile`: bloco-aviso ("mecanismo ainda não confirmado").

`get_profile(name)` resolve via dict `_PROFILES`; desconhecido → `ValueError` barulhento. Exposto pela CLI como `install-prompt` (apenas CLI, não MCP).

## 8. `core/session` — estado de sessão unificado (feature 004) 🟢 **NOVO**

**Arquivos:** `serializer.py` (109), `sinks.py` (77), `errors.py` (7).

Papel: persistir e reinjetar o estado da última sessão entre boots do agente. Formato canônico de `.harness/estado-da-sessao.md` = **front-matter YAML** (header-máquina) + **corpo Markdown** (`##` por seção da narrativa).

**`serializer`** — round-trip com invariante `parse(render(x)) == x`:
- `parse(text)`: regex `_FRONTMATTER_RE` separa meta e corpo. Sem `---` → `MalformedSessionStateError`. YAML inválido / não-dict → erro. Campos obrigatórios `_REQUIRED_META = (commit, feature, start_time, status)`; ausência → erro. `status == "active"` (case-insensitive) define `is_active`. Constrói `SessionState`; `ValueError` do domínio (ex.: commit não-SHA1) → `MalformedSessionStateError`.
- `render(state)`: monta meta (`commit/feature/start_time/status`), `yaml.safe_dump(sort_keys=False)`, anexa o corpo.
- `render_narrative(narrative)`: 4 seções fixas `_SECTIONS` — "O que foi feito"→`feito`, "Próximos passos"→`proximos_passos`, "Pendências / bloqueios"→`pendencias`, "Ponteiros"→`ponteiros`. Reusado na reinjeção de contexto.
- `_coerce_datetime`: aceita `datetime` ou string ISO (troca `Z`→`+00:00`); naive → UTC.

**`sinks`** — entrega do estado ao contexto do agente (na borda; o core não conhece harness — RN-N5):
- `HookContextSink` (Claude/Gemini): imprime no stdout `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": <texto>}}`; trunca em `MAX_CHARS = 10000` (teto do Claude) com sufixo de aviso.
- `FileProjectionSink` (Antigravity): grava o estado em `.agents/rules/estado-sessao.md` (cria o diretório-pai), pois o agy não injeta stdout no contexto.
- `get_sink(active_harness, fs)`: `_FAMILY_BY_HARNESS` (claude/gemini→hook; antigravity→file); desconhecido → `ValueError` barulhento.

**`errors`:** `MalformedSessionStateError(Exception)` — distingue "ausente" (normal) de "corrompido" (RN-N4).

## 9. `core/domain` — modelos, config tipada e cache 🟢

**Arquivos:** `models.py` (137), `config.py` (40), `cache.py` (6). Pydantic v2.

**`models.py`:**
- `Relationship`: `rel_type` validado contra 6 verbos (`depende-de, substitui, refina, relaciona, estende, bloqueia`, normalizado lower); `target_id` regex `^MD-\d{4}$`.
- `Decision`: `id` (regex MD), `gancho`, `status` (`ativo`/`descartado`), `relationships`, `filepath`, `raw_content`. `add_relationship` e `validate_integrity` (exige H1 com o ID e as 4 seções `D / PORQUÊ / DESCARTADO / ESTADO` via regex case-insensitive; `raw_content` ausente → erro).
- `SessionNarrative`: 4 listas (`feito, proximos_passos, pendencias, ponteiros`) + `is_empty()`. Value-object dentro de `SessionState`.
- `SessionState`: `commit_hash` (regex SHA1 de 40), `active_feature`, `start_time` (default UTC now), `is_active`, `narrative`. Métodos `start_session`/`close_session`/`update_active_feature` (este levanta `ValueError` se a sessão estiver inativa).

**`config.py`** — config tipada (crítico para feature 005):
- `HarnessConfig` = `harness` (`HarnessSection.active_harness` ∈ {claude,gemini,antigravity}) + `formatting` + `sync` + `decisions`.
- `DecisionsSection`: `dir=.harness/decisoes`, `index_file=.harness/microdecisoes.md`, `header_file=.harness/decisoes/_cabecalho.md`.
- `load_config(fs, config_path="harness.toml") -> HarnessConfig`: arquivo ausente → defaults; presente → `toml.loads(fs.read_file(...))` → `HarnessConfig(**data)`. **Funcional** (ver verificação dirigida V3).

**`cache.py`:** `SyncCache(last_checked_time: datetime, commit_hash: constr(SHA1))`.

## 10. `core/ports` — contratos abstratos 🟢

`fs.py` (`FileSystemPort`: `read_file, write_file, write_file_atomic, exists, list_dir, makedirs, remove`), `git.py` (`GitPort`: `get_head_commit, get_remote_commit`), `process.py` (`ProcessPort`: `execute_formatter -> (exit, stdout, stderr)`). Todas `ABC` com `@abstractmethod`. São a fronteira de inversão de dependência do hexágono.

## 11. `adapters` — implementações físicas + drivers 🟢

- **`fs/local.py`** (`LocalFileSystemAdapter`): I/O UTF-8; `write_file_atomic` grava `.<nome>.tmp` no mesmo diretório e faz `os.replace` (atômico no SO), com limpeza do tmp em falha.
- **`git/subprocess.py`** (`SubprocessGitAdapter`): `git rev-parse HEAD` e `git ls-remote origin main`; `CalledProcessError` → `RuntimeError` com stderr.
- **`process/formatter.py`** (`HostFormatterAdapter`): mapeia formatador→args (`ruff format`, `prettier --write`, `rustfmt <file>`); `FileNotFoundError`→`(127, ...)`; outro erro→`(-1, ...)`.
- **`mcp/server.py`** (driver MCP — FastMCP "Harness"): instancia os 3 adaptadores e expõe 4 ferramentas: `format_file`, `check_repository_sync`, `process_decisions`, `session_command`. **Contém os bugs latentes V1 e V2** (ver abaixo).
- **`main.py`** (driver CLI v2.0.0, 303 linhas): argparse com 7 subcomandos (`bootstrap, format, decisions, cmd, doc-gen, doc-serve, install-prompt`); orquestra serviços; resolve sinks de sessão; serve a documentação por `http.server`. **Contém o bug latente do achado adicional** (`json` não importado).

---

## Verificação dirigida — vereditos

> Examinados os arquivos-fonte reais. Escala: 🟢 CONFIRMADO / 🟡 INFERIDO / 🔴 LACUNA.

### V1 — `server.py` chama `load_config(fs)` sem importar `load_config` → 🟢 CONFIRMADO (bug, candidato a ticket T1)

`src/adapters/mcp/server.py:60` executa `config = load_config(fs)` dentro de `process_decisions`. Os imports do arquivo (linhas 1–11) **não incluem** `from src.core.domain.config import load_config` — diferentemente de `main.py:18`, que o importa. `load_config` está fora do escopo do módulo. Toda chamada à ferramenta MCP `process_decisions` levanta `NameError: name 'load_config' is not defined`, capturado pelo `try/except Exception` da própria função (server.py:82) e devolvido como string `"Erro ao processar decisões: name 'load_config' is not defined"`. A ferramenta nunca processa decisões via MCP. **Candidato a ticket de manutenção.**

### V2 — divergência de caminho de sessão CLI × MCP → 🟢 CONFIRMADO (bug, candidato a ticket T2)

- **CLI** (`main.py:192`): `session_file = ".harness/estado-da-sessao.md"` (local canônico da feature 004).
- **MCP** (`server.py:92`): `session_file = "ESTADO-DA-SESSAO.md"` (raiz, caminho legado pré-004).

`session_command` via MCP lê/escreve um arquivo diferente do que a CLI usa: `resume`/`encerrar-sessao` pelo MCP não enxergam o estado mantido pela CLI (e vice-versa), e podem criar um `ESTADO-DA-SESSAO.md` órfão na raiz. O MCP usa caminho **chumbado**, sem ler config (não há seção `[session]` no domínio). **Candidato a ticket de manutenção.**

### V3 — `load_config` em `config.py` é funcional → 🟢 CONFIRMADO

`src/core/domain/config.py` importa `toml` (linha 1), `pydantic` (2) e `FileSystemPort` (5). `load_config(fs, config_path="harness.toml")` (35–40) está completo e correto: ausência do arquivo → `HarnessConfig()` (defaults); presença → `toml.loads(fs.read_file(...))` → `HarnessConfig(**data)`. **Funcional.** O W003 da feature 005 (decisões lidas de `[decisions]` sem literais) é sustentado por esta função: `main.py` (`decisions` e `install-prompt`) e `server.py` (`process_decisions`) derivam os caminhos de `load_config().decisions`. A falha de V1 está **no driver MCP** (import ausente), **não** em `config.py`.

### Achado adicional (não solicitado) — `json.loads` em `main.py` sem `import json` → 🟢 CONFIRMADO (bug, candidato a ticket T3)

`main.py:63` (`resolve_format_target`) chama `payload = json.loads(raw)`, mas `main.py` **não importa `json`** (importa `os, sys, argparse, toml`). Quando `./harness format` roda **sem** argumento de caminho — exatamente o caso do hook `PostToolUse`, que entrega `tool_input.file_path` pelo stdin —, a leitura do stdin chega a `json.loads` e levanta `NameError: name 'json' is not defined`. O `except Exception` da própria `resolve_format_target` o captura e retorna `None`, então `main()` faz `sys.exit(0)` (no-op): **a formatação automática via hook nunca ocorre quando o caminho vem do stdin**. Degrada em silêncio. Como o fluxo Claude usa hook (não pre-commit do bootstrap), este é o caminho real de formatação. **Candidato a ticket de manutenção.**

---

## Fluxo de decisões — leitura de caminhos (feature 005) 🟢

Confirmada a **ausência de literais de caminho de decisão chumbados** nos drivers:

- **CLI** (`main.py`, subcomando `decisions`, linhas 160–185): `config = load_config(fs)` → `decisoes_dir = config.decisions.dir`, `output_file = config.decisions.index_file`, `header_file = config.decisions.header_file`. Nenhum literal `decisoes/` ou `microdecisoes.md`.
- **MCP** (`server.py`, `process_decisions`, linhas 60–64): `config = load_config(fs)` → `decisoes_dir = ... or config.decisions.dir`, `output_file = ... or config.decisions.index_file`; `header_file = os.path.join(decisoes_dir, "_cabecalho.md")`.

Diferença sutil: a CLI usa `config.decisions.header_file` (configurável); o MCP **deriva** o header de `os.path.join(decisoes_dir, "_cabecalho.md")` — coincide com o default mas ignora um eventual override de `header_file` no `harness.toml`. 🟡 (inconsistência menor, não bug). Ressalva crítica: por V1, no MCP a chamada a `load_config` **quebra** por import ausente, então o caminho configurável nunca é exercido via MCP.

`harness.toml` confirma a seção `[decisions]` com os três valores em `.harness/`. O `DecisionService` recebe tudo por parâmetro, sem chumbar nada.

> Nota residual: `main.py` ainda mantém a função antiga `load_harness_config` (linhas 21–41), que monta um dict com defaults **sem** a seção `[decisions]`. Ela coexiste com `load_config` (a tipada). O subcomando `cmd` lê `active_harness` desse dict legado (`config["harness"]["active_harness"]`, linha 213); o `decisions` e o `install-prompt` usam `load_config` (a tipada). Duas vias de configuração convivem — dívida de coesão, não bug. 🟡

---

## Resumo de candidatos a ticket (sem corrigir — apenas documentar)

| # | Local | Sintoma | Severidade sugerida |
|---|-------|---------|---------------------|
| T1 | `adapters/mcp/server.py:60` | `load_config` usado sem import → `NameError` em `process_decisions` (MCP) | Alta (ferramenta MCP inoperante) |
| T2 | `adapters/mcp/server.py:92` | `session_command` aponta para `ESTADO-DA-SESSAO.md` (raiz), divergente da CLI (`.harness/estado-da-sessao.md`) | Alta (estado de sessão divergente CLI×MCP) |
| T3 | `main.py:63` | `json.loads` sem `import json` → `NameError` no `format` via stdin (hook `PostToolUse`); mascarado por `except`, formatação silenciosamente não ocorre | Alta (autoformat por hook não funciona) |
| T4 | `formatting/service.py` | Blindagens e opt-out chumbados; `[formatting]` do `harness.toml` não alimenta o serviço | Média (config declarada sem efeito) |
| T5 | `main.py` 21–41/213 | `load_harness_config` (dict legado) coexiste com `load_config` (tipada); duas vias de configuração | Baixa (coesão) |
| T6 | repositório | Sem lock file; pins apenas `>=` (já levantado pelo Scout) | Média (reprodutibilidade) |
