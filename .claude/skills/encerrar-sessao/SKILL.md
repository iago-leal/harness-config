---
name: encerrar-sessao
description: >-
  Encerra a sessão do Harness — atualiza a narrativa da sessão, regenera os
  artefatos derivados e conduz o fechamento pedindo aval antes de qualquer
  escrita no git: pergunta se deve commitar o trabalho pendente e se deve gravar
  o commit de encerramento (o registro do fechamento por cima do último commit de
  trabalho). Ative quando o usuário pedir para "encerrar a sessão", "fechar a
  sessão", "finalizar a sessão", "encerrar sessão do Harness" ou digitar
  "/encerrar-sessao". NÃO ative para iniciar ou retomar a sessão (isso é função do
  resume), nem para apenas commitar trabalho sem encerrar.
license: MIT
compatibility: Antigravity, Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills.
metadata:
  author: iagoleal
  version: "1.4.0"
  framework: harness
  role: session
---

# Encerrar sessão do Harness

Conduza o encerramento autônomo da sessão do Harness. A lógica vive no Harness
Core (testada); os scripts desta skill são finos e apenas a invocam — não
reimplementam regra.

O `.harness/estado-da-sessao.md` tem duas metades: o front-matter (âncora, status
e tempo, que o fechamento mantém sozinho) e a **narrativa** — as quatro seções
`##` que só você, agente, sabe escrever. O core nunca inventa a narrativa; por
isso o primeiro passo do encerramento é **você** consolidá-la. Se esquecer, o
fechamento recusa de forma barulhenta (marker `NARRATIVA_PENDENTE`) e não fecha.

**Consentimento antes de escrever no git (feature 024).** Nada entra no histórico
do repositório por iniciativa sua ao encerrar: nem o commit do trabalho pendente,
nem o commit de encerramento. Você **pergunta**, e só escreve mediante aval
explícito. Sem terminal (hook, automação), o silêncio nunca autoriza: o commit de
encerramento só ocorre com a flag `--com-commit-encerramento`, e a ausência produz
um estado não versionado mais um marker de aviso.

## Passos

1. **Atualize a narrativa da sessão.** Edite `.harness/estado-da-sessao.md` e
   reescreva as quatro seções refletindo o trabalho REAL desta sessão — não
   repita a narrativa anterior; descreva o que mudou:

   - `## O que foi feito`
   - `## Próximos passos`
   - `## Pendências / bloqueios`
   - `## Ponteiros`

   Preserve o front-matter YAML no topo: o fechamento o reescreve; você cuida só
   do corpo.

2. **Encerre a sessão.** Execute o script de entrada desta skill, que fica ao
   lado deste `SKILL.md`:

   ```bash
   python3 scripts/encerrar_sessao.py
   ```

   Ele resolve a raiz do projeto (via git) e localiza o Harness Core: primeiro em
   `.harness/harness-core` local; se ausente (projeto migrado à fonte única), no
   `upstream_path` do `harness.toml`. Em seguida conduz, em ordem: regeneração dos
   artefatos derivados → pré-check de trabalho pendente → gate de narrativa → gate
   de registro de decisões → **decisão do commit de encerramento** → ofertas de
   fim de sessão. Se a regeneração falhar (exit ≠ 0), o script **para** antes de
   fechar e mostra o erro.

3. **Se a saída trouxer um marker `[HARNESS:COMMIT_PENDENTE …]`**, há trabalho não
   commitado fora de `.harness/`. **Pergunte antes de commitar** — não commite por
   conta própria e não trate um pedido antigo de autonomia como autorização
   permanente para escrever no git:

   - Anuncie ao usuário: *"há `<total>` mudanças não commitadas, quer fazer o
     commit?"* (o `total` vem do campo `total` do marker; mostre a lista de
     `arquivos` só se ele pedir).
   - **Aval concedido:** commite apenas o que for trabalho real, **por caminho**
     (`git add -- <arquivo>` e `git commit` com mensagem descritiva; nunca
     `git add -A`; separe fonte de artefato regenerável, que pode ir ao
     `.gitignore`) e rode o script novamente.
   - **Aval negado:** pergunte se ele quer encerrar assim mesmo. **Sim** → rode o
     script com `--com-pendencias` (encerra com o trabalho fora do histórico, e a
     declaração fica na narrativa). **Não** → não reexecute; informe que a sessão
     segue aberta.

