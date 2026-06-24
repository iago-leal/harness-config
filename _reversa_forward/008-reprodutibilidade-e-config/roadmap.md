# Roadmap: Reprodutibilidade e Configuração Viva de Formatação

> Identificador: `008-reprodutibilidade-e-config`
> Data: `2026-06-24`
> Requirements: `_reversa_forward/008-reprodutibilidade-e-config/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Para o gerenciamento de dependências, utilizaremos o `uv` no ambiente de desenvolvimento do core. O `requirements.txt` será travado deterministicamente com `uv pip compile`. Para a CI, configuraremos um GitHub Actions simples executando os testes unitários do `harness-core` em cada commit no Python 3.12/3.13. 
Para a formatação, alteraremos o construtor do `FormattingService` para receber opcionalmente `config: Optional[HarnessConfig]`. Modificaremos o loop de busca recursiva de opt-out para usar `config.formatting.opt_out_file` em vez do valor literal chumbado. Implementaremos a checagem de caminhos de exclusão em `exclude_paths` utilizando `fnmatch` para suportar glob patterns (ex: `**/*.log`, `temp/*`) além de correspondência por prefixo de pasta. Preservaremos as blindagens fixas de segurança em `~`, `~/Notas` e `~/.claude` em nível de código como restrição mínima de segurança.

## 2. Princípios aplicados

Nenhum princípio global configurado no projeto (`.reversa/principles.md` não encontrado).

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Usar `uv` e `uv pip compile` para travar dependências | Garante reprodutibilidade determinística sem forçar um framework pesado de empacotamento, mantendo o footprint baixo. | `pip freeze` (não resolve dependências transitivas elegantemente), `poetry` ou `pipenv` (adicionam arquivos complexos adicionais no repositório). | 🟢 |
| D-02 | Usar `fnmatch` para correspondência em `exclude_paths` | Nativo do Python, resolve de forma simples e rápida a validação de caminhos com curingas (ex: `**/*.log`, `temp/*`). | Expressões regulares manuais (muito complexas de ler e propensas a erros de segurança), apenas correspondência de prefixo simples (não atende ao requisito de casar glob patterns). | 🟢 |
| D-03 | Injeção de Dependência da Configuração no `FormattingService` | Permite testar o serviço injetando configurações dinâmicas mockadas (`HarnessConfig`), mantendo o acoplamento baixo. | Acessar a configuração lendo do disco diretamente dentro do serviço (violaria o isolamento hexagonal e dificultaria os testes unitários). | 🟢 |

## 4. Premissas

Nenhuma premissa adotada a partir de dúvidas pendentes (todas as dúvidas foram esclarecidas).

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `core/formatting` | `_reversa_sdd/architecture.md#1. Estilo de Arquitetura` | regra-alterada | `FormattingService` aceita `HarnessConfig` e valida opt-out e exclusões de forma dinâmica. |
| `core/domain` | `_reversa_sdd/architecture.md#1. Estilo de Arquitetura` | regra-alterada | `load_config` em `config.py` e os modelos do `HarnessConfig` continuam os mesmos, mas passam a alimentar o formatador. |

## 6. Delta no modelo de dados

- Resumo das mudanças: Nenhuma alteração de dados ou campos no `harness.toml`. O modelo `HarnessConfig` e sua seção `[formatting]` já existem e estão tipados, apenas passando a ser consumidos no serviço de formatação.
- Detalhe completo em: `_reversa_forward/008-reprodutibilidade-e-config/data-delta.md`

## 7. Delta de contratos externos

Nenhum contrato externo HTTP, fila ou gRPC é alterado; o wrapper CLI e a interface MCP continuam com o mesmo contrato de entrada/saída.

## 8. Plano de migração

Não há migração de dados no disco (n/a).

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Um glob pattern mal formado em `exclude_paths` ignorar arquivos incorretamente | médio | baixo | Utilizar `fnmatch` de forma isolada com tratamento robusto de erros e fallback seguro. |
| Dependência em bibliotecas externas na CI falhar | médio | baixo | CI utiliza cache de dependências do `uv` e instala de forma estrita via arquivo lock. |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-24 | Versão inicial gerada por `/reversa-plan` | reversa |
