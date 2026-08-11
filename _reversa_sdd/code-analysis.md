# Análise de Código — harness-core

> Regenerado pelo Archaeologist em 2026-06-24 15:19 (Re-extração após a feature 009-hooks-antigravity; histórico: features 003, 004, 005, 006, 007 e 008). Âncora (HEAD): `e30b9a6`.
> Projeto: `/Users/iagoleal/dev/harness`. Módulo único: **harness-core** — CLI Python + servidor MCP + **driver de ganchos do Antigravity**, em arquitetura hexagonal (ports & adapters). `doc_level = completo`.
> **Reconciliação de 2026-07-05** (Archaeologist, pós-features 010-021 — este documento estava congelado desde a 009): nova unidade **13. `core/migrate`** (feature 020); unidade **8. `core/session`** expandida com `close_flow.py` (018, fonte única de orquestração do encerramento) e `resume_context.py` (021, apêndice do índice de decisões no `resume`). Caminhos confirmados sob `.harness/harness-core/` (a relocação em si é da feature 011). `data-dictionary.md` e `modules.json` reconciliados em conjunto — ver notas no rodapé de cada um.
> **Reconciliação de 2026-07-15** (Archaeologist, pós-MD-0014 e features 022-023): unidade **4. `core/decisions`** ganhou o módulo `gate.py` (gate de registro de microdecisões — avaliação pura, dupla identidade fina/grossa); **8. `core/session`** ganhou o 3º portão no `close_flow.py` e os campos anti-loop no `serializer.py`; **borda** `main.py` ganhou `decisions --gate` (hook Stop) e `cmd encerrar-sessao --sem-decisao`; `GitPort`/`SubprocessGitAdapter` ganharam `list_changed_paths_since`; o `AntigravityHookBridge` ganhou o advisory via `gate_evaluator` injetado; **o PostToolUse (format-on-edit) foi aposentado no perfil Claude** (MD-0014) — `ClaudeProfile.hooks_block()` e `claude_settings.py` não o materializam mais. Core 2.0.1 → **2.1.1**.
> **Reconciliação de 2026-08-11** (Archaeologist, pós-features 024-027; 025/026/027 lidas da árvore de trabalho, ainda sem commit): nova unidade **14. `core/progress`** (026/027 — medidor read-only `harness progress` + exportador kanban, quatro módulos: `service.py`, `stages.py`, `render.py`, `kanban.py`); **5. `core/commands`** ganhou `versionar_estado` no `execute_command` (024); **8. `core/session`** teve o `close_flow.py` reescrito no eixo do **consentimento** (024 — pré-check vira oferta com desfecho de segunda ordem, commit de encerramento tri-estado com default assimétrico por borda, marker `ENCERRAMENTO_NAO_VERSIONADO`); a borda `main.py` teve o ramo `decisions --gate` **despromovido de soft-block a advisory puro** (025 — stdout sempre vazio, aviso em stderr, exit 0) e ganhou o subcomando **`progress`** (026/027, três modos mutuamente exclusivos e contrato de exit codes 0/1/2); `config.py` ganhou `ProgressSection`/`ProgressKanbanSection`. Core 2.1.1 → **2.5.0**.

Categoria (Princípio nº 4): **Aplicação** — ferramenta com usuário (o próprio mantenedor), evolui no tempo, organizada em camadas.

## Visão geral da arquitetura

Hexágono clássico em três anéis:

- **Núcleo de domínio** (`src/core/`): regras de negócio puras, uma pasta por capacidade. Depende apenas de `core/ports/` (interfaces `ABC`), nunca de adaptadores concretos.
- **Portas** (`src/core/ports/`): contratos abstratos `FileSystemPort`, `GitPort`, `ProcessPort`.
- **Adaptadores** (`src/adapters/`): implementações físicas — `fs/local.py`, `git/subprocess.py`, `process/formatter.py` — e os **três drivers de entrada**: a CLI (`src/main.py`), o servidor MCP (`src/adapters/mcp/server.py`) e o **driver de ganchos do Antigravity** (`src/adapters/antigravity/hook_bridge.py`, feature 009).

Inversão de dependência preservada: os serviços recebem as portas por injeção no construtor; quem as instancia (`main.py`, `server.py`, testes) escolhe a implementação concreta. O driver do Antigravity segue o mesmo padrão: recebe `fs` e os serviços de domínio por injeção, e a CLI (`agy-hook`) faz a instanciação concreta na borda.

São **14 unidades** analisadas: 10 serviços de capacidade (`bootstrap`, `formatting`, `sync`, `decisions`, `commands`, `documentation`, `install`, `session`, `migrate` — feature 020 — e o **novo `progress`**, features 026/027), o pacote `domain` (modelos + config + cache), o pacote `ports` e o pacote `adapters` (que abriga o terceiro driver, em `adapters/antigravity/`).

```mermaid
graph TD
    CLI[main.py — CLI] --> Services
    MCP[adapters/mcp/server.py — FastMCP] --> Services
    AGY[adapters/antigravity/hook_bridge.py — AntigravityHookBridge] --> Services
    CLI -- agy-hook --> AGY
    CLI -- migrate --> Migrate[core/migrate — feature 020]
    CLI -- progress --> Progress[core/progress — features 026/027]
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
    sess --- closeflow[session/close_flow.py — feature 018]
    sess --- resumectx[session/resume_context.py — feature 021]
    dec --- gate[decisions/gate.py — features 022/023]
    Services --> Ports[core/ports — fs/git/process]
    Ports -.implementadas por.-> Adapters[adapters — fs/git/process]
    Migrate --> Ports
    Progress --> Ports
    cmd --> sess
    CLI --> Config[core/domain/config.load_config]
    MCP --> Config
```

---

## 1. `core/bootstrap` — ganchos Git, inicialização de repositório e upgrade 🟢

**Arquivos:** `src/core/bootstrap/service.py` (57 linhas), `src/core/bootstrap/init_service.py` (95 linhas).

Esta unidade é responsável pela instalação dos ganchos Git locais, assim como pelo provisionamento e evolução (upgrade) de novos workspaces físicos do Harness.

