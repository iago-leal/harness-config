# Relatório de Confiança — harness

> Gerado pelo Revisor em 2026-06-23 (Re-extração após Feature 002)
> Nível de Documentação: **Completo**

Este relatório sintetiza a avaliação de confiança das especificações técnicas levantadas para o ecossistema `harness` (incluindo o novo núcleo Python `harness-core`, o wrapper raiz e a documentação HTML).

---

## Resumo Geral

| Nível | Quantidade | Percentual |
| :--- | :---: | :---: |
| 🟢 CONFIRMADO | 98 | 94.2% |
| 🟡 INFERIDO | 6 | 5.8% |
| 🔴 LACUNA | 0 | 0.0% |
| **Total** | **104** | **100%** |

**Confiança Geral do Projeto:** **97.1%** 🟢
*(Cálculo: (98 + 6 * 0.5) / 104 = 97.1%)*

---

## Por Spec

| Unidade de Especificação (Unit) | 🟢 | 🟡 | 🔴 | Confiança |
| :--- | :---: | :---: | :---: | :---: |
| `sdd/bootstrap` | 11 | 1 | 0 | 95.8% |
| `sdd/sync-check` | 13 | 0 | 0 | 100.0% |
| `sdd/format-on-edit` | 14 | 0 | 0 | 100.0% |
| `sdd/microdecisoes` | 11 | 1 | 0 | 95.8% |
| `sdd/comandos-customizados` | 13 | 0 | 0 | 100.0% |
| `sdd/run-harness-core-local` | 13 | 0 | 0 | 100.0% |
| `sdd/documentacao-uso-html` | 23 | 4 | 0 | 92.5% |

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
