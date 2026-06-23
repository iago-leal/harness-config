# Microdecisões, Requisitos (Requirements)

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [decisoes/](file:///Users/iagoleal/dev/harness/harness-config/decisoes/) e [gerar-index-decisoes.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/gerar-index-decisoes.sh)

## Visão Geral
Gerencia e consolida o histórico de decisões de arquitetura e design técnico de forma atômica e descentralizada, provendo um grafo navegável de backlinks para rastrear a evolução do projeto e otimizar o consumo de contexto dos agentes de IA.

## Responsabilidades
* Armazenar decisões técnicas em arquivos individuais de Markdown (`MD-NNNN.md`) contendo metadados explícitos. 🟢
* Compilar automaticamente a base de dados distribuída num arquivo de índice geral (`microdecisoes.md`). 🟢
* Inverter o grafo de relações direcionadas para expor os backlinks correspondentes de cada tomada de decisão. 🟢

## Regras de Negócio
* **Estruturação Semântica Estrita:** Cada arquivo sob `decisoes/` deve seguir a ordem H1, tabela de metadados (`gancho`, `relacoes`), e seções textuais delimitadas: decisão (`D`), justificativa (`PORQUÊ`), alternativas (`DESCARTADO`) e status (`ESTADO`). 🟢 [MD-0005.md](file:///Users/iagoleal/dev/harness/harness-config/decisoes/MD-0005.md)
* **Rejeição de Metadados Malformados:** O parser deve acusar erros e abortar a compilação do índice caso identifique relações de design declaradas de forma incorreta (diferente de 2 tokens ex: `refina MD-0002`). 🟢 [gerar-index-decisoes.sh:100](file:///Users/iagoleal/dev/harness/harness-config/bin/gerar-index-decisoes.sh#L100) (inferido a partir do commit `b955e17`)
* **Consistência do Índice no Git:** É proibido comitar propostas de decisões ou alterações de código se o índice físico `microdecisoes.md` estiver inconsistente ou defasado em relação às fichas individuais. 🟢 [bootstrap.sh:53](file:///Users/iagoleal/dev/harness/harness-config/bin/bootstrap.sh#L53)

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
| :--- | :--- | :---: | :--- |
| **RF-01** | Processamento de relações direcionais. | Must | Mapear chaves de relações como `depende-de`, `substitui`, `refina`, `relaciona`. |
| **RF-02** | Cálculo automático de backlinks. | Must | Inverter as arestas do grafo (ex: A refina B implica que B é refinado por A) e documentar de forma visual no markdown do índice. |
| **RF-03** | Validação passiva de integridade (`--check`). | Must | Prover flag que executa o parse e compara o resultado consolidado atual sem reescrever o arquivo físico, retornando erro se houver defasagem. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
| :--- | :--- | :--- | :---: |
| Simplicidade | Armazenamento text-only no Git, eliminando dependências de mecanismos DB relacionais. | `decisoes/` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que uma nova decisão MD-0018 foi adicionada e vinculada à MD-0005 via 'refina MD-0005'
Quando o compilador de índice for executado
Então a ficha da MD-0005 no índice compilado deve apresentar automaticamente a referência reversa '↳ refinada-por MD-0018'.

Dado que o índice compilado físico está defasado em relação aos arquivos de decisões em disco
Quando o script de geração for invocado com a flag --check
Então ele deve encerrar com status 1 exibindo aviso de inconsistência de arquivos.
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
| :--- | :---: | :--- |
| Estrutura física particionada | Must | Resolve problemas de concorrência e economiza contexto de leitura dos agentes. |
| Inversão de backlinks | Must | Garante a visibilidade e navegação de efeitos colaterais de mudanças conceituais. |
| Validação de índice (`--check`) | Should | Permite automatizar a checagem no pre-commit do Git. |
