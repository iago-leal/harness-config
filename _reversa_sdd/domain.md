# Modelo de Domínio e Glossário (Domain) — harness-core

> Regenerado pelo Detective em 2026-06-24 (Re-extração após a feature 009-hooks-antigravity)
> Nível de Documentação: **Completo**
> **Reconciliação de 2026-06-28** (já incorporada abaixo): cobriu até a feature 018 (`encerrar-sessao` como skill, §2.12-2.15).
> **Reconciliação de 2026-08-11-b** (Detective, pós-feature 028/MD-0022, dirigida): **RN-N41 revisada in-place** (§2.18 — o resume passou a injetar a **visão compacta** `.harness/decisoes-recentes.md`, com fallback autoresolvente para o índice completo); nova seção **2.26** (RN-N56..RN-N58: derivação na mesma passada nas duas bordas + write-only-when-changed; precedência e fallback do apêndice; guidance write-once do init por marcador). Glossário ganhou "Visão Compacta de Decisões". Registrada também a **MD-0021** (abandono da atualização do vault Obsidian no encerramento — decisão operacional, sem código no core). Core 2.6.0.
> **Reconciliação de 2026-07-15** (Detective, pós-MD-0014 e features 022-023): novas seções **2.19** (MD-0014, aposentadoria do format-on-edit no perfil Claude), **2.20** (022, gate de registro obrigatório de microdecisões) e **2.21** (023, dupla identidade do lembrete). Glossário ganhou os conceitos do gate; RN-N42..RN-N47 novas.
> **Reconciliação de 2026-07-05** (Detective, pós-features 019-021, esta rodada): novas seções **2.16** (019, pré-check de pendência restrito ao arquivo de estado), **2.17** (020, fonte única de execução + `harness migrate`) e **2.18** (021, resume ancorado no índice de decisões). **Achado factual relevante:** o plano original da 020 previa remover `upgrade_project`/`SyncService` e tornar `upgrade` um no-op (ver `_reversa_forward/020-fonte-unica-e-hooks/actions.md` T008/T009/T013/T015/T016) — mas a varredura de implementação revelou que ambos sustentam a **oferta de upgrade ao encerrar** (feature 014, `session/offers.py`), e o mantenedor **desescopou** essa remoção em 2026-07-01 para uma feature futura (ainda não numerada — a candidata "021" virou o hook de busca ancorada, feature diferente). RN-N19/RN-N20/RN-N21 abaixo foram **revisadas**, não removidas: `upgrade`/`sync`/checagem de versão seguem vivos e funcionais no código atual.

Este documento define o glossário semântico e as regras de domínio que regem o comportamento e as restrições do núcleo Python do `harness`. Reflete o estado ATUAL do repositório, após o purge do legado `claude-config/` (commit `5624f78`), a migração de estado e decisões para `.harness/`, o suporte a bootstrapping evolucionário (feature 007), a reprodutibilidade e configuração dinâmica de formatação (feature 008), os ganchos de ciclo de vida do Antigravity via driver de borda (feature 009), a materialização de `encerrar-sessao` como skill versionável (feature 018), a oferta de commit estendida a `.harness/` (feature 019), a fonte única de execução com `harness migrate` (feature 020), o resume ancorado no índice de decisões (feature 021), a aposentadoria do format-on-edit no perfil Claude (MD-0014), o gate de registro obrigatório de microdecisões com dupla identidade anti-loop (features 022-023), o consentimento para escrita no git ao encerrar (024), a aposentadoria do soft-block do Stop (025), o medidor de progresso e o exportador kanban (026-027) e a visão compacta de decisões no resume (feature 028, MD-0022).

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
- **Formatador de Arquivos (`Formatter`):** Executável local ou global (`ruff`/`prettier`/`rustfmt`) invocado para manter a padronização, sempre de modo não-bloqueante. **Desde MD-0014, o disparo on-edit existe só no Antigravity** (`agy-hook post-tool-use`); no Claude, restam o git pre-commit e o uso manual (`harness format`) — o gatilho `PostToolUse` foi aposentado.
- **Opt-out de Formatação:** Recusa de formatação automática ativada pela presença do arquivo `.no-autoformat` na pasta do arquivo ou em qualquer diretório superior.
- **Documentação Standalone (`harness-docs.html`):** Arquivo HTML único, autossuficiente e offline, contendo a superfície da CLI, as regras de domínio vigentes e o andamento dos checkpoints do Reversa.
- **Repositório Upstream (`upstream_path`):** Caminho físico absoluto ou relativo configurado na seção `[harness]` do repositório de destino que aponta para o diretório original do core. Até a feature 019, servia de base para evolução (`upgrade`, ainda ativo) e checagem de atualizações; a partir da feature 020, é também a **âncora única de execução** sob a fonte única — o shim instalado no destino executa o core diretamente a partir deste caminho.
- **Versão Local Instalada (`version`):** String contendo o identificador semântico de versão física do Harness instalado no repositório de destino. Continua gravada pelo `init`/`upgrade` legados (via `InitializationService`); a feature 020 **não** a removeu do fluxo real (a remoção estava planejada, mas foi desescopada — ver nota de reconciliação no topo do arquivo).
- **Shim de Execução (`render_shim()`):** Conteúdo canônico do wrapper `harness` sob a fonte única (feature 020): resolve `upstream_path` do `harness.toml` do próprio projeto, muda para a raiz do projeto (`cd`) e executa o Python/`main.py` do **upstream**, repassando `$@` e o código de saída. Erro barulhento (nomeado, exit ≠ 0) se o upstream estiver ausente ou inacessível. Reutilizado por `init` (escrita direta) e por `migrate` (conversão de instalações existentes).
- **Fonte Única de Execução:** Modelo em que o código do core (e sua `.venv`) reside **apenas** no repositório upstream; instalações-alvo recebem só o shim + a árvore de estado `.harness/` (decisões, índice, sessão) + `harness.toml` (com `upstream_path`, sem cópia de código). Introduzido pela feature 020 para o **novo** `init`; instalações já existentes no layout antigo (cópia local do core) permanecem funcionais via `upgrade` até serem convertidas por `migrate`.
- **`MigrateService` / `harness migrate`:** Ferramenta de manutenção da base de instalações (feature 020) que varre uma raiz (default `~/dev`) por projetos com `harness.toml` e converte cada um do layout copiado para a fonte única — shim, ganchos, settings do Claude, remoção da cópia local do core (nessa ordem, para nunca deixar o projeto sem executor). Suporta `--dry-run`. Única exceção deliberada ao footprint per-projeto (RN-N17): atua sobre _outros_ projetos por design.
- **Apêndice de Decisões no Resume:** Bloco de texto anexado ao contexto reinjetado pelo `cmd resume`, quando o harness ativo é o Claude e `session.inject_decisions_index` está ligado (default). Desde a 028, a fonte primária é a **visão compacta** (`.harness/decisoes-recentes.md`); o índice completo (`.harness/microdecisoes.md`) é o fallback autoresolvente quando a compacta ainda não existe. Ancora a busca do agente antes de varreduras amplas do repositório (feature 021, revisada pela 028).
- **Visão Compacta de Decisões (`.harness/decisoes-recentes.md`):** Segundo artefato DERIVADO do grafo de decisões (feature 028, MD-0022), gerado na mesma passada do índice por todas as bordas que indexam (CLI, ponte Antigravity e, desde a MD-0023, a tool MCP): contagem total, ponteiros de consulta (índice completo, pasta de fichas, `./harness decisions`) e as K fichas mais recentes (`decisions.compact_index_size`, default 10) só com títulos, sem backlinks — custo de injeção ~constante, independente do tamanho do acervo. Nunca editada à mão; escrita condicionada a mudança.
- **Gate de Registro de Microdecisões (feature 022):** Mecanismo que impede sessões com trabalho substantivo de terminarem sem microdecisão registrada. Avaliação **pura** em `core/decisions/gate.py` (`evaluate_registration_gate`): universo = diff da âncora (`list_changed_paths_since`) ∪ working tree sujo (`list_dirty_paths`), menos o arquivo de estado, o índice e o cabeçalho de decisões; **pendente** quando há mudanças e nenhuma ficha `MD-*.md` tocada. Sem filtro por tipo de arquivo (repositórios documentais contam). Ligado por `decisions.require_registration` (default `True`).
- **Veredito do Gate (`GateVerdict`):** Value-object transitório com `pendente`, `mudancas`, `fichas_tocadas`, os dois fingerprints e `aviso` (preenchido no fail-open). Não persistido — só os fingerprints sobrevivem, nos campos anti-loop do `SessionState`.
- **Dupla Identidade do Gate (feature 023):** Dois fingerprints com semânticas opostas. **Fina** (`compute_fingerprint` = `sha1(âncora+HEAD+sujos ordenados)`): usada pelo 3º portão do encerramento — trabalho novo rearma a garantia. **Grossa** (`compute_lembrete_fingerprint` = `sha1(âncora)`): usada pelo lembrete do Stop — estável na sessão, o soft-block dispara no máximo uma vez por sessão. Sem relógio em nenhuma das duas.
- **Marker `DECISAO_PENDENTE`:** Terceiro marker estruturado da família `COMMIT_PENDENTE`/`NARRATIVA_PENDENTE` (`[HARNESS:DECISAO_PENDENTE mudancas="..." total=N acao="..."]`, cap de 20 caminhos), emitido sem TTY pelo protocolo abortar-e-reexecutar; com TTY vira orientação legível. Contrato em `_reversa_forward/022-hook-registro-decisoes/interfaces/decisao-pendente-marker.md`.
- **Escape `--sem-decisao`:** Declaração explícita, na chamada de `encerrar-sessao`, de que não houve decisão não óbvia na sessão. Satisfaz o gate deixando rastro auditável na narrativa (`feito`) — não é o core inventando narrativa (RN-N3), é registro de ato deliberado.

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
  - `.harness/microdecisoes.md` é DERIVADO pelo `./harness decisions` (hook `Stop`, desde a 022 na forma `decisions --gate`) a partir das fichas; o cabeçalho do arquivo declara "Não edite à mão".
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
- **RN-N19: Inicialização de Repositório Alvo (Bootstrap)** 🟡 **[REVISADA pela feature 020, ver §2.17 RN-N36]**
  - Origem: `.harness/harness-core/src/core/bootstrap/init_service.py`
  - Descrição histórica (válida até a feature 019): o comando `init` realizava a replicação física do wrapper e do core para um diretório de destino, ignorando pastas de desenvolvimento local e cache (`.git`, `.venv`, etc.), inicializava uma `.venv` no destino e instalava os ganchos locais Git. **A partir da feature 020, este NÃO é mais o comportamento do `init`** — ver RN-N36. Mantida aqui só como registro histórico do que instalações antigas (pré-020, ainda não convertidas por `migrate`) carregam no disco.
