# Progress (Medidor de Entregáveis + Exportador Kanban) — Design Técnico

> Gerado pelo Writer em 2026-08-11 (Reconciliação das features 026-027)
> Foca no COMO a unit é construída, a partir do código legado lido. Escala: 🟢 / 🟡 / 🔴

## Interface

| Símbolo                        | Assinatura                          | Retorno                          | Observação                                                                                     |
| ------------------------------ | ----------------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------- |
| `ProgressService.measure`      | `(repo_path: str, config)`          | `Medicao`                        | Leitura pura (tripwire `fs.writes == []`); ordena alertas por (severidade, origem, mensagem).   |
| `stages.detectar_estagio`      | `(fs, feature_dir: str)`            | `str`                            | Estágio físico por artefatos (mesma tabela do skill `reversa-requirements`).                    |
| `stages.contar_checkboxes`     | `(actions_md: str)`                 | `(feitas, total)`                | Só linhas de tabela terminadas em `\| [ ] \|` / `\| [X] \|` (`_CHECKBOX_ROW`).                  |
| `stages.listar_acoes`          | `(actions_md: str)`                 | `[(id, descricao, fase, feita)]` | Mesmo critério de linha do `contar_checkboxes` (paridade em ponto único).                       |
| `stages.contar_por_fase`       | `(actions_md: str)`                 | `[(fase, feitas, total)]`        | Fases pelas headings `##`.                                                                      |
| `render.render_markdown`       | `(medicao)`                         | `str`                            | Sem timestamp, sem caminho absoluto; commits abreviados.                                        |
| `render.render_json`           | `(medicao, aferido_em: str)`        | `str`                            | Único lugar com carimbo de hora; stdout, não versionado.                                        |
| `kanban.extrair_manuais`       | `(board_json: str)`                 | manuais por coluna               | JSON inválido → exceção (a borda converte em exit 2 sem escrita).                               |
| `kanban.render_board`          | `(medicao, board_atual)`            | `str` (JSON do board)            | Recomputa só `category == "harness"`; manuais preservados byte a byte; determinístico.          |

**Modelos transitórios (Pydantic, jamais persistidos):** `Medicao` (raiz: `forward_disponivel`, `ativa`, `pausadas`, `concluidas`, `outras_incompletas`, `harness`, `board_habilitado` ✨f027, `demandas` ✨f027, `alertas`, `avisos`, `falhas`), `FeatureProgresso` (com `FasesProgresso` e `acoes: List[AcaoProgresso]` ✨f027), `AcaoProgresso` (IDs reais `T00N`), `Demanda` ✨f027, `Alerta` (`severidade` alta/média, `origem`, `mensagem`), `HarnessMedicao` (`sessao_status`, `ancora`, `fichas_total`, `ultima_ficha`, `gate_pendente`, `gate_mudancas`).

## Fluxo Principal

1. **`measure(repo_path, config)`:** `_medir_forward` (varre `_reversa_forward/` resolvendo o folder por `.reversa/state.json`; feature ativa/pausadas via `active-requirements.json`; estágio físico por `stages.detectar_estagio`; declarado ≠ físico → alerta **alta**; marca literal `_MARCA_RECONCILIACAO` no regression-watch → alerta **média**) → `_medir_harness` (estado de sessão, fichas MD, gate reavaliado em leitura pura sem persistir fingerprint) → `_medir_demandas` (✨f027: só com `board_habilitado`, lê apenas os cards manuais fora de `done`) → ordena alertas. 🟢
2. **Borda, modo padrão (`main.py`):** `measure` → `render_markdown` → compara com o conteúdo atual de `config.progress.file` → regrava atomicamente **só se mudou**; com `[progress.kanban].enabled`, `render_board` → mesma política write-only-when-changed no `config.progress.kanban.file`. 🟢
3. **Borda, `--json`:** `render_json(medicao, aferido_em=now)` no stdout; nada gravado. 🟢
4. **Borda, `--em-hook`:** exit 1 **apenas** se o artefato em disco difere do recém-renderizado (defasado); alerta grave → aviso em stderr, exit 0 (D-03: sem exit 3, sem terceira política de bloqueio). 🟢
5. **`render_board(medicao, board_atual)` (✨f027):** extrai manuais do board atual; recomputa cards `harness` (ativa→in-progress com um card por ação `hns:<feature>:<T00N>`, pausadas→todo, alertas→todo bug prio 9/5, `[X]`→done); `creation_time` do primeiro `ts` do `progress.jsonl` (fallback `started-at`); funde com os manuais preservados nas quatro colunas `_COLUNAS`. 🟢

