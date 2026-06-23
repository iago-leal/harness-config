# Microdecisões, Tarefas de Implementação

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [decisoes/](file:///Users/iagoleal/dev/harness/harness-config/decisoes/) e [gerar-index-decisoes.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/gerar-index-decisoes.sh)

## Pré-requisitos
* [ ] Permissões de escrita e alteração do arquivo `microdecisoes.md` na raiz do projeto.
* [ ] Parser awk/sed mapeado e disponível no host.

---

## Tarefas

- [ ] **T-01: Algoritmo de Varredura e Parser de Metadados**
  * Origem no legado: `bin/gerar-index-decisoes.sh` (bloco de loop inicial)
  * Critério de pronto: Localizar arquivos de decisões sequenciais em `decisoes/` e realizar parse robusto extraindo ID, título, gancho e relações, emitindo erro em caso de relações malformadas.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-02: Implementação da Inversão de Grafo (Backlinks)**
  * Origem no legado: `bin/gerar-index-decisoes.sh` (processamento awk)
  * Critério de pronto: Computar corretamente as relações inversas e injetá-las na ficha correspondente da decisão de destino sob a formatação hierárquica.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-03: Geração do Markdown Consolidado**
  * Origem no legado: `bin/gerar-index-decisoes.sh` (bloco de escrita final)
  * Critério de pronto: Escrever a tabela navegável e os blocos de grafo a partir do cabeçalho canônico `decisoes/_cabecalho.md`.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-04: Implementação da Flag de Validação Passiva (`--check`)**
  * Origem no legado: `bin/gerar-index-decisoes.sh:40`
  * Critério de pronto: Executar em modo comparativo sem reescrever arquivos, finalizando com status `1` se houver divergências.
  * Confiança: 🟢 CONFIRMADO

---

## Tarefas de Teste

- [ ] **TT-01: Validação de Inversão de Relações**
  * Critério de pronto: Criar duas microdecisões mock com relações de refina/depende e atestar que a compilação do índice exibe as referências reversas na ordem esperada.
- [ ] **TT-02: Teste de Interpolação de Metadados Inválidos**
  * Critério de pronto: Inserir relação malformada com 3 tokens em um arquivo e verificar se o compilador aborta exibindo o erro em `stderr`.
