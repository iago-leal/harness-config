# Legacy Impact: Correção do no-op silencioso no `encerrar-sessao`

> Identificador: `015-corrige-encerrar-sessao-noop`
> Data: `2026-06-27`

## Arquivos afetados

| Arquivo afetado                                                     | Componente (`_reversa_sdd/`)               | Tipo            | Severidade | Justificativa                                                                                                                                                      |
| ------------------------------------------------------------------- | ------------------------------------------ | --------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/main.py` (borda `cmd`)                                         | `architecture.md#4` — Integrações de Borda | regra-nova      | HIGH       | Passa a ramificar o tratamento de erro por nome do comando; toca o caminho do `resume`/`SessionStart` — sensível, porém coberto por teste de não-regressão (RF-02) |
| `src/core/commands/service.py`                                      | `architecture.md#3` — Serviço de Comandos  | regra-alterada  | MEDIUM     | O ramo `encerrar-sessao` deixa de retornar string de erro e passa a levantar `NoActiveSessionError`; muda o contrato interno de retorno                            |
| `src/core/commands/errors.py`                                       | `architecture.md#3` — Serviço de Comandos  | componente-novo | LOW        | Nova exceção nomeada `NoActiveSessionError`, irmã de `SessionCommitError`                                                                                          |
| `src/core/domain/config.py`                                         | `architecture.md#2` — Configuração         | regra-alterada  | LOW        | Bump de versão 1.2.51 → 1.2.52                                                                                                                                     |
| `src/core/bootstrap/init_service.py`                                | `architecture.md#6` — Bootstrap            | regra-alterada  | LOW        | Bump de `current_version` 1.2.51 → 1.2.52                                                                                                                          |
| `tests/test_commands.py`, `tests/test_cli.py`, `tests/test_init.py` | (cobertura)                                | —               | —          | Novos casos de regressão dos dois no-ops; inversão do teste que cristalizava o `exit 0`; ajuste da asserção de versão                                              |

## Diff conceitual por componente

### Borda `cmd` (`main.py`) — regra-nova

Antes, um único `except MalformedSessionStateError` fazia `exit 0` incondicional, e o caminho de "sessão inativa" sequer levantava exceção (retornava string impressa antes do `exit 0` final). Agora a borda classifica a invocação pelo nome do comando — sinal que já usava para escolher o sink: `resume` (boot) preserva `exit 0` não-bloqueante; os comandos explícitos propagam `exit ≠ 0` para `MalformedSessionStateError` (hash curto) e para a nova `NoActiveSessionError`, com mensagens orientadoras. A fronteira boot × explícito, antes implícita, vira regra.

### Serviço de Comandos (`service.py`) — regra-alterada

O ramo `encerrar-sessao` trocou `return "Erro: Nenhuma sessão ativa..."` por `raise NoActiveSessionError(...)`. O serviço continua agnóstico ao harness e à borda (RN-N5): sinaliza a falha por tipo, não decide código de saída nem canal.

### Versão — regra-alterada

Bump sincronizado 1.2.51 → 1.2.52 nos três pontos (config, bootstrap, asserção de teste), condição para a propagação via `./harness upgrade` não ficar stale.

## Preservadas (regras 🟢 do `domain.md` intactas)

- **RN-N31 (commit isolado do estado):** o caminho feliz do `encerrar-sessao` e o `commit_paths` do estado permanecem idênticos; smoke confirmou commit de encerramento com âncora = HEAD de trabalho.
- **RN-N32 (commit pela porta, falha barulhenta):** preservada e agora **de fato cumprida na borda** — o falso `exit 0` que a contradizia foi eliminado.
- **RN-N5 (o core não conhece o harness):** preservada e reforçada — a decisão de exit code/canal é exclusiva da borda; o serviço só levanta exceção nomeada.
- **RN-N3 (resume reativa preservando narrativa):** intacta; o `resume` segue não-bloqueante no boot.

## Modificadas (regras 🟢 estendidas)

- **RN-N4 (ausente ≠ malformado, falha barulhenta):** estendida a uma **terceira categoria** — sessão válida porém inativa —, que antes escapava como `exit 0`. A semântica de "falha explícita, nunca silenciosa" passa a valer também no comando explícito de encerramento, não só no parsing do estado. Confidência mantida 🟢.