### Instalação de Ganchos (`BootstrapService`)

`BootstrapService.install_hooks(repo_path)` cria `.git/hooks/` e grava dois scripts Bash **idempotentemente** (reescreve a cada execução):

- `pre-commit` → invoca `.harness/harness-core/.venv/bin/python3 .harness/harness-core/src/main.py format "$@"`.
- `post-merge` → invoca o mesmo binário com `decisions "$@"`.

Os caminhos do interpretador e da CLI são literais chumbados dentro dos scripts (`_pre_commit_script`/`_post_merge_script`, `@staticmethod`). Cada script só executa se `$PYTHON_CLI` existir, senão `exit 0` (não bloqueia). Retorna a lista de caminhos instalados.

### Inicialização e Evolução (`InitService` — feature 007)

A feature 007 introduziu a rotina de cópia física e setup evolucionário:

- **`init_target(fs, process, target_path, active_harness, upstream_path, version)`**:
  1. Cria o diretório de destino se inexistente.
  2. Executa cópia física recursiva dos arquivos do core e do wrapper Bash ignorando pastas de desenvolvimento e cache (`.git/`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `tmp/`).
  3. Descarrega o arquivo padrão `harness.toml` contendo o `active_harness`, o `upstream_path` (caminho absoluto para o core original) e a `version` corrente.
  4. Executa a criação da `.venv` local no destino (`python3 -m venv .venv` via `ProcessPort.run_command`). Se falhar por falta de dependências no host, gera um alerta fail-fast e detalhado de setup para ação humana.
  5. Instala os ganchos Git locais de forma automática e idempotente.
  6. **(feature 009)** Quando `active_harness == "antigravity"`, materializa `.agents/hooks.json` chamando `materialize_hooks_json(fs, target_path, command_path)`, onde `command_path = os.path.abspath(target_path)` é o prefixo absoluto que substitui `<ABS>` no `command` dos ganchos. 🟢
- **`upgrade_target(fs, process, target_path, upstream_path, version)`**:
  1. Atualiza o wrapper executável `harness` na raiz do destino.
  2. Realiza a replicação física do `.harness/harness-core/` do upstream para o destino de forma **estritamente não-destrutiva**: as pastas `.reversa/` (dados de engenharia reversa) e `.harness/decisoes/` (metadados arquiteturais locais) são preservadas intactas.
  3. Atualiza os campos de configuração no `harness.toml` do destino para sincronizar a versão do core instalado.
  4. **(feature 009)** Lê `active_harness` do `harness.toml`; se for `antigravity`, **reescreve** `.agents/hooks.json` via `materialize_hooks_json` com o caminho absoluto corrente — assim o `command` segue válido caso o repositório tenha sido movido desde o `init` (mitiga a dívida do caminho absoluto). 🟢

---

## 2. `core/formatting` — formatação por linguagem com blindagens 🟢

**Arquivo:** `src/core/formatting/service.py` (93 linhas). Serviço mais denso em regras de negócio.

`FormattingService.format_file(file_path) -> int` **sempre retorna 0** (no-op silencioso/não bloqueia — BR-MIGRAR-006), com `try/except Exception` envolvendo todo o corpo. Etapas:

1. **Blindagem de diretórios pessoais** (BR-MIGRAR-007): se `abs_path == ~`, ou começa por `~/Notas` ou `~/.claude`, retorna 0 sem formatar.
2. **Descoberta da raiz do projeto + opt-out** (BR-MIGRAR-009): sobe a árvore a partir do arquivo; em cada nível, se existir `.no-autoformat`, aborta (retorna 0); marca como raiz o nível que contiver `.git` **ou** `harness.toml`. Fallback: `os.getcwd()`.
3. **Seleção do formatador por extensão:** `.py`→`ruff`; `.js/.ts/.json/.css/.md`→`prettier`; `.rs`→`rustfmt`; extensão não suportada → retorna 0.
4. **Precedência de executável local** (BR-MIGRAR-008): para `ruff` procura `<root>/.venv/bin/ruff` e depois `venv/bin/ruff`; para `prettier`, `<root>/node_modules/.bin/prettier`. Se achar, passa o caminho; senão deixa o adaptador resolver no PATH.
5. **Execução** via `ProcessPort.execute_formatter(...)`, ignorando o código de retorno.

- 🟢 **Configuração viva de formatação:** O `FormattingService` consome o `HarnessConfig` passado em seu construtor e utiliza as regras dinâmicas definidas no `harness.toml` para `opt_out_file` e `exclude_paths` (com suporte a glob matching e checagem de diretórios via `fnmatch`), mantendo a blindagem básica incondicional de segurança como salvaguarda mínima.

---

## 3. `core/sync` — verificação de sincronia Git e alertas passivos de versão 🟢

**Arquivo:** `src/core/sync/service.py` (69 linhas).

### Sincronia Git (`SyncService.check_sync`)

`SyncService.check_sync(repo_path) -> bool` decide se o repo local está em sincronia com o remoto, **resiliente a falhas** (BR-MIGRAR-005): retorna `True` em qualquer erro de rede/git (imprime aviso e prossegue).

1. **Cache** (BR-MIGRAR-003): se `cache_filepath` existe, lê JSON, parseia `last_checked_time` (ISO, coerção tz → UTC se naive). Dentro do TTL (`cache_ttl_hours`, default 24): retorna `True` — se o `commit_hash` do cache bate com o HEAD local, por consistência; mas **mesmo divergindo, retorna `True`** dentro do TTL.
2. **Rede:** `git rev-parse HEAD` (local) e `git ls-remote origin main` (remoto).
3. **Atualiza cache** atomicamente via `SyncCache(...).model_dump_json()` + `write_file_atomic`.
4. Retorna `local_commit == remote_commit`.

### Alertas Passivos de Versão (`check_version_update` — feature 007)

A feature 007 introduziu `check_version_update(fs, local_version, upstream_path)` para ler a configuração do upstream diretamente de forma I/O estritamente local (sem rede ou subprocessos custosos):

