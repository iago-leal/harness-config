---
schemaVersion: 1
generatedAt: 2026-06-23T14:17:00Z
reversa:
  version: "1.2.43"
kind: topology_decision
producedBy: designer
hash: "sha256:552115669ef2c36073b58b6f9c1277a9018a5d0092caa250e4ce46028ac52c90"
---

# Topology Decision

> Decisão consciente sobre como organizar o sistema novo: preservar a topologia do legado, adotar uma topologia moderna ou aplicar um híbrido.
> Este artefato é leitura obrigatória do próprio Designer (para decompor bounded contexts) e do agente de codificação (para criar a árvore de pastas).

## Topologia do legado detectada
- **Padrão organizacional**: Monolito sem fronteiras claras de domínio, organizado por pastas de utilidade/infraestrutura física (`bin/`, `hooks/`, `commands/`, `decisoes/`).
- **Confiança**: 🟢 CONFIRMADO
- **Evidências**:
  - `_reversa_sdd/inventory.md` descreve scripts utilitários isolados em `bin/` (`bootstrap.sh`, `sync-check.sh`, `gerar-index-decisoes.sh`).
  - `_reversa_sdd/architecture.md` detalha o acoplamento do gancho do editor em `hooks/format-on-edit.sh` e o armazenamento de decisões conceituais sob `decisoes/`.
- **Mapa da árvore legada** (resumido):
  ```
  harness-config/
  ├── bin/
  │   ├── bootstrap.sh
  │   ├── sync-check.sh
  │   └── gerar-index-decisoes.sh
  ├── commands/
  │   ├── clarificar.md
  │   ├── encerrar-sessao.md
  │   ├── handoff.md
  │   └── resume.md
  ├── decisoes/
  │   ├── _cabecalho.md
  │   └── MD-0001.md...MD-0017.md
  ├── hooks/
  │   └── format-on-edit.sh
  └── settings.json
  ```

## Diagnóstico estrutural
- **Acoplamento**: alto. Os ganchos e comandos estão acoplados diretamente ao Claude CLI (`settings.json` e formato de prompts em Markdown compatível com Claude).
- **Coesão por módulo**: baixa. A lógica de formatação de arquivos e validação do Git está misturada no mesmo script shell com formatações do sistema de arquivos e comandos do host.
- **Módulos órfãos / mortos**: nenhum.
- **Camadas redundantes**: nenhuma.
- **Violações de fronteira**: A inversão de backlinks de decisões (`gerar-index-decisoes.sh`) manipula diretamente cabeçalhos MD usando scripts de regex estruturados (awk/sed) sem validação de integridade semântica.
- **Mistura de paradigmas/estilos**: scripts procedural imperativos em Bash misturados com manipulação de metadados.
- **Avaliação geral**: problemática devido ao alto acoplamento com Claude Code e complexidade de manutenção do código procedural em Bash.

## Topologia moderna proposta
- **Padrão**: Arquitetura Hexagonal (Portas e Adaptadores) estruturada em Módulos de Domínio (Python OOP).
- **Justificativa**: A modularidade de um compilador de ganchos exige alta coesão de domínio (regras de sync, lint e decisões) e baixo acoplamento físico nas bordas do sistema (adaptadores de IDEs/Harnesses específicos). A POO em Python viabiliza esse desacoplamento de forma robusta por meio de herança e injeção de dependências.
- **Ganhos concretos esperados**:
  - Testabilidade unitária e funcional com Mocks de sistema de arquivos e subprocessos de rede Git.
  - Baixo acoplamento: novas ferramentas ou CLIs (Gemini, Antigravity) necessitam apenas da criação de novos adaptadores de entrada (como comandos MCP ou CLI simples), mantendo as regras de negócio intocadas no Core.
  - Manutenibilidade a longo prazo sob conceitos de alta coesão.
- **Custo / risco**:
  - Pequeno overhead inicial para implementar as classes e interfaces em Python.
  - Latência (cold start) que deve ser mitigada via wrappers leves.
