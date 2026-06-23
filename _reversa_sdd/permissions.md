# Matriz de Permissões (Permissions) — harness-core

> Gerado pelo Detective em 2026-06-23
> Nível de Documentação: **Completo**

Este documento detalha o controle de privilégios de execução no `harness-core`. Embora o sistema seja monousuário local, a divisão reside entre as automações automatizadas do agente de IA (Hooks) versus a intervenção manual do Desenvolvedor Humano.

---

## 🔑 1. Atores do Sistema

* **Desenvolvedor Humano (iago):** Mantenedor único do projeto. Executa ações com privilégios administrativos e intervenção direta via CLI.
* **Agente de IA (Antigravity/Claude):** Assistente rodando no host. Executa automações em sub-shells sob ganchos do ciclo de vida, sem permissão para quebrar o sistema.

---

## 📊 2. Matriz de Permissões

A tabela a seguir consolida as operações permitidas por tipo de ator no projeto:

| Operação | Descrição | Agente de IA | Desenvolvedor Humano | Confiança |
| :--- | :--- | :---: | :---: | :--- |
| **bootstrap** | Instalar ou atualizar hooks locais Git (`.git/hooks/`). | ❌ Negado | 🟢 Permitido | 🟢 CONFIRMADO |
| **format** | Formatar e padronizar arquivos editados. | 🟢 Permitido | 🟢 Permitido | 🟢 CONFIRMADO |
| **decisions** | Validar e atualizar o grafo de microdecisões. | 🟢 Permitido | 🟢 Permitido | 🟢 CONFIRMADO |
| **cmd resume** | Retomar sessão de trabalho de uma feature. | 🟢 Permitido | 🟢 Permitido | 🟢 CONFIRMADO |
| **cmd encerrar-sessao** | Fechar sessão ativa gravando a âncora Git. | 🟢 Permitido | 🟢 Permitido | 🟢 CONFIRMADO |
| **cmd handoff** | Gerar dados do bastão de handoff. | 🟢 Permitido | 🟢 Permitido | 🟢 CONFIRMADO |
| **Paralelismo (Shadow)** | Configurar execução paralela (Shadow Mode). | ❌ Negado | 🟢 Permitido | 🟢 CONFIRMADO |
