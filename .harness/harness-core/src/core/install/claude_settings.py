"""Materialização do `.claude/settings.json` do Claude (feature 016, RN-05).

Rotina única, compartilhada por `init` e `upgrade`, que GARANTE de forma
idempotente a presença dos ganchos do harness (`SessionStart → cmd resume`,
`PostToolUse → format`, `Stop → decisions`) no `settings.json` do projeto-alvo,
preservando as demais chaves de topo e eventos de hook de terceiros. O conteúdo
canônico vem do `ClaudeProfile` (`hooks_block()`). Toda escrita ocorre sob
`project_path` (footprint global zero, RN-N17). Espelha o molde de
`antigravity_hooks.materialize_hooks_json`.

Antes da 016, este `settings.json` nunca era escrito automaticamente: o bloco de
ganchos do Claude só era emitido como texto colável no install-prompt, o que
deixava consumidores sem o `SessionStart → cmd resume` e, por isso, com a sessão
presa em `inactive`.
"""

import json
import os

from src.core.ports.fs import FileSystemPort
from src.core.install.harness_profiles import ClaudeProfile


def materialize_claude_settings(fs: FileSystemPort, project_path: str) -> None:
    """Grava (merge idempotente) os ganchos do harness em `<project_path>/.claude/settings.json`.

    Lê o `settings.json` existente se houver, garante os eventos de hook do
    harness e grava de forma atômica via `fs.write_file_atomic`, preservando
    quaisquer outras chaves de topo e eventos de terceiros.
    """
    harness_hooks = json.loads(ClaudeProfile().hooks_block())["hooks"]

    claude_dir = os.path.join(project_path, ".claude")
    settings_path = os.path.join(claude_dir, "settings.json")

    existing = _read_existing(fs, settings_path)
    hooks = existing.get("hooks")
    if not isinstance(hooks, dict):
        hooks = {}
    # Merge POR-ITEM (feature 020, RN-06): para cada evento gerenciado pelo
    # harness, substitui/insere apenas o ITEM do harness dentro do array,
    # preservando os itens próprios do usuário no mesmo evento — além dos
    # eventos de terceiros (ex.: PreToolUse) e das demais chaves de topo
    # (model, theme, permissions…), já intocados. Antes da 020, `hooks[event] =
    # value` trocava o array inteiro e descartava hooks do usuário no evento.
    for event, harness_items in harness_hooks.items():
        arr = hooks.get(event)
        if not isinstance(arr, list):
            arr = []
        for h_item in harness_items:
            sig = _item_harness_signature(h_item)
            for i, existing_item in enumerate(arr):
                if _item_harness_signature(existing_item) == sig:
                    arr[i] = h_item
                    break
            else:
                arr.append(h_item)
        hooks[event] = arr
    existing["hooks"] = hooks

    fs.makedirs(claude_dir)
    fs.write_file_atomic(
        settings_path, json.dumps(existing, indent=2, ensure_ascii=False) + "\n"
    )


# Assinaturas estáveis que identificam um item de hook como sendo do harness:
# a substring do subcomando no `command` (resistente ao prefixo
# ${CLAUDE_PROJECT_DIR}/harness …). Um item alheio não contém nenhuma delas.
_HARNESS_COMMAND_SIGNATURES = (
    "harness cmd resume",
    "harness format",
    "harness decisions",
)


def _item_harness_signature(item):
    """Retorna a assinatura do harness contida no `command` do item, ou None.

    Percorre os comandos aninhados em ``item["hooks"][*]["command"]`` e devolve
    a primeira assinatura conhecida encontrada. Itens do usuário devolvem None,
    de modo que nunca casam com o item do harness no merge por-item.
    """
    if not isinstance(item, dict):
        return None
    for hook in item.get("hooks", []):
        if not isinstance(hook, dict):
            continue
        command = hook.get("command", "")
        for sig in _HARNESS_COMMAND_SIGNATURES:
            if sig in command:
                return sig
    return None


def _read_existing(fs: FileSystemPort, settings_path: str) -> dict:
    """Lê o `settings.json` atual se existir e for JSON válido; senão, dict vazio."""
    if not fs.exists(settings_path):
        return {}
    raw = fs.read_file(settings_path)
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
