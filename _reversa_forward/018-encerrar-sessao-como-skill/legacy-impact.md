# Legacy Impact: feature 018 — encerrar-sessao como skill versionável

> Feature `018-encerrar-sessao-como-skill` · 2026-06-28
> Âncora: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md` (extração de 2026-06-28).
> Severidade alinhada ao `/reversa-audit`: CRITICAL · HIGH · MEDIUM · LOW.

A capacidade `encerrar-sessao` deixou de ser um slash command/workflow `.md` que
delega ao binário e passou a ser uma **skill versionável** (diretório `SKILL.md`

- `scripts/`) materializada nos dois harnesses. Para não duplicar a orquestração,
  ela foi **extraída** da borda `main.py` para um serviço do core
  (`SessionCloseFlow`) consumido pela CLI **e** pelos scripts finos da skill. O core
  de domínio (`CommandService`/`GitPort`/`DecisionService`/serializer) ficou
  **intacto**.

## 1. Arquivos afetados

| Arquivo afetado                                                   | Componente (architecture.md)               | Tipo                | Severidade | Justificativa                                                                                                                                                                                                                                   |
| ----------------------------------------------------------------- | ------------------------------------------ | ------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/main.py`                                                     | Driver CLI; dispatch `cmd encerrar-sessao` | regra-alterada      | HIGH       | A orquestração do encerramento (pré-check de pendência → fechamento → ofertas) saiu da borda para `SessionCloseFlow`; o ramo agora delega. Helpers movidos para o core e reexportados. Fluxo 016/014 preservado pela rede de testes subprocess. |
| `src/core/session/close_flow.py`                                  | — (novo)                                   | componente-novo     | HIGH       | Fonte única do fluxo de encerramento, consumida por CLI e skill (D-01).                                                                                                                                                                         |
| `src/core/install/harness_profiles.py`                            | Superfície de comando no perfil (RN-N29)   | regra-alterada      | MEDIUM     | `session_command_artifact` removido; perfil passa a expor `skills_dir` por harness e os órfãos legados a limpar.                                                                                                                                |
| `src/core/install/session_commands.py`                            | Materialização incondicional (RN-N28)      | componente-extinto  | HIGH       | Substituído por `session_skills.py`; deixava de fazer sentido (gravava o `.md` que delegava).                                                                                                                                                   |
| `src/core/install/session_skills.py`                              | — (novo)                                   | componente-novo     | HIGH       | Materializa a árvore agnóstica da skill por `skills_dir` e migra os órfãos (RN-N28 reescrita, não-destrutiva).                                                                                                                                  |
| `src/core/install/local_apply.py`                                 | `apply_local_materializers`                | componente-alterado | MEDIUM     | Passa a chamar `materialize_session_skills` (sem `command_path`); ramos de hooks/settings inalterados.                                                                                                                                          |
| `src/core/install/assets/skills/encerrar-sessao/`                 | — (novo)                                   | componente-novo     | MEDIUM     | Árvore-fonte agnóstica (SKILL.md + `scripts/_bootstrap.py` + `scripts/encerrar_sessao.py`) que o materializador copia.                                                                                                                          |
| `src/core/domain/config.py`, `src/core/bootstrap/init_service.py` | Versão do core                             | regra-alterada      | LOW        | Bump `1.2.54 → 1.2.55` para o `upgrade` propagar a rematerialização.                                                                                                                                                                            |

## 2. Diff conceitual por componente

- **Orquestração de encerramento (main.py → close_flow.py).** Antes, o ramo `cmd
encerrar-sessao` em `main.py` carregava a sessão, fazia o pré-check de trabalho
  pendente (016), chamava `CommandService.execute_command`, tratava o estado
  malformado e conduzia as ofertas (014) — tudo na borda. Agora isso vive em
  `SessionCloseFlow.run(repo_path, config, *, out, err, asker, is_interactive)`,
  com IO injetável, devolvendo o código de saída. A CLI faz
  `sys.exit(SessionCloseFlow(...).run(...))`; os helpers (`pending_work_paths`,
  `conduct_commit_pendente`, `render_*`, `conduct_end_session_offers`) migraram
  para o core e são reexportados por `src.main` (compat. dos testes da 014). O
  core continua sem conhecer o harness (RN-N5).

