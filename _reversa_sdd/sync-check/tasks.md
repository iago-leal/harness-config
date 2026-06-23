# Sync-Check, Tarefas de Implementação

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [sync-check.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh)

## Pré-requisitos
* [ ] Permissões de escrita em `$HOME/.claude/` para criação de pastas de cache.
* [ ] Utilitário `jq` instalado no host de execução.

---

## Tarefas

- [ ] **T-01: Resolução de Timeout e Sanatização de Caminhos**
  * Origem no legado: `bin/sync-check.sh:25-45`
  * Critério de pronto: Identificar o utilitário de timeout portável no host e possuir função de higienização de strings para gerar nomes seguros de cache.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-02: Algoritmo de Verificação de Sincronia Remota**
  * Origem no legado: `bin/sync-check.sh:47-73`
  * Critério de pronto: Implementar o check por TTL de cache de hashes remoto e verificação de local commit com fallback offline silencioso.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-03: Algoritmo de Verificação de Commits não Enviados**
  * Origem no legado: `bin/sync-check.sh:75-95`
  * Critério de pronto: Calcular dirty-status do working tree e o contador de commits à frente da branch upstream do remote.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-04: Parse de JSON de Entrada e Formatação de Alerta**
  * Origem no legado: `bin/sync-check.sh:97-137`
  * Critério de pronto: Ler o stdin, deduplificar caminhos e formatar o payload JSON `SessionStart` contendo as pendências de sincronização na saída padrão.
  * Confiança: 🟢 CONFIRMADO

---

## Tarefas de Teste

- [ ] **TT-01: Executar suite de teste canônica**
  * Origem no legado: `bin/test_sync_check.sh`
  * Critério de pronto: Rodar os testes de fumaça de sync e verificar se todas as asserções de mock e cache passam com sucesso.
- [ ] **TT-02: Teste de Cache TTL**
  * Critério de pronto: Alterar a data do arquivo de cache simulando expiração e validar se o ls-remote é disparado de fato na próxima execução.