1. Se `upstream_path` estiver configurado, lê o `harness.toml` do upstream usando a `FileSystemPort`.
2. Parseia a versão do upstream.
3. Se a versão do upstream for semanticalmente maior que a local, retorna a versão do upstream para que o driver principal exiba alertas discretos de upgrade no boot do agente.

---

## 4. `core/decisions` — grafo de microdecisões e índice derivado 🟢

**Arquivo:** `src/core/decisions/service.py` (147 linhas). Três responsabilidades:

**`load_decisions(directory) -> List[Decision]`**: lista ordenada de `MD-*.md`; para cada, split por `---` (front-matter YAML, máx. 3 partes). Extrai `id`, `gancho`, `estado` (default `ativo`); parseia `relacoes` (cada string = `<verbo> <MD-XXXX>`, dois tokens). Diretório ausente → lista vazia. Front-matter ausente ou YAML inválido → `ValueError` barulhento.

**`validate_integrity(decisions) -> List[str]`**: agrega erros (lista vazia = grafo válido):

- Validação individual de cada ficha (`Decision.validate_integrity` — ver §9).
- **Auto-relação** (`target == self.id`): erro.
- **Aresta órfã** (alvo fora do `decision_map`): erro.

**`compile_index(decisions, output, header)`**: deriva backlinks e grava o índice consolidado:

- Tabela de **verbos inversos**: `refina→refinado-por`, `depende-de→requerido-por`, `estende→estendido-por`, `substitui→substituído-por`, `relaciona→relacionado-com`, `bloqueia→bloqueado-por`.
- Backlinks ordenados por ID de origem (determinismo).
- Título de cada item extraído do H1 `# MD-XXXX — <título>` por regex.
- Sub-linha `↳ <saídas> · <entradas>` montada por composição.
- Cabeçalho opcional concatenado no topo. Gravação **atômica**.

### `gate.py` — gate de registro de microdecisões (features 022/023, NOVO) 🟢

**Arquivo:** `src/core/decisions/gate.py` (103 linhas). Avaliação **pura** de pendência de registro: houve trabalho substantivo na sessão sem nenhuma ficha `MD-*.md` nova ou modificada? Agnóstico ao harness (RN-N5): não conhece `active_harness` nem decide COMO interceptar — bloqueio, lembrete ou advisory são escolhas da borda.

- **`evaluate_registration_gate(git, repo_path, session, config) -> GateVerdict`**: universo = `git.list_changed_paths_since(âncora)` ∪ `git.list_dirty_paths()` (trabalho commitado + sujo). Excluem-se o arquivo de estado (`config.session.state_file`), o índice e o cabeçalho de decisões; fichas são os caminhos sob `config.decisions.dir` que casam `^MD-.*\.md$`. `pendente = bool(mudancas) and not fichas`. **Sem filtro por tipo de arquivo** (esclarecimento 2026-07-15: repositórios documentais contam tanto quanto código). **Fail-open barulhento** (RN-05): âncora ilegível/repo sem commit → `pendente=False` + `aviso` preenchido; a borda ecoa em stderr.
- **`compute_fingerprint(anchor, head, dirty)`** — identidade **fina**, `sha1(âncora + HEAD + sujos ordenados)`: trabalho novo muda o fingerprint e **rearma** o portão do encerramento. Sem relógio (D-03 da 022).
- **`compute_lembrete_fingerprint(anchor)`** — identidade **grossa** (023/D-02), `sha1(âncora)`: estável do início ao fim da sessão → o lembrete do Stop dispara **no máximo uma vez por sessão**; nem arquivo tocado nem commit novo o rearmam.
- **`GateVerdict`** (Pydantic, não persistido): `pendente`, `mudancas`, `fichas_tocadas`, `fingerprint` (fina), `fingerprint_lembrete` (grossa), `aviso`. Só os fingerprints sobrevivem, nos campos anti-loop do `SessionState`.

**Três bordas consomem o veredito** (desde a 025, com apenas **duas políticas**): o 3º portão do `SessionCloseFlow` (a ÚNICA política bloqueante, com escape `--sem-decisao`, identidade fina — §8), o ramo `decisions --gate` do `main.py` (**advisory puro desde a 025/MD-0018**: o soft-block JSON `{"decision":"block",...}` no stdout foi aposentado; o desfecho pendente vira linha `Aviso:` em stderr, stdout sempre vazio, exit 0 — identidade grossa preservada, no máximo 1 aviso por sessão — §11) e o `AntigravityHookBridge` (advisory em stderr, nunca bloqueia, inalterado — §12). Liga/desliga por `decisions.require_registration` (default `True`).

---

## 5. `core/commands` — slash commands de sessão agnósticos à IDE 🟢

**Arquivo:** `src/core/commands/service.py` (92 linhas).

`CommandService.execute_command(command, args, repo_path, session_filepath, versionar_estado=True) -> str` normaliza o comando (`strip().lower().lstrip("/")`) e despacha:

- **`encerrar-sessao`**: carrega sessão; se ausente/inativa → erro. Senão lê HEAD (`git`), `session.close_session(commit)`, salva atomicamente. **Desde a 024 (MD-0017)**, o parâmetro `versionar_estado` (default `True`, preservando todos os chamadores) controla o commit de fechamento: com `False`, fecha o estado no arquivo, **pula** `commit_paths`, acrescenta linha declarativa na narrativa (RN-N3: registra ato, não inventa narrativa) e devolve mensagem anunciando o não-versionamento — a âncora é capturada antes de qualquer escrita e, sem commit, âncora e HEAD coincidem. A borda MCP mantém `versionar_estado=True` por assimetria deliberada (D-04 da 024).
- **`resume`**: sem sessão → cria `SessionState` com HEAD atual e feature `args[0]` (ou `"default_feature"`), salva, retorna "Nova sessão". Com sessão → compara `session.commit_hash` com HEAD; se divergir, monta `⚠️ ALERTA` de âncora; `start_session` reativa **preservando a narrativa** escrita pelo agente; salva; retorna `<warning><corpo da narrativa>\n<footer>`.
- **`clarificar`**: texto fixo (limite de 2 rodadas de diálogo).
- **`handoff`**: monta bloco Markdown com feature ativa + HEAD.
- Desconhecido → `"Comando desconhecido: <command>"`.

