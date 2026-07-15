# Requirements: Granularidade do lembrete do gate de registro (rearme estável por pendência)

> Identificador: `023-granularidade-lembrete-gate`
> Data: `2026-07-15`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O mantenedor relata que "cada mudança de arquivo está rodando o hook", com frequência que atrapalha o andamento do trabalho. O diagnóstico factual descarta hooks por-edição: não existe gancho `PostToolUse` em nenhum projeto (aposentado na MD-0014). A causa real é o lembrete do gate de registro de microdecisões (feature 022): sua identidade anti-loop inclui o conjunto de arquivos sujos do working tree, então cada arquivo novo tocado rearma o soft-block no fim do turno — o "no máximo um lembrete por pendência" degenera, durante trabalho ativo, em um bloqueio por mudança de arquivo. Esta feature entrega ao mantenedor um lembrete que dispara de forma estável (uma vez por pendência real), preservando intacta a garantia dura do registro no encerramento da sessão.

## 2. Contexto a partir do legado

> Nota de defasagem: a extração `_reversa_sdd/` está congelada pré-022 (reconciliação pendente, registrada no estado da sessão). As fontes autoritativas do gate são os artefatos da própria feature 022 e o código atual, citados abaixo com verificação direta nesta sessão.

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `.harness/harness-core/src/core/decisions/gate.py#compute_fingerprint` | Fingerprint anti-loop = `sha1(âncora + HEAD + sujos ordenados)`; o próprio docstring declara a intenção "mudança nova → o gate volta a valer" — a granularidade por-arquivo é comportamento projetado, não bug de implementação | 🟢 |
| `.harness/harness-core/src/main.py` (ramo `decisions --gate`) | Soft-block emitido quando `pendente` e o fingerprint gravado difere do atual; o fingerprint novo é persistido no estado antes de bloquear | 🟢 |
| `_reversa_forward/022-hook-registro-decisoes/roadmap.md#D-03` | Decisão original: fingerprint no front-matter do estado como anti-loop, "sem relógio" | 🟢 |
| `_reversa_forward/022-hook-registro-decisoes/requirements.md#RF-08` (reconciliado) | O evento de fim de turno do agente não tem canal não-bloqueante que alcance o modelo → o lembrete é um soft-block único por estado de pendência | 🟢 |
| `.harness/decisoes/MD-0015.md` | Gate de registro: fingerprint no estado e soft-block único no Stop; estende MD-0005 | 🟢 |
| `_reversa_sdd/domain.md#RN-N26` | No Antigravity o gate é advisory em stderr, nunca bloqueante — o incômodo relatado só pode vir do perfil Claude | 🟢 |
| `_reversa_sdd/state-machines.md` (gates de aborto) | O encerramento já impõe portões antes de `ATIVA → INATIVA`; o 3º portão (022) é a garantia dura do registro, independente do lembrete | 🟢 |
| Varredura desta sessão (`~/dev/*/.claude/settings.json`) | Zero ocorrências de `PostToolUse` na base instalada; neste repo só existem `SessionStart` (resume) e fim de turno (`decisions --gate`) | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor (iago) | Trabalhar numa sessão longa sem ser interrompido a cada arquivo tocado | Sessão de codificação toca 15 arquivos em 10 turnos; o mantenedor quer no máximo um lembrete de registro, não dez |
| Agente (perfil Claude) | Concluir turnos sem reentrar no laço por soft-blocks repetidos | Após acusar o lembrete uma vez, o agente segue editando arquivos e só reencontra o gate no encerramento da sessão |
| Mantenedor de projeto-alvo | Receber o comportamento corrigido ao atualizar o core | Projeto instalado atualiza e herda o lembrete estável sem reconfiguração |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** A identidade do estado de pendência usada pelo anti-loop do lembrete é a âncora de commit da sessão, estável do início ao encerramento. Nem o crescimento do conjunto de arquivos tocados nem novos commits sem ficha rearmam o lembrete: dentro de uma sessão, ele dispara no máximo uma vez. 🟢
   - Origem no legado: `_reversa_forward/022-hook-registro-decisoes/roadmap.md#D-03` (altera a composição da identidade decidida lá)
   - Tipo: alterada
