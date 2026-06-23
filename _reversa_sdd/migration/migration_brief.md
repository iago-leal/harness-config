---
schemaVersion: 1
generatedAt: "2026-06-23T13:58:00Z"
reversa:
  version: "1.2.43"
kind: migration_brief
producedBy: orchestrator
hash: "sha256:be60138d3226f118053918e063616450a9814ebac98920a2c131f607ba3a686e"
---

# Migration Brief

> Documento de critério de migração coletado em entrevista no início do `/reversa-migrate`.
> Consumido pelos seis agentes do Time de Migração. Não pergunta paradigma (responsabilidade do Paradigm Advisor) nem apetite (derivado em `paradigm_decision.md`).

## Objetivo da migração
Estamos migrando o ambiente pois ele está muito acoplado ao Claude Code. O objetivo é torná-lo agnóstico à IDE/Harness de desenvolvimento para que possa ser executado por múltiplos agentes/ferramentas.

## Métricas de sucesso
- Obter paridade funcional completa das automações.
- Garantir estabilidade operacional cross-harness.

## Restrições
- **Prazo**: Sem restrições de prazo declaradas.
- **Orçamento**: Sem restrições de orçamento declaradas.
- **Técnicas**: Compatibilidade de execução cross-harness e adaptabilidade a diferentes interpretadores de hooks.
- **Operacionais**: Sem restrições operacionais declaradas.

## Fatores de risco conhecidos
- Quebra da lógica determinística de hooks nos diferentes harnesses.
- Quebra e incompatibilidade da barra de comandos (slash commands) em interfaces que não suportam Markdown de prompt do Claude.

## Stakeholders
| Nome / papel | Responsabilidade na migração |
|---|---|
| Iago | Dono do projeto, validador técnico e revisor geral |

## Stack alvo
- **Linguagem**: Indefinido (provavelmente .sh, .toml)
- **Framework**: Nenhum
- **Banco**: Nenhum
- **Mensageria** (se houver): Nenhuma
- **Infra**: Portável cross-harness
- **Outros componentes relevantes**: Adaptabilidade conforme execução de hooks de cada Harness.

## Escopo declarado
- **Incluído**: Todos os módulos atuais (bootstrap, sync-check, format-on-edit, microdecisões, slash commands).
- **Excluído**: Nenhum.

## Notas livres
O projeto deve ser portável e focado em rodar em qualquer Harness/agente de IA compatível, mantendo a consistência dos ganchos determinísticos.
