# Dicionário de Dados — harness-core

> Regenerado pelo Archaeologist em 2026-06-24 (re-extração pós-feature 008-reprodutibilidade-e-config).
> Nível de documentação: **completo**. Fonte: `.harness/harness-core/src/core/domain/{models.py,config.py,cache.py}` e os serviços que consomem/persistem essas estruturas.
> **Reconciliação de 2026-07-05** (pós-features 010-021): novo campo `[session].inject_decisions_index` (§6, feature 021); novo agregado de valor `EndSessionOffers`/`PushOffer`/`UpgradeOffer` (§8, feature 014, `session/offers.py` — dataclasses, não Pydantic, exceção deliberada pois são apenas DTOs de decisão da borda); `.harness/decisoes/` cresceu de 5 para 12 fichas (§4).

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

Campos obrigatórios no front-matter (`serializer._REQUIRED_META`): `commit`, `feature`, `start_time`, `status`. Ausência de qualquer um → `MalformedSessionStateError`.

Métodos de domínio: `start_session(feature, commit)`, `close_session(commit)`, `update_active_feature(feature)` (levanta `ValueError` se sessão inativa).

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
**Persistência:** fichas em `.harness/decisoes/MD-0001..MD-0012.md` (cresceu de 5 para 12 desde a extração anterior). Caminho lido de `[decisions].dir` no `harness.toml`.

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
| `[session]`    | `state_file`                                    | str                                      | `.harness/estado-da-sessao.md`    |
| `[session]`    | `inject_decisions_index` (novo 🟢, feature 021) | bool                                     | `True`                            |

> 🟢 **`upstream_path`** e **`version`** foram adicionados na feature 007 à seção `[harness]` para permitir que instalações físicas locais em repositórios de destino retenham metadados que conectam a cópia ao seu core upstream original e acompanhem as atualizações físicas.
> 🟢 **`inject_decisions_index`** (feature 021): opt-out do apêndice do índice de decisões anexado ao `cmd resume` — só tem efeito quando `active_harness == "claude"` (gate por harness fixado no código, não configurável). Retrocompatível: harness.toml sem a chave assume `True`.

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

## Mudanças vs extração anterior (feature 007)

- **`HarnessConfig`** (Consumo Ativo de Configurações): As chaves de formatação (`exclude_paths` e `opt_out_file`) do `HarnessConfig` agora são consumidas dinamicamente pelo `FormattingService`. O suporte à exclusão dinâmica inclui casamento de padrões glob (wildcards como `*` e `?`) via `fnmatch`.
- **Reprodutibilidade**: Gerenciamento de dependências unificado usando `uv` com compilação determinística do `requirements.txt` a partir de `requirements.in`. Pipeline de integração contínua (CI) adicionado sob `.github/workflows/ci.yml`.

## Mudanças vs extração anterior (features 010-021, reconciliação 2026-07-05)

- **`inject_decisions_index`** (021): novo campo booleano em `[session]`, default `True` — único ponto de configuração da feature de resume ancorado.
- **`EndSessionOffers`/`PushOffer`/`UpgradeOffer`** (014): agregado de valor novo, não coberto na extração anterior porque a feature 014 é posterior a ela; documentado agora por ainda estar em uso ativo (consumido por `close_flow.py`, ver code-analysis.md §8).
- **`Decision`**: mesma forma de dados, mas a população de fichas cresceu de 5 para 12 — sem mudança de schema, só de volume.
- Nenhuma mudança de schema em `SessionState`/`SessionNarrative`/`SyncCache`/`HARNESS_DOC_DATA` foi identificada no período.
