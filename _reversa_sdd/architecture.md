# Visão Geral Arquitetural (Architecture) — harness

> Gerado pelo Architect em 2026-06-23 (Re-extração após Feature 002)
> Nível de Documentação: **Completo**

Este documento apresenta a síntese arquitetural do núcleo `harness-core`, consolidando o estilo estrutural, dependências, dívidas técnicas e matriz de rastreabilidade.

---

## 🗺️ 1. Estilo de Arquitetura

O `harness-core` adota o padrão de **Arquitetura Hexagonal (Portas e Adaptadores)**. A regra de negócio principal (composta por domínios e serviços de ciclo de vida) é mantida isolada de acoplamentos externos de infraestrutura, comunicando-se exclusivamente por meio de interfaces (Portas).

Os princípios fundamentais adotados são:
* **Injeção de Dependências:** Serviços como `FormattingService`, `SyncService`, `BootstrapService`, `CommandService` e o novo `DocumentationService` recebem instâncias das suas respectivas Portas (`FileSystemPort`, `GitPort`, `ProcessPort`) via construtor, simplificando os testes unitários.
* **Isolamento de Entrada/Saída:** Adaptadores concretos localizados sob `src/adapters/` gerenciam o acesso ao disco, o tráfego do protocolo Git via subprocessos locais e a execução de formatadores externos.
* **Portabilidade de Interfaces:** A aplicação disponibiliza interfaces complementares: a CLI de terminal (`main.py`) com gerador de documentação e servidor HTTP local, e um servidor de protocolo de contexto MCP (`adapters/mcp/server.py`).

---

## 🏗️ 2. Detalhes de Modelagem C4

Os diagramas de arquitetura detalhados em Mermaid estão divididos nos seguintes artefatos:
1. **Contexto Geral (Nível 1):** Relação do sistema com o desenvolvedor, o agente de IA e os repositórios remotos. Consulte [c4-context.md](file:///Users/iagoleal/dev/harness/_reversa_sdd/c4-context.md).
2. **Arquitetura de Containers (Nível 2):** Detalhamento dos containers lógicos (CLI Python, servidor MCP, ambiente virtual, documentação HTML e disco de persistência). Consulte [c4-containers.md](file:///Users/iagoleal/dev/harness/_reversa_sdd/c4-containers.md).
3. **Estrutura de Componentes (Nível 3):** Detalhamento interno dos sub-serviços do núcleo e seus respectivos adaptadores de infraestrutura. Consulte [c4-components.md](file:///Users/iagoleal/dev/harness/_reversa_sdd/c4-components.md).

---

## 📊 3. Modelo de Entidades e Rastreabilidade

* O modelo de entidades e relacionamentos lógicos do domínio do core está mapeado em [erd-complete.md](file:///Users/iagoleal/dev/harness/_reversa_sdd/erd-complete.md).
* A matriz de impacto mapeando quais componentes de software sustentam os requisitos críticos de negócio e segurança está consolidada em [spec-impact-matrix.md](file:///Users/iagoleal/dev/harness/_reversa_sdd/traceability/spec-impact-matrix.md).

---

## 🔌 4. Integrações Externas e APIs

As únicas conexões de borda do núcleo Python consistem em:
* **Executáveis de Terceiros do Host (Linters/Formatadores):** Chamadas locais via subprocessos de shell (`subprocess.run`) para as ferramentas `ruff format` (Python), `prettier` (frontend) e `rustfmt` (Rust).
* **Protocolo Git (git ls-remote):** Executado via linha de comando local para obter a hash SHA-1 do remote origin correspondente ao HEAD da branch.
* **Servidor HTTP de Rede Local:** Exposição de porta TCP local (`http://localhost:8000`) para servir o arquivo HTML consolidado de documentação via socket.

---

## ⚠️ 5. Dívidas Técnicas Identificadas

Durante a engenharia reversa do sistema, as seguintes fragilidades técnicas foram catalogadas pelo Detective e Architect:

1. **Dependência Implícita de Interpretador Global no Host:**
   - Embora o wrapper `./harness` isole a execução usando a venv dedicada do core, o setup original das dependências em si ainda assume que o host possui um interpretador Python 3 global com as ferramentas `venv` e `pip` ativas.
2. **Falhas Silenciosas nos Formatadores Locais:**
   - Para obedecer à regra de não-bloqueio de salvamentos de arquivos da IA (BR-MIGRAR-006), o formatador captura e silencia todas as exceções internas. Isso impede panes operacionais, mas mascara problemas de PATH corrompido de formatadores (como Prettier ou Ruff ausente no ambiente do host).
3. **Mapeamento de Backlinks baseado em Strings Puras:**
   - O parsing de relações das microdecisões em `DecisionService` que constrói os backlinks do grafo baseia-se em expressões regulares simples. O parser não valida se o ID apontado (`MD-XXXX`) realmente existe na pasta física de decisões, permitindo referências quebradas silenciosas.
