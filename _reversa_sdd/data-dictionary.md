# Dicionário de Dados (Data Dictionary) — harness-core

> Gerado pelo Archaeologist em 2026-06-23 (Re-extração após Feature 002)
> Nível de Documentação: **Completo**

Este documento detalha o dicionário de dados e os modelos de domínio persistidos sob o repositório `harness`.

---

## 💾 1. Estado da Sessão (`SessionState`)

Persistido no arquivo Markdown `ESTADO-DA-SESSAO.md` na raiz do projeto local. Mapeia a integridade e a âncora da sessão atual do agente.

| Campo | Tipo | Obrigatoriedade | Descrição | Valor Padrão / Exemplo |
| :--- | :--- | :--- | :--- | :--- |
| **active_feature** | String | Obrigatório | Identificador em formato kebab-case da feature em andamento. | `001-run-harness-core-local` |
| **commit_hash** | String | Obrigatório | Hash SHA-1 de 40 caracteres do commit Git correspondente à âncora da sessão. | `b955e1742468cf5b2c7081702f2324bc01c0d56b` |
| **start_time** | DateTime | Obrigatório | Data e hora no formato ISO 8601 UTC de início da sessão do agente. | `2026-06-23T15:23:45.000000+00:00` |
| **status** | String | Obrigatório | Status atual da sessão do agente. Valores válidos: `active`, `inactive`. | `active` |

---

## 💾 2. Cache de Sincronia Git (`SyncCache`)

Persistido em formato JSON sob `$HOME/.claude/.sync-check` ou arquivo de cache configurado localmente. Evita chamadas Git redundantes.

| Campo | Tipo | Obrigatoriedade | Descrição | Exemplo |
| :--- | :--- | :--- | :--- | :--- |
| **last_checked_time** | DateTime | Obrigatório | Timestamp ISO 8601 UTC do último check Git `ls-remote`. | `2026-06-23T12:22:09+00:00` |
| **commit_hash** | String | Obrigatório | Hash SHA-1 do HEAD remoto detectado na última verificação. | `b955e1742468cf5b2c7081702f2324bc01c0d56b` |

---

## 💾 3. Microdecisão (`Decision`)

Entidade conceitual que mapeia o front-matter YAML de cada ficha `MD-*.md` em `decisoes/`.

| Campo | Tipo | Obrigatoriedade | Descrição | Exemplo |
| :--- | :--- | :--- | :--- | :--- |
| **id** | String | Obrigatório | ID identificador único no formato `MD-NNNN`. | `MD-0001` |
| **gancho** | String | Opcional | Descrição do evento que ativa a decisão (ex: pre-commit). | `SessionStart` |
| **estado** | String | Obrigatório | Estado de vigência da decisão. Valores: `ativo`, `em-revisao`, `rejeitado`. | `ativo` |
| **relacoes** | Array[String] | Opcional | Lista de arestas de relações com outras decisões no formato `"<verbo> <id_alvo>"`. | `["substitui MD-0002"]` |

---

## 💾 4. Dados Injetados de Documentação (`HARNESS_DOC_DATA`)

Estrutura JSON compilada em tempo de build pelo `DocumentationService` e injetada no script do `harness-docs.html` para exibição offline.

| Campo | Tipo | Obrigatoriedade | Descrição |
| :--- | :--- | :--- | :--- |
| **commands** | Array[Object] | Obrigatório | Lista dos comandos CLI do `harness-core` extraídos via introspecção. |
| **rules** | Array[Object] | Obrigatório | Lista de Regras de Negócio vigentes parseadas dos arquivos de domínio da extração reversa. |
| **state** | Object | Obrigatório | Estado completo e checkpoints da engenharia reversa lidos de `.reversa/state.json`. |
