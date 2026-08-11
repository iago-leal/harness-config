---
schema_version: 1
id: BUG-20260811-XZ3B
display_number: 1
title: Encerramento direto não deriva o índice de decisões nem a visão compacta
status: open
phase: triaging
severity: medium
priority: P2
created: 2026-08-11
updated: 2026-08-11

origin:
  type: manual-report
  external_ref: null

area: core
module: session
feature: encerramento-de-sessao
labels: [base-instalada]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs:
    - "_reversa_sdd/domain.md#2.26 (RN-N56: Duas Visões, Uma Passada, Todas as Bordas)"
    - "_reversa_sdd/adrs/0028 (visão compacta de decisões, MD-0022)"
  affected_code:
    - ".harness/harness-core/src/core/session/close_flow.py"
    - ".harness/harness-core/src/core/install/assets/skills/encerrar-sessao/scripts/encerrar_sessao.py"
    - ".harness/harness-core/src/core/decisions/service.py"
  root_cause: null
  reproduction_tests: []
  regression_tests: []

spec_verdict: null

change_set: []

closure:
  policy: local-software
  satisfied: false
resolution_kind: null
---

# Encerramento direto não deriva o índice de decisões nem a visão compacta

## Summary

Uma sessão encerrada pela borda direta do fluxo de fechamento (o script
`encerrar_sessao.py` da skill, rodado no terminal, ou qualquer caminho que não passe
pelo hook Stop de uma IDE) não recompila `.harness/microdecisoes.md` nem deriva
`.harness/decisoes-recentes.md`. Ficha de microdecisão criada durante a sessão fica
invisível às duas visões até que outra borda (CLI `decisions`, hook Stop, MCP) rode
por acaso. Observado no projeto instalado `comentarios-concursos`: a ficha `MD-0001`
existia e estava commitada, a sessão foi encerrada com commit de encerramento, e o
índice seguia vazio ("Total: 0 fichas") até recompilação manual em 2026-08-11.

## Expected Behavior

A RN-N56 (spec efetiva, `_reversa_sdd/domain.md` §2.26, estendida pela MD-0023 a
"Todas as Bordas") determina que toda borda que processa decisões derive, na mesma
passada e write-only-when-changed, as duas visões: índice completo e visão compacta.
O fluxo de encerramento processa decisões (o gate da MD-0015 lê as fichas para
decidir se bloqueia o fechamento), portanto o encerramento deveria deixar índice e
visão compacta coerentes com as fichas existentes ao fechar a sessão.

## Actual Behavior

O fluxo de encerramento roda o gate de decisões mas não compila visão alguma. A
varredura no core (2.6.1) mostra `compile_index`/`compile_compact_view` presentes
apenas nas bordas CLI (`src/main.py:393`), MCP (`src/adapters/mcp/server.py:84`) e
Antigravity (`src/adapters/antigravity/hook_bridge.py:130`); nenhuma chamada em
`close_flow.py` nem no script `encerrar_sessao.py`. Quando o hook Stop do Claude
Code não está por perto (execução direta no terminal), nada deriva as visões.

Sintoma colateral registrado: sem índice utilizável, o agente da sessão afetada
improvisou concatenação em zsh (`cat _cabecalho.md MD-*.md`), que estourou com
`(eval):1: no matches found` por glob sem correspondência (ver Evidence).

## Steps to Reproduce

1. Em um projeto com o harness instalado (skill `encerrar-sessao` materializada),
   criar uma ficha nova `.harness/decisoes/MD-NNNN.md` e commitá-la.
2. Sem deixar o hook Stop rodar (terminal puro), executar
   `python3 .claude/skills/encerrar-sessao/scripts/encerrar_sessao.py` até o
   fechamento completar.
3. Inspecionar `.harness/microdecisoes.md` e `.harness/decisoes-recentes.md`: a
   ficha nova não consta em nenhuma das visões.

## Evidence

