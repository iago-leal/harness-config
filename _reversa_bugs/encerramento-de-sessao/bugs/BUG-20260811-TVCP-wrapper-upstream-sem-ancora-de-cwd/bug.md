---
schema_version: 1
id: BUG-20260811-TVCP
display_number: 3
title: Wrapper local do upstream não ancora o cwd e o hook de SessionStart semeia .harness/ fora da raiz
status: resolved
phase: resolved
severity: medium
priority: P2
created: 2026-08-11
updated: 2026-08-11

origin:
  type: inspection
  external_ref: null

area: base-instalada
module: bootstrap
feature: resume
labels: [ambiente-operacional]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers:
    - "cwd do shell da sessão fora da raiz do projeto no momento de um SessionStart (compact/resume)"

blocking: []

relationships:
  - type: related-to
    target: BUG-20260811-XZ3B
    state: supported
    note: >-
      mesma família de defeitos de borda do ciclo de sessão; descoberto durante a
      correção do XZ3B. Promovida de proposed a supported no fix: a investigação
      confirmou o vínculo causal do episódio (o SessionStart do compact disparou
      durante a sessão de correção do XZ3B e semeou o artefato espúrio).

traceability:
  specs:
    - "_reversa_forward/020-fonte-unica-e-hooks/interfaces/shim-execution.md (o shim da 020 DEVE ancorar o cwd na raiz)"
  affected_code:
    - "harness (wrapper local da raiz do upstream, sem cd para o próprio diretório)"
    - ".harness/harness-core/src/main.py (resolução de caminhos por os.getcwd())"
    - ".claude/settings.json (hook SessionStart com matcher compact, MD-0024)"
  root_cause:
    state: confirmed
    statement: >-
      O wrapper local ./harness do upstream é anterior à feature 020 e nunca
      recebeu a âncora cd "$SCRIPT_DIR" que o render_shim() emite para os
      projetos-alvo; era o único executável da base sem âncora, e o core resolve
      todos os caminhos por os.getcwd().
    evidence:
      - "evidence/estado-espurio-harness-core.md (artefato semeado pelo hook)"
      - "evidence/reproduction.md (vermelho provado contra o wrapper antigo)"
  reproduction_tests:
    - "tests/test_shim.py::test_wrapper_local_do_upstream_ancora_o_cwd (vermelho contra git show 39ccdd4:harness)"
  regression_tests:
    - "tests/test_shim.py::test_wrapper_local_do_upstream_ancora_o_cwd (permanente na suíte; executa os bytes reais do wrapper de uma subpasta)"

spec_verdict: spec-gap  # adendo aditivo: _reversa_sdd/addenda/bug-BUG-20260811-TVCP-v001.md

change_set:
  - id: CHG-001
    kind: code
    ref: "fix/CHG-001-md0027-ancora-wrapper.diff (commit 8b3533f, MD-0027)"
  - id: CHG-002
    kind: specification
    ref: "_reversa_sdd/addenda/bug-BUG-20260811-TVCP-v001.md"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Wrapper local do upstream não ancora o cwd e o hook de SessionStart semeia .harness/ fora da raiz

## Summary

O wrapper `./harness` da raiz do repositório upstream resolve a localização do
core a partir do próprio diretório, mas preserva o cwd do chamador no `exec`.
Como o core resolve `harness.toml` e todos os caminhos de `.harness/` por
`os.getcwd()`, qualquer invocação com cwd fora da raiz opera sobre o diretório
errado. O hook de SessionStart (`${CLAUDE_PROJECT_DIR}/harness cmd resume`,
com matcher `compact` desde a MD-0024) herdou o cwd do shell da sessão, que
estava em `.harness/harness-core/`, e o `cmd resume` semeou um
`.harness/estado-da-sessao.md` espúrio ali dentro.

## Expected Behavior

Toda invocação do wrapper opera sobre a raiz do projeto onde ele mora,
independentemente do cwd do chamador. É o contrato do shim da feature 020
(`shim-execution.md`), que já faz `cd "$SCRIPT_DIR"` nos projetos instalados
e migrados; o wrapper local do upstream ficou para trás.

## Actual Behavior

Com cwd em `.harness/harness-core/`, o hook de SessionStart do compact
executou o resume com `harness.toml` inexistente (defaults) e semeou
`.harness/harness-core/.harness/estado-da-sessao.md` (227 bytes, feature
`default_feature`). O artefato apareceu como entrada não rastreada no
`git status`, dentro da árvore versionada do core.

## Steps to Reproduce

1. No repositório upstream, `cd .harness/harness-core`
2. Executar `../../harness cmd resume` (ou aguardar um SessionStart do Claude
   Code com o shell da sessão nesse cwd)
3. Observar `.harness/` recém-criado dentro de `harness-core/`

## Evidence

- `evidence/estado-espurio-harness-core.md`: conteúdo integral do arquivo
  espúrio, com timestamps e correlação com o compact da sessão.
