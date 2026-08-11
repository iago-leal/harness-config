# Requirements: Índice de microdecisões leve com consulta sob demanda

> Identificador: `028-indice-decisoes-sob-demanda`
> Data: `2026-08-11`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O índice derivado de microdecisões (`.harness/microdecisoes.md`) cresce linearmente com o número de fichas e é reinjetado íntegro no início de cada sessão do Claude (feature 021), além de servir de ponto de consulta para os agentes. Em projeto anterior do mantenedor, esse crescimento inchou o contexto: cada sessão e cada consulta pagavam o acervo inteiro em tokens. Esta feature limita o custo de contexto do índice a um teto que não cresce com o acervo, mantendo o grafo completo acessível sob demanda e ensinando o agente onde buscá-lo. Nenhuma informação se perde: as fichas `MD-NNNN.md` seguem sendo a fonte de verdade.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/microdecisoes/requirements.md#RN-N12` | O índice é DERIVADO por `harness decisions` (hook Stop), com backlinks por verbos inversos, determinístico, "não edite à mão". | 🟢 |
| `_reversa_sdd/microdecisoes/requirements.md#RN-N11` | Caminhos (`dir`, `index_file`, `header_file`) vêm de `[decisions]` no `harness.toml`; nada chumbado no serviço. | 🟢 |
| `_reversa_sdd/session/requirements.md` (feature 021) | O `resume` (SessionStart) anexa o índice INTEIRO ao contexto reinjetado, gated por `active_harness == "claude"` e `session.inject_decisions_index` (default `true`); índice ausente → aviso e segue só com o estado (`resume_context.py`; `main.py`, ramo `cmd resume`). | 🟢 |
| `_reversa_sdd/domain.md#2.20` (RN-N36, fonte única) | Mudança comportamental num comando propaga a todos os projetos pelo shim, sem regravar hooks materializados. | 🟢 |
| `_reversa_sdd/microdecisoes/requirements.md#RN-N14` | Front-matter obrigatório com `id`, `gancho`, `estado`, `relacoes`; relações tipadas num conjunto fechado de seis verbos (inclui `substitui`). | 🟢 |
| `_reversa_sdd/progress/requirements.md` (features 026/027) | Padrão consolidado dos artefatos derivados: determinísticos, sem timestamp nem valor volátil, escrita atômica, write-only-when-changed. | 🟢 |
| Constatação as-built (2026-08-11) | O core NÃO escreve `CLAUDE.md` nem `AGENTS.md` hoje: nenhuma referência a esses arquivos existe em `src/` (guidance materializada seria classe nova de artefato). | 🟢 |
| `.harness/decisoes/MD-0016.md` (as-built) | Ficha substituída (MD-0016 ← `substitui` da MD-0018) permanece com `estado: ativo` no front-matter: a vigência real hoje só é derivável das relações, não do campo `estado`. | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor (single maintainer intermitente) | Retomar o projeto após semanas pagando pouco contexto por sessão, sem perder o histórico decisório | Abre sessão num projeto com acervo grande de fichas e o bloco inicial continua pequeno |
| Agente de sessão (Claude / Antigravity) | Saber que o grafo de decisões existe e onde consultá-lo, sem carregá-lo inteiro a cada sessão | Recebe visão compacta no SessionStart; ao investigar um tema, segue o ponteiro e lê só o necessário |
| Harness core | Derivar as visões do acervo no mesmo passo de reindexação já existente (hook Stop) | `harness decisions` valida o grafo e regrava as visões quando o acervo muda |

## 4. Regras de negócio novas ou alteradas

1. **RN-01 — Custo de contexto limitado no SessionStart:** o bloco de decisões injetado na abertura da sessão tem teto que NÃO cresce com o número de fichas; hoje o custo é linear (injeção integral do índice). 🟢
   - Origem no legado: `_reversa_sdd/session/requirements.md` (feature 021)
   - Tipo: alterada
2. **RN-02 — Índice completo vira artefato de consulta sob demanda:** o índice consolidado com backlinks continua derivado, determinístico e não editado à mão (`_reversa_sdd/microdecisoes/requirements.md#RN-N12` preservada), mas deixa de ser o artefato injetado: passa a ser referenciado pelo bloco compacto e lido apenas quando a tarefa pede. 🟢
   - Origem no legado: `_reversa_sdd/microdecisoes/requirements.md#RN-N12`
   - Tipo: alterada
3. **RN-03 — Visão compacta derivada da mesma fonte:** a visão injetada é derivada das mesmas fichas, pelo mesmo comando `harness decisions`, na mesma passada de reindexação; sem timestamp nem valor volátil, com escrita atômica e regravação apenas quando o conteúdo muda (padrão das features 026/027). 🟢
   - Tipo: nova
