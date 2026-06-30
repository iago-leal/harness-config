# Onboarding: testar a oferta de commit pendente cobrindo `.harness/`

> Identificador: `019-oferta-commit-cobre-harness`
> Data: `2026-06-30`
> Objetivo: verificar, à mão, que decisões/índice de `.harness/` entram na oferta de commit pendente, que o `estado-da-sessao.md` sozinho não dispara, e que o `sync-cache.json` não é oferecido.

## Pré-requisitos

- Repositório com o Harness Core instalado e uma sessão ativa.
- Working tree limpa antes de começar (`git status --porcelain` vazio).
- Estar na raiz do projeto (onde vive `.harness/`).

## Cenário A — decisão suja entra na oferta (caso principal)

1. Crie uma decisão de teste: grave um arquivo em `.harness/decisoes/MD-9999.md` com qualquer conteúdo.
2. Toque o índice: edite `.harness/microdecisoes.md` (uma linha qualquer).
3. Rode o encerramento sem TTY (modo agente/slash):
   ```
   ./harness cmd encerrar-sessao
   ```
4. **Esperado:** o comando **não fecha** e emite o marker
   `[HARNESS:COMMIT_PENDENTE arquivos="...,.harness/decisoes/MD-9999.md,.harness/microdecisoes.md" total=... acao="..."]`,
   listando os dois caminhos de `.harness/` (sem o `estado-da-sessao.md`). Exit 0.

## Cenário B — só o estado de sessão sujo fecha sem oferta

1. Garanta que o único arquivo sujo seja `.harness/estado-da-sessao.md` (descarte ou commite o resto).
2. Rode `./harness cmd encerrar-sessao`.
3. **Esperado:** nenhuma linha `COMMIT_PENDENTE`; o fechamento procede e grava o commit de marcador versionando só `.harness/estado-da-sessao.md`; a saída reporta os dois hashes (trabalho + marcador).

## Cenário C — o cache de sync não é oferecido

1. Force a existência de `.harness/sync-cache.json` (rode um `resume`/`sync-check`, ou crie o arquivo).
2. Confirme que ele está ignorado: `git status --porcelain | grep sync-cache` deve vir **vazio**.
3. Suje uma decisão (passo 1 do Cenário A) e rode `./harness cmd encerrar-sessao`.
4. **Esperado:** o marker lista a decisão, mas **não** `sync-cache.json`.

> Se o `sync-cache.json` aparecer no `git status`, o `.gitignore` do projeto ainda não tem a entrada — rode `./harness upgrade` (que a re-materializa) ou adicione `.harness/sync-cache.json` à mão.

## Cenário D — converge após commit (abortar-e-reexecutar)

1. A partir do Cenário A (marker emitido), commite as decisões por caminho:
   ```
   git add -- .harness/decisoes/MD-9999.md .harness/microdecisoes.md
   git commit -m "test: decisao de teste 019"
   ```
2. Re-rode `./harness cmd encerrar-sessao`.
3. **Esperado:** com a árvore limpa exceto `estado-da-sessao.md`, a sessão fecha; a âncora aponta para o último commit de **trabalho**, não para o commit de marcador.

## Limpeza

- Remova `.harness/decisoes/MD-9999.md` e reverta a edição de teste em `microdecisoes.md` se foram só para o teste.
- `git log --oneline -3` para conferir a ordem trabalho → marcador.
