# ADR 0028: Visão compacta de decisões — derivação dupla na mesma passada, fallback autoresolvente e guidance write-once no init

- **Status:** Aceito
- **Data:** 2026-08-11 (feature 028-indice-decisoes-sob-demanda, MD-0022; não commitada na data desta extração)
- **Contexto Técnico:** `core/decisions/service.py` ganha `compile_compact_view(decisions, output_filepath, index_file, decisions_dir, max_items)` e os auxiliares compartilhados `_extract_title` (H1 com fallback no ID) e `_write_if_changed`; `build_decisions_appendix` (`resume_context.py`) ganha `compact_file` com precedência compacta→índice; `_ensure_decisions_guidance` como último passo do `initialize_project` (`init_service.py`); `DecisionsSection.compact_file` (default `.harness/decisoes-recentes.md`) e `compact_index_size` (int, `ge=0`, default 10) em `config.py`; as duas bordas (`main.py` ramo `decisions` e `_handle_stop` da `AntigravityHookBridge`) derivam a compacta logo após o índice. Core 2.5.0 → 2.6.0, suíte 389.
- **Escala de Confiança:** 🟢 CONFIRMADO (TDD, suíte 389 verde; delta na árvore de trabalho, sem commit).
- **Decisões relacionadas:** MD-0022 (`refina MD-0002`, `relaciona MD-0019`); ADR 0021 (o apêndice original do resume); domain.md §2.18 (RN-N41 revisada) e §2.26 (RN-N56/N57/N58).

## Contexto e Problema

A feature 021 injetava o **índice integral** de microdecisões no SessionStart do Claude. Com 22 fichas o custo já era perceptível, e a experiência do mantenedor em outro projeto mostrou o limite do desenho: o índice incha linearmente com a vida do projeto e a injeção a cada sessão paga esse custo inteiro mesmo quando a sessão não consulta decisão alguma. Era preciso separar **ancoragem** (saber que as decisões existem e onde estão, barato, toda sessão) de **consulta** (ler fichas específicas, sob demanda, só quando necessário) — sem quebrar o contrato do resume nem criar um segundo pipeline de escrita.

## Decisão

**Duas visões, uma passada, duas bordas (RN-N56).** A visão compacta `.harness/decisoes-recentes.md` (cabeçalho, 3 linhas de orientação, `Total: N ficha(s)`, K=10 mais recentes por ID decrescente, só `- **MD-NNNN** — título`, sem backlinks) é derivada na **mesma passada** que compila o índice completo, nas duas bordas que já o compilavam (CLI `decisions` e `_handle_stop` da ponte Antigravity). Não há comando novo, gatilho novo nem estado novo: o custo marginal é uma escrita condicionada. `compact_index_size = 0` degrada para cabeçalho + contagem + ponteiros, sem lista.

**Artefato derivado, nunca fonte (RN-N57).** A compacta estende à nova visão a regra do índice (RN-N12): regenerada por inteiro a cada passada, edição manual é sobrescrita sem aviso. `_write_if_changed` nas duas escritas mantém o mtime imóvel quando nada mudou.

**Resume com fallback autoresolvente (RN-N41 revisada).** O apêndice do SessionStart passa a injetar a compacta; se ela não existir ainda (instalação anterior à 028), cai para o índice completo com `Aviso:` em stderr — a situação se autoresolve na primeira passada de compilação seguinte. Ambos ausentes → só o estado, exit 0 sempre. O corte Claude-only da 021 permanece.

**Guidance write-once no init (RN-N58).** O `init` grava no arquivo da engine ativa (claude→CLAUDE.md, antigravity→AGENTS.md, gemini→GEMINI.md) um trecho que ensina o agente a consultar fichas sob demanda, idempotente pelo marcador `<!-- harness:decisoes -->`: presente, não regrava; ausente, faz append. O `upgrade` **jamais** toca o trecho — depois do init, o arquivo pertence ao mantenedor. Risco aceito: instalações antigas ficam com guidance defasado até intervenção manual.

## Alternativas Consideradas

- **Separar as fichas em mais arquivos/pastas por período:** descartado — a queixa era o custo da *injeção*, não o tamanho do arquivo; fragmentar o índice complicaria a consulta sem reduzir o token gasto no resume.
- **Comando novo (`decisions --compact`) ou gatilho próprio:** descartado — criaria segunda passada e segundo ponto de sincronização; derivar na mesma passada garante que compacta e índice nunca divergem.
- **Truncar o próprio índice completo:** descartado — o índice integral segue sendo o mapa de consulta (backlinks, todas as fichas); truncá-lo destruiria a função de catálogo pela qual ele existe (MD-0002).
- **Guidance regravado pelo upgrade:** descartado — o arquivo da engine é do mantenedor; reescrita automática arriscaria sobrescrever edição humana. Write-once com marcador é o mesmo padrão de consentimento das features 024/025.
- **Injetar nada e confiar só no guidance:** descartado — perderia a ancoragem barata por sessão; a compacta custa ~K linhas e mantém o agente ciente do total e dos ponteiros.

## Consequências

- **Positivas:**
  - O custo de token do SessionStart fica **O(K)** e não mais **O(N)**: independe do crescimento do acervo de fichas.
  - Nenhuma migração exigida: o fallback autoresolvente cobre instalações pré-028 até a primeira compilação.
  - Sem estado novo nem gatilho novo: a superfície de manutenção do subsistema de decisões quase não cresce.
- **Negativas / em aberto:**
  - Instalações antigas não recebem o guidance retroativamente (risco aceito da RN-N58); o mantenedor precisa colar o trecho à mão ou re-rodar o init.
  - A compacta mostra só títulos: decisão cujo título envelheceu mal fica invisível na ancoragem — mitigável pela disciplina de títulos das fichas.
  - K fixo por config (não adaptativo): projetos com rajadas de decisões podem preferir K maior; ajuste manual em `harness.toml`.