- Episódio anterior da mesma família (memória da sessão, 2026-08): rodar o
  `encerrar_sessao.py` de dentro da pasta da skill semeava um
  `.harness/microdecisoes.md` de 1 byte ali (MD-0011 relata a variante em
  slash commands). A skill hoje ancora com `os.chdir(root)`; o wrapper não.

## Suspected Area

O wrapper `harness` da raiz do upstream (falta o `cd "$SCRIPT_DIR"` que o
`render_shim()` da 020 já emite para os projetos-alvo). O core em si é
cwd-relativo por design (fonte única: o mesmo core roda para N projetos);
a âncora é responsabilidade de quem invoca.

## Acceptance Criteria

1. O wrapper da raiz do upstream ancora o cwd no próprio diretório antes do
   `exec`, como o shim da 020.
2. Invocar o wrapper de qualquer subpasta não semeia `.harness/` fora da raiz.
3. Teste-guarda impede regressão (o conteúdo do wrapper deve conter a âncora).

## Traceability

- **Spec efetiva:** `shim-execution.md` da feature 020 define a âncora de cwd
  para o shim dos projetos-alvo; o wrapper local do upstream é anterior (era da
  cópia vendorizada) e nunca foi coberto pela letra — **spec-gap parcial**: o
  princípio existe, o artefato ficou fora do enunciado.
- **Código onde aparece:** `harness` (raiz), `src/main.py` (os.getcwd()).
- **Gatilho que expôs:** MD-0024 estendeu o SessionStart ao `compact`, que
  dispara com o cwd corrente do shell da sessão, imprevisível por natureza.

## Agent Notes

- O shim da 020 (projetos instalados/migrados) NÃO é afetado: `render_shim()`
  emite `cd "$SCRIPT_DIR"` desde a origem. O bootstrap da skill
  encerrar-sessao também ancora (`_repo_root()` via git + `os.chdir(root)`).
  A exposição restante é exclusiva do wrapper local do repositório upstream.
- Correção óbvia e de baixo risco: adicionar `cd "$SCRIPT_DIR" || exit 1`
  antes do `exec`, alinhando ao contrato do shim. Efeito colateral aceito:
  argumentos de caminho RELATIVOS passados ao wrapper invocado de outra pasta
  passam a resolver contra a raiz (caso raro; `./harness` da raiz é o uso
  normal e não muda).
- **2026-08-11, pós-registro:** correção aplicada pelo fluxo nativo de TDD
  direto (fora da cerimônia do `/reversa-debugger-fix`): âncora adicionada ao
  wrapper e teste-guarda `test_wrapper_local_do_upstream_ancora_o_cwd` em
  `test_shim.py`, que copia os bytes reais do wrapper para um layout fake e o
  invoca de uma subpasta com bash real. Vermelho comprovado contra o wrapper
  antigo (HEAD anterior); suíte 405 verdes. Ficha MD-0027; sem bump do core
  (o artefato é do repositório upstream, não do core). Veredito de spec:
  **spec-gap parcial** — o contrato de âncora existia na 020 para o shim dos
  projetos-alvo, o wrapper local ficou fora da letra.
  Os campos de closure/resolution ficam intactos para o fix formal.

## Resolution

Fechado em 2026-08-11 pelo ciclo formal do `/reversa-debugger-fix` (plano retroativo
aprovado pelo usuário; correção implementada no mesmo dia pelo fluxo de TDD direto).

- **Causa raiz (confirmed):** o wrapper local do upstream, anterior à 020, nunca recebeu
  a âncora de cwd que o `render_shim()` emite; era o único executável da base sem âncora.
  O gatilho que expôs foi o matcher `compact` do SessionStart (MD-0024) herdando o cwd
  do shell da sessão.
- **Veredito de spec (aprovado pelo usuário): spec-gap (parcial).** O contrato de âncora
  existia só para o shim dos projetos-alvo; adendo ADITIVO estende a letra a todo
  executável que invoque o core: `_reversa_sdd/addenda/bug-BUG-20260811-TVCP-v001.md`.
- **resolution_kind:** fixed.

| CHG | Tipo | Artefato | Commit |
|-----|------|----------|--------|
| CHG-001 | code | `harness` (âncora `cd "$SCRIPT_DIR" \|\| exit 1`) + teste-guarda em `test_shim.py` | `8b3533f` (MD-0027) |
| CHG-002 | specification | adendo `bug-BUG-20260811-TVCP-v001.md` | este fechamento |

Diff completo em `fix/`. **Prova vermelho→verde:** teste-guarda FALHOU contra o wrapper
antigo (`git show 39ccdd4:harness` restaurado no lugar) e passa com o corrigido; verde
final `405 passed in 22.28s` (2026-08-11, exit 0), CI verde em 3.12/3.13 no commit
`8b3533f`. Closure policy `local-software` satisfeita: regressão passando + veredito
aprovado. Relação com o XZ3B promovida a `supported` (episódio confirmado).
