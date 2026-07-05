# Legacy-impact: Hook de busca ancorada no estado da sessão e no índice de decisões

> Identificador: `021-hook-busca-ancorada`
> Data: `2026-07-05`
> Base de comparação: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`

## 1. Arquivos afetados

| Arquivo afetado                                                             | Componente (`architecture.md`)                                  | Tipo                   | Severidade | Justificativa                                                                                                                        |
| --------------------------------------------------------------------------- | --------------------------------------------------------------- | ---------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `.harness/harness-core/src/core/domain/config.py`                           | `domain` — configuração tipada (RN-N16)                         | delta-de-dados         | LOW        | `SessionSection` ganha `inject_decisions_index: bool = True`; aditivo e retrocompatível (tomls sem o campo herdam `True`)            |
| `.harness/harness-core/src/core/session/resume_context.py` (novo)           | Serviço de sessão / reinjeção de contexto (`architecture.md#4`) | componente-novo        | LOW        | Função pura `build_decisions_appendix`, agnóstica ao harness, coberta por teste unitário; sem I/O de borda                           |
| `.harness/harness-core/src/main.py`                                         | Driver de entrada CLI (`architecture.md#1`), ramo `cmd resume`  | regra-alterada         | MEDIUM     | O `resume` passa a compor estado + índice de decisões (gated a Claude) antes do sink; altera o conteúdo observável do `SessionStart` |
| `.harness/harness-core/tests/{test_config,test_resume_context,test_cli}.py` | Suíte de testes                                                 | regra-nova (cobertura) | LOW        | +10 testes: parse do flag, função de apêndice (3 casos), fiação do resume (4 casos)                                                  |

## 2. Diff conceitual por componente

**`domain/config.py` (SessionSection).** Antes, a seção `[session]` expunha apenas `state_file`. Agora expõe também `inject_decisions_index` (default `True`), que governa se o `cmd resume` anexa o índice de decisões. É um ponto de configuração tipado, coerente com a via única (RN-N16); não há via paralela nem literal chumbado.

**`session/resume_context.py` (novo).** Encapsula a decisão "montar ou não o apêndice de decisões" numa função pura de responsabilidade única. Recebe `enabled` já resolvido pela borda (que aplica o gate por harness, preservando RN-N5) e o `index_file` da config. Devolve `""` quando desabilitado, ausente ou vazio — degradação silenciosa e segura (RN-N4). Quando presente, devolve um cabeçalho de orientação ("consulte antes de buscas amplas") seguido do índice, prefixado por separação para concatenar depois do estado.

**`main.py` (ramo `cmd resume`).** O fluxo do resume ganhou três linhas de cola: calcula `enabled = (active_harness == "claude") and session.inject_decisions_index`; avisa em `stderr` se o índice estiver habilitado mas ausente; concatena o apêndice ao `result_msg` antes de `sink.emit`. O `HookContextSink` continua truncando o texto somado no teto de 10 000 (RN-N8) sem alteração. A `execute_command` (compartilhada com o driver MCP) **não** foi tocada.

## 3. Preservadas (regras 🟢 do `domain.md` intactas)

- **RN-N5** (o core não conhece o harness): a composição é pura; o gate por `active_harness` ficou na borda, como já ocorre em `get_sink`.
- **RN-N8** (teto de 10 000 no `HookContextSink`): reusado sem alteração; o texto ampliado herda o truncamento.
- **RN-N11 / RN-N12** (caminhos de decisão por config; índice derivado): o índice é apenas **lido** de `decisions.index_file`; sua derivação pelo hook `Stop → decisions` permanece intacta.
- **RN-03 / RN-N4** (não-bloqueio; ausente ≠ falha): índice ausente/vazio degrada para "só estado" com aviso em `stderr` e exit 0; nada trava o boot.
- **RN-N16** (configuração por via única tipada): o novo flag entra pelo `HarnessConfig`, sem via paralela.
- **RN-N17** (footprint global zero): a feature só lê artefatos sob o repositório; nenhuma escrita nova, muito menos fora dele.
- **RN-07** núcleo (validação da âncora Git no resume): inalterada; o alerta de âncora continua antecedendo a narrativa.

## 4. Modificadas (regras 🟢 ampliadas ou com comportamento novo)

- **RN-07 / "Reinjeção de Contexto" (`domain.md#1.1`, `#2.3`) — ESTENDIDA.** A reinjeção do boot deixou de entregar apenas a narrativa do estado: no harness Claude, passa a anexar também o índice de decisões (`microdecisoes.md`), quando `session.inject_decisions_index` está ligado. A entrega segue via `HookContextSink` (família hook). Gemini e Antigravity permanecem inalterados neste corte.
- **Regra nova de domínio (a formalizar na re-extração):** "No resume, o harness Claude ancora a busca do agente anexando o índice de decisões ao contexto reinjetado, uma vez por sessão, respeitando o teto de reinjeção e o flag de configuração." Candidata a uma RN-N nova em `domain.md#2.3`.