---

## 6. `core/documentation` — geração do HTML por introspecção 🟢

**Arquivo:** `src/core/documentation/service.py` (114 linhas).

`DocumentationService` compõe um HTML estático injetando dados num template:

- **`extract_commands(parser)`**: varre `parser._actions`, acha o `_SubParsersAction`, lê `help` das pseudo-ações como fallback de `subparser.description`, e coleta args de cada subparser (flags, help, required, default). Introspecção do argparse — fonte única com a CLI real.
- **`parse_markdown_rules(domain_filepath)`**: regex extrai regras `**RN-XX: título** detalhes <emoji-confiança>` de `_reversa_sdd/domain.md`.
- **`load_checkpoints(state_filepath)`**: lê `.reversa/state.json` como dict (erro → `{}`).
- **`generate_html(...)`**: lê o template, monta `{commands, rules, state}`, serializa em JSON e substitui o placeholder `/* INJECTED_DATA_PLACEHOLDER */` por `const HARNESS_DOC_DATA = {...};`. Grava atomicamente.

---

## 7. `core/install` — prompt de instalação colável + materialização de ganchos 🟢

**Arquivos:** `service.py` (45), `harness_profiles.py` (157), `antigravity_hooks.py` (68, feature 009), `template.md`.

Papel: gerar, por **composição**, um prompt Markdown que o usuário cola no agente para instalar o harness passo a passo, de forma idempotente; e, a partir da feature 009, **materializar fisicamente** o `.agents/hooks.json` do Antigravity.

### Perfis por harness (`harness_profiles.py`) — feature 009

`HarnessProfile` (ABC) define `hooks_block()` e `apply_instructions()`; três concretas registradas em `_PROFILES`, resolvidas por `get_profile(name)` (fail-fast em nome desconhecido). O escopo por harness (onde aplicar os ganchos, nunca em diretório global) migrou para `apply_instructions()` dos três perfis — antes estava chumbado no `template.md`.

- **`ClaudeProfile`**: bloco JSON `hooks` real (`SessionStart`→`harness cmd resume`; `Stop`→`harness decisions --gate`, desde a 022), com `${CLAUDE_PROJECT_DIR}` e timeouts. **O item `PostToolUse → harness format` foi aposentado** (MD-0014): o format-on-edit deixou de ser materializado no Claude (mantidos o pre-commit e o perfil Antigravity). Em `claude_settings.py`, a assinatura `"harness format"` saiu de `_HARNESS_COMMAND_SIGNATURES` e `"harness decisions"` casa a forma com e sem `--gate` — instalações pré-022 são **substituídas** pelo item novo no merge por-item, sem duplicar. `apply_instructions()` aponta o `.claude/settings.json` do projeto.
- **`GeminiProfile`**: orienta a ponte `context.*` do `settings.json` do Gemini do projeto.
- **`AntigravityProfile` (deixou de ser placeholder):** `hooks_block()` agora emite, via `json.dumps`, o named-hook `harness` do esquema `hooks.json` do Antigravity — `PreToolUse`/`PostToolUse` com `matcher = WRITE_MATCHER` (`write_to_file|replace_file_content|multi_replace_file_content`) e `Stop` sem matcher, cada um apontando `<ABS>/harness agy-hook {pre-tool-use|post-tool-use|stop}` com timeouts 10/30/10. O literal `ABS_PLACEHOLDER = "<ABS>"` permanece no JSON colável; é resolvido na materialização. `apply_instructions()` aponta o `.agents/hooks.json` do projeto e registra que o `init` já o materializa por merge.

### Materialização do `.agents/hooks.json` (`antigravity_hooks.py`) — feature 009 🟢

`materialize_hooks_json(fs, project_path, command_path, profile=None)` é a **rotina única de escrita**, compartilhada por `init` e `upgrade`, com **merge por named-hook**:

1. Resolve o bloco canônico chamando `profile.hooks_block()` (default `AntigravityProfile()`), substitui `<ABS>` por `command_path` e extrai o named-hook `harness` da string JSON (`_resolve_harness_block`).
2. Lê o `.agents/hooks.json` existente se houver e for JSON válido (`_read_existing`: vazio/ilegível → dict vazio); **substitui apenas a chave `harness`**, preservando quaisquer outras chaves de terceiros (idempotência + footprint zero).
3. Cria `.agents/` (`fs.makedirs`) e grava de forma **atômica** (`fs.write_file_atomic`, `indent=2`, `ensure_ascii=False`), sempre **sob `project_path`** (RN-N17). Toda escrita passa pelo `FileSystemPort`.

---

## 8. `core/session` — estado de sessão, encerramento e resume ancorado 🟢

**Arquivos:** `serializer.py` (122), `sinks.py` (77), `errors.py` (7), `offers.py` (96), **`close_flow.py` (399, feature 018)**, **`resume_context.py` (28, feature 021)**.

Papel: persistir e reinjetar o estado da última sessão entre boots do agente. Formato canônico de `.harness/estado-da-sessao.md` = **front-matter YAML** + **corpo Markdown**. Cresceu de 3 para 6 arquivos desde a extração de 2026-06-24 — a unidade que mais mudou no período 010-021.

### `close_flow.py` — orquestração do encerramento, fonte única (feature 018) 🟢

Extraído da borda `main.py` (D-01) para que a CLI (`main.py`, ramo `cmd encerrar-sessao`) e os scripts finos da skill `encerrar-sessao` consumam a **mesma** sequência, sem duplicar lógica (RN-N5, core segue agnóstico ao harness). Todo I/O é injetável (`out`/`err`/`asker`/`is_interactive`), o que permite o mesmo comportamento sob dois regimes: sem TTY (agente, emite _markers_ estruturados) e com TTY (usuário, pergunta `[s/N]`).

Sequência orquestrada por `SessionCloseFlow.run(repo_path, config, ...)`:

