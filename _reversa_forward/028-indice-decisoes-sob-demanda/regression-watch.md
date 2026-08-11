# Regression Watch: Índice de microdecisões leve com consulta sob demanda

> Identificador: `028-indice-decisoes-sob-demanda`
> Criado em: `2026-08-11`

## Watch items

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|---|---|---|---|---|
| W001 | `_reversa_sdd/domain.md` §2.18 (RN-N41) | O `cmd resume` (Claude, `inject_decisions_index` ativo) injeta a VISÃO COMPACTA (`decisions.compact_file`, cabeçalho `## Decisões recentes (índice completo sob demanda)`), não mais o índice integral | redação | A RN-N41 re-extraída seguir descrevendo a injeção do índice integral como comportamento vigente, sem mencionar a visão compacta |
| W002 | `_reversa_sdd/domain.md` §2.18 (RN-N41) | Fallback autoresolvente: compacta ausente + índice presente → injeta o índice integral com aviso em stderr; ambos ausentes → só o estado, com aviso | presença | A re-extração não registrar o fallback, ou registrá-lo como bloqueante/exit ≠ 0 |
| W003 | `.harness/harness-core/src/core/decisions/service.py` (`compile_compact_view`) | As duas visões são derivadas na MESMA passada, nas DUAS bordas (ramo `decisions` da CLI e `_handle_stop` da ponte Antigravity), após a validação de integridade | presença | Alguma borda derivar só o índice; ou a compacta ser derivada antes/apesar de erro de integridade |
| W004 | `.harness/harness-core/src/core/decisions/service.py` (`_write_if_changed`) | Escrita condicionada a mudança nas duas gravações: sem mudança nas fichas, nem o índice nem a compacta são regravados (mtime imóvel) | presença | Regravação incondicional em qualquer das duas visões |
| W005 | `.harness/harness-core/src/core/decisions/service.py` (`_extract_title`) | Extração de título num único ponto compartilhado pelas duas visões (regex do H1 `# MD-NNNN — título`, fallback para o ID) | presença | Duplicação da extração de título ou divergência de formato entre índice e compacta |
| W006 | `.harness/harness-core/src/core/domain/config.py` (`DecisionsSection`) | `compact_file` (default `.harness/decisoes-recentes.md`) e `compact_index_size` (default 10, `ge=0`; negativo → erro de validação barulhento; 0 degrada para cabeçalho+contagem+ponteiros) | presença | Campos ausentes, defaults alterados, ou negativo aceito em silêncio |
| W007 | `.harness/harness-core/src/core/bootstrap/init_service.py` (`_ensure_decisions_guidance`) | O `init` grava o trecho de guidance UMA única vez, idempotente pelo marcador `<!-- harness:decisoes -->`, no arquivo da engine (claude→`CLAUDE.md`, antigravity→`AGENTS.md`, gemini→`GEMINI.md`); o `upgrade` nunca o toca | presença | Re-init duplicando o trecho; upgrade reescrevendo a seção; marcador alterado |
| W008 | `_reversa_sdd/domain.md` §2 (RN-N12) | A visão compacta é artefato DERIVADO, nunca editado à mão, declarando essa natureza no próprio cabeçalho (mesma regra do índice) | redação | A re-extração tratar `decisoes-recentes.md` como artefato editável ou como fonte primária |

## Observações (fora do peso de regressão)

- O alvo de guidance do perfil antigravity era 🟡 no plan (`AGENTS.md` a confirmar); confirmado no coding e coberto por teste (`test_init_antigravity_grava_guidance_em_agents_md`). Se a engine mudar o arquivo de guidance, o mapa `_GUIDANCE_FILE_BY_HARNESS` é o único ponto a ajustar.
- O risco documentado no contrato (usuário remove o marcador mas mantém o texto → re-init duplica) é aceito por decisão de design; não é regressão.

## Histórico de re-extrações

<!-- Preenchido pelo agente reverso a cada rodada de /reversa. -->

### 2026-08-11-b — reconciliação dirigida pós-feature 028 (primeira verificação)

| ID | Veredito | Evidência |
|---|---|---|
| W001 | 🟢 | RN-N41 revisada in-place em `domain.md` §2.18: injeção da visão compacta como comportamento vigente, com nota "revisada pela 028/MD-0022 (redação original injetava o índice integral)". Glossário atualizado. |
| W002 | 🟢 | Fallback autoresolvente registrado na RN-N41 e na RN-N57 (§2.26): compacta ausente → índice integral com `Aviso:` em stderr; ambos ausentes → só o estado, exit 0. Cenários gherkin em `comandos-customizados/requirements.md`. |
| W003 | 🟢 | Confirmado no código e nos artefatos: `main.py:394` (ramo `decisions`) e `hook_bridge.py:133` (`_handle_stop`) chamam `compile_compact_view` na mesma passada, após `validate_integrity` (RN-N56; `c4-components.md`, cadeia do stop). |
| W004 | 🟢 | `_write_if_changed` (`service.py:94`) media as duas gravações (`service.py:133` compacta, `service.py:195` índice); RN-N56 e `microdecisoes/design.md` documentam mtime imóvel nas duas visões. |
| W005 | 🟢 | `_extract_title` (`service.py:83`) é o ponto único, consumido pelas duas visões (`service.py:132` e `service.py:166`); documentado na RN-N56 e no design da unit. |
| W006 | 🟢 | `config.py:45-46`: `compact_file` default `.harness/decisoes-recentes.md`, `compact_index_size` `Field(default=10, ge=0)` (negativo → erro de validação pydantic barulhento; 0 degrada — RF-08 da unit `microdecisoes/`, ERD atualizado). |
| W007 | 🟢 | `init_service.py`: marcador `DECISIONS_GUIDANCE_MARKER` (l.20), mapa `_GUIDANCE_FILE_BY_HARNESS` (l.23), `_ensure_decisions_guidance` (l.171) chamado no fim do init (l.169); `upgrade` não o invoca. RN-N58, `bootstrap/requirements.md`, `permissions.md`. |
| W008 | 🟢 | RN-N57 (§2.26) estende RN-N12 à segunda visão: artefato derivado, nunca editado à mão, natureza declarada no cabeçalho; `permissions.md` ganhou a salvaguarda de posse do artefato derivado. |

**Veredito da rodada: 🟢 sem regressão (8/8).** Nota: todo o delta da 028 existia apenas na árvore de trabalho, sem commit, nesta verificação.

## Arquivadas

<!-- Vazio. -->
