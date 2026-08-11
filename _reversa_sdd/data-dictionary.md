# Dicionário de Dados — harness-core

> Regenerado pelo Archaeologist em 2026-06-24 (re-extração pós-feature 008-reprodutibilidade-e-config).
> Nível de documentação: **completo**. Fonte: `.harness/harness-core/src/core/domain/{models.py,config.py,cache.py}` e os serviços que consomem/persistem essas estruturas.
> **Reconciliação de 2026-07-05** (pós-features 010-021): novo campo `[session].inject_decisions_index` (§6, feature 021); novo agregado de valor `EndSessionOffers`/`PushOffer`/`UpgradeOffer` (§8, feature 014, `session/offers.py` — dataclasses, não Pydantic, exceção deliberada pois são apenas DTOs de decisão da borda); `.harness/decisoes/` cresceu de 5 para 12 fichas (§4).
> **Reconciliação de 2026-07-15** (pós-MD-0014 e features 022-023): `SessionState` ganhou os campos anti-loop `gate_lembrete_fingerprint`/`gate_encerramento_fingerprint` (§1); `[decisions]` ganhou `require_registration` (§6); novo value-object não persistido `GateVerdict` (§9, `decisions/gate.py`); fichas de 12 para 16 (§4).

Estruturas de dados e modelos de domínio do harness-core. Todos os modelos são Pydantic v2.

---

## 1. `SessionState` — estado de sessão do agente 🟢

**Modelo:** `src/core/domain/models.py:SessionState`.
**Persistência:** arquivo Markdown `.harness/estado-da-sessao.md`. Esse caminho é lido de `[session].state_file` no `harness.toml` (default idêntico), tanto na CLI quanto no MCP. Formato = front-matter YAML (header-máquina) + corpo Markdown (a narrativa). Round-trip por `session/serializer.py`.

| Campo (modelo)   | Chave no front-matter | Tipo               | Obrigatório | Validação / Default                                 | Exemplo                     |
| ---------------- | --------------------- | ------------------ | ----------- | --------------------------------------------------- | --------------------------- |
| `commit_hash`    | `commit`              | str                | sim         | regex `^[a-f0-9]{40}$` (SHA1)                       | `c548223…` (40 hex)         |
| `active_feature` | `feature`             | str                | sim         | —                                                   | `005-decisoes-em-harness`   |
| `start_time`     | `start_time`          | datetime           | sim         | default `datetime.now(utc)`; coerção ISO, naive→UTC | `2026-06-24T00:02:09+00:00` |
| `is_active`      | `status`              | bool               | sim         | `status=="active"`→True; senão False                | `active` / `inactive`       |
| `narrative`      | corpo `##`            | `SessionNarrative` | não         | default vazio                                       | (ver §2)                    |
| `gate_lembrete_fingerprint` (022) | `gate_lembrete_fingerprint` | str? | não | default `None`; gravado só quando preenchido | sha1 hex (identidade grossa) |
| `gate_encerramento_fingerprint` (022) | `gate_encerramento_fingerprint` | str? | não | default `None`; gravado só quando preenchido | sha1 hex (identidade fina) |

Campos obrigatórios no front-matter (`serializer._REQUIRED_META`): `commit`, `feature`, `start_time`, `status`. Ausência de qualquer um → `MalformedSessionStateError`.

Métodos de domínio: `start_session(feature, commit)`, `close_session(commit)`, `update_active_feature(feature)` (levanta `ValueError` se sessão inativa).

> 🟢 **Campos anti-loop do gate (022/023):** guardam o último estado de pendência já **lembrado** no Stop (`gate_lembrete_fingerprint`, identidade grossa = `sha1(âncora)`) e já **bloqueado** no encerramento (`gate_encerramento_fingerprint`, identidade fina = `sha1(âncora+HEAD+sujos)`) — o mesmo estado nunca dispara o gate duas vezes. Opcionais e omitidos quando vazios: estados pré-022 permanecem parseáveis e o arquivo fica byte-compatível com o formato anterior enquanto o gate não for acionado. `close_session` os **zera** (não vazam para a próxima sessão). O estado de sessão persiste esses campos por ser a exceção consagrada do pré-check de pendência.