- `evidence/erro-encerramento-direto.txt`: saída colada pelo usuário (erro de glob
  no zsh durante o fluxo).
- `evidence/estado-observado-20260811.md`: fotografia antes/depois no
  `comentarios-concursos` e varredura das bordas que compilam.

## Suspected Area

`src/core/session/close_flow.py` e o script fino da skill
(`assets/skills/encerrar-sessao/scripts/encerrar_sessao.py`): o fluxo de fechamento
invoca o gate de decisões sem a derivação das visões. Hipótese de causa raiz
(estado: hypothesized): a MD-0023 estendeu a RN-N56 apenas à borda MCP (fechando o
achado G-20/T8) e a borda de encerramento ficou fora da extensão, repetindo o mesmo
padrão de lacuna uma borda adiante.

## Acceptance Criteria

- Encerrar sessão por qualquer borda (script da skill no terminal, hook, MCP) deixa
  `.harness/microdecisoes.md` e `.harness/decisoes-recentes.md` coerentes com as
  fichas presentes, write-only-when-changed.
- Teste de regressão cobrindo a borda de encerramento: ficha criada na sessão,
  fechamento direto, visões coerentes ao final.
- Veredito de spec registrado: ou a RN-N56 já cobre a borda de encerramento
  (spec-correta, defeito de código), ou ganha adendo explicitando-a.

## Traceability

- **Spec:** `_reversa_sdd/domain.md` §2.26, RN-N56 (e ADR 0028). Vale conferir a
  redação exata de "Todas as Bordas" na decisão do fix.
- **Código onde aparece:** `close_flow.py`, `encerrar_sessao.py` (ausência de
  chamada); `decisions/service.py` (as funções de derivação existem e funcionam).
- **Testes existentes relacionados:** `tests/test_close_flow.py`,
  `tests/test_decisions.py`, `tests/test_mcp.py` (este último é o precedente da
  MD-0023, mesmo formato de correção).

## Agent Notes

- Correção provável é análoga à MD-0023: chamar `compile_index` +
  `compile_compact_view` na borda que falta, preservando a semântica de erro do
  fluxo (o fechamento não deve morrer se a derivação falhar? decidir e registrar).
- Ao resolver caminhos, considerar o bug conhecido do índice relativo ao cwd
  (MD-0011 e memória da sessão): o fix não deve semear artefato fora da raiz.
- Não confundir com o no-op de sessão ausente (D1 da 016): aqui a sessão existia e
  fechou com sucesso; só as visões ficaram para trás.
- **2026-08-11, pós-registro:** correção aplicada no core pelo fluxo nativo de TDD
  direto do projeto (fora da cerimônia do `/reversa-debugger-fix`, que permanece
  disponível para o fechamento formal): `SessionCloseFlow._derive_decision_views`
  chamado antes do 1º portão, não-bloqueante, sem regravação com grafo inválido e
  sem derivação com acervo vazio (fichas ausentes em `decisions.dir` — o critério
  do diretório ausente foi descartado pela verificação adversarial, pois o `init`
  sempre cria o diretório). A mesma verificação (workflow ultracode, 12 agentes,
  7 achados confirmados) revelou e corrigiu a ausência de
  `decisions.compact_file` nos excluídos do gate de registro (`gate.py`), que
  gerava DECISAO_PENDENTE espúrio. Testes: 4 novos em `test_close_flow.py`, 1
  estendido em `test_decision_gate.py` e smoke com git real em `test_cli.py`
  (suíte 397 verdes), core 2.6.2 → 2.6.3, ficha MD-0025, RN-N43/RN-N56
  atualizadas no `domain.md`. Veredito de spec: **spec-desatualizada**
  (o princípio cobria a borda, a letra não; adendo aplicado como na MD-0023).
  Dívida documentada: a borda MCP `session_command("encerrar-sessao")` segue sem
  derivar (executa pelo `CommandService`, fora do flow).
  Os campos de closure/resolution ficam intactos para o fix formal.
