# Legacy Impact: Documentação de Uso Autogerada em HTML

> Identificador: `002-documentacao-uso-html`
> Data: `2026-06-23`

## 1. Tabela de Impacto

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `harness-core/src/main.py` | `main.py` | componente-alterado | LOW | Registro de novos subcomandos CLI (`doc-gen` e `doc-serve`). |
| `harness` | `harness` | componente-alterado | LOW | Comportamento estendido para repasse de novos comandos sem quebrar compatibilidade. |
| `harness-core/src/core/documentation/service.py` | `DocumentationService` | componente-novo | LOW | Implementação do gerador de documentação com introspecção de CLI e parsing de regras. |
| `harness-core/src/core/documentation/template.html` | `DocumentationTemplate` | componente-novo | LOW | Arquivo de template para renderização do HTML estático standalone. |
| `harness-core/tests/test_documentation.py` | `test_documentation.py` | componente-novo | LOW | Suíte de testes unitários e integração de comandos. |

## 2. Diff Conceitual por Componente

- **`main.py`**: A CLI principal foi estendida para suportar dois novos comandos adicionais (`doc-gen` para compilação local e `doc-serve` para expor o HTML). A lógica de argparse foi movida para uma função pura `build_parser()` para possibilitar introspecção dinâmica de ajuda.
- **`DocumentationService`**: Nova classe introduzida para acoplar dados de metadados de CLI (via introspecção de argparse), regras de negócio extraídas de `domain.md` e checkpoints de engenharia reversa do `state.json`.

## 3. Preservadas

As seguintes regras de negócio confirmadas do legado em `_reversa_sdd/domain.md` foram mantidas 100% intactas e operacionais:

* **RN-01: Janela TTL de Sincronia (Cache Local)** 🟢
* **RN-02: Resiliência Offline** 🟢
* **RN-03: Não-Bloqueio de Formatadores (Blindagem)** 🟢
* **RN-04: Proteção de Diretórios Críticos** 🟢
* **RN-05: Precedência de Executáveis Locais** 🟢
* **RN-06: Opt-out do Projeto** 🟢
* **RN-07: Validação da Âncora de Integridade Git** 🟢

## 4. Modificadas

Nenhuma regra de negócio legada foi modificada ou removida por esta feature (puramente aditiva).
