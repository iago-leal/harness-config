# Onboarding: testar as ofertas de fim de sessão

> Identificador: `014-oferta-upgrade-ao-encerrar`
> Data: `2026-06-26`
> Público: quem vai validar a feature pela primeira vez

A feature só tem efeito num **projeto-alvo** (instalação derivada com `upstream_path`
configurado), não no repositório canônico do harness (cujo `harness.toml` não define
`upstream_path`). Os smokes abaixo usam um sandbox derivado.

## 0. Pré-requisitos

- Suíte verde: dentro de `.harness/harness-core/`, `python -m pytest`.
- Um sandbox derivado: `./harness init /tmp/alvo-014` (gera `harness.toml` com `upstream_path`
  apontando para este repositório). Inicialize um `git` com remoto de teste no sandbox se for
  exercitar o push (pode ser um remoto local: `git init --bare /tmp/remoto-014` e
  `git -C /tmp/alvo-014 remote add origin /tmp/remoto-014`).

## 1. Oferta de push — caminho feliz (terminal)

1. No sandbox, inicie uma sessão (`./harness cmd resume feature-x`) e faça um commit de trabalho.
2. Garanta o tracking: `git -C /tmp/alvo-014 push -u origin feature-x` e depois mais um commit
   local (para ficar 1 à frente).
3. Rode `./harness cmd encerrar-sessao` **num terminal interativo**.
4. **Esperado:** após a mensagem de encerramento (dois hashes), aparece a pergunta
   `Há N commit(s) à frente de origin/feature-x. Publicar agora (git push)? [s/N]`. Responder `s`
   publica; `git -C /tmp/alvo-014 status` fica "up to date".

## 2. Oferta de push — branch principal (aviso reforçado)

1. No sandbox, em `main`, com commits à frente do remoto, rode `./harness cmd encerrar-sessao`.
2. **Esperado:** a oferta de push traz o aviso reforçado de publicação direta na principal antes
   de pedir a confirmação.

## 3. Branch em dia — sem oferta de push

1. Com o branch sincronizado (0 à frente), encerre a sessão.
2. **Esperado:** nenhuma pergunta/linha de push.

## 4. Oferta de upgrade (terminal)

1. Deixe a `version` do `harness.toml` do sandbox atrás da versão publicada no upstream remoto.
2. Rode `./harness cmd encerrar-sessao` no terminal e aceite a oferta de upgrade.
3. **Esperado:** o clone do upstream é sincronizado (fast-forward) antes da cópia; o `upgrade`
   roda e a `version` do sandbox passa a refletir a publicada.

## 5. Ordem das ofertas

1. Com commits à frente **e** upstream à frente, encerre a sessão.
2. **Esperado:** a oferta de push é apresentada **antes** da de upgrade.

## 6. Modo sem terminal (slash command / agente)

1. Simule o acionamento sem TTY: `echo "" | ./harness cmd encerrar-sessao` (stdin não é TTY).
2. **Esperado:** o comando termina sem esperar entrada; o `stdout` traz as linhas-marcador
   `[HARNESS:PUSH_DISPONIVEL ...]` e/ou `[HARNESS:UPGRADE_DISPONIVEL ...]` conforme cabível.

## 7. Degradação resiliente (falha de rede)

1. Deixe o remoto do upstream inacessível (ex.: renomeie `/tmp/remoto-014` temporariamente) e
   encerre a sessão.
2. **Esperado:** a sessão encerra normalmente (estado versionado), sem travar, com aviso em
   `stderr` e **sem** oferta de upgrade enganosa.

## 8. Recusa

1. Com push e upgrade cabíveis, responda `n` a ambos no terminal.
2. **Esperado:** sessão permanece encerrada; nada é publicado nem atualizado.

## 9. Limpeza

- `rm -rf /tmp/alvo-014 /tmp/remoto-014`.
