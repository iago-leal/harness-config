---
schemaVersion: 1
generatedAt: "2026-06-23T14:07:00Z"
reversa:
  version: "1.2.43"
kind: target_business_rules
producedBy: curator
hash: "sha256:351cfa858193c30ccef7b24ee3699c3e7179303c6706edf57f83e10c1f23e979"
---

# Target Business Rules

> Catálogo das regras de negócio do legado com decisão de migração: MIGRAR, DESCARTAR ou DECISÃO HUMANA.
> Cada item rastreia para a origem em `_reversa_sdd/` e respeita o `paradigm_decision.md`.

## Resumo
- Total de regras analisadas: 18
- MIGRAR: 15
- DESCARTAR: 2 (detalhe em `discard_log.md`)
- DECISÃO HUMANA: 1

---

## Regras MIGRAR

### BR-MIGRAR-001: Sincronização unificada de hooks Git
- **Origem**: `_reversa_sdd/bootstrap/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: O processo de bootstrap deve configurar e sincronizar os ganchos de git (`pre-commit`, `post-merge`) respeitando a diretiva `core.hooksPath` do Git local.
- **Justificativa de migração**: Regra crítica de infraestrutura que garante a consistência do ambiente de desenvolvimento.
- **Compatibilidade com paradigma alvo**: Será implementada no módulo compilador Python que grava os adaptadores nos locais adequados.

### BR-MIGRAR-002: Prevenção de commits com índice defasado
- **Origem**: `_reversa_sdd/bootstrap/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: Impede o pre-commit se o índice de microdecisões em `microdecisoes.md` estiver defasado em relação às fichas individuais.
- **Justificativa de migração**: Evita inconsistências conceituais no Git.
- **Compatibilidade com paradigma alvo**: Mantida inalterada na lógica do pre-commit.

### BR-MIGRAR-003: Cache TTL de sincronia de rede
- **Origem**: `_reversa_sdd/sync-check/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: A consulta à rede via `git ls-remote` é limitada a uma execução a cada 24 horas por repositório, gravando o timestamp e o commit hash em arquivo de cache.
- **Justificativa de migração**: Essencial para manter a inicialização do agente rápida (sem gargalos de rede).
- **Compatibilidade com paradigma alvo**: A verificação de cache e cálculo de expiração será feita via `FileSystemClient` do core Python.

### BR-MIGRAR-004: Sincronia remota read-only
- **Origem**: `_reversa_sdd/sync-check/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: Nunca executa `git fetch` ou `git pull` de forma silenciosa e invisível para sincronia remota (opera apenas detectando commits novos via `ls-remote`).
- **Justificativa de migração**: Preserva a integridade local do código do desenvolvedor.
- **Compatibilidade com paradigma alvo**: Lógica isolada no adaptador de rede read-only.

### BR-MIGRAR-005: Não-bloqueio de ganchos em falha de rede/git
- **Origem**: `_reversa_sdd/sync-check/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: Erros em repositórios isolados ou queda de conexão de internet não devem derrubar a CLI; o status code de saída é sempre `0`.
- **Justificativa de migração**: Garante resiliência do boot sob qualquer condição de rede.
- **Compatibilidade com paradigma alvo**: Tratamento de exceções geral no core Python.

### BR-MIGRAR-006: Não-bloqueio absoluto do hook de formatação
- **Origem**: `_reversa_sdd/format-on-edit/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: O gancho de formatação deve retornar status `0`, impedindo que bugs do compilador travem a escrita de arquivos da IA.
- **Justificativa de migração**: Crítico para usabilidade operacional.
- **Compatibilidade com paradigma alvo**: Tratado no adaptador de saída.

### BR-MIGRAR-007: Blindagem de diretórios pessoais e notas
- **Origem**: `_reversa_sdd/format-on-edit/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: Nunca formata ou altera arquivos no HOME, pasta de Notas Obsidian (`~/Notas`) ou arquivos do Claude (`~/.claude`).
- **Justificativa de migração**: Salvaguarda contra perda ou alteração acidental de dados pessoais.
- **Compatibilidade com paradigma alvo**: Regra implementada no core em Python comparando caminhos absolutos com parâmetros carregados no TOML.

### BR-MIGRAR-008: Precedência de binários locais
- **Origem**: `_reversa_sdd/format-on-edit/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: Resolve executáveis priorizando os pacotes locais do projeto (ex: `.venv/bin/ruff`, `node_modules/.bin/prettier`) antes de cair para os globais.
- **Justificativa de migração**: Garante que o formatador siga a versão estrita configurada no projeto de trabalho.
- **Compatibilidade com paradigma alvo**: Lógica encapsulada no serviço resolvedor em Python.

