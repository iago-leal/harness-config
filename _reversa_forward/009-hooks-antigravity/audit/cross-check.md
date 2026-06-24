# Cross-check: Ganchos de ciclo de vida para o Antigravity

> Identificador da feature: `009-hooks-antigravity`
> Data: `2026-06-24`
> Artefatos analisados:
>
> - `_reversa_forward/009-hooks-antigravity/requirements.md`
> - `_reversa_forward/009-hooks-antigravity/roadmap.md`
> - `_reversa_forward/009-hooks-antigravity/actions.md` — **AUSENTE** (gerado por `/reversa-to-do`)
>   Apoio de legado: `_reversa_sdd/domain.md`, `_reversa_sdd/architecture.md`

> **Escopo desta auditoria:** parcial. O `actions.md` ainda não foi gerado, então os eixos "Sanidade do actions" e "decisão → ação" ficam **diferidos**. Os eixos Cobertura (requisito → decisão), Consistência e Coerência com o legado foram auditados na íntegra sobre `requirements.md` ↔ `roadmap.md`.

## Resumo

| Severidade                    | Quantidade |
| ----------------------------- | ---------- |
| CRITICAL                      | 0          |
| HIGH                          | 0          |
| MEDIUM                        | 3          |
| LOW                           | 2          |
| Diferido (actions.md ausente) | 1          |

Veredito de leitura: **sem bloqueios.** Nenhuma decisão do roadmap contradiz regra 🟢 do `domain.md`; o desenho é fortemente coerente com RN-N5 e RN-N6. As pendências MEDIUM são refinamentos a fechar antes/durante a decomposição, não impedimentos.

## Findings

| ID   | Severidade | Eixo                                         | Descrição                                                                                                                                                                                                                                                                               | Onde está                                            |
| ---- | ---------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| A001 | MEDIUM     | Coerência com legado                         | D-06 diz que `upgrade` "reescreve o `hooks.json`", mas não restata o merge por named-hook que D-05 exige no `init`. Reescrita cega no upgrade pode apagar named-hooks de terceiros, em tensão com a garantia não-destrutiva de RN-N20.                                                  | `roadmap.md#3` (D-06) vs `domain.md#RN-N20`          |
| A002 | MEDIUM     | Consistência                                 | Colisão de namespace de IDs: as regras da feature `RN-05`/`RN-06` (requirements) coincidem com `RN-05`/`RN-06` do `domain.md` (Precedência de Executáveis / Opt-out). A citação "RN-06" no roadmap fica ambígua entre a regra da feature (adaptador de borda) e a do domínio (opt-out). | `requirements.md#4`, `roadmap.md` vs `domain.md#2.2` |
| A003 | MEDIUM     | Consistência                                 | D-04 fala em "placeholder de escopo por perfil", o que sugeriria um 5º placeholder no `template.md` e alteraria RN-N9 (invariante de 4 placeholders). O escopo deveria ser dobrado em `apply_instructions()` (`{{APPLY_HOOKS}}`), preservando RN-N9.                                    | `roadmap.md#3` (D-04) vs `domain.md#RN-N9`           |
| A004 | LOW        | Consistência                                 | Variação terminológica: requirements usa "camada de adaptação de borda" (RN-06); roadmap usa "terceiro driver de entrada / adaptador de borda" (D-02). Mesmo conceito; convém convergir o termo.                                                                                        | `requirements.md#4` vs `roadmap.md#3,#5`             |
| A005 | LOW        | Coerência com legado                         | Âncoras de citação aproximadas (`inventory.md#núcleo-python`, `architecture.md#...`): os slugs reais podem diferir levemente do citado. Cosmético.                                                                                                                                      | `roadmap.md#5`                                       |
| A006 | Diferido   | Sanidade do actions / Cobertura decisão→ação | Não avaliável: `actions.md` ainda não existe. Reexecutar `/reversa-audit` após `/reversa-to-do` para checar dependências, ciclos, `[//]` sem colisão de arquivo-alvo, e decisão→ação.                                                                                                   | —                                                    |

## Detalhe dos findings relevantes

### A001 — Merge no upgrade (MEDIUM)