- **Esboço da árvore proposta**:
  ```
  harness-core/
  ├── src/
  │   ├── core/                  # Núcleo de domínio (OOP, independente de infra/harness)
  │   │   ├── bootstrap/         # Caso de uso: bootstrap de ganchos Git locais
  │   │   ├── formatting/        # Caso de uso: formatação de arquivos com Ruff, Prettier, etc.
  │   │   ├── sync/              # Caso de uso: sync-check de repositórios remotos
  │   │   ├── decisions/         # Caso de uso: parser e validador do grafo de microdecisões
  │   │   └── commands/          # Caso de uso: interpretador agnóstico de slash-commands
  │   ├── adapters/              # Adaptadores de entrada e saída (infra, harnesses)
  │   │   ├── cli/               # CLI Python agnóstica
  │   │   ├── mcp/               # Servidor MCP local (FastMCP) para Gemini, Claude e Antigravity
  │   │   ├── git/               # Adaptador Git local
  │   │   └── fs/                # Adaptador de sistema de arquivos local
  │   └── main.py                # Entrypoint do sistema
  ├── harness.toml               # Configurações globais portáveis
  └── requirements.txt
  ```

## Opções apresentadas ao usuário
1. **Preservar topologia legada** (conservador)
   - Consequências: mantém o mapa mental de scripts lineares separados por utilitários, mas perpetua a dificuldade de teste e o acoplamento físico com o Claude.
2. **Adotar topologia moderna proposta** (transformacional)
   - Consequências: rompe completamente com o débito estrutural de scripts imperativos Bash legados; implementa Hexagonal real em Python OOP; maximiza robustez e flexibilidade de IAs locais.
3. **Híbrido** (equilibrado)
   - Consequências: Mantém o Core em scripts lineares Bash com lógica de negócios, mas isola o parse de JSON de IDEs em scripts utilitários auxiliares em Python sem POO.

## Decisão do usuário
- **Escolha**: 2 (Adotar topologia moderna proposta - Hexagonal em Python OOP + Adaptadores MCP/CLI)
- **Justificativa do usuário**: Opção recomendada para romper com o acoplamento legado, isolar o domínio conceitual de ganchos e indexadores de decisões, simplificar a evolução cross-harness e viabilizar testes unitários robustos de forma isolada.
- **Decidido em**: 2026-06-23T14:17:08Z

## Mapeamento legado → novo
| Módulo / pasta legada | Bounded context novo | Tipo | Observações |
|---|---|---|---|
| `bin/bootstrap.sh` | `bootstrap` | dividido | A lógica de bootstrap de ganchos Git vira caso de uso no core, enquanto os scripts adaptadores por IDE viram infra. |
| `bin/sync-check.sh` | `sync` | dividido | Lógica de checagem/caching no core Python; adaptador MCP vira interface. |
| `hooks/format-on-edit.sh` | `formatting` | dividido | Resolvedor de formatadores/extensões no core Python; adaptador MCP vira interface. |
| `bin/gerar-index-decisoes.sh` + `decisoes/` | `decisions` | fundido | O parser Markdown de microdecisões e indexador de backlinks OO viram o domínio `decisions`. |
| `commands/` | `commands` | preservado | Slash-commands interpretados de forma agnóstica via adaptador de prompts. |
| `settings.json` | (descartado) | removido | Acoplamento direto à IDE, substituído por `harness.toml` configurável e adaptadores. |

## Implicações pendentes para próximos passos do Designer
| Etapa do Designer | Implicação | Como honrar |
|---|---|---|
| Bounded contexts | Decomposição em 5 contextos coerentes | Definir responsabilidades para `bootstrap`, `sync`, `formatting`, `decisions` e `commands`. |
| target_architecture | Injeção de dependências | Desenhar Portas para interfaces de FS e Git e Adaptadores correspondentes no módulo de infraestrutura. |
| target_domain_model | Entidades e Casos de Uso | Modelar `Decision` como agregado rico com backlinks validados. |
| target_data_model | Configuração de disco | Mapear o formato do `harness.toml` e cache de arquivos locais. |

## Notas
A estrutura proposta separa completamente a interface de chamada (MCP, CLI ou Bash Ganchos rápidos) das lógicas de validação e formatação que residem no core em Python OOP.
