# Relatório de Confiança — harness

> Gerado pelo Revisor em 2026-06-23
> Nível de Documentação: **Completo**

Este relatório sintetiza a avaliação de confiança das especificações técnicas levantadas para o ecossistema `harness-config`.

---

## Resumo Geral

| Nível | Quantidade | Percentual |
| :--- | :---: | :---: |
| 🟢 CONFIRMADO | 62 | 96.9% |
| 🟡 INFERIDO | 2 | 3.1% |
| 🔴 LACUNA | 0 | 0.0% |
| **Total** | **64** | **100%** |

**Confiança Geral do Projeto:** **98.4%** 🟢
*(Cálculo: (62 + 2 * 0.5) / 64 = 98.4%)*

---

## Por Spec

| Unidade de Especificação (Unit) | 🟢 | 🟡 | 🔴 | Confiança |
| :--- | :---: | :---: | :---: | :---: |
| `sdd/bootstrap` | 11 | 1 | 0 | 95.8% |
| `sdd/sync-check` | 13 | 0 | 0 | 100.0% |
| `sdd/format-on-edit` | 14 | 0 | 0 | 100.0% |
| `sdd/microdecisoes` | 11 | 1 | 0 | 95.8% |
| `sdd/comandos-customizados` | 13 | 0 | 0 | 100.0% |

---

## Lacunas Pendentes 🔴
Nenhuma lacuna pendente.

---

## Histórico de Reclassificações

| De | Para | Afirmação | Evidência / Justificativa |
| :---: | :---: | :--- | :--- |
| 🟡 | 🟢 | Inversão de grafo e backlinks de decisões de design. | Confirmado via lógica awk no [gerar-index-decisoes.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/gerar-index-decisoes.sh). |
| 🟡 | 🟢 | TTL de 24 horas no cache de sincronia. | Confirmado via constante no [sync-check.sh:20](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh#L20). |
| 🟡 | 🟢 | Formato exato do payload JSON do hook SessionStart. | Confirmado via contrato de saída em [sync-check.sh:136](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh#L136). |
