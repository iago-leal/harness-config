# Roadmap: Script de Bootstrap Simples (harness-init)

> Identificador: `007-bootstrap-harness-init`
> Data: `2026-06-24`
> Requirements: `_reversa_forward/007-bootstrap-harness-init/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Esta feature implementa o provisionamento automatizado de novos ambientes harness de forma 100% isolada e robusta (princípio do módulo per-projeto autocontido). 
O processo de inicialização de novos repositórios será feito através de um subcomando Python na CLI original (`./harness init <caminho-destino>`), o qual copiará fisicamente o núcleo `harness-core` (excluindo arquivos de cache e a venv) e o wrapper executável `harness` da raiz, criará a estrutura padrão da pasta de dados `.harness/` (decisões e sessão), configurará um ambiente virtual Python isolado e instalará os hooks Git pre-commit e post-merge locais.
Adicionalmente, gravaremos o metadado `upstream_path` em configuração do destino, permitindo comparação rápida de versão local contra o repositório original de distribuição e o subcomando `./harness upgrade` para atualização limpa e não destrutiva do código-fonte do núcleo no destino.

## 2. Princípios aplicados

> `.reversa/principles.md` **não existe** neste projeto. O desenho técnico adota os princípios globais do mantenedor (alta coesão, baixo acoplamento, OOP, TDD, SDD e neutralidade a harness), servindo como crivo para as decisões.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Baixo acoplamento | Evita o uso de links simbólicos entre pastas locais do host, prevenindo falhas em cascata se o repositório original do harness for movido ou apagado. | respeita |
| Alta coesão | Toda a lógica de instalação e atualização fica unificada em Python dentro do pacote `src/core/bootstrap` do core, e não dispersa em múltiplos scripts shell. | respeita |
| Testabilidade (TDD) | A implementação em Python sob portas abstratas (`FileSystemPort`, `ProcessPort`) permite escrever testes unitários completos no pytest que simulam a instalação/atualização. | respeita |
| Módulo Per-Projeto (MD-0005) | A cópia física das pastas do core para o destino assegura que o projeto seja autocontido, de footprint global zero e gerido diretamente pelo Git local. | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Comando `init` na CLI de Origem | Executar a inicialização do destino via `./harness init <caminho>` a partir da CLI original do harness. Aproveita a venv ativa de origem para o setup, facilitando a testabilidade (TDD) em Python. | Script Bash standalone na raiz (baixa testabilidade, dependência de ferramentas POSIX cruas no shell). | 🟢 |
| D-02 | Cópia Física Completa | Copiar o código fonte do core e o wrapper `harness` para o destino de forma íntegra. | Links simbólicos / symlinks (rompe o isolamento per-projeto e gera quebras silenciosas sob mudança da origem). | 🟢 |
| D-03 | Criação de Venv no Destino | Automatizar `python3 -m venv` e `pip install -r requirements.txt` na pasta de destino, emitindo alertas barulhentos se as dependências do host faltarem. | Exigir criação da venv manualmente (gera fricção excessiva no onboarding e delega setup técnico para a IA). | 🟢 |
| D-04 | Rastreamento do Upstream | Gravar o caminho do repositório original (`upstream_path`) no `harness.toml` ou `.harness/setup.json` do destino. | Não rastrear (torna atualizações difíceis e exige intervenção manual). | 🟢 |
| D-05 | Comando `upgrade` no Destino | Implementar `./harness upgrade` que substitui o código de `harness-core/` do destino preservando dados em `.harness/` e `.reversa/`. | Git merge/pull (muito complexo se o destino não compartilhar histórico do git com o harness). | 🟢 |

## 4. Premissas

> Não foram adotadas premissas baseadas em dúvidas, uma vez que todas as lacunas do requirements foram 100% resolvidas.

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `BootstrapService` | `_reversa_sdd/architecture.md#5-componentes` | regra-alterada | Ganha os métodos `initialize_project(target_path, active_harness)` e `upgrade_project(target_path)`. |
| CLI Python (main.py) | `_reversa_sdd/architecture.md#5-componentes` | regra-alterada | Ganha os subcomandos `init` (apenas executável na origem) e `upgrade` (executável no destino). |
| Config (`HarnessConfig`) | `_reversa_sdd/architecture.md#5-componentes` | regra-alterada | `HarnessSection` ganha os atributos opcionais `upstream_path` e `version` (ou lê de um arquivo do core). |

## 6. Delta no modelo de dados

- Resumo das mudanças: Configuração do `harness.toml` no destino ganha o campo `upstream_path` e `version` na seção `[harness]`. O arquivo `.harness/setup.json` também pode rastrear esses metadados.
- Detalhe completo em: `_reversa_forward/007-bootstrap-harness-init/data-delta.md`

## 7. Delta de contratos externos

> A feature não consome nem expõe contratos externos (HTTP, gRPC, filas ou arquivos compartilhados com terceiros). Toda a comunicação e operação é de CLI local.

## 8. Plano de migração

> n/a (Nova capacidade de instalação para novos projetos; não afeta os repositórios preexistentes, a menos que queiram rastrear o upstream retrospectivamente, o que pode ser feito rodando o init novamente).

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Sobrescrita acidental de decisões do usuário no upgrade | alto | baixo | O comando `upgrade` restringe suas escritas estritamente às pastas `harness-core/` (excluindo dados) e ao wrapper `harness`. As pastas `.harness/` e `.reversa/` são ignoradas ou blindadas. |
| Incompatibilidade de interpretador python no host de destino | médio | médio | O script captura erros de inicialização de subprocessos e ensina o usuário a instalar a versão mínima necessária do python. |
| Cópia de lixo local (venv, pytest caches) | baixo | baixo | O script usa uma lista de exclusão explícita de caminhos e padrões de arquivos ao copiar recursivamente o diretório. |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `regression-watch.md` gerado
- [ ] Suíte de testes no pytest cobrindo init, upgrade e detecção de versão verde

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-24 | Versão inicial gerada por `/reversa-plan` | reversa |