- **RN-N20: Evolução Não-Destrutiva (Upgrade)** 🟢 **[ainda ATIVA — remoção planejada na 020 foi desescopada, ver nota no topo do arquivo]**
  - Origem: `.harness/harness-core/src/core/bootstrap/init_service.py`
  - O comando `upgrade` **continua** atualizando fisicamente o código e o wrapper no destino a partir de seu upstream, preservando intactas as pastas locais `.reversa/` (dados de engenharia reversa) e `.harness/decisoes/` (metadados arquiteturais). **A partir da feature 012**, a rematerialização dos artefatos de IDE no `upgrade` roda via **subprocesso do python de destino** (subcomando interno `materialize`), com o código recém-copiado e nunca com os módulos antigos em memória (corrige o bug de materialização stale). O `upgrade` aceita `--force`, que ignora a comparação de versão e força recópia + rematerialização. Serve hoje sobretudo instalações que ainda não foram convertidas para a fonte única (§2.17); coexiste com `harness migrate`, que converte em vez de recopiar.
- **RN-N21: Checagem Passiva de Atualização e Detecção Resiliente de Versão** 🟢 **[ainda ATIVA — mesma ressalva de RN-N20]**
  - Origem: `.harness/harness-core/src/core/sync/service.py`, `.harness/harness-core/src/core/bootstrap/init_service.py`, `.harness/harness-core/src/main.py`
  - No boot da CLI e do servidor MCP, realiza-se uma comparação passiva rápida e estritamente local de versão local vs versão do upstream configurado. Se o upstream estiver à frente, exibe um alerta de nova versão disponível, de forma não-bloqueante e tolerante a erros de leitura. **A partir da feature 012**, a leitura da versão do upstream varre caminhos-candidato (`CORE_CONFIG_CANDIDATE_RELPATHS` em `layout.py`: layout canônico `.harness/harness-core/...` + legado da raiz), de modo a sobreviver a relocações do core no upstream. No `upgrade` (diferente do alerta passivo, que é silencioso), uma versão **indeterminada** faz o comando **abortar barulhento** (erro claro + instrução de `init`, exit ≠ 0) em vez de cair num fallback que igualaria a versão local e geraria um upgrade fantasma. `SyncService`/o alerta passivo sustentam a `UpgradeOffer` do encerramento de sessão (feature 014, §2.14/RN-N33) — é essa dependência que motivou o desescopo da remoção planejada pela 020.

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

### 🩹 2.12 Capacidade de Sessão Materializada no Bootstrap (feature 010 → skill versionável ✨f018)

> Evolução do mecanismo de entrega: 010 nasceu como slash command/workflow `.md` que delegava ao binário; 017 corrigiu o caminho do Antigravity (plural → singular); **✨f018** trocou a _forma_ do artefato — de command/workflow para **skill versionável** (`SKILL.md` + `scripts/`) que consome o core testado. A lógica de fechamento nunca saiu do core (RN-N5). Motivação da 018: no Antigravity, slash commands/workflows locais não são reconhecidos; skills ativam por contexto.

