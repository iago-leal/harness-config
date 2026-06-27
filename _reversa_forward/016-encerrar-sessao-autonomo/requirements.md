# Requirements: encerrar-sessao autônomo — auto-reativa, regenera artefatos e commita o trabalho

> Identificador: `016-encerrar-sessao-autonomo`
> Data: `2026-06-27`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Hoje o encerramento de sessão falha sistematicamente nos ambientes em que o hook de boot não dispara (Claude Desktop, terminal puro): a sessão permanece `inactive` e o `encerrar-sessao` aborta com "Nenhuma sessão ativa encontrada" (efeito barulhento introduzido pela feature 015). Esta feature elimina o atrito do estado ativa/inativa e entrega o "comando que faz tudo" pedido pelo mantenedor: o encerramento (i) **auto-reativa** a sessão inativa antes de fechar, de forma ruidosa; (ii) **regenera** os artefatos derivados do projeto a partir de um contrato configurável; e (iii) **commita o trabalho pendente** com mensagem descritiva, tudo orquestrado na borda, sem comprometer os invariantes do core (jamais `git add -A`; âncora sempre no último commit de trabalho). A correção nasce no upstream (`~/dev/harness`) e propaga aos consumidores via `./harness upgrade`.

## 2. Contexto a partir do legado

| Fonte                                                     | Trecho relevante                                                                                                                                                                                                                                                                        | Confidência |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `_reversa_sdd/domain.md#2.3` (RN-07, RN-N3, RN-N4, RN-N5) | Âncora capturada antes de qualquer escrita; `resume`/`start_session` reativa preservando a narrativa; ausente ≠ malformado (falha barulhenta); o core não conhece o harness (seleção de borda)                                                                                          | 🟢          |
| `_reversa_sdd/domain.md#2.14` (RN-N31, RN-N32)            | Encerramento versiona **exclusivamente** o `state_file` num commit isolado por cima do trabalho, via `GitPort.commit_paths` (`git add -- <paths>`, nunca `-A`); âncora nunca vira o commit de fechamento; falha de commit → `SessionCommitError` (exit ≠ 0) sem reverter o estado salvo | 🟢          |
| `_reversa_sdd/domain.md#1.1`                              | Reinjeção de contexto no boot pelo hook `SessionStart` → `./harness cmd resume` (premissa de design: só o resume alimenta o SessionStart)                                                                                                                                               | 🟢          |
| `_reversa_sdd/domain.md#2.12` (RN-N28, RN-N29)            | Materialização incondicional dos slash commands de sessão por `init`/`upgrade`; superfície de comando encapsulada por `HarnessProfile.session_command_artifact`; o comando delega ao `CommandService`, não reimplementa o fechamento                                                    | 🟢          |
| `_reversa_sdd/domain.md#2.13` (RN-N30)                    | `apply_local_materializers` é a função única de materialização; `init` in-process, `upgrade` via subprocesso do código novo                                                                                                                                                             | 🟢          |
| `_reversa_sdd/domain.md#2.8` (RN-N16, RN-N17)             | Configuração por via única tipada (`harness.toml` → `HarnessConfig`); footprint global zero (toda escrita sob `project_path`)                                                                                                                                                           | 🟢          |
| `.harness/harness-core/src/core/commands/service.py`      | Ramo `encerrar-sessao`: hoje, sessão ausente ou `is_active=False` → `NoActiveSessionError` (015). Ramo `resume`: `start_session` reativa + valida âncora                                                                                                                                | 🟢          |
| `.harness/harness-core/src/core/domain/config.py`         | `HarnessConfig` tipado (pydantic); `version = "1.2.52"` (consumida pela 015); ponto de extensão para o contrato de regen                                                                                                                                                                | 🟢          |
| `BRIEF-oferta-commit-pendente-ao-encerrar.md` (raiz)      | Origem do item (iii); recomenda pré-check da working tree fora de `.harness/` e o padrão "abortar-e-reexecutar" via marker (dualidade TTY × não-TTY da feature 014)                                                                                                                     | 🟡          |

## 3. Personas e cenários de uso

