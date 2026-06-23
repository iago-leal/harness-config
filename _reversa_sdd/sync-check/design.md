# Sync-Check, Design Técnico

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [sync-check.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh)

## Interface

O script aceita passagem de caminhos como argumentos ou lê a configuração JSON no STDIN.

| Símbolo | Assinatura | Retorno | Observação |
| :--- | :--- | :--- | :--- |
| `sync-check.sh` | `./bin/sync-check.sh [repo1] [repo2] ...` | `JSON` no stdout (ou nada se ok) | Saída vazia indica que tudo está sincronizado. |

---

## Fluxo Principal
1. **Definição de Parâmetros e Cache:**
   * Mapeia caminhos de infraestrutura fixa (`~/.claude`, `~/.agent-memory`).
   * Configura local do cache de estado em `~/.claude/.sync-check/`.
2. **Leitura de Entrada:**
   * Se houver argumentos (`$# > 0`), checa apenas os caminhos informados (modo teste).
   * Caso contrário, lê payload JSON no stdin, extrai `.cwd` (diretório de trabalho atual) e adiciona os caminhos de infraestrutura à lista.
3. **Verificação de Sincronia Remota (`check_repo`):**
   * Obtém a branch HEAD atual do repositório local.
   * Se existir arquivo de cache válido dentro do TTL (24 horas), usa o hash remoto cacheado.
   * Se o cache estiver expirado ou ausente, faz consulta remota com timeout (`git ls-remote origin refs/heads/[branch]`) e atualiza o arquivo de cache local.
   * Se o hash remoto não existir localmente (`git cat-file -e`), marca o repositório como atrasado.
4. **Verificação de Trabalho Local (`check_local`):**
   * Mede alterações não commitadas (`git status --porcelain`) e commits locais à frente do remote (`git rev-list --count`).
5. **Formatação de Alertas:**
   * Consolida pendências e emite o payload JSON SessionStart na saída padrão (stdout).

---

## Dependências
* Interpretador `jq` — Usado para parse do stdin e formatação da saída do hook.
* Ferramenta `git` — Usada para consulta de metadados e hashes locais/remotos.

---

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
| :--- | :--- | :---: |
| Gravação de cache contendo `[timestamp] [commit_hash]` separados por espaço | `sync-check.sh:67` | 🟢 |
| Busca portátil de timeout utilizando `timeout` do GNU ou `gtimeout` do macOS | `sync-check.sh:29` | 🟢 |

---

## Estado Interno
* **Caches Locais:** Armazenados em arquivos individuais nomeados com o caminho higienizado do repositório, contendo a data da última consulta e o hash do remote.

---

## Observabilidade
* O script emite JSON estruturado se houver pendências de sincronização.
* Erros do git ls-remote são silenciados redirecionando `2>/dev/null` e tratados de forma segura.
