#!/usr/bin/env bash
# @managed-by: /encerrar-sessao — não edite à mão (reconciliado automaticamente).
# Carrega o estado da última sessão DESTE projeto na nova sessão.
# Escopo estrito: o diretório do projeto. No-op silencioso se não houver estado.
set -euo pipefail
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
estado="$dir/.claude/ESTADO-DA-SESSAO.md"
[ -f "$estado" ] || exit 0
conteudo="$(cat "$estado")"
cabecalho="Estado da última sessão neste projeto (.claude/ESTADO-DA-SESSAO.md):"
# Âncora git: compara o HEAD atual com o commit que gravou este snapshot (o último
# a tocar o ESTADO). Se entraram commits depois, avisa que o registro pode estar
# defasado. Derivado de ground truth; nunca mente. Defensivo: no-op se git ausente,
# fora de repo, ou em qualquer erro — sempre entrega o estado.
ancora=""
if command -v git >/dev/null 2>&1 && git -C "$dir" rev-parse --git-dir >/dev/null 2>&1; then
  ref="$(git -C "$dir" log -1 --format=%H -- .claude/ESTADO-DA-SESSAO.md 2>/dev/null || true)"
  if [ -n "$ref" ]; then
    n="$(git -C "$dir" rev-list --count "$ref"..HEAD 2>/dev/null || true)"
    if [ -n "$n" ] && [ "$n" != "0" ]; then
      lista="$(git -C "$dir" log --oneline -n 20 "$ref"..HEAD 2>/dev/null || true)"
      ancora="$(printf '⚠ Âncora git: %s commit(s) entraram DEPOIS deste snapshot; o registro abaixo pode estar defasado — verifique (git log) antes de assumir o estado. Commits desde então:\n%s' "$n" "$lista")"
    fi
  fi
fi
if [ -n "$ancora" ]; then
  corpo="$(printf '%s\n\n%s\n\n%s' "$ancora" "$cabecalho" "$conteudo")"
else
  corpo="$(printf '%s\n\n%s' "$cabecalho" "$conteudo")"
fi
if command -v jq >/dev/null 2>&1; then
  jq -n --arg c "$corpo" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$c}}'
else
  printf '%s\n' "$corpo"
fi
