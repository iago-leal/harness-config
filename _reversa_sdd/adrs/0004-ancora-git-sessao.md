# ADR 0004: Âncora de Commit de Sessão

* **Status:** Aceito (localização e formato superados pelo ADR 0010)
* **Data:** 2026-06-21
* **Contexto Técnico:** Módulo `commands` (`encerrar-sessao`)
* **Escala de Confiança:** 🟢 CONFIRMADO

> ⚠️ **Atualização (2026-06-24, feature 004):** a ideia da âncora de commit **permanece** (HEAD gravado no fechamento, validado na retomada). Mas o artefato deixou de ser `ESTADO-DA-SESSAO.md` na raiz / `.claude/`: hoje o estado vive em `.harness/estado-da-sessao.md`, com formato front-matter YAML + corpo narrativo (`SessionNarrative`) e round-trip pelo serializer. Ver **ADR 0010**. A "ramificação Git ativa" descrita abaixo **não** é persistida pelo modelo atual (`SessionState` guarda `commit_hash`, não o branch).

## Contexto e Problema

Quando agentes de IA trabalham de forma concorrente em diferentes ramificações ou alternam sessões de desenvolvimento com humanos, o estado dos arquivos abertos e o andamento da tarefa na última sessão podem se perder.

Sem um indicador confiável da revisão do Git no momento em que a sessão anterior foi concluída, a retomada da sessão pode ocorrer sob a revisão errada, fazendo com que o agente tome decisões de design inválidas ou repita passos já implementados.

## Decisão

Adotar uma **Âncora de Commit de Sessão** gravada automaticamente no encerramento de cada sessão de desenvolvimento pelo comando `/encerrar-sessao`.

A âncora é persistida no arquivo `ESTADO-DA-SESSAO.md` e contém:
1. O commit hash atual (HEAD) correspondente.
2. A ramificação Git ativa no encerramento.
3. Lista de modificações e contexto funcional da sessão que está sendo fechada.

Durante o boot de uma nova sessão ou inicialização do agente, a âncora é utilizada para validar a integridade da base local do host, detectando se houve desvios ou se a base está defasada em relação ao commit âncora documentado.

## Alternativas Consideradas

* **Rastreabilidade baseada em arquivos de log temporários:** Rejeitada porque arquivos fora do controle de versão são fáceis de corromper ou perder durante limpezas locais ou transições de hosts (como VPS/Mac).

## Consequências

* **Positivas:**
  * Rastreabilidade comportamental exata do estado final da sessão de desenvolvimento.
  * Facilidade de auditoria e menor ocorrência de regressão semântica ao retomar tarefas.
  * O arquivo `ESTADO-DA-SESSAO.md` versionado funciona como um contrato visual estável de handoff de sessão.
* **Negativas:**
  * Necessidade de commits adicionais para registrar as atualizações do `ESTADO-DA-SESSAO.md` ao final da sessão.
