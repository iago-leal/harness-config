# Roadmap: oferta de commit pendente cobre o vão de `.harness/`

> Identificador: `019-oferta-commit-cobre-harness`
> Data: `2026-06-30`
> Requirements: `_reversa_forward/019-oferta-commit-cobre-harness/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A correção é cirúrgica e mora num único predicado. Hoje `pending_work_paths` (em `close_flow.py`) exclui da oferta de commit pendente **todo** o diretório que contém o `state_file` — `.harness/` —, enquanto o fechamento versiona apenas o arquivo `.harness/estado-da-sessao.md`. Estreita-se a exclusão de _diretório_ para _arquivo de estado_ (`p != session_file`), de modo que decisões (`.harness/decisoes/MD-*.md`) e o índice (`.harness/microdecisoes.md`) passem a ser oferecidos junto com o trabalho fora de `.harness/`. Como o filtro deixa de mascarar o diretório inteiro, um cache de runtime — `.harness/sync-cache.json` — passaria a ser oferecido nos consumidores; portanto a feature **também** garante esse cache no `.gitignore` materializado pelo `init`/`upgrade` (decisão de não usar denylist no código, §9 do requirements). Os invariantes do fechamento (RN-N31/N32) ficam intactos: o pré-check é anterior e não toca `commit_paths`. Fecha-se com bump `1.2.55 → 1.2.56` para propagar via `./harness upgrade`.

## 2. Princípios aplicados

> `.reversa/principles.md` não existe neste projeto (apenas `setup.json` declara `principles.enabled`). Sem princípios formais a checar; registra-se o alinhamento aos princípios operacionais do projeto (longevidade, coesão, baixo acoplamento). Nenhum conflito.

| Princípio         | Como a feature se relaciona                                                                                                                                                                 | Status   |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Alta coesão / SRP | A regra "trabalho pendente" passa a ser o complemento exato do que o marcador versiona — uma definição sem exceção arbitrária; o defeito era justamente o caso especial `.harness/` sim/não | respeita |
| Baixo acoplamento | A mudança fica no predicado de `pending_work_paths`; o método de git permanece no port `list_dirty_paths`; nenhuma denylist de nomes chumbada no core                                       | respeita |
| Mínimo de dívida  | Filtro mínimo + salvaguarda via `.gitignore` (config, não código) elimina o vão sem introduzir lista que apodrece                                                                           | respeita |
| Erros barulhentos | O pré-check segue anunciando (marker/`[s/N]`); falha de `list_dirty_paths` é barulhenta                                                                                                     | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                       | Justificativa                                                                                                                                           | Alternativas descartadas                                                            | Confidência |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ----------- |
| D-01 | `pending_work_paths` exclui apenas `session_file` (`p != session_file`), não o diretório do harness                                           | É a fronteira correta da responsabilidade: complemento do que o marcador versiona; reconcilia o código com `016/interfaces/commit-pendente-marker.md#5` | excluir prefixo `.harness/` (status quo, mantém o vão); excluir por lista de pastas | 🟢          |
| D-02 | Garantir `.harness/sync-cache.json` no `.gitignore` via `_ensure_gitignore_entry` no `init` e no `upgrade`; sem denylist de runtime no código | Decisão §9 do requirements (confiar no `.gitignore`); a 019 é quem expõe o cache, logo é quem o protege                                                 | denylist hardcoded em `pending_work_paths` (acopla, apodrece)                       | 🟢          |
| D-03 | Agrupamento do commit permanece decisão do agente (herda contrato 016 §4); core só lista                                                      | RN-N5: o core não faz `git add`; normatizar agrupamento imporia política a quem não executa                                                             | split obrigatório no contrato; commit único forçado                                 | 🟢          |
| D-04 | `commit_paths` e o passo de fechamento ficam intocados; a mudança é toda no pré-check anterior                                                | Preserva RN-N31/N32 (marcador versiona só o estado, `git add --`, falha barulhenta)                                                                     | mexer no fechamento (risco de regressão 013)                                        | 🟢          |
| D-05 | Atualizar a mensagem TTY de `conduct_commit_pendente` e os docstrings/`acao` para "exceto o estado de sessão" no lugar de "fora de .harness/" | A semântica do conjunto mudou; texto e contrato devem refletir                                                                                          | manter o texto antigo (enganoso)                                                    | 🟢          |
| D-06 | Bump `1.2.55 → 1.2.56` em `config.py`, `init_service.py` e `tests/test_init.py`, em lockstep                                                  | Sem bump a correção não chega aos consumidores via `upgrade` (RN-N30)                                                                                   | não versionar (correção fica presa no upstream)                                     | 🟢          |

