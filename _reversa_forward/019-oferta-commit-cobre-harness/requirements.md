# Requirements: oferta de commit pendente cobre o vão de `.harness/`

> Identificador: `019-oferta-commit-cobre-harness`
> Data: `2026-06-30`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O pré-check de trabalho pendente do `encerrar-sessao` (introduzido pela feature 016) oferece commitar o que está solto na working tree antes de fechar, mas exclui da oferta **todo** o diretório `.harness/`, sob a premissa de que o fechamento o versiona. A premissa é falsa: o commit de fechamento versiona **apenas** `.harness/estado-da-sessao.md`. Decisões (`.harness/decisoes/MD-*.md`) e o índice regenerado (`.harness/microdecisoes.md`) ficam num vão — nem o pré-check os oferece, nem o marcador de fechamento os captura — e exigem commit manual a cada sessão. Esta feature estreita o filtro do pré-check de _diretório inteiro_ para _apenas o arquivo de estado_, de modo que todo trabalho versionável de `.harness/` passe a ser oferecido junto com o trabalho fora dele. O comportamento do fechamento em si permanece intocado; muda só o que o pré-check considera pendente.

## 2. Contexto a partir do legado

| Fonte                                                                                             | Trecho relevante                                                                                                                                                                                                             | Confidência |
| ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `_reversa_sdd/domain.md#2.15` (RN-N33)                                                            | `SessionCloseFlow.run` é a fonte única do encerramento: pré-check de pendências (016) → fechamento (`CommandService`) → ofertas pós (014). Core agnóstico ao harness; o IO é injetável (marker sem TTY, `[s/N]` com TTY).    | 🟢          |
| `_reversa_sdd/domain.md#2.14` (RN-N31, RN-N32)                                                    | O commit de fechamento versiona **exclusivamente** o `state_file` (`git add -- <paths>`, nunca `-A`), por cima do trabalho; falha de commit → `SessionCommitError` (exit ≠ 0) sem reverter o estado. Invariante a preservar. | 🟢          |
| `.harness/harness-core/src/core/session/close_flow.py#pending_work_paths`                         | Filtro atual: `harness_dir = session_file.split("/",1)[0]` (→ `.harness`) e exclui `p == harness_dir or p.startswith(harness_dir + "/")` — ou seja, **o diretório inteiro**. É a origem mecânica do vão.                     | 🟢          |
| `_reversa_forward/016-encerrar-sessao-autonomo/interfaces/commit-pendente-marker.md#5`            | Contrato já declara a **intenção correta**: "Só `.harness/estado-da-sessao.md` sujo → tratado como limpo: é o que o fechamento versiona". O código diverge do contrato (exclui o diretório, não o arquivo).                  | 🟢          |
| `.harness/harness-core/src/core/ports/git.py#list_dirty_paths` + `src/adapters/git/subprocess.py` | `list_dirty_paths` lê `git status --porcelain` (omite ignorados por padrão); é a porta read-only que alimenta o pré-check. O core nunca faz `git add` do trabalho (RN-N5).                                                   | 🟢          |
| `.harness/harness-core/src/core/domain/config.py` + `bootstrap/init_service.py`                   | `version = "1.2.55"` em dois pontos + asserção em `tests/test_init.py`. Decisões em `.harness/decisoes`, índice em `.harness/microdecisoes.md`, estado em `.harness/estado-da-sessao.md` (config canônica).                  | 🟢          |

## 3. Personas e cenários de uso

| Persona                        | Objetivo                                                          | Cenário-chave                                                                                                                          |
| ------------------------------ | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Mantenedor intermitente (iago) | Fechar a sessão num passo, sem lembrar de commitar decisões à mão | Registra uma microdecisão na sessão e roda `/encerrar-sessao`; a decisão e o índice entram na oferta de commit, não no vão             |
| Agente de IA (borda sem TTY)   | Mediar o fechamento preservando os invariantes do core            | Recebe o marker `COMMIT_PENDENTE` já contendo os caminhos de `.harness/decisoes/` e `microdecisoes.md`, commita o que é real e re-roda |
| Operador em terminal (TTY)     | Ver, antes de fechar, todo trabalho solto — inclusive decisões    | A listagem `[s/N]` do pré-check passa a incluir os artefatos versionáveis de `.harness/`                                               |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** O pré-check de trabalho pendente exclui da oferta **apenas** o arquivo de estado exato (`state_file`, ex.: `.harness/estado-da-sessao.md`), não o diretório que o contém. 🟢
   - Origem no legado: altera `close_flow.py#pending_work_paths` e reconcilia com `016/interfaces/commit-pendente-marker.md#5` (que já previa "só o estado-da-sessao.md → limpo").
   - Tipo: alterada
