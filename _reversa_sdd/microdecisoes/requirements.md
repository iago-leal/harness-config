# Microdecisões (Decisions) — Requisitos (Requirements)

> Regenerado pelo Writer em 2026-06-24 (Re-extração após a feature 005)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`.harness/harness-core/src/core/decisions/service.py`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/core/decisions/service.py) e [`gate.py`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/core/decisions/gate.py); fichas em [`.harness/decisoes/`](file:///Users/iagoleal/dev/harness/.harness/decisoes/); índice [`.harness/microdecisoes.md`](file:///Users/iagoleal/dev/harness/.harness/microdecisoes.md). Drivers: `src/main.py` (subcomando `decisions [--gate]`, hook `Stop`) e `adapters/mcp/server.py` (`process_decisions`).
> **Reconciliação de 2026-08-11-b (feature 028, não commitada nesta data):** a unit ganhou a **visão compacta** `.harness/decisoes-recentes.md` — derivada por `compile_compact_view` na MESMA passada do índice, nas duas bordas que já o compilavam (CLI `decisions`, com e sem `--gate`, e `_handle_stop` da ponte Antigravity), com write-only-when-changed nas duas escritas (`_write_if_changed`; `_extract_title` compartilhado extrai o título do H1 com fallback no ID). Config nova: `DecisionsSection.compact_file` (default `.harness/decisoes-recentes.md`) e `compact_index_size` (`ge=0`, default 10; 0 degrada para cabeçalho + contagem + ponteiros). RN-N56/N57 e RF-08 abaixo; o consumo no resume (precedência compacta→índice) está na unit `comandos-customizados/`; o guidance do init (RN-N58) na unit `bootstrap/`. Ver `domain.md#2.26`, ADR 0028 / MD-0022 (`refina MD-0002`).
> **Reconciliação de 2026-08-11 (feature 025, não commitada nesta data):** o soft-block do Stop foi **aposentado** — o ramo `decisions --gate` deixa de emitir JSON `{"decision":"block"}` no stdout e emite linha `Aviso:` em stderr; stdout sempre vazio. O enforcement colapsa de três políticas para duas (portão duro único no encerramento; advisory nos fins de turno, idêntico nas duas bordas). `gate.py` byte-idêntico; toda a mecânica (avaliação pura, fingerprint grosso persistido antes da emissão, máx. um aviso/sessão, fail-open, exit 0) preservada. RN-N44 revisada e RF-06 reescrito abaixo; ADR 0025 / MD-0018 (`substitui MD-0016`).
> **Reconciliação de 2026-07-15 (features 022-023):** a unit ganhou o **gate de registro** (`gate.py`) — avaliação pura de pendência de registro de microdecisão, com dupla identidade anti-loop. RN-N43..N47 e RF-05..RF-07 abaixo; ressalva T1 da RN-N11 removida (resolvida em `cf73980`, estava stale).

> ⚠️ **Reescrita vs versão anterior:** a implementação **deixou de ser** o script shell `bin/gerar-index-decisoes.sh` em `harness-config/` (purgado, commit `5624f78`) e passou a ser o `DecisionService` Python em `harness-core`. As fichas migraram de `decisoes/` (raiz) para `.harness/decisoes/` e o índice de `microdecisoes.md` (raiz) para `.harness/microdecisoes.md` (feature 005). Os caminhos não são mais chumbados: vêm de `[decisions]` no `harness.toml`.

## Visão Geral

Gerencia o grafo de microdecisões arquiteturais — fichas `MD-NNNN.md` com front-matter YAML e relações tipadas — e DERIVA delas **duas visões**: o índice `.harness/microdecisoes.md` com backlinks (verbos inversos) e, desde a feature 028, a visão compacta `.harness/decisoes-recentes.md` (contagem, ponteiros, K títulos mais recentes), ambas na mesma passada. Valida a integridade do grafo antes de compilar. Os caminhos são lidos de configuração, não chumbados (feature 005).

## Responsabilidades

- Carregar as fichas `MD-*.md` de um diretório, parseando front-matter (`id`, `gancho`, `estado`, `relacoes`). 🟢
- Validar a integridade do grafo (fichas individuais + auto-relação + aresta órfã). 🟢
- Compilar o índice consolidado com backlinks derivados por verbos inversos, de forma determinística. 🟢
- Receber todos os caminhos por parâmetro — não chumbar `decisoes/` nem `microdecisoes.md`. 🟢
- Derivar a visão compacta na mesma passada do índice, com escrita condicionada a mudança (✨f028). 🟢

## Regras de Negócio

- **RN-N11 — Caminhos desacoplados via config:** `dir`, `index_file`, `header_file` vêm de `[decisions]` no `harness.toml`; o `DecisionService` recebe tudo por parâmetro. Default: `.harness/decisoes`, `.harness/microdecisoes.md`, `.harness/decisoes/_cabecalho.md`. (watch item **W001**) 🟢
- **RN-N12 — Índice derivado, não editado à mão:** `.harness/microdecisoes.md` é DERIVADO pelo `./harness decisions`; o cabeçalho declara "Não edite à mão". Backlinks ordenados por ID de origem (determinismo). 🟢
- **RN-N13 — Integridade do grafo:** `validate_integrity` agrega erros — validação de cada ficha, **auto-relação** (`target == self.id`) e **aresta órfã** (alvo fora do grafo). Lista vazia = grafo válido. 🟢
- **RN-N14 — Front-matter obrigatório:** cada `MD-*.md` exige front-matter YAML; diretório ausente → lista vazia; front-matter ausente/YAML inválido → `ValueError`. Cada relação é `"<verbo> MD-XXXX"` (dois tokens), verbo num conjunto fechado de seis, alvo `^MD-\d{4}$`. 🟢
- **Integridade de conteúdo da ficha:** H1 `# MD-XXXX` + as 4 seções obrigatórias `D / PORQUÊ / DESCARTADO / ESTADO` (regex case-insensitive). 🟢
- **RN-N43 — Pendência de registro por sinal físico (feature 022):** universo = diff da âncora (`list_changed_paths_since`) ∪ sujos (`list_dirty_paths`), menos estado/índice/cabeçalho; fichas = `^MD-.*\.md$` sob `decisions.dir`; `pendente = mudanças ∧ ¬fichas`. Sem filtro por tipo de arquivo. Fail-open barulhento (âncora ilegível → `pendente=False` + `aviso`). 🟢
- **RN-N44 (revisada na feature 025) — Enforcement em duas políticas:** o mesmo veredito alimenta (1) o **único portão bloqueante**, o 3º portão do `encerrar-sessao` (escape `--sem-decisao`), e (2) o **advisory de fim de turno**, agora idêntico em espírito nas duas bordas: o hook Stop do Claude (`decisions --gate`) emite `Aviso:` em stderr com stdout vazio e exit 0, mesma política que o Antigravity sempre teve. O soft-block JSON da redação original (022) foi aposentado na 025; nenhum hook regravado — a mudança é comportamental no comando, propagada pela fonte única (RN-N36). Ligado por `decisions.require_registration` (default `True`). 🟢
- **RN-N45 — Anti-loop por fingerprint no estado de sessão:** o mesmo estado de pendência nunca dispara o gate duas vezes; campos opcionais no front-matter, zerados no fechamento. 🟢
- **RN-N47 — Dupla identidade (feature 023):** lembrete usa `sha1(âncora)` (grossa — máx. 1 soft-block/sessão); portão usa `sha1(âncora+HEAD+sujos)` (fina — trabalho novo rearma, pinado por teste-guarda). 🟢
- **RN-N56 — Duas visões, uma passada, duas bordas (feature 028):** `compile_compact_view(decisions, output_filepath, index_file, decisions_dir, max_items)` deriva a compacta imediatamente após `compile_index`, nas duas bordas (CLI `decisions` e `stop` da ponte); formato fixo (`# Decisões recentes`, 3 linhas de orientação, `Total: N ficha(s)`, K mais recentes por ID decrescente como `- **MD-NNNN** — título`, sem backlinks); `max_items=0` degrada para cabeçalho + contagem + ponteiros; write-only-when-changed nas duas escritas. 🟢
- **RN-N57 — Compacta é artefato derivado (feature 028, estende RN-N12):** `.harness/decisoes-recentes.md` é regenerada por inteiro a cada passada; edição manual é sobrescrita sem aviso; nunca é fonte de dado. 🟢

## Requisitos Funcionais

| ID    | Requisito                           | Prioridade | Critério de Aceite                                                                                                            |
| ----- | ----------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------- |
| RF-01 | Carregar fichas e parsear relações. | Must       | `load_decisions(dir)` retorna lista ordenada de `Decision`; relação malformada → `ValueError`.                                |
| RF-02 | Validar integridade do grafo.       | Must       | `validate_integrity` detecta auto-relação, aresta órfã e ficha sem seção obrigatória; grafo válido → lista vazia.             |
| RF-03 | Compilar o índice com backlinks.    | Must       | `compile_index` grava `.harness/microdecisoes.md` com sub-linhas `↳ <saídas> · <entradas>`, deterministicamente.              |
| RF-04 | Caminhos por configuração.          | Must       | `./harness decisions` lê `dir`/`index_file`/`header_file` de `load_config().decisions`; nenhum literal de caminho no serviço. |
| RF-05 | Avaliar pendência de registro (022). | Must      | `evaluate_registration_gate` devolve `GateVerdict` com `pendente`, `mudancas`, `fichas_tocadas`, fingerprints e `aviso` opcional; nunca levanta para a borda. |
| RF-06 | Aviso único no Stop do Claude (022/023, **advisory desde a 025**). | Must | `decisions --gate`: pendência com identidade grossa inédita → linha `Aviso:` em **stderr** (stdout sempre vazio) e persistência do fingerprint **antes** da emissão; mesma sessão não re-emite; exit 0 sempre; jamais bloqueia. |
| RF-07 | Escape auditável no encerramento (022). | Must   | `encerrar-sessao --sem-decisao` grava a declaração na narrativa e satisfaz o gate. |
| RF-08 | Visão compacta derivada na mesma passada (028). | Must | Após `compile_index`, `compile_compact_view` grava `.harness/decisoes-recentes.md` com contagem, ponteiros para índice/fichas e os K=`compact_index_size` títulos mais recentes por ID decrescente; conteúdo inalterado → nenhuma escrita (mtime imóvel); `max_items=0` → só cabeçalho + contagem + ponteiros. |

## Requisitos Não Funcionais

| Tipo             | Requisito inferido                                         | Evidência no código                                  | Confiança |
| ---------------- | ---------------------------------------------------------- | ---------------------------------------------------- | --------- |
| Determinismo     | Backlinks ordenados por ID de origem; índice reprodutível. | `core/decisions/service.py` (`compile_index`)        | 🟢        |
| Robustez         | Front-matter inválido falha barulhento (`ValueError`).     | `core/decisions/service.py` (`load_decisions`)       | 🟢        |
| Atomicidade      | Gravação do índice via `write_file_atomic`.                | `core/decisions/service.py` + `adapters/fs/local.py` | 🟢        |
| Manutenibilidade | Caminhos desacoplados (config), sem literais.              | `core/decisions/service.py`, `core/domain/config.py` | 🟢        |

## Critérios de Aceitação

```gherkin
Dado que MD-0002 declara "refina MD-0001"
Quando executo `./harness decisions`
Então o índice .harness/microdecisoes.md mostra em MD-0001 o backlink "↳ refinado-por MD-0002".

Dado uma ficha cuja relação aponta para um MD inexistente
Quando validate_integrity roda
Então o erro de aresta órfã é incluído na lista de erros (índice não é compilado limpo).

Dado um harness.toml com [decisions].dir customizado
Quando `./harness decisions` roda
Então o serviço lê as fichas do diretório configurado, sem caminho chumbado.

Dado uma ficha MD-*.md sem front-matter YAML
Quando load_decisions roda
Então um ValueError barulhento é levantado.

Dado trabalho substantivo na sessão (commit desde a âncora ou working tree sujo) sem ficha MD-*.md tocada
Quando `./harness decisions --gate` roda pela primeira vez na sessão
Então stderr recebe a linha `Aviso:` com o lembrete, o stdout fica vazio e o fingerprint grosso é persistido no estado (advisory desde a 025).

Dado que o lembrete já disparou nesta sessão (fingerprint grosso persistido)
Quando novos arquivos são tocados e `decisions --gate` roda de novo
Então nenhum novo aviso é emitido (máx. 1 por sessão — feature 023; canal advisory desde a 025).

Dado o portão do encerramento já bloqueado uma vez para o estado de pendência atual
Quando um NOVO commit sem ficha entra e `encerrar-sessao` roda
Então o portão REARMA e bloqueia de novo (identidade fina; teste-guarda da 023).
```

## Prioridade (MoSCoW)

| Requisito                                   | MoSCoW | Justificativa                                       |
| ------------------------------------------- | ------ | --------------------------------------------------- |
| Compilação do índice com backlinks (RN-N12) | Must   | Entrega central; o índice é o artefato consumido.   |
| Integridade do grafo (RN-N13)               | Must   | Sem ela, o índice consolida um grafo inconsistente. |
| Caminhos por config (RN-N11)                | Must   | Efeito da feature 005; watch item W001.             |
| Front-matter obrigatório (RN-N14)           | Must   | Pré-condição do parse; falha barulhenta.            |

## Rastreabilidade de Código

| Arquivo                     | Função / Classe                                                               | Cobertura |
| --------------------------- | ----------------------------------------------------------------------------- | --------- |
| `core/decisions/service.py` | `DecisionService.load_decisions`, `validate_integrity`, `compile_index`       | 🟢        |
| `core/decisions/gate.py`    | `evaluate_registration_gate`, `compute_fingerprint`, `compute_lembrete_fingerprint`, `GateVerdict` (022/023) | 🟢        |
| `core/domain/models.py`     | `Decision`, `Relationship`                                                    | 🟢        |
| `core/domain/config.py`     | `DecisionsSection`, `load_config`                                             | 🟢        |
| `src/main.py`               | Subcomando `decisions` (deriva caminhos de `load_config`)                     | 🟢        |
| `adapters/mcp/server.py`    | Tool `process_decisions` (T1 resolvido em `cf73980`: `load_config` importado) | 🟢        |
| `tests/`                    | Cobertura de teste do serviço de decisões                                     | 🟢        |