## 4. Premissas

> Nenhuma. O `requirements.md` está sem marcadores `[DÚVIDA]`; as duas dúvidas foram resolvidas em `/reversa-clarify` (§9).

## 5. Delta arquitetural

| Componente                                                  | Arquivo de origem no legado                             | Tipo de mudança   | Resumo                                                                         |
| ----------------------------------------------------------- | ------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------ |
| `SessionCloseFlow` / `pending_work_paths`                   | `_reversa_sdd/domain.md#2.15` (RN-N33); `close_flow.py` | regra-alterada    | Exclusão de diretório → exclusão do arquivo de estado                          |
| `conduct_commit_pendente` / `render_commit_pendente_marker` | `close_flow.py`                                         | contrato-alterado | Semântica do conjunto/mensagem: "tudo menos o estado", não "fora de .harness/" |
| `BootstrapInitService` (gitignore)                          | `init_service.py`; `domain/layout.py`                   | regra-alterada    | Garante `.harness/sync-cache.json` ignorado no alvo (init + upgrade)           |
| Versão do core                                              | `config.py`, `init_service.py`, `tests/test_init.py`    | regra-alterada    | `1.2.55 → 1.2.56` em lockstep                                                  |

## 6. Delta no modelo de dados

- Resumo das mudanças: não há banco de dados nem schema persistido. A única "estrutura" afetada é o conjunto de caminhos retornado por `pending_work_paths` (em memória) e a lista de entradas garantidas no `.gitignore` do alvo.
- Detalhe completo em: `_reversa_forward/019-oferta-commit-cobre-harness/data-delta.md`

## 7. Delta de contratos externos

| Contrato                                             | Tipo                            | Arquivo de detalhe                                                                      |
| ---------------------------------------------------- | ------------------------------- | --------------------------------------------------------------------------------------- |
| Marker `[HARNESS:COMMIT_PENDENTE …]` (core → agente) | arquivo/stream (linha-marcador) | `_reversa_forward/019-oferta-commit-cobre-harness/interfaces/commit-pendente-marker.md` |

## 8. Plano de migração

1. Aplicar a mudança no upstream (`~/dev/harness`) com TDD: testes vermelhos primeiro, depois o predicado e a salvaguarda do gitignore.
2. Bump `1.2.55 → 1.2.56` nos três pontos; suíte verde.
3. Commit + push no `harness-config` (push aguarda aval do mantenedor).
4. Consumidores recebem via `./harness upgrade`; o upgrade re-materializa o `.gitignore` (entrada do sync-cache) com o código novo (RN-N30).
5. Sem migração de dados — n/a.

## 9. Riscos e mitigações

| Risco                                                                                                                                                | Impacto | Probabilidade | Mitigação                                                                                                                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `sync-cache.json` exposto na oferta antes de o `.gitignore` ser atualizado nos consumidores                                                          | médio   | médio         | D-02: a mesma feature garante a entrada no `.gitignore`; o `upgrade` a aplica antes de o novo filtro valer                                 |
| Divergência de nome do cache: `close_flow.py`/`main.py` usam `.harness/sync-cache.json`, mas `adapters/mcp/server.py` usa `.harness/sync_cache.json` | baixo   | —             | Fora do escopo da 019; anotar para faxina futura. Ignorar o nome canônico do fluxo de encerramento (hífen); avaliar ignorar ambos no to-do |
| Comparação de path exata falha por normalização (`./`, separador)                                                                                    | baixo   | baixo         | `list_dirty_paths` e `config.session.state_file` usam o mesmo formato relativo com `/`; cobrir por teste com o path canônico               |
| Regressão dos testes da 016 que assumem "fora de .harness/"                                                                                          | médio   | alto          | Atualizar expectativas dos testes; vigiar em `regression-watch.md`                                                                         |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `pending_work_paths` testado: decisão/índice incluídos, `estado-da-sessao.md` excluído, trabalho externo preservado
- [ ] Salvaguarda do `.gitignore` (`.harness/sync-cache.json`) testada no `init` e no `upgrade`, idempotente
- [ ] Versão `1.2.56` em lockstep nos três pontos; suíte do core verde
- [ ] Contrato `interfaces/commit-pendente-marker.md` (delta de semântica) atualizado
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-06-30 | Versão inicial gerada por `/reversa-plan` | reversa |
