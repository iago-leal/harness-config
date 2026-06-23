# Análise Técnica Consolidada (Code Analysis) — harness

> Gerado pelo Archaeologist em 2026-06-23
> Nível de Documentação: **Completo**

Este documento apresenta a análise técnica detalhada dos módulos que compõem o projeto `harness` (infraestrutura e ganchos de configuração do ambiente de desenvolvimento `harness-config`).

---

## 🗺️ 1. Visão Geral dos Módulos

O projeto é estruturado em quatro módulos técnicos principais voltados para automação, padronização, tomadas de decisão e gerenciamento de estado de sessões de agentes.

```mermaid
graph TD
    subgraph harness-config [Estrutura do Harness]
        M_bin[bin] --> |Scripts de Automação & Grafo| M_decisoes[decisoes]
        M_commands[commands] --> |Slash Commands & Ciclos| M_bin
        M_hooks[hooks] --> |PostToolUse Formatters| harness-config
    end
```

---

## 📦 2. Detalhamento Técnico por Módulo

### ⚙️ 2.1 Módulo `bin` (Automação e Inicialização)
* **Propósito:** Scripts responsáveis por inicializar o ambiente, sincronizar repositórios de agentes, validar e compilar índices de microdecisões de design.
* **Componentes Principais:**
  * `bin/bootstrap.sh` — Inicializador de ambiente. Configura os ganchos locais e valida dependências.
  * `bin/sync-check.sh` — Verifica a sincronia de repositórios de memória compartilhada.
  * `bin/gerar-index-decisoes.sh` — Compila microdecisões no arquivo `microdecisoes.md` resolvendo backlinks.
  * `bin/test_sync_check.sh` — Testes automatizados da lógica de sincronia.
* **Algoritmos Identificados:**
  * **Graph Inversion (Inversão de Grafo):** Algoritmo presente no `gerar-index-decisoes.sh` que lê os arquivos `MD-*.md`, rastreia as relações declaradas (`refina`, `depende-de`, `substitui`, `relaciona`) e gera o mapeamento inverso correspondente (`refinado-por`, `dependência-de`, `substituído-por`, etc.) gerando uma visualização bidirecional do grafo de decisões.
* **Complexidade:** Média (devido à manipulação de strings e processamento de grafos no shell).
* **Confiança:** 🟢 CONFIRMADO

### 💬 2.2 Módulo `commands` (Slash Commands dos Agentes)
* **Propósito:** Define o comportamento e os contratos dos comandos de barra executados pelas IAs no ambiente (Claude Code e Gemini CLI).
* **Componentes Principais:**
  * `commands/clarificar.md` — Instruções para clarificação de requisitos sob o protocolo PCCP.
  * `commands/encerrar-sessao.md` — Roteiro de finalização de sessão (commits pequenos, consolidação do estado do repositório, compilação de índices e reconciliação de ganchos).
  * `commands/handoff.md` & `commands/resume.md` — Protocolo de troca e retomada de bastão de tarefas entre IAs via `~/.agent-memory/BASTAO.md`.
* **Complexidade:** Baixa.
* **Confiança:** 🟢 CONFIRMADO

### 📂 2.3 Módulo `decisoes` (Microdecisões de Design)
* **Propósito:** Armazenamento distribuído e particionado de decisões de engenharia e arquitetura do projeto.
* **Componentes Principais:**
  * `decisoes/_cabecalho.md` — Cabeçalho descritivo do índice de decisões.
  * `decisoes/MD-0001.md` a `decisoes/MD-0017.md` — Fichas de decisões de design individuais e histórico de alterações.
* **Estrutura de Dados:**
  * Cada arquivo segue o formato estruturado: H1 com ID/Título, metadados (gancho de ativação e relações com outras decisões), e bloco de conteúdo semântico (`D: decisão`, `PORQUÊ: justificativa`, `DESCARTADO: alternativas consideradas`, `ESTADO: aceito/rejeitado`).
* **Complexidade:** Baixa.
* **Confiança:** 🟢 CONFIRMADO

### 🎨 2.4 Módulo `hooks` (Ganchos de Formatação Automática)
* **Propósito:** Executa rotinas automáticas de formatação e linting imediatamente após a escrita ou modificação de arquivos por agentes de IA.
* **Componentes Principais:**
  * `hooks/format-on-edit.sh` — Roteador principal disparado por hooks do editor.
  * `hooks/README.md` — Documentação de instalação e salvaguardas.
* **Algoritmos Identificados:**
  * **Manifest-based Recursive Root Detection:** Sobe recursivamente a árvore de diretórios procurando por manifestos estruturais (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.) para classificar a pasta do arquivo modificado como pertencente a um projeto de software válido.
* **Complexidade:** Média (gerenciamento estrito de subprocessos, resolução de caminhos locais/globais e concorrência).
* **Confiança:** 🟢 CONFIRMADO

---

## 🛡️ 3. Regras de Negócio Cruciais do Sistema

A tabela abaixo compila as principais restrições e regras de negócio codificadas no sistema legado:

| Módulo | Regra de Negócio / Comportamento Esperado | Código/Arquivo de Origem | Confiança |
| :--- | :--- | :--- | :--- |
| **bin** | **Cache TTL no Sync-Check:** Evita requisições redundantes guardando o resultado da verificação de repositórios remotos em cache local por 24 horas. | [sync-check.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh#L20) | 🟢 CONFIRMADO |
| **bin** | **Bloqueio de Commits Manuais com Índices Defasados:** Impede a execução de commits se o índice de microdecisões estiver inconsistente com os arquivos Markdown físicos. | [bootstrap.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/bootstrap.sh#L53) | 🟢 CONFIRMADO |
| **commands** | **Limite de Clarificação PCCP:** Limita a 2 rodadas de perguntas e respostas para evitar loops e paralisia de análise (PCCP). | [clarificar.md](file:///Users/iagoleal/dev/harness/harness-config/commands/clarificar.md#L39) | 🟢 CONFIRMADO |
| **commands** | **Isolamento de Estado:** Limita as operações de finalização de sessão exclusivamente à árvore do repositório ativo para evitar vazamento ou contaminação de sessões paralelas. | [encerrar-sessao.md](file:///Users/iagoleal/dev/harness/harness-config/commands/encerrar-sessao.md#L11) | 🟢 CONFIRMADO |
| **hooks** | **Não-bloqueio:** O script de formatação deve sempre encerrar com código `0`, assegurando que problemas nos formatadores nunca causem pane ou bloqueiem as tarefas de gravação da IA. | [format-on-edit.sh](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh#L14) | 🟢 CONFIRMADO |
| **hooks** | **Proteção de Diretórios Críticos:** O script aborta instantaneamente e não altera arquivos se detectado que o arquivo modificado reside no `$HOME`, em diretórios de configuração (`~/.claude`) ou notas Obsidian (`~/Notas`). | [format-on-edit.sh](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh#L38) | 🟢 CONFIRMADO |
| **hooks** | **Preferência Local:** Executa binários do projeto (ex: `.venv/bin/ruff`, `node_modules/.bin/prettier`) de forma preferencial sobre binários globais para manter compatibilidade com as ferramentas de cada projeto. | [format-on-edit.sh](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh#L119) | 🟢 CONFIRMADO |
| **hooks** | **Opt-out do Projeto:** Permite desativar a formatação automatizada se o arquivo `.no-autoformat` estiver presente na raiz do projeto. | [format-on-edit.sh](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh#L111) | 🟢 CONFIRMADO |
