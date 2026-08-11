# Data delta: Índice de microdecisões leve com consulta sob demanda

> Identificador: `028-indice-decisoes-sob-demanda`
> Data: `2026-08-11`
> Base: `_reversa_sdd/erd-complete.md` e `_reversa_sdd/data-dictionary.md`

## 1. Resumo

Dois campos novos de configuração na seção `[decisions]` do `harness.toml`, ambos com default; um artefato derivado novo em disco; nenhum campo novo no `SessionState`; nenhuma migração de fichas ou de estado.

## 2. Campos novos

### `DecisionsSection` (`core/domain/config.py`)

| Campo | Tipo | Default | Semântica |
|-------|------|---------|-----------|
| `compact_file` | `str` | `".harness/decisoes-recentes.md"` | Caminho (relativo à raiz do projeto) da visão compacta derivada. |
| `compact_index_size` | `int` | `10` | Teto K de fichas na visão compacta. `0` é válido (degrada para cabeçalho + contagem + ponteiros); negativo é erro de configuração barulhento. |

Os defaults dispensam edição dos `harness.toml` existentes: projeto que nunca ouviu falar da 028 ganha o comportamento novo no primeiro reindex após o upgrade.

## 3. Artefato derivado novo

| Artefato | Origem | Ciclo de vida |
|----------|--------|---------------|
| `.harness/decisoes-recentes.md` (path via `compact_file`) | Derivado das fichas `MD-NNNN.md` pela MESMA passada de `DecisionService` que compila o índice completo | Criado na primeira reindexação pós-upgrade; regravado só quando o conteúdo muda; sem timestamp nem valor volátil; nunca editado à mão (aviso no cabeçalho, como no índice). |

## 4. O que NÃO muda

- **`SessionState`**: nenhum campo novo (D-08). Os campos do gate (`gate_fingerprint`, `gate_lembrete_fingerprint`) seguem intocados.
- **Fichas `MD-NNNN.md`**: formato de front-matter e corpo inalterados; nenhuma migração.
- **Índice completo** (`.harness/microdecisoes.md`): formato byte-idêntico ao atual; só a POLÍTICA de escrita muda (write-only-when-changed) e o consumo no SessionStart (deixa de ser injetado quando a visão compacta existe).
- **`SessionSection.inject_decisions_index`**: mesma flag, semântica preservada em espírito (`false` → nada é injetado; `true` → injeta a visão compacta, ou o índice integral em fallback).
- **Gate de registro** (RN-N43..N47): avaliação, fingerprints e exit codes intocados.

## 5. Migração

Nenhum código de migração. Sequência autoresolvente:

1. Upgrade da fonte única → comportamento novo disponível.
2. Primeiro `resume` pós-upgrade: `compact_file` não existe → injeta o índice integral (comportamento atual) + aviso em stderr.
3. Primeiro Stop ou `harness decisions` manual → visão compacta derivada.
4. Sessões seguintes: injeção compacta. Convergência completa, sem intervenção.
