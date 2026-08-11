# Rastreabilidade SPEC ↔ BUG (espelho gerado)

> View gerada pelo Time Reversa Bugs em 2026-08-11. Não edite à mão.
> Source of truth: `_reversa_bugs/<contexto>/bugs/<ID>/bug.md`.

## Contexto: encerramento-de-sessao

| Bug | Título | Status | Spec efetiva | Código afetado |
|-----|--------|--------|--------------|----------------|
| BUG-20260811-XZ3B (#1) | Encerramento direto não deriva o índice de decisões nem a visão compacta | resolved (fixed, 2026-08-11; DONE) | `domain.md` §2.26, RN-N56; ADR 0028; adendo `addenda/bug-BUG-20260811-XZ3B-v001.md` (spec-desatualizada) | `core/session/close_flow.py`; `core/decisions/service.py`; `adapters/mcp/server.py`; `core/commands/service.py` |
| BUG-20260811-OYKV (#2) | Memória por-projeto desatualizada reintroduz o ritual do vault abolido pela MD-0021 | resolved (data-repair, 2026-08-11; DONE) | spec-gap sem adendo (referência: MD-0021) | nenhum (artefato externo: memória por-projeto do Claude Code, reescrita) |
| BUG-20260811-TVCP (#3) | Wrapper local do upstream não ancora o cwd e o hook de SessionStart semeia .harness/ fora da raiz | resolved (fixed, 2026-08-11; DONE) | adendo aditivo `addenda/bug-BUG-20260811-TVCP-v001.md` (spec-gap parcial sobre `shim-execution.md` da 020) | `harness` (wrapper da raiz, corrigido); `tests/test_shim.py` (guarda) |