| Persona                                    | Objetivo                                                                                       | Cenário-chave                                                                                          |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Mantenedor intermitente (iago)             | Fechar a sessão num passo, sem lembrar de commitar nem se preocupar com o estado ativa/inativa | Roda `/encerrar-sessao` ao fim do trabalho num consumidor; o comando regenera, commita e fecha sozinho |
| Agente de IA (borda)                       | Orquestrar o fechamento "faz tudo" preservando os invariantes do core                          | Recebe o marker de pré-check, lista o trabalho solto, commita o que é real e re-roda o fechamento      |
| Operador em terminal puro / Claude Desktop | Encerrar mesmo quando o hook de `SessionStart` nunca disparou                                  | `./harness cmd encerrar-sessao` sobre sessão `inactive` reativa e fecha em vez de abortar              |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** Encerramento tolera sessão inativa **e ausente**, sem abortar, de forma ruidosa. 🟢
   - Origem no legado: altera `_reversa_sdd/domain.md#2.3` (uso de `start_session`) e o comportamento de `NoActiveSessionError` introduzido na feature 015.
   - Tipo: alterada
   - Detalhe: sobre sessão **válida porém inativa**, o `encerrar-sessao` chama `start_session(feature, HEAD)` (reativa preservando a narrativa, RN-N3), registra na saída que reativou automaticamente, e segue o fechamento normal. Sobre sessão **ausente** (arquivo inexistente ou estado inicial com campos `null`), o comando não falha: emite um aviso explícito ("não havia sessão para encerrar") e termina com exit 0, sem criar commit de encerramento (não há narrativa nem trabalho de sessão a registrar). Reverte conscientemente a decisão do clarify da 015 ("falha barulhenta, sem auto-reparo"), preservando o **espírito ruidoso** (a reativação e o no-op são anunciados, nunca silenciosos). Decisão D1 (§9).

2. **RN-02:** Contrato de regeneração de artefatos derivados, configurável e opcional. 🟢
   - Origem no legado: estende `_reversa_sdd/domain.md#2.8` (RN-N16, config tipada via via única).
   - Tipo: nova
   - Detalhe: novo campo opcional no `harness.toml` (ex.: `regen = "..."`) declara o comando de regeneração do projeto. Capacidade fina e testável do core (`./harness cmd regen`) lê o config e executa via _port_ de subprocesso. Campo ausente → pula sem erro. Falha do regen → barulhenta (exit ≠ 0) e **não** prossegue para o fechamento. O core permanece agnóstico ao que cada projeto deriva (baixo acoplamento; não conhece `gerar_site.py`).

3. **RN-03:** Oferta de commit do trabalho pendente, mediada na borda, fora de `.harness/`. 🟢
   - Origem no legado: deriva do `BRIEF-oferta-commit-pendente-ao-encerrar.md` e estende a dualidade TTY × não-TTY da feature 014.
   - Tipo: nova
   - Detalhe: antes de fechar, lista as mudanças da working tree **excluindo** `.harness/` (que o fechamento versiona). Havendo trabalho solto, o agente na borda o commita com mensagem descritiva e _split_ sensato entre fonte e regenerável (derivados podem ir ao `.gitignore`); só com a árvore limpa (fora de `.harness/`) o fechamento prossegue. O staging é sempre **por caminho** — `git add -- <path>`, jamais `git add -A` (RN-N32 preservada).

4. **RN-04:** Invariantes do fechamento preservados. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.14` (RN-N31, RN-N32) e `#2.3` (RN-07).
   - Tipo: inalterada (restrição)
   - Detalhe: o commit de fechamento continua versionando **somente** `.harness/estado-da-sessao.md`; a âncora é o último commit de **trabalho**, capturada antes de qualquer escrita, e nunca aponta para o commit de encerramento. Toda a orquestração nova (regen, commit do trabalho, auto-reativação) é **anterior** ou **lateral** ao `commit_paths`, sem alterá-lo.

5. **RN-05:** Resume confiável no `SessionStart` de todo consumidor. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#1.1` (reinjeção via `SessionStart` → `cmd resume`) e `#2.12`/`#2.13` (materializadores únicos).
   - Tipo: alterada (robustez de materialização)
   - Detalhe: garantir que `init`/`upgrade` plantem de forma confiável o hook `SessionStart → ./harness cmd resume` no perfil de cada consumidor. A causa de o hook não ter sido materializado no consumidor `contrato-fotos-higor` precisa ser investigada (ver §10). Mitiga a raiz: sessão que nasce ativa não chega inativa ao fechamento.

## 5. Requisitos Funcionais

