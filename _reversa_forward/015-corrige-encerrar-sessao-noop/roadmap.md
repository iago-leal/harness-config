# Roadmap: Correção do no-op silencioso no `encerrar-sessao`

> Identificador: `015-corrige-encerrar-sessao-noop`
> Data: `2026-06-27`
> Requirements: `_reversa_forward/015-corrige-encerrar-sessao-noop/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A correção é um delta cirúrgico em dois pontos, sem tocar o invariante de fechamento (RN-N31/N32). No **core** (`commands/service.py`), o ramo `encerrar-sessao` deixa de devolver a string `"Erro: Nenhuma sessão ativa..."` e passa a levantar uma exceção nomeada — `NoActiveSessionError` — no mesmo espírito de `SessionCommitError`. O core permanece agnóstico ao harness (RN-N5): sinaliza a falha por **tipo**, não decide código de saída. Na **borda** (`main.py`, despacho `cmd`), o tratamento de erro passa a ramificar pelo **nome do comando**, reusando o sinal que já existe (`if cmd_name_norm == "resume"`): para o `resume` de boot, `MalformedSessionStateError` segue não-bloqueante (`exit 0` + aviso em `stderr`); para os comandos explícitos, tanto `MalformedSessionStateError` (que cobre o hash curto legado) quanto `NoActiveSessionError` viram `exit ≠ 0` com mensagem orientadora. Sem auto-reparo do hash e sem comando novo de "abrir" — decisões de clarify, escopo mínimo. Bump 1.2.51 → 1.2.52 para propagar via `upgrade`.

## 2. Princípios aplicados

`.reversa/principles.md` ausente: não há princípios versionados do projeto. Aplicam-se os princípios operacionais do mantenedor (CLAUDE.md global).

| Princípio                           | Como a feature se relaciona                                                                                              | Status   |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | -------- |
| Erros barulhentos > performance     | É o núcleo da feature: elimina dois `exit 0` silenciosos, substituindo-os por falha nomeada e visível                    | respeita |
| Leveza / footprint mínimo           | Sem auto-reparo e sem comando novo; o delta é uma exceção nomeada + uma ramificação na borda                             | respeita |
| Alta coesão, baixo acoplamento, OOP | A decisão de exit code vive na borda (que conhece o comando); o core só sinaliza por tipo — RN-N5 preservada             | respeita |
| TDD                                 | RF-04 exige testes que reproduzem os dois no-ops antes da correção; a suíte do core já existe                            | respeita |
| Estabilidade / retomável            | O boot do agente (`resume`) não regride; o estado legado fica retomável após correção manual única, guiada pela mensagem | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                              | Justificativa                                                                                             | Alternativas descartadas                                                                                                                                             | Confidência |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| D-01 | `execute_command`, ramo `encerrar-sessao`, levanta `NoActiveSessionError` (nova, em `commands/errors.py`) quando `not session or not session.is_active`, em vez de retornar string   | Erro barulhento por tipo, simétrico a `SessionCommitError`; mantém o core agnóstico ao harness (RN-N5)    | (a) retornar a string e o `main.py` inspecionar o prefixo `"Erro:"` — frágil, acopla a borda ao texto; (b) retornar código de saída do próprio service — viola RN-N5 | 🟢          |
| D-02 | A borda `cmd` ramifica o tratamento de exceção pelo nome do comando: `resume` → `exit 0` não-bloqueante; explícitos → `exit ≠ 0`                                                     | Reusa o sinal já presente no despacho; formaliza a fronteira boot × explícito (RN-04) sem heurística nova | (a) endurecer todos os comandos sem exceção — travaria o `SessionStart`; (b) flag de ambiente para distinguir boot — sinal redundante, mais acoplamento              | 🟢          |
| D-03 | Mensagens orientadoras distintas por caminho: malformado/hash curto → instruir a regravar a âncora de 40 caracteres; inativo → informar que a sessão reabre no próximo boot/`resume` | RF-06; usabilidade para o mantenedor intermitente                                                         | Mensagem genérica única — não orienta a saída concreta                                                                                                               | 🟡          |
| D-04 | Sem auto-reparo do hash curto e sem comando novo de abrir/ativar                                                                                                                     | Decisões de clarify (2026-06-27); escopo mínimo, menos casos de borda                                     | (a) auto-reparo expandindo o prefixo; (b) `iniciar-sessao` explícito — ambos adiados                                                                                 | 🟢          |
| D-05 | Bump de versão 1.2.51 → 1.2.52 nos três pontos (`domain/config.py`, `bootstrap/init_service.py`, `tests/test_init.py`); rematerialização Claude+Antigravity e suíte verde como gate  | Propagação por `upgrade` exige versão nova não-stale (padrão das features 011–014)                        | Não versionar — consumidores não receberiam o fix                                                                                                                    | 🟢          |

## 4. Premissas

Nenhuma. As duas `[DÚVIDA]` do requirements foram resolvidas em `/reversa-clarify` (ver `requirements.md#9`); não há premissa pendente.

