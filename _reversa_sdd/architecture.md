# Visão Geral Arquitetural (Architecture) — harness-config

> Gerado pelo Architect em 2026-06-23
> Nível de Documentação: **Completo**

Este documento apresenta a síntese arquitetural do projeto `harness-config`, consolidando os padrões de infraestrutura, as integrações de sistema, dívidas técnicas identificadas e a matriz de impacto.

---

## 🗺️ 1. Estilo de Arquitetura

O `harness-config` é uma **arquitetura de ganchos (hooks) e automação orientada a eventos de ciclo de vida do agente de IA**. O sistema opera de forma desacoplada da CLI do agente (Claude Code), agindo como um interceptor de chamadas do sistema de arquivos e do terminal local.

Os padrões fundamentais são:
* **Desacoplamento Baseado em JSON:** Toda a comunicação entre o host (hooks locais) e o agente de IA é realizada por payloads JSON passados via `stdin`/`stdout`.
* **Persistência Baseada em Arquivos (File-based Storage):** Sem bancos de dados relacionais pesados ou serviços em execução em background. O estado do sistema reside de forma portável em arquivos Markdown e JSON no disco.

---

## 🏗️ 2. Detalhamento C4 (Níveis 1, 2 e 3)

O mapeamento visual completo da arquitetura é dividido nos seguintes diagramas em Mermaid:
1. **Contexto Geral (Nível 1):** Relação do sistema com o desenvolvedor humano, IAs e repositórios remotos. Veja em [c4-context.md](file:///Users/iagoleal/dev/harness/_reversa_sdd/c4-context.md).
2. **Arquitetura de Containers (Nível 2):** Divisão lógica dos componentes (Claude CLI, ganchos de formatação, scripts de automação e disco de persistência). Veja em [c4-containers.md](file:///Users/iagoleal/dev/harness/_reversa_sdd/c4-containers.md).
3. **Estrutura de Componentes de Automação (Nível 3):** Detalhamento interno dos roteadores e validadores locais de ganchos Git e TTL. Veja em [c4-components.md](file:///Users/iagoleal/dev/harness/_reversa_sdd/c4-components.md).

---

## 📊 3. Modelo de Entidades e Rastreabilidade

* O modelo relacional lógico que rege o fluxo de microdecisões e estado está documentado no ERD em [erd-complete.md](file:///Users/iagoleal/dev/harness/_reversa_sdd/erd-complete.md).
* A relação e o impacto de modificações nos componentes de software sobre os requisitos críticos de negócio estão mapeados na Matriz de Impacto em [spec-impact-matrix.md](file:///Users/iagoleal/dev/harness/_reversa_sdd/traceability/spec-impact-matrix.md).

---

## 🔌 4. Integrações Externas e APIs

O sistema não consome APIs Web REST/GraphQL de terceiros tradicionais. Suas únicas interfaces externas são:
* **Git Remote Protocol (ls-remote):** Executado de forma assíncrona/read-only pelo `sync-check.sh` via porta SSH/HTTPS contra o repositório de origem no GitHub.
* **Ferramentas locais de estilo do Host (Host Formatters):** Invocadas como binários compilados executados em subprocessos locais:
  * Python: `ruff format` e `ruff check --fix`
  * Frontend: `prettier --write`
  * Rust: `rustfmt`
  * Shell Script: `shfmt -w`

---

## ⚠️ 5. Dívidas Técnicas Identificadas

Durante a engenharia reversa do sistema, as seguintes fragilidades técnicas foram catalogadas pelo Detective e Architect:

1. **Acoplamento Rígido a Shell Script (Bash):**
   * Toda a lógica de verificação de concorrência, parse de cabeçalhos markdown e backlinks de microdecisões está implementada em código Bash puro (auxiliada por utilitários como `jq`, `sed` e `awk`). Isso torna a manutenção complexa e sensível a pequenas divergências entre interpretadores do macOS (bash 3.2+) e Linux.
2. **Suscetibilidade a Quebras de PATH de Formatadores:**
   * O resolvedor de formatadores (`resolve()` em `format-on-edit.sh`) depende fortemente de links estáveis ou binários locais no `.venv` ou `node_modules`. Versões globais (especialmente prettier sob controle do `nvm` que altera pastas físicas sob troca de versão do node) quebram facilmente o link estável de execução, gerando falhas silenciosas registradas em logs.
3. **Ausência de Testes Automatizados Robustos:**
   * A única cobertura de teste de qualidade existente reside em um arquivo simples `bin/test_sync_check.sh`. Módulos complexos como a lógica de inversão de grafos do `gerar-index-decisoes.sh` e o roteador de formatação `format-on-edit.sh` carecem de suites de teste de fumaça de CI/CD.
4. **Acordo Conceitual em Relações do Grafo:**
   * O parsing de relações em `gerar-index-decisoes.sh` falha de forma silenciosa ou aborta de forma barulhenta apenas se o token tiver tamanho diferente de 2 (commit `b955e17`). Não há validação semântica de integridade referencial se o ID referenciado (`MD-XXXX`) de fato existe em disco.
