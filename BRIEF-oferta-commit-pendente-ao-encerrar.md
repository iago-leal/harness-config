# Brief — Oferta de commit do trabalho pendente antes de encerrar a sessão

> Registro de intenção para a próxima feature do Harness Core (provável `015-oferta-commit-ao-encerrar`).
> Como usar: abrir sessão neste repo (`/Users/iagoleal/dev/harness`) e rodar `/reversa-requirements` passando este brief (ou seu resumo) como argumento; depois seguir o forward (clarify → plan → to-do → coding).
> Origem: pedido do usuário em sessão do TECH+ (26/06/2026), ao notar que o `encerrar-sessao` não captura mudanças soltas da working tree.

## 1. Problema / motivação

Hoje o `encerrar-sessao` grava o commit de fechamento versionando **apenas** `.harness/estado-da-sessao.md` (stage por caminho via `git add -- <path>`, **nunca** `git add -A` — decisão deliberada, ver `domain.md#2.14` RN-N31/N32 e `commit_paths`). Isso é correto: o commit de fechamento é um marcador limpo, não varre o working tree. **Efeito colateral:** trabalho legítimo deixado sem commit não entra no fechamento — fica solto, atravessa a sessão e só é notado depois. O usuário precisa lembrar de commitar **antes** de encerrar.

## 2. Objetivo

Antes de fechar, o `encerrar-sessao` faz um **pré-check da working tree**. Se houver mudanças fora de `.harness/` (o estado que o próprio fechamento versiona), o comando **oferece commitar** esse trabalho primeiro; só com a árvore limpa o fechamento prossegue e grava o commit de marcador por cima. Resultado: o usuário não precisa mais lembrar de commitar antes; e o histórico não fica com um "sessão encerrada" cercado de trabalho solto.

## 3. Contexto de código (âncoras já mapeadas)

- **Ofertas de fim de sessão (feature 014)** — `src/main.py`: `conduct_end_session_offers(...)` e `render_offer_markers(...)`. Dualidade **TTY × não-TTY**: com terminal, pergunta `[s/N]`; sem terminal (slash command), emite marker estruturado que o agente medeia. Markers atuais: `[HARNESS:PUSH_DISPONIVEL ...]`, `[HARNESS:UPGRADE_DISPONIVEL ...]`. Contrato em `_reversa_forward/014-oferta-upgrade-ao-encerrar/interfaces/session-end-offers.md`. **Esta feature é uma oferta irmã, mas PRÉ-fechamento.**
- **Fechamento** — `src/core/commands/service.py`: captura a âncora (último commit de trabalho), grava o estado e chama `commit_paths`. Invariante que **não pode** ser comprometido (`domain.md#2.14`).
- **Git port/adapter** — `src/core/ports/git.py` e `src/adapters/git/subprocess.py`: `commit_paths(repo, paths, msg)` faz `git add -- <paths>`. **Provavelmente falta** um método para listar a sujeira (ex.: `list_dirty_paths(repo)` via `git status --porcelain`), filtrando `.harness/`. Esse é o novo ponto no port.
- **Versão** (bump obrigatório para propagar): `src/core/domain/config.py` (`version`), `src/core/bootstrap/init_service.py` (`current_version`), e o teste `tests/.../test_init.py` que afirma `version = "1.2.51"`. Atual: **1.2.51 → 1.2.52**.

## 4. Desenho proposto (a refinar no plan)

1. **Pré-check** no fluxo do `encerrar-sessao` (em `main.py`, antes de invocar o serviço de fechamento): listar mudanças da working tree **excluindo** `.harness/` (que o fechamento versiona).
2. **Se houver sujeira:**
   - **Sem TTY (agente):** emitir `[HARNESS:COMMIT_PENDENTE arquivos=… acao="git add + commit"]` e **não fechar** (early return). O agente lista os arquivos, oferece commitar o que for trabalho real, commita, e **re-roda** o `encerrar-sessao`, que então acha a árvore limpa e fecha.
   - **Com TTY:** perguntar `[s/N]` se deseja commitar o pendente antes de encerrar (mensagem de commit pedida ou padrão), executar, e seguir o fechamento.
3. **Se a árvore estiver limpa** (fora de `.harness/`): comportamento atual, sem mudança.
4. **Invariante preservado:** o fechamento em si continua intocado (âncora + `git add -- estado-da-sessao.md` + falha barulhenta). A nova etapa é **anterior** e não altera o `commit_paths`.

> Decisão de interação recomendada: **abortar-e-reexecutar** (early return + marker), não fechar e depois commitar. Mantém o commit de fechamento como o último passo limpo. Confirmar no clarify.

## 5. Propagação (parte explícita do pedido)

- Mudança no **upstream** (`/Users/iagoleal/dev/harness`, remote `iago-leal/harness-config`).
- **Bump de versão** 1.2.51 → 1.2.52 nos três pontos (config, bootstrap, teste).
- **Commit + push** no `harness-config`.
- Consumidores (`TECH+`, `livro-mfc`, `comentarios-ipm`, …) recebem via `./harness upgrade` quando quiserem.

## 6. Prioridades (do usuário)

Longevidade, alta coesão, baixo acoplamento, OOP, **TDD** (teste antes; a suíte do core já existe), **SDD** (esta feature deriva de spec). O novo método de git fica no **port** (abstração), com adapter `subprocess`; o pré-check é uma responsabilidade coesa, separada do `commit_paths` do fechamento.

## 7. Critérios de aceite (rascunho)

- Working tree suja fora de `.harness/` → `encerrar-sessao` não fecha e emite/pergunta a oferta de commit; após commit, re-rodar fecha normalmente.
- Working tree limpa (fora de `.harness/`) → fechamento idêntico ao atual (sem regressão da feature 013/014).
- `.harness/estado-da-sessao.md` sozinho sujo **não** dispara a oferta (é o que o fechamento versiona).
- Versão 1.2.52 nos três pontos; suíte verde; contrato do novo marker documentado em `interfaces/`.