1. **Pré-check de trabalho pendente** (`pending_work_paths` — feature 016, estendida na 019 para cobrir `.harness/`): lista os caminhos sujos da working tree, **exceto** o próprio arquivo de estado. **Desde a 024 (MD-0017)**, `conduct_commit_pendente` devolve `bool` (autorização) em vez de sempre abortar: anuncia a contagem à frente e pergunta o desfecho de segunda ordem — com TTY, `s` autoriza encerrar com o trabalho fora do histórico (rastro na narrativa) e `n` aborta; sem TTY, a autorização vem apenas da flag `--com-pendencias` (marker `[HARNESS:COMMIT_PENDENTE ...]` com `acao` de OFERTA). O core segue sem jamais fazer `git add` do trabalho alheio: toda escrita dele é sobre ato próprio.
2. **Gate de narrativa viva** (`narrative_is_stale`): recusa encerrar se a narrativa das 4 seções está vazia OU idêntica à do commit-âncora de partida (sinal de que o agente esqueceu de consolidar). Fail-open só quando não há baseline legível na âncora E a narrativa atual já está preenchida. `conduct_narrativa_pendente` replica a dualidade marker/TTY do passo anterior.
3. **Fechamento propriamente dito** — delega a `CommandService.execute_command("encerrar-sessao", ...)`. **Desde a 024**, `run` resolve antes um **tri-estado `versionar_encerramento`** com default assimétrico por borda: com TTY pergunta `[S/n]` (default afirmativo); **sem TTY o silêncio NÃO autoriza** — versiona só com `--com-commit-encerramento` (par mutuamente exclusivo com `--sem-commit-encerramento`, erro de uso barulhento se ambas). Quando não versiona, repassa `versionar_estado=False` ao serviço e, **após o sucesso e antes da oferta de push**, emite o marker `ENCERRAMENTO_NAO_VERSIONADO` com `motivo` distinguindo esquecimento do agente de recusa explícita — para a oferta de push nunca sugerir publicar achando que o registro entrou junto.
4. **Ofertas de fim de sessão** (`conduct_end_session_offers`, feature 014, ordem **push → upgrade**, RN-10): cada oferta cabível (`offers.push`/`offers.upgrade`) é anunciada por _marker_ sem TTY ou pergunta `[s/N]` com TTY; a falha de uma ação (rede/push/upgrade) avisa e segue sem abortar a outra nem desfazer o encerramento já concluído (RN-02/RN-09).

**3º portão (feature 022), entre o gate de narrativa e o fechamento:** com `decisions.require_registration` ligado, `evaluate_registration_gate` avalia a pendência de registro — o pré-check já forçou o commit do trabalho, então o diff da âncora enxerga a sessão inteira. Quatro desfechos: (a) `aviso` do veredito ecoa em `err` (fail-open barulhento); (b) pendente + `sem_decisao=True` → o escape auditável (RN-03) grava `"Declarado: sem decisão não óbvia nesta sessão (gate de registro)."` na narrativa (`feito`) e segue — não é o core inventando narrativa (RN-N3), é rastro de ato deliberado; (c) pendente + fingerprint **fino** já bloqueado antes (`gate_encerramento_fingerprint == verdict.fingerprint`) → avisa "pendência não sanada" e **encerra mesmo assim** (anti-loop, RF-04); (d) pendente inédito → persiste o fingerprint no estado, emite `conduct_decisao_pendente` (marker `[HARNESS:DECISAO_PENDENTE mudancas=... total=N acao=...]` sem TTY, cap de 20 caminhos; texto legível com TTY) e **aborta com exit 0** — protocolo abortar-e-reexecutar, o core nunca cria a ficha pelo usuário. A identidade fina garante que trabalho novo após o bloqueio **rearma** o portão (pinado por teste-guarda, 023).

🟢 **Sem duplicação CLI↔skill:** `main.py` reexporta `render_offer_markers`, `conduct_end_session_offers`, `pending_work_paths`, `render_commit_pendente_marker`, `conduct_commit_pendente`, **`render_decisao_pendente_marker`, `conduct_decisao_pendente`** (022), **`render_encerramento_nao_versionado_marker`, `conduct_encerramento_nao_versionado`** (024) e `SessionCloseFlow` do core (ver topo do arquivo) — os scripts finos da skill materializada importam os mesmos símbolos, nunca uma cópia paralela.

**`serializer.py` (022):** `parse`/`render` ganharam os campos anti-loop `gate_lembrete_fingerprint`/`gate_encerramento_fingerprint` no front-matter — opcionais (estados pré-022 herdam `None`) e gravados **só quando preenchidos** (sem gate acionado, o arquivo permanece byte-compatível com o formato anterior). `SessionState.close_session` os **zera** no fechamento: fingerprints não vazam para a próxima sessão.

### `resume_context.py` — apêndice do índice de decisões no resume (feature 021) 🟢

Função pura `build_decisions_appendix(fs, index_file, enabled) -> str`, agnóstica ao harness (RN-N5): não decide o gate, apenas o executa. Retorna `""` (não-bloqueante, RN-N4) se `enabled` for falso, se o índice não existir, ou se estiver vazio; caso contrário, devolve um cabeçalho fixo (`"\n\n---\n## Índice de decisões (consulte antes de buscas amplas)\n\n"`) seguido do conteúdo de `.harness/microdecisoes.md`.

Fiação em `main.py` (ramo `cmd resume`, só após `execute_command` produzir o corpo da narrativa): `enabled = config.harness.active_harness == "claude" and config.session.inject_decisions_index` — o gate por harness (**Claude-first**; Gemini/Antigravity adiados, decisão explícita da feature 021) e o flag de opt-out (`SessionSection.inject_decisions_index`, default `True`, seção `[session]` do `harness.toml`) vivem na borda; a função em si é composição pura. Estado ausente é avisado em `stderr` antes da chamada, não dentro dela. O índice é **anexado depois** do estado da sessão no `result_msg`, de modo que, sob truncamento por teto de tamanho do sink (`HookContextSink`, RN-N8), o estado tem precedência e o índice cede.

