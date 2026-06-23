---
schemaVersion: 1
generatedAt: 2026-06-23T14:24:00Z
reversa:
  version: "1.2.43"
kind: handoff
producedBy: orchestrator
hash: "sha256:f22fcec99cf9982ce0af43791f659c67001b3a21a254449ab6f61691a13da25c"
---

# Handoff para o Agente de Codificação

> Este documento é a porta de entrada para o agente de codificação (Claude Code, Codex, Cursor, Antigravity, etc.) que vai escrever o sistema novo a partir das specs.

## ⚠️ Leitura obrigatória primeiro

1. **`paradigm_decision.md`**, leitura inegociável. O paradigma alvo molda como toda a codificação deve acontecer.
2. **`topology_decision.md`**, leitura inegociável. A topologia escolhida (preservar / modernizar / híbrido) define a árvore de pastas e a fronteira entre módulos.
3. **`screen_modernization_decision.md`**, pular (o Screen Translator concluiu em modo `skipped` devido à ausência de UI no projeto).

## Ordem de leitura recomendada

1. `paradigm_decision.md` (obrigatório, primeiro)
2. `topology_decision.md` (obrigatório, segundo)
3. `migration_brief.md`
4. `target_business_rules.md`
5. `migration_strategy.md`
6. `target_architecture.md`
7. `target_domain_model.md`
8. `target_data_model.md`
9. `data_migration_plan.md`
10. `parity_specs.md` + `parity_tests/`
11. `risk_register.md` + `cutover_plan.md`
12. `discard_log.md` (consultivo)
13. `ambiguity_log.md` (consultivo)

## Lista de artefatos produzidos

| Artefato | Produzido por | Status |
|---|---|---|
| `migration_brief.md` | orchestrator | criado |
| `paradigm_decision.md` | paradigm_advisor | criado |
| `target_business_rules.md` | curator | criado |
| `discard_log.md` | curator | criado |
| `migration_strategy.md` | strategist | criado |
| `risk_register.md` | strategist | criado |
| `cutover_plan.md` | strategist | criado |
| `topology_decision.md` | designer (Fase 1) | criado |
| `target_architecture.md` | designer | criado |
| `target_domain_model.md` | designer | criado |
| `target_data_model.md` | designer | criado |
| `data_migration_plan.md` | designer | criado |
| `screen_modernization_decision.md` | screen_translator (Fase 1) | skipped |
| `target_screens.md` | screen_translator | skipped |
| `screen_deviation_log.md` | screen_translator | skipped |
| `parity_specs.md` | inspector | criado |
| `parity_tests/*.feature` | inspector | 4 arquivos |
| `ambiguity_log.md` | orchestrator | consolidado |

## Bloqueadores para começar a implementação
> Itens que precisam de decisão humana antes do agente de codificação começar.

- **Nenhum bloqueador, prosseguir**: Todas as decisões humanas e ambiguidades de pipeline (`AMB-001` e `AMB-002`) foram devidamente resolvidas e documentadas no `ambiguity_log.md`.

## Próximos passos para o agente de codificação

1. **Ler `paradigm_decision.md` e internalizar**: o paradigma alvo é Orientação a Objetos com Injeção de Dependências (Core Python). Toda escolha de código deve honrar esse paradigma.
2. **Ler `topology_decision.md` e internalizar**: a topologia escolhida é Opção 2: Adotar topologia moderna proposta (Hexagonal em Python OOP + Adaptadores MCP/CLI). Use o esboço da árvore registrado nesse artefato como base para criar a estrutura de pastas do novo repositório.
3. **Configurar o repositório novo** com a stack declarada em `migration_brief.md` (Python 3.10+, FastMCP, Ruff/Prettier/Rustfmt de host) e a topologia Hexagonal.
4. **Implementar bottom-up** seguindo `target_architecture.md` e `target_domain_model.md`:
   - Começar pelas interfaces das portas (`FileSystemPort`, `GitPort`, `ProcessPort`).
   - Implementar os adaptadores de infraestrutura correspondentes (`LocalFileSystemAdapter`, `SubprocessGitAdapter`, `HostFormatterAdapter`).
   - Implementar os aggregates do domínio (`AGG-Decision`, `AGG-Session`).
   - Desenvolver os casos de uso no core (`DecisionService`, `FormattingService`, `SyncService`, `BootstrapService`, `CommandService`).
   - Implementar o servidor MCP (`McpServerAdapter` via FastMCP) e a CLI de terminal agnóstica (`main.py`).
5. **Escrever os testes** a partir de `parity_specs.md` e `parity_tests/*.feature` desde o início, testando com MockFileSystem as regras de grafo e lint de forma isolada.
6. **Para a migração de dados** de microdecisões Markdown legadas, seguir `data_migration_plan.md` implementando a automação de injeção de Front-matter YAML.
7. **Para o cutover**, seguir `cutover_plan.md` respeitando o shadow run do Parallel Run.

## Itens auto-decididos (apenas se executado em --auto)
> Listar aqui itens cujo default foi aplicado sem confirmação humana. Recomenda-se revisar antes do cutover.

- Pipeline executado em modo interativo; nenhum item auto-decidido.

## Notas finais
O projeto está pronto para reconstrução de ponta a ponta. O acoplamento rígido ao Claude Code legado é totalmente removido na nova arquitetura, permitindo que a IA invoque o servidor MCP em qualquer harness e execute automações de forma consistente e centralizada no core Python.
