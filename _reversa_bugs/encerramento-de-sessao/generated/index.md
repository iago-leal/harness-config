# Contexto: encerramento-de-sessao — índice de bugs

> View gerada pelo protocolo do /reversa-debugger-graph em 2026-08-11. Não edite à mão.
> Source of truth: `../bugs/<ID>/bug.md`.

## Abertos (0)

Nenhum.

## Resolvidos (3)

| # | ID | Título | Sev. | Pri. | resolution_kind | Área/Módulo | Veredito de spec |
|---|----|--------|------|------|-----------------|-------------|------------------|
| 1 | BUG-20260811-XZ3B | Encerramento direto não deriva o índice de decisões nem a visão compacta | medium | P2 | fixed | core/session | spec-desatualizada (adendo v001) |
| 2 | BUG-20260811-OYKV | Memória por-projeto desatualizada reintroduz o ritual do vault abolido pela MD-0021 | low | P3 | data-repair | ambiente-operacional/memoria-por-projeto | spec-gap (sem adendo) |
| 3 | BUG-20260811-TVCP | Wrapper local do upstream não ancora o cwd e o hook de SessionStart semeia .harness/ fora da raiz | medium | P2 | fixed | base-instalada/bootstrap | spec-gap (adendo aditivo v001) |

## Travados por DONE.md (3)

BUG-20260811-XZ3B, BUG-20260811-OYKV e BUG-20260811-TVCP: pastas somente leitura desde
2026-08-11. Reabertura: remover a trava conscientemente ou registrar bug novo com
`regression-of`.