**Decisão de escopo (D-02 da feature 021):** injeta o **índice** (`.harness/microdecisoes.md`, ~1,7 KB), nunca a pasta `decisoes/` inteira (~31 KB) — que estouraria o teto de 10 KB do sink. As fichas `MD-NNNN` individuais ficam para aprofundamento sob demanda, seguindo os ponteiros do próprio índice.

---

## 9. `core/domain` — modelos, config tipada e cache 🟢

**Arquivos:** `models.py` (137), `config.py` (40), `cache.py` (6). Pydantic v2.

`load_config(fs, config_path="harness.toml") -> HarnessConfig` expõe as seções da configuração. Na feature 007, a seção `[harness]` (`HarnessSection`) ganhou suporte opcional aos campos `upstream_path` e `version` para possibilitar a rotina evolucionária de atualização e avisos passivos de versão defasada no boot.

**Delta 022/023:** `DecisionsSection` ganhou `require_registration: bool = True` (liga o gate de registro; tomls sem o campo herdam `True`, desativável por projeto — sem flag nova para a granularidade, política fixa no core por YAGNI). `SessionState` (`models.py`) ganhou os campos anti-loop `gate_lembrete_fingerprint`/`gate_encerramento_fingerprint` (opcionais, zerados por `close_session`). O literal de versão em `HarnessSection.version` foi de `2.0.1` para **`2.1.1`** (`CORE_VERSION` derivado dele, fonte única — lembrando que `_get_upstream_version` parseia esta linha por regex, o literal não pode virar expressão).

---

## 10. `core/ports` — contratos abstratos 🟢

`fs.py` (`FileSystemPort` com `read_file, write_file, write_file_atomic, exists, list_dir, makedirs, remove, is_dir`), `git.py` (`GitPort`: `get_head_commit, get_remote_commit, commit_paths, list_dirty_paths, list_changed_paths_since, merge_ff_only`), `process.py` (`ProcessPort`: `execute_formatter`, `run_command`).

As assinaturas `is_dir` e `run_command` foram acrescentadas para viabilizar as rotinas de bootstrap físicas e setup do virtual environment no destino. **`list_changed_paths_since(repo_path, ref)` (022):** caminhos alterados entre `ref` e o HEAD (`git diff --name-only <ref> HEAD`) — enxerga o trabalho já **commitado** na sessão (diff da âncora), complemento de `list_dirty_paths` (trabalho não commitado). Read-only; ref inválida levanta `RuntimeError` (RN-N4), cabendo à borda tratar como ausência de baseline (o gate converte em fail-open com aviso).

---

## 11. `adapters` — implementações físicas + drivers 🟢

- **`fs/local.py`** (`LocalFileSystemAdapter`): Implementa operações físicas no disco local, adicionando suporte a `is_dir` via `os.path.isdir`.
- **`git/subprocess.py`** (`SubprocessGitAdapter`): Mapeia os comandos subprocess de `git`.
- **`process/formatter.py`** (`HostFormatterAdapter`): Mapeia chamadas do formatador e implementa `run_command` via subprocess.
- **`mcp/server.py`** (driver MCP — FastMCP "Harness"): Instancia os adaptadores e expõe 4 ferramentas. Incorpora avisos discretos de atualização passiva no boot do servidor MCP.
- **`antigravity/hook_bridge.py`** (driver de ganchos do Antigravity — `AntigravityHookBridge`, feature 009): terceiro driver de entrada, descrito em detalhe na §12.
- **`main.py`** (driver CLI v2.1.1): Argparse expandido para expor os subcomandos `init` (inicialização de workspace físico no destino), `upgrade` (atualização evolucionária não destrutiva) e **`agy-hook <evento>`** (feature 009). Incorpora alertas passivos no topo do boot de comandos da CLI.
  - **Flag `decisions --gate` (features 022/023):** modo hook Stop do Claude. Os informativos da validação/indexação migram para `stderr` e o `stdout` fica reservado ao JSON do hook; **exit sempre 0** (inclusive com grafo inválido — sob `--gate` erros de integridade não derrubam o turno; sem a flag, o comportamento manual/post-merge permanece byte-idêntico, MD-0006). Depois da indexação, avalia o gate: com sessão ativa, `require_registration` ligado, veredito `pendente` e **identidade grossa** inédita (`session.gate_lembrete_fingerprint != verdict.fingerprint_lembrete`), persiste a grossa no estado e emite `{"decision": "block", "reason": <marker DECISAO_PENDENTE + orientação>}` — o soft-block dispara **no máximo uma vez por sessão** (023). Qualquer falha interna vira aviso em `stderr` e libera o turno.
  - **Flag `cmd --sem-decisao` (feature 022):** só para `encerrar-sessao` — declara que não houve decisão não óbvia na sessão; repassada a `SessionCloseFlow.run(..., sem_decisao=...)`, satisfaz o 3º portão deixando rastro auditável na narrativa.
  - **Subcomando `agy-hook` (feature 009):** aceita `event ∈ {pre-tool-use, post-tool-use, stop}` (validado pelo argparse). `agy-hook` foi adicionado à exceção (`args.command not in ("init", "upgrade", "agy-hook")`) tanto do carregamento global de config quanto do check passivo de sync — o gancho de borda **não** usa essa config global; ele a (re)carrega dentro do próprio ramo. Garantia não-bloqueante de borda: TODO o ramo (resolução de config, leitura do stdin, construção de `FormattingService`/`DecisionService`/`AntigravityHookBridge` e a delegação) roda sob `try/except`; o `fallback` exigido por evento (`{"decision": "allow"}` para `pre-tool-use`, senão `{}`) é **pré-computado a partir de `args.event` antes de qualquer operação que possa lançar**, de modo que config corrompida, stdin ilegível ou qualquer outra falha ainda emite o stdout exigido e encerra com **exit 0**. O stdin é lido com guarda de `isatty()`.

---

## 12. `adapters/antigravity` — driver de ganchos do Antigravity (feature 009) 🟢

**Arquivo:** `src/adapters/antigravity/hook_bridge.py` (162 linhas). Terceiro driver de entrada do hexágono, simétrico à CLI e ao servidor MCP: fala o protocolo de ganchos do Antigravity (stdin/stdout JSON camelCase, um formato por evento) e **delega aos serviços de domínio já existentes**, sem ramificar o core por harness (RN-N5 preservada — o domínio nunca conhece `active_harness`).

