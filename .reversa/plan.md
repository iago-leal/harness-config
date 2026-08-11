# Plano de Exploração — harness

> Criado pelo Reversa em 2026-06-21
> Marque cada tarefa com ✅ quando concluída.
> Você pode editar este plano antes de iniciar: adicione, remova ou reordene tarefas conforme necessário.

---

## Fase 1: Reconhecimento 🔍

- [x] **Scout** — Mapeamento de estrutura de pastas e tecnologias
- [x] **Scout** — Análise de dependências e gerenciadores de pacotes
- [x] **Scout** — Identificação de entry points, CI/CD e configurações

## Decisão de organização das specs 🗂️

> Entre o Scout e o Arqueólogo, o Reversa pergunta como você quer organizar as specs (por módulo, caso de uso, endpoint, híbrida, por features ou customizada). A escolha fica persistida em `.reversa/config.toml` na seção `[specs]` e não será reagendada em execuções futures. Para reapresentar o menu, remova manualmente a seção.

## Fase 2: Escavação 🏗️

- [x] **Archaeologist** — Análise do módulo `harness-core`

## Fase 3: Interpretação 🧠

- [x] **Detetive** — Arqueologia Git e ADRs retroativos
- [x] **Detetive** — Regras de negócio implícitas e máquinas de estado
- [x] **Detetive** — Matriz de permissões (RBAC/ACL)
- [x] **Arquiteto** — Diagramas C4 (Contexto, Containers, Componentes)
- [x] **Arquiteto** — ERD completo e integrações externas
- [x] **Arquiteto** — Spec Impact Matrix

## Fase 4: Geração 📝

- [x] **Redator** — Specs SDD por componente
- [x] **Redator** — Code/Spec Matrix

## Fase 5: Revisão ✅

- [x] **Revisor** — Relatório de confiança final

---

## Agentes Independentes

> Execute estes agentes quando os recursos estiverem disponíveis — podem rodar in-place em qualquer fase.

- [N/A] **Visor** — Análise de interface via screenshots — sem interface (CLI puro, sem telas)
- [N/A] **Data Master** — Análise completa do banco de dados — sem banco de dados no projeto
- [N/A] **Design System** — Extração de tokens de design — sem CSS/tema (o único `style.css` do repo é da documentação gerada pelo próprio Reversa, não da aplicação)
- [N/A] **Tracer** — Análise dinâmica (requer sistema acessível) — harness é uma CLI stateless invocada por agentes, sem processo de longa duração para instrumentar

_Reavaliado em 2026-07-05: nenhum recurso aplicável neste projeto; agentes marcados N/A em vez de pendentes._

## Re-extração 2026-07-05 (reconciliação pós-features 019-021 + defasagem estrutural 009)

> Escopo: Scout/Archaeologist/Architect fazem re-extração estrutural ampla (inventory.md, code-analysis.md,
> c4-components.md, spec-impact-matrix.md estavam congelados desde a feature 009). Detective/Writer fazem
> reconciliação incremental para as features 019 (smoke real de git), 020 (fonte única / `harness migrate`)
> e 021 (hook de busca ancorada nas microdecisões). Reviewer atualiza o relatório de confiança. Encerra com
> regression-check (step-04) contra os regression-watch das três features.

- [x] **Scout** — re-extração estrutural (inventory, dependencies, surface.json)
- [x] **Archaeologist** — re-extração estrutural (code-analysis, data-dictionary, modules.json)
- [x] **Detective** — reconciliação incremental (domain, state-machines, permissions, ADRs 019-021)
- [x] **Architect** — re-extração estrutural (architecture, c4-\*, erd-complete, spec-impact-matrix)
- [x] **Writer** — reconciliação incremental (specs SDD por componente, code-spec-matrix)
- [x] **Reviewer** — atualização do relatório de confiança
- [x] **Regression-check** — veredito dos watch items de 019/020/021 (+ verificação completa das 21 features)

## Re-extração 2026-07-15 (reconciliação pós-MD-0014 e features 022-023 — gate de microdecisões)

> Escopo: reconciliação incremental do delta desde 2026-07-05. MD-0014 aposentou o gatilho
> PostToolUse (format-on-edit) no perfil Claude; a feature 022 introduziu o gate de registro
> obrigatório de microdecisões (novo módulo `core/decisions/gate.py`, 3º portão no
> `close_flow.py`, ramo `decisions --gate` no `main.py`, fingerprint persistido no estado);
> a feature 023 calibrou o lembrete com dupla identidade (grossa no Stop, fina no portão).
> Scout/Archaeologist atualizam os estruturais no delta (gate.py, main.py, close_flow.py);
> Detective/Writer reconciliam regras, ADRs e specs (unit `microdecisoes`, `format-on-edit`,
> `session`); Architect atualiza c4/erd/spec-impact; Reviewer fecha o relatório de confiança.
> Encerra com regression-check (step-04) — primeira verificação de 022 (W001-W010) e
> 023 (W001-W006) + varredura completa das 23 features.

- [x] **Scout** — atualização estrutural no delta (inventory, dependencies, surface.json)
- [x] **Archaeologist** — atualização estrutural no delta (code-analysis, data-dictionary, modules.json)
- [x] **Detective** — reconciliação incremental (domain, state-machines, permissions, ADRs 022-023 + MD-0014)
- [x] **Architect** — atualização estrutural (architecture, c4-\*, erd-complete, spec-impact-matrix)
- [x] **Writer** — reconciliação incremental (units `microdecisoes`, `format-on-edit`, `session`, `comandos-customizados`; code-spec-matrix)
- [x] **Reviewer** — atualização do relatório de confiança
- [x] **Regression-check** — primeira verificação de 022/023 + varredura completa das 23 features