---

## 2. `SessionNarrative` — narrativa de retomada (value-object) 🟢

**Modelo:** `src/core/domain/models.py:SessionNarrative`. Aninhado em `SessionState.narrative`.
**Persistência:** seções `##` no corpo de `.harness/estado-da-sessao.md`.

| Campo             | Seção no corpo Markdown     | Tipo      | Obrigatório | Default |
| ----------------- | --------------------------- | --------- | ----------- | ------- |
| `feito`           | `## O que foi feito`        | List[str] | não         | `[]`    |
| `proximos_passos` | `## Próximos passos`        | List[str] | não         | `[]`    |
| `pendencias`      | `## Pendências / bloqueios` | List[str] | não         | `[]`    |
| `ponteiros`       | `## Ponteiros`              | List[str] | não         | `[]`    |

Cada item da lista corresponde a uma linha `- <item>` sob a seção. Helper `is_empty()` → True se as 4 listas vazias.

---

## 3. `SyncCache` — cache de sincronia Git 🟢

**Modelo:** `src/core/domain/cache.py:SyncCache`.
**Persistência:** JSON em `cache_filepath` — caminho canônico único `.harness/sync-cache.json` (`layout.py:SYNC_CACHE_REL_PATH`, consumido por CLI, close_flow e MCP desde o saneamento do T7, MD-0013). Evita chamadas `ls-remote` redundantes dentro do TTL.

| Campo               | Tipo     | Obrigatório | Validação                                  | Exemplo                     |
| ------------------- | -------- | ----------- | ------------------------------------------ | --------------------------- |
| `last_checked_time` | datetime | sim         | —                                          | `2026-06-24T00:02:09+00:00` |
| `commit_hash`       | str      | sim         | `constr(pattern=r"^[a-f0-9]{40}$")` (SHA1) | `c548223…` (40 hex)         |

---

## 4. `Decision` — microdecisão (ficha do grafo) 🟢

**Modelo:** `src/core/domain/models.py:Decision`. Mapeia o front-matter YAML de cada `MD-*.md`.
**Persistência:** fichas em `.harness/decisoes/MD-0001..MD-0016.md` (12 → 16 na reconciliação de 2026-07-15). Caminho lido de `[decisions].dir` no `harness.toml`.

| Campo (modelo)  | Chave no front-matter | Tipo                 | Obrigatório | Validação / Default                    |
| --------------- | --------------------- | -------------------- | ----------- | -------------------------------------- |
| `id`            | `id`                  | str                  | sim         | regex `^MD-\d{4}$`                     |
| `gancho`        | `gancho`              | str                  | sim         | —                                      |
| `status`        | `estado`              | str                  | não         | default `ativo` (`ativo`/`descartado`) |
| `relationships` | `relacoes`            | List[`Relationship`] | não         | `[]` (cada item = `"<verbo> MD-XXXX"`) |
| `filepath`      | — (runtime)           | str?                 | não         | preenchido no load                     |
| `raw_content`   | — (runtime)           | str?                 | não         | Markdown integral, para validação      |

**Integridade de conteúdo** (`Decision.validate_integrity`): exige H1 `# MD-XXXX` e as 4 seções obrigatórias no corpo, casadas por regex case-insensitive:

| Seção        | Padrão exigido      |
| ------------ | ------------------- |
| `D`          | `- **D:**`          |
| `PORQUÊ`     | `- **PORQUÊ:**`     |
| `DESCARTADO` | `- **DESCARTADO:**` |
| `ESTADO`     | `- **ESTADO:**`     |

---

## 5. `Relationship` — aresta do grafo de decisões 🟢

**Modelo:** `src/core/domain/models.py:Relationship`. Aninhado em `Decision.relationships`.