4. **Se a saída trouxer um marker `[HARNESS:NARRATIVA_PENDENTE …]`**, a narrativa
   continua vazia ou idêntica à do início da sessão — o Passo 1 não foi feito, ou
   não refletiu nada de novo. Volte ao Passo 1, reescreva de fato as quatro
   seções e rode o script novamente. O fechamento só prossegue quando a narrativa
   muda.

5. **Se a saída trouxer um marker `[HARNESS:DECISAO_PENDENTE …]`**, houve trabalho
   substantivo nesta sessão (código, documento, contrato — qualquer mudança
   versionável) sem nenhuma microdecisão registrada. Duas saídas, e a escolha é
   uma decisão consciente — não escolha o escape por preguiça:

   - **Houve decisão não óbvia?** Registre-a como ficha
     `.harness/decisoes/MD-NNNN.md` (front-matter `id`/`gancho`/`estado`/
     `relacoes` + seções `D / PORQUÊ / DESCARTADO / ESTADO`), commite a ficha e
     rode o script novamente.
   - **Realmente não houve?** Rode o script com o escape auditável:

     ```bash
     python3 scripts/encerrar_sessao.py --sem-decisao
     ```

     A declaração fica registrada na narrativa do estado de sessão ("O que foi
     feito"), visível na retomada seguinte.

   O gate nunca re-bloqueia o mesmo estado de pendência duas vezes: se você
   re-rodar sem mudar nada, o fechamento prossegue com um aviso de pendência não
   sanada em stderr.

6. **Decisão do commit de encerramento.** Passados os portões, o core resolve se
   grava o commit de encerramento (o registro que versiona **só** o
   `.harness/estado-da-sessao.md`, por cima do trabalho):

   - **No terminal**, ele pergunta com default afirmativo (`[S/n]`): Enter ou `s`
     versiona; `n` fecha sem versionar.
   - **Sem terminal** (o seu caso, via script), o default se inverte: sem flag,
     **nada é versionado**. Para autorizar, rode com `--com-commit-encerramento`;
     para recusar explicitamente, `--sem-commit-encerramento`. Pergunte ao usuário
     e passe a flag conforme a resposta.

   Se o fechamento ocorrer sem versionar, a saída traz o marker
   `[HARNESS:ENCERRAMENTO_NAO_VERSIONADO arquivo="…" ancora="…" motivo="…" …]`.
   Reaja pelo `motivo`:

   - `motivo="sem-autorizacao"` — a pergunta não foi feita (esquecimento seu):
     avise o usuário e pergunte agora se ele quer versionar o encerramento.
   - `motivo="recusa-explicita"` — foi decisão do usuário: apenas confirme que o
     estado ficou como mudança pendente no working tree.

   **Não reexecute** o encerramento para versionar depois: a sessão já está
   fechada, e reexecutar produz um no-op ruidoso de sessão ausente. Para
   registrar, `git add -- <arquivo de estado> && git commit`, por caminho.

7. **Ofertas finais.** Ao encerrar, o script pode emitir markers oferecendo
   publicar o trabalho (`[HARNESS:PUSH_DISPONIVEL …]` → `git push`) e atualizar o
   Harness Core (`[HARNESS:UPGRADE_DISPONIVEL …]` → `./harness upgrade`). Conduza
   essas ofertas se aparecerem. O aviso de encerramento não versionado, quando há,
   precede a oferta de push — para ninguém publicar achando que o registro da
   sessão entrou junto. Mostre a saída ao usuário.

## Em caso de erro

Se o Harness Core não for encontrado ou não puder ser importado, o script falha
de forma **barulhenta** (exit ≠ 0 com mensagem orientadora), nunca em silêncio.
Confirme que você está dentro de um projeto com o Harness instalado (existe um
wrapper `./harness` e, ou o diretório `.harness/harness-core`, ou um
`upstream_path` no `harness.toml` cujo core esteja acessível).
