# Regression-watch: Hook de busca ancorada no estado da sessão e no índice de decisões

> Identificador: `021-hook-busca-ancorada`
> Data: `2026-07-05`
> Uso: cada item deve continuar verdadeiro nas próximas extrações reversas. O agente reverso preenche o "Histórico de re-extrações" ao rodar `/reversa` de novo.

## Watch items

| ID   | Origem (arquivo, seção)                                                                                  | Regra esperada após a mudança                                                                                                                                               | Tipo de verificação | Sinal de violação                                                                                                                            |
| ---- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | `src/main.py` (ramo `cmd resume`) · `src/core/session/resume_context.py` · estende `domain.md#2.3` RN-07 | No harness **Claude**, com `session.inject_decisions_index` ligado, o `resume` anexa o índice de decisões (`decisions.index_file`) ao `additionalContext`, depois do estado | presença            | O `additionalContext` do `resume` no Claude não contém o índice mesmo com o flag ligado e o índice presente                                  |
| W002 | `src/main.py` (`enabled = active_harness == "claude" and …`) · `domain.md#2.3` RN-N5                     | O apêndice é **gated a Claude** neste corte: Gemini e Antigravity não o recebem; o gate vive na borda, sem ramificar serviço de domínio                                     | ausência            | O apêndice passa a ser injetado para Gemini/Antigravity sem o desenho de projeção próprio, ou o gate migra para dentro de um serviço do core |
| W003 | `src/main.py` (aviso + concat) · `domain.md#2.2` RN-03 / `#2.3` RN-N4                                    | Índice habilitado porém ausente/vazio → aviso em `stderr`, `resume` reinjeta ao menos o estado e encerra com exit 0                                                         | presença            | O `resume` falha (exit ≠ 0) ou deixa de reinjetar o estado quando o índice está ausente                                                      |
| W004 | `src/core/session/sinks.py` `HookContextSink` · `domain.md#2.3` RN-N8                                    | O teto de 10 000 caracteres é aplicado ao texto **somado** (estado + índice), truncando com aviso quando excede                                                             | presença            | `additionalContext` do `resume` excede 10 000 caracteres sem truncamento/aviso                                                               |
| W005 | `src/core/domain/config.py` `SessionSection.inject_decisions_index` · `domain.md#2.8` RN-N16             | O flag existe, nasce `True` (habilitado por padrão) e desativa o anexo quando `false`; tomls sem o campo herdam `True`                                                      | presença / redação  | O campo some, o default deixa de ser `True`, ou `false` não suprime o apêndice                                                               |

## Observações (sem peso de regressão)

- A extensão da entrega a **Gemini** (mesmo `HookContextSink`, custo trivial) e **Antigravity** (família arquivo, `FileProjectionSink`, sem teto — exige desenho de projeção) fica adiada como "Won't (this time)" no `requirements.md`. Não é regressão; é escopo futuro.
- A `execute_command` (`commands/service.py`), compartilhada por CLI e MCP, foi deliberadamente **não** tocada; o driver MCP não recebe o apêndice neste corte.

## Histórico de re-extrações

_(vazio — preenchido pelo agente reverso ao rodar `/reversa` novamente)_

## Arquivadas

_(vazio)_
