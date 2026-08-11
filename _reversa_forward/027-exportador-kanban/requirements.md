# Requirements: Exportador kanban derivado da Medicao

> Identificador: `027-exportador-kanban`
> Data: `2026-08-11`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

A feature 026 entregou o medidor de progresso (`harness progress`), cuja `Medicao` já contém tudo que um quadro kanban precisa: features por estágio físico, ações por fase com checkboxes, pausadas, alertas. Esta feature acrescenta um TERCEIRO renderizador sobre a mesma `Medicao`: um exportador one-way para o formato do vscode-kanban (fork do mantenedor, interface recém-refatorada), gravando `.vscode/vscode-kanban.json` para visualização rica no editor. O exportador é config-gated (desligado por padrão) e nunca lê o board como fonte: o fluxo é sempre fontes → `Medicao` → board, preservando o invariante de artefato derivado da 026.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `.harness/harness-core/src/core/progress/service.py` (026; `_reversa_sdd/` ainda não descreve o componente, pendência registrada no regression-watch da 026) | `Medicao` com `ativa`/`pausadas`/`concluidas`/`alertas`, computada em leitura pura das quatro fontes | 🟢 |
| `.harness/harness-core/src/core/progress/render.py` (026) | Padrão de renderizador puro sobre a `Medicao` (markdown, JSON); o exportador kanban é o terceiro da série | 🟢 |
| `~/dev/vscode-kanban/.vscode/vscode-kanban.json` (fork do mantenedor, lido na fonte) | Board = objeto com colunas `todo`/`in-progress`/`testing`/`done`, cada uma array de cards `{id, title, type, prio, creation_time, description{content,mime}, details{content,mime}, category}` | 🟢 |
| `_reversa_sdd/domain.md#2.17` (RN-N36..N40) | Fonte única: código novo no core propaga à base instalada sem reinstalação | 🟢 |
| `.harness/decisoes/MD-0019.md`, DESCARTADO (f) | A integração kanban foi explicitamente adiada da 026 para cá, para não acoplar o core ao schema da extensão dentro daquela feature | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor intermitente (único usuário) | Retomar o projeto após semanas vendo o estado como quadro visual, não como texto | Abre o VS Code, o vscode-kanban carrega o board exportado e mostra as ações da feature ativa por coluna |
| O mesmo, durante uma sessão de coding | Acompanhar o avanço das ações sem sair do editor | Roda `harness progress`; o board regenerado reflete os checkboxes fechados desde a última medição |

## 4. Regras de negócio novas ou alteradas

1. **RN-01: Exportação one-way DENTRO do namespace gerenciado.** O exportador possui os cards de categoria gerenciada (`harness`): esses ele cria, atualiza e remove livremente, e editar um deles à mão não altera `actions.md` nem fonte alguma (a edição é sobrescrita na exportação seguinte). Cards FORA da categoria gerenciada são do mantenedor: o exportador os preserva byte a byte, em qualquer coluna, e jamais os remove ou reordena entre si. 🟢
   - Origem no legado: mesmo princípio do `progresso.md` (026, RN-04 daquele ciclo), restrito ao namespace após o esclarecimento D2
   - Tipo: nova
2. **RN-02: Config-gated, desligado por padrão.** Seção `[progress.kanban]` no `harness.toml` com `enabled = false` default. Projeto sem a seção herda o default sem migração; a base instalada não ganha `.vscode/vscode-kanban.json` sem opt-in explícito por projeto. 🟢
   - Tipo: nova
3. **RN-03: Determinismo do artefato.** Mesmo estado medido → mesmos bytes no board (ordenação estável de cards, ids estáveis derivados dos ids reais: `T001`, `026`, `W-...`). Campos voláteis do schema (`creation_time`) recebem valor determinístico derivado das fontes (ex.: primeiro `ts` da ação no `progress.jsonl`) ou valor fixo, nunca `now()`. 🟢
   - Origem no legado: RN-02 da 026 (sem timestamp de geração)
   - Tipo: nova
