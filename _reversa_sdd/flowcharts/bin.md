# Fluxogramas do Módulo `bin`

> Gerado pelo Archaeologist em 2026-06-23

Esta pasta contém a representação visual dos fluxos de controle e lógicas dos scripts em `bin/`.

---

## 🚀 1. bootstrap.sh

Fluxo de inicialização e reconciliação de dependências por-host.

```mermaid
graph TD
    Start([Início]) --> Step1[Revisar Repositórios de Dependência]
    Step1 --> CloneCheck{agent-memory e skills existem?}
    CloneCheck -- Não --> Clone[git clone dos repositórios] --> SymlinkStep
    CloneCheck -- Sim --> SymlinkStep[Garantir permissões executáveis em bin/*]
    
    SymlinkStep --> GeminiCheck{~/.gemini existe?}
    GeminiCheck -- Sim --> GeminiBridge[Executar ensure-gemini-memory-bridge.py]
    GeminiBridge --> GeminiSync[Executar sync-claude-gemini-commands.py]
    GeminiSync --> GitHooks[Instalar Hooks post-merge e pre-commit unificados]
    GitHooks --> SymlinkActive
    GeminiCheck -- Não --> SymlinkActive[Ler skills.active e criar symlinks em ~/.claude/skills/]
    
    SymlinkActive --> CredCheck{~/.claude/.credentials.json existe?}
    CredCheck -- Não --> WarnCred[Emitir aviso: SEM credenciais] --> End([Fim])
    CredCheck -- Sim --> End
```

---

## 🔄 2. sync-check.sh

Fluxo de checagem de sincronização local/remota (Hook SessionStart).

```mermaid
graph TD
    Start([Início - Recebe repos via stdin ou args]) --> Loop[Para cada repositório...]
    Loop --> GitCheck{É repo git e tem HEAD?}
    
    GitCheck -- Sim --> CacheCheck{Cache existe e tempo < TTL?}
    GitCheck -- Não --> Next[Próximo repo]
    
    CacheCheck -- Sim --> UseCache[Ler hash remoto do Cache] --> CatFile
    CacheCheck -- Não --> NetFetch[Executar git ls-remote origin]
    NetFetch --> FetchSuccess{Conseguiu obter hash?}
    FetchSuccess -- Sim --> UpdateCache[Atualizar Cache local] --> CatFile[Verificar se hash remoto existe localmente]
    FetchSuccess -- Não --> Next
    
    CatFile -- Não (atrás) --> AddAlert[Adicionar alerta: remote tem commit novo] --> PushCheck
    CatFile -- Sim (atualizado) --> PushCheck{Verificar commits locais não-pushados ou alterados?}
    
    PushCheck -- Sim --> AddPushAlert[Adicionar alerta: commits pendentes de push/commit] --> Next
    PushCheck -- Não --> Next
    
    Next --> LoopEnd{Todos os repos checados?}
    LoopEnd -- Não --> Loop
    LoopEnd -- Sim --> AlertCheck{Existem alertas?}
    
    AlertCheck -- Sim --> OutputJSON[Emitir JSON com additionalContext] --> End([Fim])
    AlertCheck -- Não --> End
```

---

## 📝 3. gerar-index-decisoes.sh

Fluxo de compilação e verificação de integridade do índice de microdecisões.

```mermaid
graph TD
    Start([Início]) --> ModeCheck{Argumento --check passado?}
    ModeCheck -- Sim --> SetCheck[Definir CHECK_MODE = 1] --> ParseFiles
    ModeCheck -- Não --> SetCheckNormal[Definir CHECK_MODE = 0] --> ParseFiles
    
    ParseFiles[Varrer decisoes/MD-*.md] --> Loop1[Para cada arquivo de decisão...]
    Loop1 --> ExtractRelations[Extrair linha de Relações]
    ExtractRelations --> HasRelations{Possui relações?}
    
    HasRelations -- Sim --> SplitRelations[Separar por ';' e validar formato MD-NNNN]
    SplitRelations --> ValidateDest{Destino existe e é diferente do original?}
    ValidateDest -- Sim --> AddEdge[Adicionar à tabela temporária de arestas: Origem/Verbo/Destino] --> NextFile1
    ValidateDest -- Não (Erro) --> Abort[Abortar com erro barulhento]
    
    HasRelations -- Não --> NextFile1[Próximo arquivo]
    NextFile1 --> Loop1End{Todos os arquivos varridos?}
    
    Loop1End -- Não --> Loop
    Loop1End -- Sim --> InitTmp[Escrever preâmbulo _cabecalho.md no arquivo temporário]
    
    InitTmp --> Loop2[Para cada decisão ordenada...]
    Loop2 --> ExtractGancho[Extrair linha de Gancho]
    ExtractGancho --> HasGancho{Possui gancho?}
    HasGancho -- Não --> Abort
    HasGancho -- Sim --> WriteIndex[Escrever entrada formatada com link]
    WriteIndex --> QueryEdges[Consultar arestas diretas e backlinks inversos]
    QueryEdges --> WriteRelations[Escrever linha de setas de relacionamento ↳] --> NextFile2
    
    NextFile2 --> Loop2End{Todas as decisões indexadas?}
    Loop2End -- Não --> Loop2
    Loop2End -- Sim --> FinalCheck{CHECK_MODE == 1?}
    
    FinalCheck -- Sim --> CompareFiles{Arquivo temporário == microdecisoes.md?}
    CompareFiles -- Sim --> ReturnSuccess[Exibir sucesso] --> End([Fim])
    CompareFiles -- Não --> ReturnDrift[Exibir erro: drift detectado] --> Exit1[Sair com código 1]
    
    FinalCheck -- Não --> AtomicRename[Mover arquivo temporário para microdecisoes.md atômico] --> End
```
