# Contrato: execução shim ↔ core do upstream

> Feature: `020-fonte-unica-e-hooks` · Tipo: arquivo/processo · Confidência: 🟢

## Papel

O wrapper `harness` do projeto-alvo deixa de ser uma cópia executora e passa a ser um **shim**: um despachante fino que executa o core que vive no **upstream**, com o cwd do projeto. É o único ponto que muda para o alvo passar a usar a fonte única.

## Entrada

- **Arquivo:** `<projeto>/harness.toml`, campo `[harness].upstream_path` (caminho absoluto do repo-fonte).
- **Args:** `$@` — repassados verbatim ao `main.py` do upstream.
- **Ambiente:** o shim é invocado da raiz do projeto (uso manual) ou pelo git (hooks, cwd = raiz do repo).

## Comportamento

1. Resolve `SCRIPT_DIR` = diretório do próprio shim (a raiz do projeto).
2. `cd "$SCRIPT_DIR"` — garante o cwd na raiz, para o core resolver `.harness/` e `harness.toml` do projeto (mesmo se chamado de subpasta).
3. Lê `upstream_path` do `harness.toml`: `sed -n 's/^upstream_path = "\(.*\)"/\1/p' harness.toml | head -1`.
4. Monta `PY="$UPSTREAM/.harness/harness-core/.venv/bin/python3"` e `MAIN="$UPSTREAM/.harness/harness-core/src/main.py"`.
5. `exec "$PY" "$MAIN" "$@"` — substitui o processo, repassando código de saída e stdio.

## Saída

- Código de saída e stdout/stderr são exatamente os do `main.py` do upstream (transparência total).

## Erros

- `upstream_path` ausente/vazio no toml, ou `$MAIN`/`$PY` inexistentes → **erro nomeado em stderr** e `exit 1`, com instrução (verificar `upstream_path`; reidratar via `init`). Nunca executa nada degradado nem cai em silêncio.

## Invariantes

- **Footprint de escrita zero (RN-N17/RN-02):** o shim só lê do upstream; toda escrita permanece sob o cwd (projeto).
- **Isolamento (RN-04):** dois projetos usam o mesmo `$MAIN`, cada um com seu cwd → nenhum cross-talk (o core é stateless).
- **Idempotência:** reinstalar o shim (via `init`/`migrate`) produz bytes equivalentes.

## Exemplo (forma canônica)

```bash
#!/bin/bash
# Shim do Harness — executa o core do upstream (fonte única)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1
UPSTREAM=$(sed -n 's/^upstream_path = "\(.*\)"/\1/p' harness.toml | head -1)
PY="$UPSTREAM/.harness/harness-core/.venv/bin/python3"
MAIN="$UPSTREAM/.harness/harness-core/src/main.py"
if [ -z "$UPSTREAM" ] || [ ! -f "$MAIN" ] || [ ! -f "$PY" ]; then
  echo "Erro: core do upstream não encontrado (confira upstream_path no harness.toml)." >&2
  exit 1
fi
exec "$PY" "$MAIN" "$@"
```

> Opcional: `export PYTHONDONTWRITEBYTECODE=1` antes do `exec` para evitar `__pycache__` no upstream compartilhado (inócuo, mas mais limpo).
