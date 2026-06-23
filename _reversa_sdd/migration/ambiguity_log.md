---
schemaVersion: 1
generatedAt: 2026-06-23T14:10:00Z
reversa:
  version: "1.2.43"
kind: ambiguity_log
producedBy: orchestrator
hash: "sha256:0a73fbe1f50cc073e2450c03030ed58380ef3a420e75bef0375d5a9a554b975d"
---

# Ambiguity Log

> Consolidação de todos os itens ⚠️ AMBÍGUOS ou pendentes detectados pelos agentes ao longo do pipeline.
> Status final esperado quando o pipeline conclui: nenhum item PENDENTE.

## Resumo
- Total de itens: 2
- PENDENTES: 0
- RESOLVIDOS COM DECISÃO HUMANA: 2
- REFERIDOS À CODIFICAÇÃO: 0

## Itens

### AMB-001
- **Descrição**: Mecanismo de Invocação de Hooks Cross-Harness. O Claude Code executa hooks de forma nativa via `settings.json`. O Gemini e o Antigravity CLI operam sob modelos diferentes. Como disparar o format-on-edit e o sync-check nesses harnesses sem hooks de IDE equivalentes?
- **Detectado por**: curator
- **Origem**: _reversa_sdd/migration/target_business_rules.md § BR-HUMANA-001
- **Status**: RESOLVIDO COM DECISÃO HUMANA
- **Decisão tomada**:
  - **Escolha**: Opção B: Expor as lógicas de formatador e sync-check como um servidor MCP local.
  - **Decisor**: Usuário (Iago Leal)
  - **Quando**: 2026-06-23T14:12:44Z
  - **Justificativa**: Garante baixo acoplamento, alta coesão e integração nativa com os diferentes harnesses de execução de forma limpa, respeitando a arquitetura hexagonal.

### AMB-002
- **Descrição**: Ausência de Interface Gráfica (UI) no projeto legado. O projeto harness-config é estritamente uma ferramenta de automação local e configuração de terminal/Git, não possuindo telas ou layout visual.
- **Detectado por**: screen_translator
- **Origem**: _reversa_sdd/inventory.md
- **Status**: RESOLVIDO COM DECISÃO HUMANA
- **Decisão tomada**:
  - **Escolha**: Pular execução do Screen Translator (status: skipped).
  - **Decisor**: Sistema/Orquestrador (com base na ausência de telas confirmada pelo inventário).
  - **Quando**: 2026-06-23T14:20:10Z
  - **Justificativa**: Legado não possui interfaces gráficas ou visualizadores, apenas automações CLI e ganchos Git locais.

## Itens referidos à codificação
> Lista somente itens com status `REFERIDO À CODIFICAÇÃO`. Aparecem destacados em `handoff.md`.

*(Nenhum item referido à codificação até o momento)*

## Notas
Inicialização do log de ambiguidades contendo a decisão humana herdada do Curator sobre o mecanismo de execução dos ganchos em múltiplos ambientes.
