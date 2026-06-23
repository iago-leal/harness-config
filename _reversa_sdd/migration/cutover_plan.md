---
schemaVersion: 1
generatedAt: 2026-06-23T14:15:00Z
reversa:
  version: "1.2.43"
kind: cutover_plan
producedBy: strategist
hash: "sha256:ca8ff795260d33bd319ba49efe6a6fd81195dea50d72a9408423ef3676224306"
---

# Cutover Plan

> Plano de corte do legado para o sistema novo, alinhado à estratégia escolhida em `migration_strategy.md`.

## Estratégia base
- **Estratégia confirmada**: Estratégia B: Parallel Run (Coexistência de Homologação) de `migration_strategy.md`.

## Pré-requisitos
- [ ] Coexistência de execução paralela (shadow run) sem divergências nos logs de formatação e checagem de sincronia por pelo menos 5 dias consecutivos.
- [ ] 100% de sucesso na suite de testes de paridade a ser gerada pelo Inspector em `parity_tests/`.
- [ ] Latência do overhead do gancho Git Python mensurada abaixo de 200ms de execução.
- [ ] Validação manual de funcionamento em todas as 3 plataformas alvo (Claude Code, Gemini CLI e Antigravity CLI).

## Janela de cutover
- **Data alvo**: A definir (estimado em 5 dias úteis após a implementação completa das specs).
- **Duração estimada**: 1 hora
- **Ambiente afetado**: Ambiente de desenvolvimento local.
- **Comunicação prévia**: Apenas o dono do projeto (Iago) deve ser informado.

## Passos do cutover

| # | Passo | Owner | Duração | Reversível? |
|---|---|---|---|---|
| 1 | Interromper novas edições conceituais no repositório ativo | Iago | 5 min | Sim |
| 2 | Efetuar backup completo do diretório de ganchos `.git/hooks/` e do `settings.json` local | Iago | 10 min | Sim |
| 3 | Remover os symlinks locais de ganchos em Bash criados pelo antigo `bootstrap.sh` | Developer | 10 min | Sim |
| 4 | Configurar o Servidor MCP local nos arquivos de inicialização do Claude Code, Gemini CLI e Antigravity | Developer | 15 min | Sim |
| 5 | Executar o novo `bootstrap` do core Python compilando os novos ganchos Git adaptadores | Developer | 10 min | Sim |
| 6 | Realizar smoke tests simulando gravação de arquivos, checagem de sincronia externa e backlinks | Developer | 10 min | Sim |

## Plano de rollback
- **Critérios de acionamento**:
  - Ganchos do Git retornando erro de execução não resolvido que impeça o fluxo normal de commits locais.
  - Latência excessiva (acima de 500ms) observada de forma consistente em operações do terminal local.
  - Travamento completo de sessões do agente de IA devido a falhas de handshake no servidor MCP local.
- **Passos**:
  1. Restaurar o backup das configurações originais do `settings.json`.
  2. Apagar os adaptadores de ganchos Git Python sob `.git/hooks/`.
  3. Re-executar o script legado `harness-config/bin/bootstrap.sh` para reconstruir os links simbólicos dos hooks em Bash legados.
  4. Reiniciar a IDE/CLI e testar a integridade operacional anterior.
- **Tempo máximo aceitável até rollback**: 15 minutos
- **Owner do rollback**: Iago

## Critérios de go / no-go
- **Go**:
  - Paridade comportamental validada contra as especificações `parity_specs.md`.
  - Servidor MCP local autenticando e respondendo em milissegundos sem consumo elevado de CPU.
- **No-go**:
  - Qualquer falha ou exceção não tratada na suite de testes do Inspector.
  - Inconsistência nos backlinks compilados em `microdecisoes.md` em comparação ao gerador legado.

## Pós-cutover
- [ ] Monitoramento contínuo dos logs de formatação nas três CLIs por 7 dias.
- [ ] Desativação definitiva e arquivamento físico da pasta do legado `harness-config/` em 14 dias após estabilidade completa.

## Notas
Como o cutover ocorre inteiramente em máquina local de desenvolvimento sem interrupção de infraestrutura pública, a reversibilidade é extremamente simples e rápida de ser efetuada caso ocorra qualquer imprevisto.
