# Regression Watch: Correção do no-op silencioso no `encerrar-sessao`

> Identificador: `015-corrige-encerrar-sessao-noop`
> Data: `2026-06-27`
> O agente reverso preenche a seção "Histórico de re-extrações" ao rodar `/reversa` de novo.

## Itens de vigilância

| ID   | Origem (arquivo, seção)   | Regra esperada após a mudança                                                                                                                                                                     | Tipo de verificação | Sinal de violação                                                                                            |
| ---- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------ |
| W001 | `domain.md#2.14` (RN-N32) | `encerrar-sessao` explícito que não conclui o fechamento (estado malformado/hash curto ou sessão inativa) termina com `exit ≠ 0` e mensagem nomeada; nunca `exit 0` silencioso                    | comportamento       | `encerrar-sessao` retornando `exit 0` ao falhar, ou mensagem de erro no `stdout` em vez de `stderr`          |
| W002 | `domain.md#2.3` (RN-N4)   | `resume`/boot tolera estado malformado: `exit 0` não-bloqueante, aviso em `stderr`, `SessionStart` não trava                                                                                      | comportamento       | `resume` propagando `exit ≠ 0` sobre estado malformado                                                       |
| W003 | `domain.md#2.4` (RN-N5)   | O serviço de comandos sinaliza falha por exceção nomeada (`NoActiveSessionError`, `MalformedSessionStateError`, `SessionCommitError`); a borda `cmd` é o único ponto que decide exit code e canal | presença            | `service.py` decidindo exit code/`sys.exit`, ou voltando a retornar string de erro no ramo `encerrar-sessao` |
| W004 | `domain.md#2.14` (RN-N31) | O caminho feliz do `encerrar-sessao` permanece intocado: âncora = HEAD de trabalho, `commit_paths` versiona só o estado, commit de encerramento por cima                                          | presença            | `git add -A` no fechamento, âncora apontando para o commit de encerramento, ou ausência do commit isolado    |

## Observações (confidência original 🟡, sem peso de regressão)

- A fronteira **boot × explícito** é decidida pelo **nome do comando** (`cmd_name_norm == "resume"`). Formalização nova (RN-04 do requirements, 🟡): se um futuro comando explícito de sessão for adicionado, ele deve herdar o tratamento de `exit ≠ 0`, não o caminho não-bloqueante do `resume`.
- O estado legado de **hash curto** continua exigindo correção manual da âncora (sem auto-reparo — decisão de escopo). Se a fricção recorrer, reabrir como feature de melhoria.

## Histórico de re-extrações

> (vazio — preenchido pelo agente reverso na próxima execução de `/reversa`)

## Arquivadas

> (vazio)
