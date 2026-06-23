# Requirements: Execução Local do Harness Core

> Identificador: `001-run-harness-core-local`
> Data: `2026-06-23`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Esta feature estabelece uma interface de execução unificada para o núcleo do sistema na raiz do projeto local. Através de um script de automação de entrada e de um snippet de configuração de ciclo de vida do agente de IA, o sistema delega a formatação de arquivos, a validação de microdecisões de design e a execução de ganchos diretamente ao núcleo executável local, eliminando o acoplamento a caminhos globais do host.

## 2. Contexto a partir do legado

As definições e restrições desta feature apoiam-se nos mapeamentos técnicos da engenharia reversa do sistema legado:

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#1-estilo-de-arquitetura` | O sistema opera como interceptor local desacoplado via arquivos markdown e ganchos de ciclo de vida. | 🟢 |
| `_reversa_sdd/inventory.md#scripts-e-utilitarios-bin` | Mapeamento dos utilitários legados de bootstrap, verificação de sincronia e consolidação de índices. | 🟢 |
| `_reversa_sdd/code-analysis.md#24-modulo-hooks` | Roteamento de automação de formatação disparado por eventos de edição de arquivos. | 🟢 |
| `_reversa_sdd/domain.md#21-fluxo-de-sincronizacao-e-resiliencia` | O boot do agente local e a execução de ganchos devem funcionar de forma independente de rede ou dependências externas globais. | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Desenvolvedor Único | Executar ações do núcleo local na raiz de forma transparente e portável. | O desenvolvedor salva um arquivo e o ganchos locais chamam o resolvedor do núcleo local para padronizar o código. |
| Agente de IA | Integrar ganchos e comandos do ciclo de vida sem depender de utilitários globais do host. | O agente de IA invoca o comando de consolidação de decisões usando o caminho relativo do projeto local. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01: Ponto de Entrada Relativo Unificado** 🟢
   - Origem no legado: `_reversa_sdd/inventory.md#scripts-e-utilitarios-bin`
   - Tipo: nova
   - Descrição: O projeto deve prover uma interface executável simplificada na raiz local que direcione as chamadas ao núcleo executável Python utilizando o interpretador do ambiente virtual correspondente, repassando todos os parâmetros recebidos.

2. **RN-02: Isolamento de Ganchos do Agente** 🟢
   - Origem no legado: `_reversa_sdd/domain.md#32-integridade-e-salvaguarda-de-arquivos`
   - Tipo: alterada
   - Descrição: Os ganchos do ciclo de vida do agente de IA configurados no escopo do projeto devem apontar de forma exclusiva para o ponto de entrada local na raiz, assegurando que alterações no ambiente de desenvolvimento global do host não causem falhas operacionais ou inconsistências no projeto.

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Script wrapper de conveniência na raiz local | Must | A chamada `./harness <comando>` a partir da raiz redireciona para a execução do interpretador de ambiente virtual do núcleo com sucesso. | 🟢 |
| RF-02 | Configuração portátil de ganchos do ciclo de vida | Must | Disponibilização de um snippet de ganchos local para o agente de IA que utiliza o ponto de entrada da raiz. | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Portabilidade | Compatibilidade com sistemas baseados em POSIX (macOS e Linux). | Garantir o funcionamento dos ganchos locais independente de variações de interpretadores shell do host. | 🟢 |
| Desempenho | Tempo de resposta de encaminhamento inferior a 100ms. | A execução do wrapper de entrada não deve adicionar overhead perceptível aos eventos de escrita (`PostToolUse`). | 🟡 |
| Robustez | Validação da presença do núcleo e do ambiente virtual. | O script deve verificar a existência dos caminhos locais e reportar falhas legíveis antes de tentar invocar o interpretador. | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Execução bem-sucedida do wrapper na raiz
  Dado que o ambiente virtual do núcleo está instalado em harness-core/.venv
  E o script principal do núcleo existe em harness-core/src/main.py
  Quando o usuário executa o comando `./harness decisions` na raiz do projeto
  Então a validação de microdecisões do núcleo é invocada e retorna o resultado correto

Cenário: Tentativa de execução sem ambiente virtual instalado
  Dado que o diretório do ambiente virtual harness-core/.venv está ausente
  Quando o usuário executa o comando `./harness decisions`
  Então o script de conveniência aborta a execução, exibe uma mensagem orientando sobre o setup do ambiente e retorna código de saída 1
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | Necessário para unificar a execução e simplificar os caminhos no terminal. |
| RF-02 | Must | Essencial para que os ganchos do agente passem a interagir com a version Python local. |
| RNF de Portabilidade | Should | Importante para manter a portabilidade entre ambientes locais macOS e Linux. |
| RNF de Robustez | Should | Garante que mensagens claras sejam exibidas em vez de erros crípticos do interpretador. |

## 9. Esclarecimentos

> Nenhuma sessão de dúvidas registrada ainda. Rode `/reversa-clarify` quando houver `[DÚVIDA]` pendente.

## 10. Lacunas

- Nenhuma lacuna identificada para o escopo inicial de mapeamento do ponto de entrada local.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-requirements` | reversa |