2. **RN-02:** O conjunto "trabalho pendente" passa a incluir todo artefato versionável de `.harness/` que esteja sujo e não seja o `state_file` — em particular decisões (`.harness/decisoes/MD-*.md`) e o índice regenerado (`.harness/microdecisoes.md`). 🟢
   - Tipo: alterada (consequência direta de RN-01)
3. **RN-03 (invariante, não alterada):** O commit de fechamento continua versionando **exclusivamente** o `state_file`, por cima do trabalho, via `commit_paths` (`git add -- <paths>`, nunca `-A`), com falha barulhenta. O pré-check é anterior e não toca esse passo. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.14` (RN-N31, RN-N32). Tipo: preservada
4. **RN-04 (invariante, não alterada):** O core **lista** o trabalho pendente, mas nunca faz `git add` dele; quem decide e commita é o agente (sem TTY) ou o usuário (com TTY), que então re-roda o comando. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.3` (RN-N5) e `016/interfaces/commit-pendente-marker.md#5`. Tipo: preservada
5. **RN-05:** Arquivos ignorados pelo git nunca entram na oferta — decorrência de a fonte ser `git status --porcelain`, que omite ignorados. Artefatos de runtime de `.harness/` que não devam ser versionados dependem do `.gitignore` do projeto consumidor; o core **não** mantém denylist de runtime (decisão de §9). O `init`/template do harness deve assegurar que os runtime conhecidos (ex.: `sync-cache.json`) estejam ignorados. 🟢
   - Tipo: nova (explicita uma garantia de borda).

## 5. Requisitos Funcionais

| ID    | Requisito                                                                                                                          | Prioridade | Critério de aceite                                                                                                                     | Confidência |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | Uma decisão suja (`.harness/decisoes/MD-*.md`) e/ou o índice (`.harness/microdecisoes.md`) entram no conjunto de trabalho pendente | Must       | Com esses arquivos sujos e nada mais, o `encerrar-sessao` **não** fecha e oferece commitá-los (marker sem TTY / `[s/N]` com TTY)       | 🟢          |
| RF-02 | `.harness/estado-da-sessao.md` como **único** arquivo sujo é tratado como árvore limpa                                             | Must       | Nessa condição, nenhuma oferta dispara e o fechamento procede normalmente                                                              | 🟢          |
| RF-03 | Trabalho fora de `.harness/` permanece coberto (sem regressão da 016)                                                              | Must       | Arquivo sujo fora de `.harness/` continua disparando a oferta exatamente como hoje                                                     | 🟢          |
| RF-04 | Após o commit do pendente (inclusive decisões/índice), re-rodar encerra normalmente                                                | Must       | Com a árvore limpa exceto `estado-da-sessao.md`, a re-execução fecha e grava o commit de marcador                                      | 🟢          |
| RF-05 | O marker `COMMIT_PENDENTE` e a listagem TTY incluem os caminhos de `.harness/` junto aos demais, no mesmo contrato                 | Should     | `arquivos="..."` e a lista `[s/N]` contêm os paths de `.harness/` (exceto `estado-da-sessao.md`); contrato em `interfaces/` atualizado | 🟢          |
| RF-06 | Bump de versão `1.2.55 → 1.2.56` nos três pontos, com a suíte verde                                                                | Must       | `config.py`, `init_service.py` e `tests/test_init.py` em lockstep na 1.2.56; toda a suíte do core passa                                | 🟢          |

## 6. Requisitos Não Funcionais

| Tipo                    | Requisito                                                                                                                               | Evidência ou justificativa                                        | Confidência |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ----------- |
| Observabilidade         | A oferta é sempre anunciada (marker ou texto), nunca silenciosa                                                                         | Espírito ruidoso do encerramento (`domain.md#2.3` RN-N4; 015/016) | 🟢          |
| Segurança/Privacidade   | Nenhum arquivo ignorado pelo git é oferecido, evitando expor cache/segredos de runtime                                                  | `list_dirty_paths` via `git status --porcelain` (omite ignorados) | 🟢          |
| Manutenibilidade/Coesão | A mudança fica isolada no predicado de `pending_work_paths`; o método de git permanece no port `list_dirty_paths`, sem novo acoplamento | `close_flow.py`, `ports/git.py`, RN-N5                            | 🟢          |
| Reprodutibilidade       | O bump propaga aos consumidores via `./harness upgrade`; os três pontos de versão mudam juntos                                          | `domain.md#2.13` (RN-N30, materialização com código novo)         | 🟢          |

