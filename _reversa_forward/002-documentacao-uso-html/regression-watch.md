# Regression Watch: Documentação de Uso Autogerada em HTML

> Identificador: `002-documentacao-uso-html`

## 1. Tabela de Regressões (Watch List)

| ID  | Origem (arquivo, seção) | Regra esperada após mudança                                              | Tipo de verificação | Sinal de violação |
| --- | ----------------------- | ------------------------------------------------------------------------ | ------------------- | ----------------- |
| -   | -                       | Não há regras legadas modificadas ou removidas para monitorar regressão. | -                   | -                 |

## 2. Histórico de re-extrações

### Re-extração 2026-06-24 08:10

Sem watch items de regressão — tabela principal vazia por design. A feature não modificou código legado que necessite monitoramento de regressão. As regras novas (RN-08, RN-09, RN-10) continuam válidas conforme histórico anterior.

### Re-extração 2026-06-23 21:58

Sem watch items de regressão na tabela principal (a feature não modificou regras legadas) — nada a verificar. Re-extração executada e artefatos centrais regenerados e coerentes. As regras novas observadas continuam válidas:

| Regra                                                 | Veredito | Observação                                                                                                                            |
| ----------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| RN-08 (build recria `harness-docs.html`)              | 🟢 verde | Preservada nas specs e no `code-analysis.md`.                                                                                         |
| RN-09 (HTML standalone, sem dependências de internet) | 🟢 verde | Confirmada.                                                                                                                           |
| RN-10 (introspecção dinâmica do argparse)             | 🟢 verde | Elevada de 🟡 para 🟢 pelo Detective nesta re-extração — introspecção confirmada em dois consumidores (`doc-gen` e `install-prompt`). |

## 3. Observações

As seguintes regras novas foram introduzidas e devem ser observadas em evoluções futuras:

- **RN-08: Sincronização Automática da Documentação (Build)** 🟢
  - Garante que a build de documentação recrie o arquivo de saída `harness-docs.html`.
- **RN-09: Autossuficiência e Portabilidade do HTML** 🟢
  - Exige que o HTML seja standalone e sem dependências externas via internet.
- **RN-10: Introspecção Dinâmica dos Comandos** 🟡
  - Os metadados de CLI devem ser derivados programaticamente do argparse.

## 4. Arquivadas

_Nenhuma regra arquivada._
