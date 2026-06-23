# Modelo de Domínio e Glossário (Domain) — harness

> Gerado pelo Detetive em 2026-06-23
> Nível de Documentação: **Completo**

Este documento define a linguagem de domínio, o glossário semântico e as regras fundamentais que regem o comportamento e as restrições do projeto `harness`.

---

## 📖 1. Glossário de Domínio

### 🛡️ 1.1 Conceitos e Entidades Chave

* **Microdecisão:** Registro individualizado, atômico e estruturado de uma tomada de decisão arquitetural ou de design técnico. Substitui a terminologia genérica "ADR" no contexto do projeto para destacar seu escopo focado.
* **Bastão (Memória Compartilhada):** Mecanismo de sincronia física sob `~/.agent-memory/BASTAO.md` contendo o objetivo da tarefa, o estado atual das investigações, as decisões e os próximos passos. Usado no handoff entre IAs (Claude e Gemini).
* **PCCP (Problema-Causa-Consequência-Proposta):** Protocolo estruturado de clarificação de demandas que impede saltos causais e ambiguidades antes da fase de planejamento técnico de uma feature.
* **Âncora Git de Sessão:** Mecanismo de validação de consistência que grava a hash e ramificação Git do commit de fechamento da sessão no `ESTADO-DA-SESSAO.md`, impedindo regressão semântica se houver retomada da sessão sob uma ramificação ou revisão defasada.
* **Ponte Gemini-Claude:** Infraestrutura física de scripts e compartilhamento de estado estável configurada entre os ambientes do host local (Mac) e servidores remotos (VPS) para permitir portabilidade dos agentes de IA.
* **Hook PostToolUse:** Evento acionado pelo editor de desenvolvimento (Claude Code) imediatamente após a IA utilizar e concluir com sucesso uma ferramenta (como escrita ou edição de arquivos).
* **Cache de Sincronia (ls-remote cache):** Registro contendo timestamp e commit hash do remote origin mantido sob `$HOME/.claude/.sync-check` para evitar chamadas de rede redundantes a cada abertura de sessão.

---

## ⚡ 2. Regras de Domínio Fundamentais

### 🔄 2.1 Fluxo de Sincronização e Resiliência
* **Verificação Sincronizada em SessionStart:** A sincronia local e remota dos repositórios deve ser consultada a cada boot do agente de IA (através do hook local `SessionStart`).
* **Resiliência Offline:** O ambiente de boot do agente não deve falhar nem impedir a operação do usuário caso o host local esteja sem conexão à rede de computadores.
* **Garantia de Throttle (Janela TTL):** O acesso à rede para verificar se a base de código está atrás do remote deve ser restringido por um TTL padrão de 24 horas por repositório Git, evitando consumo de banda e lentidão de boot.

### ✍️ 2.2 Integridade e Salvaguarda de Arquivos
* **Garantia de Não-Bloqueio de Formatadores:** Hooks de pós-edição de arquivos (PostToolUse) devem sempre silenciar erros dos compiladores e retornar código de saída `0`, assegurando que tarefas de gravação nunca sejam abortadas.
* **Blindagem de Diretórios Pessoais:** Arquivos fora da árvore de um projeto de software válido (como Notas Obsidian no `$HOME/Notas` ou arquivos soltos no diretório raiz do usuário) **nunca** devem ser alterados ou padronizados de forma automatizada por ganchos do editor.

### 👥 2.3 Tomada de Decisão Compartilhada
* **Multiplicidade de Escolhas:** Qualquer processo que envolva a tomada de decisão estruturada compartilhada de design técnico exige a formulação de, no mínimo, 3 opções distintas de implementação, além de requerer um ponteiro sempre ativo e visível referenciando a alternativa selecionada.
* **Consolidação Automática no Fechamento:** Todo fechamento formal de sessão de trabalho (comando `/encerrar-sessao`) deve recalcular o grafo de backlinks e gerar a consolidação do índice de decisões de design.
