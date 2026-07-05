# Roadmap: Hook de busca ancorada no estado da sessão e no índice de decisões

> Identificador: `021-hook-busca-ancorada`
> Data: `2026-07-05`
> Requirements: `_reversa_forward/021-hook-busca-ancorada/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Em vez de criar um gancho isolado, a feature **amplia a reinjeção de contexto que já existe**: o fluxo `SessionStart → ./harness cmd resume`, hoje limitado à narrativa do estado (`serializer.render_narrative`, `commands/service.py:112`), passa a anexar também o índice derivado `.harness/microdecisoes.md`. A composição do texto ampliado vira uma função pura no core (agnóstica ao harness, testável), e a borda `main.py` a costura no ramo `resume` — logo antes de `sink.emit` (`main.py:353-355`) — reusando o `HookContextSink`, cujo teto de 10 000 caracteres (`sinks.py:28`) já entrega a salvaguarda de truncamento sem código novo. A `execute_command` **não** muda de assinatura (é compartilhada com o driver MCP), o que mantém o risco de regressão baixo. Neste primeiro corte a fiação é gated para o harness Claude; o core permanece agnóstico, de modo que estender a Gemini (mesmo sink) e Antigravity (família arquivo) depois seja aditivo. O comportamento nasce ligado e é desativável por um flag tipado em `harness.toml`.

## 2. Princípios aplicados

> O projeto não tem `.reversa/principles.md` (ausente na varredura). Aplicam-se os princípios globais do mantenedor; nenhum conflito identificado.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Footprint global zero (RN-N17) | A feature só lê artefatos sob o repositório (`.harness/…`) e não escreve nada fora dele | respeita |
| Não-bloqueio dos ganchos (RN-03/RN-N4) | Índice ausente/ilegível não trava o boot: aviso em `stderr`, resume segue reinjetando ao menos o estado, exit 0 | respeita |
| Alta coesão / baixo acoplamento (Princípio nº 5) | A composição do apêndice é função pura de responsabilidade única no core; a borda só fia; sem acoplar `execute_command` ao índice | respeita |
| Configuração fora do código (Princípio nº 5.1) | Caminho do índice e liga/desliga vêm de `harness.toml` tipado (`[decisions]`/`[session]`), sem literais chumbados | respeita |
| Core agnóstico ao harness (RN-N5) | A seleção por `active_harness` fica na borda (padrão de `get_sink`); a função de composição não conhece harness | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Estender o `cmd resume`/`SessionStart` (uma injeção por sessão) em vez de novo gancho | Menor custo de tokens e reuso do trilho pronto (sink + teto); decidido no `/reversa-clarify` | Gancho `UserPromptSubmit` por turno; `PreToolUse` por busca; diretiva de comportamento pura | 🟢 |
| D-02 | Anexar o índice `microdecisoes.md` (~1,7 KB), não a pasta `decisoes/` (~31 KB) | O índice cabe no teto e traz os ponteiros; a pasta estouraria e sobrecarregaria (decisão do mantenedor) | Injetar `decisoes/*.md` na íntegra | 🟢 |
| D-03 | Compor o apêndice numa função pura no core (`session/resume_context.py`); a borda só fia | Testabilidade e coesão; **não** altera `execute_command`, cuja assinatura é compartilhada com o MCP | Alterar `execute_command`; compor na borda `main.py` | 🟢 |
| D-04 | Gate por `active_harness == "claude"` na borda | Corte Claude-first (clarify); consistente com a seleção por harness já feita em `get_sink` | Gate por família hook (incluiria Gemini); sem gate (atingiria Antigravity) | 🟢 |
| D-05 | Flag `SessionSection.inject_decisions_index: bool = True` | Habilitado por padrão e desativável por projeto (RN-05), via config tipada única | Flag em `[decisions]`; sem flag (sempre ligado) | 🟢 |
| D-06 | Ordem no texto: estado primeiro, índice depois | Sob truncamento no teto, o `HookContextSink` corta o final — sacrifica o índice antes da narrativa prioritária | Índice antes do estado | 🟢 |
| D-07 | Reusar o teto de 10 000 do `HookContextSink`, sem reimplementar truncamento | A salvaguarda RN-N8 já existe e cobre o texto ampliado ao ser emitido | Truncar na função de composição | 🟢 |
| D-08 | MCP `session_command` e Gemini ficam fora deste corte | O `SessionStart` invoca a CLI `cmd resume`, não o MCP; Gemini adiado pelo clarify (extensão trivial, mesmo sink) | Cobrir MCP e Gemini já agora | 🟡 |

## 4. Premissas

> Nenhuma. O `requirements.md` foi para o plano com zero marcadores `[DÚVIDA]` (resolvidos na Sessão 2026-07-05 de `/reversa-clarify`).

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| — | — | — |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Composição do contexto de resume | `_reversa_sdd/architecture.md#4` (Reinjeção via sink) | componente-novo | Função pura `build_decisions_appendix(fs, index_file, enabled)` em `src/core/session/resume_context.py`: lê o índice e devolve o bloco a anexar (ou `""`) |
| Configuração de sessão | `_reversa_sdd/domain.md#2.8` (RN-N16) · `config.py` `SessionSection` | regra-alterada | Novo campo `inject_decisions_index: bool = True` |
| Borda CLI — ramo `cmd resume` | `_reversa_sdd/architecture.md#1` (driver CLI) · `main.py:353-355` | regra-alterada | Após `execute_command`, se `active_harness == "claude"`, anexa o apêndice ao `result_msg` antes de `sink.emit` |
| `HookContextSink` | `_reversa_sdd/domain.md#2.3` (RN-N8) · `sinks.py` | inalterado (reusado) | Teto de 10 000 e truncamento aplicados ao texto ampliado, sem alteração |
| `CommandService.execute_command` | `commands/service.py` | inalterado (intocado) | Assinatura preservada — compartilhada com o driver MCP |

## 6. Delta no modelo de dados

- Resumo das mudanças: a seção `[session]` do `harness.toml` ganha um único campo booleano `inject_decisions_index` (default `True`). Nenhum campo removido; mudança aditiva e retrocompatível — tomls sem o campo herdam o default.
- Detalhe completo em: `_reversa_forward/021-hook-busca-ancorada/data-delta.md`

## 7. Delta de contratos externos

> n/a. A feature não toca contratos externos (HTTP, fila, gRPC, GraphQL). O formato do `additionalContext` do `SessionStart` é um contrato **interno** com o Claude Code, já documentado em `sinks.py` e `_reversa_sdd/domain.md#2.3` (RN-N8), e permanece inalterado. Diretório `interfaces/` omitido.

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| — | — | — |

## 8. Plano de migração

n/a — mudança aditiva. Instalações existentes herdam `inject_decisions_index = True` ao carregar a config; nenhum passo manual, nenhuma reescrita de `harness.toml` é necessária. Quem quiser desligar acrescenta o flag.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Estado + índice excedem 10 000 caracteres e o índice é truncado | médio | baixa | Ordem estado→índice (D-06); medição atual soma ~5,9 KB, com folga sobre o teto |
| Índice `microdecisoes.md` desatualizado (stale) no momento do resume | baixo | baixa | É o mesmo índice que o agente leria manualmente; o hook `Stop → decisions` o regenera a cada turno |
| Assimetria: Gemini usa o mesmo `HookContextSink` mas não recebe o apêndice neste corte | baixo | média | Documentado (D-08); extensão trivial numa iteração — trocar o gate `claude` por família hook |
| Sobreposição leve entre o índice e "ponteiros" já citados na narrativa | baixo | média | Aceita; o índice é curto e o ganho de orientação supera a redundância marginal |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Campo `inject_decisions_index` na `SessionSection` com default `True`, coberto por teste de parse (presente/ausente/desligado)
- [ ] `build_decisions_appendix` coberto por teste nos três casos: habilitado + índice presente → bloco com cabeçalho e conteúdo; desabilitado → `""`; índice ausente → `""` (+ aviso em `stderr` na borda)
- [ ] `cmd resume` no harness Claude anexa o índice ao `additionalContext`; Gemini/Antigravity inalterados
- [ ] Suíte do core verde + **smoke real** de `./harness cmd resume` mostrando estado + índice no JSON de `SessionStart`, e a supressão quando `inject_decisions_index = false`
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-07-05 | Versão inicial gerada por `/reversa-plan` | reversa |
