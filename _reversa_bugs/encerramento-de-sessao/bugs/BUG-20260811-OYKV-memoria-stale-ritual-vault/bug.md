---
schema_version: 1
id: BUG-20260811-OYKV
display_number: 2
title: Memória por-projeto desatualizada reintroduz o ritual do vault abolido pela MD-0021
status: resolved
phase: resolved
severity: low
priority: P3
created: 2026-08-11
updated: 2026-08-11

origin:
  type: manual-report
  external_ref: null

area: ambiente-operacional
module: memoria-por-projeto
feature: encerramento-de-sessao
labels: [spec-gap]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20260811-XZ3B
    type: related-to
    state: supported
    evidence:
      - "relatados no mesmo episódio real de encerramento no comentarios-concursos (intake de 2026-08-11); promovida de proposed a supported no fix"

traceability:
  specs: []
  affected_code: []
  root_cause:
    state: confirmed
    statement: >-
      Memória por-projeto gravada em 2026-08-02 e nunca reconciliada com dois
      fatos posteriores (MD-0021 aboliu o ritual do vault; commit 3ff3f3f9
      reinstalou o harness via fonte única); não existe mecanismo que invalide
      memórias por-projeto quando decisões do repositório as contradizem.
    evidence:
      - "evidence/ritual-de-encerramento-de-sessao-snapshot.md (estado stale integral)"
      - ".harness/decisoes/MD-0021.md e commit 3ff3f3f9 do comentarios-concursos (os fatos que a memória contradizia)"
  reproduction_tests: []   # artefato externo não executável; verificação documental na cápsula
  regression_tests: []     # sem proteção automatizável; decisão registrada: sem salvaguarda sistêmica

spec_verdict: spec-gap  # sem adendo: nenhuma spec do harness governa memórias por-projeto de IDE (artefato externo)

change_set:
  - id: CHG-001
    kind: data-repair
    ref: "memória reescrita (antes: evidence/ritual-de-encerramento-de-sessao-snapshot.md; depois: fix/memoria-reescrita-depois.md)"

closure:
  policy: local-software
  satisfied: true
resolution_kind: data-repair
---

# Memória por-projeto desatualizada reintroduz o ritual do vault abolido pela MD-0021

## Summary

A memória por-projeto do Claude Code no `comentarios-concursos`
(`~/.claude/projects/-Users-iagoleal-dev-comentarios-concursos/memory/ritual-de-encerramento-de-sessao.md`,
gravada em 2026-08-02) prescreve, no encerramento de sessão, a atualização da nota
`Projetos/comentarios-concursos.md` no vault Obsidian com commit e push no repo do
vault. Esse ritual foi abolido pela decisão MD-0021 deste repo. A mesma memória
afirma ainda que o Harness foi desinstalado do projeto em 2026-07-31 e que não há
skill `encerrar-sessao` nem estado de sessão, quando o histórico mostra a
reinstalação (commit `3ff3f3f9`, "o projeto ganha o sistema de sessão") e a skill
atual (1.4.0) instalada. O agente que a recarrega a cada sessão reintroduz o ritual
espúrio e parte de premissas falsas sobre a presença do harness.

## Expected Behavior

Comportamento nunca especificado no core (label `spec-gap`): nenhuma spec do
harness governa a higiene das memórias por-projeto das IDEs. A expectativa
operacional, registrada na MD-0021, é que o encerramento NÃO atualize o vault; e a
expectativa geral de memória é que fato invalidado seja corrigido ou apagado, não
resservido a cada sessão.

## Actual Behavior

A memória segue ativa com dois fatos vencidos (ritual do vault; harness ausente) e
é injetada em toda sessão do projeto, contradizendo a MD-0021 e o estado real do
repositório.

## Steps to Reproduce

1. Abrir qualquer sessão do Claude Code em `/Users/iagoleal/dev/comentarios-concursos`.
2. Pedir para encerrar a sessão.
3. Observar o agente incluir a atualização da nota do vault no ritual (ou tratar o
   harness como desinstalado), guiado pela memória citada.