2. **RN-02:** A garantia dura do registro permanece exclusivamente no encerramento da sessão (3º portão do fluxo de fechamento, com escape auditável `--sem-decisao`); o lembrete de fim de turno é conveniência informativa e sua frequência menor não enfraquece a garantia. 🟢
   - Origem no legado: `.harness/decisoes/MD-0015.md`
   - Tipo: inalterada (reafirmada como invariante desta feature)
3. **RN-03:** O registro de uma ficha de decisão satisfaz a pendência pela sessão inteira — semântica que o avaliador do gate já aplica (qualquer ficha tocada desde a âncora anula a pendência) e que o portão do encerramento compartilha. Não há rearme intra-sessão após ficha: lembrete e portão usam a mesma definição de pendência. 🟢
   - Origem no legado: `.harness/harness-core/src/core/decisions/gate.py` (semântica de `fichas_tocadas`)
   - Tipo: inalterada (explicitada; corrige leitura anterior deste documento, que previa rearme pós-ficha em contradição com o avaliador)
4. **RN-04:** O opt-out por configuração (`decisions.require_registration = false`) continua desligando lembrete e portão de encerramento, sem mudança de semântica. 🟢
   - Origem no legado: `_reversa_forward/022-hook-registro-decisoes/requirements.md` (esclarecimento 3a)
   - Tipo: inalterada

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Durante uma mesma pendência, turnos subsequentes que tocam arquivos novos não geram lembretes adicionais | Must | Sessão ativa com pendência: após o 1º lembrete, editar ≥ 3 arquivos novos em ≥ 3 turnos distintos produz zero lembretes adicionais | 🟢 |
| RF-02 | O comportamento silencioso atual é preservado: sem pendência ou com lembrete já emitido, a saída padrão do fim de turno fica vazia; erro interno avisa no canal de erro e libera o turno | Must | Casos "sem pendência", "mesma pendência" e "falha interna" reproduzem byte a byte o contrato da 022 (`interfaces/stop-gate-lembrete.md`) | 🟢 |
| RF-03 | O 3º portão do encerramento permanece inalterado em semântica e mensagens | Must | Suíte da feature 022 relativa ao fluxo de fechamento continua verde sem edição dos testes de comportamento | 🟢 |
| RF-04 | Após o registro de uma ficha, os fins de turno restantes da sessão ficam silenciosos mesmo com trabalho substantivo novo, e o portão do encerramento considera a sessão satisfeita | Should | Registrar ficha → editar arquivos novos em turnos seguintes → zero lembretes; `encerrar-sessao` não aborta pelo 3º portão | 🟢 |
| RF-05 | Estados de sessão gravados por versões anteriores (fingerprints no formato da 022) são tolerados sem erro e convergem para a semântica nova no primeiro fim de turno | Must | Estado pré-023 carregado: nenhuma exceção; no máximo 1 lembrete emitido na transição | 🟢 |
| RF-06 | A correção chega à base instalada pelo fluxo normal de atualização do core, sem passo manual por projeto além do já previsto | Could | Bump de versão do core; projeto-alvo atualizado herda o comportamento novo | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | A avaliação do gate no fim de turno conclui dentro do timeout de 10 s já configurado e não adiciona chamadas ao controle de versão além das três atuais (HEAD, sujos, diff da âncora) | `.claude/settings.json` (timeout 10); `gate.py#evaluate_registration_gate` | 🟢 |
| Compatibilidade | Mudança retrocompatível de estado e configuração: campos existentes preservados, tomls sem campo novo herdam o default (padrão das features 021/022) | `_reversa_forward/022-hook-registro-decisoes/actions.md` T002/T003 | 🟢 |
| Observabilidade | Falhas e avisos do gate continuam ecoados no canal de erro, nunca engolidos (erros barulhentos, princípio do mantenedor) | `main.py` ramo `--gate` (aviso em stderr, exit 0) | 🟢 |
| UX do agente | No pior caso, o mantenedor vê 1 lembrete por pendência real por sessão — nunca 1 por arquivo tocado | Queixa desta feature; RN-01 | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: lembrete único durante trabalho ativo
  Dado uma sessão ativa com trabalho substantivo e nenhuma ficha de decisão nova
  E o lembrete de pendência já foi emitido uma vez neste estado
  Quando o agente edita três arquivos novos em três turnos consecutivos
  Então nenhum lembrete adicional é emitido nesses turnos
  E o 3º portão do encerramento ainda exige ficha ou --sem-decisao

