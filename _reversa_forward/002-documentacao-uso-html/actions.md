# Actions: Documentação de Uso Autogerada em HTML

> Identificador: `002-documentacao-uso-html`
> Data: `2026-06-23`
> Roadmap: `_reversa_forward/002-documentacao-uso-html/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 12 |
| Paralelizáveis (`[//]`) | 5 |
| Maior cadeia de dependência | 6 |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Criar o esqueleto do serviço de documentação `DocumentationService` em `harness-core/src/core/documentation/service.py`. | - | `[//]` | `harness-core/src/core/documentation/service.py` | 🟢 | `[X]` |
| T002 | Criar o arquivo base de template HTML em `harness-core/src/core/documentation/template.html` que conterá o layout da documentação. | - | `[//]` | `harness-core/src/core/documentation/template.html` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Criar a suíte de testes unitários para validar a geração da documentação e comportamento do serviço. | T001 | `[//]` | `harness-core/tests/test_documentation.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T004 | Implementar a extração dos comandos da CLI no `DocumentationService` através de introspecção recursiva do `argparse.ArgumentParser`. | T001 | - | `harness-core/src/core/documentation/service.py` | 🟢 | `[X]` |
| T005 | Implementar a leitura e parsing do Markdown em `_reversa_sdd/domain.md` e `_reversa_sdd/architecture.md` no `DocumentationService`. | T001 | - | `harness-core/src/core/documentation/service.py` | 🟡 | `[X]` |
| T006 | Implementar a leitura do `.reversa/state.json` e compilar o HTML gerado para `harness-docs.html` na raiz de forma atômica. | T001, T002, T004, T005 | - | `harness-core/src/core/documentation/service.py` | 🟢 | `[X]` |
| T007 | Desenvolver o visual responsivo (CSS Dark Mode elegante) e comportamento interativo (busca instantânea em Vanilla JS) no arquivo de template. | T002 | - | `harness-core/src/core/documentation/template.html` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T008 | Registrar o subcomando CLI `doc-gen` no parser do `harness-core/src/main.py` e chamar o serviço de compilação. | T006 | - | `harness-core/src/main.py` | 🟢 | `[X]` |
| T009 | Registrar o subcomando CLI `doc-serve` no `harness-core/src/main.py` e implementar o servidor local com o módulo nativo `http.server`. | T008 | - | `harness-core/src/main.py` | 🟢 | `[X]` |
| T010 | Atualizar o script executável wrapper `harness` na raiz para dar suporte e repassar os novos comandos CLI. | T008, T009 | - | `harness` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T011 | Adicionar testes de integração cobrindo a execução dos novos comandos `doc-gen` e `doc-serve` via CLI com pytest. | T003, T008, T009 | `[//]` | `harness-core/tests/test_documentation.py` | 🟢 | `[X]` |
| T012 | Validar o encerramento amigável do servidor local com `Ctrl+C` e a escrita atômica contra falhas silenciosas. | T009 | `[//]` | `harness-core/src/main.py` | 🟢 | `[X]` |

## Notas de execução

Nenhuma nota inserida ainda.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-to-do` | reversa |
