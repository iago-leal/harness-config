# Bootstrap, Requisitos (Requirements)

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [bootstrap.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/bootstrap.sh)

## Visão Geral
Inicializa e configura o ambiente de desenvolvimento local (`harness-config`) garantindo que todos os ganchos (hooks) do Git estejam instalados, dependências estejam resolvidas e o ambiente esteja consistente para operações seguras de desenvolvimento por humanos e agentes de IA.

## Responsabilidades
* Instalar ganchos do Git locais (`pre-commit`, `post-merge`) na pasta do repositório `.git/hooks/`. 🟢
* Validar a instalação e configuração de dependências necessárias no host de desenvolvimento. 🟢
* Sincronizar o repositório local com comandos e scripts customizados. 🟢

## Regras de Negócio
* **Sincronização Unificada de Hooks:** O processo de bootstrap deve configurar e sincronizar ganchos do git respeitando a diretiva `core.hooksPath` do Git local. 🟢 [bootstrap.sh:96](file:///Users/iagoleal/dev/harness/harness-config/bin/bootstrap.sh#L96)
* **Prevenção de Commits com Índice Defasado:** Impede a conclusão de commits manuais ou automatizados caso o compilador de microdecisões identifique alguma divergência física ou lógica de referências. 🟢 [bootstrap.sh:53](file:///Users/iagoleal/dev/harness/harness-config/bin/bootstrap.sh#L53)

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
| :--- | :--- | :---: | :--- |
| **RF-01** | Instalação de ganchos do Git. | Must | Ganchos `pre-commit` e `post-merge` devem estar presentes em `.git/hooks/` e executáveis (`+x`). |
| **RF-02** | Verificação de dependências locais do host. | Should | Rodar script de pré-requisitos (`verify-prerequisites.sh`) e emitir alertas caso ferramentas cruciais estejam ausentes. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
| :--- | :--- | :--- | :---: |
| Portabilidade | Portabilidade cross-machine entre macOS e Linux bash v3.2+. | `bootstrap.sh:1` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado um repositório git recém-clonado sem hooks locais instalados
Quando o desenvolvedor executar o script de bootstrap
Então os scripts pre-commit e post-merge devem ser vinculados à pasta .git/hooks/ e marcados como executáveis.

Dado um ambiente sem as dependências mínimas requeridas instaladas
Quando o script de bootstrap for executado
Então um alerta deve ser impresso em stdout detalhando quais ferramentas precisam ser configuradas manualmente.
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
| :--- | :---: | :--- |
| Instalação de ganchos do Git | Must | Garante a execução automática das rotinas de proteção de commit e sincronização. |
| Verificação de dependências | Should | Importante para evitar falhas silenciosas de formatação/sync posteriores. |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
| :--- | :--- | :---: |
| `bin/bootstrap.sh` | Lógica principal de bootstrapping | 🟢 |
| `bin/sync-check.sh` | Chamado indiretamente ou sincronizado | 🟢 |