- **RN-N28: Materialização Incondicional da Capacidade de Sessão** 🟢 — ✨f018: de slash command para skill
  - Origem: `.harness/harness-core/src/core/install/session_skills.py`, `.harness/harness-core/src/core/bootstrap/init_service.py`
  - `materialize_session_skills(fs, project_path, profiles=None)` é a **rotina única** que entrega a capacidade `encerrar-sessao` na IDE do agente. É chamada por `initialize_project` e por `upgrade_project` **sempre** — diferente de `materialize_hooks_json`, **não** há gate por `active_harness` (D-03): a capacidade deve aparecer para o Claude **e** para o Antigravity em qualquer instalação. ✨f018 mudou a forma do artefato: em vez de gravar um `.md` que delegava ao binário (`materialize_session_commands`, **aposentado**), grava a **árvore agnóstica de uma skill versionável** — `SKILL.md` (front-matter com `name`/`description`/`version`) + `scripts/` (entrada fina que consome o core testado, RN-N33) — lida dos assets do core (`src/core/install/assets/skills/encerrar-sessao/`, **mesmos bytes** para todos os harnesses) e copiada sob `<project_path>/<skills_dir>/encerrar-sessao/`. Itera os perfis, grava cada arquivo de forma atômica via `write_file_atomic` e cria os diretórios; toda escrita ocorre sob `project_path` — footprint global zero preservado (RN-N17; o materializador segue coberto pelo teste de footprint, ressalva de 006/W003). Não-destrutivo e idempotente: a árvore tem nome próprio (`encerrar-sessao`), de modo que arquivos de terceiros nos diretórios não são lidos nem tocados; reexecutar `init`/`upgrade` converge ao mesmo resultado. A skill **não reimplementa** o fechamento — os scripts consomem o `SessionCloseFlow` do core (RN-N33), preservando RN-N5. A migração remove os artefatos legados (command/workflow `.md`) via `stale_session_command_paths` (RN-N29).
- **RN-N29: Superfície de Skill Encapsulada no Perfil** 🟢 — ✨f018: `session_command_artifact` → `skills_dir`
  - Origem: `.harness/harness-core/src/core/install/harness_profiles.py`
  - O que varia por harness passou a ser só o **diretório de skills**, exposto por `HarnessProfile.skills_dir() -> str | None`, sem `if active_harness` no serviço (RN-N5 reforçada). `ClaudeProfile` devolve `.claude/skills`; `AntigravityProfile` devolve `.agents/skills` (plural — ativação **semântica** por contexto, ao contrário do workflow legado, que vivia em `.agent/workflows` singular); `GeminiProfile` devolve `None` (sem superfície de skill — é pulado na escrita da árvore, mas ainda tem seus órfãos limpos). O método `session_command_artifact(command_path)` da 010/017 foi **removido**: como a árvore da skill é única (mesmos bytes), não há conteúdo por-harness a encapsular, só o prefixo. A limpeza dos órfãos legados continua no perfil via `stale_session_command_paths()`: `ClaudeProfile` → `.claude/commands/encerrar-sessao.md`; `AntigravityProfile` → `.agent/workflows/encerrar-sessao.md` (singular, 017) **e** `.agents/workflows/encerrar-sessao.md` (plural, pré-017); só o arquivo nomeado, nunca o diretório (não-destrutivo). 🟡 A ativação semântica da skill no Antigravity não é verificável localmente; validar contra o Antigravity real quando disponível (amarelo herdado de 009/017/W009).

### 🔁 2.13 Upgrade Resiliente e Materialização com Código Novo (feature 012)

- **RN-N30: Materialização Local por Função Única, com Código Recém-Copiado no Upgrade** 🟢
  - Origem: `.harness/harness-core/src/core/install/local_apply.py`, `.harness/harness-core/src/core/bootstrap/init_service.py`, `.harness/harness-core/src/main.py`
  - `apply_local_materializers(fs, project_path, command_path, active_harness)` é a **função única** que aplica os materializadores de IDE: `materialize_session_skills` sempre (RN-N28, ✨f018 — antes era `materialize_session_commands`), `materialize_hooks_json` só quando `active_harness == "antigravity"` (RN-N27) e `materialize_claude_settings` só quando `active_harness == "claude"` (feature 016). O `init` a chama **in-process** (o código em execução já é o do upstream, fresco); o `upgrade` a invoca via **subprocesso do python de destino** pelo subcomando interno `materialize` — garantindo que a materialização rode com o código recém-copiado, nunca com os módulos antigos em memória. Antes do subprocesso, o `upgrade` guarda a presença da venv e do `main.py` de destino, abortando barulhento com instrução de `init` se o core estiver incompleto. Toda escrita segue sob `project_path` (RN-N17 preservada).
  - **Janela conhecida (🟡):** o primeiro `upgrade` de um alvo ainda na versão anterior materializa com o código antigo (em execução), porque o fix só passa a valer com o código novo já carregado; do bump em diante o mecanismo é correto.

### 🔖 2.14 Versionamento do Encerramento de Sessão (feature 013)

- **RN-N31: Encerramento Versiona o Estado num Commit Isolado — Quando Versiona** 🟢 — **revisada pela 024/MD-0017 (§2.22): o versionamento deixou de ser incondicional e passou a depender de consentimento (RN-N48); o restante da regra vale intacto quando o consentimento existe**
  - Origem: `.harness/harness-core/src/core/commands/service.py`, `.harness/harness-core/src/adapters/git/subprocess.py`
  - Ao `encerrar-sessao` **com versionamento autorizado**, o comando captura a âncora (HEAD de **trabalho**) **antes** de qualquer escrita (RN-07), grava o estado e então cria um commit contendo **exclusivamente** o `state_file`, por cima do trabalho — via `GitPort.commit_paths(repo_path, [state_file], msg)`, que faz `git add -- <paths>` (nunca `git add -A`) e `git commit`. A âncora segue apontando para o trabalho; o commit de encerramento fica por cima e nunca se torna a âncora. A mensagem é `chore(sessao): encerrar sessão <feature>; âncora <ancora>` (limpa, sem co-autoria) e a saída do comando reporta os **dois** hashes. Vale para CLI **e** MCP, que compartilham o `CommandService`. Antes da 013 o registro de encerramento ficava como mudança pendente no working tree.
- **RN-N32: Commit pela Porta e Falha Barulhenta** 🟢
  - Origem: `.harness/harness-core/src/core/ports/git.py`, `.harness/harness-core/src/core/commands/errors.py`
  - O domínio versiona apenas pela porta `GitPort.commit_paths` (RN-N5 preservada; nenhum `subprocess`/`git` direto no serviço de comandos). Se o commit não puder ser criado, o comando levanta `SessionCommitError` (erro nomeado, exit ≠ 0), sem devolver sucesso e **sem reverter** o `state_file` já salvo (RN-N4 estendida ao fechamento).

### 🪟 2.15 Orquestração de Encerramento Extraída para o Core (feature 018)

- **RN-N33: Fluxo de Encerramento como Serviço Único, Consumido por CLI e Skill** 🟢
  - Origem: `.harness/harness-core/src/core/session/close_flow.py`, `.harness/harness-core/src/main.py`, `.harness/harness-core/src/core/install/assets/skills/encerrar-sessao/scripts/`
  - A orquestração do `encerrar-sessao` — pré-check de trabalho pendente (016) → fechamento via `CommandService` → ofertas de fim de sessão (014: push → upgrade) — foi **extraída** da borda `main.py` para `SessionCloseFlow.run(repo_path, config, *, out, err, asker, is_interactive) -> int` no core (D-01). Fonte **única** consumida por duas bordas: a CLI faz `sys.exit(SessionCloseFlow(fs, git, process).run(...))`, e o script fino da skill (RN-N28) compõe o mesmo serviço (`RegenService` → `SessionCloseFlow`) — sem duplicar lógica (DRY). Todo IO é injetável (markers estruturados sem TTY, perguntas `[s/N]` com TTY), e os helpers da 014/016 (`pending_work_paths`, `conduct_commit_pendente`, `render_*`, `conduct_end_session_offers`) migraram para o módulo e são **reexportados** por `src.main` (compatibilidade dos testes da 014/016). O serviço continua agnóstico ao harness (RN-N5): o prefixo por harness vive no perfil (`skills_dir`), não no fluxo. Estado malformado e falha de commit do estado encerram **barulhento** (exit 1), nunca em silêncio (RN-N4/RN-N31/N32 preservadas).
  - **Scripts finos da skill (contrato, 🟢):** `scripts/_bootstrap.py` resolve a raiz via `git rev-parse --show-toplevel`, localiza `.harness/harness-core` e o torna importável sob o venv do core (teste por `sys.prefix`/`CoreNotFoundError`); `scripts/encerrar_sessao.py` roda da raiz, compõe `RegenService(process).run(...)` (regenera os artefatos derivados; falha barulhenta aborta **antes** de fechar) e então `SessionCloseFlow(...).run(...)`, sem reimplementar regra. Core ausente/não-importável → falha barulhenta (exit ≠ 0 + mensagem orientadora), nunca silenciosa.

