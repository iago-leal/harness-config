# Requirements: Artefatos de decisão dentro de `.harness/`

> Identificador: `005-decisoes-em-harness`
> Data: `2026-06-23`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA
> Precedente: `decisoes/MD-0002.md` e `decisoes/MD-0003.md` (`.harness/` como diretório neutro do harness-core)

## 1. Resumo executivo

Consolidar os artefatos de decisão sob o diretório neutro `.harness/`, no mesmo princípio que a feature 004 aplicou ao estado de sessão. `decisoes/` passa a `.harness/decisoes/` (incluindo `_cabecalho.md` e as fichas `MD-NNNN.md`) e o índice `microdecisoes.md` passa a `.harness/microdecisoes.md`. O sistema de microdecisões (formato, índice derivado, backlinks, validação) é preservado integralmente; muda apenas a localização e as referências que apontam para os caminhos antigos. Beneficiário: o mantenedor, que passa a ter todos os artefatos do harness-core agrupados num teto só, mais fácil de retomar e de transportar entre harnesses.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/code-analysis.md#2.4-módulo-decisoes` | Parser/indexador de microdecisões; inversão de grafo e compilação de backlinks em `microdecisoes.md` | 🟢 |
| `_reversa_sdd/state-machines.md#2` | Máquina de estados da `Decisão` (em-revisão/ativo/rejeitado) — preservada | 🟢 |
| `_reversa_sdd/architecture.md#5` | Dívida: backlinks por string pura; não valida ID órfão (fora do escopo desta feature) | 🟡 |
| `harness-core/src/main.py` (branch `decisions`) | Caminhos hardcoded: `decisoes_dir="decisoes"`, `output_file="microdecisoes.md"`, `header_file="decisoes/_cabecalho.md"` | 🟢 |
| `harness-core/src/core/decisions/service.py` | `load_decisions(directory)` e `compile_index(..., output_filepath, header_filepath)` já recebem os caminhos por argumento — o serviço é agnóstico ao local | 🟢 |
| `decisoes/MD-0002.md`, `decisoes/MD-0003.md` | `.harness/` adotado como diretório neutro e agnóstico a harness | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor intermitente | Achar todos os artefatos do harness num lugar só | Abre `.harness/` e encontra estado de sessão, decisões e índice juntos |
| Agente de IA (qualquer harness) | Consultar decisões antes de agir | O lembrete e o índice apontam para `.harness/microdecisoes.md` |
| Hook Stop | Validar e reindexar decisões a cada turno | `./harness decisions` lê `.harness/decisoes/` e reescreve `.harness/microdecisoes.md` |

## 4. Regras de negócio novas ou alteradas

1. **RN-N1: Local único dos artefatos de decisão** 🟢
   - `decisoes/` → `.harness/decisoes/` (fichas `MD-NNNN.md` e `_cabecalho.md`); `microdecisoes.md` → `.harness/microdecisoes.md`.
   - Tipo: alterada
2. **RN-N2: Caminhos na borda, não no domínio** 🟢
   - O `DecisionService` já é parametrizável; apenas o `main.py` (branch `decisions`) muda os três caminhos. Sem mudança na lógica de parse/índice/backlinks.
   - Tipo: alterada
3. **RN-N3: Sistema de microdecisões preservado** 🟢
   - Formato `MD-NNNN`, front-matter, índice derivado, backlinks e validação de integridade inalterados (origem: `_reversa_sdd/code-analysis.md#2.4`).
   - Tipo: nova (invariante de preservação)
4. **RN-N4: Referências externas realinhadas** 🟡
   - O guardrail global `~/.agent-memory/bin/guardrail-decisoes.sh` (vigia `decisoes/*.md`) e o hook `UserPromptSubmit` (lembrete que cita `microdecisoes.md`/`decisoes/`) passam a apontar para `.harness/`. Escopo a confirmar (são externos a este repo).
   - Tipo: alterada

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | `./harness decisions` lê `.harness/decisoes/` e escreve `.harness/microdecisoes.md` | Must | Após mover, `./harness decisions` valida zero-erros e regenera o índice no novo local | 🟢 |
| RF-02 | Mover os arquivos preservando histórico git | Must | `git mv` aplicado a `decisoes/` e `microdecisoes.md`; `git log --follow` mostra o histórico | 🟢 |
| RF-03 | Hook Stop segue funcionando sem mudança de comando | Must | `./harness decisions` (mesmo subcomando) opera no novo local; nenhum ajuste no `.claude/settings.json` | 🟢 |
| RF-04 | Referências externas atualizadas para `.harness/` | Should | Guardrail global e hook de lembrete apontam para `.harness/decisoes/` e `.harness/microdecisoes.md` | 🟡 |
| RF-05 | Sistema de microdecisões preservado | Must | Backlinks, validação e formato `MD-NNNN` idênticos antes e depois (MD-0001..0003 reindexados sem diferença semântica) | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Manutenibilidade | Todos os artefatos do harness-core sob `.harness/` | Coerência com MD-0002/MD-0003; agrupamento | 🟢 |
| Acoplamento | Caminhos só na borda (`main.py`); domínio intacto | `DecisionService` já parametrizável | 🟢 |
| Reprodutibilidade | Histórico git preservado na movimentação | `git mv` / `git log --follow` | 🟢 |
| Observabilidade | Guardrail e lembrete continuam ativos pós-mudança | Erros barulhentos; não cegar os ganchos | 🟡 |

## 7. Critérios de Aceitação

```gherkin
Cenário: reindexação no novo local
  Dado decisoes/ e microdecisoes.md movidos para .harness/
  Quando ./harness decisions é executado
  Então o grafo valida com zero erros
  E .harness/microdecisoes.md é regenerado com os mesmos backlinks de antes

Cenário: histórico preservado
  Dado que os arquivos foram movidos com git mv
  Quando rodo git log --follow em .harness/decisoes/MD-0001.md
  Então o histórico anterior à mudança aparece

Cenário (negativo): caminho antigo não ressurge
  Dado a migração concluída
  Quando inspeciono a raiz do projeto
  Então não existem mais decisoes/ nem microdecisoes.md na raiz
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 reindexação no novo local | Must | Coração da feature |
| RF-02 git mv com histórico | Must | Reprodutibilidade |
| RF-03 hook Stop intacto | Must | Não pode regredir o ciclo de decisões |
| RF-05 sistema preservado | Must | Mudança é de local, não de comportamento |
| RF-04 referências externas | Should | Material, mas escopo (externos ao repo) a confirmar no clarify |

## 9. Esclarecimentos

> Nenhuma sessão de dúvidas registrada ainda. Rode `/reversa-clarify` quando houver `[DÚVIDA]` pendente.

## 10. Lacunas

- 🟡 [DÚVIDA] Escopo das referências externas (RF-04): a 005 atualiza o guardrail global `~/.agent-memory/bin/guardrail-decisoes.sh` e o hook `UserPromptSubmit` (ambos fora deste repo), ou só o harness-core, deixando os externos como ajuste manual documentado?
- 🟡 [DÚVIDA] Localização exata do hook `UserPromptSubmit` que injeta o lembrete de consultar `microdecisoes.md` (global `~/.claude/settings.json` vs `~/.agent-memory`) — a confirmar na investigação do `/reversa-plan`.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-requirements` | reversa |
