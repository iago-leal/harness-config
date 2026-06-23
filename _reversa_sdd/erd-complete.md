# Modelo de Entidades e Relacionamentos (ERD) — harness-core

> Gerado pelo Architect em 2026-06-23
> Nível de Documentação: **Completo**

Este documento apresenta o modelo relacional lógico das entidades persistidas e conceituais do `harness-core`.

---

```mermaid
erDiagram
    %% Entidades Físicas
    SESSION_STATE {
        string active_feature PK "Kebab-case ID da feature"
        string commit_hash "Hash SHA-1 do commit âncora"
        datetime start_time "Timestamp ISO 8601 de início"
        string status "Status: active / inactive"
    }

    SYNC_CACHE {
        string commit_hash PK "SHA-1 remoto detectado"
        datetime last_checked_time "Timestamp ISO 8601 do check"
    }

    %% Entidades Conceituais (Markdown Front-matter)
    DECISION {
        string id PK "MD-NNNN ID único"
        string gancho "Gatilho de ciclo de vida associado"
        string status "Vigência: ativo, em-revisao, rejeitado"
        string filepath "Caminho do arquivo MD"
    }

    RELATIONSHIP {
        string rel_type "Tipo de relação: refina, depende-de, substitui"
        string target_id FK "ID da microdecisão de destino"
    }

    %% Relacionamentos do Grafo de Decisões
    DECISION ||--o{ RELATIONSHIP : "contém"
    RELATIONSHIP }o--|| DECISION : "aponta-para"
```

---

## 📖 Descrição das Relações

1. **Relação de Grafo de Decisões:**
   - Uma **`DECISION`** (Microdecisão) pode conter zero ou mais **`RELATIONSHIP`** (Arestas de relações) declaradas em seu Front-matter.
   - Cada **`RELATIONSHIP`** aponta para outra **`DECISION`** por meio do seu ID único (target_id). A consistência destas referências é validada pelo `DecisionService`, reportando referências órfãs caso o ID destino não exista fisicamente em disco.
2. **Isolamento de Cache e Sessão:**
   - As entidades **`SESSION_STATE`** e **`SYNC_CACHE`** operam de forma isolada, servindo puramente de controle de infraestrutura local do projeto.
