# Requirements: harness-core como módulo per-projeto autocontido

> Identificador: `006-harness-core-config-canonica`
> Data: `2026-06-24`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA
> Nota de identidade: o nome da pasta (`...-config-canonica`) é histórico, da premissa original. A clarify de 2026-06-24 reviu o escopo: a feature deixou de buscar "substituir o `~/.claude`" e passou a consolidar o `harness-core` como módulo per-projeto. Ver §9.
> Precedente: feature 004 (estado de sessão sob `.harness/`) e feature 005 (decisões sob `.harness/`).

## 1. Resumo executivo

Consolidar o `harness-core` como módulo **per-projeto autocontido**, dirigido por configuração e com **footprint global zero**: instalá-lo ou executá-lo nunca escreve fora do repositório do projeto. A feature abandona deliberadamente a premissa anterior de tornar o `harness-core` substituto do `~/.claude` (reframe da clarify, §9), porque esse alvo era do fornecedor, reacoplava a um único harness e tinha raio de explosão global. A entrega concreta é interna e segura: unificar a configuração numa via única tipada, parametrizar o caminho de estado de sessão, e selar tudo com um contrato de footprint testado. Beneficiário: o mantenedor intermitente, que passa a instalar o harness em qualquer projeto com confiança, sem risco à sua memória global.

## 2. Contexto a partir do legado

| Fonte                                                                  | Trecho relevante                                                                                                                                                                        | Confidência |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `harness-core/src/core/install/template.md:23`                         | Regra vigente já per-projeto: "aplique SEMPRE no `.claude/settings.json` do projeto. Nunca edite a configuração global em `~/.claude`"                                                  | 🟢          |
| `harness-core/src/core/formatting/service.py:25-27` + `harness.toml:7` | `~/.claude` e `~/Notas` blindados contra escrita do harness (BR-MIGRAR-007) — a preservar                                                                                               | 🟢          |
| `~/.agent-memory/` (repo git, remoto `iago-leal/agent-memory`)         | Memória global do mantenedor é um repositório versionado e separado, com `decisoes/`, `microdecisoes.md`, `bin/`, `ALICERCE.md` — é o nível global, distinto do `.harness/` per-projeto | 🟢          |
| `.harness/decisoes/MD-0004.md`                                         | Declarava a intenção de "substituto da config global"; esta feature **reverte** essa intenção (ver §9)                                                                                  | 🟢          |
| `_reversa_sdd/adrs/0012-caminhos-decisao-por-configuracao.md#decisao`  | Padrão "caminhos por configuração" (seção tipada lida por `load_config`, injetada na borda) — molde do saneamento                                                                       | 🟢          |
| `_reversa_sdd/adrs/0012-...#alternativas-consideradas`                 | Seção `[session]` análoga a `[decisions]` foi desenhada mas não implementada na 005 (resíduo de T2)                                                                                     | 🟢          |
| `_reversa_sdd/session/requirements.md#Regras-de-Negócio`               | RN-N1 (locus canônico único sob `.harness/`) e RN-N5 ("o core não conhece o harness") — precedente direto                                                                               | 🟢          |
| `harness-core/src/main.py` (`load_harness_config` vs `load_config`)    | Duas vias de configuração coexistem (dívida T5): dict legado sem `[decisions]` × config tipada                                                                                          | 🟢          |

> Nota de saneamento: a extração `_reversa_sdd/` documenta os bugs de driver T1/T2/T3 como abertos, mas o código vivo confirma que já foram corrigidos no commit `cf73980` (o MCP importa `load_config` e lê `config.decisions`; o caminho de sessão do MCP aponta para `.harness/estado-da-sessao.md`). Logo, **não há T1/T2/T3 a refazer**. Permanece em aberto apenas o que esta feature trata: parametrizar o caminho de sessão por `[session]` e unificar as duas vias de config (T5).

## 3. Personas e cenários de uso

| Persona                         | Objetivo                                             | Cenário-chave                                                                                                              |
| ------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Mantenedor intermitente         | Instalar o harness em qualquer projeto com confiança | Roda o `install-prompt` num repositório novo; nada é escrito em `~/.claude` nem em `~/.agent-memory`                       |
| Agente de IA (qualquer harness) | Validar e consultar as decisões do projeto           | O hook `Stop` local chama `./harness decisions`; `.harness/microdecisoes.md` é regenerado, sem depender de scripts globais |
| Mantenedor (memória global)     | Manter a memória transversal separada e intacta      | `~/.agent-memory` segue como nível global versionado, sem interferência do harness do projeto                              |

## 4. Regras de negócio novas ou alteradas

1. **RN-01: Footprint global zero** 🟢
   - Instalar ou executar o `harness-core` escreve apenas dentro do repositório do projeto. `~/.claude` e `~/.agent-memory` nunca são escritos pelo harness.
   - Origem no legado: `harness-core/src/core/install/template.md:23`; `formatting/service.py:25-27`.
   - Tipo: nova (eleva a regra existente a invariante testável).
