# Regression-watch: fonte única + hooks não-destrutivos

> Feature: `020-fonte-unica-e-hooks`
> Itens a manter verdadeiros nas próximas extrações reversas. **Rodada parcial** (bloco de materializadores); as próximas rodadas farão append (W003+), sem reciclar IDs.

## Watch items

| ID   | Origem (arquivo, seção)                                                                 | Regra esperada após a mudança                                                                                                                                                                                             | Tipo de verificação | Sinal de violação                                                                                                                                  |
| ---- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | `src/core/bootstrap/service.py` · `domain.md#2.7` (RN-N15)                              | `install_hooks` é **não-destrutivo**: hook alheio de mesmo nome preservado em `<hook>.local` e encadeado; hook próprio (assinatura `Harness Core`) atualizado no lugar; ausente criado. Hooks de outro nome nunca tocados | presença + redação  | Um `pre-commit`/`post-merge` do projeto sobrescrito sem preservar `.local`; ou a instalação apagando/alterando hook de outro nome                  |
| W002 | `src/core/bootstrap/service.py` · `domain.md#2.7` (RN-N15)                              | Os scripts de hook invocam o shim `./harness format` / `./harness decisions`, com guarda `[ -x ./harness ]` (não bloqueia se ausente); não referenciam mais o python local do core                                        | redação             | Hook voltando a chamar `.venv/bin/python3`/`src/main.py`; ou bloqueando o commit quando o shim está ausente                                        |
| W003 | `src/core/install/claude_settings.py` · feature 016/RN-05 (sob `domain.md#2.13` RN-N30) | `materialize_claude_settings` mescla **por-item** dentro do array de cada evento do harness, preservando itens próprios do usuário no mesmo evento; idempotente por assinatura                                            | presença            | Um hook próprio do usuário em `SessionStart`/`PostToolUse`/`Stop` descartado após `materialize`/`init`; ou item do harness duplicado ao reexecutar |

## Observações (sem peso de regressão)

- A ativação semântica de skills no Antigravity segue como amarelo herdado (RN-N29/009/017), não afetada por este bloco.

## Histórico de re-extrações

<!-- Preenchido pelo agente reverso quando `/reversa` rodar de novo. -->

## Arquivadas

<!-- Vazio. -->
