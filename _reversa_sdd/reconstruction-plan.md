# Reconstruction Plan — harness

**Fonte:** migração
**Paradigma alvo:** Orientação a Objetos com Injeção de Dependências (Core Python) + Hexagonal
**Topologia:** Opção 2: Adotar topologia moderna proposta (Hexagonal em Python OOP + Adaptadores MCP/CLI)
**Stack:** Python 3.10+, FastMCP, Ruff/Prettier/Rustfmt de host
**Estratégia:** Estratégia B: Parallel Run (Coexistência de Homologação)
**Gerado em:** 2026-06-23
**Status:** 14 tarefas | 14 concluídas | 0 pendentes

---

## Alertas de pré-voo

> Revise antes de iniciar. Itens REFERIDOS À CODIFICAÇÃO em `ambiguity_log.md` que afetam tarefas específicas estão marcados.

Nenhum item bloqueante. Pode iniciar.

---

## Tarefas

### Tarefa 01 — Setup do Projeto Novo
**Status:** done
**Lê:** `_reversa_sdd/migration/topology_decision.md`, `_reversa_sdd/migration/paradigm_decision.md`
**Constrói:** estrutura inicial de pastas/módulos, configuração base, dependências mínimas (`pyproject.toml` or `requirements.txt`)
**Pronto quando:** Esqueleto do repositório novo bate com a topologia aprovada (src/core, src/adapters, etc.) e o paradigma OO hexagonal.

---

### Tarefa 02 — Schema do Banco Alvo
**Status:** done
**Lê:** `_reversa_sdd/migration/target_data_model.md`
**Constrói:** Definições do arquivo de configuração do sistema (`harness.toml`) e do diretório de cache
**Pronto quando:** O modelo de configuração do `harness.toml` e cache em disco local está definido e estruturado conforme o modelo de dados alvo. (Obs: sem banco de dados relacional clássico).

---

### Tarefa 03 — Plano de Migração de Dados
**Status:** done
**Lê:** `_reversa_sdd/migration/data_migration_plan.md`, `_reversa_sdd/migration/target_data_model.md`
**Constrói:** Script utilitário em Python para conversão física de arquivos de decisões Markdown legadas (injeção de metadados Front-matter YAML)
**Pronto quando:** Automação de conversão testada localmente em lote representativo de decisões legadas para o novo formato Markdown com YAML.

---

### Tarefa 04 — Entidades de Domínio Alvo
**Status:** done
**Lê:** `_reversa_sdd/migration/target_domain_model.md`, `_reversa_sdd/migration/target_business_rules.md`
**Constrói:** classes de domínio em `src/core/domain/` (entidades, agregados como `Decision` e `Session`, regras de integridade)
**Pronto quando:** Core domain model implementado e 100% coberto por testes unitários locais usando mocks.

---

### Tarefa 05 — Adaptadores de Infraestrutura (Portas de Saída)
**Status:** done
**Lê:** `_reversa_sdd/migration/target_architecture.md` (seções adaptadores de infraestrutura / saída)
**Constrói:** Portas de saída (`FileSystemPort`, `GitPort`, `ProcessPort`) em `src/core/ports/` e seus adaptadores físicos (`LocalFileSystemAdapter`, `SubprocessGitAdapter`, `HostFormatterAdapter`) em `src/adapters/`
**Pronto quando:** Os adaptadores de infraestrutura comunicam-se fisicamente com o host (executando git, chamando formatadores do host e gravando arquivos) e batem com suas respectivas portas abstratas.

---

### Tarefa 06 — Módulo de Registro de Decisões (DecisionService)
**Status:** done
**Lê:** `_reversa_sdd/migration/target_architecture.md` (seção `DecisionService`), `_reversa_sdd/migration/target_domain_model.md`, `_reversa_sdd/migration/target_business_rules.md`
**Constrói:** caso de uso `DecisionService` em `src/core/decisions/`
**Pronto quando:** O serviço de domínio lê os Markdowns de decisão, monta o grafo em memória, valida integridade de backlinks e gera o sumário consolidado de decisões corretamente.

---

