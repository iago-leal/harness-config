# C4 Component Diagram (Nível 3) — harness-core

> Gerado pelo Architect em 2026-06-23 (Re-extração após Feature 002)
> Nível de Documentação: **Completo**

Este diagrama detalha a estrutura de componentes e classes em `src/core/` e `src/adapters/` do `harness-core` sob Arquitetura Hexagonal.

---

```mermaid
graph TB
    subgraph core [Núcleo da Aplicação (src/core/)]
        subgraph ports [Portas (src/core/ports/)]
            FsPort["FileSystemPort<br/>[Interface]"]
            GitPort["GitPort<br/>[Interface]"]
            ProcPort["ProcessPort<br/>[Interface]"]
        end

        subgraph services [Serviços (src/core/services/)]
            BootServ["BootstrapService<br/>[Classe]<br/>Instala hooks Git."]
            FormatServ["FormattingService<br/>[Classe]<br/>Formata arquivos."]
            SyncServ["SyncService<br/>[Classe]<br/>Verifica sincronia."]
            DecServ["DecisionService<br/>[Classe]<br/>Processa microdecisões."]
            CmdServ["CommandService<br/>[Classe]<br/>Gere comandos de sessão."]
            DocServ["DocumentationService<br/>[Classe]<br/>Extrai dados e compila o HTML consolidado."]
        end
    end

    subgraph adapters [Adaptadores (src/adapters/)]
        FsAdap["LocalFileSystemAdapter<br/>[Classe]<br/>Implementa FileSystemPort."]
        GitAdap["SubprocessGitAdapter<br/>[Classe]<br/>Implementa GitPort."]
        FormatAdap["HostFormatterAdapter<br/>[Classe]<br/>Implementa ProcessPort."]
    end

    %% Injeção de dependências (Serviços usam Portas)
    BootServ -->|Usa| FsPort
    FormatServ -->|Usa| FsPort
    FormatServ -->|Usa| ProcPort
    SyncServ -->|Usa| FsPort
    SyncServ -->|Usa| GitPort
    DecServ -->|Usa| FsPort
    CmdServ -->|Usa| FsPort
    CmdServ -->|Usa| GitPort
    DocServ -->|Usa| FsPort

    %% Implementações (Adaptadores herdam/implementam Portas)
    FsAdap -.->|Implementa| FsPort
    GitAdap -.->|Implementa| GitPort
    FormatAdap -.->|Implementa| ProcPort
```

---

## 🛠️ Descrição das Camadas e Injeção

1. **Portas (Interfaces):**
   - **`FileSystemPort`:** Define os métodos de E/S em disco (exists, read_file, write_file_atomic, list_dir).
   - **`GitPort`:** Define as chamadas Git (`get_head_commit`, `get_remote_commit`).
   - **`ProcessPort`:** Define a execução de formatadores externos no shell.
2. **Adaptadores (Infraestrutura):**
   - Realizam as chamadas físicas do sistema (operações em disco reais, subprocessos de formatador Ruff/Prettier e Git CLI).
3. **Injeção de Portas nos Serviços:**
   - Cada serviço do núcleo (`FormattingService`, `SyncService`, `DocumentationService`, etc.) é instanciado na CLI (`main.py`) injetando as implementações reais de adaptadores correspondentes. Nos testes unitários do pytest, stubs são injetados para simular cenários de falha de disco e rede de forma controlada.
