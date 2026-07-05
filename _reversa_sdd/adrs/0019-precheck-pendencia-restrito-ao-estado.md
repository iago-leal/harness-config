# ADR 0019: Pré-check de trabalho pendente restrito ao arquivo de estado, não ao diretório `.harness/` inteiro

- **Status:** Aceito
- **Data:** 2026-06-30 (feature 019-oferta-commit-cobre-harness)
- **Contexto Técnico:** `src/core/session/close_flow.py:pending_work_paths` — filtro alterado de "exclui todo o diretório que contém `session_file`" para "exclui só o caminho exato de `session_file`". Nenhuma mudança de assinatura pública; `SessionCloseFlow`, o commit de fechamento (RN-N31/N32) e as ofertas (RN-N33) permanecem intocados.
- **Escala de Confiança:** 🟢 CONFIRMADO (código as-built; smoke com git real, não `FakeGit`).
- **Decisões relacionadas:** ADR 0018 (`SessionCloseFlow` como fonte única do encerramento); RN-N31/RN-N32 (o commit de fechamento versiona só `state_file`); feature 016 (introduziu o pré-check original).

## Contexto e Problema

O pré-check de trabalho pendente do `encerrar-sessao` (feature 016) existia para evitar fechar a sessão com mudanças soltas na working tree. A implementação original excluía **todo** o diretório que contém o arquivo de estado (`.harness/` inteiro) da lista de "pendente", sob a premissa de que o commit de fechamento versionava esse diretório por completo. A premissa estava errada: o commit de fechamento versiona **exclusivamente** `state_file` (`.harness/estado-da-sessao.md`), via `git add -- <paths>` — nunca `-A` (RN-N31). Decisões (`.harness/decisoes/MD-*.md`) e o índice regenerado (`.harness/microdecisoes.md`) ficavam, na prática, **invisíveis** ao pré-check: nem entravam na oferta de commit, nem eram capturados pelo commit de fechamento. Resultado: a cada sessão em que o mantenedor registrava uma microdecisão, era preciso lembrar de commitá-la manualmente — o contrato já declarado em `_reversa_forward/016-.../interfaces/commit-pendente-marker.md` ("só o `estado-da-sessao.md` sujo é tratado como limpo") já previa o comportamento correto; o código divergia dele.

A investigação também expôs um achado metodológico: o smoke test com **git real** (não o `FakeGit` usado nos testes unitários) revelou que `git status --porcelain` colapsa um subdiretório inteiro **untracked** numa única linha — um mock que já devolvesse a lista expandida arquivo-a-arquivo mascarava esse comportamento e teria deixado a régua antiga passar despercebida por mais tempo.

## Decisão

Estreitar o filtro de `pending_work_paths` de "diretório inteiro" para "arquivo exato": a função continua lendo `git.list_dirty_paths(repo_path)` (read-only, RN-N5 preservada — o core nunca faz `git add` do trabalho alheio) e agora exclui apenas `p == session_file`. Todo o restante de `.harness/` que estiver sujo — decisões, índice — passa a integrar a lista de pendências, oferecida pelo mesmo par marker/prompt já existente (`COMMIT_PENDENTE` sem TTY, listagem `[s/N]` com TTY). Como consequência colateral necessária, o cache de runtime `.harness/sync-cache.json` (que nunca deveria ser oferecido, por ser artefato não-versionável) passa a depender explicitamente do `.gitignore` do projeto-alvo — o `init` grava essa entrada — em vez de uma denylist ampla no código.

## Alternativas Consideradas

- **Manter a exclusão do diretório inteiro e adicionar uma allowlist de subcaminhos versionáveis dentro dele:** descartado — reintroduziria uma lista chumbada de exceções, exatamente o tipo de acoplamento que a config declarativa (`[decisions]`/`[session]` no `harness.toml`) já evita em outras partes do domínio.
- **Fazer o commit de fechamento versionar todo `.harness/` (`git add .harness/`):** descartado — misturaria, no mesmo commit atômico de encerramento, mudanças de estado com mudanças de conteúdo que merecem mensagem própria (decisões arquiteturais não são "encerrar sessão"); quebraria a garantia RN-N31 de que o commit de fechamento é sempre sobre o `state_file` isolado.
- **Deixar como estava e documentar o vão como limitação conhecida:** descartado pelo mantenedor — o custo de lembrar manualmente a cada sessão superava o custo da correção, que é pequena e cirúrgica.

## Consequências

- **Positivas:**
  - Decisões e o índice regenerado nunca mais ficam invisíveis ao pré-check; o mantenedor intermitente não precisa lembrar de um commit manual paralelo a cada sessão.
  - O commit de fechamento continua estritamente sobre `state_file` (RN-N31 intocada) — nenhuma mudança de comportamento no que já funcionava.
  - Reforça a lição metodológica de testar contra git real em qualquer lógica que dependa da forma exata da saída do porcelain.
- **Negativas / em aberto:**
  - Nenhuma identificada; a mudança é estritamente aditiva sobre o conjunto de "pendências visíveis", sem novo modo de falha.