`AntigravityHookBridge.__init__(fs, formatting_service, decision_service, decisions_dir, decisions_index_file, decisions_header_file, gate_evaluator=None)` recebe `fs` e os serviços por **injeção**; a instanciação concreta fica na borda (`agy-hook` no `main.py`), mantendo o adaptador testável com dublês. **`gate_evaluator` (022, advisory):** callable sem argumentos, montado na borda, que devolve um `GateVerdict` (ou `None` quando o gate não se aplica — sessão inativa ou `require_registration` desligado). No `stop`, pendência vira **aviso em stderr** (`_log`), nunca bloqueio nem reentrada no laço (RN-N26); falha do avaliador é capturada sem descartar a reindexação já feita. O bridge continua sem conhecer git/config.

`handle(event, stdin_text) -> str` despacha por evento e **nunca levanta**: cada ramo passa por `_safe(event, handler, stdin_text, fallback)`, que executa o handler e, em qualquer exceção, loga em `stderr` (erro barulhento, via `_log`) e emite o `fallback` do evento. Evento desconhecido → loga e retorna `{}`. Os três handlers (algoritmo as-built por evento):

- **`pre-tool-use` (captura) → `_handle_pre_tool_use`:** lê `stepIdx` e `toolCall.args.TargetFile` do payload; se ambos presentes, grava o par `{ "<stepIdx>": "<TargetFile>" }` no **mapa de scratch da conversa**. Stdout: `{"decision": "allow"}` — **nunca bloqueia** (jamais `"deny"`).
- **`post-tool-use` (formatação) → `_handle_post_tool_use`:** lê `stepIdx` e `error`; se `stepIdx` presente, `error` vazio e o scratch existe, recupera o `TargetFile` pelo `stepIdx` e chama `formatting_service.format_file(target_file)` (que já honra opt-out/exclusões e **sempre retorna 0**, RN-03). Stdout: `{}`.
- **`stop` (decisões) → `_handle_stop`:** carrega as microdecisões de `decisions_dir`, roda `validate_integrity` (erros são **logados**, nunca bloqueiam nem reentram no laço) e `compile_index(decisions, decisions_index_file, decisions_header_file)` — equivale a `./harness decisions`. Stdout: `{}` (**nunca** `{"decision": "continue"}`).

**Mapa `stepIdx → TargetFile` (scratch):** `_scratch_path(payload)` resolve `<artifactDirectoryPath>/.harness-agy/pending-format.json` (constantes `_SCRATCH_DIRNAME = ".harness-agy"`, `_SCRATCH_FILENAME = "pending-format.json"`); sem `artifactDirectoryPath` no payload → `None` (sem captura). `_read_map` lê via `fs.read_file` e tolera ausência/JSON inválido (→ dict vazio); `_write_map` cria o diretório (`fs.makedirs`) e grava **atomicamente** (`fs.write_file_atomic`). Persistir o caminho no `PreToolUse` e recuperá-lo no `PostToolUse` é a estratégia D-03 (captura + formatação) que preserva a granularidade por-edição sem parsear o `transcript.jsonl`.

**Não-bloqueio e observabilidade:** `_log(message)` escreve sempre em `stderr` (`[harness agy-hook] ...`), jamais em `stdout` (reservado ao contrato). Toda exceção é capturada em dois anéis — no `_safe` (interno) e no ramo `agy-hook` do `main.py` (borda) —, garantindo que o laço do agente Antigravity nunca seja interrompido por falha do harness.

---

## 13. `core/migrate` — conversão do layout copiado para a fonte única (feature 020, NOVO) 🟢

**Arquivo:** `src/core/migrate/service.py` (139 linhas). Décima terceira unidade, ausente na extração anterior (não existia antes da 020).

`MigrateService.migrate(root, dry_run=False, upstream_self=None) -> list` varre `root` (default `~/dev`) por instalações do harness (qualquer subpasta com `harness.toml`) e converte cada uma do **layout copiado** (cópia local do `harness-core` + `.venv` por projeto — o modelo pré-020) para a **fonte única** (shim `./harness` + `.venv` locais que executam o core do upstream via `upstream_path`). Devolve uma lista de resultados por instalação (`status ∈ {migrated, would-migrate, skipped}`).

**Algoritmo por instalação (`_migrate_one`), ordem deliberadamente segura** — instala o executor novo ANTES de remover o antigo, para o projeto nunca ficar sem `./harness` funcional:

1. Lê `upstream_path`/`active_harness` do `harness.toml` do projeto.
2. **Guarda 1:** recusa migrar o próprio `upstream_self` (a fonte real do core — nunca se automigra).
3. **Guarda 2:** recusa migrar se o projeto for uma autoreferência do upstream (upstream aponta para dentro do próprio projeto) ou não tiver `upstream_path` configurado.
4. **Guarda 3:** recusa se o core do upstream não existir no caminho declarado (o shim ficaria quebrado).
5. Detecta o(s) diretório(s) do core a remover: `.harness/harness-core` (layout pós-011) e/ou `harness-core` na raiz (layout legado pré-011 — “o `livro-mfc` carrega os dois”, comentário no código).
6. **Modo `--dry-run`:** só relata `{status: "would-migrate", removes: [...]}`, sem escrever nem remover nada.
7. **Modo real**, na ordem: (a) escreve o shim (`render_shim()`) e o torna executável; (b) instala os ganchos Git via `BootstrapService` (tolera ausência de repo git); (c) materializa `.claude/settings.json` por merge, se `active_harness == "claude"`; (d) remove o campo `version` do `harness.toml` (deixa de fazer sentido sob fonte única — a versão passa a ser sempre a do upstream); (e) **por último**, remove a(s) cópia(s) do core (`_safe_remove_core`, que recusa remover qualquer diretório cujo nome-base não seja literalmente `harness-core` — guarda contra um `remove_tree` malformado apagar a coisa errada).

