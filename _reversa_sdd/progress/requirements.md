# Progress (Medidor de Entregáveis + Exportador Kanban) — Requisitos (Requirements)

> Gerado pelo Writer em 2026-08-11 (Reconciliação das features 026-027; **nenhuma das duas commitada nesta data**)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`.harness/harness-core/src/core/progress/`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/core/progress/) — `service.py`, `stages.py`, `render.py`, `kanban.py`. Driver: `src/main.py` (subcomando `progress`, 13º da CLI, ramos padrão/`--json`/`--em-hook`). Configuração: `ProgressSection`/`ProgressKanbanSection` em `core/domain/config.py`. ADRs 0026/0027; MD-0019/MD-0020; `domain.md` §2.24-2.25 (RN-N50..N55).

## Visão Geral

Esta unit responde "**quanto falta**", complementando o "o quê" (sessão) e o "por quê" (microdecisões). A `ProgressService.measure()` agrega cinco fontes de verdade num modelo transitório `Medicao`, **em leitura pura**, e a borda projeta a medição em até dois artefatos derivados: o markdown `.harness/progresso.md` (sempre) e o board do fork do vscode-kanban (`.vscode/vscode-kanban.json`, opt-in). Reproduz o padrão do `make estado` de `comentarios-concursos`: termômetro read-only, sem estado próprio, cujo artefato versionado só gera diff quando o estado muda.

## Responsabilidades

- Medir o ciclo forward por artefatos físicos (estágio de cada feature, checkboxes do `actions.md` por fase, pausadas, concluídas) e pelo `active-requirements.json`. 🟢
- Derivar alertas de sinais físicos: a marca literal "pendência de reconciliação" no regression-watch (média) e divergência entre estágio declarado e físico (alta); reavaliar o gate de microdecisões **sem persistir fingerprint**. 🟢
- Renderizar markdown sem valor volátil (sem timestamp, sem caminho absoluto) e JSON com `aferido_em`; regravar o artefato atomicamente e só quando mudou. 🟢
- Exportar o board kanban com posse por namespace: cards `category == "harness"` recomputados do zero; cards manuais preservados byte a byte e, fora de `done`, expostos como `Medicao.demandas` (canal de entrada de demandas). 🟢

## Regras de Negócio

- **RN-N50 — Medição é derivação pura, sem estado próprio:** `ProgressService.measure()` não escreve nada (invariante pinada por teste `fs.writes == []`); a `Medicao` é transitória e jamais persistida. Fonte ausente é `n/a` legítimo; fonte ilegível é falha real (vai para `Medicao.falhas`). Divergência entre medidas é **achado** (alerta), nunca corrigida silenciosamente. 🟢
- **RN-N51 — Artefato derivado sem valor volátil; contrato de exit codes na borda:** o markdown não carrega timestamp nem caminho absoluto (diff só quando o estado muda); `--json` pode carimbar `aferido_em` (stdout, não versionado). Na borda: fonte ilegível → `Erro de leitura:` em stderr, exit 2, **nenhum artefato regravado**; `--em-hook` sai 1 apenas por artefato defasado (alerta grave vira aviso em stderr, nunca bloqueia — o exit 3 do medidor original não foi transplantado, D-03). 🟢
- **RN-N52 — Alerta persistente por sinal físico; paridade com o skill em ponto único:** alerta existe enquanto o sinal físico existir, sem mecanismo de ack (a marca `_MARCA_RECONCILIACAO` no regression-watch é o exemplo canônico). `stages.py` é o ponto único que codifica a tabela de estágio físico e a contagem de checkboxes que o skill `reversa-requirements` descreve em prosa; o gate é reavaliado em leitura pura, sem persistir fingerprint. 🟢
- **RN-N53 — Posse por namespace; manuais são ilha intocável e canal de demandas (027):** card `category == "harness"` pertence ao exportador (recomputado do zero, ids `hns:<feature>`, `hns:<feature>:<T00N>`, `hns:alerta:<origem>`); qualquer outro card é manual, preservado byte a byte na coluna onde estiver; manuais fora de `done` viram `Medicao.demandas`. Mapeamento fixo: `[ ]`→todo, `[X]`→done, ativa→in-progress, pausadas→todo, alertas→todo (bug, prio 9/5); `testing` nunca recebe card gerenciado; concluídas não geram card. 🟢
- **RN-N54 — Board 100% determinístico (027):** nenhum caminho consulta a hora corrente; `creation_time` deriva do primeiro `ts` da ação no `progress.jsonl`, com fallback no `started-at`. Mesmo estado + mesmos manuais → bytes idênticos (idempotência pinada por teste). 🟢
- **RN-N55 — Fluxo unidirecional e segurança do arquivo executável do fork (027):** a fonte de verdade é o `actions.md`; edição manual em card gerenciado é descartada na exportação seguinte. Board lido só com `[progress.kanban] enabled = true` e só pelos manuais; escrito só no modo padrão; board ilegível → exit 2 sem escrita. O exportador **jamais** cria ou toca `.vscode/vscode-kanban.js` (o fork o executa, `workspaces.ts:769`). 🟢

## Requisitos Funcionais