### 🧹 2.16 Pré-check de Pendência Restrito ao Arquivo de Estado (feature 019)

> A oferta de commit pendente do `encerrar-sessao` (016) mascarava **todo** o diretório `.harness/` sob a premissa de que o fechamento o versionava por completo. A premissa era falsa: o commit de fechamento versiona só `state_file` (RN-N31). Decisões e o índice regenerado ficavam num vão sem oferta e sem captura, exigindo commit manual. Esta feature estreita o filtro do pré-check.

- **RN-N34: Pendência Restrita ao Arquivo de Estado, Não ao Diretório** 🟢 — revisa a implementação de `pending_work_paths`
  - Origem: `.harness/harness-core/src/core/session/close_flow.py:pending_work_paths`
  - `pending_work_paths(git, repo_path, session_file)` exclui da lista de trabalho pendente **apenas** o caminho exato de `session_file` (ex.: `.harness/estado-da-sessao.md`), nunca o diretório `.harness/` inteiro. Consequência direta: decisões sujas (`.harness/decisoes/MD-*.md`) e o índice regenerado (`.harness/microdecisoes.md`) passam a **entrar** na oferta de commit (marker `COMMIT_PENDENTE` sem TTY; listagem `[s/N]` com TTY) em vez de ficarem invisíveis. O commit de fechamento em si (RN-N31) é intocado — muda só o que o pré-check considera pendente.
  - Achado que motivou a correção: o smoke test com **git real** (não `FakeGit`) revelou que `git status --porcelain` colapsa um subdiretório inteiro numa única linha quando ele é totalmente untracked — um mock que já devolvesse a lista expandida mascarava esse comportamento (ver `dependencies.md`/memória `smoke-git-real-vs-mock-porcelain`).
- **RN-N35: Cache de Sync Explicitamente Ignorado** 🟢
  - Origem: `.harness/harness-core/src/core/domain/layout.py:SYNC_CACHE_GITIGNORE_ENTRY`, `.harness/harness-core/src/core/bootstrap/init_service.py`
  - Como o pré-check deixou de proteger o diretório `.harness/` inteiro, o cache de runtime `.harness/sync-cache.json` precisa ser ignorado explicitamente no `.gitignore` do projeto-alvo (o `init` grava a entrada) para não ser oferecido como pendência — o core nunca usa denylist própria, confia no `.gitignore`.

### 🧬 2.17 Fonte Única de Execução e Migração da Base Instalada (feature 020)

> Antes da 020, cada `harness init` replicava fisicamente o `harness-core` + uma `.venv` própria no destino (RN-N19 histórica) — medição real em `~/dev`: 17 instalações, ~1,83 GB, ~97% dos quais venvs duplicadas. A feature colapsa a duplicação: o `init` passa a instalar só um **shim** que executa o core a partir do **upstream**; o código-fonte + venv residem exclusivamente lá. Junto, corrige dois materializadores que eram destrutivos (hooks do Claude por-evento, hooks git incondicionais) e adiciona `harness migrate` para converter a base já instalada. **Achado de reconciliação:** o plano original também previa aposentar `upgrade`/`sync`/`version` (tornando `upgrade` um no-op) — isso foi **desescopado** em 2026-07-01 porque ambos sustentam a `UpgradeOffer` do encerramento de sessão (RN-N33/§2.14); a descontinuação fica para uma feature futura, ainda não numerada.

- **RN-N36: Fonte Única de Execução no `init`** 🟢 — substitui o comportamento histórico de RN-N19
  - Origem: `.harness/harness-core/src/core/bootstrap/init_service.py:InitializationService.initialize_project`, `.harness/harness-core/src/core/bootstrap/shim.py`
  - `init` **não copia mais** o `harness-core` nem cria uma `.venv` no destino. Grava o **shim** (`render_shim()`, executável) no lugar do wrapper, cria a árvore `.harness/` (decisões, índice, estado — só se ausentes, não sobrescreve), grava `harness.toml` com `upstream_path` (sem `version` para instalações novas), instala os ganchos Git **in-process** (o código em execução já é o do upstream, sem venv de destino para um subprocesso) e materializa os artefatos de IDE. O core executável (código + venv) passa a residir **exclusivamente** no upstream; o shim o invoca com o cwd do projeto-alvo.
- **RN-N37: Footprint de Escrita Per-Projeto Preservado Sob Leitura Externa** 🟢 — preserva RN-N17 com premissa revisada
  - Origem: `_reversa_forward/020-fonte-unica-e-hooks/requirements.md#4` (RN-02), `.harness/harness-core/tests/test_footprint.py`
  - Executar o core do upstream **lê** código de fora do repositório-alvo, mas toda **escrita** de estado (sessão, decisões, índice, cache de sync) permanece sob o `.harness/` do projeto, resolvida pelo cwd do processo. O upstream é um repositório-fonte **versionado** (não um diretório de fornecedor externo nem estado global invisível) — a preocupação original do ADR-0013 permanece atendida; o teste de footprint continua válido sem alteração.
- **RN-N38: Migração da Base Instalada via Comando Dedicado (`harness migrate`)** 🟢 — feature NOVA, sem equivalente anterior
  - Origem: `.harness/harness-core/src/core/migrate/service.py:MigrateService`
  - `harness migrate [root] [--dry-run]` varre uma raiz (default `~/dev`) por projetos com `harness.toml` no layout copiado e converte cada um para a fonte única: shim → ganchos Git não-destrutivos → settings do Claude por merge → remoção do campo `version` → remoção da(s) cópia(s) do core **por último** (ordem que nunca deixa o projeto sem executor). Guardas: nunca migra o próprio upstream nem uma autorreferência circular; recusa se o core do upstream não existir; `_safe_remove_core` recusa remover qualquer diretório cujo nome-base não seja `harness-core`. **Exceção consciente ao footprint per-projeto** (RN-N17): atua sobre _outros_ projetos por design, é ferramenta de manutenção da base, não uma operação isolada. 🟡 Não executado nos 17 projetos reais até esta reconciliação — é ação separada do mantenedor, deliberadamente não automática.
