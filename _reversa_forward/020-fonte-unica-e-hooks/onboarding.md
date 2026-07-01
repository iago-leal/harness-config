# Onboarding: testar a fonte única + hooks não-destrutivos

> Feature: `020-fonte-unica-e-hooks` · Data: `2026-07-01`
> Objetivo: roteiro executável para validar a feature pela primeira vez, à mão, além da suíte automatizada.
> Convenções: `UPSTREAM=~/dev/harness` (o repo-fonte); `SB=$(mktemp -d)` como sandbox descartável.

## Pré-requisitos

- Estar no `UPSTREAM` com o core buildado (`.harness/harness-core/.venv` presente).
- `git` disponível; nenhuma alteração fora do sandbox.

## Cenário A — `init` não cria venv nem copia o core

```bash
UPSTREAM=~/dev/harness
SB=$(mktemp -d)/proj && mkdir -p "$SB" && git -C "$SB" init -q
"$UPSTREAM/harness" init "$SB"          # ou: cd "$UPSTREAM" && ./harness init "$SB"
# Verificações:
test ! -d "$SB/.harness/harness-core" && echo "OK: sem core copiado"
test ! -d "$SB/.harness/harness-core/.venv" && echo "OK: sem venv"
test -x "$SB/harness" && echo "OK: shim executável presente"
grep -q "upstream_path" "$SB/harness.toml" && echo "OK: upstream_path gravado"
grep -q "^version" "$SB/harness.toml" && echo "FALHA: version ainda presente" || echo "OK: sem version"
du -sh "$SB" # esperado: kilobytes, não ~108 MB
```

## Cenário B — o shim executa o core do upstream com o cwd do projeto

```bash
cd "$SB"
./harness cmd resume        # deve rodar sem erro, lendo o .harness/ deste projeto
./harness decisions         # valida o grafo de decisões DESTE projeto (vazio → OK)
# Confirmar que usou o python do upstream:
head -20 ./harness | grep -q "upstream" && echo "OK: shim aponta para o upstream"
```

## Cenário C — falha barulhenta sem o core do upstream

```bash
cd "$SB"
cp harness.toml harness.toml.bak
sed -i '' 's#upstream_path = ".*"#upstream_path = "/caminho/inexistente"#' harness.toml
./harness cmd resume ; echo "exit=$?"   # esperado: stderr com erro nomeado + exit != 0
mv harness.toml.bak harness.toml
```

## Cenário D — merge do `settings.json` preserva hook próprio no mesmo evento

```bash
cd "$SB"
mkdir -p .claude
cat > .claude/settings.json <<'JSON'
{
  "model": "opus",
  "hooks": {
    "PostToolUse": [
      { "matcher": "Write", "hooks": [ { "type": "command", "command": "meu-linter.sh" } ] }
    ],
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [ { "type": "command", "command": "meu-guard.sh" } ] }
    ]
  }
}
JSON
./harness materialize
# Verificações:
grep -q "meu-linter.sh" .claude/settings.json && echo "OK: hook próprio de PostToolUse preservado"
grep -q "meu-guard.sh"  .claude/settings.json && echo "OK: PreToolUse (evento alheio) preservado"
grep -q "harness format" .claude/settings.json && echo "OK: hook do harness adicionado ao mesmo array"
grep -q '"model": "opus"' .claude/settings.json && echo "OK: chave de topo preservada"
```

## Cenário E — `install_hooks` preserva `pre-commit` alheio

```bash
cd "$SB"
printf '#!/bin/bash\necho meu-pre-commit\n' > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
./harness bootstrap
# Verificações:
test -f .git/hooks/pre-commit.local && grep -q "meu-pre-commit" .git/hooks/pre-commit.local \
  && echo "OK: pre-commit alheio preservado em .local (encadeado)"
grep -q "harness" .git/hooks/pre-commit && echo "OK: hook do harness ativo via shim"
```

## Cenário F — `harness migrate` num projeto de teste

```bash
# Simular uma instalação no layout ANTIGO (core copiado + venv):
OLD=$(mktemp -d)/legado && mkdir -p "$OLD" && git -C "$OLD" init -q
# (usar uma build antiga do init OU copiar manualmente um .harness/harness-core para simular)
cd "$OLD"
./harness migrate --dry-run     # relata espaço a liberar e hooks a preservar, sem escrever
./harness migrate               # executa
test ! -d .harness/harness-core && echo "OK: core removido"
test -x harness && echo "OK: shim instalado"
# Estado preservado:
ls .harness/decisoes >/dev/null 2>&1 && echo "OK: decisões preservadas"
```

## Limpeza

```bash
rm -rf "$SB" "$OLD"    # sandboxes descartáveis; nada fora deles foi tocado
```

## Critério de aprovação manual

Todos os `OK:` acima impressos; nenhum `FALHA:`; `du -sh` do Cenário A na casa dos KB; Cenário C com exit ≠ 0 e mensagem clara.
