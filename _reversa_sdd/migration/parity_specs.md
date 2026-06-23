---
schemaVersion: 1
generatedAt: 2026-06-23T14:22:00Z
reversa:
  version: "1.2.43"
kind: parity_specs
producedBy: inspector
hash: "sha256:0ca8ce993c2c70b307f145670f8953248dd1494a12a6d8b6546b9112f2203477"
---

# Parity Specs

> Estratégia de validação de equivalência comportamental entre legado e sistema novo, adaptada ao paradigma escolhido em `paradigm_decision.md` e à Estratégia B (Parallel Run) de `migration_strategy.md`.

## Estratégia geral
- **Modos de validação aplicáveis**:
  - [X] Shadow mode (execução paralela em background nos ganchos locais gravando logs de comparação)
  - [X] Characterization tests (suíte derivada das regras determinísticas de ganchos do legado)
  - [X] Contract tests (interfaces de ferramentas MCP expostas a múltiplos harnesses)
  - [ ] Data parity (snapshots e checksums)

## Critérios de "paridade aceita"
- **Métrica primária**: 100% de paridade em ganchos determinísticos executados em modo sombra (shadow mode) por 5 dias consecutivos sem nenhuma falha operacional ou divergência de arquivos gravados.
- **Janela de observação**: 5 dias de execução paralela diária no workflow de desenvolvimento de Iago.
- **Critério de bloqueio**: Qualquer erro de execução do pre-commit (status diferente de 0) ou erro de parse de metadados de microdecisões no core Python bloqueia o cutover definitivo.

## Cobertura adaptada ao paradigma

### Transição Procedural Bash → OO em Python com Injeção de Dependências
- **Invariantes em aggregates**:
  - `AGG-Decision` deve validar metadados e integridade estrutural Markdown, lançando exceção estruturada em caso de malformação de backlinks (equivalente ao crash de awk legados).
  - `AGG-Session` deve validar se o commit hash gravado em `ESTADO-DA-SESSAO.md` corresponde exatamente à âncora Git local.
- **Validação em construtores / serviços**:
  - `FormattingService` deve isolar a lógica de busca de formatadores locais/globais e opt-out de diretório de forma testável com `MockFileSystem` e `MockProcessRunner`, sem depender de estado global da máquina.
- **Comportamento equivalente sem acoplamento a ambiente**:
  - Validação de que os adaptadores MCP traduzem as chamadas das ferramentas para os métodos OO correspondentes com a mesma semântica que os scripts legados do Claude.

## Tipos de teste a aplicar
- **Funcionais**: Testes comportamentais baseados em cenários Gherkin validando as lógicas de format-on-edit, sync-check e grafo de microdecisões.
- **Contrato**: Validação de schemas do servidor MCP (FastMCP) e conformidade das respostas JSON com Gemini, Claude e Antigravity.
- **Performance**: Testes de latência medindo o overhead do boot Python nos ganchos do Git (overhead tolerado de no máximo 200ms).

## Reuso de characterization_specs do time de descoberta
- **Origem**: Não existia suíte de `characterization_specs` estruturada no legado (apenas smoke tests simples em `bin/test_sync_check.sh`).
- **Adaptações necessárias**: Derivar cenários Gherkin completos a partir do comportamento verificado na arqueologia técnica (`_reversa_sdd/code-analysis.md`).

## Saídas
- `parity_tests/01-sync-check.feature`: Validação de TTL do cache de rede e falhas resilientes.
- `parity_tests/02-format-on-edit.feature`: Validação de formatadores locais/globais e opt-out.
- `parity_tests/03-decision-graph.feature`: Validação de parsing de backlinks e indexação de grafos.
- `parity_tests/04-interactive-commands.feature`: Validação do limite PCCP e controle de sessão.

## Notas
Como o sistema não possui interface de usuário (UI) e o Screen Translator concluiu em modo `skipped`, nenhuma validação de paridade de telas ou de golden files visuais se faz necessária.
