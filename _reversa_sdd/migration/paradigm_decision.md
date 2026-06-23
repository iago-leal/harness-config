---
schemaVersion: 1
generatedAt: "2026-06-23T14:06:00Z"
reversa:
  version: "1.2.43"
kind: paradigm_decision
producedBy: paradigm_advisor
hash: "sha256:3cdafd989724f3522c0729a09a12506e699fd99c7c516ff7535ec835c4313049"
---

# Paradigm Decision

> Decisão consciente sobre como tratar a mudança (ou ausência) de paradigma entre o legado e a stack alvo.
> Este artefato é leitura obrigatória primeiro para qualquer agente posterior e para o agente de codificação.

## Paradigma do legado detectado
- **Paradigma principal**: Procedural 🟢
- **Confiança**: 🟢 CONFIRMADO
- **Evidências**:
  - Ausência de herança, polimorfismo ou injeção de dependências em todos os módulos legados (`bin`, `commands`, `hooks`). 🟢
  - Lógica baseada em funções top-level e scripts lineares sequenciais de shell. 🟢 [format-on-edit.sh](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh) e [sync-check.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh)
  - Manipulação de dados e estados diretamente via arquivos texto ou buffers de variáveis globais do shell. 🟢
- **Variações observadas**:
  - As decisões de design são armazenadas de forma estruturada baseada em metadados Markdown (comportamento de persistência local). 🟢 [decisoes/](file:///Users/iagoleal/dev/harness/harness-config/decisoes/)

## Stack alvo declarada
- Linguagem: Python + scripts adaptadores leve em Shell + TOML 🟢
- Framework: Arquitetura Hexagonal (Portas e Adaptadores) com Orientação a Objetos pura 🟢
- Infra: Portável e independente de IDE (compatível com Claude Code, Gemini CLI e Antigravity) 🟢

## Paradigma natural inferido
- **Paradigma**: Orientação a Objetos com Injeção de Dependências (Core Python) + Dataflow (Compilador de Hooks). 🟢
- **Justificativa**: A modularidade de um compilador de ganchos exige alta coesão de domínio (regras de sync, lint e decisões) e baixo acoplamento físico nas bordas do sistema (adaptadores de IDEs/Harnesses específicos). A POO em Python viabiliza esse desacoplamento de forma robusta por meio de herança e injeção de dependências. 🟢
- **Alternativas viáveis**: Programação procedural estruturada em Python (Opção C), descartada por violar as prioridades de coesão, baixo acoplamento e longevidade. 🟢

## Gap identificado
- **Severidade**: Médio 🟢
- **Implicações concretas** (implicações da quebra de acoplamento a IDE do Claude Code):
  - **Implicação 1: Processamento de JSON específico de IDE vira injeção de adaptadores.**
    No legado, os hooks `format-on-edit.sh` e `sync-check.sh` manipulam diretamente payloads JSON específicos do Claude Code. Na nova stack, o núcleo Python interage com interfaces genéricas de eventos (Portas de Entrada), e adaptadores de Harnesses (`ClaudeAdapter`, `GeminiAdapter`, `AntigravityAdapter`) traduzem as particularidades físicas de cada um. 🟢
  - **Implicação 2: Lógica de grafo via Bash vira Domain Model com Entities em Python.**
    No legado, a inversão de backlinks de decisões está codificada em shell script usando comandos awk associativos complexos em `gerar-index-decisoes.sh`. Na nova stack, as decisões e suas dependências viram entidades e objetos de valor ricos (`Decision`, `Relationship`) estruturados e validados de forma OO. 🟢
  - **Implicação 3: Gerenciamento de cache e logs migra para adaptadores de infraestrutura.**
    No legado, os caminhos físicos de gravação de cache de rede do `sync-check.sh` e logs de formatação são rígidos e acoplados a diretórios específicos (`~/.claude`). Na nova stack, esses side-effects são injetados como adaptadores do `FileSystemClient` orientados à configuração do `harness.toml`. 🟢
  - **Implicação 4: Slash commands e prompts em markdown viram templates parametrizáveis.**
    No legado, os comandos `/` residem em markdown descritivo sob `commands/` feito sob medida para o interpretador do Claude. Na stack alvo, a lógica de prompts e interações PCCP/handoff vira templates gerais que os adaptadores convertem para a notação de cada Harness. 🟢

## Opções apresentadas ao usuário
1. **Adotar paradigma natural da stack (transformacional - Hexagonal)**
   - Consequências: Isolamento total do domínio do sistema novo em Python OO contra ganchos de IDE, fácil extensibilidade, testabilidade robusta de lógica através de mocks e zero acoplamento de infraestrutura.
2. **Forçar paradigma similar ao legado (conservador - Shell Script)**
   - Consequências: Manutenção de toda a automação em scripts Shell (.sh), resolvendo o suporte a novos harnesses via estruturas extensivas de `if/else` imperativos dentro de cada script.
3. **Híbrido (equilibrado)**
   - Consequências: Core em scripts de shell rápidos de milissegundos para evitar cold start de execução do interpretador, mas delegando a lógica complexa de processamento conceitual para módulos Python chamados em background.

## Decisão do usuário
- **Escolha**: 1 (Adotar core agnóstico em Python com arquitetura Hexagonal / Portas e Adaptadores). 🟢
- **Justificativa do usuário**: Foco estratégico em longevidade, manutenibilidade, saúde do repositório a longo prazo e eliminação máxima de dívida técnica, baseando-se em conceitos estritos de alta coesão, baixo acoplamento e programação orientada a objetos. 🟢
- **Decidido em**: 2026-06-23T14:05:00Z 🟢

## Apetite derivado
- `derived_appetite`: transformational 🟢

## Implicações pendentes para próximos agentes
| Agente | Implicação | Como honrar |
|---|---|---|
| Curator | Separação de acoplamento de IDE | Identificar trechos de parse de payloads JSON de IDE no legado e classificá-los como lógica do adaptador, não de domínio. |
| Strategist | Roadmaps técnicos de transição | Propor estratégia de coexistência paralela que mantenha os hooks do Claude active enquanto a nova CLI Python é construída e homologada. |
| Designer | Modelagem orientada a objetos e adaptadores | Desenhar as Portas, as Entidades de Domínio do compilador e os adaptadores específicos para Claude, Gemini e Antigravity. |
| Inspector | Testabilidade e cobertura | Definir testes de paridade baseados em mocks de sistema de arquivos e subprocessos para validar a CLI em Python de forma independente. |

## Notas
Para evitar gargalo de latência (cold start) do Python a cada gravação do editor, a implementação física dos adaptadores de IDE pode se manter como scripts de shell leves (`.sh`) que apenas despacham a chamada em background ou chamam a CLI Python de forma assíncrona.
