---
schemaVersion: 1
generatedAt: 2026-06-23T14:15:00Z
reversa:
  version: "1.2.43"
kind: migration_strategy
producedBy: strategist
hash: "sha256:ce60e43938e0624031eb543b0e4175254d9afeed0d924c8f296d2e052ef51b4f"
---

# Migration Strategy

> Estratégias de migração avaliadas com trade-offs explícitos. A estratégia recomendada é a sugestão do Strategist; a decisão final é humana.

## Estratégias avaliadas

### Estratégia A: Big Bang com Rollback Imediato
- **Descrição**: Reconstrução completa do core em Python OOP + Servidor MCP local e corte total e imediato substituindo os ganchos do Git local e configurações da IDE para apontar para o novo sistema.
- **Quando aplica**: Sistemas pequenos, janelas de manutenção curtas toleradas, poucas integrações vivas e apetite transformacional.
- **Custo**: baixo
- **Risco**: alto
- **Tempo**: curto
- **Adequação ao apetite derivado** (`transformational`): Adequada. Como o sistema é muito pequeno, a reescrita completa e corte imediato é viável, embora arriscada para o workflow diário do desenvolvedor.
- **Trade-offs**:
  - Prós:
    - Implementação direta sem necessidade de manter infraestrutura de coexistência.
    - Rápido encerramento da migração e início de uso do novo sistema.
  - Contras:
    - Alto risco de quebrar o workflow do desenvolvedor imediatamente em caso de bugs ocultos.
    - Janela curta de homologação em ambiente real de uso.

### Estratégia B: Parallel Run (Coexistência de Homologação) - RECOMENDADA
- **Descrição**: O novo core Python e o servidor MCP são desenvolvidos em paralelo. Os hooks do Git continuam chamando os scripts legados em Bash no dia a dia, mas executam a versão Python de forma assíncrona/shadow (dry-run) gravando outputs em arquivos de log temporários. Uma ferramenta simples de auditoria valida a paridade funcional em background até 100% de consistência ser provada.
- **Quando aplica**: Lógicas críticas de fluxo de trabalho ou mudanças profundas de paradigma (como de procedural Bash para Python OOP/MCP) onde a quebra operacional imediata é inaceitável.
- **Custo**: médio
- **Risco**: baixo
- **Tempo**: médio
- **Adequação ao apetite derivado** (`transformational`): Muito adequada. Garante que a transição conceitual profunda de paradigma e a introdução da interface MCP não causem regressão nos ganchos.
- **Trade-offs**:
  - Prós:
    - Risco operacional próximo de zero para o desenvolvedor durante a migração.
    - Validação de paridade em ambiente real de uso diário (shadow execution).
  - Contras:
    - Requer esforço extra para configurar a execução paralela (shadow) e comparar outputs de log.

### Estratégia C: Strangler Fig (Migração Incremental de Componentes)
- **Descrição**: Substituição gradual dos ganchos e comandos um a um. Por exemplo, migra-se primeiro a formatação (`format-on-edit.sh`), depois de validada migra-se a sincronia (`sync-check.sh`), e por fim a indexação de microdecisões.
- **Quando aplica**: Sistemas médios a grandes, onde a complexidade de reconstrução total é muito alta para ser feita em uma única iteração.
- **Custo**: médio
- **Risco**: médio
- **Tempo**: longo
- **Adequação ao apetite derivado** (`transformational`): Baixa. O tamanho reduzido do legado (35 arquivos) não justifica a sobrecarga de manter um sistema híbrido com partes em Python e partes em Bash de forma sustentada.
- **Trade-offs**:
  - Prós:
    - Entrega incremental de valor nas ferramentas de desenvolvimento.
  - Contras:
    - Aumento do acoplamento temporário no código adaptador de interface para orquestrar chamadas híbridas.

## Comparativo

| Critério | Estratégia A (Big Bang) | Estratégia B (Parallel Run) | Estratégia C (Strangler Fig) |
|---|---|---|---|
| Custo | Baixo | Médio | Médio |
| Risco | Alto | Baixo | Médio |
| Tempo | Curto | Médio | Longo |
| Aderência ao apetite | Alta | Alta | Baixa |
| Compatibilidade com mudança de paradigma | Baixa | Alta | Média |

## Recomendação do Strategist
- **Estratégia recomendada**: **Estratégia B: Parallel Run (Coexistência de Homologação)**
- **Justificativa**: Embora o sistema legado seja pequeno, o gap de paradigma (Bash Procedural para Python OOP + Servidor MCP) altera fundamentalmente o fluxo de chamadas do Git e da IDE. Adotar o Parallel Run (rodando o servidor MCP em shadow mode enquanto os hooks locais rodam em Bash) permite garantir 100% de paridade funcional nos ganchos (que são altamente determinísticos) sem risco de interromper o fluxo de trabalho do dono do projeto (Iago).

## Sinais de alerta específicos
- **Transição de Paradigma + Servidor MCP**: Mudanças no interpretador do Git ou cold start na execução Python local podem introduzir latência nos ganchos paralelos. A validação shadow deve medir o tempo de execução do novo core Python.

## Decisão humana
- **Estratégia escolhida**: Estratégia B: Parallel Run (Coexistência de Homologação)
- **Quem decidiu**: Usuário (Iago Leal)
- **Quando**: 2026-06-23T14:15:36Z
- **Justificativa do decisor**: Opção recomendada para garantir segurança operacional e validação completa de paridade em ambiente de uso real, mitigando o risco de interrupção do workflow local de desenvolvimento.
