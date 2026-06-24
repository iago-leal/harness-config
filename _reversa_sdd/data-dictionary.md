# Dicionário de Dados — harness-core

> Regenerado pelo Archaeologist em 2026-06-24 (re-extração após as features 003, 004 e 005).
> Nível de documentação: **completo**. Fonte: `harness-core/src/core/domain/{models.py,config.py,cache.py}` e os serviços que consomem/persistem essas estruturas.

Estruturas de dados e modelos de domínio do harness-core. Todos os modelos são Pydantic v2.

---

## 1. `SessionState` — estado de sessão do agente 🟢

**Modelo:** `src/core/domain/models.py:SessionState`.
**Persistência:** arquivo Markdown `.harness/estado-da-sessao.md` (local canônico desde a **feature 004**; antes ficava em `ESTADO-DA-SESSAO.md` na raiz). Formato = front-matter YAML (header-máquina) + corpo Markdown (a narrativa). Round-trip por `session/serializer.py`.

| Campo (modelo) | Chave no front-matter | Tipo | Obrigatório | Validação / Default | Exemplo |
|---|---|---|---|---|---|
| `commit_hash` | `commit` | str | sim | regex `^[a-f0-9]{40}$` (SHA1) | `c548223…` (40 hex) |
| `active_feature` | `feature` | str | sim | — | `005-decisoes-em-harness` |
| `start_time` | `start_time` | datetime | sim | default `datetime.now(utc)`; coerção ISO, naive→UTC | `2026-06-24T00:02:09+00:00` |
| `is_active` | `status` | bool | sim | `status=="active"`→True; senão False | `active` / `inactive` |
| `narrative` | corpo `##` | `SessionNarrative` | não | default vazio | (ver §2) |

Campos obrigatórios no front-matter (`serializer._REQUIRED_META`): `commit`, `feature`, `start_time`, `status`. Ausência de qualquer um → `MalformedSessionStateError`.

Métodos de domínio: `start_session(feature, commit)`, `close_session(commit)`, `update_active_feature(feature)` (levanta `ValueError` se sessão inativa).

## 2. `SessionNarrative` — narrativa de retomada (value-object) 🟢 **NOVO (feature 004)**

**Modelo:** `src/core/domain/models.py:SessionNarrative`. Aninhado em `SessionState.narrative`. Escrito pelo agente, lido/reinjetado pela CLI — nunca inventado.
**Persistência:** seções `##` no corpo de `.harness/estado-da-sessao.md`.

| Campo | Seção no corpo Markdown | Tipo | Obrigatório | Default |
|---|---|---|---|---|
| `feito` | `## O que foi feito` | List[str] | não | `[]` |
| `proximos_passos` | `## Próximos passos` | List[str] | não | `[]` |
| `pendencias` | `## Pendências / bloqueios` | List[str] | não | `[]` |
| `ponteiros` | `## Ponteiros` | List[str] | não | `[]` |

Cada item da lista corresponde a uma linha `- <item>` sob a seção. Helper `is_empty()` → True se as 4 listas vazias.

## 3. `SyncCache` — cache de sincronia Git 🟢

**Modelo:** `src/core/domain/cache.py:SyncCache`.
**Persistência:** JSON em `cache_filepath` — no MCP, chumbado em `.harness/sync_cache.json` (`server.py:40`). Evita chamadas `ls-remote` redundantes dentro do TTL.

| Campo | Tipo | Obrigatório | Validação | Exemplo |
|---|---|---|---|---|
| `last_checked_time` | datetime | sim | — | `2026-06-24T00:02:09+00:00` |
| `commit_hash` | str | sim | `constr(pattern=r"^[a-f0-9]{40}$")` (SHA1) | `c548223…` (40 hex) |

## 4. `Decision` — microdecisão (ficha do grafo) 🟢

**Modelo:** `src/core/domain/models.py:Decision`. Mapeia o front-matter YAML de cada `MD-*.md`.
**Persistência:** fichas em `.harness/decisoes/MD-0001..MD-0004.md` (local canônico desde a **feature 005**; antes em `decisoes/` na raiz). Caminho lido de `[decisions].dir` no `harness.toml`.

| Campo (modelo) | Chave no front-matter | Tipo | Obrigatório | Validação / Default |
|---|---|---|---|---|
| `id` | `id` | str | sim | regex `^MD-\d{4}$` |
| `gancho` | `gancho` | str | sim¹ | — |
| `status` | `estado` | str | não | default `ativo` (`ativo`/`descartado`) |
| `relationships` | `relacoes` | List[`Relationship`] | não | `[]` (cada item = `"<verbo> MD-XXXX"`) |
| `filepath` | — (runtime) | str? | não | preenchido no load |
| `raw_content` | — (runtime) | str? | não | Markdown integral, para validação |