## Fluxos Alternativos

- **Projeto sem ciclo forward:** `forward_disponivel=False`, seções `n/a` — medição legítima, não erro. 🟢
- **Fonte ilegível:** entra em `Medicao.falhas`; a borda emite `Erro de leitura:` em stderr, exit 2, **sem regravar** nenhum artefato. 🟢
- **Board corrompido (JSON inválido):** `extrair_manuais` levanta; borda → exit 2, nenhuma escrita (manuais nunca são perdidos por sobrescrita cega). 🟢
- **Opt-in desligado:** nada sob `.vscode/` é lido nem criado; `demandas` fica vazia. 🟢
- **Gate com sessão ausente:** `gate_pendente=None` (`n/a`), sem avaliação. 🟢

## Dependências

- `core/decisions/gate.evaluate_registration_gate` — reavaliado em leitura pura (RN-N52).
- `core/domain/config.ProgressSection`/`ProgressKanbanSection` — caminhos e opt-in.
- `FileSystemPort` (leitura; escrita só na borda) e `GitPort` (âncora/sujos para o gate).
- `pydantic` — modelos transitórios; stdlib `json`/`re` — parse das fontes e do board.

## Decisões de Design Identificadas

| Decisão                                                                    | Evidência no código                                | Confiança               |
| --------------------------------------------------------------------------- | -------------------------------------------------- | ----------------------- |
| Medição pura no serviço; toda escrita e todo exit code na borda             | `service.py` × ramo `progress` do `main.py`        | 🟢 (ADR 0026 / MD-0019) |
| Artefato sem valor volátil; hora só no `--json`                             | `render.py` (`render_markdown` × `render_json`)    | 🟢 (ADR 0026)           |
| Alerta por sinal físico, sem ack                                            | `service.py` (`_MARCA_RECONCILIACAO`)              | 🟢 (RN-N52)             |
| Paridade com o skill num ponto único                                        | `stages.py` (`_CHECKBOX_ROW` compartilhado)        | 🟢 (RN-N52)             |
| Schema do fork confinado a um módulo                                        | `kanban.py` (único import do formato do board)     | 🟢 (ADR 0027 / MD-0020) |
| Posse por namespace `category == "harness"`; ids `hns:*` (ordinais rejeitados) | `kanban.py` (`_CATEGORIA_GERENCIADA`), DESCARTADO-e | 🟢 (ADR 0027)          |
| `creation_time` do jsonl, nunca `now()`                                     | `service.py` (`_criacao_por_acao`)                 | 🟢 (RN-N54)             |
| Duas projeções da mesma `Medicao` (markdown + board), sem retrabalho        | `render.py` + `kanban.py` sobre o mesmo modelo     | 🟢 (ADRs 0026/0027)     |

## Estado Interno

Nenhum. A `Medicao` vive só durante a execução; os dois artefatos derivados (`.harness/progresso.md` e o board) são projeções regravadas pela borda, versionadas no git do projeto. Não há cache, snapshot nem ack de alertas — o "estado" do medidor **é** o estado das fontes.

## Observabilidade

- `Erro de leitura:` em stderr (exit 2) para fonte ilegível; avisos de alerta grave em stderr no `--em-hook` (exit 0).
- O diff do artefato versionado é o sinal de mudança de estado (write-only-when-changed).
- `--json` para inspeção programática com carimbo `aferido_em`.

## Riscos e Lacunas

- 🟡 **Paridade `stages.py` ↔ prosa do skill é convenção vigiada por teste**, não derivação automática: mudar o skill `reversa-requirements` exige mudar o código junto (ADR 0026, Consequências).
- 🟡 **Conferência visual do board no fork pendente** do mantenedor (ids não numéricos, campos opcionais ausentes, efeito de mover card gerenciado na UI) — Observações do regression-watch da 027.
- 🟡 Nenhum hook dispara o medidor por padrão; a defasagem do artefato só é detectada quando alguém roda `--em-hook` ou o comando manual.
- 🟡 O board como canal de demandas é convenção operacional: nada automatiza a condução das `Medicao.demandas` pelo ciclo forward.