- **RN-N39: Merge Não-Destrutivo de Hooks do Claude e Ganchos Git** 🟢 — revisa parcialmente RN-N15 (hooks Git) e estende RN-N27 (padrão de merge) ao `.claude/settings.json`
  - Origem: `.harness/harness-core/src/core/install/claude_settings.py`, `.harness/harness-core/src/core/bootstrap/service.py`
  - A materialização de `.claude/settings.json` passa a mesclar **por-item dentro do array de cada evento** (identifica o item do harness pela assinatura no `command`; substitui se presente, insere se ausente; preserva os demais itens do mesmo evento) em vez de substituir o array inteiro do evento (bug anterior). Os ganchos Git (`install_hooks`) deixam de reescrever incondicionalmente: hook ausente → cria; hook do harness (identificado por assinatura) → atualiza; hook alheio sem a assinatura → **preservado**, encadeado antes do trecho do harness. Ambos passam a invocar o **shim** em vez do python local.
- **RN-N40: Versão Canônica Única do Core** 🟢
  - Origem: `.harness/harness-core/src/core/domain/config.py:CORE_VERSION`
  - `CORE_VERSION` (usado no help da CLI e em `InitializationService.current_version`) deriva de `HarnessSection().version`, literal `"2.0.0"` — fonte única, sem valores chumbados divergentes entre `main.py` e o serviço de bootstrap. Bump de `1.3.0` para `2.0.0` reflete que o contrato de instalação mudou de forma incompatível (sem cópia do core, sem venv própria, shim).

### 🧭 2.18 Resume Ancorado em Decisões (feature 021, revisada pela 028)

> A reinjeção de contexto no boot (`SessionStart` → `cmd resume`) entregava só a narrativa da sessão. A 021 acrescentou o índice de decisões ao mesmo apêndice — medição da época: `estado-da-sessao.md` = 4,2 KB, `microdecisoes.md` = 1,7 KB, `decisoes/` (12 fichas) = 31,2 KB. A **028 (MD-0022)** constatou que o próprio índice cresce linearmente com as fichas (22 e subindo, com backlinks) e o substituiu na injeção pela **visão compacta** de custo ~constante, mantendo o índice completo a um passo de leitura, sob demanda.

- **RN-N41: Apêndice de Decisões no Resume — Visão Compacta com Fallback (Claude-first)** 🟢 — **revisada pela 028/MD-0022** (redação original injetava o índice integral)
  - Origem: `.harness/harness-core/src/core/session/resume_context.py:build_decisions_appendix`, `.harness/harness-core/src/main.py` (ramo `cmd resume`)
  - Ao processar `cmd resume`, se `active_harness == "claude"` e `session.inject_decisions_index` (default `True`) estiverem ambos satisfeitos, o resultado reinjetado ganha um apêndice anexado **depois** do estado da sessão (cede sob truncamento do teto de 10.000 caracteres do `HookContextSink`, RN-N8 — o estado tem precedência). **Desde a 028, a fonte primária é a visão compacta** (`decisions.compact_file`, cabeçalho `## Decisões recentes (índice completo sob demanda)`); o índice integral não é mais injetado como comportamento vigente.
  - **Fallback autoresolvente (028):** compacta ausente/vazia + índice presente → injeta o índice integral sob o cabeçalho antigo, com `Aviso:` em stderr orientando a regeneração ("rode `./harness decisions` ou aguarde o próximo fim de turno" — a compacta nasce sozinha na primeira derivação); ambos ausentes → só o estado, com aviso. Nunca bloqueante, exit 0 sempre (RN-N4 estendida). O gate por harness segue fixado no código; só o opt-out (`inject_decisions_index`) é configurável.
  - Escopo por harness inalterado desde a 021: **só Claude**. Gemini e Antigravity permanecem adiados por decisão explícita do mantenedor.
  - Decisão de escopo (021, refinada pela 028): nunca injetar a pasta `decisoes/` inteira; agora tampouco o índice integral — contagem + ponteiros + K títulos recentes bastam para ancorar; o aprofundamento segue os ponteiros (compacta → índice → fichas).
  - Função pura, agnóstica ao harness (RN-N5 preservada): a composição do apêndice não decide o gate, só o executa; habilitação (harness + flag) e avisos de fallback são calculados na borda (`main.py`).

### ✂️ 2.19 Aposentadoria do Format-on-Edit no Perfil Claude (MD-0014)

> Em máquina com dezenas de projetos sob `~/dev`, o gatilho on-edit (`PostToolUse → harness format`) se tornou dano em vez de higiene: herdado inclusive pelo `.claude/settings.json` da pasta-mãe, reescrevia arquivos a cada `Write|Edit` em diretórios onde nenhuma formatação fora solicitada — reincidência do incômodo que já havia motivado a descontinuação do `format-on-edit.sh` global do legado. A remoção é na FONTE (o perfil), para que `init`/`upgrade` futuros não reintroduzam o hook.

- **RN-N42: Format-on-Edit é Opt-in Manual no Claude** 🟢 — reverte parcialmente o comportamento do ADR 0002
  - Origem: `.harness/harness-core/src/core/install/harness_profiles.py:ClaudeProfile.hooks_block`, `.harness/harness-core/src/core/install/claude_settings.py:_HARNESS_COMMAND_SIGNATURES`
  - `ClaudeProfile.hooks_block()` emite apenas `SessionStart → cmd resume` e `Stop → decisions --gate`; o item `PostToolUse → harness format` **não é mais materializado**. A assinatura `"harness format"` saiu de `_HARNESS_COMMAND_SIGNATURES` — consequência deliberada: um item legado num projeto-alvo pré-MD-0014 deixa de ser reconhecido como "do harness" e é **preservado como se fosse de terceiro** (a poda ativa foi descartada por ser superfície destrutiva sem demanda; a limpeza dos materializados existentes foi manual). `harness format`, o `FormattingService` e o disparo on-edit do **Antigravity** permanecem intactos — o pre-commit dispara só no commit, ato deliberado.

### 🚧 2.20 Gate de Registro Obrigatório de Microdecisões (feature 022)

> Microdecisões eram puladas em algumas sessões: o trabalho terminava, a sessão fechava e a decisão não virava ficha. A feature cria o gate de registro com **enforcement híbrido**: garantia dura no encerramento, lembrete único no fim de turno do Claude, advisory no Antigravity. Fundamento: o canal do `Stop` do Claude que alcança o modelo é apenas `{"decision":"block","reason":...}` — stdout com exit 0 não é reinjetado —, logo o "lembrete não-bloqueante" só existe como soft-block limitado por fingerprint (MD-0015).

- **RN-N43: Pendência de Registro por Sinal Físico, Avaliação Pura** 🟢
  - Origem: `.harness/harness-core/src/core/decisions/gate.py:evaluate_registration_gate`
  - A pendência deriva **só de sinal físico verificável**: universo = diff da âncora (`GitPort.list_changed_paths_since`, novo — enxerga o trabalho já commitado, indispensável porque o pré-check da 019 força commit antes do fechamento) ∪ working tree sujo (`list_dirty_paths`); excluem-se o arquivo de estado, o índice, o cabeçalho de decisões e a visão compacta (`decisions.compact_file`, acrescentada pela MD-0025 — lacuna latente desde a feature 028, tornada determinística quando o encerramento passou a derivar a compacta); fichas = caminhos sob `decisions.dir` casando `^MD-.*\.md$`; `pendente = mudanças ∧ ¬fichas`. **Sem filtro por tipo de arquivo** (repositórios documentais contam — decisão explícita do clarify). Nunca metadado auto-declarado, nunca detecção semântica, nunca parse de transcript (descartados na MD-0015). O módulo é agnóstico ao harness (RN-N5): não conhece `active_harness` nem decide COMO interceptar.