### Tarefa 07 — Módulo de Formatação de Código (FormattingService)
**Status:** done
**Lê:** `_reversa_sdd/migration/target_architecture.md` (seção `FormattingService`), `_reversa_sdd/migration/target_domain_model.md`, `_reversa_sdd/migration/target_business_rules.md`
**Constrói:** caso de uso `FormattingService` em `src/core/formatting/`
**Pronto quando:** Formatação automática invoca corretamente Ruff/Prettier/Rustfmt conforme as extensões e regras do arquivo de opt-out `.no-autoformat`.

---

### Tarefa 08 — Módulo de Sincronização de Repositório (SyncService)
**Status:** done
**Lê:** `_reversa_sdd/migration/target_architecture.md` (seção `SyncService`), `_reversa_sdd/migration/target_domain_model.md`, `_reversa_sdd/migration/target_business_rules.md`
**Constrói:** caso de uso `SyncService` em `src/core/sync/`
**Pronto quando:** Validação de commits locais contra a branch remota funciona de forma isolada com cache local de expiração em 24h.

---

### Tarefa 09 — Módulo de Sessão Interativa e Slash-Commands (CommandService)
**Status:** done
**Lê:** `_reversa_sdd/migration/target_architecture.md` (seção `CommandService`), `_reversa_sdd/migration/target_domain_model.md`, `_reversa_sdd/migration/target_business_rules.md`
**Constrói:** caso de uso `CommandService` em `src/core/commands/`
**Pronto quando:** Interpretador agnóstico de comandos (`/clarificar`, `/encerrar-sessao`, `/handoff`, `/resume`) e geração de templates markdown está operacional.

---

### Tarefa 10 — Módulo de Bootstrap de Ganchos (BootstrapService)
**Status:** done
**Lê:** `_reversa_sdd/migration/target_architecture.md` (seção `BootstrapService`), `_reversa_sdd/migration/target_domain_model.md`, `_reversa_sdd/migration/target_business_rules.md`
**Constrói:** caso de uso `BootstrapService` em `src/core/bootstrap/`
**Pronto quando:** Lógica de orquestração de instalação de hooks Git locais no repositório está implementada.

---

### Tarefa 11 — Adaptador de Interface CLI e Ganchos (CliAdapter & GitHookAdapter)
**Status:** done
**Lê:** `_reversa_sdd/migration/target_architecture.md` (seções `CliAdapter` e `GitHookAdapter`)
**Constrói:** `src/adapters/cli/` (`main.py`) e wrappers leves de shell em `src/adapters/git/hooks/`
**Pronto quando:** Chamadas via CLI executam comandos e os hooks git leves desviam chamadas para a CLI Python de forma assíncrona (mitigando latência).

---

### Tarefa 12 — Servidor MCP (McpServerAdapter)
**Status:** done
**Lê:** `_reversa_sdd/migration/target_architecture.md` (seção `McpServerAdapter`), `_reversa_sdd/migration/target_domain_model.md`
**Constrói:** `src/adapters/mcp/` utilizando FastMCP
**Pronto quando:** Servidor expõe ferramentas de formatação, sync e grafo de decisões para qualquer harness de IA conectável.

---

### Tarefa 13 — Cutover
**Status:** done
**Lê:** `_reversa_sdd/migration/cutover_plan.md`
**Constrói:** migração definitiva de ganchos git e desligamento dos scripts bash do repositório original
**Pronto quando:** O sistema novo está instalado em modo ativo oficial no repositório de desenvolvimento e os hooks legados em Bash foram congelados ou arquivados.

---

### Tarefa 14 — Validação de Paridade
**Status:** done
**Lê:** `_reversa_sdd/migration/parity_specs.md`, `_reversa_sdd/migration/parity_tests/01-sync-check.feature`, `_reversa_sdd/migration/parity_tests/02-format-on-edit.feature`, `_reversa_sdd/migration/parity_tests/03-decision-graph.feature`, `_reversa_sdd/migration/parity_tests/04-interactive-commands.feature`
**Constrói:** Testes automatizados rodando em paralelo nos dois sistemas e validação fina de equivalência operacional
**Pronto quando:** Todos os 4 cenários de teste Gherkin rodam com sucesso tanto no legado quanto na nova implementação Python Hexagonal sem divergências.
