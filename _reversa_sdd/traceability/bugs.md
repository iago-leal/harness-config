# Rastreabilidade SPEC ↔ BUG (espelho gerado)

> View gerada pelo Time Reversa Bugs em 2026-08-11. Não edite à mão.
> Source of truth: `_reversa_bugs/<contexto>/bugs/<ID>/bug.md`.

## Contexto: encerramento-de-sessao

| Bug | Título | Status | Spec efetiva | Código afetado |
|-----|--------|--------|--------------|----------------|
| BUG-20260811-XZ3B (#1) | Encerramento direto não deriva o índice de decisões nem a visão compacta | open (triaging, medium/P2) | `domain.md` §2.26, RN-N56; ADR 0028 | `core/session/close_flow.py`; `install/assets/skills/encerrar-sessao/scripts/encerrar_sessao.py` |
| BUG-20260811-OYKV (#2) | Memória por-projeto desatualizada reintroduz o ritual do vault abolido pela MD-0021 | open (triaging, low/P3) | spec-gap (referência: MD-0021) | nenhum (artefato externo: memória por-projeto do Claude Code) |
