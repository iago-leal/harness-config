# Contrato: reinjeção de contexto por harness

> Tipo: hook / arquivo. Como o estado canônico chega ao contexto do agente no boot.
> O core (`cmd resume`) produz texto puro; o mecanismo abaixo vive na borda (Strategy por `active_harness`).

## Família A — hook `SessionStart` + `additionalContext` (Claude, Gemini CLI)

`cmd resume` emite no **stdout**, com **exit 0**, exatamente:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<corpo do estado-da-sessao, possivelmente com aviso de âncora>"
  }
}
```

- **Claude**: gatilho em `.claude/settings.json` → `SessionStart` (matcher `startup|resume|clear`) → `./harness cmd resume`. Teto **10.000 caracteres**. Exit 2 é bloqueante (JSON ignorado).
- **Gemini CLI** (≥ 0.25): gatilho em `.gemini/settings.json` → mesmo hook `SessionStart`, mesmo JSON. Sem limite documentado.
- **Invariante**: nada além do JSON pode ir ao stdout. Avisos (divergência de âncora) vão para stderr e/ou embutidos no `additionalContext`.

## Família B — projeção em arquivo estático (Antigravity / `agy`)

O `agy` não injeta stdout no contexto; relê markdown estático a cada sessão.

- `cmd encerrar-sessao` (e, se houver hook de pré-invocação, `cmd resume`) **projeta** o canônico `.harness/estado-da-sessao.md` para `.agents/rules/estado-sessao.md` (ou um bloco delimitado em `AGENTS.md`).
- A injeção é **passiva**: o conteúdo já está no arquivo de regras quando o `agy` inicia.
- **Âncora/status no boot** 🟡: via hook `PreInvocation` do `agy` rodando `cmd resume` em modo sem-injeção (a confirmar por teste de fumaça). Sem o hook, degrada para reinjeção passiva pura.

## Seleção

A família é escolhida por `active_harness` (em `harness.toml`), reusando o padrão de `core/install/harness_profiles.py`:

| `active_harness` | Família | Gatilho |
|------------------|---------|---------|
| `claude` | A | hook em `.claude/settings.json` |
| `gemini` | A | hook em `.gemini/settings.json` |
| `antigravity` | B | projeção em `.agents/rules/` + hook de pré-invocação (a validar) |

## Erros e idempotência

- `cmd resume` é idempotente: reexecutar reescreve o estado e re-emite o JSON sem efeito colateral acumulado.
- Falha de IO/parse → erro nomeado (RN-N4); no contexto de hook, evitar exit 2 acidental que bloqueie o boot — preferir exit não-bloqueante com aviso em stderr quando o estado não for crítico.