| ID     | Requisito                                                                      | Prioridade | Critério de aceite                                                                                                                                           | Confidência |
| ------ | ------------------------------------------------------------------------------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| RF-01  | `encerrar-sessao` sobre sessão **inativa** auto-reativa e fecha num passo      | Must       | Estado `status: inactive` → comando reativa, fecha, grava commit de encerramento, exit 0, e a saída declara que houve reativação automática                  | 🟢          |
| RF-01b | `encerrar-sessao` sobre sessão **ausente** é no-op ruidoso, não erro           | Must       | Estado ausente (arquivo inexistente / campos `null`) → aviso "não havia sessão para encerrar", exit 0, sem commit de encerramento                            | 🟢          |
| RF-02  | Contrato de regen opcional no `harness.toml` lido por `./harness cmd regen`    | Must       | Com `regen` configurado, o comando executa o comando declarado via port de subprocesso; ausente → no-op silencioso com exit 0                                | 🟢          |
| RF-03  | Falha do regen é barulhenta e bloqueia o fechamento                            | Must       | Comando de regen retorna exit ≠ 0 → `./harness cmd regen` falha com exit ≠ 0 e mensagem; no fluxo "faz tudo", o fechamento **não** ocorre                    | 🟢          |
| RF-04  | Pré-check da working tree exclui `.harness/` e detecta trabalho solto          | Must       | Mudança fora de `.harness/` → sinalizada (marker sem TTY / pergunta com TTY); `.harness/estado-da-sessao.md` sozinho sujo **não** dispara a oferta           | 🟢          |
| RF-05  | Commit do trabalho pendente é por caminho, com mensagem descritiva             | Must       | O trabalho real é commitado via `git add -- <path>` (nunca `-A`); a working tree fica limpa fora de `.harness/` antes do fechamento                          | 🟢          |
| RF-06  | Invariante de fechamento preservado                                            | Must       | Commit de fechamento contém só `.harness/estado-da-sessao.md`; âncora = HEAD de trabalho anterior; saída reporta os dois hashes (regressão da 013/014 verde) | 🟢          |
| RF-07  | `init`/`upgrade` plantam o hook `SessionStart → cmd resume` de forma confiável | Must       | Após `init` ou `upgrade` num projeto, o settings/perfil do harness ativo contém o hook de resume; rematerialização converge ao mesmo resultado               | 🟡          |
| RF-08  | Skill de borda "faz tudo" orquestra regen → commit do trabalho → fechamento    | Should     | O slash command materializado conduz a sequência, delegando o fechamento ao `CommandService` (RN-N28/N29; não reimplementa o core)                           | 🟢          |
| RF-09  | Bump de versão e propagação                                                    | Must       | `version` em `config.py`, `current_version` em `init_service.py` e a asserção de `test_init.py` em 1.2.53; suíte verde                                       | 🟢          |

## 6. Requisitos Não Funcionais

| Tipo              | Requisito                                                                                                                       | Evidência ou justificativa                      | Confidência |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ----------- |
| Manutenibilidade  | Novo `cmd regen` é capacidade coesa e testável, isolada do `commit_paths` do fechamento                                         | Princípio nº 5 (alta coesão, SRP); brief §6     | 🟢          |
| Baixo acoplamento | Core não conhece o regen concreto do projeto; depende do contrato declarado e de um port de subprocesso                         | RN-N5; `_reversa_sdd/domain.md#2.3`             | 🟢          |
| Observabilidade   | Auto-reativação, regen e commit do trabalho são anunciados na saída; falhas são nomeadas (exceções) e barulhentas               | RN-N4/N32; Princípio nº 5.2 (erros barulhentos) | 🟢          |
| Reprodutibilidade | Contrato de regen é determinístico (config fora do código), roda igual ao longo do tempo                                        | RN-N16; Princípio nº 5.3                        | 🟢          |
| Segurança         | `cmd regen` executa um comando declarado pelo próprio dono do projeto; sem `git add -A`; nenhuma escrita fora de `project_path` | RN-N17; RN-N32                                  | 🟡          |
| Compatibilidade   | Mudança propaga via `upgrade` sem quebrar consumidores que não configuram `regen` (campo opcional)                              | RN-N20 (evolução não-destrutiva)                | 🟢          |

## 7. Critérios de Aceitação