- **RN-N44: Enforcement em Duas Políticas — Portão Duro no Encerramento, Advisory nos Fins de Turno** 🟢 — **revisada pela 025/MD-0018 (§2.23): o soft-block do Stop foi aposentado; de três políticas restaram duas**
  - Origem: `.harness/harness-core/src/core/session/close_flow.py` (3º portão), `.harness/harness-core/src/main.py` (ramo `decisions --gate`), `.harness/harness-core/src/adapters/antigravity/hook_bridge.py` (`gate_evaluator`)
  - O mesmo veredito alimenta três bordas com apenas **duas políticas**: (1) **portão do `encerrar-sessao`** — a ÚNICA política bloqueante: aborta (exit 0, marker `DECISAO_PENDENTE`, protocolo abortar-e-reexecutar) até registrar ficha ou declarar `--sem-decisao`; (2) **hook Stop do Claude** (`decisions --gate`) — **advisory puro desde a 025**: pendência inédita vira linha `Aviso:` em stderr (marker da 022 + frase de ação), **stdout sempre vazio** (o JSON `{"decision":"block",...}` foi aposentado), exit 0 sempre; a identidade grossa (023) segue persistida antes da emissão → no máximo **um aviso** por sessão; sob `--gate`, nem erros de integridade do grafo derrubam o turno; (3) **Antigravity** — aviso em stderr (advisory por construção, RN-N26), inalterado — o Claude convergiu para a política que o Antigravity já tinha.
- **RN-N45: Anti-loop por Fingerprint Persistido no Estado de Sessão** 🟢
  - Origem: `.harness/harness-core/src/core/domain/models.py:SessionState`, `.harness/harness-core/src/core/session/serializer.py`
  - O mesmo estado de pendência nunca dispara o gate duas vezes: os campos opcionais `gate_lembrete_fingerprint`/`gate_encerramento_fingerprint` persistem no front-matter do estado de sessão — a **exceção consagrada** do pré-check de pendência (RN-N34); um scratch novo sob `.harness/` viraria `COMMIT_PENDENTE` perpétuo ou exigiria entrada de `.gitignore` em toda a base instalada (lição do T7; scratch dedicado descartado na MD-0015). Gravados só quando preenchidos (arquivo byte-compatível com o formato pré-022 enquanto o gate não é acionado), tolerados como ausentes no parse (estados antigos), e **zerados por `close_session`** (não vazam para a próxima sessão). No portão, pendência com fingerprint fino já bloqueado → aviso "não sanada" e o encerramento **prossegue** (anti-loop, o gate nunca trava indefinidamente). **Fail-open barulhento**: âncora ilegível/repo sem commit → `pendente=False` + `aviso` ecoado em stderr pela borda — o gate nunca trava o agente por erro interno.
- **RN-N46: Escape Auditável (`--sem-decisao`)** 🟢
  - Origem: `.harness/harness-core/src/main.py` (`cmd --sem-decisao`), `.harness/harness-core/src/core/session/close_flow.py`
  - `encerrar-sessao --sem-decisao` satisfaz o gate gravando `"Declarado: sem decisão não óbvia nesta sessão (gate de registro)."` na narrativa (`feito`) antes do fechamento — rastro de ato deliberado do agente/usuário, não invenção de narrativa pelo core (RN-N3 preservada). A declaração fica visível na retomada seguinte.

### 🎚️ 2.21 Granularidade do Lembrete: Dupla Identidade Anti-loop (feature 023)

> Queixa do mantenedor: "cada mudança de arquivo está rodando o hook". Diagnóstico: não havia hook por-edição (MD-0014 já o aposentara) — o rearme vinha do fingerprint do lembrete incluir os sujos: cada arquivo tocado mudava a identidade fina e rearmava o soft-block. A correção dá a cada consumidor a identidade da sua semântica, em vez de "consertar" o fingerprint na origem.

- **RN-N47: Lembrete com Identidade Grossa, Portão com Identidade Fina** 🟢 — estende RN-N45 (MD-0016 estende MD-0015)
  - Origem: `.harness/harness-core/src/core/decisions/gate.py:compute_lembrete_fingerprint`, `.harness/harness-core/src/main.py` (ramo `--gate`), `.harness/harness-core/tests/test_close_flow.py::test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio`
  - O lembrete do Stop compara/persiste a identidade **grossa** (`sha1(âncora)`, estável do início ao encerramento) → **no máximo um soft-block por sessão** com pendência; nem arquivo tocado nem commit novo o rearmam. O 3º portão mantém a identidade **fina** (`sha1(âncora+HEAD+sujos)`) → trabalho novo sem ficha **continua rearmando** a garantia dura — comportamento pinado por teste-guarda. Justificativa da grossa: espelha a definição de pendência do avaliador (ficha desde a âncora satisfaz a sessão inteira, logo "um lembrete por pendência" ≡ "um por sessão"). Descartados (MD-0016): mudar `compute_fingerprint` globalmente (enfraqueceria o portão), `sha1(âncora+HEAD)` (subgranularidade sem semântica no domínio), carência de N turnos (sabor de relógio), remover o lembrete (reverte o enforcement híbrido), flag no toml (YAGNI), âncora crua no estado (quebraria a uniformidade dos campos-fingerprint). **Transição autoresolvente**: sem schema novo, sem flag, sem migração — o valor antigo (fino) nunca coincide com a composição nova (grossa), então há no máximo 1 lembrete pós-atualização e o estado converge. Core 2.1.0 → 2.1.1 (patch: nenhum contrato externo muda).

### 🤝 2.22 Consentimento para Escrita no Git ao Encerrar (feature 024, MD-0017)

> O encerramento tinha dois momentos de escrita no git por iniciativa própria: o pré-check abortava exigindo commit do trabalho pendente, e o fechamento sempre commitava o estado. A 024 subordina ambos a consentimento, com default assimétrico por borda: no terminal quem responde é o usuário; sem terminal, silêncio não autoriza.

- **RN-N48: Toda Escrita no Git ao Encerrar Exige Consentimento, com Default Assimétrico por Borda** 🟢 — revisa RN-N31 (o "quando" do versionamento)
  - Origem: `.harness/harness-core/src/core/session/close_flow.py` (`run`, `conduct_commit_pendente`), `.harness/harness-core/src/core/commands/service.py` (`execute_command(..., versionar_estado=True)`), `.harness/harness-core/src/main.py` (flags do `cmd`)
  - Dois pontos de decisão: (1) **trabalho pendente** — `conduct_commit_pendente` devolve `bool`: com TTY anuncia a contagem e pergunta o desfecho de segunda ordem (`s` = encerrar com o trabalho fora do histórico, com rastro na narrativa; `n` = abortar); sem TTY só a flag `--com-pendencias` autoriza. (2) **commit de encerramento** — tri-estado `versionar_encerramento` resolvido por borda: com TTY, pergunta `[S/n]` com default **afirmativo**; sem TTY, **o silêncio é recusa** — versiona apenas com `--com-commit-encerramento` (mutuamente exclusiva com `--sem-commit-encerramento`; ambas → erro de uso barulhento). `CommandService.execute_command` ganhou `versionar_estado: bool = True` (todos os chamadores atuais preservados; a borda MCP mantém `True` por assimetria deliberada, D-04). Com `False`: fecha o estado no arquivo, **pula** `commit_paths`, grava linha declarativa na narrativa (RN-N3: rastro de ato, não invenção) — âncora e HEAD coincidem, pois nada foi commitado.