4. **RN-04: Acoplamento contido num módulo.** O conhecimento do schema do vscode-kanban vive num único renderizador (`render_kanban` ou módulo próprio); `Medicao`, serviço e demais renderizadores não ganham nenhum campo específico de kanban. Se o fork mudar o schema, muda um arquivo. 🟢
   - Tipo: nova
5. **RN-05: Escrita na borda, write-only-when-changed.** Como na 026: serviço puro, escrita no `main.py`, regravação apenas quando o conteúdo muda, escrita atômica. Falha real de medição (exit 2) não regrava o board. O board existente é lido apenas para os cards MANUAIS (preservação no merge, RN-01, e listagem de demandas, RN-06); cards do namespace gerenciado jamais são lidos como fonte de progresso. 🟢
   - Origem no legado: contrato da 026 (`interfaces/progress-cli.md`)
   - Tipo: nova
6. **RN-06: Board como canal de entrada de demandas.** Card manual (fora da categoria gerenciada) é uma DEMANDA do mantenedor: o medidor o reporta (contagem no `progresso.md` e na saída `--json`), tornando-o visível ao agente, que deve conduzi-lo pelo processo forward (`/reversa-requirements` em diante) em vez de implementá-lo por fora. O card manual permanece no board, intocado, até o próprio mantenedor movê-lo ou removê-lo; o exportador nunca o converte, conclui ou apaga por conta própria. 🟢
   - Origem: esclarecimento D2 (sessão 2026-08-11)
   - Tipo: nova
7. **RN-07: Board ilegível não derruba a exportação silenciosamente.** Se `.vscode/vscode-kanban.json` existir mas for JSON inválido, o exportador NÃO regrava (preservaria dados manuais corrompendo-os ou os perderia): reporta falha real, mesmo contrato do exit 2 da 026. Board ausente é caso normal de primeira exportação. 🟢
   - Origem no legado: RN-N43 aplicada (falha real vs ausência legítima)
   - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Renderizador kanban puro sobre a `Medicao`, produzindo JSON válido no schema do fork (colunas `todo`/`in-progress`/`testing`/`done`) | Must | O arquivo gerado abre no vscode-kanban do fork sem erro e sem card malformado | 🟢 |
| RF-02 | Granularidade dupla (D1): um card por ação da feature ativa, na coluna conforme o status do checkbox, MAIS um card-resumo por feature (ativa, pausadas, concluídas recentes) com contagem de ações no título | Must | Ação `[ ]` aparece em `todo`/`in-progress`, ação `[X]` em `done`; cada feature tem card-resumo; contagens batem com o `progresso.md` | 🟢 |
| RF-03 | Exportação acionada pelo próprio `harness progress` (modo padrão) quando `[progress.kanban].enabled = true`; sem flag nova obrigatória | Must | Com a seção habilitada, uma invocação regrava markdown E board; desabilitada, o board não é tocado | 🟢 |
| RF-04 | Alertas da `Medicao` viram cards visíveis (ex.: `type: "bug"`, `category: "alerta"`, prio por severidade) | Should | Alerta alta presente na medição aparece no board; some quando a causa some | 🟢 |
| RF-05 | Ids e ordenação estáveis entre exportações do mesmo estado (RN-03); cards manuais preservados byte a byte (RN-01) | Must | Duas exportações consecutivas sem mudança de estado → bytes idênticos, zero diff; card manual sobrevive a N exportações | 🟢 |
| RF-06 | Smoke real neste repositório com o fork instalado | Should | Board deste projeto renderiza no editor com as features 026/027 e a pausada 024 | 🟡 |
| RF-07 | Demandas manuais visíveis na medição (RN-06): o `progresso.md` e o `--json` reportam contagem e títulos dos cards manuais em colunas não-`done` | Must | Card manual criado no board aparece na próxima medição como demanda de entrada; some do relatório quando movido para `done` ou removido pelo mantenedor | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Manutenibilidade | Schema do fork isolado num módulo; zero campo kanban fora dele (RN-04) | Fork é projeto pessoal e pode mudar; acoplamento contido é o preço aceitável do recurso | 🟢 |
| Reprodutibilidade | Board determinístico, diff só quando o estado muda (RN-03) | Mesmo princípio que provou valor no `progresso.md` | 🟢 |
| Segurança | O exportador escreve APENAS o JSON do board; nunca cria/toca `.vscode/vscode-kanban.js` (vetor de execução apontado nos achados de segurança do próprio fork) | Cards de segurança do board do fork (`workspaces.ts:769`, execução de script do workspace) | 🟢 |
| Observabilidade | stdout informa `board regravado`/`em dia` como o markdown; avisos em stderr | Padrão da 026 | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: exportação habilitada acompanha a medição
  Dado um projeto com [progress.kanban].enabled = true e ciclo forward ativo
  Quando o mantenedor roda `harness progress`
  Então `.harness/progresso.md` e o board kanban são regravados se o estado mudou
  E as colunas do board refletem os checkboxes do actions.md da feature ativa

