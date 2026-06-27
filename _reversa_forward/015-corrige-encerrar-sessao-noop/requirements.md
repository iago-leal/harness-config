# Requirements: Correção do no-op silencioso no `encerrar-sessao`

> Identificador: `015-corrige-encerrar-sessao-noop`
> Data: `2026-06-26` (expandido e esclarecido em `2026-06-27`)
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O `encerrar-sessao` devolve um sucesso aparente — saída zero — em pelo menos **dois** caminhos que não fecham nada, e em ambos o usuário fica com a sessão aberta e o trabalho sem o commit de encerramento. No primeiro, o estado traz um commit-âncora de hash curto, escrito por uma versão antiga do harness, anterior à validação de quarenta caracteres: a borda levanta `MalformedSessionStateError`, o `main.py` a converte em aviso e termina com `exit 0`. No segundo, a sessão está **válida porém inativa** (já fechada antes): o serviço devolve a string `"Erro: Nenhuma sessão ativa..."`, que a borda imprime e segue para `exit 0`, sem fechamento e sem falha. A feature elimina os dois falsos sucessos: todo **comando explícito** de sessão que não conclui seu efeito passa a falhar barulhento — saída diferente de zero e mensagem nomeada —, preservando a saída não-bloqueante apenas no caminho de boot que reinjeta a sessão (`resume`). No caminho do estado inativo, a mensagem **orienta** o ciclo de vida (a sessão reabre no próximo boot/`resume`) sem introduzir um comando novo de "abrir"; e o hash curto legado é tratado como falha barulhenta, sem auto-reparo — escopo deliberadamente mínimo.

## 2. Contexto a partir do legado

| Fonte                                                   | Trecho relevante                                                                                                                                                                                                                                                                                                                        | Confidência |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `_reversa_sdd/domain.md#2.3` (RN-N4)                    | Estado **ausente** → `None`; estado **malformado** (sem `---`, YAML inválido, campo obrigatório ausente, **commit não-SHA1**) → `MalformedSessionStateError`, "falha explícita, **nunca silenciosa**". A regra cobre ausente e malformado, mas **não** a sessão válida porém inativa — a terceira categoria, onde mora o segundo no-op. | 🟢          |
| `_reversa_sdd/domain.md#2.14` (RN-N32)                  | No fechamento, falha que impeça o registro levanta erro nomeado com `exit ≠ 0`, sem devolver sucesso — "RN-N4 estendida ao fechamento". Os dois no-ops contradizem esta extensão por chegarem a `exit 0`.                                                                                                                               | 🟢          |
| `_reversa_sdd/architecture.md#4` (Integrações de Borda) | O slash command `./harness cmd encerrar-sessao` é materializado para Claude e Antigravity; a borda `cmd` em `main.py` despacha **todos** os comandos de sessão sob o mesmo fluxo.                                                                                                                                                       | 🟢          |
| `_reversa_sdd/domain.md#2.3` (RN-N3)                    | Em `resume` sob sessão existente, `start_session` **reativa** preservando a narrativa; é o único caminho que leva a sessão de inativa a ativa. Não há comando explícito de "abrir/ativar" fora do boot.                                                                                                                                 | 🟢          |
| `_reversa_sdd/architecture.md#5` (Dívidas Técnicas)     | T1–T6 dados como resolvidos; estes no-ops silenciosos são bug latente **ainda não catalogado**, observado em uso (dogfooding).                                                                                                                                                                                                          | 🟡          |
| `_reversa_sdd/domain.md#glossário`                      | Âncora Git de Sessão = SHA-1 do commit HEAD gravado no fechamento; usada na retomada para detectar divergência da base local.                                                                                                                                                                                                           | 🟢          |

Locus confirmado por leitura de código (fora do `_reversa_sdd/`, citado como apoio):