## Evidence

- `evidence/ritual-de-encerramento-de-sessao-snapshot.md`: cópia integral da
  memória stale como estava em 2026-08-11.

## Suspected Area

Artefato externo ao repositório: a memória por-projeto citada no Summary. Nenhum
código do harness envolvido.

## Acceptance Criteria

- A memória do projeto afetado reescrita (ou removida) refletindo: harness
  reinstalado, encerramento via skill `/encerrar-sessao`, vault fora do ritual
  (MD-0021).
- Decisão registrada sobre a salvaguarda sistêmica: vale criar aviso no fluxo de
  encerramento (ou guidance materializada) declarando que memórias que prescrevam
  passos de encerramento extras não prevalecem sobre a skill? Se sim, vira feature;
  se não, o fechamento deste bug é a higiene pontual.

## Traceability

- **Spec:** nenhuma (spec-gap). Referência de decisão: MD-0021 deste repo
  (abandono da atualização do vault no encerramento) e memória global
  `vault-obsidian-abandonado-no-encerramento.md`.
- **Código afetado:** nenhum.

## Agent Notes

- O registro NUNCA corrige: a reescrita da memória stale é ato de higiene fora
  deste skill, a executar depois do registro (o usuário já sinalizou que quer a
  lógica do vault fora).
- Ao reescrever, preservar o que segue válido na mesma memória: o remoto do vault
  chama-se `origin` (não `notas-obsidian`), e o trabalho do projeto vai direto na
  `main` com push autorizado pela instrução composta do usuário.
- **2026-08-11, pós-registro:** higiene aplicada fora da cerimônia do
  `/reversa-debugger-fix` (que permanece disponível para o fechamento formal): a
  memória `ritual-de-encerramento-de-sessao.md` do projeto `comentarios-concursos`
  foi reescrita — harness declarado reinstalado (fonte única, commit `3ff3f3f9`),
  ritual encerra com `/encerrar-sessao` e o vault Obsidian saiu do fluxo (MD-0021);
  preservados os fatos válidos (remoto do vault é `origin`; trabalho direto na
  `main`). Linha correspondente do `MEMORY.md` atualizada. Campos de
  closure/resolution intactos.

## Resolution

Fechado em 2026-08-11 pelo ciclo formal do `/reversa-debugger-fix` (plano retroativo
aprovado pelo usuário; higiene aplicada no mesmo dia, fora da cerimônia).

- **Causa raiz (confirmed):** memória de 2026-08-02 nunca reconciliada com a MD-0021 nem
  com a reinstalação do harness (`3ff3f3f9`); nenhum mecanismo invalida memórias
  por-projeto contraditas por decisões do repositório.
- **Veredito de spec (aprovado pelo usuário): spec-gap, sem adendo.** Nenhuma spec do
  harness governa memórias por-projeto de IDE; artefato externo ao repositório.
- **Decisão de salvaguarda (aprovada pelo usuário):** a higiene pontual fecha o bug;
  SEM salvaguarda sistêmica no core (episódio único não justifica feature; memória de
  IDE é artefato externo). Se o padrão reincidir, registrar bug novo com `regression-of`
  e reavaliar a salvaguarda.
- **resolution_kind:** data-repair.

| CHG | Tipo | Artefato |
|-----|------|----------|
| CHG-001 | data-repair | memória `ritual-de-encerramento-de-sessao.md` do `comentarios-concursos` reescrita (backup: snapshot em `evidence/`; estado final: `fix/memoria-reescrita-depois.md`; rollback: restaurar o snapshot) |

**Verificação:** leitura comparada snapshot × versão atual (cápsula em
`evidence/reproduction.md`); não há teste automatizável para artefato externo, e a
closure policy `local-software` é satisfeita pela verificação documental + veredito
aprovado. Relação com o XZ3B promovida a `supported` (mesmo episódio real de intake).
