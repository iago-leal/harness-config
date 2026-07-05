# Onboarding: testar o hook de busca ancorada

> Identificador: `021-hook-busca-ancorada`
> Data: `2026-07-05`
> Objetivo: verificar, na mão, que o `cmd resume` passa a anexar o índice de decisões ao contexto reinjetado — e que o comportamento é não-bloqueante e desativável.

Todos os comandos rodam a partir da raiz do repositório (`/Users/iagoleal/dev/harness`), pelo wrapper `./harness`.

## Pré-condições

1. Suíte do core verde antes de começar:
   ```bash
   cd .harness/harness-core && python -m pytest -q && cd -
   ```
2. Garantir que o índice de decisões existe e está atualizado (é derivado pelo hook `Stop`, mas force uma geração):
   ```bash
   ./harness decisions
   ```
   Esperado: `Índice de decisões compilado com sucesso em '.harness/microdecisoes.md'.`

## Cenário A — resume anexa o índice (harness Claude, padrão ligado)

3. Rodar o resume como o `SessionStart` faz e inspecionar o JSON emitido:
   ```bash
   ./harness cmd resume < /dev/null
   ```
   Esperado no `stdout`: um JSON com `hookSpecificOutput.additionalContext` contendo **duas** partes —
   (a) a narrativa do estado (seções "O que foi feito / Próximos passos / …");
   (b) o bloco do índice de decisões (cabeçalho de orientação + a lista `- **MD-NNNN** — título …`).
4. Conferir que o volume do bloco de decisões corresponde ao índice (~1,7 KB), não às fichas inteiras (~31 KB):
   ```bash
   wc -c .harness/microdecisoes.md .harness/decisoes/*.md | tail -1
   ```

## Cenário B — desativação por configuração

5. Desligar o recurso no `harness.toml`:
   ```toml
   [session]
   inject_decisions_index = false
   ```
6. Rodar de novo:
   ```bash
   ./harness cmd resume < /dev/null
   ```
   Esperado: o `additionalContext` traz **apenas** a narrativa do estado; nenhum bloco de índice.
7. Reverter a alteração no `harness.toml` (remover o flag ou voltar para `true`).

## Cenário C — índice ausente não trava o boot (não-bloqueio)

8. Simular a ausência do índice sem apagá-lo de verdade:
   ```bash
   mv .harness/microdecisoes.md /tmp/microdecisoes.bak
   ./harness cmd resume < /dev/null ; echo "exit=$?"
   mv /tmp/microdecisoes.bak .harness/microdecisoes.md
   ```
   Esperado: aviso em `stderr` sobre o índice ausente; o `stdout` ainda traz o estado; `exit=0`.

## Cenário D — teto de contexto (opcional)

9. Se estado + índice somarem mais de 10 000 caracteres, o `HookContextSink` corta o final e anexa `…[truncado: estado excede 10000 caracteres]`. Com o tamanho atual (~5,9 KB) não há truncamento; este cenário é coberto por teste unitário, não exige reprodução manual.

## Saúde final

10. Reexecutar a suíte e confirmar verde:
    ```bash
    cd .harness/harness-core && python -m pytest -q && cd -
    ```
11. Conferir que Gemini/Antigravity permanecem inalterados (fora do corte): a mudança só atua quando `active_harness == "claude"`.
