# Roadmap: Documentação de Uso Autogerada em HTML

> Identificador: `002-documentacao-uso-html`
> Data: `2026-06-23`
> Requirements: `_reversa_forward/002-documentacao-uso-html/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A abordagem técnica consiste na criação de um módulo gerador de documentação centralizado no `harness-core` (`src/core/documentation/service.py`) e na exposição de novos subcomandos na CLI principal (`main.py`): `doc-gen` e `doc-serve`. 

O serviço de documentação realizará a introspecção das rotas e argumentos do parser `argparse` no entrypoint da CLI, fará o parsing de arquivos Markdown sob `_reversa_sdd/` (regras de negócio e diagramas) e coletará o status do projeto a partir do `.reversa/state.json`. Ao final, compilará essas informações em um único arquivo HTML standalone (`harness-docs.html` na raiz do projeto) utilizando CSS embutido moderno e JavaScript Vanilla para busca instantânea e interatividade. O comando `doc-serve` utilizará o módulo nativo do Python `http.server` para expor localmente este HTML.

## 2. Princípios aplicados

Não há princípios globais ativos definidos no arquivo `.reversa/principles.md` no momento da criação deste plano.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| n/a | n/a | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Introspecção do `argparse` em tempo de execução | Evita duplicação de explicações de comandos CLI no código, gerando a documentação diretamente da estrutura ativa do `main.py`. | (a) Escrever comandos estaticamente em um arquivo JSON auxiliar, (b) Fazer parse manual do código-fonte em string. | 🟢 |
| D-02 | Geração em Arquivo Único (Standalone) | Garante portabilidade absoluta e execução sem internet (offline) de forma simples para humanos e robôs. | (a) Gerar pasta com ativos JS/CSS separados, (b) Depender de CDNs externas online para carregar Tailwind ou fontes. | 🟢 |
| D-03 | Servidor nativo baseado em `http.server` | Permite rodar a visualização localmente através de um comando CLI simples sem adicionar frameworks pesados ao core. | (a) Integrar biblioteca externa como Flask/FastAPI, (b) Exigir que o usuário utilize ferramentas de terceiros (ex: Live Server). | 🟢 |
| D-04 | Gráficos e Timeline via SVG Inline / Vanilla JS | Permite desenhar o progresso dos checkpoints de forma visual premium sem puxar dependências externas como D3/Highcharts se executado offline. | (a) Incorporar scripts grandes de bibliotecas pesadas de gráficos, (b) Deixar o progresso apenas em tabela textual pura. | 🟡 |

## 4. Premissas

Nenhuma premissa adotada a partir de dúvidas pendentes, pois todas as lacunas do requirements foram resolvidas na sessão de esclarecimento.

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| n/a | n/a | n/a |

## 5. Delta arquitetural

Liste apenas os componentes do `_reversa_sdd/architecture.md` que mudam.

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `main.py` | `_reversa_sdd/inventory.md#⚡ Wrapper de conveniência` | componente-alterado | Adiciona os subcomandos `doc-gen` e `doc-serve` à CLI do `harness`. |
| `harness` | `_reversa_sdd/inventory.md#⚡ Wrapper de conveniência` | componente-alterado | Atualização do wrapper bash para repassar e dar suporte aos novos comandos de documentação. |
| `DocumentationService` | n/a (Novo Componente) | componente-novo | Módulo `src/core/documentation/service.py` encarregado da extração e compilação do HTML. |

## 6. Delta no modelo de dados

- Resumo das mudanças: Não há alterações em modelos de dados persistidos nem estruturas SQL/NoSQL. O estado do Reversa em `.reversa/state.json` é lido de forma estritamente somente-leitura.
- Detalhe completo em: `_reversa_forward/002-documentacao-uso-html/data-delta.md`

## 7. Delta de contratos externos

Não há contratos externos HTTP, gRPC, ou integradores de fila expostos para esta funcionalidade.

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| n/a | n/a | n/a |

## 8. Plano de migração

A funcionalidade é puramente aditiva no `harness-core`. Não há dados legados a migrar.

1. Instalação e teste dos novos subcomandos CLI localmente.
2. Execução da primeira build manual do HTML para confirmar a geração do arquivo `harness-docs.html` na raiz do projeto.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Quebra de compatibilidade com versões antigas do Python ao usar HTTP Server nativo | baixo | baixa | Usar apenas classes consolidadas como `http.server.HTTPServer` compatíveis com Python >= 3.8. |
| Travamento da CLI ao executar o servidor local sem sinal de encerramento | médio | média | Tratar de forma limpa o sinal de interrupção do terminal (`KeyboardInterrupt` / `Ctrl+C`) para fechar o socket do servidor. |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `regression-watch.md` gerado
- [ ] Arquivo `harness-docs.html` gerado na raiz e validado offline no navegador de forma manual
- [ ] Execução dos testes automatizados via `pytest` no `harness-core` cobrindo o novo módulo de documentação

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-plan` | reversa |
