# ADR 0024: Consentimento para escrita no git ao encerrar — default assimétrico por borda

- **Status:** Aceito
- **Data:** 2026-08-11 (feature 024-oferta-commit-consentida, MD-0017; commit `5c4433d`)
- **Contexto Técnico:** `SessionCloseFlow.run` ganha `com_pendencias: bool` e o tri-estado `versionar_encerramento`; `conduct_commit_pendente` passa a devolver `bool` (oferta com pergunta de segunda ordem); `CommandService.execute_command(..., versionar_estado: bool = True)`; flags novas no `cmd encerrar-sessao` (`--com-pendencias`, `--com-commit-encerramento` ⊻ `--sem-commit-encerramento`); marker `ENCERRAMENTO_NAO_VERSIONADO` com `motivo`; skill `encerrar-sessao` 1.3.0 → 1.4.0. Core 2.1.1 → 2.2.0.
- **Escala de Confiança:** 🟢 CONFIRMADO (TDD; suíte verde; feature commitada em `5c4433d`).
- **Decisões relacionadas:** MD-0017; domain.md §2.22 (RN-N48/N49); revisa RN-N31 (o "quando" do versionamento); ADR 0025 (irmã na mesma direção: reduzir iniciativa unilateral do harness).

## Contexto e Problema

O encerramento escrevia no git por iniciativa própria em dois momentos: o pré-check abortava exigindo que o mantenedor commitasse o trabalho pendente antes de encerrar, e o fechamento sempre commitava o estado da sessão num commit isolado (RN-N31 original: versionamento incondicional). Para um mantenedor único e intermitente, isso invertia a autoridade: a ferramenta decidia o que entrava no histórico. A queixa de fundo era a mesma da 025 — o harness impunha atrito onde deveria oferecer.

## Decisão

**Subordinar toda escrita no git ao consentimento, com default assimétrico por borda.** No terminal (TTY), quem responde é o mantenedor: o pré-check de pendência vira oferta (encerrar mesmo assim, com rastro na narrativa, ou abortar) e o commit de encerramento pergunta `[S/n]` com default afirmativo. Sem TTY (agente, hook), **silêncio não autoriza**: pendência exige `--com-pendencias`, commit de encerramento exige `--com-commit-encerramento` (mutuamente exclusiva com `--sem-commit-encerramento`; ambas juntas são erro de uso barulhento). A borda MCP mantém `versionar_estado=True` por assimetria deliberada (D-04).

O desfecho não versionado nunca é silencioso (RN-N49): marker `ENCERRAMENTO_NAO_VERSIONADO` emitido após o sucesso e antes da oferta de push, com `motivo` distinguindo esquecimento (nenhuma flag) de recusa explícita — para a oferta de push não sugerir publicar supondo que o registro entrou no histórico. Com `versionar_estado=False`, o estado fecha no arquivo (âncora = HEAD, coincidentes por nada ter sido commitado), `commit_paths` é pulado e uma linha declarativa entra na narrativa (RN-N3: rastro de ato, não invenção).

## Alternativas Consideradas

- **Manter o versionamento incondicional:** descartado — era a própria queixa; a autoridade sobre o histórico é do mantenedor.
- **Default recusa também no TTY:** descartado — no terminal o custo da pergunta é zero e o commit isolado do estado continua sendo o desfecho recomendado; default afirmativo preserva o hábito.
- **Default consentimento também sem TTY:** descartado — silêncio de agente não é consentimento; a assimetria é o ponto da decisão.
- **Uma flag única `--commit`/`--no-commit`:** descartado — colapsaria dois consentimentos distintos (trabalho pendente vs estado da sessão) numa alavanca só.

## Consequências

- **Positivas:**
  - O histórico do git volta a ser integralmente do mantenedor; o harness passa de executor a ofertante.
  - Nenhum desfecho silencioso: o marker com `motivo` mantém a auditabilidade (a skill 1.4.0 reage por motivo).
  - Contrato preservado: `versionar_estado` tem default `True`, todos os chamadores existentes intactos; MCP inalterado.
- **Negativas / em aberto:**
  - Encerramentos não versionados deixam o estado fechado apenas no working tree; o commit fica a cargo do mantenedor (rastro na narrativa mitiga).
  - T028 (propagação manual da skill às cópias) permanece pendente na feature (27/28).
