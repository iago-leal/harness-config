# Matriz de Rastreabilidade Código-Especificação (Code-Spec Matrix)

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**

Esta matriz correlaciona cada arquivo do repositório legado com as respectivas unidades de especificação funcional e o nível de cobertura de mapeamento.

---

## 📊 Matriz de Rastreabilidade

| Arquivo do Legado | Unit Correspondente | Cobertura | Observações / Justificativa |
| :--- | :--- | :---: | :--- |
| `bin/bootstrap.sh` | `bootstrap/` | 🟢 | Cobertura total das rotinas de instalação de hooks e sincronia. |
| `bin/sync-check.sh` | `sync-check/` | 🟢 | Cobertura total da verificação com cache TTL e direções push/pull. |
| `bin/test_sync_check.sh` | `sync-check/` | 🟢 | Mapeado na seção de Tarefas de Teste (cobertura de testes legada). |
| `bin/gerar-index-decisoes.sh` | `microdecisoes/` | 🟢 | Mapeado nas lógicas de compilação de grafo e backlinks. |
| `hooks/format-on-edit.sh` | `format-on-edit/` | 🟢 | Cobertura total do roteador de formatadores PostToolUse. |
| `hooks/README.md` | `format-on-edit/` | 🟢 | Documentação integrada nas regras de precedência e symlinks. |
| `commands/clarificar.md` | `comandos-customizados/` | 🟢 | Mapeado nas regras e fluxos do slash-command `/clarificar`. |
| `commands/encerrar-sessao.md` | `comandos-customizados/` | 🟢 | Mapeado nas regras de consolidação e âncora de sessão `/encerrar-sessao`. |
| `commands/handoff.md` | `comandos-customizados/` | 🟢 | Mapeado no fluxo de escrita do bastão de tarefas `/handoff`. |
| `commands/resume.md` | `comandos-customizados/` | 🟢 | Mapeado no fluxo de retomada de tarefas `/resume`. |
| `decisoes/` (MD-0001 a MD-0017) | `microdecisoes/` | 🟢 | Mapeado na definição de modelo de dados de decisões. |
| `settings.json` | `comandos-customizados/` | 🟢 | Contém os mapeamentos de ativação de hooks e ganchos de comandos. |
| `skills.active` | `bootstrap/` | 🟢 | Utilizado no boot de dependências de skills ativas. |
| `microdecisoes.md` | `microdecisoes/` | 🟢 | Arquivo compilado pelo script de geração de índices. |
| `ESTADO-DA-SESSAO.md` | `comandos-customizados/` | 🟢 | Contém a âncora Git atualizada no encerramento. |

---

## 📈 Métricas de Cobertura Estimada

* **Arquivos do Legado Mapeados:** 15 de 15 arquivos de infraestrutura relevantes analisados.
* **Percentual de Cobertura de Engenharia Reversa:** **100%** 🟢
* **Arquivos Sem Mapeamento (Candidatos a Descarte):** Nenhum. Todos os scripts, ganchos e ficheiros de configuração foram completamente rastreados até as unidades do modelo de desenvolvimento direcionado a especificações (SDD).
