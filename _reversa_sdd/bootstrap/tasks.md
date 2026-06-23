# Bootstrap, Tarefas de Implementação

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [bootstrap.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/bootstrap.sh)

## Pré-requisitos
* [ ] Acesso aos binários do shell do host.
* [ ] Permissões de escrita na pasta `.git/hooks/` do repositório.

---

## Tarefas

- [ ] **T-01: Inicialização do Script e Resolução de Raiz**
  * Origem no legado: `bin/bootstrap.sh:1-15`
  * Critério de pronto: O script deve inicializar com diretivas robustas (`set -uo pipefail`) e encontrar o caminho absoluto do repositório do projeto.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-02: Integração com Scripts de Pré-requisitos**
  * Origem no legado: `bin/bootstrap.sh:20-35`
  * Critério de pronto: Invocar `verify-prerequisites.sh` e abortar a execução do bootstrap caso o retorno de validação falhe.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-03: Instalação física dos Ganchos Git**
  * Origem no legado: `bin/bootstrap.sh:40-75`
  * Critério de pronto: Mapear e copiar os scripts de hooks locais para a pasta `.git/hooks/` aplicando permissões executáveis (`+x`).
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-04: Acoplamento da Ponte de Memória Gemini**
  * Origem no legado: `bin/bootstrap.sh:76-96`
  * Critério de pronto: Garantir o mapeamento físico do diretório `~/.agent-memory/` configurado e injetado nos ganchos.
  * Confiança: 🟢 CONFIRMADO

---

## Tarefas de Teste

- [ ] **TT-01: Validação de Bootstrap em ambiente limpo**
  * Critério de pronto: Rodar o bootstrap em um repositório clonado do zero e verificar se todos os hooks foram criados e são funcionais no Git.
- [ ] **TT-02: Teste de Interrupção por Falha de Dependência**
  * Critério de pronto: Simular a ausência de uma ferramenta (como `jq`) e certificar que o script aborta retornando status `1`.