D-05 define corretamente que o `init` escreve `.agents/hooks.json` com **merge por named-hook**, preservando chaves de terceiros. D-06 trata da reescrita pelo `upgrade` (para corrigir o caminho absoluto se o repositório mudar de lugar), mas não reafirma a mesma idempotência. RN-N20 garante evolução **não-destrutiva** no upgrade (preserva `.reversa/` e `.harness/decisoes/`); embora `.agents/hooks.json` não esteja na lista preservada, sobrescrever named-hooks que o usuário tenha adicionado contraria o espírito não-destrutivo. **Direção sugerida:** ao decompor em `/reversa-to-do`, garantir que init e upgrade compartilhem a mesma rotina de escrita com merge por named-hook. (Este skill não corrige; apenas aponta.)

### A002 — Colisão de IDs de regra (MEDIUM)

O template de requirements usa o formato `RN-NN` para regras da feature, que colide com a numeração histórica do `domain.md`. Não é erro factual, mas um leitor que cruze "RN-06" entre os documentos pode confundir o adaptador de borda (feature) com o opt-out (domínio). **Direção sugerida:** considerar um prefixo de feature (ex.: `F009-RN-06`) ou citar sempre as regras do legado pela âncora `_reversa_sdd/domain.md#...`. Ajuste editorial via edição manual ou nova passada de `/reversa-clarify`; este skill não altera os artefatos.

### A003 — Invariante de placeholders (MEDIUM)

RN-N9 (🟢) fixa que o prompt de instalação é montado por substituição de **quatro** placeholders. A redação de D-04 sugere um placeholder novo de escopo. A realização recomendada — mover o texto de escopo (hoje `.claude/settings.json` chumbado nas linhas estáticas do `template.md`) para dentro de `apply_instructions()`, que já alimenta `{{APPLY_HOOKS}}` — preserva o invariante. **Direção sugerida:** fixar essa abordagem na decomposição, sem expandir o conjunto de placeholders.

## Itens verificados que passaram

### Cobertura (requisito → decisão)

- RF-01 → D-01 (hooks.json no lugar do placeholder). OK
- RF-02 → D-01 + `interfaces/antigravity-hook-io.md` (matcher das tools de escrita). OK
- RF-03 → D-01 + interface (Stop → decisões). OK
- RF-04 → D-05 (init materializa `.agents/hooks.json`). OK
- RF-05 → D-02 + interface (contrato de I/O por evento). OK
- RF-06 → reuso de `FormattingService` em D-02; coerente com RN-N22/N23/N24. OK
- RF-07 → D-04 (apply_instructions sem placeholder). OK
- RF-08 → coberto pelo plano de migração e pelo critério de pronto (sem D-row dedicada). OK
- Cenários Gherkin (5) → todos rastreados a decisões/onboarding. OK

### Consistência

- IDs `RN-02`, `RN-05`, `RN-06`, `RF-04`, `RF-05` citados no roadmap existem no requirements. OK
- Nomes das tools de escrita idênticos em requirements, roadmap e interface. OK
- Sem identificadores-fantasma. OK

### Coerência com o legado

- D-02 (terceiro driver no anel de adaptadores) coerente com `architecture.md#1` (hexágono, dois drivers de entrada) e **fortemente alinhado** a RN-N5 ("o core não conhece o harness"). OK
- Reinjeção de estado permanece no `FileProjectionSink` (RN-05 da feature) — coerente com RN-N6 do domínio. OK
- Não-bloqueio do adaptador via reuso de `format_file` — coerente com RN-03. OK
- Escrita só dentro do repositório (RN-04 da feature / D-06) — coerente com RN-N17 (footprint zero). OK
- Componentes citados (`AntigravityProfile`, `init_service`, `FileProjectionSink`, `FormattingService`, `DecisionService`) existem no legado. OK

### Observação positiva (não é finding)

- RN-N15: os ganchos **git** (`pre-commit` → `format`, `post-merge` → `decisions`) já rodam independentemente do harness. Isso oferece um baseline de formatação/indexação mesmo que a estratégia D-03 (format-on-edit por evento do Antigravity) não se concretize — **reduz o impacto** do risco de runtime registrado no roadmap.

## Histórico de alterações

| Data       | Alteração                                                                                   | Autor   |
| ---------- | ------------------------------------------------------------------------------------------- | ------- |
| 2026-06-24 | Auditoria cruzada parcial (requirements ↔ roadmap; actions.md ausente) por `/reversa-audit` | reversa |
