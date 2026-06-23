# Roadmap: Artefatos de decisão dentro de `.harness/`

> Identificador: `005-decisoes-em-harness`
> Data: `2026-06-23`
> Requirements: `_reversa_forward/005-decisoes-em-harness/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Mover os artefatos de decisão para `.harness/` é uma mudança de **borda**: o domínio (`DecisionService`, `harness-core/src/core/decisions/service.py`) já é agnóstico ao local — recebe `directory`, `output_filepath` e `header_filepath` por argumento. A mudança real concentra-se nos pontos de composição que hoje **chumbam** os caminhos: o CLI (`main.py:161-163`) e o adapter MCP (`adapters/mcp/server.py:43`). O move físico é `git mv` para preservar histórico. Decisão técnica central a travar (D-01): chumbar `.harness/...` nos dois pontos (mínimo, fiel ao requirements) **versus** centralizar os três caminhos numa seção `[decisions]` do `harness.toml`, lida pelo loader já existente (`core/domain/config.py`), eliminando a duplicação entre os dois pontos de entrada. Após move + ajuste, `./harness decisions` valida o grafo e regenera `.harness/microdecisoes.md` no novo local.

## 2. Princípios aplicados

Não há `.reversa/principles.md` neste projeto (princípios formais não definidos via `/reversa-principles`). Aplicam-se os princípios globais do mantenedor (`~/.claude/CLAUDE.md`):

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Nº 5.1 — Configuração fora do código | Opção B (`[decisions]` no toml) honra; opção A (chumbar) tolera por proporcionalidade | respeita (B) / tensiona (A) |
| Nº 5 — Baixo acoplamento / fonte única | Centralizar os paths remove o drift entre `main.py` e `mcp/server.py` | respeita (B) |
| Nº 4 — Proporcionalidade | O caminho é convenção fixa (`.harness/`, MD-0002), não config tunável por projeto | tensiona (B pode ser over-config) |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | **TRAVADO (B):** Centralizar os 3 caminhos numa seção `[decisions]` do `harness.toml`, lida via `load_config` (`config.py`), defaults `.harness/decisoes`, `.harness/microdecisoes.md`, `.harness/decisoes/_cabecalho.md` | Loader pydantic já existe e já serve `[formatting]`/`[sync]`; remove a duplicação entre `main.py` e `mcp/server.py` (fonte única); honra Princípio 5.1 | (A) chumbar `.harness/...` nos dois pontos — fiel ao RN-N2, mas mantém 2 sites duplicados | 🟢 |
| D-02 | Realinhar TAMBÉM o adapter MCP `process_decisions` (`server.py:43`), não só o `main.py` | É um 2º ponto de composição com os mesmos defaults chumbados; mover sem tocá-lo deixa o MCP apontando para o local velho | manter só `main.py` (escopo literal do requirements) — recusado: cega o MCP | 🟢 |
| D-03 | Mover com `git mv` (não copiar + apagar) | Preserva histórico (`git log --follow`), RF-02 | `cp` + `rm` — perde histórico | 🟢 |
| D-04 | Domínio (`DecisionService`) e máquina de estados da `Decisão` permanecem intactos | Já parametrizável (`_reversa_sdd/code-analysis.md#2.4`, `_reversa_sdd/state-machines.md#2`); a mudança é só de local | reescrever o serviço — desnecessário | 🟢 |

## 4. Premissas

Nenhuma. As duas `[DÚVIDA]` foram resolvidas na clarify de 2026-06-23 (DÚVIDA #2 por investigação; DÚVIDA #1 diferida para a feature de config canônica). Nenhum marcador pendente foi convertido em premissa.

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| CLI composition root (`decisions`) | `harness-core/src/main.py` | regra-alterada | lê os 3 caminhos a partir de `.harness/` (via config se D-01=B) |
| Adapter MCP `process_decisions` | `harness-core/src/adapters/mcp/server.py` | contrato-alterado | defaults do tool passam a `.harness/...` |
| Loader de config | `harness-core/src/core/domain/config.py` | componente-novo | nova `DecisionsSection` pydantic (D-01=B travado) |
| `DecisionService` (domínio) | `harness-core/src/core/decisions/service.py` (`_reversa_sdd/code-analysis.md#2.4`) | inalterado | agnóstico ao local |

## 6. Delta no modelo de dados

- Resumo: **nenhuma** mudança de esquema. Apenas relocação física: `decisoes/` → `.harness/decisoes/` e `microdecisoes.md` → `.harness/microdecisoes.md`. Formato `MD-NNNN`, front-matter, índice derivado e backlinks idênticos.
- Detalhe completo em: `_reversa_forward/005-decisoes-em-harness/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| MCP tool `process_decisions` | MCP (tool) | `_reversa_forward/005-decisoes-em-harness/interfaces/mcp-process-decisions.md` |

## 8. Plano de migração

1. `git mv decisoes .harness/decisoes` e `git mv microdecisoes.md .harness/microdecisoes.md`.
2. **(D-01=B travado)** Criar `DecisionsSection` em `config.py` (defaults `.harness/...`), adicionar `[decisions]` ao `harness.toml`, e fazer `main.py:159-183` e `server.py:42-64` lerem os caminhos de `load_config().decisions` em vez de literais.
3. Rodar `./harness decisions` → valida grafo (zero erros) e regenera `.harness/microdecisoes.md`.
4. Verificar `git log --follow .harness/decisoes/MD-0001.md` (histórico preservado) e ausência de `decisoes/` / `microdecisoes.md` na raiz.
5. (Opcional) Alinhar referências de doc ao caminho novo: `src/core/install/template.md:42` (cita `decisoes/MD-0001.md`).

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Esquecer o 2º site (MCP) → drift entre CLI e MCP | médio | média | D-02 (tocar ambos); D-01=B elimina por fonte única |
| Rodar `./harness decisions` ANTES do move → índice vazio sobrescreve | médio | baixa | ordem do plano: mover antes de validar |
| Hook `Stop` (`.claude/settings.json`) quebrar | alto | baixa | comando inalterado (`./harness decisions`); só o destino interno muda (RF-03) |
| Referências de doc obsoletas apontando para a raiz | baixo | média | passo 5 (opcional) de alinhamento |

## 10. Critério de pronto

- [ ] `decisoes/` e `microdecisoes.md` não existem mais na raiz; vivem em `.harness/`
- [ ] `./harness decisions` valida zero erros e regenera `.harness/microdecisoes.md`
- [ ] `git log --follow` mostra o histórico pré-move
- [ ] `main.py` e `mcp/server.py` apontam para `.harness/` (chumbado ou via config)
- [ ] Suíte de testes verde
- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `regression-watch.md` gerado

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-plan` | reversa |
| 2026-06-23 | D-01 travado como B (caminhos via `[decisions]` no `harness.toml`) | mantenedor |