- **RN-N49: Desfecho Não Versionado é Anunciado, Nunca Silencioso** 🟢 — estende RN-N4 ao fechamento sem commit
  - Origem: `.harness/harness-core/src/core/session/close_flow.py` (`render_encerramento_nao_versionado_marker`, `conduct_encerramento_nao_versionado`)
  - Quando o encerramento conclui **sem** versionar, o fluxo emite o marker `ENCERRAMENTO_NAO_VERSIONADO` **após o sucesso e antes da oferta de push**, com `motivo` que distingue esquecimento do agente (nenhuma flag) de recusa explícita (`--sem-commit-encerramento`/resposta `n`) — para a oferta de push jamais sugerir publicar supondo que o registro entrou no histórico. A skill `encerrar-sessao` (v1.4.0) reage por `motivo`.

### 🕊️ 2.23 Aposentadoria do Soft-block do Stop (feature 025, MD-0018)

> O soft-block do fim de turno (022/023) provou-se mais atrito que garantia: o mantenedor relatou o projeto "bloqueando o desenvolvimento com muitas pausas". A 025 despromove o lembrete a advisory e concentra toda a garantia dura no único momento em que ela é barata: o encerramento.

- **A regra viva é a RN-N44 revisada (§2.20)** 🟢 — o ramo `decisions --gate` mantém TODA a mecânica (avaliação pura RN-N43, persistência da identidade grossa RN-N45/N47, reindexação, fail-open, exit 0), mudando apenas o desfecho da pendência inédita: aviso em stderr em vez de JSON de bloqueio no stdout. Nenhum arquivo de hooks foi regravado (o comando do hook Stop é o mesmo); a propagação à base migrada é automática pela fonte única (RN-N36). `gate.py`, `close_flow.py`, serializer e modelos permaneceram byte-idênticos (escopo negativo conferido no diff da 025).

### 🌡️ 2.24 Medidor Read-only de Progresso de Entregáveis (feature 026, MD-0019)

> O harness respondia "o quê" (estado de sessão) e "por quê" (microdecisões); faltava "quanto falta". O medidor reproduz o padrão do `make estado` de `comentarios-concursos`: termômetro inteiramente derivado das fontes de verdade, sem estado próprio.

- **RN-N50: Medição é Derivação Pura, Sem Estado Próprio** 🟢
  - Origem: `.harness/harness-core/src/core/progress/service.py:ProgressService.measure`
  - `measure()` agrega as fontes de verdade (ciclo forward via `active-requirements.json` + artefatos físicos; regression-watch; microdecisões com gate reavaliado em leitura pura, sem persistir fingerprint; estado de sessão; e, com opt-in, os cards manuais do board) num modelo transitório `Medicao`, **jamais persistido**. O serviço é leitura pura — invariante pinada por teste (`fs.writes == []`); toda escrita vive na borda CLI. Fonte ausente é `n/a` legítimo; fonte presente mas ilegível é **falha real**. Divergência entre estágio declarado e físico é **achado** (alerta alta), nunca corrigida silenciosamente pelo medidor.
- **RN-N51: Artefato Derivado Sem Valor Volátil; Contrato de Exit Codes na Borda** 🟢
  - Origem: `.harness/harness-core/src/core/progress/render.py`, `.harness/harness-core/src/main.py` (ramo `progress`)
  - O markdown (`[progress].file`, default `.harness/progresso.md`) não carrega timestamp nem caminho absoluto: o diff do artefato versionado só aparece quando o estado medido muda; a regravação é atômica e **write-only-when-changed**. `--json` (stdout, não versionado) pode carimbar `aferido_em`. `--em-hook` sai com **1 apenas por artefato defasado** (instruindo o re-commit); alerta grave vira aviso em stderr **sem bloquear** — o medidor não cria terceira política de bloqueio (RN-N44 pós-025; o exit 3 do medidor original não foi transplantado, D-03). Falha real → `Erro de leitura:` em stderr, exit **2**, **nenhum artefato regravado**.
- **RN-N52: Alerta Persistente por Sinal Físico; Paridade com o Skill em Ponto Único** 🟢
  - Origem: `.harness/harness-core/src/core/progress/service.py` (`_MARCA_RECONCILIACAO`), `.harness/harness-core/src/core/progress/stages.py`
  - Alertas derivam de sinal físico e **persistem enquanto o problema existir** (sem ack): a marca literal "pendência de reconciliação" num `regression-watch.md` gera alerta média a cada medição até a re-extração removê-la. `stages.py` é a implementação em código da tabela de estágio físico e da contagem de checkboxes que vivem em prosa no skill `reversa-requirements` — ponto único de paridade; `contar_checkboxes` e `listar_acoes` compartilham o MESMO critério de linha.

### 📋 2.25 Exportador Kanban Derivado da Medição (feature 027, MD-0020)

> Segunda projeção da mesma `Medicao`, para o fork do vscode-kanban do mantenedor (interface recém-refatorada). O mantenedor ampliou o escopo no clarify: o board é também canal de ENTRADA — cards manuais apresentam demandas novas sem passar antes pelo processo, e o agente as conduz pelo ciclo forward.

- **RN-N53: Posse por Namespace; Cards Manuais São Ilha Intocável e Canal de Demandas** 🟢
  - Origem: `.harness/harness-core/src/core/progress/kanban.py` (`extrair_manuais`, `render_board`)
  - Card `category == "harness"` pertence ao exportador: recomputado do zero a cada exportação, ids estáveis derivados dos ids reais (`hns:<feature>`, `hns:<feature>:<T00N>`, `hns:alerta:<origem>`; ordinais rejeitados por instabilidade a reordenação). Qualquer outro card (categoria ausente ou diferente) é **manual**: preservado byte a byte, na coluna onde estiver, ordem relativa mantida; só o mantenedor o remove. Manuais em coluna não-`done` viram `Medicao.demandas` — fila de entrada que o agente deve executar pelo processo forward. Mapeamento fixo: ação `[ ]` → `todo`, `[X]` → `done`, resumo da ativa → `in-progress`, pausadas → `todo`, alertas → `todo` como `bug` (prio 9/5); `testing` nunca recebe card gerenciado; concluídas não geram card.
- **RN-N54: Board 100% Determinístico — Nenhum Caminho Consulta a Hora Corrente** 🟢
  - Origem: `.harness/harness-core/src/core/progress/kanban.py`, `.harness/harness-core/src/core/progress/service.py` (`_criacao_por_acao`)
  - `creation_time` deriva do primeiro `ts` da ação no `progress.jsonl` (linhas corrompidas silenciosamente puladas) com fallback no `started-at` da feature; resumos e alertas usam a mesma base. Mesmo estado medido + mesmos cards manuais → **bytes idênticos** (idempotência pinada por teste). Consequência: o board versionado só gera diff quando o estado muda (coerente com RN-N51).
