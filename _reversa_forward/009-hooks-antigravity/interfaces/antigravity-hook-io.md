# Interface: protocolo de ganchos do Antigravity (stdin/stdout)

> Identificador: `009-hooks-antigravity`
> Tipo: contrato de processo (CLI ↔ agente), arquivo de configuração `hooks.json`
> Fonte normativa: `https://antigravity.google/docs/hooks` (doc oficial, lida nesta sessão)

Este arquivo descreve o contrato que o **adaptador de borda** (`./harness agy-hook <evento>`) implementa. O adaptador lê o payload no `stdin` (JSON), age via serviços de domínio e escreve a resposta no `stdout` (JSON, camelCase).

## Arquivo de configuração — `.agents/hooks.json`

```json
{
  "harness": {
    "PreToolUse": [
      {
        "matcher": "write_to_file|replace_file_content|multi_replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "<ABS>/harness agy-hook pre-tool-use",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "write_to_file|replace_file_content|multi_replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "<ABS>/harness agy-hook post-tool-use",
            "timeout": 30
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "<ABS>/harness agy-hook stop",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

- `<ABS>` é o caminho absoluto do projeto-alvo, gravado pelo `init` (D-06). O `matcher` é regex sobre o nome da tool; `""`/`"*"` casa todas.
- O bloco `PreToolUse` só é emitido se a estratégia de captura (D-03) for a escolhida; no fallback Stop+git-diff ele é omitido.

## Campos comuns (todos os eventos, no stdin)

| Campo                   | Tipo            | Uso pelo adaptador                                                     |
| ----------------------- | --------------- | ---------------------------------------------------------------------- |
| `conversationId`        | string (UUID)   | Chave de escopo do scratch de captura                                  |
| `workspacePaths`        | array de string | Raiz(es) do projeto; base para resolver caminhos e rodar git           |
| `transcriptPath`        | string          | Não usado na estratégia primária (evita acoplar ao `transcript.jsonl`) |
| `artifactDirectoryPath` | string          | Diretório de scratch para o mapa `stepIdx→TargetFile`                  |

## Evento `PreToolUse` (captura)

**stdin (relevante):**

| Campo                      | Tipo   | Descrição                             |
| -------------------------- | ------ | ------------------------------------- |
| `toolCall.name`            | string | Nome da tool (ex.: `write_to_file`)   |
| `toolCall.args.TargetFile` | string | Caminho do arquivo a ser escrito      |
| `stepIdx`                  | int    | Índice 0-based do passo na trajetória |

**Ação do adaptador:** grava `{ "<stepIdx>": "<TargetFile>" }` no scratch sob `artifactDirectoryPath`.

**stdout exigido:** `{ "decision": "allow" }` — **nunca** bloqueia (gancho não-bloqueante; jamais `"deny"`).

## Evento `PostToolUse` (formatação)

**stdin (relevante):**

| Campo     | Tipo              | Descrição                                  |
| --------- | ----------------- | ------------------------------------------ |
| `stepIdx` | int               | Índice do passo concluído                  |
| `error`   | string (opcional) | Mensagem de erro do tool; vazio se sucesso |

**Ação do adaptador:** resolve o caminho via scratch do `stepIdx`; se houver e `error` vazio, chama `FormattingService.format_file(path)` (que já honra `opt_out_file` e `exclude_paths`). Sempre não-bloqueante (o serviço retorna 0 mesmo em falha).

**stdout exigido:** `{}` (objeto vazio).

## Evento `Stop` (decisões)

**stdin (relevante):**

| Campo               | Tipo              | Descrição                                             |
| ------------------- | ----------------- | ----------------------------------------------------- |
| `terminationReason` | string            | Ex.: `model_stop`, `max_steps_exceeded`, `error`      |
| `fullyIdle`         | bool              | `true` se o agente terminou e não há tarefas de fundo |
| `error`             | string (opcional) | Erro de sistema, se houver                            |

**Ação do adaptador:** chama `DecisionService` (equivalente a `./harness decisions`) para validar e reindexar microdecisões.

**stdout exigido:** objeto JSON **sem** `"decision": "continue"` (não queremos reentrar no laço). Emitir `{}` é suficiente.

## Tratamento de erros, idempotência e timeouts

- **Idempotência:** todas as ações são idempotentes (formatação e indexação podem reexecutar sem efeito colateral). Reentregas do mesmo evento são seguras.
- **Erros:** falha interna do adaptador é logada (erro barulhento) mas **nunca** vira `"deny"`/`"continue"`; o adaptador captura exceções e ainda emite o stdout exigido com exit 0, preservando o laço do agente.
- **Timeouts:** herdados do `hooks.json` (`PreToolUse` 10s, `PostToolUse` 30s, `Stop` 10s), alinhados aos timeouts do perfil do Claude.
- **camelCase:** toda chave de entrada e saída segue camelCase, conforme o contrato.
