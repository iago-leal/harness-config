# Roadmap: harness-core como módulo per-projeto autocontido

> Identificador: `006-harness-core-config-canonica`
> Data: `2026-06-24`
> Requirements: `_reversa_forward/006-harness-core-config-canonica/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A feature é higiene interna mais um contrato de segurança, tudo per-projeto, expresso como delta de **borda** sobre o legado. Três aglomerados de mudança: (i) adicionar uma seção `[session]` ao `harness.toml`, espelhando o padrão `[decisions]` que o ADR 0012 firmou, para que o CLI (`harness-core/src/main.py:193`) e o adapter MCP (`harness-core/src/adapters/mcp/server.py:93`) parem de chumbar o caminho do estado de sessão e passem a lê-lo de `load_config().session`; (ii) remover `load_harness_config` (`main.py:22-42`), cujo único consumidor é o branch `cmd`, fazendo-o ler `active_harness` do `load_config` tipado (fecha a dívida T5); (iii) adicionar um **contrato de footprint** como teste, via um duplo instrumentado de `FileSystemPort` que captura toda escrita e afirma que ela cai dentro do repositório, nunca em `~/.claude` nem em `~/.agent-memory` (RF-03), além de fixar por teste a zona protegida já existente (RF-04). Por fim, registrar uma microdecisão que reverte a intenção "substituto da config global" do `MD-0004`. Nenhum contrato externo muda e não há migração de dados: o default do caminho de sessão permanece `.harness/estado-da-sessao.md`.

## 2. Princípios aplicados

Não há `.reversa/principles.md` neste projeto. Aplicam-se os princípios globais do mantenedor (`~/.claude/CLAUDE.md`):

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Nº 5.1 — Configuração fora do código | `[session]` tira o caminho de sessão do hardcode, como já se fez com `[decisions]` | respeita |
| Nº 5 — Baixo acoplamento / fonte única | Uma via única de config (`load_config`) elimina o drift CLI×MCP e a dívida T5 | respeita |
| Nº 5.2 — Testável e testado | O contrato de footprint adiciona cobertura nova e barulhenta | respeita |
| Nº 4 — Proporcionalidade | `[session]` é convenção fixa de uma chave (como `[decisions]`), não config tunável; o contrato de footprint é barato | respeita (leve tensão de over-config, mitigada pelo precedente da 005) |
| Footprint global zero / reversibilidade | O eixo da feature: nada é escrito fora do repositório | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Criar `SessionSection` em `config.py` (campo `state_file`, default `.harness/estado-da-sessao.md`) e seção `[session]` no `harness.toml`; CLI (`main.py:193`) e MCP (`server.py:93`) leem de `load_config().session.state_file` | Espelha o padrão `[decisions]` (ADR 0012); fonte única remove o drift entre os dois pontos de entrada; honra Princípio 5.1; fecha o resíduo de T2 | (a) manter literal chumbado nos dois sites (drift); (b) seção genérica `[paths]` para tudo (over-config, foge do precedente) | 🟢 |
| D-02 | Remover `load_harness_config` (`main.py:22-42`); o branch `cmd` lê `active_harness` de `load_config(fs).harness.active_harness` | Único consumidor do dict legado é o `cmd`; unifica numa via tipada e fecha T5 | manter as duas vias coexistindo — recusado: é a própria dívida T5 | 🟢 |
| D-03 | Contrato de footprint como **teste**: duplo `RecordingFileSystem` (implementa `FileSystemPort`) captura `write_file`/`write_file_atomic`/`makedirs`/`remove` e afirma que todo caminho resolve dentro da raiz do repo de teste, nunca sob `~/.claude` ou `~/.agent-memory` | RF-03 pede um teste barulhento; a arquitetura hexagonal roteia toda escrita por `FileSystemPort`, então o duplo intercepta tudo; risco de regressão menor que um guard de runtime | (a) guard de runtime no `LocalFileSystemAdapter` (quebraria escritas legítimas como `harness-docs.html` no cwd; over-engineering); (b) teste de integração varrendo o FS real (lento, instável) | 🟡 |
| D-04 | Preservar a zona protegida de `formatting/service.py:20-27` (BR-MIGRAR-007) intacta; o contrato de footprint a fixa por teste | RF-04; a salvaguarda existente não pode regredir | relaxar a blindagem — recusado, contraria o objetivo da feature | 🟢 |
| D-05 | Registrar a reversão do `MD-0004` como nova ficha `MD-NNNN` em `.harness/decisoes/`, com backlink; validada e indexada por `./harness decisions` | RF-05; coerência do histórico de decisões do projeto | não registrar — recusado, deixaria o `MD-0004` ativo e divergente da decisão atual | 🟢 |

> Fronteira de escopo (não-decisões, fora desta feature): G-10 (MCP `process_decisions` deriva `header_file` por `os.path.join`, ignorando `config.decisions.header_file`), T4 (`[formatting]` inerte) e o caminho de cache de sync chumbado (`server.py:41`) são dívidas adjacentes **não** cobertas pelos requisitos da 006. Ficam registradas para visibilidade, sem ação aqui.

## 4. Premissas

Nenhuma. As três `[DÚVIDA]` foram resolvidas na clarify de 2026-06-24 (reframe para módulo per-projeto). Nenhum marcador pendente foi convertido em premissa.

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Loader de config | `harness-core/src/core/domain/config.py` (`_reversa_sdd/architecture.md#1`) | componente-novo | nova `SessionSection` pydantic + campo em `HarnessConfig` |
| Config do projeto | `harness-core/harness.toml` | regra-alterada | nova seção `[session]` com `state_file` |
| CLI composition root (`cmd`) | `harness-core/src/main.py` | regra-alterada | lê caminho de sessão de config; remove `load_harness_config`; lê `active_harness` tipado |
| Adapter MCP `session_command` | `harness-core/src/adapters/mcp/server.py` | regra-alterada | lê caminho de sessão de config (default idêntico) |
| Suíte de testes | `harness-core/tests/` (`helpers.py`, `test_domain.py`, `test_cli.py`, `test_mcp.py`) | componente-novo | contrato de footprint + testes da seção `[session]` e da via única de config |
| `FormattingService` | `harness-core/src/core/formatting/service.py` | inalterado | zona protegida preservada (RF-04) |

