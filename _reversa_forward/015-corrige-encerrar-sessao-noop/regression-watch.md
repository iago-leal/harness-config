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

### Re-extração 2026-07-05 17:00

> **Primeira verificação dos watch da 015** (nunca fora checada em rodadas anteriores). A feature 016, que veio logo em seguida, **revisou deliberadamente** parte da regra de W001/W003: sessão inativa deixou de ser condição de falha (reativa e fecha, exit 0) e a exceção `NoActiveSessionError` foi **removida** — o próprio código documenta isso (`core/commands/errors.py`, comentário "NOTA (feature 016)"). Não é regressão acidental da reconciliação atual; é uma decisão de produto já tomada há tempo, só nunca antes registrada neste watch.

| ID   | Veredito   | Observação                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ---- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟡 amarelo | **Parcialmente superado pela feature 016.** O sub-caso "estado malformado/hash curto" segue `exit ≠ 0` com mensagem nomeada (confirmado em `main.py`, ramo `except MalformedSessionStateError`, branch não-`resume` → exit 1). O sub-caso "sessão inativa" **não é mais falha**: `CommandService` reativa e fecha com sucesso (exit 0, mensagem anuncia a reativação) — mudança deliberada da 016 (D1/D3), não regressão.                                 |
| W002 | 🟢 verde   | `resume`/boot tolera estado malformado: confirmado em `main.py` — `MalformedSessionStateError` no ramo `resume` imprime aviso em `stderr` e `sys.exit(0)`, não trava o `SessionStart`.                                                                                                                                                                                                                                                                    |
| W003 | 🟡 amarelo | **Parcialmente superado pela feature 016.** `NoActiveSessionError` foi **removida** (`core/commands/errors.py` confirma via comentário explícito) — sessão ausente é hoje um no-op sem exceção, não um erro nomeado. `MalformedSessionStateError`/`SessionCommitError` seguem vivas e o princípio geral (a borda `cmd` decide exit code/canal, o serviço não chama `sys.exit`) permanece verdadeiro — só o exemplo específico citado ficou desatualizado. |
| W004 | 🟢 verde   | Caminho feliz do `encerrar-sessao` intocado: âncora = HEAD de trabalho capturado antes da escrita, `commit_paths` versiona só `session_filepath` (nunca `git add -A`), commit de encerramento por cima — `core/commands/service.py` confirmado sem alteração de RN-N31.                                                                                                                                                                                   |

## Arquivadas

> (vazio)
