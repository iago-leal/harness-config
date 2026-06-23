# Regression Watch: Documentação de Uso Autogerada em HTML

> Identificador: `002-documentacao-uso-html`

## 1. Tabela de Regressões (Watch List)

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|-----------------------------|---------------------|-------------------|
| - | - | Não há regras legadas modificadas ou removidas para monitorar regressão. | - | - |

## 2. Histórico de re-extrações

*Nenhuma re-extração executada após esta feature.*

## 3. Observações

As seguintes regras novas foram introduzidas e devem ser observadas em evoluções futuras:

* **RN-08: Sincronização Automática da Documentação (Build)** 🟢
  - Garante que a build de documentação recrie o arquivo de saída `harness-docs.html`.
* **RN-09: Autossuficiência e Portabilidade do HTML** 🟢
  - Exige que o HTML seja standalone e sem dependências externas via internet.
* **RN-10: Introspecção Dinâmica dos Comandos** 🟡
  - Os metadados de CLI devem ser derivados programaticamente do argparse.

## 4. Arquivadas

*Nenhuma regra arquivada.*
