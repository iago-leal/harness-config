# Session (Estado de Sessão Unificado) — Design Técnico

> Regenerado pelo Writer em 2026-06-24 (Re-extração; feature 004)
> Foca no COMO a unit é construída, a partir do código legado lido. Escala: 🟢 / 🟡 / 🔴

## Interface

| Símbolo                       | Assinatura                      | Retorno        | Observação                                                                                                                      |
| ----------------------------- | ------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `serializer.parse`            | `(text: str)`                   | `SessionState` | Sem `---` → `MalformedSessionStateError`; YAML inválido/não-dict → erro; campo obrigatório ausente → erro.                      |
| `serializer.render`           | `(state: SessionState)`         | `str`          | Monta meta (`commit/feature/start_time/status`) via `yaml.safe_dump(sort_keys=False)` + corpo.                                  |
| `serializer.render_narrative` | `(narrative: SessionNarrative)` | `str`          | 4 seções fixas `_SECTIONS`. Reusado na reinjeção.                                                                               |
| `serializer._coerce_datetime` | `(value)`                       | `datetime`     | Aceita `datetime` ou ISO (`Z`→`+00:00`); naive → UTC.                                                                           |
| `HookContextSink.deliver`     | `(text: str)`                   | —              | Imprime `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": <texto>}}`; trunca em `MAX_CHARS=10000`. |
| `FileProjectionSink.deliver`  | `(text: str)`                   | —              | Grava o estado em `.agents/rules/estado-sessao.md` (cria o diretório-pai).                                                      |
| `get_sink`                    | `(active_harness: str, fs)`     | `SessionSink`  | `_FAMILY_BY_HARNESS`: claude/gemini→hook; antigravity→file; desconhecido → `ValueError`.                                        |

**Mapa front-matter ↔ modelo** (`_REQUIRED_META = (commit, feature, start_time, status)`):

| Chave YAML   | Campo `SessionState` | Validação                              |
| ------------ | -------------------- | -------------------------------------- |
| `commit`     | `commit_hash`        | regex SHA1 `^[a-f0-9]{40}$`            |
| `feature`    | `active_feature`     | —                                      |
| `start_time` | `start_time`         | ISO, naive→UTC                         |
| `status`     | `is_active`          | `=="active"` (case-insensitive) → True |

**Mapa seção ↔ narrativa** (`_SECTIONS`): "O que foi feito"→`feito`, "Próximos passos"→`proximos_passos`, "Pendências / bloqueios"→`pendencias`, "Ponteiros"→`ponteiros`.

## Fluxo Principal

1. **parse(text):** `_FRONTMATTER_RE` separa meta e corpo. Sem `---` → `MalformedSessionStateError`. `yaml.safe_load` da meta; não-dict → erro. Confere `_REQUIRED_META`. `status` define `is_active`. Constrói `SessionState`; `ValueError` do domínio (ex.: commit não-SHA1) é convertido em `MalformedSessionStateError`. O corpo é parseado nas 4 seções → `SessionNarrative`. 🟢
2. **render(state):** monta dict de meta na ordem fixa, `yaml.safe_dump(sort_keys=False)` entre `---`, anexa `render_narrative(state.narrative)`. 🟢
3. **render_narrative(narrative):** para cada uma das 4 seções, emite `## <título>` e as linhas `- <item>`. 🟢
4. **Reinjeção (na borda):** `main.py` resolve `get_sink(active_harness, fs)` e chama `deliver(texto)`. O `HookContextSink` serializa o envelope JSON no stdout (truncando em 10000); o `FileProjectionSink` projeta num arquivo estático relido a cada boot. 🟢

## Fluxos Alternativos

- **Arquivo ausente:** o consumidor (`core/commands.load_session`) trata como `None` (sessão nova). O serializer só é chamado com conteúdo presente. 🟢
- **Estado corrompido:** qualquer violação no parse → `MalformedSessionStateError` (RN-N4). 🟢
- **Contexto longo (Claude):** `HookContextSink` trunca em `MAX_CHARS=10000` e anexa sufixo de aviso. 🟢
- **Harness desconhecido:** `get_sink` levanta `ValueError` barulhento. 🟢

## Dependências

- `core/domain/models.SessionState` / `SessionNarrative` — estruturas serializadas.
- `core/session/errors.MalformedSessionStateError` — erro de estado corrompido.
- `PyYAML` — `safe_load`/`safe_dump` do front-matter.
- `FileSystemPort` — usado pelo `FileProjectionSink` (gravação + `makedirs`).
- Consumidor: `core/commands/service.py` (`load_session`/`save_session`, `resume`/`encerrar-sessao`).

## Decisões de Design Identificadas

| Decisão                                                                         | Evidência no código                                   | Confiança |
| ------------------------------------------------------------------------------- | ----------------------------------------------------- | --------- |
| Formato front-matter YAML + corpo Markdown (header-máquina + narrativa legível) | `serializer.py` (`_FRONTMATTER_RE`, `_SECTIONS`)      | 🟢        |
| Invariante de round-trip como contrato testável                                 | `serializer.py` + `test_session.py`                   | 🟢        |
| Sink como Strategy escolhida na borda (core agnóstico a harness)                | `sinks.py` (`get_sink`, `_FAMILY_BY_HARNESS`)         | 🟢        |
| Duas famílias de entrega (hook vs arquivo) por limitação de cada agente         | `sinks.py` (`HookContextSink` × `FileProjectionSink`) | 🟢        |
| Teto de 10000 chars no envelope do Claude                                       | `sinks.py` (`MAX_CHARS`)                              | 🟢        |

## Estado Interno

O estado de domínio (`SessionState`) é externalizado em `.harness/estado-da-sessao.md`. A unit em si não guarda estado em memória entre chamadas; serializer e sinks são puros sobre suas entradas (o sink de arquivo tem efeito colateral de I/O).

## Observabilidade

- `HookContextSink` escreve o envelope JSON no stdout (consumido pelo runtime do agente).
- `MalformedSessionStateError` é a sinalização barulhenta de corrupção (RN-N4).
- Sem logging estruturado dedicado.

## Riscos e Lacunas

- 🟢 **T2 (RESOLVIDO via configuração, feature 006):** o caminho do estado deixou de ser chumbado nos drivers. CLI (`main.py:169`) e MCP (`server.py:94`) leem `config.session.state_file` (`SessionSection`, default `.harness/estado-da-sessao.md`). O literal `ESTADO-DA-SESSAO.md` na raiz foi removido do MCP; a máquina de estado paralela CLI×MCP não existe mais. Registro histórico: a divergência existia até a feature 006, que a fechou por configuração.
- 🟡 O `FileProjectionSink` grava em caminho fixo `.agents/rules/estado-sessao.md` (não parametrizado). O caminho do estado canônico, porém, passou a vir de `[session].state_file` no `harness.toml` (`SessionSection` no domínio) ✨f006.
