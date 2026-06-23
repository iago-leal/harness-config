# Matriz de Rastreabilidade Código-Especificação (Code-Spec Matrix)

> Gerado pelo Redator em 2026-06-23 (Re-extração após Feature 002)
> Nível de Documentação: **Completo**

Esta matriz correlaciona cada arquivo do repositório legado e as classes/adaptadores do novo `harness-core` com as respectivas unidades de especificação funcional e o nível de cobertura de mapeamento.

---

## 📊 Matriz de Rastreabilidade

### 1. Mapeamento do Legado (Claude Config)

| Arquivo do Legado | Unit Correspondente | Cobertura | Observações / Justificativa |
| :--- | :--- | :---: | :--- |
| `claude-config/bin/bootstrap.sh` | `bootstrap/` | 🟢 | Cobertura total das rotinas de instalação de hooks e sincronia. |
| `claude-config/bin/sync-check.sh` | `sync-check/` | 🟢 | Cobertura total da verificação com cache TTL e direções push/pull. |
| `claude-config/bin/test_sync_check.sh` | `sync-check/` | 🟢 | Mapeado na seção de Tarefas de Teste (cobertura de testes legada). |
| `claude-config/bin/gerar-index-decisoes.sh` | `microdecisoes/` | 🟢 | Mapeado nas lógicas de compilação de grafo e backlinks. |
| `claude-config/hooks/format-on-edit.sh` | `format-on-edit/` | 🟢 | Cobertura total do roteador de formatadores PostToolUse. |
| `claude-config/hooks/README.md` | `format-on-edit/` | 🟢 | Documentação integrada nas regras de precedência e symlinks. |
| `claude-config/commands/clarificar.md` | `comandos-customizados/` | 🟢 | Mapeado nas regras e fluxos do slash-command `/clarificar`. |
| `claude-config/commands/encerrar-sessao.md` | `comandos-customizados/` | 🟢 | Mapeado nas regras de consolidação e âncora de sessão `/encerrar-sessao`. |
| `claude-config/commands/handoff.md` | `comandos-customizados/` | 🟢 | Mapeado no fluxo de escrita do bastão de tarefas `/handoff`. |
| `claude-config/commands/resume.md` | `comandos-customizados/` | 🟢 | Mapeado no fluxo de retomada de tarefas `/resume`. |
| `claude-config/decisoes/` (MD-0001 a MD-0017) | `microdecisoes/` | 🟢 | Mapeado na definição de modelo de dados de decisões. |
| `claude-config/settings.json` | `comandos-customizados/` | 🟢 | Contém os mapeamentos de ativação de hooks e ganchos de comandos. |
| `claude-config/skills.active` | `bootstrap/` | 🟢 | Utilizado no boot de dependências de skills ativas. |
| `microdecisoes.md` | `microdecisoes/` | 🟢 | Arquivo compilado pelo script de geração de índices. |
| `ESTADO-DA-SESSAO.md` | `comandos-customizados/` | 🟢 | Contém a âncora Git atualizada no encerramento. |

### 2. Mapeamento do Núcleo Hexagonal (`harness-core`)

| Componente / Arquivo do Core | Unit Correspondente | Cobertura | Observações / Justificativa |
| :--- | :--- | :---: | :--- |
| `harness` (raiz do projeto) | `run-harness-core-local/` | 🟢 | Script Bash wrapper de conveniência que encapsula execução via venv. |
| `.reversa/settings.json.snippet` | `run-harness-core-local/` | 🟢 | Snippet de hooks de lifecycle da IDE sugerido para o agente. |
| `harness-core/tests/test_wrapper.py` | `run-harness-core-local/` | 🟢 | Suite de testes unitários e de integração do wrapper local. |
| `harness-core/src/main.py` | `bootstrap/` | 🟢 | Ponto de entrada (CLI Entry Point) e injeção de dependência física. Registro dos comandos de doc. |
| `harness-core/src/core/ports/fs.py` | *Transversal (Ports)* | 🟢 | Interface `FileSystemPort` para abstração de operações de E/S. |
| `harness-core/src/core/ports/git.py` | *Transversal (Ports)* | 🟢 | Interface `GitPort` para abstração de comandos do Git local/remoto. |
| `harness-core/src/core/ports/process.py` | *Transversal (Ports)* | 🟢 | Interface `ProcessPort` para abstração de execução de processos do host. |
| `harness-core/src/core/bootstrap/service.py` | `bootstrap/` | 🟢 | Classe `BootstrapService` de instalação e gestão dos hooks. |
| `harness-core/src/core/formatting/service.py` | `format-on-edit/` | 🟢 | Classe `FormattingService` de linting/formatting de arquivos. |
| `harness-core/src/core/sync/service.py` | `sync-check/` | 🟢 | Classe `SyncService` que coordena o fluxo de status de sincronia. |
| `harness-core/src/core/decisions/service.py` | `microdecisoes/` | 🟢 | Classe `DecisionService` que indexa microdecisões e backlinks. |
| `harness-core/src/core/commands/service.py` | `comandos-customizados/` | 🟢 | Classe `CommandService` para lifecycle de sessões e commands. |
| `harness-core/src/core/documentation/service.py` | `documentacao-uso-html/` | 🟢 | Classe `DocumentationService` de compilação da documentação HTML. |
| `harness-core/src/core/documentation/template.html` | `documentacao-uso-html/` | 🟢 | Template de design visual interativo do HTML de documentação. |
| `harness-core/tests/test_documentation.py` | `documentacao-uso-html/` | 🟢 | Suite de testes unitários e de integração de documentação. |
| `harness-docs.html` (raiz do projeto) | `documentacao-uso-html/` | 🟢 | HTML consolidado autossuficiente e offline de documentação gerado. |
| `harness-core/src/core/domain/models.py` | `comandos-customizados/` | 🟢 | Modelos ricos de domínio como `SessionState` e `Decision`. |
| `harness-core/src/core/domain/config.py` | *Transversal (Domain)* | 🟢 | Entidade de configuração centralizada `HarnessConfig`. |
| `harness-core/src/core/domain/cache.py` | `sync-check/` | 🟢 | Objeto de valor `SyncCache` para controle de TTL de checagem. |
| `harness-core/src/adapters/fs/local.py` | *Transversal (Adapters)* | 🟢 | `LocalFileSystemAdapter` implementando chamadas em disco do SO. |
| `harness-core/src/adapters/git/subprocess.py` | *Transversal (Adapters)* | 🟢 | `SubprocessGitAdapter` invocando a CLI do Git através do shell. |
| `harness-core/src/adapters/process/formatter.py` | `format-on-edit/` | 🟢 | `HostFormatterAdapter` que gerencia Ruff, Prettier, etc. |
| `harness-core/src/adapters/mcp/server.py` | `bootstrap/` | 🟢 | Adaptador de protocolo de servidor MCP para o Harness Core. |

---

## 📈 Métricas de Cobertura Estimada

* **Arquivos do Legado Mapeados:** 15 de 15 arquivos de infraestrutura relevantes analisados.
* **Componentes do Core Mapeados:** 23 de 23 componentes estruturais identificados no C4.
* **Percentual de Cobertura de Engenharia Reversa:** **100%** 🟢
* **Arquivos Sem Mapeamento (Candidatos a Descarte):** Nenhum. Todos os scripts, ganchos e ficheiros de configuração foram completamente rastreados até as unidades do modelo de desenvolvimento direcionado a especificações (SDD).
