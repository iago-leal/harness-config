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
  ↳ refina MD-0004 · relacionado-com MD-0006 · relacionado-com MD-0010 · estendido-por MD-0015
- **MD-0006** — hook post-merge não repassa o argumento do git ao `decisions`
  ↳ relaciona MD-0005 · relacionado-com MD-0007
- **MD-0007** — bootstrap recusa-se a instalar fora de um repositório git e oferece `git init`
  ↳ relaciona MD-0006 · relacionado-com MD-0008
- **MD-0008** — teste do adapter git portável; o CI estava silenciosamente vermelho
  ↳ relaciona MD-0007 · relacionado-com MD-0009
- **MD-0009** — actions do CI pinadas em versão exata (Node 20 → 24)
  ↳ relaciona MD-0008
- **MD-0010** — caminhos dos regression-watch pré-011 atualizados para o layout `.harness/`
  ↳ relaciona MD-0005
- **MD-0011** — Slash command de encerrar-sessao resolve a raiz via git (robusto a cwd)
  ↳ relacionado-com MD-0012
- **MD-0012** — `encerrar-sessao` resolve o core do upstream quando não há core local (fonte única)
  ↳ relaciona MD-0011 · relacionado-com MD-0013
- **MD-0013** — Caminho do cache de sync centralizado em `layout.py` (saneamento do T7)
  ↳ relaciona MD-0012 · refinado-por MD-0019
- **MD-0014** — Aposentar o gatilho `PostToolUse` (format-on-edit) no perfil Claude
  ↳ relacionado-com MD-0015
- **MD-0015** — Gate de registro de microdecisões: fingerprint no estado e soft-block único no Stop
  ↳ relaciona MD-0014, estende MD-0005 · estendido-por MD-0016 · relacionado-com MD-0017 · refinado-por MD-0018
- **MD-0016** — Lembrete do gate com identidade grossa: um soft-block por sessão, âncora como fingerprint
  ↳ estende MD-0015 · substituído-por MD-0018
- **MD-0017** — Consentimento para escrita no git ao encerrar: dois pontos de decisão, default assimétrico por borda
  ↳ relaciona MD-0015
- **MD-0018** — Aposentadoria do soft-block do Stop: o lembrete vira advisory em stderr; a garantia dura fica só no portão do encerramento
  ↳ substitui MD-0016, refina MD-0015 · relacionado-com MD-0019
- **MD-0019** — Medidor de progresso de entregáveis: `harness progress`, artefato derivado sem timestamp, alerta como achado persistente
  ↳ relaciona MD-0018, refina MD-0013 · refinado-por MD-0020
- **MD-0020** — Exportador kanban derivado da `Medicao`: namespace gerenciado por categoria, cards manuais preservados como canal de demandas
  ↳ refina MD-0019