## 5. Delta arquitetural

| Componente                         | Arquivo de origem no legado                                                             | Tipo de mudança | Resumo                                                                                                            |
| ---------------------------------- | --------------------------------------------------------------------------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------- |
| Serviço de comandos de sessão      | `_reversa_sdd/architecture.md#3` · `src/core/commands/service.py`                       | regra-alterada  | ramo `encerrar-sessao` levanta `NoActiveSessionError` em vez de retornar string de erro                           |
| Erros de comandos                  | `src/core/commands/errors.py`                                                           | componente-novo | nova exceção nomeada `NoActiveSessionError` (irmã de `SessionCommitError`)                                        |
| Borda `cmd` (despacho de comandos) | `_reversa_sdd/architecture.md#4` · `src/main.py`                                        | regra-alterada  | tratamento de exceção ramifica por nome do comando; explícitos propagam `exit ≠ 0`, `resume` segue não-bloqueante |
| Versão / propagação                | `src/core/domain/config.py`, `src/core/bootstrap/init_service.py`, `tests/test_init.py` | regra-alterada  | bump 1.2.51 → 1.2.52                                                                                              |

Detalhe do contrato de saída em `interfaces/session-command-exit-contract.md`.

## 6. Delta no modelo de dados

- Resumo das mudanças: nenhuma alteração no schema persistido do `SessionState` (campos, formato canônico, round-trip do serializer permanecem idênticos). A única adição é uma exceção de runtime, não um dado persistido.
- Detalhe completo em: `_reversa_forward/015-corrige-encerrar-sessao-noop/data-delta.md`

## 7. Delta de contratos externos

| Contrato                                                   | Tipo          | Arquivo de detalhe                                                                              |
| ---------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------------- |
| Saída do `./harness cmd <comando>` (exit codes × condição) | arquivo / CLI | `_reversa_forward/015-corrige-encerrar-sessao-noop/interfaces/session-command-exit-contract.md` |

## 8. Plano de migração

1. Escrever os testes de regressão (RF-04): "hash curto + `encerrar-sessao` → exit ≠ 0" e "sessão inativa + `encerrar-sessao` → exit ≠ 0", além de "resume sobre estado malformado → exit 0" (RF-02). Confirmar que falham contra o código atual.
2. Adicionar `NoActiveSessionError` em `commands/errors.py`; alterar `execute_command` para levantá-la (D-01).
3. Ajustar a borda `cmd` em `main.py` (D-02, D-03): ramificar o tratamento de exceção por nome do comando, com mensagens orientadoras.
4. Atualizar os testes existentes que casavam a string `"Erro: Nenhuma sessão ativa..."` (risco R1).
5. Bump 1.2.51 → 1.2.52 nos três pontos (D-05).
6. Suíte verde; rematerializar Claude+Antigravity em sandbox e validar o smoke (feliz + os dois negativos).
7. (Fora desta feature, sob aval) commit + push no `harness-config`; consumidores recebem via `./harness upgrade`.

## 9. Riscos e mitigações

| Risco                                                                                                                   | Impacto | Probabilidade | Mitigação                                                                                             |
| ----------------------------------------------------------------------------------------------------------------------- | ------- | ------------- | ----------------------------------------------------------------------------------------------------- |
| R1: trocar retorno do service (string → exceção) quebra testes/chamadores que casavam `"Erro: Nenhuma sessão ativa..."` | médio   | médio         | localizar e ajustar os testes (`test_commands.py`, `test_cli.py`); a string deixa de ser contrato     |
| R2: ramificação boot × explícito mal feita trava o `SessionStart` (`resume` viraria `exit ≠ 0`)                         | alto    | baixo         | teste explícito RF-02/RF-05 fixando `resume → exit 0` sobre estado malformado                         |
| R3: `handoff`/`clarificar` (também explícitos) afetados inesperadamente                                                 | baixo   | baixo         | hoje não levantam `NoActiveSessionError`; cobrir com smoke; mudança restrita ao tratamento de exceção |
| R4: bump esquecido em um dos três pontos deixa o `upgrade` stale                                                        | médio   | baixo         | seguir o checklist das features 011–014; o `test_init` falha se a versão divergir                     |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Suíte do core verde (inclui os novos testes de regressão dos dois no-ops)
- [ ] `regression-watch.md` gerado
- [ ] Rematerialização Claude+Antigravity sem regressão; smoke feliz + dois negativos
- [ ] Bump 1.2.52 consistente nos três pontos
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-06-27 | Versão inicial gerada por `/reversa-plan` | reversa |