| Campo       | Tipo | Obrigatório | Validação                                                                                       |
| ----------- | ---- | ----------- | ----------------------------------------------------------------------------------------------- |
| `rel_type`  | str  | sim         | ∈ {`depende-de`, `substitui`, `refina`, `relaciona`, `estende`, `bloqueia`} (normalizado lower) |
| `target_id` | str  | sim         | regex `^MD-\d{4}$`                                                                              |

---

## 6. `HarnessConfig` — configuração tipada 🟢 (novos campos de upstream/version na feature 007)

**Modelo:** `src/core/domain/config.py`. Carregado de `harness.toml` por `load_config(fs)`.

| Seção          | Campo                                           | Tipo                                     | Default                           |
| -------------- | ----------------------------------------------- | ---------------------------------------- | --------------------------------- |
| `[harness]`    | `active_harness`                                | Literal[`claude`,`gemini`,`antigravity`] | `claude`                          |
| `[harness]`    | `upstream_path`                                 | str? (novo 🟢)                           | `None`                            |
| `[harness]`    | `version`                                       | str? (novo 🟢)                           | `None`                            |
| `[formatting]` | `exclude_paths`                                 | List[str]                                | `[]`                              |
| `[formatting]` | `opt_out_file`                                  | str                                      | `.no-autoformat`                  |
| `[sync]`       | `cache_ttl_hours`                               | int                                      | `24`                              |
| `[sync]`       | `remote_check_enabled`                          | bool                                     | `True`                            |
| `[decisions]`  | `dir`                                           | str                                      | `.harness/decisoes`               |
| `[decisions]`  | `index_file`                                    | str                                      | `.harness/microdecisoes.md`       |
| `[decisions]`  | `header_file`                                   | str                                      | `.harness/decisoes/_cabecalho.md` |
| `[decisions]`  | `require_registration` (novo 🟢, feature 022)   | bool                                     | `True`                            |
| `[decisions]`  | `compact_file` (novo 🟢, feature 028)           | str                                      | `.harness/decisoes-recentes.md`   |
| `[decisions]`  | `compact_index_size` (novo 🟢, feature 028)     | int (`ge=0`)                             | `10`                              |
| `[session]`    | `state_file`                                    | str                                      | `.harness/estado-da-sessao.md`    |
| `[session]`    | `inject_decisions_index` (novo 🟢, feature 021) | bool                                     | `True`                            |

> 🟢 **`upstream_path`** e **`version`** foram adicionados na feature 007 à seção `[harness]` para permitir que instalações físicas locais em repositórios de destino retenham metadados que conectam a cópia ao seu core upstream original e acompanhem as atualizações físicas.
> 🟢 **`inject_decisions_index`** (feature 021): opt-out do apêndice do índice de decisões anexado ao `cmd resume` — só tem efeito quando `active_harness == "claude"` (gate por harness fixado no código, não configurável). Retrocompatível: harness.toml sem a chave assume `True`.
> 🟢 **`require_registration`** (feature 022): liga o gate de registro de microdecisões (bloqueio no `encerrar-sessao`, lembrete no Stop do Claude, advisory no Antigravity). Habilitado por padrão; desativável por projeto; tomls sem o campo herdam `True`. A granularidade do lembrete (uma vez por sessão) é política fixa no core, sem flag (YAGNI, MD-0016).
> 🟢 **`compact_file`/`compact_index_size`** (feature 028, MD-0022): caminho da **visão compacta** de decisões (artefato derivado, mesma passada do índice) e quantas fichas recentes ela lista. `compact_index_size` valida `ge=0` (negativo → erro Pydantic barulhento); `0` degrada para cabeçalho + contagem + ponteiros, sem lista. Tomls sem os campos herdam os defaults.

---

## 7. `HARNESS_DOC_DATA` — payload injetado no HTML 🟢

Estrutura JSON compilada por `DocumentationService.generate_html` e injetada no `template.html`.

