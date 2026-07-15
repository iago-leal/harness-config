# Data delta: 023-granularidade-lembrete-gate

> Data: `2026-07-15`
> Base: modelo extraído em `_reversa_sdd/erd-complete.md` + campos da 022 (`SessionState`, front-matter do estado de sessão)

## 1. Campos

| Entidade | Campo | Mudança | Detalhe |
|----------|-------|---------|---------|
| `SessionState` | `gate_lembrete_fingerprint` | **semântica do valor** (schema intocado) | Antes: `sha1(âncora + HEAD + sujos ordenados)` — muda a cada arquivo tocado. Depois: `sha1(âncora)` — estável durante a sessão inteira |
| `SessionState` | `gate_encerramento_fingerprint` | nenhuma | Continua `sha1(âncora + HEAD + sujos ordenados)`: o portão precisa da finura para rearmar com trabalho novo |
| `GateVerdict` (não persistido) | `fingerprint_lembrete` | **campo novo** | Computado por `compute_lembrete_fingerprint(anchor)`; consumido só pelo ramo `--gate` |

## 2. Migração

Nenhuma. A transição é autoresolvente:

| Estado gravado | Primeiro `--gate` pós-atualização | Resultado |
|----------------|-----------------------------------|-----------|
| `gate_lembrete_fingerprint` no formato antigo (fino) | valor difere de `sha1(âncora)` | no máximo 1 lembrete; campo regravado no formato novo |
| Campo `None` (sessão nova ou pré-022) | difere | 1 lembrete se houver pendência; campo gravado |
| Campo já no formato novo | igual enquanto a âncora não mudar | silêncio até o fim da sessão |

O fechamento da sessão já zera os dois fingerprints (comportamento da 022, inalterado).

## 3. Índices, constraints, persistência

n/a — o estado vive no front-matter YAML de `.harness/estado-da-sessao.md`; sem banco, sem índice, sem constraint. O round-trip do serializer (render/parse) não muda porque os nomes e tipos dos campos são os mesmos.
