---
commit: ecaccc446a732a9819d15f56b1ee83950a839aa8
feature: saneamento do T7 (cache de sync com fonte única em layout.py)
start_time: '2026-08-11T15:18:51.921581+00:00'
status: inactive
---

## O que foi feito
- **Feature 028 — índice de decisões sob demanda (MD-0022), ciclo forward completo**: o resume deixou de injetar o índice integral de microdecisões e passou a injetar a visão compacta derivada `.harness/decisoes-recentes.md` (contagem, ponteiros e os K=10 títulos mais recentes), derivada na MESMA passada do índice nas bordas CLI `decisions` e `stop` da ponte Antigravity, ambas write-only-when-changed. Fallback autoresolvente para o índice completo quando a compacta faltar; trecho de guidance idempotente gravado pelo `init` no arquivo da engine (marcador `<!-- harness:decisoes -->`, write-once); config `DecisionsSection.compact_file`/`compact_index_size` (ge=0). Core **2.6.0**, 12/12 ações.
- **Fichas MD-0021 e MD-0022** registradas: abandono da verificação do vault Obsidian no encerramento (decisão operacional, sem código) e a visão compacta em si. **README.md** novo na raiz e ajuda da CLI corrigida.
- **Re-extração `/reversa` 2026-08-11-b, completa (7/7)**: reconciliação dirigida do delta da 028. RN-N41 revisada in-place e nova §2.26 no domain (**RN-N56/N57/N58**); **ADR 0028**; units `microdecisoes`, `comandos-customizados` e `bootstrap`; estruturais atualizados (inventory, code-analysis, data-dictionary, architecture, c4, erd, spec-impact, code-spec-matrix). Confiança do delta **~98%** (único 🟡: contagem da suíte relatada, não re-executada); **G-19** registrado (guidance write-once não retroativa, risco aceito na MD-0022). Regression-check: **028 com 8/8 verdes**; históricos das 005/007/009/012/021 atualizados; W001 da 021 **arquivado por supersessão** da 028.
- **Achado G-20/T8 fechado no mesmo dia por TDD direto (MD-0023)**: a tool MCP `process_decisions` compilava só o índice, violando a RN-N56. Novo teste em `test_mcp.py`, chamada a `compile_compact_view` após `compile_index` em `server.py`, preservando a semântica histórica do MCP (compila mesmo com erros de integridade; a compacta segue o índice). RN-N56 estendida a "Todas as Bordas". Core **2.6.1**, suíte **390 verdes**.
- **Sete commits temáticos empurrados** (`30e8298..72019de`, CI verde em 3.12 e 3.13): feat(core) da 028 em 2.6.0 → fix(core) MD-0023 em 2.6.1 (o `config.py` entrou parcialmente em cada um) → docs README → docs(reversa) forward da 028 → docs(reversa) re-extração b → chore(reversa) com 44 diretórios de skills auxiliares materializados → chore removendo o índice espúrio de 1 byte que estava **versionado** em `.harness/harness-core/.harness/`.
- **Cinco artefatos espúrios do bug de cwd removidos do disco** (índices semeados fora da raiz em `.harness/harness-core/`, `_reversa_forward/` e `_reversa_forward/028-…/`); nenhum entrou nos commits novos.
- **Medidor e kanban regenerados pós-028**: `active-requirements.json` com `current-stage: done`, extinguindo o alerta de divergência declarado × físico que o board acusava.

## Próximos passos
- **Corrigir o bug do índice relativo ao cwd** (origem dos espúrios recorrentes; ver memória da sessão e MD-0011): o `decisions` deveria resolver `.harness/` sempre pela raiz do projeto, qualquer que seja o cwd. Candidata a feature curta com teste de regressão.
- **Retomar a feature 024 pausada** (`024-oferta-commit-consentida`, 27/28 ações em coding) ou formalizar seu fechamento.
- **Propagar o core 2.6.1 à base instalada** (raiz `~/dev` e projetos migrados) quando conveniente.
- **`harness migrate` real** nos projetos com layout copiado (manual, `!`); descontinuação de `sync`/`upgrade` segue feature futura; mini-site a regenerar via `/reversa-docs`.
- 💡 Reversa 1.2.43 → 1.2.52 disponível no npm (`npx reversa update`), se quiser atualizar o framework em si.

## Pendências / bloqueios
- Sem bloqueios. Working tree limpo após os commits desta sessão, exceto este arquivo de estado e os derivados do medidor commitados no fechamento.
- Vault: abandonada a verificação no encerramento por decisão da MD-0021.

## Ponteiros
- Feature 028: `_reversa_forward/028-indice-decisoes-sob-demanda/` (requirements → roadmap → actions → regression-watch com 1ª verificação registrada); fichas `.harness/decisoes/MD-0021..MD-0023.md`; código em `core/decisions/service.py` (`compile_compact_view`, service.py:83/94), `core/session/resume_context.py`, `core/bootstrap/init_service.py` (guidance, init_service.py:169), `main.py`, `adapters/antigravity/hook_bridge.py`, `adapters/mcp/server.py`; testes nos seis `test_*.py` tocados.
- Re-extração b: `_reversa_sdd/` (domain §2.26, ADR 0028, confidence-report ~98%) e `.reversa/{state.json,plan.md}` (bloco "Re-extração 2026-08-11-b").
- Commits da sessão: `87e6500` (feat 028) → `fbd42d8` (fix MD-0023) → `9e4b418` (README) → `4be8fbd` (forward 028) → `ea8add6` (re-extração b) → `36875aa` (skills) → `72019de` (espúrio versionado).
- Decisões: base MD-0001..MD-0023; visão compacta em `.harness/decisoes-recentes.md`.