2. **RN-02: `harness-core` é módulo per-projeto, não config global** 🟢
   - A canonicidade vale **dentro** do projeto (`.harness/` + `harness.toml`). A feature não substitui nem gerencia a config global do fornecedor (`~/.claude`).
   - Origem no legado: reframe da clarify (§9); `.harness/decisoes/MD-0004.md` (revertido).
   - Tipo: alterada (reverte a intenção de `MD-0004`).
3. **RN-03: Dois níveis de memória, nomeados e sem competição** 🟢
   - Nível global: `~/.agent-memory` (transversal, repo próprio). Nível per-projeto: `<repo>/.harness/`. O `harness-core` opera somente no nível per-projeto.
   - Origem no legado: verificação de `~/.agent-memory`; `_reversa_sdd/adrs/0011-...`.
   - Tipo: nova.
4. **RN-04: Neutralidade a harness preservada** 🟢
   - O locus único sob `.harness/` é neutro; a variação por agente fica isolada na borda por `active_harness`.
   - Origem no legado: `_reversa_sdd/session/requirements.md#Regras-de-Negócio` (RN-N5); `_reversa_sdd/adrs/0011-...`.
   - Tipo: nova (invariante de preservação).
5. **RN-05: Zona protegida do `~/.claude` preservada** 🟢
   - A blindagem BR-MIGRAR-007 permanece; a feature não relaxa nenhuma regra que proteja a config global.
   - Origem no legado: `harness-core/src/core/formatting/service.py:25-27`.
   - Tipo: nova (confirmação explícita).
6. **RN-06: Toda config dirigida por uma via única tipada** 🟢
   - O caminho de estado de sessão passa a vir de uma seção `[session]` no `harness.toml`; a via de config legada (`load_harness_config`) é removida em favor de `load_config`.
   - Origem no legado: `_reversa_sdd/adrs/0012-...` (padrão); dívida T5.
   - Tipo: alterada.

## 5. Requisitos Funcionais

| ID    | Requisito                                                                                                            | Prioridade            | Critério de aceite                                                                                                                                | Confidência |
| ----- | -------------------------------------------------------------------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | Caminho de estado de sessão dirigido por configuração (nova seção `[session]` no `harness.toml`, lida por CLI e MCP) | Must                  | Alterar `[session]` no `harness.toml` muda o caminho lido pela CLI e pelo MCP; nenhum literal de caminho de sessão chumbado sobrevive nos drivers | 🟢          |
| RF-02 | Via única de configuração: remover `load_harness_config` legado, tudo por `load_config` tipada                       | Must                  | `grep load_harness_config` não retorna usos; o subcomando `cmd` lê `active_harness` via `load_config`                                             | 🟢          |
| RF-03 | Contrato de footprint global zero, testado                                                                           | Must                  | Existe teste que falha de forma barulhenta se qualquer escrita do harness mirar `~/.claude`, `~/.agent-memory` ou caminho fora do repositório     | 🟢          |
| RF-04 | Zona protegida preservada                                                                                            | Must                  | BR-MIGRAR-007 mantida; nenhum caminho novo de escrita global é introduzido                                                                        | 🟢          |
| RF-05 | Registrar a reversão da premissa global                                                                              | Should                | Nova ficha `MD-NNNN` em `.harness/decisoes/` aposenta a intenção "substituto da config global" de `MD-0004`, com backlink                         | 🟡          |
| RF-06 | Scripts globais de observabilidade reconhecerem `.harness/` (antigo RF-04 da 005)                                    | Won't (nesta feature) | Diferido para o repo `agent-memory` como mudança própria; no projeto, o hook `Stop` → `./harness decisions` já cobre validação e índice           | 🟢          |

## 6. Requisitos Não Funcionais

| Tipo                    | Requisito                                                                                          | Evidência ou justificativa                      | Confidência |
| ----------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ----------- |
| Manutenibilidade        | Módulo autocontido e dirigido por uma via única de config                                          | Padrão do ADR 0012; remove dívida T5            | 🟢          |
| Acoplamento             | Dois níveis de memória nomeados, sem competição; core agnóstico ao harness                         | RN-N5 da 004; `~/.agent-memory` separado        | 🟢          |
| Segurança / Privacidade | Footprint zero protege segredos e histórico do global; nada do `~/.claude` é versionado no projeto | `~/.claude` guarda `sessions/`, `history.jsonl` | 🟢          |
| Observabilidade         | Erros barulhentos; o contrato de footprint falha alto se algo tentar escrever no global            | Princípio do projeto; RF-03                     | 🟢          |
| Reprodutibilidade       | Instalar em projeto novo é git-reproduzível, sem estado global oculto                              | Sem symlink/env/XDG; tudo no repo               | 🟢          |

