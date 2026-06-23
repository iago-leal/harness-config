# Fluxogramas do Módulo `hooks`

> Gerado pelo Archaeologist em 2026-06-23

Esta pasta contém a representação visual dos fluxos de execução do gancho de padronização em `hooks/`.

---

## 🎨 1. Roteador de Formatação Automática (`format-on-edit.sh`)

Fluxo disparado no evento `PostToolUse` (matchers `Write` e `Edit`) do Claude Code.

```mermaid
graph TD
    Start([Início]) --> ReadStdin[Ler payload JSON de STDIN]
    ReadStdin --> ExtractPath[Extrair file_path do JSON]
    ExtractPath --> ValidateFile{Arquivo existe e é válido?}
    
    ValidateFile -- Não --> EndExit[Sair com status 0]
    ValidateFile -- Sim --> NormalizePath[Resolver caminho absoluto do arquivo]
    
    NormalizePath --> CheckDeny{Está em DENY_PREFIXES?<br/>Ex: ~/Notas ou ~/.claude}
    CheckDeny -- Sim --> LogSkipDeny[Log: skip denylist] --> EndExit
    CheckDeny -- Não --> FindRoot[Buscar raiz do projeto - find_project_root]
    
    subgraph RootSearch [Busca por Manifesto]
        FindRoot --> LoopDir[Subir diretórios de forma recursiva]
        LoopDir --> NonRootCheck{Diretório em NON_ROOT_DIRS?<br/>Ex: ~, /, /Users}
        NonRootCheck -- Sim --> UpDir[Ignorar manifesto e subir nível]
        NonRootCheck -- Não --> MarkerCheck{Contém manifesto de build?<br/>Ex: package.json, pyproject.toml}
        MarkerCheck -- Sim --> SetRoot[Raiz encontrada: retornar diretório]
        MarkerCheck -- Não --> UpDir
        UpDir --> LoopDir
    end
    
    SetRoot --> CheckRoot{Raiz de projeto encontrada?}
    CheckRoot -- Não --> EndExit
    CheckRoot -- Sim --> CheckNoFormat{Existe .no-autoformat na raiz?}
    
    CheckNoFormat -- Sim --> LogSkipNoFmt[Log: skip .no-autoformat] --> EndExit
    CheckNoFormat -- Não --> ReadHash[Calcular hash inicial do arquivo - shasum]
    
    ReadHash --> DispatchExt{Extensão do arquivo?}
    
    DispatchExt -- "py / pyi" --> ResolveRuff[Resolver ruff: local .venv > global] --> RunRuff[Executar ruff format + ruff check --fix] --> CheckChange
    DispatchExt -- "js/ts/json/css/html/md/yaml" --> ResolvePrettier[Resolver prettier: local node_modules > global] --> RunPrettier[Executar prettier --write] --> CheckChange
    DispatchExt -- "rs" --> CheckRustfmt{rustfmt instalado?} -- Sim --> RunRustfmt[Executar rustfmt] --> CheckChange
    CheckRustfmt -- Não --> LogMissing[Log: ferramenta ausente] --> CheckChange
    DispatchExt -- "sh / bash" --> CheckShfmt{shfmt instalado?} -- Sim --> RunShfmt[Executar shfmt -w] --> CheckChange
    CheckShfmt -- Não --> LogMissing
    DispatchExt -- "Sem extensão" --> ShebangCheck{Shebang é sh/bash?} -- Sim --> CheckShfmt
    ShebangCheck -- Não --> CheckChange
    DispatchExt -- "Outros" --> CheckChange
    
    CheckChange[Calcular hash final do arquivo] --> HashCompare{Hash mudou?}
    HashCompare -- Não --> EndExit
    HashCompare -- Sim --> SystemMessage[Imprimir JSON systemMessage para Claude Code] --> EndExit
    
    EndExit --> End([Fim])
```
,Description:
