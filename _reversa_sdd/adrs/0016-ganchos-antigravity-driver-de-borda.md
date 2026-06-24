# ADR 0016: Ganchos do Antigravity via `hooks.json` declarativo traduzido por driver de borda

- **Status:** Aceito
- **Data:** 2026-06-24 (feature 009-hooks-antigravity)
- **Contexto Técnico:** Novo adaptador `src/adapters/antigravity/hook_bridge.py` (`AntigravityHookBridge`); módulo `src/core/install/antigravity_hooks.py` (`materialize_hooks_json`); `src/core/install/harness_profiles.py` (`AntigravityProfile`); subcomando `agy-hook` em `src/main.py`; `src/core/bootstrap/init_service.py` (`initialize_project`, `upgrade_project`)
- **Escala de Confiança:** 🟢 CONFIRMADO (código as-built; runtime real do Antigravity coberto por fixtures, ver Consequências)
- **Decisões relacionadas:** MD-0003 (mecanismos de reinjeção por harness, que registrava o gancho do Antigravity como pendência), MD-0005 (módulo per-projeto, footprint global zero); ADRs 0011 (Strategy multi-harness sem `if`s no core), 0002 (formatação não-bloqueante no `PostToolUse`)

## Contexto e Problema

O ADR 0011 deixou o `AntigravityProfile` como **placeholder**: o `hooks_block()` emitia apenas um aviso de "mecanismo não confirmado", e o caminho de ganchos do Antigravity seguia como pendência aberta (registrada no MD-0003). A reinjeção de estado já estava resolvida pela Strategy de sink (`FileProjectionSink`), mas faltava o outro lado do ciclo de vida: capturar as edições de arquivo do agente para formatá-las (paridade com o `PostToolUse` do Claude, ADR 0002) e revalidar as microdecisões ao fim do laço.

O Antigravity diverge dos demais harnesses em dois pontos. Primeiro, o protocolo: seus ganchos são declarados num arquivo dedicado `.agents/hooks.json` (named-hooks com eventos `PreToolUse`/`PostToolUse`/`Stop`), e cada gancho é um processo externo que recebe um payload JSON camelCase no `stdin` e responde com JSON no `stdout` — um formato por evento. Segundo, o esquema do payload é próprio: a tool de escrita não chega no nome `Write|Edit` do Claude nem com o `tool_input.file_path` que o `resolve_format_target` (`main.py`) já sabia ler, mas como `write_to_file|replace_file_content|multi_replace_file_content` com o caminho em `toolCall.args.TargetFile`, e o `PostToolUse` não traz o caminho — só o `stepIdx`.

Ensinar o core a falar esse protocolo embutindo `if active_harness == "antigravity"` nos serviços de domínio violaria a neutralidade do hexágono e a RN-N5 ("o core não conhece o harness"), contradizendo o ADR 0011. Estender o `resolve_format_target` para dois esquemas de payload acoplaria a CLI do Claude ao contrato do Antigravity, baixando a coesão.

## Decisão

Tratar o protocolo do Antigravity como mais um **driver de entrada na borda do hexágono**, simétrico à CLI (`main.py`) e ao servidor MCP (`adapters/mcp/server.py`), em três frentes:

1. **Terceiro driver de entrada (`AntigravityHookBridge`).** Novo adaptador em `src/adapters/antigravity/hook_bridge.py` que traduz o protocolo — lê o payload JSON do `stdin`, despacha por evento e **delega aos serviços de domínio já existentes** (`FormattingService`, `DecisionService`), que recebe por injeção e permanecem agnósticos ao harness. Invocado pelo subcomando fino `./harness agy-hook <evento>` (`main.py`), que constrói os mesmos adaptadores concretos da CLI e repassa ao bridge. O `resolve_format_target` (esquema Claude) fica intacto.

2. **Captura `PreToolUse` → formatação `PostToolUse` via scratch.** Como o `PostToolUse` do Antigravity não traz o caminho do arquivo, o bridge grava no `PreToolUse` um mapa `stepIdx → TargetFile` num arquivo de scratch sob o `artifactDirectoryPath` do payload (`.harness-agy/pending-format.json`) e o consome no `PostToolUse`, resolvendo o caminho pelo `stepIdx` antes de chamar `FormattingService.format_file`. Isso preserva a granularidade por-edição (RN-03/ADR 0002) usando só campos documentados do contrato, sem parsear o `transcript.jsonl` interno. O stdout por evento é fixo: `{"decision": "allow"}` no `pre-tool-use` (nunca bloqueia), `{}` no `post-tool-use`, e `{}` no `stop` — jamais `{"decision": "continue"}`, para não reentrar no laço do agente. O `Stop` roda o `DecisionService` (equivalente a `./harness decisions`).

