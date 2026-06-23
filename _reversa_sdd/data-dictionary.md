# Dicionário de Dados (Data Dictionary) — harness

> Gerado pelo Archaeologist em 2026-06-23
> Nível de Documentação: **Completo**

Este documento cataloga de forma estruturada as entidades de dados, formatos de payload de comunicação (hooks), arquivos de cache e estruturas de estado persistentes encontradas e utilizadas no projeto.

---

## 🗂️ 1. Entidades de Domínio

### 📄 1.1 Microdecisão (`Microdecisao`)
* **Descrição:** Representa uma ficha física individual de decisão arquitetural ou de design que orienta a evolução do projeto.
* **Localização Física:** `decisoes/MD-NNNN.md` (formato Markdown).
* **Estrutura de Atributos:**

| Atributo | Tipo de Dado | Obrigatório | Descrição | Exemplo / Formato |
| :--- | :--- | :---: | :--- | :--- |
| **id** | Texto (String) | Sim | Identificador único estruturado, sequencial com 4 dígitos. | `MD-0005` |
| **título** | Texto (String) | Sim | Título da tomada de decisão. | `Estrutura de Pastas e Markdown` |
| **gancho** | Texto (String) | Sim | Gatilho ou contexto de aplicação em que a decisão é ativa. | `sempre` ou `reversa` |
| **relações** | Lista de Textos | Não | Relações explícitas com outros IDs de decisões de design. | `[ "depende-de MD-0001", "refina MD-0002" ]` |
| **decisão (D)** | Texto (String) | Sim | O conteúdo semântico da decisão de engenharia tomada. | *"Adotar markdown no formato..."* |
| **porque** | Texto (String) | Sim | Racional e justificativa por trás da decisão escolhida. | *"Garante legibilidade humana..."* |
| **descartado** | Texto (String) | Sim | Abordagens alternativas analisadas e descartadas. | *"Banco relacional puro..."* |
| **estado** | Texto (String) | Sim | Estado do ciclo de vida da decisão de design. | `aceito`, `rejeitado` ou `em_revisao` |

---

## 🔌 2. Contratos de Comunicação e Payloads (Hooks)

### 📥 2.1 Hook de Pós-Gravação (`format-on-edit.sh` - PostToolUse)

#### Entrada (STDIN)
JSON enviado automaticamente pelo Claude Code após executar ferramentas de escrita/edição de arquivos.
```json
{
  "tool_input": {
    "file_path": "/Users/iago/dev/harness/harness-config/hooks/format-on-edit.sh"
  },
  "tool_response": {
    "filePath": "/Users/iago/dev/harness/harness-config/hooks/format-on-edit.sh"
  }
}
```

#### Saída (STDOUT)
JSON opcional ecoado apenas se o formatador padronizar o arquivo e alterar seu conteúdo.
```json
{
  "systemMessage": "🎨 prettier padronizou hooks/format-on-edit.sh"
}
```

---

### 📥 2.2 Hook de Inicialização (`sync-check.sh` - SessionStart)

#### Entrada (STDIN)
JSON contendo o diretório de trabalho atual onde a sessão do agente foi disparada.
```json
{
  "cwd": "/Users/iago/dev/harness"
}
```

#### Saída (STDOUT)
JSON emitido se houver repositórios de infraestrutura física ou o projeto de trabalho atrasados ou com mudanças não enviadas ao remote.
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "⚠️ SYNC — pendências de sincronização. Avise o usuário e ofereça...\n- harness: remote tem commit novo — git pull\n"
  }
}
```

---

## 💾 3. Arquivos de Cache e Estado Persistente

### ⏱️ 3.1 Cache de Sincronia de Git (`.sync-check/<repo_sanitized>`)
* **Localização:** `$HOME/.claude/.sync-check/`
* **Formato:** Linha única contendo dados brutos em texto, delimitados por espaço.
* **Estrutura de Dados:**
  ```
  [unix_timestamp] [remote_git_commit_hash]
  ```
* **Descrição dos Campos:**
  * `unix_timestamp` (Epoch segundos): Data/hora em que a última consulta de rede ao remote (`git ls-remote`) foi executada. Utilizado para controle do TTL (throttle) de 24 horas.
  * `remote_git_commit_hash` (String hexadecimal): Commit hash SHA-1 mais recente na ramificação remota correspondente.

---

### ⚙️ 3.2 Estado e Metadados do Pipeline (`.reversa/state.json`)
* **Localização:** `.reversa/state.json`
* **Formato:** JSON estruturado.
* **Atributos Chave:**
  * `version` (String): Versão instalada do framework Reversa.
  * `project` (String): Nome do projeto sob análise.
  * `doc_level` (String): Nível de detalhamento da documentação (`essencial`, `completo`, `detalhado`).
  * `phase` (String): Fase atual do pipeline (`reconhecimento`, `escavacao`, `interpretacao`, `geracao`, `revisao`).
  * `completed` (Array de Strings): Fases que já foram finalizadas e homologadas.
  * `pending` (Array de Strings): Fases subsequentes do plano.
  * `checkpoints` (Objeto): Detalhamento do progresso dos agentes do Reversa (ex: módulos analisados e arquivos gerados pelo Scout e Archaeologist).
