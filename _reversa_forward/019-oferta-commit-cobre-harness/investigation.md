# Investigação: oferta de commit pendente cobre o vão de `.harness/`

> Identificador: `019-oferta-commit-cobre-harness`
> Data: `2026-06-30`

## 1. Pergunta de fundo

Por que decisões e o índice de `.harness/` caem fora tanto da oferta de commit pendente quanto do commit de fechamento, exigindo commit manual a cada sessão?

## 2. Diagnóstico no código

- **Oferta (016):** `close_flow.py#pending_work_paths` calcula `harness_dir = session_file.split("/", 1)[0]` (→ `.harness`) e exclui todo `p == harness_dir or p.startswith(harness_dir + "/")`. Resultado: o diretório inteiro some da oferta.
- **Fechamento (013):** `CommandService` versiona via `GitPort.commit_paths(repo, [state_file], msg)` — **apenas** `.harness/estado-da-sessao.md`.
- **O vão:** o conjunto `{.harness/* } \ {estado-da-sessao.md}` — decisões `MD-*.md`, índice `microdecisoes.md` — não é coberto por nenhum dos dois. É exatamente o que o mantenedor commitou à mão (MD-0001 no pivô, MD-0002 depois).
- **Contradição código × contrato:** `016/interfaces/commit-pendente-marker.md#5` já afirmava a intenção correta — "Só `.harness/estado-da-sessao.md` sujo → tratado como limpo: é o que o fechamento versiona". O código exclui o diretório; o contrato dizia o arquivo. A 019 reconcilia.

## 3. Alternativas avaliadas

| Alternativa                                                                           | Avaliação                                                                                | Veredito                        |
| ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------- |
| Excluir só o `session_file` (`p != session_file`)                                     | Fronteira correta: complemento exato do que o marcador versiona; regra sem caso especial | **Escolhida** (D-01)            |
| Manter exclusão de `.harness/` e tratar decisões noutro fluxo                         | Mantém o vão; exige um segundo mecanismo paralelo (baixa coesão)                         | Descartada                      |
| Denylist de runtime no `pending_work_paths` (excluir `sync-cache.json` etc. por nome) | Acopla nomes de cache ao core; apodrece a cada novo runtime                              | Descartada (§9 do requirements) |
| Confiar no `.gitignore` + garantir o cache ignorado no init/upgrade                   | `git status --porcelain` já omite ignorados; a salvaguarda é config, não código          | **Escolhida** (D-02)            |

## 4. Padrões aplicáveis

- **Filtro mínimo / complemento explícito:** definir o que excluir como exatamente o que outra etapa já trata, evitando exclusões largas que mascaram casos.
- **Configuração fora do código:** a política de "o que não versionar" vive no `.gitignore` do projeto, não numa lista no core (alinhado ao princípio de configuração fora do código).
- **Reconciliação código ↔ contrato:** quando um contrato já documenta a intenção e o código diverge, corrigir o código em vez de reescrever o contrato.

## 5. Observação lateral (fora de escopo)

`adapters/mcp/server.py:42` referencia `.harness/sync_cache.json` (underscore), enquanto `main.py`/`close_flow.py` usam `.harness/sync-cache.json` (hífen). Divergência pré-existente, não introduzida pela 019; registrada como item de faxina no `roadmap.md#9`.

## 6. Fontes

- `_reversa_sdd/domain.md#2.14` (RN-N31, RN-N32), `#2.15` (RN-N33)
- `.harness/harness-core/src/core/session/close_flow.py`
- `.harness/harness-core/src/adapters/git/subprocess.py#list_dirty_paths`
- `.harness/harness-core/src/core/bootstrap/init_service.py`, `src/core/domain/layout.py`
- `_reversa_forward/016-encerrar-sessao-autonomo/interfaces/commit-pendente-marker.md`
