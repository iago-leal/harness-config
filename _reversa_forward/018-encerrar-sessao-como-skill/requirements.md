# Requirements: encerrar-sessao como skill versionável (skill como adaptador)

> Identificador: `018-encerrar-sessao-como-skill`
> Data: `2026-06-27`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Migrar a capacidade `encerrar-sessao` de **command** (entregue por slash command/workflow que delega ao binário `./harness`) para uma **skill versionável** que é, ela própria, o **adaptador por harness**. A skill embute **scripts finos e coesos** que consomem a lógica de domínio **já testada** do `harness-core` (commit, escrita de microdecisões, gravação do estado-da-sessão) — sem duplicar a lógica nem perder a rede de testes. Em vez de o `HarnessProfile` materializar um arquivo que chama o binário, ele materializa a skill, válida igualmente para **Claude Code** (`.claude/skills/`) e **Antigravity** (`.agents/skills/`). Motivação: a feature 017 e a validação por `skill-spec` mostraram que, no Antigravity, slash commands/workflows locais não são reconhecidos — skills são ativadas semanticamente e funcionam. Esta feature cobre **apenas `encerrar-sessao`** e estabelece o padrão reutilizável pelos demais comandos depois.

## 2. Contexto a partir do legado

| Fonte                                                             | Trecho relevante                                                                                                                                                                                                                                                                                | Confidência |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `_reversa_sdd/comandos-customizados/requirements.md#f010`         | Hoje `encerrar-sessao` é despachado pelo `CommandService`; o `init`/`upgrade` materializa slash commands de IDE que **apenas delegam** ao `./harness cmd encerrar-sessao` (RN-N5 preservada).                                                                                                   | 🟢          |
| `_reversa_sdd/domain.md` (RN-N5)                                  | "O Core Não Conhece o Harness": o domínio produz texto puro; a seleção do mecanismo de entrega por `active_harness` vive na borda (`sinks.py`, `main.py`).                                                                                                                                      | 🟢          |
| `_reversa_sdd/domain.md` (RN-N29)                                 | Superfície de comando encapsulada no `HarnessProfile.session_command_artifact(command_path) -> (rel_path, content)`. É o ponto de adaptação que esta feature reformula.                                                                                                                         | 🟢          |
| `_reversa_sdd/domain.md` (RN-N2; `Decision`; `SessionState`)      | Estado-da-sessão em `.harness/estado-da-sessao.md` com serializer round-trip (4 seções); microdecisões `MD-NNNN.md` em `.harness/decisoes/` com índice derivado `.harness/microdecisoes.md`; commit isolado via `GitPort.commit_paths` (RN-N31/N32). São as três lógicas que a skill orquestra. | 🟢          |
| `_reversa_sdd/adrs/0011-reinjecao-multi-harness-strategy-sink.md` | A adaptação multi-harness é hoje um Strategy (`HarnessProfile`/`SessionSink`). Esta feature faz a unidade de adaptação passar a ser a skill.                                                                                                                                                    | 🟢          |
| Descoberta empírica (sessão atual, feature 017 + `skill-spec`)    | Workflows/slash commands locais não são reconhecidos pelo Antigravity; skills (`.agents/skills/<nome>/SKILL.md`, `name`+`description`) são ativadas por contexto. SPEC da skill `encerrar-sessao` pontuou 82/100.                                                                               | 🟢          |

## 3. Personas e cenários de uso

| Persona                           | Objetivo                                                              | Cenário-chave                                                                                                                        |
| --------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Mantenedor no Claude Code         | Encerrar a sessão por uma skill versionada, não por command delegado  | Ativa a skill `encerrar-sessao`; seus scripts finos conduzem commit + microdecisões + estado e fecham.                               |
| Mantenedor no Antigravity         | Mesma capacidade, mesma skill, no formato que o Antigravity reconhece | Pede "encerre a sessão"; a skill em `.agents/skills/` ativa por contexto e executa a mesma lógica.                                   |
| Mantenedor que versiona o tooling | Evoluir a capacidade com rastreabilidade                              | A skill tem versão no front-matter; mudanças na orquestração são versionadas com a skill, a lógica de domínio segue testada no core. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** A capacidade `encerrar-sessao` é entregue como **skill versionável** (`SKILL.md` com `name`+`description`+`version`), e não mais como slash command/workflow que delega ao binário. 🟢
   - Origem no legado: altera o mecanismo de RN-N29 e o artefato de `comandos-customizados/#f010`. Tipo: **alterada**.
