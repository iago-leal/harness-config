# ADR 0018: `encerrar-sessao` entregue como skill versionável (skill como adaptador), com a orquestração extraída para o core

- **Status:** Aceito (substitui a [ADR 0017](0017-comandos-ide-materializados-no-init.md))
- **Data:** 2026-06-28 (feature 018-encerrar-sessao-como-skill)
- **Contexto Técnico:** Novo módulo `src/core/install/session_skills.py` (`materialize_session_skills`, substitui `session_commands.py` — removido); novo serviço `src/core/session/close_flow.py` (`SessionCloseFlow` + helpers reexportados por `src/main.py`); nova árvore-fonte `src/core/install/assets/skills/encerrar-sessao/` (`SKILL.md` + `scripts/_bootstrap.py` + `scripts/encerrar_sessao.py`); em `harness_profiles.py`, `session_command_artifact` removido e `skills_dir()` adicionado; `local_apply.py` passa a chamar `materialize_session_skills`. Bump `1.2.54 → 1.2.55`.
- **Escala de Confiança:** 🟢 CONFIRMADO (código as-built; 212 testes verdes; smoke real de `materialize` confirma a árvore da skill nos dois `skills_dir` e a remoção dos três órfãos preservando terceiros). 🟡 Ativação semântica da skill no Antigravity não verificável localmente (ver Consequências).
- **Decisões relacionadas:** ADR 0017 (substituída), ADR 0011 (Strategy multi-harness sem `if`s no core), ADR 0016 (materialização única `init`/`upgrade`), RN-N5 (core não conhece o harness), RN-N28/RN-N29 (reescritas), RN-N33 (nova); features 014 (ofertas de fim de sessão) e 016 (encerramento autônomo + pré-check de pendência).

## Contexto e Problema

A ADR 0017 materializava `encerrar-sessao` como slash command (Claude) e workflow (Antigravity) `.md` que delegavam a `./harness cmd encerrar-sessao`. A feature 017 e a validação por `skill-spec` mostraram, empiricamente, que **slash commands e workflows locais não são reconhecidos pelo Antigravity** — só **skills** (`.agents/skills/<nome>/SKILL.md`, com `name`+`description`) ativam, por contexto semântico. O artefato da 017 era, na prática, inerte naquele harness. Além disso, um `.md` que só delega ao binário não é versionável como capacidade (sem `version`, sem rastreabilidade própria) e não "contém" comportamento testável.

O pedido: entregar `encerrar-sessao` como **skill versionável**, válida para Claude **e** Antigravity, sem duplicar a lógica de domínio já testada (commit, microdecisões, estado) nem perder a rede de testes do `harness-core`.

## Decisão

**A skill é o adaptador.** Duas decisões compõem o desenho:

1. **Materializar a árvore de uma skill, não um `.md` que delega.** `materialize_session_skills(fs, project_path, profiles=None)` (em `src/core/install/session_skills.py`, substituindo `materialize_session_commands`) grava a **árvore agnóstica** da skill — `SKILL.md` (front-matter `name`/`description`/`version`) + `scripts/` finos — sob `<skills_dir>/encerrar-sessao/` de cada perfil. A árvore é **única** (mesmos bytes para todos os harnesses), lida dos assets do core (`src/core/install/assets/skills/encerrar-sessao/`), de modo que só o diretório-prefixo varia por harness. Permanece **incondicional** (Claude + Antigravity), **atômica**, **não-destrutiva** e sob `project_path` (footprint zero, RN-N17), reusando as garantias da ADR 0016. O que varia por harness migrou de `session_command_artifact(command_path)` (removido) para `HarnessProfile.skills_dir()`: Claude `.claude/skills`, Antigravity `.agents/skills`, Gemini `None`. A migração remove os órfãos legados (`.claude/commands/encerrar-sessao.md`, `.agent/workflows/encerrar-sessao.md`, `.agents/workflows/encerrar-sessao.md`) via `stale_session_command_paths()`, só o arquivo nomeado (RN-N28/RN-N29 reescritas).

2. **Extrair a orquestração para o core, scripts finos a consomem (não duplicam).** O fluxo de encerramento — pré-check de pendência (016) → fechamento via `CommandService` → ofertas (014) — saiu da borda `main.py` para `SessionCloseFlow.run(...) -> int` (em `src/core/session/close_flow.py`), com IO injetável. A CLI faz `sys.exit(SessionCloseFlow(...).run(...))`; o script `encerrar_sessao.py` da skill compõe `RegenService` → `SessionCloseFlow` — **fonte única**, sem duplicar lógica (DRY). `_bootstrap.py` resolve a raiz via git, localiza `.harness/harness-core` e re-executa sob o venv do core; core ausente → falha barulhenta. O core continua agnóstico ao harness (RN-N5). Detalhe em `domain.md#2.15` (RN-N33).

Escopo deliberado: **apenas `encerrar-sessao`**. O padrão "skill-como-adaptador sobre o core testado" fica como molde para `resume`/`handoff`/`clarificar` migrarem depois, em features curtas (proporcionalidade, P4).

## Alternativas Consideradas

- **Manter slash command/workflow `.md` (ADR 0017):** descartado — inerte no Antigravity (descoberta empírica de 017); não versionável como capacidade.
- **Duplicar a lógica de commit/microdecisão/estado dentro dos scripts da skill:** descartado — violaria DRY, criaria duas fontes divergentes (dívida + acoplamento) e perderia a rede de testes do core.
- **Skill que delega puro a `./harness cmd encerrar-sessao` (sem scripts):** descartado — não "contém scripts" nem é versionável de fato; e dependeria do wrapper resolvível no ambiente da skill.
- **Aposentar `CommandService`/serializer/`DecisionService` e reimplementar na skill:** descartado — perderia os testes e a fonte única de verdade; a lógica permanece no hexágono sob TDD.
- **Materializar só para o `active_harness`:** descartado — mantém-se a cobertura dupla incondicional da 010 (a capacidade deve existir nos dois harnesses).

## Consequências

- **Positivas:**
  - `encerrar-sessao` passa a funcionar de fato no Antigravity (ativação semântica por contexto) e ganha versão própria (`version` no front-matter) — rastreável e evoluível com a skill.
  - Sem duplicação: a lógica de domínio segue no core testado (212 testes verdes); os scripts são casca fina. `SessionCloseFlow` vira fonte única para CLI e skill, eliminando a orquestração duplicada na borda.
  - Reusa o molde testado da ADR 0016 (rotina única `init`+`upgrade`, escrita atômica, footprint zero) e a Strategy da ADR 0011 (conhecimento por-harness no perfil, sem `if active_harness` no serviço).
  - Migração não-destrutiva: os órfãos legados são removidos, terceiros preservados (verificado em smoke: `SPEC.md` e workflow de terceiro intactos).
- **Negativas / em aberto:**
  - A ativação semântica da skill no Antigravity (por contexto, não slash visual) **não é verificável localmente** — herdado do amarelo de 009/017. Validar contra o Antigravity real quando disponível.
  - A janela conhecida do `upgrade` stale (RN-N30) continua valendo: o primeiro `upgrade` de um alvo na versão anterior materializa com o código antigo; do bump 1.2.55 em diante o mecanismo é correto.
  - A rotina é dona do nome `encerrar-sessao` no diretório de skills: uma skill do usuário com esse mesmo nome seria sobrescrita. Documentado; demais arquivos preservados.