### BR-MIGRAR-009: Opt-out local via arquivo `.no-autoformat`
- **Origem**: `_reversa_sdd/format-on-edit/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: Desativa formatação automática se `.no-autoformat` estiver na raiz do projeto.
- **Justificativa de migração**: Dá controle ao desenvolvedor sobre quais projetos não devem sofrer autoformatação.
- **Compatibilidade com paradigma alvo**: Verificação no FileSystemClient do Python.

### BR-MIGRAR-010: Estrutura semântica estrita da microdecisão
- **Origem**: `_reversa_sdd/microdecisoes/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: Fichas sob `decisoes/` devem conter H1, metadados (`gancho`, `relacoes`), e blocos demarcados (`D`, `PORQUÊ`, `DESCARTADO`, `ESTADO`).
- **Justificativa de migração**: Garante a consistência estrutural dos dados de design do projeto.
- **Compatibilidade com paradigma alvo**: Implementado utilizando interpretador de Markdown no core Python.

### BR-MIGRAR-011: Rejeição de metadados malformados
- **Origem**: `_reversa_sdd/microdecisoes/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: O parser deve acusar erros se as relações de design declaradas possuírem tamanho de tokens diferente de 2 (ex: `refina MD-0002`).
- **Justificativa de migração**: Evita que links malformados quebrem o grafo de backlinks.
- **Compatibilidade com paradigma alvo**: Validação no parser de metadados no core.

### BR-MIGRAR-012: Teto de 2 rodadas na clarificação PCCP
- **Origem**: `_reversa_sdd/comandos-customizados/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: Limita a 2 rodadas de diálogo interativo no comando `/clarificar` para evitar loops de IAs.
- **Justificativa de migração**: Regra crucial de economia de tokens e produtividade.
- **Compatibilidade com paradigma alvo**: Lógica no fluxo conceitual de interação.

### BR-MIGRAR-013: Precedência de travamento (/travar)
- **Origem**: `_reversa_sdd/comandos-customizados/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: A codificação de demandas complexas exige travamento de escopo por comando do usuário ou fallback por esgotamento de rodadas.
- **Justificativa de migração**: Protege o escopo de implementações parciais.
- **Compatibilidade com paradigma alvo**: Mapeado na controladora de prompts.

### BR-MIGRAR-014: Isolamento de diretório no encerramento
- **Origem**: `_reversa_sdd/comandos-customizados/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: Restringe commits e alterações apenas na árvore física do repositório ativo.
- **Justificativa de migração**: Evita commits acidentais em outros repositórios de infraestrutura.
- **Compatibilidade com paradigma alvo**: Validado na interface de Git do Python.

### BR-MIGRAR-015: Âncora de integridade Git no estado
- **Origem**: `_reversa_sdd/comandos-customizados/requirements.md` § Regras de Negócio
- **Confiança original**: 🟢 CONFIRMADO
- **Descrição**: Grava o HEAD commit hash no `ESTADO-DA-SESSAO.md` no fechamento para validar consistência na retomada da sessão.
- **Justificativa de migração**: Impede regressão de código do agente.
- **Compatibilidade com paradigma alvo**: Implementado via módulo Git no Python.

---

## Regras DESCARTAR (resumo)

| ID | Origem | Motivo curto | Vínculo a paradigma? |
| :--- | :--- | :--- | :---: |
| **BR-DESCARTAR-001** | `_reversa_sdd/format-on-edit/contracts.md` | Retorno de JSON fixo em stdout específico para ganchos do Claude Code. | Sim |
| **BR-DESCARTAR-002** | `_reversa_sdd/format-on-edit/requirements.md` | Mapeamento físico rígido a diretórios do Claude (`~/.claude/` e `settings.json`). | Sim |

---

## Regras DECISÃO HUMANA

### BR-HUMANA-001: Mecanismo de Invocação de Hooks Cross-Harness
- **Origem**: `_reversa_sdd/migration/migration_brief.md` § Stack Alvo
- **Tipo de ambiguidade**: dependência de stakeholder
- **Descrição**: O Claude Code executa hooks de forma nativa via `settings.json`. O Gemini e o Antigravity CLI operam sob modelos diferentes. Como disparar o format-on-edit e o sync-check nesses harnesses sem hooks de IDE equivalentes?
- **Opções**:
  * **Opção A:** Criar um script wrapper de terminal genérico (ex: `harness run gemini-cli`) que executa os hooks locais antes e depois da chamada da ferramenta.
  * **Opção B:** Expor as lógicas de formatador e sync-check como um servidor **MCP (Model Context Protocol)** local. Como tanto o Gemini CLI quanto o Antigravity integram com MCP servers, eles chamam a formatação/sync-check como ferramentas de forma transparente.
- **Recomendação do Curator**: **Opção B (Servidor MCP)**. Isola a lógica como um serviço local agnóstico, estendendo a compatibilidade do ambiente com qualquer IA compatível com protocolo MCP.
- **Status**: PENDENTE
