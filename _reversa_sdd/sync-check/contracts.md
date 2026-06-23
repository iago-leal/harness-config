# Sync-Check, Contratos e Payloads (Contracts)

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [sync-check.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh)

Este documento define formalmente a interface de dados e os contratos de payloads JSON consumidos e produzidos pela unidade `sync-check`.

---

## 📥 1. Payload de Entrada (STDIN)

Disparado no ciclo de vida `SessionStart` do Claude Code. O script extrai o campo `.cwd` para mapear o diretório ativo do projeto.

### Schema Lógico
* **`cwd`** (Texto, Opcional): O caminho absoluto para o diretório de trabalho local ativo no editor.

### Exemplo de Entrada
```json
{
  "cwd": "/Users/iagoleal/dev/harness"
}
```

---

## 📤 2. Payload de Saída (STDOUT)

Ecoado apenas se houver pendências reais de sincronização (direções pull ou push) identificadas nos repositórios. Caso tudo esteja sincronizado, o stdout deve retornar vazio (zero bytes).

### Schema Lógico
* **`hookSpecificOutput`** (Objeto, Obrigatório): Contém a resposta do gancho.
  * **`hookEventName`** (Texto, Obrigatório): Identificador do evento. Valor estático: `SessionStart`.
  * **`additionalContext`** (Texto, Obrigatório): Bloco de texto legível de alerta direcionado ao agente contendo a listagem de pendências de sincronização.

### Exemplo de Saída
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "⚠️ SYNC — pendências de sincronização. Avise o usuário e ofereça a ação de cada item (git pull p/ atrasados; commit/push p/ trabalho local):\n- harness: remote tem commit novo — git pull\n- .agent-memory: 1 commit(s) não-pushado(s) — commit/push\n"
  }
}
```