2. **RN-02:** A skill embute **scripts finos e coesos** (um por responsabilidade — commit, microdecisão, estado) que **consomem a lógica de domínio testada do `harness-core` como biblioteca**, sem duplicá-la. O commit é por caminho (nunca `git add -A`); o estado segue o serializer de 4 seções com commit isolado do `state_file` (RN-N31/N32); a microdecisão segue o formato `MD-NNNN` + índice derivado. 🟢
   - Origem no legado: `domain.md` (RN-N2, `Decision`, RN-N31/N32). Tipo: **alterada** (a _entrega_ muda; a lógica permanece no core).
3. **RN-03:** A mesma capacidade vale para **Claude Code e Antigravity** — a skill é materializada no diretório de skills de cada harness (`.claude/skills/encerrar-sessao/` e `.agents/skills/encerrar-sessao/`) pelo mesmo adaptador. 🟢
   - Tipo: **nova**.
4. **RN-04:** **A skill é o adaptador.** O `HarnessProfile` (ou sucessor) passa a materializar a skill por harness (`SKILL.md` + scripts finos), substituindo a materialização de slash command/workflow que delega ao binário. A lógica de domínio segue no core (RN-N5 preservada: o core não conhece o harness). 🟢
   - Origem no legado: `adrs/0011`, RN-N29. Tipo: **alterada**.
5. **RN-05:** O escopo desta feature é **apenas `encerrar-sessao`**. O padrão "skill-como-adaptador sobre o core testado" estabelecido aqui é o molde para `resume`/`handoff`/`clarificar` (e depois os hooks) migrarem em features curtas subsequentes. 🟢
   - Tipo: **nova** (decisão de escopo).

## 5. Requisitos Funcionais

| ID    | Requisito                                | Prioridade | Critério de aceite                                                                                                                                                                            | Confidência |
| ----- | ---------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | Skill `encerrar-sessao` versionável.     | Must       | Existe `encerrar-sessao/SKILL.md` com `name`, `description` e `version`; estrutura idêntica ao padrão de skills do projeto (validável por `skill-spec`, score ≥ 80).                          | 🟢          |
| RF-02 | Scripts finos consumindo o core.         | Must       | A pasta da skill contém `scripts/` que importam/chamam a lógica do `harness-core` (commit, microdecisão, estado) sem reimplementá-la; cada script tem responsabilidade única e teste próprio. | 🟢          |
| RF-03 | Paridade Claude ↔ Antigravity.           | Must       | O mesmo adaptador materializa a skill em `.claude/skills/encerrar-sessao/` e `.agents/skills/encerrar-sessao/`; ambos ativam a mesma capacidade.                                              | 🟢          |
| RF-04 | Adaptador passa a emitir skill.          | Must       | `HarnessProfile` (ou sucessor) deixa de materializar slash command/workflow que delega ao binário e passa a materializar a skill; `init`/`upgrade` propagam.                                  | 🟢          |
| RF-05 | Versionamento e migração não-destrutiva. | Should     | A versão da skill é rastreável; o `upgrade` substitui os artefatos antigos (workflow/command) pela skill sem tocar artefatos de terceiros.                                                    | 🟢          |

## 6. Requisitos Não Funcionais

| Tipo                       | Requisito                                                                                                                                                | Evidência ou justificativa                                                                                         | Confidência |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ----------- |
| Testabilidade              | A lógica de commit/microdecisões/estado permanece no `harness-core` sob TDD (cobertura de domínio ≥ 60%); os scripts finos da skill têm testes próprios. | A decisão (clarify) de manter o core como biblioteca preserva a rede de testes; nada de lógica nova fora de teste. | 🟢          |
| Baixo acoplamento / coesão | A skill é casca fina de orquestração (SRP por script); a fonte única de verdade da lógica é o core. Sem duplicação (DRY).                                | Princípio P5 do mantenedor.                                                                                        | 🟢          |
| Robustez (erro barulhento) | Falhas em commit/escrita falham explícitas (exit ≠ 0 / mensagem), nunca silenciosas.                                                                     | Princípio do projeto; contrato de saída atual.                                                                     | 🟢          |
| Não-destrutividade         | A migração não apaga artefatos de terceiros nem trabalho do usuário; substitui apenas o que o harness gera.                                              | Diretriz non-destructive do Reversa/Harness.                                                                       | 🟢          |

