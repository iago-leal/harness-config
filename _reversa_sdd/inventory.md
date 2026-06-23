# Inventário do Projeto — harness-config

> Gerado pelo Scout em 2026-06-23

Mapeamento da superfície de código e arquivos de configuração do diretório `harness-config`.

---

## 📊 Estatísticas Gerais

* **Diretório Alvo:** `/Users/iagoleal/dev/harness/harness-config`
* **Total de Arquivos:** 35
* **Linguagens Principais:**
  * **Markdown (`.md`)**: 28 arquivos (Documentação, Decisões, Comandos)
  * **Shell Script (`.sh`)**: 5 arquivos (Utilitários, Hooks, Testes)
  * **JSON (`.json`)**: 1 arquivo (Configurações)
  * **Outros (`.active`, `.gitignore`)**: 2 arquivos

---

## 📂 Estrutura de Diretórios e Arquivos

### 🛠️ Scripts e Utilitários (`bin/`)
* **`bin/bootstrap.sh`**: Script para reconstruir as dependências por-host e symlinks do Claude Code. Altamente idempotente.
* **`bin/sync-check.sh`**: Hook de inicialização (SessionStart) que verifica se os repositórios locais estão desatualizados em relação ao remote.
* **`bin/test_sync_check.sh`**: Suite de testes e validação isolada (smoke tests) para o `sync-check.sh`.
* **`bin/gerar-index-decisoes.sh`**: Script utilitário para compilar e atualizar o índice de microdecisões em `microdecisoes.md`.

### ⚙️ Configurações Gerais
* **`settings.json`**: Arquivo de configurações do Claude Code (regras de hooks, plugins habilitados, marketplaces de terceiros).
* **`skills.active`**: Manifesto contendo a lista de skills ativas a serem recriadas como symlinks pelo script de bootstrap.
* **`.gitignore`**: Configurado em modo whitelist para ignorar tudo por padrão e expor apenas arquivos de configuração seguros.

### 📋 Memória e Estado
* **`CLAUDE.md`**: Instruções globais de preferências, princípios operacionais (OOP, reprodutibilidade, proporções de rigor) e ganchos.
* **`microdecisoes.md`**: Índice gerado e validado contendo referências cruzadas das microdecisões do projeto.
* **`ESTADO-DA-SESSAO.md`**: Registro do estado atual da última sessão de trabalho para guiar a retomada de tarefas.

### 📥 Comandos Personalizados (`commands/`)
* **`commands/clarificar.md`**: Definição e contrato do comando `/clarificar` baseado em PCCP.
* **`commands/encerrar-sessao.md`**: Contrato do comando `/encerrar-sessao` para consolidar o estado e atualizar índices.
* **`commands/handoff.md`**: Comando para passar o bastão de tarefas para outro agente.
* **`commands/resume.md`**: Comando para retomar tarefas na sessão.

### 🧠 Decisões Arquiteturais (`decisoes/`)
* **`decisoes/_cabecalho.md`**: Cabeçalho padrão inserido no início do índice de decisões.
* **`decisoes/MD-0001.md`** a **`decisoes/MD-0017.md`**: Microdecisões numeradas cobrindo desde a modularização do repositório até hooks de pre-commit e regras de reprodutibilidade.

### 📖 Documentação Geral (`docs/`)
* **`docs/pccp.md`**: Guia metodológico para Clarificação Centrada no Problema.
* **`docs/reprodutibilidade.md`**: Regra de reprodução limpa sem depender do código de produção.

### ⚓ Ganchos de Ciclo de Vida (`hooks/`)
* **`hooks/README.md`**: Documentação explicativa sobre ganchos Git e Claude.
* **`hooks/format-on-edit.sh`**: Script para formatar e padronizar o código imediatamente após gravação/edição.