## Re-extração 2026-08-11 (reconciliação pós-features 024-027 — consentimento, aposentadoria do soft-block, medidor e kanban)

> Escopo: reconciliação incremental do delta desde 2026-07-15 (âncora 8348e48). Quatro
> features do ciclo forward: 024 (MD-0017) condicionou toda escrita no git ao encerrar a
> consentimento explícito, com default assimétrico por borda e marker
> ENCERRAMENTO_NAO_VERSIONADO (`close_flow.py`, skill encerrar-sessao, core 2.2.0);
> 025 (MD-0018) aposentou o soft-block do hook Stop — o gate vira advisory puro em stderr
> e o único portão duro fica no encerramento (core 2.3.0); 026 (MD-0019) criou o medidor
> read-only de entregáveis `harness progress` (novo módulo `core/progress/`:
> service/render/stages; markdown derivado sem timestamp, --json, --em-hook; core 2.4.0);
> 027 (MD-0020) somou o exportador kanban derivado da mesma `Medicao`
> (`core/progress/kanban.py`, board `.vscode/vscode-kanban.json` com namespace `harness`
> e cards manuais preservados como canal de demandas; core 2.5.0). Atenção: 025/026/027
> existem apenas na árvore de trabalho, ainda sem commit — a re-extração lê a árvore.
> Scout/Archaeologist atualizam os estruturais no delta; Detective reconcilia regras,
> máquinas de estado e ADRs 0024-0027; Architect atualiza c4/erd/spec-impact; Writer
> reconcilia as units (`session`, `microdecisoes`, nova unit `progress`); Reviewer fecha
> o relatório de confiança. Encerra com regression-check (step-04): primeira verificação
> de 024/025/026/027 + varredura das 27 features, resolvendo as pendências de
> reconciliação que alimentam os 3 alertas do medidor.

- [x] **Scout** — atualização estrutural no delta (inventory, dependencies, surface.json)
- [x] **Archaeologist** — atualização estrutural no delta (code-analysis, data-dictionary, modules.json)
- [x] **Detective** — reconciliação incremental (domain, state-machines, permissions, ADRs 0024-0027)
- [x] **Architect** — atualização estrutural (architecture, c4-\*, erd-complete, spec-impact-matrix)
- [x] **Writer** — reconciliação incremental (units `session`, `microdecisoes`, nova `progress`; code-spec-matrix)
- [x] **Reviewer** — atualização do relatório de confiança
- [x] **Regression-check** — primeira verificação de 024/025/026/027 + varredura das 27 features

## Re-extração 2026-08-11-b (reconciliação pós-feature 028 — índice de decisões sob demanda)

> Escopo: reconciliação incremental do delta desde a rodada 024-027 (mesma data, mais
> cedo). Uma feature do ciclo forward: 028 (MD-0022) substituiu a injeção do índice
> integral de microdecisões no SessionStart por uma visão compacta derivada
> (`.harness/decisoes-recentes.md`: contagem, ponteiros, K=10 mais recentes só com
> títulos), derivada na MESMA passada do índice nas duas bordas (CLI `decisions` e
> `_handle_stop` da ponte Antigravity), com write-only-when-changed nas duas escritas,
> fallback autoresolvente para o índice completo no resume e trecho de guidance
> idempotente gravado pelo init no arquivo da engine (marcador `<!-- harness:decisoes -->`).
> Config: `DecisionsSection.compact_file`/`compact_index_size` (ge=0). Core 2.6.0,
> suíte 389. Também no delta: MD-0021 (abandono do vault Obsidian no encerramento,
> decisão operacional sem código), README.md novo na raiz e ajuda da CLI corrigida.
> Atenção: todo o delta existe apenas na árvore de trabalho, sem commit.
> Detective revisa a RN-N41 in-place e cria o ADR 0028; Writer reconcilia as units
> `microdecisoes` e `session`; encerra com regression-check (step-04): primeira
> verificação da 028 (W001-W008) + varredura dirigida das features tocadas pelo diff.

- [x] **Scout** ✅ — atualização estrutural no delta (inventory, surface.json)
- [x] **Archaeologist** ✅ — atualização estrutural no delta (code-analysis, data-dictionary, modules.json)
- [x] **Detective** ✅ — reconciliação incremental (domain: RN-N41 revisada + §2.26 nova; permissions; ADR 0028)
- [x] **Architect** ✅ — atualização estrutural (architecture, c4-components, erd-complete, spec-impact-matrix)
- [x] **Writer** ✅ — reconciliação incremental (units `microdecisoes`, `comandos-customizados` e `bootstrap` — o contrato do resume vive em comandos-customizados, `session` não muda na 028; code-spec-matrix)
- [x] **Reviewer** ✅ — atualização do relatório de confiança (delta 028 ~98% 🟢; G-19 registrado; nenhuma pergunta nova)
- [x] **Regression-check** ✅ — primeira verificação da 028 (W001-W008: 8/8 🟢) + varredura dirigida (005/007/009/012/021 verdes; W001 da 021 arquivado por supersessão da 028; achado G-20/T8: MCP `process_decisions` não derivava a compacta — fechado no mesmo dia por TDD direto, MD-0023, core 2.6.1)
