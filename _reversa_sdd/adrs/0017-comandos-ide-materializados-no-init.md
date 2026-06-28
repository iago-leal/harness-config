# ADR 0017: Slash commands de IDE materializados no `init`/`upgrade`, sempre Claude+Antigravity

> ⚠️ **Substituída pela [ADR 0018](0018-encerrar-sessao-como-skill-adaptador.md) (feature 018-encerrar-sessao-como-skill).** A decisão de materializar a capacidade `encerrar-sessao` como slash command/workflow `.md` que delega ao binário foi trocada pela materialização de uma **skill versionável** (`SKILL.md` + `scripts/` finos sobre o core). A descoberta empírica de 017 (o Antigravity ignora slash commands/workflows locais; só skills ativam por contexto) invalidou a premissa central desta ADR. O registro abaixo é preservado como memória histórica; o mecanismo vigente é o da ADR 0018.

- **Status:** Substituída pela ADR 0018 (✨f018)
- **Data:** 2026-06-24 (feature 010-command-encerrar-sessao)
- **Contexto Técnico:** Novo módulo `src/core/install/session_commands.py` (`materialize_session_commands`); novo método `session_command_artifact` em `src/core/install/harness_profiles.py` (`HarnessProfile`/`ClaudeProfile`/`AntigravityProfile`/`GeminiProfile`); fiação em `src/core/bootstrap/init_service.py` (`initialize_project`, `upgrade_project`)
- **Escala de Confiança:** 🟢 CONFIRMADO (código as-built; 130 testes verdes). 🟡 Comportamento de execução do workflow do Antigravity não verificável localmente (ver Consequências)
- **Decisões relacionadas:** ADR 0011 (Strategy multi-harness sem `if`s no core), ADR 0016 (materialização única `init`/`upgrade`, molde reusado), MD-0005 (módulo per-projeto, footprint global zero); regra RN-N5 (core não conhece o harness), RN-N28/RN-N29

## Contexto e Problema

A capacidade `encerrar-sessao` existe no `CommandService`, mas só era acionável por `./harness cmd encerrar-sessao` (CLI) ou pela tool MCP `session_command` — sem atalho visível dentro da IDE do agente, assimétrico à retomada (que sobe automática pelo `SessionStart`). O pedido: o `init` deve materializar um slash command que dispare o `encerrar-sessao`, visível **tanto no Claude Code quanto no Antigravity**.

Cada harness expõe slash command num diretório próprio: o Claude lê `.claude/commands/<nome>.md`; o Antigravity registra um comando no chat ao salvar um arquivo em `.agents/workflows/<nome>.md` (equivalente fiel ao do Claude, conforme a doc de migração gcli). Embutir esse conhecimento de diretório/formato no serviço de bootstrap, com `if active_harness`, repetiria o anti-padrão que o ADR 0011 já evitou para os ganchos.

## Decisão

Reusar o molde do ADR 0016 (`materialize_hooks_json`), com duas diferenças deliberadas:

1. **Rotina única, mas incondicional.** `materialize_session_commands(fs, project_path, command_path)`, em `src/core/install/session_commands.py`, grava os arquivos de comando e é chamada por `initialize_project` e `upgrade_project` **sempre** — sem o gate `active_harness == "..."` que condiciona a materialização de hooks. A decisão de cobertura dupla incondicional foi tomada no `/reversa-clarify` (Esclarecimentos · 2026-06-24): o comando deve aparecer para Claude **e** Antigravity em qualquer instalação. A rotina itera os perfis, grava cada artefato de forma atômica via `FileSystemPort.write_file_atomic` sob `project_path` (footprint global zero, RN-N17) e ignora perfis que não expõem comando.

2. **Conteúdo encapsulado no perfil.** Cada `HarnessProfile` ganha `session_command_artifact(command_path) -> (rel_path, content) | None`. `ClaudeProfile` devolve `.claude/commands/encerrar-sessao.md` com `!`-bash em `${CLAUDE_PROJECT_DIR}/harness cmd encerrar-sessao` (portátil, sobrevive a repo movido). `AntigravityProfile` devolve `.agent/workflows/encerrar-sessao.md` (singular ✨f017 — o plural `.agents/workflows/` não é reconhecido pelo Antigravity) com o caminho **absoluto** do wrapper, resolvido na materialização (espelha o `<ABS>` dos ganchos — não há env var de projeto garantida no Antigravity); o frontmatter expõe só `description` (sem `name`) e a materialização limpa o órfão do caminho plural. `GeminiProfile` herda `None` (sem superfície definida). Assim não há `if active_harness` no serviço (RN-N5 reforçada) e um quarto harness é só mais um perfil que devolve artefato.

O comando **não reimplementa** o fechamento: ambos os corpos delegam a `./harness cmd encerrar-sessao`, que exige sessão ativa e grava o commit-âncora. A não-destrutividade é automática — cada comando é um arquivo próprio (`encerrar-sessao`), então arquivos de terceiros nos diretórios não são lidos nem tocados; reexecutar `init`/`upgrade` é idempotente.

## Alternativas Consideradas

- **Materializar só para o `active_harness`** (como `materialize_hooks_json`): descartado no `/reversa-clarify` — o requisito é cobertura dupla incondicional.
- **Antigravity via skill** (`.agents/skills/encerrar-sessao/SKILL.md`): descartado — mais pesado (pasta + front-matter + gatilho semântico); o workflow é o análogo direto de "command".
- **Comando que instrui o agente** (mediado) em vez de executar direto: descartado como padrão — preferida a execução determinística via `!`-bash no Claude; permanece como degradação aceitável só no Antigravity se o workflow não rodar shell embutido.
- **Hardcodar os dois conteúdos no materializador:** descartado — espalharia conhecimento de harness fora do `HarnessProfile`, ferindo RN-N5/baixo acoplamento.
- **Caminho relativo `./harness` ou `${CLAUDE_PROJECT_DIR}` também no Antigravity:** descartado para o Antigravity — sem env var garantida e cwd indefinido; o absoluto resolvido no `init`/`upgrade` é determinístico e footprint-safe.

## Consequências

- **Positivas:**
  - O encerramento ganha paridade de UX com a retomada: `/encerrar-sessao` no chat, sem decorar a CLI, em ambos os harnesses.
  - Reusa o molde testado do ADR 0016: rotina única `init`+`upgrade`, escrita atômica, footprint global zero — o novo materializador foi incluído no teste de footprint (`RecordingFileSystem`), honrando a ressalva de 006/W003 ("ao adicionar serviços que escrevem artefatos, inclua-os no teste").
  - Sem `if active_harness` no serviço; conhecimento por-harness no perfil (RN-N5). Ponto de extensão aberto: Gemini ou um quarto harness é só mais um `session_command_artifact`.
  - Sem dependências novas (`os` da stdlib). Suíte com 130 testes verdes.
- **Negativas:**
  - O `command` do Antigravity é absoluto: mover o repositório sem rodar `./harness upgrade` deixa o comando apontando para o caminho antigo. Mitigado pelo `upgrade` (que reescreve) e documentado no onboarding.
  - O comportamento exato do workflow do Antigravity — execução de shell embutida vs instrução ao agente — não é verificável localmente. O corpo instrui a execução de `<abs>/harness cmd encerrar-sessao`; validar contra o Antigravity real quando disponível (alinha ao amarelo herdado de 009/W009).
  - A rotina é dona do nome `encerrar-sessao`: um arquivo de comando do usuário com esse mesmo nome seria sobrescrito. Documentado; demais arquivos preservados.
