# Requirements: Execução Local do Harness Core

> Identificador: `run-harness-core-local`
> Data: `2026-06-23`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Esta unit estabelece a especificação do script wrapper de conveniência Bash (`harness`) localizado na raiz do projeto e o snippet de ganchos do agente local. Ela garante a execução isolada do núcleo Python (`harness-core`) sob o ambiente virtual dedicado e portátil, eliminando o acoplamento a interpretadores Python ou dependências instaladas globalmente no host local.

## 2. Contexto a partir do legado

A especificação baseia-se nos seguintes artefatos de engenharia reversa do núcleo:

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/inventory.md#wrapper-de-conveniencia-raiz-do-projeto` | Criação de um ponto de entrada simplificado na raiz para o core. | 🟢 |
| `_reversa_sdd/adrs/0007-wrapper-conveniencia-raiz.md` | Decisão de arquitetura por script wrapper para facilidade sintática e isolamento de dependências. | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Desenvolvedor Único | Chamar a CLI do núcleo local a partir de qualquer sub-shell sem digitar caminhos longos da venv. | O desenvolvedor executa `./harness decisions` na raiz para indexar as microdecisões. |
| Agente de IA | Integrar com ganchos do editor usando caminhos relativos ao projeto local. | O agente invoca o linter local chamando o wrapper durante o evento `PostToolUse`. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01: Redirecionamento com Venv Isolada** 🟢
   - Tipo: nova
   - Descrição: O script wrapper `./harness` deve direcionar a execução de parâmetros para `.harness/harness-core/src/main.py` utilizando o interpretador embutido em `.harness/harness-core/.venv/bin/python3`.
2. **RN-02: Fail-fast em Venv Ausente** 🟢
   - Tipo: nova
   - Descrição: Se a pasta do ambiente virtual `.harness/harness-core/.venv` estiver ausente, o script de conveniência deve abortar a execução com código `1`, exibindo instruções didáticas ao usuário de como inicializar a venv e instalar as dependências.

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Encaminhamento de chamadas da CLI | Must | Chamar `./harness <comando>` executa a CLI correspondente com sucesso. | 🟢 |
| RF-02 | Suporte de múltiplos argumentos | Must | Argumentos extras e flags são repassados ao core (`"$@"`). | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Portabilidade | Compatibilidade com Bash POSIX em macOS e Linux. | O wrapper utiliza rotinas portáveis de resolução de caminhos (`BASH_SOURCE`). | 🟢 |
| Robustez | Emissão de diagnósticos em `stderr`. | Mensagens de venv ausente são enviadas para o canal de erro padrão. | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Execução do wrapper com venv existente
  Dado que a venv existe em .harness/harness-core/.venv
  Quando o usuário executa o comando `./harness cmd clarificar`
  Então o wrapper localiza o interpretador e exibe o texto de esclarecimento de requisitos

Cenário: Execução do wrapper com venv ausente
  Dado que a venv não foi criada em .harness/harness-core/.venv
  Quando o usuário executa `./harness decisions`
  Então o wrapper aborta, exibe uma mensagem instruindo sobre o setup e retorna saída 1
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | Necessário para viabilizar a execução dos sub-serviços na raiz do projeto. |
| RF-02 | Must | Essencial para que os formatadores de hooks recebam o arquivo a formatar de forma correta. |
| RNF de Portabilidade | Should | Garante o funcionamento cross-host em ambientes macOS e Linux do desenvolvedor. |

## 9. Esclarecimentos

> Nenhuma sessão de dúvidas registrada ainda. Rode `/reversa-clarify` quando houver `[DÚVIDA]` pendente.

## 10. Lacunas

- Nenhuma lacuna identificada.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-writer` | reversa |
