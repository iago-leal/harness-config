# Fluxogramas do Módulo `decisoes`

> Gerado pelo Archaeologist em 2026-06-23

Esta pasta contém a representação visual de como as microdecisões são particionadas e indexadas.

---

## 🏗️ 1. Estrutura e Relações de Microdecisões

Cada decisão em `decisoes/` representa um arquivo separado (`MD-NNNN.md`) estruturado de forma coesa:

```mermaid
graph TD
    File[MD-NNNN.md] --> Title[H1: # MD-NNNN — Título]
    File --> Meta[Metadados: Gancho e Relações]
    File --> Content[Conteúdo: D, PORQUÊ, DESCARTADO, ESTADO]
    
    Meta --> Relations{Relações definidas?}
    Relations -- Sim --> RelType[Verbo de Relação: depende-de, substitui, refina, relaciona]
    Relations -- Não --> Direct[Nenhuma relação direta]
```

---

## 📊 2. Compilação e Grafo de Backlinks (Passo 4.1 de /encerrar-sessao)

O script `gerar-index-decisoes.sh` faz o processamento reverso do grafo de relacionamentos:

```mermaid
graph TD
    Start([Início da Compilação]) --> ReadFiles[Ler todos os MD-*.md de decisoes/]
    ReadFiles --> Loop1[Para cada arquivo...]
    
    Loop1 --> Extract[Extrair Relações: Ex. 'refina MD-0002']
    Extract --> GraphBuilder[Adicionar aresta Direta: Origem -> Refina -> Destino]
    GraphBuilder --> NextFile1[Próximo arquivo]
    
    NextFile1 --> EndLoop1{Todos os arquivos processados?}
    EndLoop1 -- Sim --> BuildIndex[Montar microdecisoes.md]
    EndLoop1 -- Não --> Loop1
    
    BuildIndex --> Loop2[Varrer decisões ordenadas por ID]
    Loop2 --> WriteGancho[Escrever link + gancho no arquivo temporário]
    WriteGancho --> ResolveRelations[Identificar relações diretas e calcular backlinks inversos]
    
    ResolveRelations --> MapBacklinks[Ex: se A refina B, B ganha backlink 'refinado-por A']
    MapBacklinks --> WriteRelLine[Escrever linha de relacionamento ↳]
    WriteRelLine --> NextFile2[Próximo arquivo]
    
    NextFile2 --> EndLoop2{Todas as decisões indexadas?}
    EndLoop2 -- Sim --> Output[Gerar microdecisoes.md] --> End([Fim])
    EndLoop2 -- Não --> Loop2
```
