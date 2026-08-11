# Data-delta: aposentar o soft-block do Stop

> Identificador: `025-aposentar-soft-block-stop`
> Data: `2026-08-11`
> Base: `_reversa_sdd/erd-complete.md` (SESSION_STATE, GATE_VERDICT)

## 1. Campos novos

Nenhum.

## 2. Campos removidos

Nenhum. Em particular, **não** se removem `gate_lembrete_fingerprint` (persistido no front-matter do `SESSION_STATE`) nem `fingerprint_lembrete` (transitório no `GATE_VERDICT`): ambos continuam em uso pelo advisory (roadmap D-02/D-03). A remoção exigiria migração de estados existentes e quebraria o invariante de round-trip do serializer (RN-N2) sem nenhum ganho funcional.

## 3. Mudança de semântica (sem mudança de schema)

| Artefato | Antes (022/023) | Depois (025) |
|---|---|---|
| `SESSION_STATE.gate_lembrete_fingerprint` | Limita o soft-block JSON a um por sessão | Limita o **advisory em stderr** a um por sessão; mesma escrita, mesma leitura, mesmo zeramento no `close_session` |
| `GATE_VERDICT` | Inalterado | Inalterado (produtor `gate.py` não muda) |

## 4. Migrações necessárias

Nenhuma. Transição autoresolvente, idêntica ao padrão da 023: estados com o fingerprint da sessão corrente já gravado simplesmente não emitem o advisory (o aviso daquela sessão já foi dado — comportamento correto); estados sem o campo seguem parseáveis (campo opcional desde a 022); o zeramento no fechamento (RN-N45) continua garantindo que nada vaza para a sessão seguinte.

## 5. Invariantes preservados

- Round-trip do serializer (`parse(render(x)) == x`, RN-N2): nenhum campo novo condicional.
- Arquivo de estado byte-compatível com o formato pré-022 enquanto o gate não é acionado (RN-N45).
- Fingerprints zerados por `close_session` (RN-N45).
