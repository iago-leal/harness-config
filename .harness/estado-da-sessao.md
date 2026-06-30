---
commit: b4dd820893ff8ce025ef1243ef9976f969d30498
feature: reversa-forward (roteamento) + brief da feature 015
start_time: "2026-06-30T22:24:15.028752+00:00"
status: inactive
---

## O que foi feito

- **Feature 019 (`oferta-commit-cobre-harness`) implementada, verificada e commitada.** O pré-check de pendências do `encerrar-sessao` (introduzido pela 016) excluía da oferta **todo** o diretório `.harness/`, sob a premissa falsa de que o fechamento o versiona — mas o fechamento versiona **só** `estado-da-sessao.md`. Decisões (`.harness/decisoes/MD-*.md`) e o índice (`microdecisoes.md`) caíam num vão e exigiam commit manual a cada sessão. A feature estreita o filtro de _diretório inteiro_ para _apenas o `state_file`_: todo trabalho versionável de `.harness/` passa a entrar na oferta, sem tocar no comportamento do fechamento (RN-N31/N32 preservadas). Bump **1.2.55 → 1.2.56** (config, bootstrap, test_init).
- **Descoberta de execução (T010):** o smoke com git real revelou que `git status --porcelain` colapsa subdiretório _untracked_ (mostra só o dir, não os arquivos); o adapter passou a usar `--untracked-files=all`. Registrado na memória `smoke-git-real-vs-mock-porcelain`.
- **Verificação real:** suíte do core **216 passed**; smoke end-to-end com git + `.gitignore` OK.
- **Pipeline forward completo da 019** (requirements → plan → to-do → coding); todas as 10 tarefas `done`. Artefatos em `_reversa_forward/019-oferta-commit-cobre-harness/`.
- **A 019 validou-se no próprio fechamento:** na 1ª passada o pré-check ofereceu os fontes de `.harness/harness-core/...` e poupou o `estado-da-sessao.md`; após o commit do pendente, a 2ª passada fechou limpo.
- **Trabalho commitado nesta sessão:** `4cd643c` (feat — código + bump 1.2.56), `b4dd820` (docs — trilha forward 019, âncora), `8591bbc` (commit de registro do fechamento).

## Próximos passos

- **PRIORIDADE — leveza do `microdecisoes`.** Ainda pendente: investigar por que registrar uma MD virou um mini-ADR (front-matter + 4 seções `D/PORQUÊ/DESCARTADO/ESTADO` + relações + validação de grafo) e propor enxugar. Decisão do mantenedor: priorizar à frente de novas features.
- **Push do bump 1.2.56** para o `harness-config` → consumidores recebem via `./harness upgrade`. (Decidido publicar ao fim desta sessão; conferir o CI real após o push.)
- **Re-extração** (`/reversa`) para reconciliar o `_reversa_sdd/` com a 019 (a defasagem estrutural do snapshot f009 segue valendo).
- **Avaliar `.gitignore`** para `.claude/commands/` e `.agents/workflows/` (materializações locais untracked recorrentes).

## Pendências / bloqueios

- O vão de `.harness/` no pré-check de pendências está **RESOLVIDO** nesta sessão (feature 019).
- Sem bloqueios técnicos. O único item "aberto" é o push, decidido para o fim desta sessão.

## Ponteiros

- Trilha forward da 019: `_reversa_forward/019-oferta-commit-cobre-harness/` (requirements, roadmap, investigation, data-delta, onboarding, interfaces, actions, progress.jsonl, legacy-impact, regression-watch).
- Contrato do marker de commit pendente: `_reversa_forward/019-oferta-commit-cobre-harness/interfaces/commit-pendente-marker.md`.
- Trilha forward da 015 (sessão anterior): `_reversa_forward/015-corrige-encerrar-sessao-noop/`.
- Âncora desta sessão: `b4dd820` (commit de trabalho da 019).