```gherkin
Cenário: encerrar sessão inativa auto-reativa e fecha
  Dado um .harness/estado-da-sessao.md válido com status: inactive
  Quando executo ./harness cmd encerrar-sessao
  Então a sessão é reativada preservando a narrativa
  E um commit de encerramento é criado contendo apenas o state_file
  E a âncora aponta para o último commit de trabalho, não para o de encerramento
  E a saída anuncia que houve reativação automática
  E o código de saída é 0

Cenário: regen configurado roda antes do fechamento
  Dado harness.toml com um comando de regen válido
  Quando o fluxo de encerramento "faz tudo" é conduzido
  Então o comando de regen é executado primeiro
  E somente após seu sucesso o fechamento prossegue

Cenário: trabalho solto fora de .harness/ é commitado antes de fechar
  Dado mudanças não commitadas fora de .harness/
  Quando inicio o encerramento
  Então o pré-check sinaliza o trabalho pendente
  E o trabalho é commitado por caminho com mensagem descritiva
  E só então o commit de fechamento é gravado

Cenário (negativo): regen falha e o fechamento não ocorre
  Dado harness.toml com um comando de regen que retorna exit diferente de zero
  Quando executo o fluxo de encerramento
  Então ./harness cmd regen falha com exit diferente de zero e mensagem clara
  E nenhum commit de encerramento é criado
  E o estado da sessão não é alterado para inativo

Cenário (negativo): apenas o state_file sujo não dispara oferta de commit
  Dado que somente .harness/estado-da-sessao.md está modificado
  Quando inicio o encerramento
  Então a oferta de commit de trabalho pendente NÃO é disparada
  E o fechamento procede como hoje (regressão da 013/014 verde)

Cenário: encerrar sessão ausente é no-op ruidoso (D1)
  Dado que não existe .harness/estado-da-sessao.md ou ele está no estado inicial com campos null
  Quando executo ./harness cmd encerrar-sessao
  Então o comando emite o aviso "não havia sessão para encerrar"
  E nenhum commit de encerramento é criado
  E o código de saída é 0

Cenário (negativo): falha no meio do "faz tudo" preserva commits parciais e não fecha (D2)
  Dado que o trabalho pendente já foi commitado mas o regen subsequente falha
  Quando o fluxo de encerramento prossegue
  Então o commit do trabalho já feito permanece no histórico
  E nenhum commit de encerramento é criado
  E o estado da sessão não é alterado para inativo
  E re-rodar o encerramento após corrigir a causa fecha normalmente
```

## 8. Prioridade MoSCoW

| Item                             | MoSCoW | Justificativa                                                            |
| -------------------------------- | ------ | ------------------------------------------------------------------------ |
| RF-01 (auto-reativar)            | Must   | É o que mata a dor imediata do mantenedor (atrito ativa/inativa)         |
| RF-04/RF-05 (commit do pendente) | Must   | Núcleo do brief; remove a necessidade de lembrar de commitar antes       |
| RF-02/RF-03 (regen)              | Must   | Item (iii) explícito do pedido; contrato escolhido por baixo acoplamento |
| RF-06 (invariantes)              | Must   | Restrição inegociável; sem ela a feature regride 013/014                 |
| RF-07 (hook confiável)           | Must   | Corrige a raiz nos consumidores; sem ela a dor reaparece                 |
| RF-09 (bump/propagação)          | Must   | Sem propagar, os consumidores não recebem a correção                     |
| RF-08 (skill "faz tudo")         | Should | Superfície de conveniência; o core robusto já entrega o essencial        |

## 9. Esclarecimentos

### Sessão 2026-06-27

- **Q (D1, escopo):** Sobre sessão **ausente** (arquivo inexistente ou estado inicial com campos `null`), e não só inativa, o `encerrar-sessao` deve ser igualmente tolerante ou manter o erro barulhento da 015?
  **R:** Tolerante também. No-op com aviso explícito ("não havia sessão para encerrar") e exit 0, nunca erro. O pedido inteiro nasce de eliminar o atrito ativa/inativa; falhar barulhento no caso ausente o reintroduziria. O aviso preserva a honestidade (RN-N4) sem bloquear. Integrado em RN-01 e RF-01b, com cenário Gherkin próprio.
- **Q (D2, técnico):** Qual o contrato de recuperação se o regen ou o commit do trabalho falhar **no meio** do fluxo "faz tudo" — abortar sem fechar, ou tentar rollback?
  **R:** Abortar sem fechar, sem rollback, falha barulhenta e re-executável. Espelha a RN-N32 (`SessionCommitError` não reverte o estado salvo) e o "abortar-e-reexecutar" do brief: trabalho já commitado e regen já produzido permanecem (são legítimos); a sessão **não** é marcada encerrada, então re-rodar após corrigir fecha limpo. Rollback automático descartado por frágil e surpreendente (contra longevidade). Integrado no cenário negativo D2.

## 10. Lacunas

- 🟡 Investigação técnica (resolvida no `plan`/`investigation`, não no clarify): **por que** `init`/`upgrade` não materializaram o hook `SessionStart → cmd resume` no consumidor `contrato-fotos-higor` (perfil/versão/instalação incompleta). Hipótese da sessão de diagnóstico: o hook existe no design mas não foi plantado nesse projeto/perfil.

## 11. Histórico de alterações

| Data       | Alteração                                                                                               | Autor   |
| ---------- | ------------------------------------------------------------------------------------------------------- | ------- |
| 2026-06-27 | Versão inicial gerada por `/reversa-requirements`                                                       | reversa |
| 2026-06-27 | D1 e D2 integradas por `/reversa-clarify` (sessão ausente tolerante; falha no meio aborta sem rollback) | reversa |