## 7. Critérios de Aceitação

```gherkin
Cenário: decisão registrada na sessão entra na oferta de commit
  Dado que ".harness/decisoes/MD-0007.md" e ".harness/microdecisoes.md" estão sujos
  E que ".harness/estado-da-sessao.md" também está sujo
  E que não há mais nada sujo na working tree
  Quando rodo "encerrar-sessao" sem TTY
  Então o comando não fecha a sessão
  E emite o marker COMMIT_PENDENTE listando os dois arquivos de ".harness/" (sem o estado-da-sessao.md)

Cenário: apenas o estado de sessão sujo fecha sem oferta
  Dado que ".harness/estado-da-sessao.md" é o único arquivo sujo
  Quando rodo "encerrar-sessao"
  Então nenhuma oferta de commit pendente dispara
  E o fechamento procede e grava o commit de marcador versionando só o estado-da-sessao.md

Cenário: re-execução após commit das decisões encerra
  Dado que commitei as decisões e o índice por caminho (git add -- <path>)
  E que a working tree está limpa exceto ".harness/estado-da-sessao.md"
  Quando re-rodo "encerrar-sessao"
  Então a sessão fecha normalmente
  E a âncora continua apontando para o último commit de trabalho, não para o commit de marcador

Cenário negativo: trabalho fora de .harness/ não regride
  Dado que "src/foo.py" está sujo
  Quando rodo "encerrar-sessao"
  Então a oferta de commit pendente dispara como antes da feature 019
  E "src/foo.py" aparece na lista de pendências
```

## 8. Prioridade MoSCoW

| Item                | MoSCoW | Justificativa                                                                      |
| ------------------- | ------ | ---------------------------------------------------------------------------------- |
| RF-01               | Must   | É o defeito que motiva a feature: o vão de `.harness/`                             |
| RF-02               | Must   | Invariante de não-regressão; o estado de sessão não pode disparar a própria oferta |
| RF-03               | Must   | Não regredir a cobertura entregue pela 016                                         |
| RF-04               | Must   | O ciclo abortar-e-reexecutar precisa convergir                                     |
| RF-06               | Must   | Sem bump, a correção não chega aos consumidores                                    |
| RF-05               | Should | O contrato do marker já existe; estendê-lo é desejável, não bloqueante             |
| RNF Observabilidade | Should | Preserva o espírito ruidoso já estabelecido                                        |

## 9. Esclarecimentos

### Sessão 2026-06-30

- **Q:** Como evitar que caches de runtime de `.harness/` (ex.: `sync-cache.json`) sejam oferecidos para commit ao incluir `.harness/` na oferta?
  **R:** Confiar no `.gitignore`. O `pending_work_paths` exclui apenas o `state_file`; como a fonte é `git status --porcelain`, arquivos ignorados nunca aparecem. Sem denylist de runtime no código — evita acoplamento e dívida que apodrece. Salvaguarda derivada: o `init`/template do harness deve garantir que os runtime conhecidos (ex.: `sync-cache.json`) estejam no `.gitignore`.
- **Q:** Quando há decisões de `.harness/` e código fora dele sujos ao mesmo tempo, como a oferta sugere o commit?
  **R:** Herdar o "split sensato" do contrato da 016 (§4): o agente/usuário decide o agrupamento. O core só **lista** o pendente (RN-N5), não faz `git add`; normatizar agrupamento no core imporia política a quem não executa. A oferta pode **sugerir** — não impor — commits separados para governança e código.

## 10. Lacunas

> Nenhuma lacuna pendente. As duas dúvidas iniciais foram resolvidas na sessão de esclarecimentos de 2026-06-30 (§9).

## 11. Histórico de alterações

| Data       | Alteração                                                            | Autor   |
| ---------- | -------------------------------------------------------------------- | ------- |
| 2026-06-30 | Versão inicial gerada por `/reversa-requirements`                    | reversa |
| 2026-06-30 | Sessão de esclarecimentos: 2 dúvidas resolvidas (`/reversa-clarify`) | reversa |
