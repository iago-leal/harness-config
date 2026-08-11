# Roadmap: Exportador kanban derivado da Medicao

> Identificador: `027-exportador-kanban`
> Data: `2026-08-11`
> Requirements: `_reversa_forward/027-exportador-kanban/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Quarto renderizador sobre a `Medicao` da 026, num módulo novo e único (`src/core/progress/kanban.py`) que concentra TODO o conhecimento do schema do fork vscode-kanban. O `ProgressService` ganha uma quinta fonte opcional, o próprio board, lida SOMENTE para os cards manuais (fora da categoria gerenciada `harness`): eles alimentam a lista `demandas` da `Medicao` (RF-07) e são preservados byte a byte no merge de escrita (RN-01). A exportação acopla-se ao modo padrão do `harness progress` quando `[progress.kanban].enabled = true` (default false): mesma borda, mesmo write-only-when-changed, mesma política de falha real (exit 2 sem regravar, agora também para board ilegível, RN-07). Cards gerenciados têm ids e ordenação determinísticos derivados dos ids reais (`T001`, `026`, watch); `creation_time` deriva das fontes (`progress.jsonl`, `started-at`), nunca de `now()`. O `progresso.md` ganha a seção de demandas manuais, fechando o papel duplo do board: projeção derivada para fora, canal de demandas para dentro.

## 2. Princípios aplicados

n/a — o projeto não possui `.reversa/principles.md`; valem os princípios globais do mantenedor (proporcionalidade: categoria **Aplicação**, rigor pleno; estabilidade; erros barulhentos), já refletidos nas decisões abaixo.

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Módulo único `src/core/progress/kanban.py` com função pura `render_board(medicao, board_atual: str \| None) -> str` e parser dos cards manuais | RN-04: schema do fork isolado num arquivo; função pura testável sem disco | Espalhar o mapeamento pelo `render.py`; subcomando separado `harness kanban` (duplicaria medição e borda) | 🟢 |
| D-02 | Namespace gerenciado = cards com `category: "harness"`; ids estáveis `hns:<feature>` (resumo), `hns:<feature>:<T00N>` (ação), `hns:alerta:<origem>` (alerta) | Critério de posse barato e visível no board; ids derivados dos ids reais garantem RF-05 | Prefixo no título (frágil, o usuário edita título); campo custom fora do schema (o fork pode rejeitar) | 🟢 |
| D-03 | Config aninhada `[progress.kanban]` → `ProgressKanbanSection(enabled: bool = False, file: str = ".vscode/vscode-kanban.json")` dentro de `ProgressSection` | RN-02 e D3 do clarify: opt-in por projeto, caminho configurável, herança sem migração | Flag de CLI (`--kanban`): exigiria lembrar a flag a cada invocação; seção top-level nova (fragmenta a config do medidor) | 🟢 |
| D-04 | O board é fonte SÓ para cards manuais: `ProgressService` lê o arquivo quando `enabled`, extrai cards com `category != "harness"` em colunas não-`done` para `Medicao.demandas`, e o conteúdo integral dos manuais segue para o merge de escrita; cards gerenciados do arquivo são descartados e recomputados | Fecha RN-01/RN-05/RN-06 sem circularidade: progresso nunca é lido do board | Ler o board inteiro como fonte (circular: o exportador leria o que escreveu); ignorar manuais na medição (mataria o RF-07, a motivação do D2) | 🟢 |
| D-05 | Mapeamento de colunas: ação `[ ]` → `todo`, ação `[X]` → `done` (só a feature ativa tem cards de ação); resumo da ativa → `in-progress`, resumos de pausadas → `todo`, resumos de concluídas recentes → `done`; alertas → `todo` com `type: "bug"` (prio 9 alta, 5 média); coluna `testing` nunca é usada pelo namespace gerenciado | O ciclo forward não tem estágio entre `[ ]` e `[X]` (Won't do requirements §8); semântica simples e derivável | Inferir `in-progress` de heurística (dependências satisfeitas): estado não derivado, adivinhação | 🟢 |
| D-06 | Determinismo do `creation_time`: ações usam o primeiro `ts` da ação no `progress.jsonl` (ausente → `started-at` da feature); resumos usam `started-at` do `active-requirements.json`; alertas usam o `started-at` da ativa; nenhum caminho chama `now()` | RN-03: mesmo estado → mesmos bytes; o campo existe no schema real e o fork o exibe | Omitir o campo (comportamento do fork ao faltar não verificado); epoch fixo (mentira visível na UI) | 🟡 |
| D-07 | Board presente mas JSON inválido → falha real: `Erro de leitura:` + exit 2, sem regravar NENHUM artefato (nem markdown nem board) | RN-07 e contrato da 026: nunca sobrescrever dado bom (aqui, possivelmente cards manuais) com medição degradada | Regravar só o markdown (deixaria os artefatos dessincronizados); recriar o board do zero (perderia demandas manuais) | 🟢 |
| D-08 | `progresso.md` ganha seção `## Demandas do board` (título + coluna de cada card manual não-`done`; `- nenhuma` quando vazio); `--json` expõe `demandas` | RF-07: é o que torna a demanda visível ao agente na retomada de sessão | Seção só no board (o agente lê markdown/JSON, não o board); alerta por demanda (demanda não é anomalia, é fila de trabalho) | 🟢 |
| D-09 | Escrita do board na borda (`main.py`), atômica, write-only-when-changed, com `makedirs` do `.vscode/` se preciso; stdout ganha linha própria (`<file> regravado.` / `já estava em dia.`) por artefato | Padrão da 026; dois artefatos derivados, mesmo contrato | Escrever no serviço (violaria a pureza testada por `fs.writes == []`) | 🟢 |
| D-10 | Bump minor 2.4.0 → 2.5.0 e ficha MD-0020 ao final | Comando ganha capacidade nova visível; fluxo padrão de versão canônica (RN-N40) | — | 🟢 |
| D-11 | O exportador jamais cria ou toca `.vscode/vscode-kanban.js` nem qualquer arquivo além do board configurado | RNF de segurança: o `.js` é vetor de execução apontado nos achados do próprio fork | — | 🟢 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| O fork aceita board com as quatro chaves de coluna e cards contendo `id`/`title`/`type`/`prio`/`creation_time`/`description`/`details`/`category` como no arquivo real lido em `~/dev/vscode-kanban/.vscode/vscode-kanban.json` | §2 (fonte 🟢 lida na fonte) | Baixo: o smoke RF-06 pega incompatibilidade antes de concluir |
| 🟡 O fork tolera cards SEM campos opcionais (`references`, `assignedTo` etc.) | §5 RF-01 | Card renderiza estranho no editor; correção barata no módulo único (D-01) |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Serviço de medição (`core/progress/service.py`, 026; ainda sem seção no `_reversa_sdd/`) | pendência de reconciliação da 026 | regra-alterada | Quinta fonte opcional (board, só cards manuais) e campo `demandas` na `Medicao` |
| Renderizadores (`core/progress/render.py`) | idem | regra-alterada | `render_markdown` ganha `## Demandas do board`; JSON expõe `demandas` |
| Exportador kanban (`core/progress/kanban.py`) | — | componente-novo | Parser de manuais + `render_board` determinístico com merge de preservação |
| Configuração (`core/domain/config.py`) | `_reversa_sdd/architecture.md#config` | regra-alterada | `ProgressKanbanSection` aninhada; bump 2.5.0 |
| Borda CLI (`src/main.py`, ramo `progress`) | `_reversa_sdd/architecture.md#main` | contrato-alterado | Segundo artefato derivado no modo padrão; falha real cobre board ilegível |