- **Materialização (session_commands → session_skills).** A rotina única deixou
  de gravar um arquivo `.md` por perfil (conteúdo no `session_command_artifact`)
  e passou a gravar a **árvore agnóstica** da skill sob `<skills_dir>/encerrar-
sessao/`, lendo os bytes dos assets do core (mesmos para todos os harnesses).
  Continua **incondicional** (Claude + Antigravity), **não-destrutiva** e sob
  `project_path` (RN-N17). A migração remove os órfãos legados
  (`.claude/commands/encerrar-sessao.md`, `.agent/workflows/encerrar-sessao.md`,
  `.agents/workflows/encerrar-sessao.md`) via `stale_session_command_paths`,
  preservando terceiros (verificado em dogfood: `SPEC.md` intacto).

- **Perfil (RN-N29).** `session_command_artifact(command_path)` foi removido; o
  que varia por harness agora é só o `skills_dir()` (Claude `.claude/skills`,
  Antigravity `.agents/skills`, Gemini `None`) — a árvore é única. Encapsulamento
  por perfil preservado; contrato trocado.

- **Skill como artefato (assets).** Novos `SKILL.md` (front-matter com gatilhos +
  cláusula NÃO ative) e scripts finos: `_bootstrap.py` resolve a raiz via git,
  localiza `.harness/harness-core` e re-executa sob o venv do core (teste por
  `sys.prefix`); `encerrar_sessao.py` compõe `RegenService` → `SessionCloseFlow`
  sem reimplementar lógica. Erro barulhento se o core não for encontrado.

## 3. Preservadas (regras 🟢 do domain.md intactas)

- **RN-N31 — Encerramento versiona o estado num commit isolado** 🟢: `CommandService`
  inalterado; o `SessionCloseFlow` apenas o invoca.
- **RN-N32 — Commit pela porta e falha barulhenta** 🟢: `SessionCommitError`
  continua barulhento; o fluxo agora também o reporta com exit ≠ 0 sem fechar.
- **RN-N4 — Ausente ≠ malformado (falha barulhenta)** 🟢: o fluxo encerra
  barulhento no malformado e faz no-op ruidoso no ausente; o `resume` segue
  não-bloqueante na CLI.
- **RN-N5 — O core não conhece o harness** 🟢: `SessionCloseFlow` é agnóstico; o
  prefixo por harness vive no perfil (`skills_dir`).
- **RN-N17 — Footprint global zero** 🟢: o materializador da skill escreve só sob
  `project_path` (teste dedicado).
- **RN-N27 — Materialização única do `hooks.json` (gate Antigravity)** 🟢: o ramo
  de `apply_local_materializers` para hooks/settings ficou inalterado.

## 4. Modificadas (regras 🟢 alteradas — viram watch)

- **RN-N28 — Materialização incondicional dos slash commands de sessão** 🟢 →
  **alterada**: a rotina única agora grava a **árvore da skill** (não o `.md` que
  delegava) e migra os órfãos. Propriedades incondicional/não-destrutiva/footprint
  preservadas; a forma do artefato mudou. (Watch `W001`, `W003`.)
- **RN-N29 — Superfície de comando encapsulada no perfil** 🟢 → **alterada**:
  `session_command_artifact` removido; o perfil expõe `skills_dir`. (Watch `W002`.)

## 5. Observações (sem peso de regressão)

- A ativação da skill no **Antigravity** é **semântica** (por contexto, não slash
  visual) — não verificável localmente (herdado do amarelo de RN-N29/017).
  Validar contra o Antigravity real quando disponível. Sinalizado em
  `regression-watch.md#Observações`, fora do watch principal.
