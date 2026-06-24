# Investigation: Comando de IDE para encerrar a sessão

> Identificador: `010-command-encerrar-sessao`
> Data: `2026-06-24`

## Pergunta de fundo

Como expor, dentro da IDE do agente, um slash command que dispare a capacidade `encerrar-sessao` já existente no `CommandService`, materializando-o automaticamente no `init` para Claude Code e Antigravity?

## O que já existe (legado)

- **Capacidade `encerrar-sessao`**: `CommandService.execute_command` (`harness-core/src/core/commands/service.py`). Exige sessão ativa, lê HEAD via `GitPort`, chama `close_session(commit)` e salva atomicamente. Hoje só acionável por `./harness cmd encerrar-sessao` (CLI, `main.py` subcomando `cmd`) e pela tool MCP `session_command`.
- **Molde de materialização**: `materialize_hooks_json` (`harness-core/src/core/install/antigravity_hooks.py`) — rotina única, chamada por `init` e `upgrade`, merge por chave nomeada, escrita atômica via `fs.write_file_atomic`, footprint sob `project_path`. Os testes em `tests/test_antigravity_hooks_materializer.py` fixam: merge preservando terceiros, resolução de placeholder, footprint zero (`RecordingFileSystem`) e atomicidade.
- **Estratégia por harness**: `HarnessProfile` (`harness-core/src/core/install/harness_profiles.py`). `ClaudeProfile` usa `${CLAUDE_PROJECT_DIR}/harness` nos hooks; `AntigravityProfile` baka caminho absoluto via placeholder `<ABS>`.
- **Wiring de init/upgrade**: `harness-core/src/core/bootstrap/init_service.py`. Hoje a chamada a `materialize_hooks_json` é **gated** por `active_harness == "antigravity"`.

## Superfícies de slash command por harness (pesquisa nos docs do Antigravity)

Fontes consultadas em 2026-06-24:

- Codelabs oficiais de Skills do Antigravity (Google) — skills são pacotes em `.agents/skills/<nome>/SKILL.md` com front-matter `name`/`description`; aparecem como slash commands.
- Guia de migração gemini-cli → Antigravity (explainx.ai; Google Cloud Community/Medium) — `.gemini/skills/` deve migrar para `.agents/skills/`; **salvar um arquivo em `.agents/workflows/` registra um comando direto no chat**; `AGENTS.md` na raiz é prependado a todo prompt.
- Cheatsheet do Antigravity CLI (scriptbyai) — confirma `.agents/skills/` e `.agents/mcp_config.json` como caminhos de workspace.

Conclusão: o equivalente fiel ao `.claude/commands/<nome>.md` do Claude é o **workflow** do Antigravity em `.agents/workflows/<nome>.md` — escolhido no `/reversa-clarify` (a skill foi descartada por ser mais pesada e por gatilho semântico, não determinístico).

| Harness | Diretório de slash command | Formato | Observação |
|---------|----------------------------|---------|------------|
| Claude Code | `.claude/commands/` | Markdown; corpo vira prompt; suporta `!`-bash e front-matter (`description`, `allowed-tools`) | Execução de shell direta e determinística |
| Antigravity | `.agents/workflows/` | Markdown registrado como comando no chat | Execução de shell embutida **não confirmada** na doc → ver risco D-06 |

## Alternativas avaliadas

| Alternativa | Veredito |
|-------------|----------|
| Antigravity via **skill** (`.agents/skills/encerrar-sessao/SKILL.md`) | Descartada no clarify: mais pesada (pasta + front-matter + gatilho semântico); workflow é o análogo direto de "command" |
| Materializar **só** para o `active_harness` (como `materialize_hooks_json`) | Descartada no clarify: requirements decidiu cobertura dupla incondicional |
| Comando **instrui o agente** a rodar o `./harness` (mediado) | Descartada no clarify como padrão: preferido execução direta; permanece como degradação aceitável só no Antigravity se faltar shell embutido |
| Hardcodar o conteúdo dos arquivos no materializador | Descartada: espalha conhecimento de harness fora do `HarnessProfile` (fere RN-N5 / baixo acoplamento) |
| Estender o `install-prompt`/`template.md` (RN-N9, placeholder `{{COMMANDS}}`) para citar o novo comando | Fora de escopo: o pedido é materialização física no `init`, não o prompt de instalação |

## Padrões aplicáveis

- **Strategy** (já no projeto): mecanismo por harness encapsulado em `HarnessProfile`.
- **Rotina única compartilhada** (RN-N27): mesma função para `init` e `upgrade`.
- **Footprint global zero** (RN-N17): toda escrita sob `project_path`, fixada por teste com `RecordingFileSystem`.

## Fontes externas

- `https://antigravity.google/docs/gcli-migration` (renderizada via JS; conteúdo útil obtido das fontes paralelas abaixo)
- `https://codelabs.developers.google.com/getting-started-with-antigravity-skills`
- `https://www.explainx.ai/blog/google-gemini-cli-deprecation-antigravity-migration-guide`
- `https://medium.com/google-cloud/migrating-to-antigravity-cli-a841c6964f37`
- `https://www.scriptbyai.com/antigravity-cli-cheatsheet/`