4. **RN-04 — O caminho da consulta é ensinado ao agente:** o próprio bloco injetado orienta, no cabeçalho, onde está o acervo completo (índice e fichas), nas duas engines; complementarmente, a **instalação** (`harness init`) grava um trecho curto de guidance no `CLAUDE.md` do projeto situando o agente (à maneira do Reversa: escrita única na instalação, idempotente em re-execução, sem gestão contínua de merge). 🟢
   - Tipo: nova
   - Nota: o equivalente para a engine Antigravity (arquivo de guidance próprio) segue a mesma regra. 🟡
5. **RN-05 — Compatibilidade de contratos:** `session.inject_decisions_index = false` segue suprimindo qualquer bloco; nenhum hook materializado é regravado (a mudança propaga pela fonte única, RN-N36); o gate de registro (RN-N43..N47) e o portão do encerramento não são afetados. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.20`
   - Tipo: alterada (semântica preservada, conteúdo do bloco muda)
6. **RN-06 — Integridade do grafo permanece global:** `validate_integrity` continua cobrindo TODAS as fichas (auto-relação, aresta órfã, seções obrigatórias — `_reversa_sdd/microdecisoes/requirements.md#RN-N13`), independentemente de como as visões sejam particionadas. 🟢
   - Origem no legado: `_reversa_sdd/microdecisoes/requirements.md#RN-N13`
   - Tipo: alterada (escopo de validação inalterado sob novo layout)
7. **RN-07 — Migração autoresolvente:** projetos existentes convergem sem passo manual: a primeira reindexação após o upgrade produz o novo layout de visões; nenhuma ficha é movida, renomeada ou apagada. 🟢
   - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Derivar uma visão compacta do acervo: as K fichas mais recentes por ID, apenas título (sem sublinhas de backlinks), mais contagem total e ponteiro para o índice completo e as fichas. K vem de `[decisions]` no `harness.toml`, default 10. | Must | Num acervo de 200 fichas com K default, o bloco compacto lista as 10 mais recentes, só títulos, informa o total (200) e o caminho do acervo completo. | 🟢 |
| RF-02 | O `resume` injeta a visão compacta no lugar do índice integral, mantendo o gate por harness e a flag `inject_decisions_index`. | Must | O tamanho do bloco injetado não cresce com o acervo além do teto; com a flag `false`, nenhum bloco é injetado. | 🟢 |
| RF-03 | `harness decisions` deriva todas as visões na mesma passada, validando o grafo inteiro antes, com escrita atômica e regravação só quando o conteúdo muda. | Must | Duas execuções consecutivas sem mudança no acervo produzem bytes idênticos e nenhuma regravação; aresta órfã em qualquer ficha continua acusada. | 🟢 |
| RF-04 | Consultar o acervo completo sob demanda é um único passo a partir do bloco injetado: o índice completo permanece num ÚNICO arquivo, em caminho previsível, configurável em `[decisions]`. | Must | Um agente que só leu o bloco injetado encontra o índice completo seguindo exclusivamente o ponteiro do bloco. | 🟢 |
| RF-05 | Na instalação, `harness init` grava um trecho curto de guidance no `CLAUDE.md` do projeto explicando o índice de decisões e a consulta sob demanda (escrita única, idempotente; sem gestão contínua de merge/upgrade). | Must | Após `init`, o `CLAUDE.md` contém o trecho; re-executar `init` não o duplica; o upgrade não o toca. | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho (contexto) | O bloco injetado no SessionStart carrega no máximo K fichas (default 10, configurável em `[decisions]`), independente do tamanho do acervo. | Queixa de origem: índice inchado gastava tokens a cada sessão/consulta em projeto anterior; decisão do clarify de 2026-08-11. | 🟢 |
| Determinismo | Todas as visões derivadas são reprodutíveis byte a byte a partir das fichas; sem timestamp, hora ou caminho absoluto. | Padrão consolidado nas features 026/027 (`_reversa_sdd/progress/requirements.md`). | 🟢 |
| Robustez | Visão ou índice ausentes nunca quebram o `resume` nem o hook: aviso em stderr e degradação graciosa (as fichas seguem a fonte de verdade). | Comportamento atual do `resume` com índice ausente (não-bloqueante, RN-N4). | 🟢 |
| Manutenibilidade | Caminhos das visões por configuração, sem literais no serviço; nenhuma segunda implementação do parse de fichas. | `_reversa_sdd/microdecisoes/requirements.md#RN-N11`. | 🟢 |
| Compatibilidade | Projetos com o layout atual convergem na primeira reindexação pós-upgrade, sem intervenção manual e sem migração de dados nas fichas. | Padrão de transição autoresolvente das features 016/023 (sem código de migração). | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: acervo grande não incha o contexto da sessão
  Dado um projeto com 200 fichas MD-*.md válidas
  Quando o hook SessionStart executa o resume
  Então o bloco de decisões injetado lista no máximo K fichas (default 10), apenas títulos
  E informa o total de fichas e onde consultar o acervo completo

