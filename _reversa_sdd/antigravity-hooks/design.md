# Antigravity Hooks (Driver de Ganchos do Antigravity) — Design Técnico

> Gerado pelo Archaeologist em 2026-06-24 15:19 (Re-extração após a feature 009-hooks-antigravity). Âncora (HEAD): `e30b9a6`.
> Foca no COMO a unit é construída, a partir do código legado lido. Escala: 🟢 / 🟡 / 🔴

## Interface

| Símbolo                                 | Assinatura                                                                                               | Retorno | Observação                                                                           |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------ |
| `AntigravityHookBridge.__init__`        | `(fs, formatting_service, decision_service, decisions_dir, decisions_index_file, decisions_header_file)` | `None`  | Tudo por injeção; instanciação concreta fica na borda (`agy-hook`).                  |
| `AntigravityHookBridge.handle`          | `(event: str, stdin_text: str)`                                                                          | `str`   | Despacha por evento e devolve o stdout JSON exigido. **Nunca levanta.**              |
| `materialize_hooks_json`                | `(fs: FileSystemPort, project_path: str, command_path: str, profile: Optional[object] = None)`           | `None`  | Grava `<project_path>/.agents/hooks.json` por merge do named-hook `harness`.         |
| `AntigravityProfile.hooks_block`        | `()`                                                                                                     | `str`   | JSON colável (named-hook `harness`); `<ABS>` permanece literal até a materialização. |
| `AntigravityProfile.apply_instructions` | `()`                                                                                                     | `str`   | Instrui aplicar no `.agents/hooks.json` do projeto; nunca em diretório global.       |

## Fluxo Principal — adaptador (`AntigravityHookBridge.handle`)

`handle(event, stdin_text)` despacha por evento; cada ramo passa por `_safe(event, handler, stdin_text, fallback)`. Evento desconhecido → loga e retorna `{}`.

1. **`pre-tool-use` → `_handle_pre_tool_use` (captura):** parseia o payload; lê `stepIdx` e `toolCall.args.TargetFile`. Se ambos presentes e `_scratch_path` resolvível, lê o mapa atual, insere `mapa[str(stepIdx)] = target_file` e o reescreve atomicamente. Retorna `{"decision": "allow"}`. 🟢
2. **`post-tool-use` → `_handle_post_tool_use` (formatação):** lê `stepIdx` e `error`. Se `stepIdx` presente, `error` vazio e o scratch existe, recupera `target_file = mapa[str(stepIdx)]`; se houver, chama `formatting_service.format_file(target_file)` (que já honra opt-out/exclusões e retorna sempre 0). Retorna `{}`. 🟢
3. **`stop` → `_handle_stop` (decisões):** `load_decisions(decisions_dir)`, `validate_integrity` (erros são logados, não bloqueiam), `compile_index(decisions, decisions_index_file, decisions_header_file)`. Retorna `{}`. 🟢

## Fluxo Principal — materialização (`materialize_hooks_json`)

1. `profile = profile or AntigravityProfile()`. 🟢
2. `_resolve_harness_block(profile.hooks_block(), command_path)`: substitui `<ABS>` por `command_path` na STRING JSON do perfil, faz `json.loads` e retorna `data["harness"]`. 🟢
3. `_read_existing(fs, hooks_path)`: lê o `.agents/hooks.json` atual se existir e for JSON válido; vazio/ilegível/não-dict → dict vazio. 🟢
4. `existing["harness"] = harness_block` — **merge por named-hook** (preserva chaves de terceiros). 🟢
5. `fs.makedirs(<project>/.agents)` e `fs.write_file_atomic(hooks_path, json.dumps(existing, indent=2, ensure_ascii=False) + "\n")`. Toda escrita sob `project_path`. 🟢

## Mapa de scratch `stepIdx → TargetFile`

