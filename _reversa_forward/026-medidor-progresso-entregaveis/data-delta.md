# Data-delta: medidor de progresso de entregáveis

> Identificador: `026-medidor-progresso-entregaveis`
> Data: `2026-08-11`
> Base: `_reversa_sdd/erd-complete.md`, `_reversa_sdd/data-dictionary.md`

## 1. Campos novos

- `ProgressSection` na config canônica (`src/core/domain/config.py`): um campo, `file: str = ".harness/progresso.md"`. Seção opcional no toml; tomls existentes herdam o default sem migração (padrão da `DecisionsSection.require_registration`, feature 022).

## 2. Campos removidos

Nenhum.

## 3. Artefato derivado novo (não é estado)

`.harness/progresso.md`: segundo exemplar do padrão RN-N12 (como `microdecisoes.md`), 100% recomputável das fontes; versionado no git do projeto; **sem** timestamp de geração. A `Medicao` (dataclass do serviço) é transitória, nunca persistida — espelho do `GateVerdict`.

## 4. Migrações necessárias

Nenhuma. Primeira execução cria o arquivo; apagá-lo não perde nada (regenerável); projetos que nunca rodarem `harness progress` não ganham arquivo algum.

## 5. Invariantes preservados

- `SessionState`, fichas MD e serializer intocados (round-trip RN-N2 sem campos novos).
- `.reversa/`, `_reversa_forward/` e `_reversa_sdd/` permanecem só-leitura para o core (RN-04 do requirements).
- Idempotência byte a byte do artefato derivado: mesmas fontes → mesmos bytes (RN-01/RN-02).