## 7. Critérios de Aceitação

```gherkin
Cenário: caminho de sessão por configuração
  Dado um harness.toml com a seção [session] apontando para um caminho X
  Quando a CLI e o MCP carregam o estado de sessão
  Então ambos leem de X, sem caminho de sessão chumbado no código

Cenário: via única de configuração
  Dado que load_harness_config foi removido
  Quando o subcomando cmd lê o active_harness
  Então ele o obtém via load_config tipada, e a suíte segue verde

Cenário: footprint global zero
  Dado um repositório de teste
  Quando o harness-core é instalado e executado
  Então nenhuma escrita ocorre em ~/.claude nem em ~/.agent-memory

Cenário (negativo): tentativa de escrita global falha barulhento
  Dado um caminho de escrita que aponta para fora do repositório
  Quando o harness tenta gravar
  Então a operação falha com erro explícito, não em silêncio

Cenário: zona protegida preservada
  Dado um arquivo sob ~/.claude
  Quando o autoformat do harness é acionado
  Então ele aborta sem formatar (BR-MIGRAR-007)
```

## 8. Prioridade MoSCoW

| Item                                           | MoSCoW                | Justificativa                                                           |
| ---------------------------------------------- | --------------------- | ----------------------------------------------------------------------- |
| RF-01 caminho de sessão por `[session]`        | Must                  | Fecha o resíduo de T2; deixa o módulo dirigido por config ponta a ponta |
| RF-02 via única de config                      | Must                  | Remove a dívida T5; precondição de um módulo confiável                  |
| RF-03 contrato de footprint testado            | Must                  | Transforma o medo do global em guardrail barulhento                     |
| RF-04 zona protegida preservada                | Must                  | Não regredir a salvaguarda existente                                    |
| RF-05 registrar a reversão                     | Should                | Coerência do histórico de decisões (reverte `MD-0004`)                  |
| RF-06 scripts globais reconhecerem `.harness/` | Won't (nesta feature) | Concern global, em repo separado; diferido por decisão da clarify (2a)  |

## 9. Esclarecimentos

### Sessão 2026-06-24

- **Q:** Objetivo da 006: tornar o `harness-core` config canônica global (substituto do `~/.claude`) ou módulo instalável per-projeto sem influenciar a memória global?
  **R:** Módulo per-projeto autocontido, com footprint global zero (opção 1a). A premissa de substituir o `~/.claude` foi abandonada: o alvo era do fornecedor, reacoplava a um único harness e tinha raio de explosão global. Resolve a DÚVIDA #1 (não há mecanismo global a escolher) e a DÚVIDA #2 (alcance = só per-projeto; zona protegida preservada).
- **Q:** O que fazer com o RF-04 diferido da 005 (scripts globais reconhecerem `.harness/`), que é o único ponto a tocar no global?
  **R:** Largar o global nesta feature (opção 2a). No projeto, o hook `Stop` → `./harness decisions` já valida e indexa as decisões em `.harness/` sem depender dos scripts globais. A mudança nos scripts fica para o repo `agent-memory`, como item próprio, se e quando `.harness/` virar convenção em vários projetos. Verificação que sustentou a decisão: `~/.agent-memory` é repo git versionado com remoto, então um eventual patch lá seria um commit normal e reversível, não estado solto.
- **Q:** O saneamento interno (unificar as duas vias de config — T5 — e parametrizar o caminho de sessão via `[session]`) entra no escopo?
  **R:** Sim (opção 3a). É higiene 100% per-projeto, alinhada a "módulo limpo e autocontido", e remove dívida adjacente barata. Resolve a DÚVIDA #3.

## 10. Lacunas

- ✅ Dúvidas #1, #2 e #3 resolvidas na clarify de 2026-06-24 (ver §9). Nenhum ponto em aberto.
- 📌 Diferido (fora desta feature, por decisão 2a): ensinar os scripts globais `~/.agent-memory/bin/guardrail-decisoes.sh` e `microdecisoes-guard.py` a reconhecerem `.harness/` — a tratar no repo `agent-memory` como mudança própria.
- ℹ️ Detalhe de implementação para o `/reversa-plan`, não dúvida de requisito: a forma de asserção do contrato de footprint (RF-03) — por exemplo, um `FileSystemPort` instrumentado nos testes que rejeite caminhos fora do repositório.

## 11. Histórico de alterações

| Data       | Alteração                                                                                                                                                                 | Autor   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| 2026-06-24 | Versão inicial gerada por `/reversa-requirements`                                                                                                                         | reversa |
| 2026-06-24 | Clarify: premissa revista para módulo per-projeto (1a/2a/3a); RF-04 global diferido; saneamento (T5 + `[session]`) no escopo; reversão de `MD-0004` registrada como RF-05 | reversa |
