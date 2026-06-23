# Format-on-Edit, Contratos e Payloads (Contracts)

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [format-on-edit.sh](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh)

Este documento define formalmente a interface de dados e os contratos de payloads JSON consumidos e produzidos pela unidade `format-on-edit`.

---

## 📥 1. Payload de Entrada (STDIN)

Disparado no ciclo de vida `PostToolUse` (matchers `Write|Edit`) do Claude Code. O script extrai o caminho do arquivo utilizando fallbacks lógicos.

### Schema Lógico
* **`tool_input`** (Objeto, Opcional):
  * **`file_path`** (Texto, Opcional): O caminho absoluto ou relativo para o arquivo alterado.
* **`tool_response`** (Objeto, Opcional):
  * **`filePath`** (Texto, Opcional): Caminho alternativo do arquivo físico.

### Exemplo de Entrada (Formato tool_input)
```json
{
  "tool_input": {
    "file_path": "/Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh"
  }
}
```

### Exemplo de Entrada (Formato tool_response)
```json
{
  "tool_response": {
    "filePath": "/Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh"
  }
}
```

---

## 📤 2. Payload de Saída (STDOUT)

Ecoado apenas se o formatador padronizar o conteúdo do arquivo com sucesso resultando em alterações físicas no arquivo. Em caso de abortos de denylist ou se a formatação não alterar o conteúdo, o stdout deve retornar vazio.

### Schema Lógico
* **`systemMessage`** (Texto, Obrigatório): Notificação visual direcionada à IDE Claude Code informando qual ferramenta efetuou a alteração.

### Exemplo de Saída
```json
{
  "systemMessage": "🎨 prettier padronizou hooks/format-on-edit.sh"
}
```
