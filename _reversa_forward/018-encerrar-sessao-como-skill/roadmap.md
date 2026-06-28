# Roadmap: encerrar-sessao como skill versionável (skill como adaptador)

> Identificador: `018-encerrar-sessao-como-skill`
> Data: `2026-06-27`
> Requirements: `_reversa_forward/018-encerrar-sessao-como-skill/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A capacidade `encerrar-sessao` deixa de ser materializada como slash command/workflow que delega ao binário e passa a ser uma **skill versionável** (diretório `SKILL.md` + `scripts/`) materializada nos dois harnesses (`.claude/skills/` e `.agents/skills/`). Para que os scripts da skill sejam **finos e não dupliquem** a orquestração que hoje vive na borda `main.py` (pré-check de trabalho pendente → marker `COMMIT_PENDENTE` → `CommandService.execute_command`), essa orquestração é **extraída para um serviço do core** testável. A borda CLI (`cmd encerrar-sessao`) e os scripts da skill passam a consumir esse mesmo serviço — fonte única de verdade, sob TDD, com o core seguindo agnóstico ao harness (RN-N5). O `HarnessProfile` passa a expor o **diretório de skills por harness**; a árvore da skill é agnóstica. O materializador grava a árvore nos dois harnesses e remove os artefatos antigos (workflow/command) de forma não-destrutiva.

## 2. Princípios aplicados

Não há `.reversa/principles.md`; aplico os princípios globais do mantenedor. Categoria (P4): **Aplicação** — rigor pleno.

| Princípio                            | Como a feature se relaciona                                                                                                  | Status   |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- | -------- |
| P5 — Alta coesão / baixo acoplamento | Orquestração vira serviço coeso do core; skill é casca fina (SRP por script); fonte única de verdade.                        | respeita |
| P5 — DRY / mínima dívida             | A orquestração não é duplicada entre borda CLI e skill; ambas consomem o mesmo serviço.                                      | respeita |
| P5.1 — OOP / contratos               | Novo serviço de orquestração em classe testável; adaptador (perfil) expõe contrato explícito (diretório de skills + árvore). | respeita |
| P5.2 — Testável e testado            | Lógica e orquestração permanecem no core sob TDD (cobertura ≥ 60%); scripts finos têm teste próprio.                         | respeita |
| RN-N5 (legado)                       | O core de domínio segue sem conhecer o harness; o prefixo por harness vive no perfil.                                        | respeita |
| Non-destructive                      | A migração remove só os artefatos que o harness gera; preserva terceiros.                                                    | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                                                                                                | Justificativa                                                                                            | Alternativas descartadas                                                                                                                                       | Confidência |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| D-01 | Extrair a orquestração de encerramento de `main.py` para um serviço do core (ex.: `core/session/close_flow.py`, ou método de `CommandService`), consumido pela borda CLI **e** pelos scripts da skill.                                                 | Evita duplicar a orquestração (DRY); mantém-na testável; preserva o fluxo da 016 (`COMMIT_PENDENTE`).    | Duplicar a sequência nos scripts da skill (dívida, divergência); scripts chamando `./harness cmd` por subprocess (= delegar ao binário, rejeitado no clarify). | 🟡          |
| D-02 | A skill é um diretório (`SKILL.md` + `scripts/`). Os scripts finos resolvem a raiz do projeto via git, localizam `.harness/harness-core`, executam com o venv do core e chamam o serviço de orquestração. Não reimplementam lógica.                    | Skill versionável que _contém_ scripts, mas a lógica é a do core testado (decisão do clarify).           | Scripts autossuficientes que reimplementam a lógica (duplicação).                                                                                              | 🟢          |
| D-03 | O `HarnessProfile` passa a expor o **diretório de skills por harness** (`.claude/skills/`, `.agents/skills/`; Gemini → `None`); a **árvore da skill** (caminhos relativos + conteúdo) é agnóstica ao harness.                                          | RN-N5 preservada: o que varia por harness é só o prefixo; o conteúdo é único.                            | Conteúdo de skill diferente por harness (acopla, duplica).                                                                                                     | 🟡          |
| D-04 | O materializador grava a árvore da skill nos dois harnesses (sempre) e remove os artefatos antigos (`.agent(s)/workflows/encerrar-sessao.md`, `.claude/commands/encerrar-sessao.md`) via `stale_session_command_paths`, estendendo o mecanismo da 017. | Migração limpa e não-destrutiva, reusando o que a 017 já construiu.                                      | Deixar artefatos antigos órfãos (confusão).                                                                                                                    | 🟢          |
| D-05 | Manter o core de domínio (`CommandService`, `DecisionService`, serializer, `GitPort`) intacto e testado; o CLI `cmd encerrar-sessao` permanece como borda alternativa.                                                                                 | Fonte única de verdade sob TDD; sem regressão; a skill é uma borda nova, não uma substituição da lógica. | Aposentar o CLI/serviços (perde rede de testes).                                                                                                               | 🟢          |
| D-06 | Bump de versão nos pontos sincronizados (`config.py`, `init_service.py`, `tests/test_init.py`).                                                                                                                                                        | O `upgrade` só regrava materializadores ao detectar versão nova.                                         | Não versionar (upgrade não propaga).                                                                                                                           | 🟢          |

## 4. Premissas

Nenhuma `[DÚVIDA]` ficou aberta. Premissas técnicas de fundo:

| Premissa                                                                                                    | Origem                                                                                                   | Risco se errada                                                                        |
| ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| O Claude lê skills de `.claude/skills/<nome>/SKILL.md` e o Antigravity de `.agents/skills/<nome>/SKILL.md`. | Verificado: o Reversa vive em `.claude/skills/`; skill `encerrar-sessao` já criada em `.agents/skills/`. | Baixo — confirmado em disco.                                                           |
| Os scripts da skill conseguem importar o core via `.harness/harness-core/src` com o venv do core.           | Mesmo mecanismo que o wrapper `./harness` já usa.                                                        | Médio — exige resolver raiz + venv; mitigado por teste e por self-bootstrap no script. |

## 5. Delta arquitetural

| Componente                       | Arquivo de origem no legado                                                                         | Tipo de mudança     | Resumo                                                                                    |
| -------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------- |
| Orquestração de encerramento     | `.harness/harness-core/src/main.py` (dispatch `cmd encerrar-sessao`, L418–475)                      | regra-alterada      | Extraída para serviço do core; `main.py` passa a chamá-lo.                                |
| Serviço de fluxo de encerramento | `.harness/harness-core/src/core/session/` (novo `close_flow.py` ou método em `commands/service.py`) | componente-novo     | Orquestra pré-check pendente → microdecisão (quando aplicável) → estado + commit isolado. |
| `HarnessProfile`                 | `.harness/harness-core/src/core/install/harness_profiles.py`                                        | contrato-alterado   | Expõe `skills_dir` por harness + árvore da skill; substitui `session_command_artifact`.   |
| Materializador                   | `.harness/harness-core/src/core/install/session_commands.py` (ou novo `session_skills.py`)          | componente-alterado | Grava a árvore da skill nos dois harnesses; limpa artefatos antigos.                      |
| Skill materializada              | `.claude/skills/encerrar-sessao/`, `.agents/skills/encerrar-sessao/`                                | componente-novo     | `SKILL.md` + `scripts/` finos.                                                            |
| Versão do core                   | `src/core/domain/config.py`, `src/core/bootstrap/init_service.py`                                   | regra-alterada      | Bump.                                                                                     |

## 6. Delta no modelo de dados

- Resumo: não há novo modelo de dados de runtime. O delta é de **artefato materializado** (de um arquivo `.md` que delega → um diretório de skill com scripts) e da constante de versão. O estado-da-sessão, as microdecisões e o commit seguem os formatos do legado (RN-N2, `MD-NNNN`, RN-N31/N32) — reusados, não alterados.
- Detalhe em: `_reversa_forward/018-encerrar-sessao-como-skill/data-delta.md`

## 7. Delta de contratos externos

| Contrato                                                      | Tipo              | Arquivo de detalhe                                                             |
| ------------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------ |
| Skill como capacidade consumida por Claude Code e Antigravity | arquivo/diretório | `_reversa_forward/018-encerrar-sessao-como-skill/interfaces/skill-contract.md` |

## 8. Plano de migração

1. **`init`** (projeto novo): materializa a skill `encerrar-sessao/` em `.claude/skills/` e `.agents/skills/`; nenhum artefato antigo a limpar.
2. **`upgrade`** (projeto existente): materializa a skill nos dois diretórios e remove os artefatos antigos (`.agent(s)/workflows/encerrar-sessao.md`, `.claude/commands/encerrar-sessao.md`), preservando terceiros.
3. **Follow-up**: re-extração (`/reversa`) reconcilia o `_reversa_sdd/`; depois `resume`/`handoff`/`clarificar` (e hooks) migram pelo mesmo padrão, em features curtas (RN-05).

## 9. Riscos e mitigações

| Risco                                                                                     | Impacto | Probabilidade | Mitigação                                                                                                                  |
| ----------------------------------------------------------------------------------------- | ------- | ------------- | -------------------------------------------------------------------------------------------------------------------------- |
| O refator de `main.py` (extrair orquestração) regride o fluxo da 016 (`COMMIT_PENDENTE`). | alto    | média         | Extrair com TDD; manter os testes da 016 verdes como rede; o serviço novo é coberto antes de trocar a borda.               |
| Scripts da skill não importam o core (PYTHONPATH/venv).                                   | alto    | média         | Script resolve raiz via git + usa o venv do core; teste de fumaça do import; erro barulhento se o core não for encontrado. |
| Materializar diretório (vários arquivos) diverge entre os dois harnesses.                 | médio   | baixa         | Árvore única agnóstica + prefixo por perfil; teste de paridade Claude/Antigravity.                                         |
| A skill no Antigravity é ativação semântica (não slash visual) e pode não disparar.       | médio   | média         | `description` rica em gatilhos (validada por `skill-spec`); teste empírico do usuário antes de propagar.                   |
| `_reversa_sdd/` fica divergente até a re-extração.                                        | baixo   | alta          | Follow-up no plano de migração; não bloqueia.                                                                              |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Serviço de orquestração de encerramento extraído e coberto por testes; fluxo da 016 (`COMMIT_PENDENTE`) preservado
- [ ] Skill `encerrar-sessao/` (SKILL.md + scripts) materializada em `.claude/skills/` e `.agents/skills/`; `skill-spec` ≥ 80
- [ ] Scripts finos importam o core e executam as três operações reusando a lógica testada; teste de fumaça do import verde
- [ ] `upgrade` migra: cria a skill e remove os artefatos antigos, preservando terceiros
- [ ] Versão bumpada nos três pontos; suíte do core verde + smoke nos dois harnesses
- [ ] `regression-watch.md` gerado

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-06-27 | Versão inicial gerada por `/reversa-plan` | reversa |
