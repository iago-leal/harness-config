# Investigation: encerrar-sessao como skill versionável

> Feature `018-encerrar-sessao-como-skill` · 2026-06-27

## 1. Pergunta de fundo

Como migrar `encerrar-sessao` de command (entregue por slash command/workflow que delega ao binário) para uma skill versionável que é o adaptador por harness, **sem** duplicar a lógica testada nem regredir a qualidade interna?

## 2. Achados sobre o legado

- A orquestração de `encerrar-sessao` vive na borda `main.py` (L418–475): constrói `CommandService(fs, git)`, faz o pré-check de trabalho pendente (016: `git.list_dirty_paths` → marker `[HARNESS:COMMIT_PENDENTE …]`), e chama `service.execute_command(...)`. `regen` é tratado fora, via `RegenService`.
- A lógica de domínio está em serviços coesos e testados: `CommandService` (`commands/service.py`), `DecisionService` (`decisions/service.py`), serializer (`session/serializer.py`), `GitPort` (`ports/git.py`).
- A adaptação por harness é hoje um Strategy: `HarnessProfile.session_command_artifact` devolve **um** arquivo (`.md`) que delega ao binário. RN-N5: o core não conhece o harness.
- Verificado em disco: o Claude lê skills de `.claude/skills/<nome>/SKILL.md` (o Reversa vive lá); o Antigravity de `.agents/skills/<nome>/SKILL.md`.

## 3. Tensão central e resolução

"Skill versionável que contém os scripts" **vs** "lógica de domínio testável e não-duplicada". Resolvida no clarify: os scripts da skill são **finos** e consomem a lógica do core como biblioteca. Para que nem a orquestração seja duplicada, ela é **extraída de `main.py` para um serviço do core** que a CLI e a skill compartilham.

## 4. Alternativas avaliadas

| Alternativa                                            | Veredito      | Razão                                                                      |
| ------------------------------------------------------ | ------------- | -------------------------------------------------------------------------- |
| Scripts finos chamando serviço de orquestração do core | **Escolhida** | DRY, testável, RN-N5; skill versionável sem duplicar.                      |
| Scripts autossuficientes (reimplementam a lógica)      | Rejeitada     | Duplicação → divergência e dívida; perde os testes.                        |
| Skill instrucional que delega a `./harness cmd`        | Rejeitada     | Mantém o acoplamento ao binário que se quer reduzir; não "contém scripts". |
| Scripts chamando `./harness cmd` por subprocess        | Rejeitada     | É delegar ao binário disfarçado; não reduz acoplamento.                    |
| Conteúdo de skill diferente por harness                | Rejeitada     | Acopla e duplica; o que varia é só o diretório-prefixo.                    |

## 5. Padrões aplicáveis

- **Strategy por harness** estendido: o perfil deixa de devolver "um arquivo que delega" e passa a expor o **diretório de skills** + a árvore agnóstica.
- **Extract Service / Façade**: a orquestração de encerramento vira um serviço de fachada sobre `CommandService`/`GitPort`/`DecisionService`, reusado por CLI e skill.
- **Self-bootstrap do script**: o script da skill resolve a raiz (git) e o venv do core, à imagem do wrapper `./harness`.

## 6. Fontes

- Legado: `main.py` (dispatch `cmd`), `core/commands/service.py`, `core/decisions/service.py`, `core/install/harness_profiles.py`, `core/install/session_commands.py`.
- `_reversa_sdd/domain.md` (RN-N2, RN-N5, RN-N29, RN-N31/N32), `_reversa_sdd/adrs/0011`.
- Sessão atual: feature 017 (caminho/limpeza de artefato) + validação por `skill-spec` (SPEC da skill `encerrar-sessao`, score 82/100).