| Campo      | Tipo          | Origem                                                                    |
| ---------- | ------------- | ------------------------------------------------------------------------- |
| `commands` | Array[Object] | introspecção do argparse (`{name, help, arguments[]}`)                    |
| `rules`    | Array[Object] | regex sobre `_reversa_sdd/domain.md` (`{id, title, details, confidence}`) |
| `state`    | Object        | `.reversa/state.json` integral                                            |

---

## 8. `EndSessionOffers` / `PushOffer` / `UpgradeOffer` — ofertas de fim de sessão (feature 014, NOVO) 🟢

**Modelo:** `src/core/session/offers.py`. Exceção deliberada ao padrão Pydantic do restante do domínio: são **`@dataclass`** puros, não persistidos (vivem só durante a execução do `encerrar-sessao`, montados por `EndSessionOffersService.detect` e consumidos por `close_flow.conduct_end_session_offers`).

| Modelo             | Campo                | Tipo          | Obrigatório | Notas                                                    |
| ------------------ | -------------------- | ------------- | ----------- | -------------------------------------------------------- |
| `PushOffer`        | `branch`             | str           | sim         | branch corrente                                          |
| `PushOffer`        | `ahead`              | int           | sim         | commits à frente do remoto (`> 0` para a oferta existir) |
| `PushOffer`        | `is_default_branch`  | bool          | sim         | dispara texto de alerta extra na pergunta se `True`      |
| `PushOffer`        | `remote`             | str           | não         | default `"origin"`                                       |
| `UpgradeOffer`     | `current_version`    | str           | sim         | de `config.harness.version`                              |
| `UpgradeOffer`     | `target_version`     | str           | sim         | detectada via `SyncService.check_version_update_remote`  |
| `UpgradeOffer`     | `upstream_path`      | str           | sim         | de `config.harness.upstream_path`                        |
| `EndSessionOffers` | `push`               | PushOffer?    | não         | `None` = sem oferta cabível                              |
| `EndSessionOffers` | `upgrade`            | UpgradeOffer? | não         | `None` = sem oferta cabível                              |
| `EndSessionOffers` | `has_any` (property) | bool          | —           | `push is not None or upgrade is not None`                |

**Resiliência (RN-02/RN-03/RN-09):** `EndSessionOffersService._detect_push`/`_detect_upgrade` engolem qualquer exceção de git/rede e degradam para `None` — nunca levantam para a borda. Sem `upstream_path` configurado, `UpgradeOffer` nunca é montada (retorna `None` cedo).

---

## 9. `GateVerdict` — veredito do gate de registro (features 022/023, NOVO) 🟢

**Modelo:** `src/core/decisions/gate.py:GateVerdict` (Pydantic). **Não persistido** — vive só durante a avaliação; apenas os dois fingerprints sobrevivem, copiados para os campos anti-loop do `SessionState` (§1) pelas bordas que decidem interceptar.

| Campo                  | Tipo      | Obrigatório | Default | Notas                                                                     |
| ---------------------- | --------- | ----------- | ------- | ------------------------------------------------------------------------- |
| `pendente`             | bool      | sim         | —       | `bool(mudancas) and not fichas_tocadas`                                    |
| `mudancas`             | List[str] | não         | `[]`    | universo (diff da âncora ∪ sujos) menos exclusões e fichas                 |
| `fichas_tocadas`       | List[str] | não         | `[]`    | caminhos sob `decisions.dir` casando `^MD-.*\.md$`                         |
| `fingerprint`          | str       | não         | `""`    | identidade **fina**: `sha1(âncora+HEAD+sujos ordenados)` — portão          |
| `fingerprint_lembrete` | str       | não         | `""`    | identidade **grossa** (023): `sha1(âncora)` — lembrete do Stop             |
| `aviso`                | str?      | não         | `None`  | preenchido no fail-open (âncora ilegível etc.); a borda ecoa em stderr     |

---

## Mudanças vs extração anterior (feature 007)

