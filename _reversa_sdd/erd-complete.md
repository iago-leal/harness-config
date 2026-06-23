# Entity Relationship Diagram (ERD) — harness-config

> Gerado pelo Architect em 2026-06-23
> Nível de Documentação: **Completo**

Este documento detalha o modelo de dados físico e lógico implícito mapeado nos arquivos de persistência do projeto `harness-config`.

---

```mermaid
erDiagram
    Microdecisao {
        string id PK "Formato MD-NNNN"
        string titulo "Título da decisão"
        string gancho "Gatilho de contexto"
        string decisao "Decisão técnica"
        string porque "Justificativa"
        string descartado "Alternativas descartadas"
        string estado "aceito | rejeitado | em_revisao"
    }

    Bastao {
        string objetivo "Objetivo da tarefa ativa"
        string estado_atual "Descrição de Fatos e Inferências"
        string decisoes_tomadas "Decisões de design tomadas"
        string proximos_passos "Fila de tarefas pendentes"
    }

    AncoraGit {
        string commit_hash PK "SHA-1 do commit de encerramento"
        string branch_name "Ramificação Git ativa"
        timestamp data_fechamento "Data de encerramento da sessão"
    }

    Microdecisao ||--o{ Microdecisao : "depende-de / refina / substitui"
    Bastao ||--o| AncoraGit : "referencia commit âncora"
```

---

## 📋 Descrição das Entidades e Atributos

1. **Microdecisao (`decisoes/MD-*.md`):**
   * **`id` (Chave Primária):** String incremental no formato `MD-NNNN`. Utilizada como referência estável de integridade nos backlinks do sistema.
   * **`relacoes` (Auto-relacionamento):** Uma microdecisão pode se relacionar com várias outras decisões históricas sob as chaves:
     * `depende-de`: Dependência técnica direta.
     * `refina`: Evolução ou detalhamento de uma escolha anterior.
     * `substitui`: Deprecia e anula uma decisão anterior (que passa ao estado `rejeitado`).
2. **Bastão de Handoff (`~/.agent-memory/BASTAO.md`):**
   * Contém as chaves funcionais para passagem de estado semântico entre sessões. É um arquivo de escrita destrutiva (sobrescrito a cada handoff).
3. **Âncora Git (`ESTADO-DA-SESSAO.md`):**
   * Armazena dados de commit do repositório físico do host. Utilizado na inicialização do agente para certificar que ele está atuando sobre a revisão correta, evitando regressão de código.