Cenário: opt-out é o default
  Dado um projeto migrado à fonte única SEM a seção [progress.kanban]
  Quando o mantenedor roda `harness progress`
  Então nenhum arquivo `.vscode/vscode-kanban.json` é criado ou modificado

Cenário: determinismo
  Dado um board recém-exportado e nenhuma mudança nas fontes
  Quando `harness progress` roda de novo
  Então o board permanece byte-idêntico e o stdout informa que estava em dia

Cenário negativo: falha real de leitura não degrada o board
  Dado um `active-requirements.json` corrompido
  Quando `harness progress` roda
  Então sai com código 2 e o board existente permanece intocado

Cenário: card manual sobrevive e vira demanda visível
  Dado um board exportado e um card criado à mão pelo mantenedor na coluna todo
  Quando `harness progress` roda de novo
  Então o card manual permanece byte-idêntico no board
  E o progresso.md reporta a demanda de entrada com o título do card

Cenário negativo: board corrompido não é sobrescrito
  Dado um `.vscode/vscode-kanban.json` com JSON inválido
  Quando `harness progress` roda com o exportador habilitado
  Então a exportação reporta falha real e o arquivo não é regravado
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-02, RF-03, RF-05 | Must | Sem renderizador válido, mapeamento correto, gate de config e determinismo não há feature |
| RF-07 (demandas manuais visíveis) | Must | É o que transforma a preservação de cards (D2) em canal de entrada, motivação declarada do mantenedor |
| RF-04 (alertas como cards) | Should | Valor alto, mas o board já é útil só com as ações |
| RF-06 (smoke com o fork) | Should | Única validação de compatibilidade real com a interface refatorada |
| Coluna `testing` com semântica própria | Won't (por ora) | O ciclo forward não tem estágio físico intermediário entre `[ ]` e `[X]`; inventar um seria estado não derivado |

## 9. Esclarecimentos

### Sessão 2026-08-11

- **Q:** D1 — Qual a granularidade dos cards no board exportado?
  **R:** Ações + features: um card por ação da feature ativa (coluna pelo status do checkbox) e um card-resumo por feature (pausadas e concluídas recentes). Incorporado ao RF-02.
- **Q:** D2 — O exportador gerencia o board inteiro ou preserva cards manuais?
  **R:** Preservar cards manuais. Motivação declarada: o mantenedor quer apresentar novas demandas criando cards à mão, e o agente harness deverá executá-las pelo processo forward. O board ganha papel duplo: projeção derivada (namespace gerenciado) e canal de entrada de demandas (cards manuais). Incorporado às RN-01/RN-06/RN-07 e ao RF-07.
- **Q:** D3 — Onde o board vive e ele entra no git?
  **R:** `.vscode/vscode-kanban.json`, caminho configurável em `[progress.kanban].file`, versionado no git como o `progresso.md`. Incorporado ao RN-02 e aos critérios de aceite.

## 10. Lacunas

- Nenhuma lacuna aberta: as três dúvidas da versão inicial foram resolvidas na sessão de 2026-08-11.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-08-11 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-08-11 | Sessão de esclarecimentos (D1/D2/D3); board ganha papel de canal de entrada de demandas (RN-06, RN-07, RF-07) | reversa-clarify |