- **`HarnessConfig`** (Consumo Ativo de Configurações): As chaves de formatação (`exclude_paths` e `opt_out_file`) do `HarnessConfig` agora são consumidas dinamicamente pelo `FormattingService`. O suporte à exclusão dinâmica inclui casamento de padrões glob (wildcards como `*` e `?`) via `fnmatch`.
- **Reprodutibilidade**: Gerenciamento de dependências unificado usando `uv` com compilação determinística do `requirements.txt` a partir de `requirements.in`. Pipeline de integração contínua (CI) adicionado sob `.github/workflows/ci.yml`.

## Mudanças vs extração anterior (features 010-021, reconciliação 2026-07-05)

- **`inject_decisions_index`** (021): novo campo booleano em `[session]`, default `True` — único ponto de configuração da feature de resume ancorado.
- **`EndSessionOffers`/`PushOffer`/`UpgradeOffer`** (014): agregado de valor novo, não coberto na extração anterior porque a feature 014 é posterior a ela; documentado agora por ainda estar em uso ativo (consumido por `close_flow.py`, ver code-analysis.md §8).
- **`Decision`**: mesma forma de dados, mas a população de fichas cresceu de 5 para 12 — sem mudança de schema, só de volume.
- Nenhuma mudança de schema em `SessionState`/`SessionNarrative`/`SyncCache`/`HARNESS_DOC_DATA` foi identificada no período.

## Mudanças vs extração anterior (MD-0014 + features 022-023, reconciliação 2026-07-15)

- **`SessionState`**: primeira mudança de schema desde a criação — dois campos opcionais anti-loop (`gate_lembrete_fingerprint`, `gate_encerramento_fingerprint`), retrocompatíveis nos dois sentidos (parse tolera ausência; render omite quando vazios).
- **`DecisionsSection.require_registration`** (022): novo booleano, default `True`.
- **`GateVerdict`** (022/023): novo value-object transitório (§9).
- **`HarnessSection.version`**: literal `2.0.1` → `2.1.1`.
- **`Decision`**: sem mudança de schema; população 12 → 16 fichas (MD-0013..MD-0016).

## 10. `Medicao` e satélites — medição de progresso (features 026/027, NOVO) 🟢

Modelos transitórios de `core/progress/service.py` (Pydantic, **jamais persistidos** — a saída versionada é a projeção markdown, o board é a projeção kanban):

| Campo (`Medicao`) | Tipo | Obrigatório | Default | Significado |
|-------------------|------|-------------|---------|-------------|
| `ativa` | FeatureProgresso? | não | `None` | feature forward ativa (de `active-requirements.json`) |
| `pausadas` | List[FeatureProgresso] | não | `[]` | features pausadas |
| `concluidas` | int | não | `0` | contagem de features `done` (sem detalhe — não geram card) |
| `alertas` | List[Alerta] | não | `[]` | derivados e persistentes: alta (divergência declarado×físico), média (pendência de reconciliação no regression-watch) |
| `falhas` | List[str] | não | `[]` | fontes presentes mas ilegíveis (falha real → exit 2 na borda) |
| `board_habilitado` | bool | não | `False` | espelha `[progress.kanban].enabled` (027) |
| `demandas` | List[Demanda] | não | `[]` | cards manuais do board em coluna não-`done` (027) |

**`FeatureProgresso`**: `feature_id`, `short_name`, `estagio` (físico, via `stages.py`), contagens por fase, `iniciada_em` (027, `started-at`) e `acoes: List[AcaoProgresso]` (027). **`AcaoProgresso`** (027): `acao_id` (ID real `T00N` — ids ordinais foram rejeitados por instabilidade a reordenação da tabela, MD-0020/DESCARTADO-e), `descricao`, `fase`, `feita`, `criada_em` (primeiro `ts` da ação no `progress.jsonl`; fallback `started-at`; nunca a hora corrente). **`Demanda`** (027): `card_id`, `titulo`, `coluna` — todos com default `""`.