- **No-op do hash curto:** o `try/except MalformedSessionStateError` na borda `cmd` (`src/main.py`) imprime aviso em `stderr` e faz `sys.exit(0)`. O comentário justifica a saída zero como proteção do `SessionStart` do agente — legítima para o `resume` de boot, indevida para o `encerrar-sessao` explícito.
- **No-op do estado inativo:** o `execute_command` (`src/core/commands/service.py`) testa `if not session or not session.is_active` e **retorna a string** `"Erro: Nenhuma sessão ativa encontrada para encerrar."` — não levanta exceção. A borda cai no ramo `else: print(result_msg)` e, ao final, faz `sys.exit(0)` incondicional; as ofertas de fim de sessão (feature 014) só disparam quando o retorno começa com `"Sessão encerrada com sucesso"`, de modo que nada acontece. O usuário lê "Erro" enquanto o shell recebe sucesso.
- **Sinal de fronteira já presente:** a mesma borda já distingue `resume` dos demais comandos pelo **nome do comando** (`if cmd_name_norm == "resume"`) para escolher o sink de reinjeção. Esse sinal é suficiente para diferenciar invocação de boot de invocação explícita, sem heurística nova.

## 3. Personas e cenários de uso

| Persona                 | Objetivo                                                   | Cenário-chave                                                                                                                                                     |
| ----------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mantenedor intermitente | Encerrar a sessão de forma confiável após semanas de pausa | Retoma o repositório com um estado de sessão legado de hash curto e roda `/encerrar-sessao`; espera fechamento real ou falha clara, não sucesso falso             |
| Mantenedor intermitente | Saber em que estado a sessão está e como encerrá-la        | Roda `/encerrar-sessao` com a sessão já inativa (fechada antes); recebe "Erro" mas saída zero, não entende o que aconteceu nem como reabrir para encerrar de fato |
| Agente de IA no boot    | Reinjetar a sessão sem travar a inicialização              | Roda `resume` no `SessionStart` sobre um estado malformado; a inicialização não pode ser interrompida por saída diferente de zero                                 |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** O `encerrar-sessao` explícito, diante de estado malformado — incluído o **hash curto** legado —, **falha barulhento**: saída diferente de zero e mensagem nomeada que identifica o arquivo de estado e a causa. Nunca `exit 0` silencioso. O hash curto é tratado como malformado terminal; o auto-reparo fica **fora do escopo** desta feature (decisão de clarify, ver Esclarecimentos). 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.3` (RN-N4) e `_reversa_sdd/domain.md#2.14` (RN-N32)
   - Tipo: alterada (corrige a borda que hoje contradiz RN-N4)
2. **RN-02:** O caminho não-bloqueante (aviso em `stderr` com `exit 0`) permanece válido **apenas** para a reinjeção de sessão no boot (`resume`/`SessionStart`); não pode mascarar a falha de comandos explícitos de sessão. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.3` (RN-N3, semântica do `resume`) e `_reversa_sdd/architecture.md#4` (borda como ponto de escolha do mecanismo)
   - Tipo: nova (formaliza a fronteira que o catch atual ignora)
3. **RN-03:** O `encerrar-sessao` explícito sobre uma sessão **válida porém inativa** falha barulhento (saída diferente de zero), com mensagem que distingue "não há sessão ativa a encerrar" de "o encerramento falhou" e **orienta** que a sessão volta a ficar ativa no próximo boot/`resume`. Não se introduz comando novo de "abrir/ativar": o ciclo de vida permanece conduzido pelo `resume` de boot. 🟢
   - Origem no legado: estende `_reversa_sdd/domain.md#2.3` (RN-N4, que não cobre a sessão inativa) e `_reversa_sdd/domain.md#2.14` (RN-N32)
   - Tipo: nova
4. **RN-04:** A borda `cmd` distingue **invocação de boot** de **invocação explícita** pelo nome do comando — `resume` é boot e preserva o `exit 0` não-bloqueante; os demais (`encerrar-sessao`, `handoff`, `clarificar`) são explícitos e propagam a falha como saída diferente de zero. A diferenciação reusa o sinal já existente no despacho, sem heurística nova. 🟡
   - Origem no legado: `_reversa_sdd/architecture.md#4` (borda como ponto de escolha) e o despacho que já ramifica por `resume`
   - Tipo: nova (formaliza a fronteira boot × explícito)

## 5. Requisitos Funcionais