3. **Materialização única compartilhada por `init` e `upgrade`.** `materialize_hooks_json(fs, project_path, command_path)`, em `src/core/install/antigravity_hooks.py`, é a rotina única que escreve o `.agents/hooks.json`. Faz **merge por named-hook**: lê o arquivo existente (dict vazio se ausente/inválido), substitui só a chave `harness` pelo bloco canônico do `AntigravityProfile` com o placeholder `<ABS>` resolvido para o caminho absoluto do projeto, e grava de forma atômica via `FileSystemPort`. `initialize_project` e `upgrade_project` a chamam **apenas** quando `active_harness == "antigravity"`; o `upgrade` reescreve o caminho absoluto se o repositório foi movido. Em paralelo, o `AntigravityProfile` deixou de ser placeholder (emite o `hooks.json` válido) e a nota de escopo "no projeto, nunca no global" migrou para o `apply_instructions()` dos três perfis, removendo do `template.md` o `.claude/` chumbado e a nota obsoleta do `SessionStart`/MD-0001 (já fechada na feature 004).

A garantia não-bloqueante é dupla: o bridge captura toda exceção, loga em `stderr` e emite o stdout-padrão do evento; e o ramo `agy-hook` no `main.py` pré-computa o fallback a partir do argumento já validado **antes** de qualquer operação que possa lançar (carga de config, leitura do stdin, construção dos serviços), de modo que `harness.toml` corrompido ou stdin ilegível ainda emita o stdout exigido e encerre com 0. Por isso o `agy-hook` é exceção ao carregamento global de config e ao check passivo de sync do `main.py`.

## Alternativas Consideradas

- **`if active_harness == "antigravity"` nos serviços de domínio:** descartado — acoplaria a regra de negócio ao harness e violaria a RN-N5/ADR 0011. A Strategy/driver na borda é o padrão já estabelecido.
- **Estender `resolve_format_target` para dois esquemas de payload:** descartado — baixaria a coesão da CLI do Claude misturando dois contratos; o protocolo de terceiro pertence ao anel de adaptadores, não ao caminho do Claude.
- **Script shell externo traduzindo o protocolo:** descartado — ficaria fora do core testável; o bridge em Python é coberto por testes de payload-fixture.
- **Parsear `transcriptPath`/`transcript.jsonl` no `Stop` (ou diff do git) para achar o arquivo editado:** descartado como caminho primário — acopla a um formato interno não documentado e perde a granularidade por-edição. Mantido como fallback conceitual (Stop+git-diff), com a captura `PreToolUse`+`PostToolUse` como estratégia escolhida.
- **Aplicar os ganchos só via `install-prompt` colável (simetria com o Claude):** descartado — diferente do `.claude/settings.json` (que mescla com outras chaves do usuário), o `.agents/hooks.json` é dedicado e seguro de escrever no `init`; materializá-lo por merge melhora a UX e cumpre o requisito sem risco. A assimetria de UX (Claude cola à mão, Antigravity auto-escreve) é registrada no `apply_instructions`.
- **`command` por caminho relativo ou variável de shell (`${CLAUDE_PROJECT_DIR}`):** descartado — o Antigravity não expõe essa variável e o cwd do gancho é indefinido na doc; o caminho absoluto resolvido no `init`/`upgrade` é determinístico e footprint-safe.

## Consequências

- **Positivas:**
  - O ciclo de vida do Antigravity ganha paridade com o Claude (captura→formatação no `PostToolUse`, decisões no `Stop`), reusando os serviços de domínio sem duplicar lógica e sem ramificar o core por harness (RN-N5 reforçada; confirmada por `grep`: zero `active_harness` nos serviços de domínio).
  - O `AntigravityProfile` deixa de ser placeholder, fechando a pendência aberta no ADR 0011 e no MD-0003.
  - `init`/`upgrade` materializam o `.agents/hooks.json` por uma rotina única com merge, preservando chaves de terceiros e mantendo footprint global zero (RN-N17/MD-0005): toda escrita ocorre sob o `project_path` via `FileSystemPort`.
  - Sem dependências novas — o bridge usa só `json`/`os`/`sys` da stdlib. Suíte com 110 testes verdes.
  - Ponto de extensão explícito: um quarto harness seria mais um driver na borda, não um `if` no domínio.
- **Negativas:**
  - O `command` é absoluto: mover o repositório sem rodar `./harness upgrade` deixa os ganchos apontando para o caminho antigo. Mitigado pelo `upgrade` (que reescreve) e documentado no onboarding.
  - Premissas de runtime do Antigravity — estabilidade do `stepIdx` entre `PreToolUse`/`PostToolUse` e acesso de leitura ao `artifactDirectoryPath` — não foram verificáveis localmente (sem o agente real). Cobertas por testes de contrato com fixtures, não por integração real; se divergirem, o adaptador isola a correção num único ponto e o fallback Stop+git-diff permanece disponível.