## 11. Card do board kanban (`.vscode/vscode-kanban.json`, feature 027, NOVO) 🟢

Contrato EXTERNO com o fork do vscode-kanban do mantenedor; schema conhecido por um único módulo (`kanban.py`). Objeto de 4 chaves ordenadas (`todo`, `in-progress`, `testing`, `done`), arrays de cards:

| Campo | Tipo | Emitido pelo exportador | Significado |
|-------|------|--------------------------|-------------|
| `id` | str | sim | gerenciados: `hns:<feature>`, `hns:<feature>:<T00N>`, `hns:alerta:<origem>` |
| `title` | str | sim | ação: `T00N — descrição`; resumo: `NNN-short-name — feitas/total ações` |
| `type` | str | sim | `note` (gerenciados) ou `bug` (alertas) |
| `prio` | int | sim | 0 ação, 1 resumo, 9 alerta alta, 5 alerta média |
| `creation_time` | str | sim | determinístico (ver `AcaoProgresso.criada_em`) |
| `description` | {content, mime} | sim | uma linha, `text/markdown` |
| `details` | {content, mime} | **não** (as-built) | opcional no fork; não emitido |
| `category` | str | sim | `"harness"` = posse do exportador; qualquer outro valor (ou ausente) = card manual, preservado byte a byte |

## Mudanças vs extração anterior (features 024-027, reconciliação 2026-08-11)

- **`ProgressSection`** (026): nova seção `[progress]` (`file`, default `.harness/progresso.md`) em `HarnessConfig`, herança sem migração.
- **`ProgressKanbanSection`** (027): aninhada como `ProgressSection.kanban` (`enabled`, default `False`; `file`, default `.vscode/vscode-kanban.json`).
- **`Medicao`/`FeatureProgresso`/`AcaoProgresso`/`Demanda`** (026/027): novos value-objects transitórios (§10).
- **Card do board** (027): novo contrato externo (§11), único delta-de-contrato-externo do período.
- **`CommandService.execute_command`** (024): novo parâmetro `versionar_estado: bool = True` — não é schema de dados, mas muda o efeito colateral (commit de fechamento condicionado a consentimento, MD-0017).
- **`HarnessSection.version`**: literal `2.1.1` → `2.5.0` (2.2.0 na 024, 2.3.0 na 025, 2.4.0 na 026, 2.5.0 na 027).
- **`SessionState`/`GateVerdict`**: sem mudança de schema no período (o gate mudou de POLÍTICA na borda — advisory, MD-0018 — não de dados).
- **`Decision`**: sem mudança de schema; população 16 → 20 fichas (MD-0017..MD-0020).

## Mudanças vs extração anterior (feature 028, reconciliação 2026-08-11-b)

- **`DecisionsSection.compact_file`/`compact_index_size`** (028): dois campos novos em `[decisions]` (ver §6) — único delta-de-dados da feature; herança sem migração.
- **Visão compacta** (`.harness/decisoes-recentes.md`): novo artefato DERIVADO (não é schema persistido de domínio): `# Decisões recentes` + 3 linhas de orientação + `Total: N ficha(s)` + K fichas mais recentes por ID decrescente (`- **MD-NNNN** — título`, sem backlinks). Derivado na mesma passada do índice em todas as bordas que indexam (CLI, ponte e, desde a MD-0023, a tool MCP), write-only-when-changed, nunca editado à mão.
- **`build_decisions_appendix`** (028): novo parâmetro `compact_file: str | None = None` — precedência compacta→índice no apêndice do `cmd resume`; chamadores antigos preservados.
- **`AntigravityHookBridge.__init__`** (028): dois parâmetros novos com default (`decisions_compact_file`, `decisions_compact_size`).
- **`HarnessSection.version`**: literal `2.5.0` → `2.6.0`.
- **`Decision`**: sem mudança de schema; população 20 → 22 fichas (MD-0021 — operacional, sem código; MD-0022).
