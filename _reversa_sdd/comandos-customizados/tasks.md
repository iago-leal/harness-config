# Comandos Customizados, Tarefas de Implementação

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [commands/](file:///Users/iagoleal/dev/harness/harness-config/commands/)

## Pré-requisitos
* [ ] Permissões de escrita e commit de arquivos locais no Git.
* [ ] Acesso físico à pasta de memória compartilhada do host local (`~/.agent-memory/`).

---

## Tarefas

- [ ] **T-01: Definição e Mapeamento de Slash-Commands**
  * Origem no legado: `commands/`
  * Critério de pronto: Criar os arquivos markdown de definição de comandos sob a pasta e configurá-los em `settings.json`.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-02: Lógica de Processamento PCCP (/clarificar)**
  * Origem no legado: `commands/clarificar.md`
  * Critério de pronto: Implementar o fluxo interativo de separação de demanda, listagem F/I/H, limites de 2 rodadas e suporte ao comando `/travar`.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-03: Lógica de Consolidação de Sessões (/encerrar-sessao)**
  * Origem no legado: `commands/encerrar-sessao.md`
  * Critério de pronto: Implementar a rotina sequencial de ancoragem git, execução de commits, reindexação de decisões, sincronia de ganchos e prompt de push remoto.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-04: Sincronização e Handoff Semântico (/handoff e /resume)**
  * Origem no legado: `commands/handoff.md` e `commands/resume.md`
  * Critério de pronto: Integrar com a pasta física comum de memória compartilhada gravando e lendo payloads de controle em `BASTAO.md`.
  * Confiança: 🟢 CONFIRMADO

---

## Tarefas de Teste

- [ ] **TT-01: Validar fluxo do `/encerrar-sessao` localmente**
  * Critério de pronto: Executar o comando de fechamento em uma ramificação temporária e testar se as assinaturas de commits e a compilação do índice ocorrem em sequência.
- [ ] **TT-02: Validar o esgotamento de rodadas do `/clarificar`**
  * Critério de pronto: Simular duas iterações de perguntas e atestar que a IA adota a hipótese de lacuna mínima e força o avanço do ciclo operacional.