## 6. Delta no modelo de dados

- Resumo das mudanças: `Medicao` ganha `demandas: List[Demanda]` (`titulo`, `coluna`, `card_id`); config ganha `ProgressKanbanSection`. Nenhum dado persistido pelo harness muda de schema; o board é artefato derivado com ilha de dados manuais preservada.
- Detalhe completo em: `_reversa_forward/027-exportador-kanban/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Board do vscode-kanban (`.vscode/vscode-kanban.json`) | arquivo | `_reversa_forward/027-exportador-kanban/interfaces/kanban-board.md` |

## 8. Plano de migração

n/a — seção nova de config com default desligado; nenhum projeto instalado muda de comportamento sem opt-in.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Fork muda o schema do board (projeto pessoal em refatoração ativa) | médio | médio | RN-04/D-01: schema num módulo único; watch item na 027 |
| Usuário edita card GERENCIADO esperando persistir | baixo | alto | Descrição do card avisa que é derivado; RN-01 documentada no onboarding |
| Merge preserva card manual corrompido a ponto de invalidar o JSON | médio | baixo | D-07: board ilegível → exit 2 sem regravar; escrita atômica |
| `creation_time` derivado divergir entre máquinas (progress.jsonl não versionado?) | baixo | baixo | `progress.jsonl` é versionado no repo; fallback determinístico para `started-at` |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Suíte completa verde + ruff nos arquivos tocados
- [ ] Smoke real neste repo: board gerado, aberto no fork, card manual sobrevive a re-exportação e aparece como demanda
- [ ] `legacy-impact.md` e `regression-watch.md` gerados
- [ ] Ficha MD-0020 registrada e índice recompilado; bump 2.5.0
