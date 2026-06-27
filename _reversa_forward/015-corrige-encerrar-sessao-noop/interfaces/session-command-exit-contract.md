# Contrato de saída — `./harness cmd <comando>`

> Identificador: `015-corrige-encerrar-sessao-noop`
> Data: `2026-06-27`
> Tipo: contrato de CLI (exit codes + canal de mensagem). Consumido pelo harness/agente no ciclo de vida da sessão.

## Fronteira

A borda `cmd` em `main.py` é o único ponto que converte o resultado do core num **código de saída** e escolhe o **canal** (stdout vs stderr, sink de reinjeção). O core (`commands/service.py`) nunca decide exit code — sinaliza falha por **tipo de exceção** (RN-N5).

## Eixo de diferenciação

A borda classifica a invocação pelo **nome do comando** (`cmd_name_norm`), sinal já presente no despacho:

- **Boot:** `resume` — reinjeta a sessão no `SessionStart`. Não pode travar a inicialização.
- **Explícito:** `encerrar-sessao`, `handoff`, `clarificar` — invocados deliberadamente pelo usuário/agente. Falha deve ser visível.

## Matriz de saída (pós-feature 015)

| Comando                  | Condição                              | Exit                     | Canal / mensagem                                                                                                      |
| ------------------------ | ------------------------------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `resume`                 | estado válido                         | `0`                      | sink de reinjeção (stdout/hook), narrativa + rodapé                                                                   |
| `resume`                 | estado malformado (inclui hash curto) | `0`                      | aviso em `stderr`; boot prossegue (não-bloqueante)                                                                    |
| `encerrar-sessao`        | sessão ativa, âncora válida           | `0`                      | stdout: `"Sessão encerrada com sucesso..."`; dispara ofertas de fim de sessão (014)                                   |
| `encerrar-sessao`        | estado malformado / hash curto        | **≠ 0**                  | `stderr`: nomeia arquivo e causa; orienta regravar a âncora de 40 caracteres                                          |
| `encerrar-sessao`        | sessão ausente ou inativa             | **≠ 0**                  | `stderr` (`NoActiveSessionError`): distingue "nada a encerrar" de falha; orienta que a sessão reabre no boot/`resume` |
| `handoff` / `clarificar` | qualquer                              | `0` salvo erro de estado | explícitos; erro de estado malformado propaga `≠ 0`                                                                   |

## Invariantes

1. **Comando explícito nunca devolve falso sucesso:** se o efeito pretendido não aconteceu, `exit ≠ 0`. (RN-01, RN-03, RN-N32)
2. **Boot nunca trava:** `resume` jamais propaga `exit ≠ 0` por estado problemático. (RN-02, RF-02)
3. **Core agnóstico:** a decisão de exit code/canal é exclusiva da borda; o serviço de comandos só levanta exceção nomeada ou retorna texto de sucesso. (RN-N5)
4. **Fechamento intocado:** o caminho feliz do `encerrar-sessao` e o commit isolado do estado permanecem idênticos às features 013/014. (RN-N31)

## Exceções nomeadas relevantes

- `MalformedSessionStateError` (`session/errors.py`) — estado presente porém corrompido (inclui commit não-SHA1 / hash curto).
- `NoActiveSessionError` (`commands/errors.py`, **nova nesta feature**) — tentativa de encerrar sessão ausente ou inativa.
- `SessionCommitError` (`commands/errors.py`) — falha ao versionar o registro de encerramento.