| ID    | Requisito                                                                          | Prioridade | Critério de aceite                                                                                                                                                                    | Confidência |
| ----- | ---------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | `encerrar-sessao` sobre estado malformado (incluído hash curto) termina barulhento | Must       | Executar o comando com estado de hash curto → código de saída diferente de zero e mensagem nomeando arquivo e causa; a sessão **não** é marcada como encerrada                        | 🟢          |
| RF-02 | A reinjeção de sessão no boot continua não-bloqueante                              | Must       | `resume` sobre o mesmo estado malformado → código de saída zero e aviso em `stderr`; o boot do agente não é interrompido                                                              | 🟢          |
| RF-03 | `encerrar-sessao` sobre sessão válida porém inativa não devolve falso sucesso      | Must       | Executar o comando com sessão inativa → código de saída diferente de zero; a mensagem distingue "nada a encerrar" de "falha" e orienta que a sessão reabre no próximo boot/`resume`   | 🟢          |
| RF-04 | Teste de regressão dos dois no-ops                                                 | Must       | A suíte ganha casos que reproduzem "hash curto + `encerrar-sessao`" **e** "sessão inativa + `encerrar-sessao`", verificando a falha barulhenta; ambos falhariam contra o código atual | 🟢          |
| RF-05 | A borda diferencia boot de comando explícito pelo nome do comando                  | Should     | Um teste fixa que `resume` preserva `exit 0` sobre estado problemático enquanto `encerrar-sessao` propaga `exit ≠ 0` na mesma condição; a diferenciação usa o nome do comando         | 🟡          |
| RF-06 | Orientação ao usuário na mensagem de falha                                         | Could      | A mensagem do caminho malformado indica como destravar (ex.: regravar a âncora de quarenta caracteres); a do caminho inativo indica como a sessão reabre                              | 🟡          |

## 6. Requisitos Não Funcionais

| Tipo             | Requisito                                                                                                                                          | Evidência ou justificativa                                                                                  | Confidência |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ----------- |
| Observabilidade  | Erro nomeado, saída diferente de zero, mensagem clara em `stderr`; nada de sucesso silencioso em comando explícito                                 | Princípio "erros barulhentos > performance" e RN-N4 / RN-N32 (`_reversa_sdd/domain.md#2.3`, `#2.14`)        | 🟢          |
| Compatibilidade  | O boot do agente não regride: `SessionStart`/`resume` jamais é travado por estado malformado ou inativo                                            | `_reversa_sdd/architecture.md#4` (ganchos de ciclo de vida) e o comentário de borda que originou o `exit 0` | 🟢          |
| Usabilidade      | A mensagem do caminho inativo orienta o ciclo de vida (a sessão reabre no boot/`resume`), não apenas relata o erro                                 | Queixa de dogfooding: o ciclo de vida active/inactive é opaco e não há comando explícito de "abrir"         | 🟡          |
| Simplicidade     | Escopo deliberadamente mínimo: sem auto-reparo de hash e sem novo comando de abrir; resolve-se o falso sucesso com a menor superfície possível     | Decisão de clarify (2026-06-27), princípio de leveza e footprint mínimo do mantenedor                       | 🟢          |
| Manutenibilidade | A correção é uma falha barulhenta orientadora; o estado legado de hash curto exige correção manual única (regravar a âncora), guiada pela mensagem | Princípio "retomável após semanas/meses"; sem o caminho de reparo, o atrito é pontual e explícito           | 🟡          |

## 7. Critérios de Aceitação

```gherkin
Cenário: Encerramento explícito sobre estado de hash curto legado falha barulhento
  Dado um arquivo de estado de sessão ativo cujo commit-âncora é um hash curto (anterior à validação de quarenta caracteres)
  Quando o mantenedor executa o comando encerrar-sessao
  Então o comando termina com código de saída diferente de zero
  E exibe uma mensagem nomeando o arquivo de estado e a causa, com instrução de como regravar a âncora
  E a sessão permanece marcada como ativa, sem registro falso de encerramento

Cenário: Encerramento explícito sobre sessão já inativa não devolve falso sucesso
  Dado um arquivo de estado de sessão válido cuja sessão está inativa (já encerrada antes)
  Quando o mantenedor executa o comando encerrar-sessao
  Então o comando termina com código de saída diferente de zero
  E a mensagem distingue "não há sessão ativa a encerrar" de uma falha de fechamento
  E orienta que a sessão reabre no próximo boot/resume

Cenário: Reinjeção de sessão no boot tolera estado problemático
  Dado o mesmo arquivo de estado malformado ou inativo
  Quando o agente executa resume no SessionStart
  Então o comando termina com código de saída zero
  E emite um aviso em stderr quando aplicável
  E o boot do agente prossegue sem interrupção
```

