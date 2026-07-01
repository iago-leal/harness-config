# Contrato: merge dos hooks do Claude em `.claude/settings.json`

> Feature: `020-fonte-unica-e-hooks` · Tipo: arquivo · Confidência: 🟢
> Altera `install/claude_settings.py::materialize_claude_settings`. Modelo: RN-N27 (merge por named-hook do Antigravity), descido um nível.

## Problema atual

Hoje o merge é **por-evento**: `hooks[event] = value` (claude_settings.py:~43) substitui o **array inteiro** de cada evento do harness (`SessionStart`, `PostToolUse`, `Stop`). Um item próprio do usuário no mesmo evento é descartado. Chaves de topo e eventos de outro nome já são preservados.

## Contrato novo — merge por-item

Para cada evento `E` do harness (`SessionStart`, `PostToolUse`, `Stop`), com item canônico `H_E`:

1. Ler `arr = existing["hooks"].get(E, [])` (lista; se ausente/ível-inválida → `[]`).
2. Localizar o índice do **item do harness** em `arr`: o primeiro item cujo `command` (dentro de `item["hooks"][*]["command"]`) contém a **assinatura** do evento:
   - `SessionStart` → substring `harness cmd resume`
   - `PostToolUse` → substring `harness format`
   - `Stop` → substring `harness decisions`
3. Se encontrado → **substituir** aquele item por `H_E`. Se não → **inserir** `H_E` (append).
4. Escrever `existing["hooks"][E] = arr` e persistir de forma **atômica** (`write_file_atomic`).

## Assinatura (identidade do item do harness)

- Marca estável = a substring do subcomando no `command` (`harness cmd resume`/`harness format`/`harness decisions`). Vale mesmo com o prefixo `${CLAUDE_PROJECT_DIR}/harness …`.
- **Não** usar `matcher` como identidade (o usuário pode ter o mesmo matcher com outro comando).

## Preservação garantida

- **Itens alheios no mesmo evento** (ex.: um `PostToolUse` com `command: meu-linter.sh`) → preservados na mesma lista.
- **Eventos de outro nome** (ex.: `PreToolUse`) → intocados.
- **Chaves de topo** (`model`, `permissions`, `theme`, …) → intocadas.

## Idempotência

Rodar `materialize`/`init` N vezes converge: na 1ª insere `H_E`; nas seguintes, encontra pela assinatura e substitui por bytes equivalentes. O array não cresce.

## Casos de borda

- `settings.json` ausente/vazio/inválido → tratar como `{}` (comportamento atual de `_read_existing` preservado).
- `hooks` presente mas não-dict → normalizar para `{}`.
- Evento presente mas não-lista → normalizar para `[]` antes do merge.

## Critérios de aceite (para os testes com `FakeFs`)

- Item próprio em `PostToolUse` sobrevive + item do harness adicionado.
- Reexecução não duplica o item do harness.
- `PreToolUse` e chaves de topo intactos.
- Sem `settings.json` prévio → cria com só os três itens do harness.
