# Matriz de Impacto de Especificações (Spec Impact Matrix) — harness-core

> Gerado pelo Architect em 2026-06-23 (Re-extração após Feature 002)
> Nível de Documentação: **Completo**

Esta matriz correlaciona os componentes lógicos e adaptadores do `harness-core` com as regras de negócio de domínio e requisitos funcionais afetados.

---

## 📊 Matriz de Correlação e Impacto

A tabela abaixo mapeia o impacto de modificações nos componentes sobre o sistema:

| Componente | Arquivo de Origem | Regras de Domínio Afeitas | Requisitos Funcionais | Severidade |
| :--- | :--- | :--- | :--- | :--- |
| **BootstrapService** | `service.py` (bootstrap) | n/a | Instalação idempotente de ganchos Git. | MEDIUM |
| **FormattingService** | `service.py` (formatting) | **RN-03** (Não-Bloqueio)<br/>**RN-04** (Proteção de Pastas)<br/>**RN-05** (Precedência Local)<br/>**RN-06** (Opt-out) | Formatação de arquivos modificados e linting automático. | HIGH |
| **SyncService** | `service.py` (sync) | **RN-01** (Janela TTL)<br/>**RN-02** (Resiliência Offline) | Validação automática de sincronia em SessionStart. | HIGH |
| **DecisionService** | `service.py` (decisions) | n/a | Parse do YAML, validação do grafo e backlinks. | MEDIUM |
| **CommandService** | `service.py` (commands) | **RN-07** (Âncora de Sessão Git) | Execução de slash-commands (resume, encerrar-sessao, handoff). | HIGH |
| **DocumentationService** | `service.py` (documentation) | **RN-08** (Sincronização)<br/>**RN-09** (Autossuficiência)<br/>**RN-10** (Introspecção) | Geração de documentação em HTML standalone e exposição local. | MEDIUM |

---

## 🛠️ Detalhamento de Impacto Crítico

1. **Alterações no `FormattingService` (Formatação):**
   - **Risco:** Qualquer quebra de código neste serviço pode travar a gravação de arquivos na IDE, violando a regra de não-bloqueio (**RN-03**).
   - **Severidade:** **HIGH**. Modificações exigem testes exaustivos na suite pytest (`test_formatting.py`).
2. **Alterações no `SyncService` (Sincronização):**
   - **Risco:** Falha de rede que cause pane não capturada no boot do agente de IA local.
   - **Severidade:** **HIGH**. Viola a resiliência offline (**RN-02**).
3. **Alterações no `CommandService` (Comandos):**
   - **Risco:** Corrupção do estado no arquivo `ESTADO-DA-SESSAO.md`, invalidando a retomada de features do ciclo forward.
   - **Severidade:** **HIGH**.
4. **Alterações no `DocumentationService` (Documentação):**
   - **Risco:** Falha de parser ou falta de arquivos de metadados legados abortar a build de documentação ou a inicialização do HTTP server local.
   - **Severidade:** **MEDIUM**.
