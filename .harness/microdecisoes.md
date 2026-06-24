# Microdecisões — harness

> Índice DERIVADO por `./harness decisions` (hook Stop). Não edite à mão.
> Cada ficha vive em `.harness/decisoes/MD-NNNN.md`.

- **MD-0001** — Purga do legado e corte total dos hooks para a CLI
  ↳ refinado-por MD-0002
- **MD-0002** — Estado de sessão unificado em `.harness/` com reinjeção de contexto
  ↳ refina MD-0001 · refinado-por MD-0003 · relacionado-com MD-0004
- **MD-0003** — Reinjeção para os três harnesses e mecanismos por harness
  ↳ refina MD-0002
- **MD-0004** — Remoção da sincronização cross-harness Claude↔Gemini
  ↳ relaciona MD-0002 · refinado-por MD-0005
- **MD-0005** — harness-core como módulo per-projeto, não substituto da config global
  ↳ refina MD-0004