## 6. Delta no modelo de dados

- Resumo: **nenhuma** mudança no esquema do estado de sessão (`SessionState`/`SessionNarrative`) nem das decisões. Muda só a **origem** do caminho de sessão (de literal para `config.session.state_file`) e some o default-dict legado de `load_harness_config`. Default do caminho idêntico ao atual, logo o `.harness/estado-da-sessao.md` existente segue válido sem migração.
- Detalhe completo em: `_reversa_forward/006-harness-core-config-canonica/data-delta.md`

## 7. Delta de contratos externos

n/a — esta feature não altera contratos externos. O tool MCP `session_command` mantém nome, parâmetros e comportamento observável; muda apenas a origem interna do caminho de sessão, com default idêntico. Por isso não há diretório `interfaces/`.

## 8. Plano de migração

1. Adicionar `SessionSection` em `config.py` (campo `state_file`, default `.harness/estado-da-sessao.md`) e plugá-la em `HarnessConfig`; adicionar `[session]` ao `harness.toml`.
2. Apontar `main.py:193` e `server.py:93` para `load_config(fs).session.state_file`.
3. Remover `load_harness_config` (`main.py:22-42`); o branch `cmd` passa a usar `load_config(fs)` e `config.harness.active_harness` (linha 214).
4. Criar o duplo `RecordingFileSystem` em `tests/helpers.py` e o teste do contrato de footprint, exercitando os serviços que escrevem artefatos (decisões, sessão, bootstrap de ganchos); somar testes de `[session]` em `test_domain.py` e da leitura de caminho em `test_cli.py`/`test_mcp.py`.
5. Escrever `MD-NNNN` em `.harness/decisoes/` revertendo o `MD-0004`; rodar `./harness decisions` para validar o grafo (zero erros) e reindexar `.harness/microdecisoes.md`.
6. Rodar `pytest` (tudo verde) e smoke: `./harness cmd resume` lê o caminho de sessão da config; o tool MCP `session_command` usa o mesmo default.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Remover `load_harness_config` sem ajustar a leitura de `active_harness` no `cmd` | médio | baixa | D-02 muda a linha 214 na mesma ação; `test_cli.py` cobre o `resume` |
| Drift do caminho de sessão entre CLI e MCP | médio | baixa | D-01: ambos leem `config.session.state_file` (fonte única) |
| Contrato de footprint dar falsa segurança (só cobre o que é exercitado) | médio | média | exercitar todos os serviços que escrevem artefatos e **logar** o que foi coberto (sem corte silencioso, Princípio do mantenedor) |
| Mudar o default do caminho de sessão por engano | alto | baixa | default idêntico ao literal atual; teste de igualdade do default |
| Over-config (`[session]` virar config supérflua) | baixo | baixa | uma chave só, espelhando `[decisions]` já aceito na 005 |

## 10. Critério de pronto

- [ ] `harness.toml` tem `[session]`; `config.py` tem `SessionSection`; CLI e MCP leem o caminho de sessão dela (sem literal chumbado nos dois sites funcionais)
- [ ] `load_harness_config` removido; `grep` não acha usos; `cmd` lê `active_harness` via `load_config`
- [ ] Contrato de footprint existe e falha de forma barulhenta se alguma escrita mirar fora do repositório, `~/.claude` ou `~/.agent-memory`
- [ ] Zona protegida (BR-MIGRAR-007) preservada e coberta por teste
- [ ] `MD-NNNN` revertendo o `MD-0004` criado e indexado por `./harness decisions` (zero erros)
- [ ] Suíte de testes verde
- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `regression-watch.md` gerado

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-24 | Versão inicial gerada por `/reversa-plan` | reversa |