¹ `gancho` é não-nulo no modelo; vem de `metadata.get("gancho")` no parse (se ausente no YAML, vira `None` e o Pydantic aceita por ser declarado `str` sem default — ver nota).

**Integridade de conteúdo** (`Decision.validate_integrity`): exige H1 `# MD-XXXX` e as 4 seções obrigatórias no corpo, casadas por regex case-insensitive:

| Seção | Padrão exigido |
|---|---|
| `D` | `- **D:**` |
| `PORQUÊ` | `- **PORQUÊ:**` |
| `DESCARTADO` | `- **DESCARTADO:**` |
| `ESTADO` | `- **ESTADO:**` |

## 5. `Relationship` — aresta do grafo de decisões 🟢

**Modelo:** `src/core/domain/models.py:Relationship`. Aninhado em `Decision.relationships`.

| Campo | Tipo | Obrigatório | Validação |
|---|---|---|---|
| `rel_type` | str | sim | ∈ {`depende-de`, `substitui`, `refina`, `relaciona`, `estende`, `bloqueia`} (normalizado lower) |
| `target_id` | str | sim | regex `^MD-\d{4}$` |

**Verbos inversos** (derivados em `DecisionService.compile_index` para backlinks): `refina→refinado-por`, `depende-de→requerido-por`, `estende→estendido-por`, `substitui→substituído-por`, `relaciona→relacionado-com`, `bloqueia→bloqueado-por`.

## 6. `HarnessConfig` — configuração tipada 🟢 (seção `[decisions]` nova na feature 005)

**Modelo:** `src/core/domain/config.py`. Carregado de `harness.toml` por `load_config(fs)`.

| Seção | Campo | Tipo | Default |
|---|---|---|---|
| `[harness]` | `active_harness` | Literal[`claude`,`gemini`,`antigravity`] | `claude` |
| `[formatting]` | `exclude_paths` | List[str] | `[]` |
| `[formatting]` | `opt_out_file` | str | `.no-autoformat` |
| `[sync]` | `cache_ttl_hours` | int | `24` |
| `[sync]` | `remote_check_enabled` | bool | `True` |
| `[decisions]` | `dir` | str | `.harness/decisoes` |
| `[decisions]` | `index_file` | str | `.harness/microdecisoes.md` |
| `[decisions]` | `header_file` | str | `.harness/decisoes/_cabecalho.md` |

> ⚠️ `[formatting]` é declarado no domínio mas **não é consumido** por `FormattingService` (blindagens e opt-out chumbados — ver code-analysis T4).

## 7. `HARNESS_DOC_DATA` — payload injetado no HTML 🟢

Estrutura JSON compilada por `DocumentationService.generate_html` e injetada no `template.html` (substitui `/* INJECTED_DATA_PLACEHOLDER */`).

| Campo | Tipo | Origem |
|---|---|---|
| `commands` | Array[Object] | introspecção do argparse (`{name, help, arguments[]}`) |
| `rules` | Array[Object] | regex sobre `_reversa_sdd/domain.md` (`{id, title, details, confidence}`) |
| `state` | Object | `.reversa/state.json` integral |

## 8. Bloco de ganchos do `install-prompt` (não persistido) 🟢 **NOVO (feature 003)**

Saída textual de `InstallPromptService.render`, montada por substituição de placeholders no `template.md`:

| Placeholder | Origem |
|---|---|
| `{{ACTIVE_HARNESS}}` | `cfg.harness.active_harness` |
| `{{APPLY_HOOKS}}` | `HarnessProfile.apply_instructions()` |
| `{{HOOKS_BLOCK}}` | `HarnessProfile.hooks_block()` |
| `{{COMMANDS}}` | introspecção do argparse (`- \`<name>\` — <help>`) |

---

## Mudanças vs extração anterior (feature 002)

- **Estado de sessão:** migrou de `ESTADO-DA-SESSAO.md` (raiz) para `.harness/estado-da-sessao.md`; ganhou o value-object `SessionNarrative` (4 listas) no corpo.
- **Microdecisões:** migraram de `decisoes/` (raiz) para `.harness/decisoes/`; caminhos agora vêm de `[decisions]` no `harness.toml`, não chumbados.
- **`HarnessConfig`:** ganhou a seção `[decisions]` tipada.
- **`SyncCache`:** o caminho do cache passou de `$HOME/.claude/.sync-check` (descrição antiga, do legado purgado) para `.harness/sync_cache.json` (chumbado no MCP).
- **`Decision.status`:** valores reais são `ativo`/`descartado` (a extração anterior citava `em-revisao`/`rejeitado`, que não constam no validador).