Cenário: consulta sob demanda em um passo
  Dado um agente que recebeu apenas o bloco compacto
  Quando ele precisa do histórico de decisões sobre um tema
  Então o ponteiro do próprio bloco o leva ao índice completo (ou à partição relevante)
  E as fichas individuais permanecem legíveis nos caminhos de `[decisions]`

Cenário: reindexação determinística e econômica
  Dado um acervo sem mudanças desde a última reindexação
  Quando `harness decisions` roda duas vezes seguidas
  Então os artefatos derivados ficam byte a byte idênticos e nada é regravado

Cenário: integridade global sob particionamento
  Dado uma ficha fora da visão compacta com relação apontando para MD inexistente
  Quando `harness decisions` roda
  Então o erro de aresta órfã é acusado normalmente (a validação cobre o acervo inteiro)

Cenário: trecho de guidance gravado na instalação
  Dado um projeto recém-inicializado com `harness init`
  Quando o mantenedor abre o `CLAUDE.md` do projeto
  Então há um trecho curto explicando o índice de decisões e a consulta sob demanda
  E re-executar `init` não duplica o trecho

Cenário negativo: injeção desligada
  Dado `session.inject_decisions_index = false` no harness.toml
  Quando o resume executa
  Então nenhum bloco de decisões é injetado, nem compacto nem integral

Cenário negativo: visão derivada ausente
  Dado que os artefatos derivados ainda não foram gerados no novo layout
  Quando o resume executa
  Então o comando avisa em stderr e segue não-bloqueante, sem quebrar a sessão
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 (visão compacta com teto) | Must | É a entrega central: sem ela o custo segue linear. |
| RF-02 (resume injeta a compacta) | Must | O ponto de dor é a injeção de sessão; é onde o teto se materializa. |
| RF-03 (derivação única, íntegra e idempotente) | Must | Preserva RN-N12/RN-N13 e o padrão de artefato derivado do projeto. |
| RF-04 (consulta em um passo) | Must | Sem trilha clara, o agente volta a varrer tudo e o ganho evapora. |
| RF-05 (trecho de guidance no init) | Must | Decisão do clarify: escopo mínimo (escrita única na instalação, sem gestão contínua), custo baixo e situa o agente fora do SessionStart. |
| RNF de desempenho (K=10 default, configurável) | Should | Valor calibrável por projeto sem tocar código. |

## 9. Esclarecimentos

### Sessão 2026-08-11

- **Q:** D1a — O que entra na visão compacta injetada no SessionStart?
  **R:** As K fichas mais recentes por ID, apenas títulos (sem as sublinhas de backlinks), mais contagem total e ponteiro para o acervo completo. O filtro por vigência foi descartado (o campo `estado:` não é confiável para isso e a derivação pelas relações adicionaria complexidade sem necessidade).
- **Q:** D1b — Como fica o acervo completo para consulta sob demanda?
  **R:** Arquivo único: o índice completo com backlinks permanece num só arquivo, apenas deixa de ser injetado. Particionamento por faixa ou tema foi descartado.
- **Q:** D2 — Qual o teto da visão compacta e onde ele é definido?
  **R:** K fichas, configurável em `[decisions]` no `harness.toml`, com default 10.
- **Q:** D3 — Onde documentar a consulta sob demanda para os agentes?
  **R:** No próprio bloco injetado (cabeçalho de orientação) e, complementarmente, um trecho curto gravado no `CLAUDE.md` do projeto **na instalação** (`harness init`), à maneira do Reversa: escrita única, idempotente em re-execução, sem gestão contínua de merge/upgrade. Nenhuma classe de artefato gerenciado continuamente é criada.

## 10. Lacunas

- Nenhuma lacuna pendente: as três dúvidas da versão inicial foram resolvidas na sessão de esclarecimentos de 2026-08-11.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-08-11 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-08-11 | Dúvidas D1-D3 resolvidas por `/reversa-clarify`; RN-04, RF-01/RF-04/RF-05, RNF e cenários atualizados | reversa |
