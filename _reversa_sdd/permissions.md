# Matriz de Permissões e Papéis (Permissions) — harness

> Gerado pelo Detetive em 2026-06-23
> Nível de Documentação: **Completo**

Este documento detalha os papéis operacionais, matriz de permissões (ACL) e restrições de escrita/execução que regem as interações entre o desenvolvedor Humano e os Agentes de IA no ambiente `harness-config`.

---

## 👥 1. Definição de Papéis

* **Humano (Owner/Revisor):** O desenvolvedor responsável por validar decisões arquiteturais, autorizar o envio de código para o repositório remoto, aprovar planos complexos e arbitrar em dúvidas e conflitos.
* **Claude Code (Agente Principal):** Agente primário de desenvolvimento interativo de software. Possui permissão de edição e execução de ferramentas dentro do sandbox.
* **Gemini CLI / Antigravity (Agente de Descoberta/Migração):** Agente de engenharia reversa e orquestração de migrações estruturais do Reversa.

---

## 📊 2. Matriz de Permissões (ACL)

A tabela abaixo define as ações permitidas por papel dentro do ambiente do repositório:

| Ação / Operação | Humano | Claude Code | Gemini CLI | Condição / Regra de Negócio |
| :--- | :---: | :---: | :---: | :--- |
| **Criar/Aprovar Microdecisões (`decisoes/`)** | **Sim** | **Proposta** | **Proposta** | O agente pode propor fichas no estado `em_revisao`. A aprovação final (estado `aceito`) é exclusiva do Humano. |
| **Modificar Scripts e Hooks (`bin/`, `hooks/`)** | **Sim** | **Sim** | **Não** | Claude Code altera scripts para evolução do ambiente. Gemini/Reversa atua apenas em modo leitura sobre o código legado. |
| **Commit Automático de Estado** | **Sim** | **Sim** | **Não** | Claude Code cria commits atômicos de progresso ao rodar `/encerrar-sessao`. |
| **Git Push (Remote Origin)** | **Sim** | **Interativo** | **Não** | O agente de IA deve obrigatoriamente solicitar aprovação humana antes de executar `git push`. |
| **Executar Formatação (`format-on-edit.sh`)** | **Sim** | **Automático** | **Não** | Disparado automaticamente no Claude Code via hook `PostToolUse` após gravação de arquivos. |
| **Leitura de Caches de Sincronia** | **Sim** | **Sim** | **Sim** | Acesso irrestrito a `$HOME/.claude/.sync-check/*` para avaliar status de ramificações. |
| **Bypass de Sandbox de Comandos** | **Sim** | **Interativo** | **Interativo** | Requer consentimento expresso do desenvolvedor Humano na interface CLI. |

---

## 🛑 3. Restrições e Regras de Segurança

* **Isolamento de Diretório:** O agente de IA não possui permissão para aplicar ganchos ou formatar arquivos fora do escopo de um projeto de software válido (opt-out local via `.no-autoformat` é sempre respeitado).
* **Bloqueio de Commits Inconsistentes:** A execução de commits que modifiquem microdecisões sem a compilação do índice `microdecisoes.md` é travada de forma automática pelo hook de pre-commit instalado no ambiente de desenvolvimento.