- **RN-N55: Fluxo Unidirecional e Segurança do Arquivo Executável do Fork** 🟢
  - Origem: `.harness/harness-core/src/core/progress/service.py` (`_medir_demandas`), `.harness/harness-core/src/main.py` (ramo `progress`, modo padrão)
  - A fonte de verdade é o `actions.md`: cards gerenciados do arquivo **jamais** servem de fonte de progresso — edição manual num card gerenciado é descartada na exportação seguinte (fluxo `actions.md` → board, nunca o inverso). O board só é lido com `[progress.kanban].enabled = true` e SÓ pelos manuais; só é escrito no modo padrão (nunca `--json`/`--em-hook`), atômico, write-only-when-changed; sem opt-in, nada sob `.vscode/` é criado. Board presente mas ilegível herda o contrato de falha real (exit 2 sem regravar nada). **Segurança**: o exportador escreve unicamente o `.json` configurado e jamais cria ou toca `.vscode/vscode-kanban.js` — o fork EXECUTA esse arquivo (`workspaces.ts:769`).

### 🪶 2.26 Visão Compacta de Decisões — Derivação Dupla e Guidance do Init (feature 028, MD-0022)

> Queixa importada de projeto passado: mesmo com o índice, a injeção no SessionStart inchava com o acervo (o índice cresce linearmente com as fichas e carrega backlinks). A 028 separa **ancoragem** (o que entra no boot: visão compacta de custo ~constante) de **consulta** (o que fica a um passo: índice completo e fichas, sob demanda), e ensina o caminho de consulta no arquivo de guidance da engine. A revisão do comportamento do resume vive na RN-N41 (§2.18); as regras abaixo cobrem a derivação e o guidance. **Nota de rodada:** a MD-0021 (mesma janela) é decisão **operacional** — abandono da atualização do vault Obsidian no encerramento — sem projeção em código do core; registrada aqui só para rastreabilidade do acervo.

- **RN-N56: Duas Visões, Uma Passada, Todas as Bordas — Ambas Write-Only-When-Changed** 🟢 — estendida à borda MCP pela MD-0023 e à borda de encerramento pela MD-0025
  - Origem: `.harness/harness-core/src/core/decisions/service.py` (`compile_compact_view`, `_extract_title`, `_write_if_changed`), `.harness/harness-core/src/main.py` (ramo `decisions`), `.harness/harness-core/src/adapters/antigravity/hook_bridge.py` (`_handle_stop`), `.harness/harness-core/src/core/session/close_flow.py` (`_derive_decision_views`)
  - A visão compacta (`decisions.compact_file`, default `.harness/decisoes-recentes.md`) é derivada **na mesma passada** do índice, **após** a validação de integridade, em TODAS as bordas que indexam (CLI `decisions`, inclusive `--gate`; `stop` da ponte Antigravity; a tool MCP `process_decisions`, desde a MD-0023; e o encerramento de sessão via `SessionCloseFlow`, desde a MD-0025) — nunca existe passada que atualize só uma visão. As duas gravações passam por `_write_if_changed`: sem mudança nas fichas, nenhum dos artefatos é regravado (mtime imóvel, diff só quando o estado muda — mesma disciplina da RN-N51/N54). O título é extraído num **único ponto** (`_extract_title`: regex do H1 `# MD-NNNN — título`, fallback para o ID), compartilhado pelas duas visões — sem divergência de formato possível. **Nota (achado G-20/T8, fechado no mesmo dia):** na varredura de 2026-08-11-b a tool MCP compilava só o índice; corrigido por TDD direto (MD-0023, `test_mcp.py`, core 2.6.1). Ressalva remanescente: a borda MCP compila mesmo com erros de integridade (semântica histórica, distinta da CLI), e a compacta a acompanha para as visões nunca divergirem. **Nota (BUG-20260811-XZ3B, fechado no mesmo dia):** o encerramento direto pela skill fechava sessão sem derivar as visões, deixando o índice defasado até a próxima passada de outra borda; corrigido por TDD direto (MD-0025, `test_close_flow.py`, core 2.6.3). Semântica da borda de encerramento: roda antes do 1º portão de pendência (visão regravada vira trabalho pendente sob a disciplina da 024), é estritamente não-bloqueante (aviso em stderr, o fechamento nunca é sacrificado), não regrava com grafo inválido (CLI menos o abort) e não deriva nada com o acervo vazio — o critério é a ausência de fichas em `decisions.dir`, não a ausência do diretório, porque o `init` sempre cria o diretório com o cabeçalho (projeto que nunca registrou decisão não ganha visões inventadas no fechamento; a CLI, invocada explicitamente, continua compilando mesmo vazia). A mesma MD-0025 acrescentou `decisions.compact_file` aos excluídos do gate de registro (RN-N43): sem isso, a compacta recém-derivada disparava DECISAO_PENDENTE espúrio por arquivo que o próprio harness escreveu. **Ressalva remanescente (dívida documentada):** a tool MCP `session_command("encerrar-sessao")` executa o comando diretamente pelo `CommandService`, sem passar pelo `SessionCloseFlow` — essa borda de encerramento específica ainda NÃO deriva as visões; rotear pelo flow acrescentaria portões ao MCP e é decisão de comportamento pendente.
  - Formato da compacta: cabeçalho declarando a natureza derivada, três linhas de orientação (índice completo, pasta de fichas, comando), `Total: N ficha(s)` e as `compact_index_size` fichas mais recentes por **ID decrescente**, cada uma `- **MD-NNNN** — título`, **sem backlinks**. `compact_index_size` valida `ge=0` (negativo → erro Pydantic barulhento, RN-N4); `0` degrada para cabeçalho + contagem + ponteiros.
- **RN-N57: A Visão Compacta é Artefato Derivado, Nunca Fonte** 🟢 — estende RN-N12 à segunda visão
  - Origem: `.harness/harness-core/src/core/decisions/service.py` (`compile_compact_view`), cabeçalho do próprio artefato
  - `.harness/decisoes-recentes.md` nunca é editado à mão nem serve de fonte de verdade: é recomputado do zero a cada derivação a partir das fichas, e o próprio cabeçalho declara essa natureza (mesma regra do índice). Consequência do fallback da RN-N41: apagar a compacta não quebra nada — o resume degrada para o índice com aviso e a próxima derivação a recria.
- **RN-N58: Guidance de Microdecisões é Write-Once do Init, Idempotente por Marcador** 🟢
  - Origem: `.harness/harness-core/src/core/bootstrap/init_service.py` (`_ensure_decisions_guidance`, `DECISIONS_GUIDANCE_MARKER`, `_GUIDANCE_FILE_BY_HARNESS`)
  - O `init` grava, como último passo, um trecho de guidance sobre o fluxo de microdecisões (fichas → visão compacta → índice sob demanda → `./harness decisions`; artefatos derivados não se editam) no arquivo de instrução da engine: `claude→CLAUDE.md`, `antigravity→AGENTS.md` (confirmado no coding e pinado por teste), `gemini→GEMINI.md`; harness desconhecido → no-op. **Idempotência pelo marcador** `<!-- harness:decisoes -->`: arquivo ausente → cria só com o trecho; marcador presente → não toca; presente sem marcador → append preservando o conteúdo do usuário (`rstrip` + separação em branco), sempre atômico. O `upgrade` **nunca** regrava esse arquivo — o texto passa a pertencer ao usuário após o init (write-once). Risco aceito por design: remover o marcador mantendo o texto duplica o trecho num re-init.
