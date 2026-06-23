# Sync-Check, Requisitos (Requirements)

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [sync-check.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh)

## Visão Geral
Verifica e sinaliza se os repositórios locais do ambiente de desenvolvimento estão atrasados em relação ao remote (origem) ou se possuem trabalho local não publicado (direção push), funcionando de forma read-only e não obstrutiva durante a inicialização de sessões de agentes.

## Responsabilidades
* Consultar de forma rápida (com cache local) a existência de novos commits no remote origin. 🟢
* Detectar commits locais não sincronizados (ahead) ou working tree sujo. 🟢
* Notificar o agente de desenvolvimento no formato JSON exigido para injeção de contexto adicional. 🟢

## Regras de Negócio
* **Cache TTL (Janela de Throttle):** A consulta à rede via `git ls-remote` é limitada a uma execução a cada 24 horas por repositório, gravando os dados brutos no cache local. 🟢 [sync-check.sh:20](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh#L20)
* **Read-only estrito:** O script não baixa nem altera objetos no repositório local. Nunca executa `git fetch` ou `git pull` de forma silenciosa. 🟢 [sync-check.sh:5](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh#L5)
* **Não-Bloqueante (Defensivo):** Erros em repositórios específicos ou falta de conexão à internet não podem interromper a execução do script; o status code de saída deve ser sempre `0`. 🟢 [sync-check.sh:14](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh#L14)

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
| :--- | :--- | :---: | :--- |
| **RF-01** | Checagem de repositórios desatualizados. | Must | Identificar se há commits mais recentes no remote origin comparando o hash local. |
| **RF-02** | Checagem de trabalho local pendente. | Must | Identificar se há commits locais à frente do remote (ahead) ou arquivos modificados sem commit. |
| **RF-03** | Controle de throttle de rede. | Must | Usar cache local em disco com expiração de 24h para pular chamadas a rede em sessões subsequentes. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
| :--- | :--- | :--- | :---: |
| Performance | Limite de tempo de execução (Timeout) de 8 segundos por chamada ls-remote. | `sync-check.sh:22` | 🟢 |
| Resiliência | Funcionamento tolerante a offline (se a rede falhar, assume no-op e termina com 0). | `sync-check.sh:66` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que o cache local do repositório foi atualizado há 10 minutos
Quando o sync-check for inicializado
Então ele deve carregar as informações do cache sem executar git ls-remote.

Dado que o host está offline e o cache expirou
Quando o sync-check tentar acessar o remoto
Então ele deve falhar silenciosamente no acesso à rede e retornar status de saída 0 sem exibir erros em stdout.
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
| :--- | :---: | :--- |
| Checagem de repositório defasado | Must | Evita divergências graves de código causadas por desenvolvimento sob branches desatualizados. |
| Controle de cache TTL | Must | Impede travamento do shell e gargalo de boot do agente. |
| Checagem de trabalho local pendente | Should | Importante para lembrar o desenvolvedor de fazer push do seu progresso. |