## 7. Critérios de Aceitação

```gherkin
Cenário: a capacidade é entregue como skill nos dois harnesses
  Dado um projeto inicializado para Claude Code e outro para Antigravity
  Quando o init/upgrade materializa a capacidade de encerrar sessão
  Então existe encerrar-sessao/SKILL.md no diretório de skills de cada harness
  E o front-matter tem name, description e version
  E a pasta da skill contém os scripts finos de orquestração

Cenário: a skill conduz as três operações reusando o core
  Dado uma sessão ativa com trabalho commitável
  Quando a skill encerrar-sessao é ativada
  Então o trabalho é commitado por caminho (nunca git add -A) via a lógica do core
  E uma microdecisão é registrada no formato MD-NNNN quando aplicável
  E o estado-da-sessão é gravado e versionado em commit isolado

Cenário: a migração não destrói artefatos alheios
  Dado um projeto com workflow/command antigo de encerrar-sessao
  Quando o upgrade roda
  Então o artefato antigo gerado pelo harness é substituído pela skill
  E artefatos de terceiros permanecem intactos

Cenário (negativo): falha de commit é barulhenta
  Dado que o commit do estado falha
  Quando a skill tenta encerrar
  Então a falha é reportada explicitamente (exit ≠ 0 / mensagem), sem fechar silenciosamente
```

## 8. Prioridade MoSCoW

| Item                                | MoSCoW | Justificativa                                                |
| ----------------------------------- | ------ | ------------------------------------------------------------ |
| RF-01 (skill versionável)           | Must   | É o cerne da migração.                                       |
| RF-02 (scripts finos sobre o core)  | Must   | Materializa a decisão de não duplicar a lógica testada.      |
| RF-03 (paridade Claude/Antigravity) | Must   | Requisito explícito do usuário.                              |
| RF-04 (adaptador emite skill)       | Must   | É a mudança de mecanismo pedida.                             |
| RF-05 (versionamento/migração)      | Should | Garante propagação limpa.                                    |
| RNF de testabilidade/coesão         | Must   | Condiciona o desenho; não pode regredir a qualidade interna. |

## 9. Esclarecimentos

### Sessão 2026-06-27

- **Q:** Como a skill deve carregar a lógica de commit, microdecisões e gravação do estado?
  **R (recomendação adotada):** **Scripts finos + core como biblioteca.** Duplicar a lógica violaria DRY e criaria duas fontes divergentes (dívida + acoplamento); delegar puro não "contém scripts". Os scripts finos da skill consomem a lógica de domínio testada do `harness-core`, entregando a skill versionável _com_ scripts sem perder os 210 testes nem duplicar. Reflete em RN-02 e RF-02.
- **Q:** Qual o destino do `CommandService`/serializer/`DecisionService`?
  **R:** **Manter como biblioteca testada.** A lógica permanece no hexágono sob TDD (cobertura ≥ 60%, erro barulhento), fonte única de verdade; a skill é o adaptador fino que a consome. Aposentar perderia a rede de testes; coexistir criaria dívida temporária. Reflete em RN-04 e RNF de testabilidade.
- **Q:** Qual a abrangência da migração?
  **R:** **Só `encerrar-sessao`**, estabelecendo o padrão. Proporcionalidade (P4) e mínima dívida: validar o molde numa capacidade antes de propagar; `resume`/`handoff`/`clarificar` e os hooks migram depois pelo mesmo padrão, em features curtas. Reflete em RN-05.

## 10. Lacunas

> Nenhuma lacuna pendente. As três dúvidas iniciais foram resolvidas na sessão de esclarecimentos de 2026-06-27.

## 11. Histórico de alterações

| Data       | Alteração                                                                                                                                                    | Autor   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| 2026-06-27 | Versão inicial gerada por `/reversa-requirements`                                                                                                            | reversa |
| 2026-06-27 | Esclarecimentos integrados (scripts finos + core como lib; manter core testado; escopo só encerrar-sessao); marcadores de dúvida zerados; RN-05 acrescentada | reversa |
