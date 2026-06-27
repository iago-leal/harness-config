# Onboarding: validar a correção do no-op no `encerrar-sessao`

> Identificador: `015-corrige-encerrar-sessao-noop`
> Data: `2026-06-27`
> Público: humano testando a feature pela primeira vez. Tudo roda no terminal, na raiz do repo.

## Pré-requisitos

- Estar na raiz do projeto: `cd "$(git rev-parse --show-toplevel)"`.
- Suíte do core executável (pytest no diretório `.harness/harness-core/`).

## A. Reproduzir os dois defeitos (antes da correção)

> Faça num clone ou branch descartável: estes passos mexem em `.harness/estado-da-sessao.md`. Guarde uma cópia antes.

1. **Hash curto.** Edite `.harness/estado-da-sessao.md`, troque o `commit_hash` da âncora por um prefixo curto (ex.: `abc1234`) e garanta `is_active: true`.
   - Rode: `./harness cmd encerrar-sessao; echo "exit=$?"`
   - **Defeito atual:** imprime um aviso, mas `exit=0` e nada é commitado.
2. **Sessão inativa.** Restaure o estado; rode `encerrar-sessao` uma vez (fecha de verdade); rode **de novo** sobre a sessão já inativa.
   - Rode: `./harness cmd encerrar-sessao; echo "exit=$?"`
   - **Defeito atual:** imprime `"Erro: Nenhuma sessão ativa..."`, mas `exit=0`.

## B. Verificar o comportamento corrigido

1. **Hash curto → falha barulhenta:** `./harness cmd encerrar-sessao; echo "exit=$?"` → `exit` diferente de zero, mensagem nomeia o arquivo de estado e a causa, e orienta regravar a âncora de 40 caracteres. A sessão **continua ativa**.
2. **Sessão inativa → falha barulhenta:** mesmo comando sobre sessão inativa → `exit` diferente de zero, mensagem distingue "não há sessão ativa a encerrar" de uma falha de fechamento e informa que a sessão reabre no próximo boot/`resume`.
3. **Boot não regride:** simule o boot com `./harness cmd resume` sobre um estado malformado → `exit=0`, aviso em `stderr`, inicialização não trava.
4. **Caminho feliz intacto:** com uma sessão ativa e âncora de 40 caracteres válida, `./harness cmd encerrar-sessao` fecha normalmente (`"Sessão encerrada com sucesso..."`, `exit=0`, commit de encerramento criado).

## C. Suíte automatizada

- Rodar a suíte do core e confirmar verde, incluindo os novos casos de regressão dos dois no-ops (RF-04) e o caso `resume → exit 0` (RF-02).

## Restaurar

- `git checkout -- .harness/estado-da-sessao.md` (ou restaure a cópia guardada) para devolver o estado de sessão real.
