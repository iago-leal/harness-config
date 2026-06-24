# Format-on-Edit (Formatting) — Contratos e Payloads (Contracts)

> Regenerado pelo Writer em 2026-06-24 (Re-extração pós-feature 008-reprodutibilidade-e-config)
> Interface de dados consumida/produzida pela unit no estado ATUAL (core Python). Escala: 🟢 / 🟡 / 🔴

> ⚠️ **Reescrita vs versão anterior:** no estado atual a formatação roda pela CLI Python (`./harness format`). O hook `PostToolUse` do Claude entrega o caminho do arquivo via stdin (JSON). **T3 (resolvido):** o parsing do stdin em `main.py` usa `json.loads` com `import json` presente (corrigido no commit `cf73980`). Ambos os caminhos — via stdin e por argumento posicional (`./harness format <arquivo>`) — funcionam sem falha.

---

## 📥 1. Entrada

### 1.1 Por argumento (caminho direto) 🟢

```
./harness format <caminho-do-arquivo>
```

O serviço `FormattingService.format_file(file_path)` recebe o caminho e formata.

### 1.2 Por stdin (hook `PostToolUse`) 🟢

Payload JSON entregue pelo Claude Code no evento `PostToolUse` (matchers `Write|Edit`):

```json
{
  "tool_input": {
    "file_path": "/Users/iagoleal/dev/harness/harness-core/src/main.py"
  }
}
```

O `main.py` extrai o `tool_input.file_path` via `json.loads`. A anterior falha T3 foi corrigida no commit `cf73980` ao adicionar o `import json`. O autoformat opera corretamente.

---

## 📤 2. Saída 🟢

`FormattingService.format_file` retorna **sempre `0`** (não-bloqueio, RN-03). Não há payload JSON de saída (`systemMessage`) nem log — comportamento do legado removido. O efeito observável é o arquivo formatado no disco, quando o formatador roda.

| Código de retorno | Significado                                                                    |
| ----------------- | ------------------------------------------------------------------------------ |
| `0`               | Sempre. Formatado, no-op por blindagem/opt-out/extensão, ou exceção capturada. |

---

## 🔌 3. Contrato com o adaptador de processo 🟢

`ProcessPort.execute_formatter(formatter, file_path, executable?) -> (exit_code, stdout, stderr)`. O serviço **ignora** o `exit_code` (não-bloqueio). Mapeamento em `HostFormatterAdapter`:

| Formatador | Comando                   |
| ---------- | ------------------------- |
| `ruff`     | `ruff format <file>`      |
| `prettier` | `prettier --write <file>` |
| `rustfmt`  | `rustfmt <file>`          |

Formatador ausente no host → `(127, "", <erro>)`, ignorado pelo serviço.