## 8. Prioridade MoSCoW

| Item                                                                 | MoSCoW | Justificativa                                                                                                  |
| -------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------- |
| RF-01 (falha barulhenta no encerrar explícito malformado/hash curto) | Must   | Núcleo do primeiro defeito: o falso sucesso contraria RN-N4/RN-N32 e o princípio de erros barulhentos          |
| RF-03 (sem falso sucesso sobre sessão inativa)                       | Must   | Núcleo do segundo defeito, o que de fato travou o mantenedor em uso; não coberto pela versão estreita anterior |
| RF-02 (boot não-bloqueante preservado)                               | Must   | Sem esta fronteira, endurecer o encerramento poderia travar o `SessionStart` — regressão inaceitável           |
| RF-04 (teste de regressão dos dois no-ops)                           | Must   | Hoje não há cobertura de nenhum dos dois caminhos no `encerrar-sessao`; sem teste, os no-ops podem voltar      |
| RF-05 (diferenciação boot × explícito)                               | Should | Formaliza e blinda a fronteira que sustenta RF-01/RF-02/RF-03; reusa sinal já existente                        |
| RF-06 (orientação na mensagem)                                       | Could  | Refinamento de mensagem; subordinado a RF-01 e RF-03                                                           |

## 9. Esclarecimentos

### Sessão 2026-06-27

> As duas decisões abaixo foram tomadas pelo assistente sob delegação explícita do mantenedor ("continuar", após dispensar a pergunta interativa), ancoradas nos princípios ativos: erros barulhentos > performance, leveza e footprint mínimo.

- **Q:** No `encerrar-sessao` sobre sessão já inativa, deve-se falhar barulhento, criar um comando explícito de abrir/ativar, ou tratar como idempotente benigno (exit 0)?
  **R:** Falhar barulhento (saída diferente de zero) e **orientar** que a sessão reabre no próximo boot/`resume`, **sem** introduzir comando novo de abrir. Menor superfície, coerente com erros barulhentos. (RN-03, RF-03)
- **Q:** Para o estado legado de hash curto, a 015 deve auto-reparar (expandir o prefixo a SHA-1 completo), só falhar barulhento, ou combinar?
  **R:** **Só falhar barulhento**, com mensagem que ensina a regravar a âncora. O auto-reparo (e seu caminho de borda) fica fora do escopo desta feature — escopo mínimo que já mata o falso sucesso. (RN-01, RF-01)

## 10. Lacunas

> Sem lacunas abertas. O auto-reparo do hash curto foi conscientemente **adiado** (não é lacuna, é decisão de escopo registrada nos Esclarecimentos); pode virar feature de melhoria futura, separada, se a fricção de regravar a âncora à mão se mostrar recorrente.

## 11. Histórico de alterações

| Data       | Alteração                                                                                                                                                                                                                                     | Autor   |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| 2026-06-26 | Versão inicial gerada por `/reversa-requirements` (escopo: no-op do hash curto)                                                                                                                                                               | reversa |
| 2026-06-27 | Escopo ampliado para o segundo no-op (sessão válida porém inativa) e o ciclo de vida: RN-05, RN-06, RF-06, RF-07, cenário Gherkin e revisão das Lacunas                                                                                       | reversa |
| 2026-06-27 | `/reversa-clarify`: decididas as duas dúvidas (falha barulhenta + orientar, sem comando novo; hash curto só falha, sem auto-reparo). Removido o caminho de auto-reparo do escopo; RNs e RFs renumeradas e consolidadas; zeradas as `[DÚVIDA]` | reversa |