**Exceção consciente ao footprint per-projeto (RN-N17, documentada no docstring do módulo):** ao contrário de `init`/`materialize`, o `migrate` **atua sobre outros projetos** por design — é ferramenta de manutenção da base já instalada, não uma operação per-projeto isolada. A guarda inegociável (guardas 1 e 2 acima) é nunca remover o core do upstream em si nem cair numa autorreferência circular.

---

## 14. `core/progress` — medidor read-only de entregáveis + exportador kanban (features 026/027, NOVO) 🟢

**Arquivos:** `service.py`, `stages.py`, `render.py`, `kanban.py`. Décima quarta unidade, inteiramente aditiva: nenhuma linha pré-existente do domínio mudou de comportamento.

Papel: responder "**quanto falta**" (o harness já respondia "o quê" e "por quê"). Termômetro 100% **derivado** das fontes de verdade — nunca armazena estado próprio; o serviço é **leitura pura** (invariante pinada por teste: `fs.writes == []` após `measure()`); toda escrita vive na borda CLI.

### `service.py` — `ProgressService.measure() -> Medicao` 🟢

Agrega **cinco fontes** num modelo transitório `Medicao` (Pydantic, jamais persistido):

1. **Ciclo forward**: `.reversa/active-requirements.json` (ativa + pausadas) e os artefatos físicos de `_reversa_forward/*` — estágio físico via `stages.py`, checkboxes por fase e, desde a 027, as **ações individuais** (`AcaoProgresso` com o ID real `T00N` e `criada_em` = primeiro `ts` da ação no `progress.jsonl`, linhas corrompidas silenciosamente puladas, fallback no `started-at`).
2. **Regression-watch**: varredura dos `regression-watch.md`; a marca literal "pendência de reconciliação" (substring, minúsculas) vira **alerta média persistente** — o alerta existe enquanto o problema existir, sem ack.
3. **Microdecisões**: contagem de fichas por listagem e gate reavaliado por `evaluate_registration_gate` em leitura pura (**sem** persistir fingerprint).
4. **Sessão**: estado via `CommandService.load_session`.
5. **Board kanban (027, condicionada a `[progress.kanban].enabled`)**: lido **somente** pelos cards manuais — os em coluna não-`done` viram `Medicao.demandas` (fila de entrada de demandas do mantenedor); cards gerenciados do arquivo jamais são fonte (fluxo unidirecional `actions.md` → board). Board ausente é ausência legítima; presente mas ilegível é **falha real**.

Divergência entre estágio declarado e físico é alerta **alta** persistente; fonte ausente é `n/a` legítimo, fonte ilegível é falha real (contrato de exit 2 na borda).

### `stages.py` — paridade com o skill `reversa-requirements` 🟢

Implementação em código da tabela de **estágio físico** e da regra de contagem de checkboxes que vivem em prosa no skill — ponto único de paridade. `contar_checkboxes` e `listar_acoes` (027 — extrai fase, ID real, descrição e status por linha) usam o **MESMO critério de linha**, o que impede contagem e listagem de divergirem para o mesmo `actions.md`.

### `render.py` — projeções da mesma `Medicao` 🟢

Markdown **sem timestamp e sem caminho absoluto** (o diff do artefato versionado só aparece quando o estado medido muda) — inclui `## Demandas do board` apenas com o kanban habilitado (`- nenhuma` quando vazio); JSON com `aferido_em` (stdout não é versionado, pode carimbar hora).

### `kanban.py` — único módulo do core que conhece o schema do board (027) 🟢

`extrair_manuais(board_json)` (valida topo dict e colunas lista → `ValueError`; filtra os `category == "harness"`) e `render_board(medicao, board_atual)` (projeção determinística + merge preservando manuais). Posse por namespace: ids `hns:<feature>` (resumo), `hns:<feature>:<T00N>` (ação da ativa), `hns:alerta:<origem>`; mapeamento ação `[ ]`→`todo`, `[X]`→`done`, resumo da ativa→`in-progress` (prio 1), pausadas→`todo` (prio 1), alertas→`todo` como `bug` (prio 9 alta / 5 média); `testing` **nunca** recebe card gerenciado; concluídas não geram card (a `Medicao` só carrega a contagem). **Nenhum caminho consulta a hora corrente** — mesmo estado + mesmos manuais → bytes idênticos. Segurança: escreve unicamente o `.json` configurado; **jamais** cria ou toca `.vscode/vscode-kanban.js` (o fork EXECUTA esse arquivo — `workspaces.ts:769`).

### Borda CLI (ramo `progress` no `main.py`) 🟢

Três modos mutuamente exclusivos: **padrão** grava `[progress].file` (default `.harness/progresso.md`) e, com opt-in, o board — ambos atômicos e **write-only-when-changed**, cada um com linha própria no stdout; **`--json`** despeja a `Medicao` com `aferido_em` sem tocar artefato; **`--em-hook`** (pensado para pre-commit) regrava artefato defasado e sai com **1** instruindo o re-commit — alerta grave vira aviso em stderr **sem jamais bloquear** (D-03 da 026: o exit 3 do medidor original de `comentarios-concursos` não foi transplantado; bloqueio duro é exclusivo do portão de encerramento, MD-0018). Falha real (fonte/board ilegível) ecoa `Erro de leitura:` e sai com **2 SEM regravar nada**, preservando os artefatos bons. `--json` e `--em-hook` nunca tocam o board.

---

## Resumo de candidatos a ticket

> Todas as principais pendências abertas no HEAD foram resolvidas.

| #   | Local                   | Sintoma                                                                                 | Severidade sugerida                 | Estado                     |
| --- | ----------------------- | --------------------------------------------------------------------------------------- | ----------------------------------- | -------------------------- |
| T4  | `formatting/service.py` | Blindagens e opt-out chumbados; `[formatting]` do `harness.toml` não alimenta o serviço | Média (config declarada sem efeito) | 🟢 Resolvido (feature 008) |
| T6  | repositório             | Sem lock file; pins apenas `>=`                                                         | Média (reprodutibilidade)           | 🟢 Resolvido (feature 008) |