Cenário: silêncio após registro de ficha
  Dado que o mantenedor registrou uma ficha MD-NNNN durante a sessão
  Quando trabalho substantivo novo aparece em turnos posteriores
  Então nenhum lembrete adicional é emitido até o encerramento
  E o 3º portão do encerramento considera a sessão satisfeita

Cenário: caso negativo — estado antigo não quebra
  Dado um estado de sessão gravado por versão anterior, com fingerprint no formato da 022
  Quando o fim de turno avalia o gate pela primeira vez após a atualização
  Então nenhuma exceção ocorre
  E no máximo um lembrete é emitido na transição de formato

Cenário: caso negativo — opt-out continua absoluto
  Dado um projeto com require_registration desligado na configuração
  Quando há trabalho substantivo sem ficha e o turno termina
  Então a saída padrão fica vazia e nenhum lembrete é emitido

Cenário: caso negativo — falha interna libera o turno
  Dado uma sessão ativa cuja âncora de commit está ilegível
  Quando o fim de turno avalia o gate
  Então a saída padrão fica vazia, um aviso é ecoado no canal de erro
  E o turno do agente não é bloqueado

Cenário: propagação à base instalada
  Dado um projeto-alvo cujo core está em versão anterior a esta feature
  Quando o mantenedor executa o fluxo normal de atualização do core
  Então o projeto herda o lembrete estável sem passo manual adicional
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | É a queixa em si: eliminar o rearme por arquivo tocado |
| RF-02 | Must | O contrato do hook de fim de turno é consumido pelo harness do agente; regressão aqui trava o laço |
| RF-03 | Must | A garantia do registro (valor da 022) não pode ser enfraquecida pela conveniência |
| RF-05 | Must | Estados pré-023 existem neste repo hoje; quebra na carga seria falha silenciosa de sessão |
| RF-04 | Should | Lembrete e portão devem compartilhar a mesma definição de pendência; divergência entre os dois seria dívida de coesão |
| RF-06 | Could | Só este repo tem o gate materializado hoje; a propagação já tem fluxo próprio pendente |
| RNF de desempenho | Should | O custo por turno já existe e não deve crescer |

## 9. Esclarecimentos

### Sessão 2026-07-15

- **Q:** O que foi percebido como "hook rodando a cada mudança de arquivo"?
  **R:** (1a) O soft-block `DECISAO_PENDENTE` repetido ao fim dos turnos deste repo — diagnóstico confirmado: não existe hook por-edição; o rearme vinha do fingerprint incluir o conjunto de arquivos sujos.
- **Q:** Qual a granularidade de rearme do lembrete dentro de uma sessão?
  **R:** O mantenedor delegou a escolha ao harness com critérios explícitos (longevidade, manutenibilidade, mínimo de dívida, alta coesão, baixo acoplamento, OOP, TDD, SDD). Recomendação adotada: **lembrete único por sessão, com a âncora de commit como identidade da pendência** (opção a). Porquê: espelha exatamente a definição de pendência do portão do encerramento (mesmo avaliador; ficha desde a âncora satisfaz a sessão inteira), evita subgranularidade por commit que o domínio não tem (opção b), dispensa contador de turnos com sabor de relógio (opção c) e preserva o enforcement híbrido decidido na 022 (descarta a opção d). Menor delta sobre D-03, testável por TDD sobre a suíte existente.
- **Q:** A política de rearme deve ser configurável por projeto?
  **R:** Por extensão da mesma delegação: **fixa no core**, sem flag nova — `decisions.require_registration` permanece o único botão. Superfície de configuração sem demanda comprovada é dívida; tornar configurável depois não quebra contrato.
- **Q:** Como tratar estados gravados no formato de fingerprint da 022?
  **R:** Por extensão da mesma delegação: **autoresolvente** — o fingerprint antigo nunca coincide com a composição nova, então o primeiro fim de turno pós-atualização emite no máximo um lembrete e o estado converge sem código de migração (RF-05).

## 10. Lacunas

- Nenhuma lacuna aberta. As duas dúvidas da versão inicial foram resolvidas na sessão de esclarecimentos de 2026-07-15.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-07-15 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-07-15 | Esclarecimentos integrados por `/reversa-clarify`: sintoma confirmado (soft-block do fim de turno); política fixada — lembrete único por sessão com a âncora como identidade (RN-01/RN-03/RF-04/RF-05 reescritos) | reversa |
