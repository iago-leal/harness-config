---
schemaVersion: 1
generatedAt: 2026-06-23T14:15:00Z
reversa:
  version: "1.2.43"
kind: risk_register
producedBy: strategist
hash: "sha256:734635da606bc90f0703a6e5fecbe52792ecfe8227f5700bca9690a3530892da"
---

# Risk Register

> Registro de riscos da migração com probabilidade, impacto, mitigação e responsável.

## Riscos

### RISK-001: Latência nos Ganchos do Git (Cold Start Python)
- **Descrição**: O interpretador Python local pode adicionar uma latência significativa (cold start) a cada execução de gancho rápido (como `pre-commit` ou `post-merge`), tornando a experiência de commit desconfortável.
- **Categoria**: técnico
- **Probabilidade**: média
- **Impacto**: médio
- **Severidade combinada**: Média
- **Trigger / sinal de alerta**: Tempo de execução de ganchos Git ultrapassando 500ms.
- **Mitigação**: O script adaptador local em Bash (`.sh`) deve fazer validações rápidas (ex. se `.no-autoformat` existe) antes de invocar o interpretador Python, ou invocar o Python em background.
- **Plano de contingência**: Utilizar compilação Python rápida, otimizar imports de bibliotecas (lazy loading), ou delegar o peso para o servidor MCP rodando em memória e usar um cliente soquete simples em C/Bash para comunicar o hook.
- **Owner**: Designer
- **Status**: aberto

### RISK-002: Incompatibilidade no Ciclo de Vida do Servidor MCP
- **Descrição**: Diferentes harnesses (Claude Code, Gemini CLI, Antigravity) gerenciam a inicialização de servidores MCP locais de formas distintas. O servidor MCP pode falhar ao ser invocado por algum dos clientes, interrompendo o formatador ou o verificador de sincronia.
- **Categoria**: operacional
- **Probabilidade**: alta
- **Impacto**: alto
- **Severidade combinada**: Alta
- **Trigger / sinal de alerta**: Mensagem de erro de conexão ao servidor MCP ou ganchos falhando silenciosamente no início de uma sessão de IA.
- **Mitigação**: Desenvolver o servidor MCP em conformidade estrita com a especificação Model Context Protocol e testar contra múltiplos clientes usando suites de simulação.
- **Plano de contingência**: Manter wrappers de terminal simples (`.sh`) como fallback para execução direta de tarefas administrativas locais sem depender de MCP.
- **Owner**: Developer
- **Status**: aberto

### RISK-003: Divergência de Parsing no Grafo de Microdecisões
- **Descrição**: O parser orientado a objetos em Python pode interpretar relacionamentos ou formatos Markdown de maneira ligeiramente diferente do utilitário Bash baseado em `sed`/`awk`, gerando quebras no arquivo `microdecisoes.md` compilado.
- **Categoria**: técnico
- **Probabilidade**: média
- **Impacto**: alto
- **Severidade combinada**: Alta
- **Trigger / sinal de alerta**: Inconsistências de backlinks geradas no arquivo consolidado de microdecisões no repositório.
- **Mitigação**: Implementar testes de paridade comparando a saída de `gerar-index-decisoes.sh` legado com o gerador Python para os mesmos conjuntos de dados de microdecisões.
- **Plano de contingência**: Adicionar uma flag de fallback de emergência para rodar o script legador em Bash até que o parser Python seja corrigido.
- **Owner**: Developer
- **Status**: aberto

### RISK-004: Erros de PATH/Ambiente sob Múltiplos Interpretadores
- **Descrição**: O resolvedor de formatadores Python pode falhar ao localizar Ruff, Prettier ou Rustfmt caso as dependências locais (`.venv`, `node_modules`) estejam em caminhos flutuantes ou em versões do gerenciador de pacotes (`nvm`, `poetry`) não carregados nas sessões de IAs de terminal puro.
- **Categoria**: técnico
- **Probabilidade**: alta
- **Impacto**: alto
- **Severidade combinada**: Alta
- **Trigger / sinal de alerta**: Formatações falhando por falta de binários ou executando versões globais incorretas das ferramentas.
- **Mitigação**: Configurar caminhos estritos e resolvedores robustos baseados na configuração central `harness.toml`.
- **Plano de contingência**: Permitir configuração manual de overrides de PATH locais no arquivo de configuração do usuário.
- **Owner**: Designer
- **Status**: aberto

## Resumo por severidade

| Severidade | Quantidade | IDs |
|---|---|---|
| Crítica | 0 | |
| Alta | 3 | RISK-002, RISK-003, RISK-004 |
| Média | 1 | RISK-001 |
| Baixa | 0 | |

## Riscos relacionados ao paradigma alvo

> Subseção dedicada quando há mudança de paradigma. Listar apenas riscos cuja origem direta é o gap registrado em `paradigm_decision.md`.

- **RISK-003 (Parsing do Grafo)**: O mapeamento de relações antes baseado em texto associativo bruto (sed/awk procedural) agora é um Domain Model orientado a objetos em Python. Divergências conceituais no modelo podem quebrar backlinks.
- **RISK-004 (Configuração em TOML)**: A passagem de caminhos de diretórios e cache do Claude legados para o modelo desacoplado `harness.toml` exige mapeamentos de ambiente adicionais, podendo quebrar permissões locais.
