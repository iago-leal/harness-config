# Fluxogramas (Flowcharts) — harness-core

> Gerado pelo Archaeologist em 2026-06-23 (Re-extração após Feature 002)
> Nível de Documentação: **Completo**

Este documento ilustra o fluxo de controle e os algoritmos dos principais sub-serviços do `harness-core`.

---

## 🔄 1. Fluxo de Formatação (`FormattingService.format_file`)

O diagrama abaixo descreve o algoritmo de formatação de arquivos, incluindo verificações de diretórios protegidos, detecção de opt-out recursivo e inibição de erros de compiladores.

```mermaid
graph TD
    Start([Início: format_file]) --> Resolve[Obter caminho absoluto do arquivo]
    Resolve --> CheckHome{Reside em pasta protegida?<br/>$HOME, Notas, .claude}
    
    CheckHome -- Sim --> ExitSuccess([Retorna 0 - Cancelado por Segurança])
    CheckHome -- Não --> SearchRoot[Subir árvore procurando .git ou harness.toml]
    
    SearchRoot --> CheckOptOut{Encontrou .no-autoformat<br/>em qualquer nível?}
    CheckOptOut -- Sim --> ExitSuccess
    CheckOptOut -- Não --> FindExt{Identificar extensão}
    
    FindExt -->|.py| SetRuff[Selecionar Ruff]
    FindExt -->|.js, .ts, .json, .css, .md| SetPrettier[Selecionar Prettier]
    FindExt -->|.rs| SetRustfmt[Selecionar Rustfmt]
    FindExt -->|Outra| ExitSuccess
    
    SetRuff --> CheckLocalRuff{Existe ruff local<br/>na .venv ou venv?}
    CheckLocalRuff -- Sim --> ExecLocalRuff[Executar ruff local]
    CheckLocalRuff -- Não --> ExecGlobalRuff[Executar ruff global]
    
    SetPrettier --> CheckLocalPrettier{Existe prettier local<br/>em node_modules?}
    CheckLocalPrettier -- Sim --> ExecLocalPrettier[Executar prettier local]
    CheckLocalPrettier -- Não --> ExecGlobalPrettier[Executar prettier global]
    
    SetRustfmt --> ExecRustfmt[Executar rustfmt global]
    
    ExecLocalRuff --> Finalize[Encerrar e capturar erro]
    ExecGlobalRuff --> Finalize
    ExecLocalPrettier --> Finalize
    ExecGlobalPrettier --> Finalize
    ExecRustfmt --> Finalize
    
    Finalize --> SafeReturn[Captura exceções e força exit code 0]
    SafeReturn --> End([Fim: Retorna 0])
```

---

## 🔄 2. Fluxo de Verificação de Sincronia (`SyncService.check_sync`)

Este diagrama mapeia a lógica de verificação resiliente de sincronia Git do repositório de memória compartilhada.

```mermaid
graph TD
    Start([Início: check_sync]) --> CheckCache{Existe cache local?}
    
    CheckCache -- Sim --> ParseCache[Ler timestamp e commit_hash]
    ParseCache --> CheckTTL{Timestamp dentro do TTL?<br/>24 horas}
    
    CheckTTL -- Sim --> VerifyHash{HEAD bate com o cache?}
    VerifyHash -- Sim --> ReturnTrue([Retorna True - Sincronizado])
    VerifyHash -- Não --> ReturnTrue
    
    CheckCache -- Não --> GitLS[Executar Git ls-remote remoto]
    CheckTTL -- Não --> GitLS
    
    GitLS --> Compare[Comparar HEAD local com o remote]
    Compare --> WriteCache[Atualizar cache local de forma atômica]
    WriteCache --> ReturnResult{Local == Remote?}
    
    ReturnResult -- Sim --> ReturnTrue
    ReturnResult -- Não --> ReturnFalse([Retorna False - Defasado])
    
    GitLS -. Falha de Rede .-> CatchError[Exibe aviso e prossegue]
    CatchError --> ReturnTrue
```

---

## 🔄 3. Geração de Documentação (`DocumentationService.generate_html`)

Este fluxograma ilustra o fluxo de geração do arquivo HTML standalone a partir do código do core e do estado do Reversa.

```mermaid
graph TD
    Start([Início: generate_html]) --> CheckTemplate{Existe template.html?}
    CheckTemplate -- Não --> RaiseError[Lança FileNotFoundError]
    
    CheckTemplate -- Sim --> ExtCLI[Introspecção do parser argparse da CLI]
    ExtCLI --> ParseRules[Parsear Regras de Negócio de domain.md via Regex]
    ParseRules --> LoadState[Carregar checkpoints do state.json]
    
    LoadState --> BuildJSON[Consolidar dados em dicionário HARNESS_DOC_DATA]
    BuildJSON --> ReadTemplate[Ler conteúdo do template.html]
    ReadTemplate --> InjectData[Substituir placeholder com o JSON serializado]
    
    InjectData --> WriteAtomic[Escrever harness-docs.html de forma atômica]
    WriteAtomic --> End([Fim: Documentação Gerada])
```