- `_scratch_path(payload)` → `<artifactDirectoryPath>/.harness-agy/pending-format.json` (constantes `_SCRATCH_DIRNAME = ".harness-agy"`, `_SCRATCH_FILENAME = "pending-format.json"`). Sem `artifactDirectoryPath` → `None` (sem captura). 🟢
- `_read_map` lê via `fs.read_file`, tolera ausência/JSON inválido/não-dict (→ `{}`). 🟢
- `_write_map` cria o diretório (`fs.makedirs`) e grava atomicamente (`fs.write_file_atomic`). 🟢

A persistência entre `PreToolUse` e `PostToolUse` é a estratégia D-03 (captura + formatação), que preserva a granularidade por-edição sem parsear o `transcript.jsonl` (formato interno frágil).

## Fluxos Alternativos

- **Qualquer exceção no handler:** capturada por `_safe`; loga em stderr (`_log`) e emite o `fallback` do evento (`{"decision": "allow"}` para `pre-tool-use`, senão `{}`). 🟢
- **Falha de borda (config/stdin/construção):** capturada no ramo `agy-hook` do `main.py`; o `fallback` é pré-computado a partir de `args.event` antes de qualquer operação que possa lançar, e impresso com exit 0. 🟢
- **`artifactDirectoryPath` ausente:** `_scratch_path` retorna `None`; captura é silenciosamente pulada. 🟢
- **`hooks.json` preexistente com chaves de terceiros:** preservadas; só `harness` é substituída. 🟢

## Dependências

- `FileSystemPort` — leitura/escrita do scratch e do `.agents/hooks.json` (injetado).
- `FormattingService` — formatação no `PostToolUse` (reusado, agnóstico ao harness).
- `DecisionService` — validação/indexação de microdecisões no `Stop` (reusado).
- `AntigravityProfile` — fonte do bloco canônico do `hooks.json` (named-hook `harness`).
- Stdlib apenas (`json`, `os`, `sys`); nenhuma dependência nova.

## Decisões de Design Identificadas

| Decisão                                                                          | Evidência no código                                  | Confiança |
| -------------------------------------------------------------------------------- | ---------------------------------------------------- | --------- |
| Terceiro driver no anel de adaptadores, delegando aos serviços de domínio (D-02) | `hook_bridge.py` (injeção + delegação)               | 🟢        |
| Captura `PreToolUse` + formatação `PostToolUse` via scratch (D-03)               | `hook_bridge.py` (`_scratch_path`/`_read_map`)       | 🟢        |
| Não-bloqueio em dois anéis (`_safe` interno + try/except da borda)               | `hook_bridge.py`, `main.py` (ramo `agy-hook`)        | 🟢        |
| Materialização por merge por named-hook (D-05)                                   | `antigravity_hooks.py` (`existing["harness"] = ...`) | 🟢        |
| Caminho absoluto resolvido no `init`, reescrito no `upgrade` (D-06)              | `init_service.py`, `antigravity_hooks.py`            | 🟢        |
| `hooks.json` canônico vindo do `AntigravityProfile` (fonte única do bloco)       | `harness_profiles.py` × `antigravity_hooks.py`       | 🟢        |

## Estado Interno

O adaptador é **sem estado em memória**: o único estado persistido é o arquivo de scratch `pending-format.json`, efêmero, sob `artifactDirectoryPath`. A materialização produz o arquivo `.agents/hooks.json` no projeto. Nenhum log persistente.

## Observabilidade

- `_log(message)` escreve sempre em `stderr` (`[harness agy-hook] ...`), jamais em `stdout` (reservado ao contrato JSON por evento).
- Erros de integridade de microdecisões no `Stop` são logados, nunca bloqueiam.
- O não-bloqueio é silencioso por design: falhas degradam para o stdout-padrão do evento + exit 0.

## Riscos e Lacunas

- 🟡 **Premissas de runtime do Antigravity:** estabilidade do `stepIdx` entre eventos e acesso ao `artifactDirectoryPath` não foram verificáveis localmente (sem runtime do Antigravity). Cobertas por testes de contrato (fixtures).
- 🟢 **Caminho absoluto no `command`:** repositório movido sem `upgrade` aponta para o caminho antigo; mitigado pelo `upgrade`, documentado no onboarding.
