# Roadmap: Execução Local do Harness Core

> Identificador: `001-run-harness-core-local`
> Data: `2026-06-23`
> Requirements: `_reversa_forward/001-run-harness-core-local/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Esta feature implementa um ponto de entrada unificado na raiz do projeto local (/Users/iagoleal/dev/harness) através do script wrapper `./harness` (Bash). Este wrapper é responsável por localizar o interpretador Python embutido no ambiente virtual dedicado (`harness-core/.venv/bin/python3`) e executar o núcleo do sistema (`harness-core/src/main.py`), repassando todos os argumentos recebidos. Além disso, as configurações de ganchos de ciclo de vida do agente de IA local são ajustadas para apontar para este wrapper, garantindo que as operações de formatação e decisões utilizem a versão mais recente e isolada do núcleo local sem depender de dependências globais no host.

## 2. Princípios aplicados

Nenhum princípio registrado em `principles.md`.

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Wrapper executável em Bash na raiz (`./harness`) | Garante a execução sob o ambiente virtual do core de forma portátil e transparente para o desenvolvedor e para ganchos automatizados. | a) Invocar `python3` global diretamente (falha caso falte dependência `toml`). b) Definir aliases de terminal (não funcionam em shells não-interativos iniciados por ganchos de IDE). | 🟢 |
| D-02 | Redirecionamento de ganchos do agente local | Garante que os hooks `SessionStart` e `PostToolUse` chamem o resolvedor em Python do núcleo local em vez dos scripts legados. | a) Manter hooks legados apontando para `$HOME/.claude/` (acoplamento global). | 🟢 |

## 4. Premissas

Nenhuma premissa baseada em dúvidas pendentes foi necessária, pois os requisitos estão totalmente definidos e sem ambiguidades.

## 5. Delta arquitetural

Componentes do legado afetados pela evolução:

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Interface executável | `_reversa_sdd/inventory.md#scripts-e-utilitarios-bin` | componente-novo | Criação de `./harness` na raiz do projeto. |
| Ganchos do ciclo de vida | `_reversa_sdd/code-analysis.md#24-modulo-hooks` | regra-alterada | Redirecionamento dos ganchos do agente para a execução local via wrapper. |

## 6. Delta no modelo de dados

- Resumo das mudanças: Não há alterações de banco de dados ou persistência estrutural de entidades nesta feature.
- Detalhe completo em: `_reversa_forward/001-run-harness-core-local/data-delta.md`

## 7. Delta de contratos externos

Não há contratos externos afetados (HTTP, gRPC, filas). Os ganchos operam de forma puramente local via CLI e arquivos.

## 8. Plano de migração

1. **Setup da venv:** Executar o instalador de dependências em `harness-core` para garantir a venv local ativa com as dependências do `requirements.txt`.
2. **Implantação do Wrapper:** Criar o script `./harness` na raiz com permissão de execução (`chmod +x`).
3. **Reconfiguração do Agente:** Aplicar a nova configuração local de ganchos no arquivo correspondente do agente de IA.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Venv do `harness-core` ausente ou desconfigurada | médio | média | O wrapper `./harness` deve validar a existência do interpretador Python na venv e dar instruções claras de como criá-la antes de abortar. |
| Desempenho lento na inicialização de subprocesso Python | baixo | baixa | O `harness-core` não possui dependências pesadas, garantindo inicialização de subprocesso em menos de 100ms. |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `regression-watch.md` gerado

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-plan` | reversa |