| ID    | Requisito                              | Prioridade | Critério de Aceite                                                                                                            |
| ----- | -------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------ |
| RF-01 | Medição pura das cinco fontes.         | Must       | `measure()` devolve `Medicao` completa com `fs.writes == []`; fontes ausentes viram `n/a`, ilegíveis viram `falhas`.          |
| RF-02 | Markdown sem valor volátil.            | Must       | `render_markdown` não emite timestamp nem caminho absoluto; regravação atômica e write-only-when-changed.                     |
| RF-03 | Alerta de pendência de reconciliação.  | Must       | Regression-watch com a marca literal gera alerta média que persiste até a marca sumir; sem ack.                               |
| RF-04 | Contrato de exit codes.                | Must       | Fonte ilegível → `Erro de leitura:` stderr + exit 2 sem regravar; `--em-hook` exit 1 só por artefato defasado; alerta grave → aviso stderr, exit 0. |
| RF-05 | JSON com carimbo.                      | Should     | `--json` emite a medição no stdout com `aferido_em`; nada é gravado em disco.                                                 |
| RF-06 | Board com posse por namespace (027).   | Must       | `render_board` recomputa só os cards `harness`; manuais preservados byte a byte; manuais fora de `done` em `Medicao.demandas`. |
| RF-07 | Determinismo do board (027).           | Must       | Duas exportações do mesmo estado produzem bytes idênticos; `creation_time` nunca vem de `now()`.                              |
| RF-08 | Opt-in e segurança (027).              | Must       | Sem `[progress.kanban] enabled = true`, nada sob `.vscode/` é lido ou criado; `vscode-kanban.js` jamais é tocado; board corrompido → exit 2 sem escrita. |

## Requisitos Não Funcionais

| Tipo             | Requisito inferido                                                     | Evidência no código                             | Confiança |
| ---------------- | ---------------------------------------------------------------------- | ----------------------------------------------- | --------- |
| Pureza           | Medição sem efeito colateral (teste-tripwire `fs.writes == []`).       | `service.py` + teste da invariante              | 🟢        |
| Determinismo     | Artefatos byte-reprodutíveis; diff = sinal, não ruído.                 | `render.py`, `kanban.py` (idempotência pinada)  | 🟢        |
| Robustez         | Falha de leitura barulhenta (exit 2) sem corromper artefatos.          | `main.py` (ramo `progress`)                     | 🟢        |
| Segurança        | Impossível criar o arquivo executável do fork.                         | `kanban.py` (escreve só o `.json` configurado)  | 🟢        |
| Manutenibilidade | Schema do fork confinado a um módulo; paridade com o skill em `stages.py`. | `kanban.py`, `stages.py`                    | 🟢        |

## Critérios de Aceitação

```gherkin
Dado um projeto com ciclo forward e regression-watch contendo "pendência de reconciliação"
Quando executo `./harness progress`
Então o .harness/progresso.md é regravado com alerta média por pendência, sem timestamp no corpo.

Dado que nada mudou nas fontes desde a última medição
Quando executo `./harness progress` de novo
Então o artefato não é regravado (bytes idênticos, sem diff no git).

Dado um actions.md ilegível (fonte corrompida)
Quando executo `./harness progress`
Então stderr recebe "Erro de leitura:", o exit code é 2 e nenhum artefato é regravado.

Dado [progress.kanban] enabled = true e um board com cards manuais
Quando executo `./harness progress`
Então os cards harness são recomputados, os manuais permanecem byte a byte e os manuais fora de done aparecem como demandas na medição.

Dado o mesmo estado das fontes e o mesmo board
Quando exporto o board duas vezes
Então os dois arquivos são byte-idênticos (nenhum caminho consulta a hora corrente).
```

## Prioridade (MoSCoW)

| Requisito                                | MoSCoW | Justificativa                                                          |
| ---------------------------------------- | ------ | ---------------------------------------------------------------------- |
| Medição pura (RN-N50)                    | Must   | Sem ela o medidor vira fonte de estado e o padrão inteiro desmorona.   |
| Artefato sem valor volátil (RN-N51)      | Must   | O diff do artefato versionado é o sinal; timestamp o poluiria.         |
| Posse por namespace (RN-N53)             | Must   | Um bug aqui sobrescreve cards manuais do mantenedor (canal de demandas). |
| Segurança do `.js` do fork (RN-N55)      | Must   | O fork executa o arquivo; criá-lo por engano é risco concreto.         |
| Board determinístico (RN-N54)            | Must   | Idempotência é o contrato que torna o board versionável.               |
| JSON com `aferido_em` (RF-05)            | Should | Conveniência de inspeção; não versionado.                              |

## Rastreabilidade de Código

| Arquivo                       | Função / Classe                                                                                          | Cobertura |
| ----------------------------- | --------------------------------------------------------------------------------------------------------- | --------- |
| `core/progress/service.py`    | `ProgressService.measure`, `_medir_forward`, `_medir_harness`, `_medir_demandas`, `Medicao`, `FeatureProgresso`, `AcaoProgresso`, `Demanda`, `Alerta`, `HarnessMedicao`, `_MARCA_RECONCILIACAO` | 🟢        |
| `core/progress/stages.py`     | `detectar_estagio`, `contar_checkboxes`, `listar_acoes`, `contar_por_fase` (paridade com o skill)         | 🟢        |
| `core/progress/render.py`     | `render_markdown` (sem valor volátil), `render_json` (com `aferido_em`)                                   | 🟢        |
| `core/progress/kanban.py`     | `extrair_manuais`, `render_board` (único módulo que conhece o schema do fork)                             | 🟢        |
| `core/domain/config.py`       | `ProgressSection` (`[progress].file`, default `.harness/progresso.md`) ✨f026; `ProgressKanbanSection` (`enabled=False`, `file=".vscode/vscode-kanban.json"`) ✨f027 | 🟢        |
| `src/main.py`                 | Subcomando `progress` (13º; ramos padrão/`--json`/`--em-hook`, mutuamente exclusivos; contrato de exit codes; board só no modo padrão) | 🟢        |
| `tests/`                      | TDD das duas features (20 testes novos na 027; suíte 372 verde), incl. tripwire `fs.writes == []` e idempotência do board | 🟢        |
