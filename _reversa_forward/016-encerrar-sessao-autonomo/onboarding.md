# Onboarding: testar o encerrar-sessao autônomo

> Identificador: `016-encerrar-sessao-autonomo`
> Data: `2026-06-27`
> Pré-requisito: estar na raiz do projeto; venv do core em `.harness/harness-core/.venv`.

## A. Suíte de testes (TDD)

```bash
cd .harness/harness-core
.venv/bin/python -m pytest -q
```

Esperado ao final do coding: verde, incluindo os testes novos (regen, tolerância, `list_dirty_paths`, materialização do settings) e os da 015 adaptados.

## B. Tolerância no fechamento (RN-01 / D1)

1. **Sessão inativa → reativa e fecha.** Garanta `status: inactive` em `.harness/estado-da-sessao.md` (ou rode um `encerrar-sessao` antes). Então:
   ```bash
   ./harness cmd encerrar-sessao
   ```
   Esperado: a saída anuncia reativação automática, grava o commit de encerramento e termina com exit 0 (`echo $?` → 0).
2. **Sessão ausente → no-op ruidoso.** Renomeie temporariamente o estado:
   ```bash
   mv .harness/estado-da-sessao.md /tmp/estado.bak
   ./harness cmd encerrar-sessao ; echo "exit=$?"
   mv /tmp/estado.bak .harness/estado-da-sessao.md
   ```
   Esperado: mensagem "não havia sessão para encerrar", **sem** commit, exit 0.
3. **Estado malformado → continua barulhento.** Corrompa a âncora (hash curto) e rode o encerrar: deve sair com exit ≠ 0 e mensagem orientadora (regressão da 015 preservada). Restaure depois.

## C. Regeneração de artefatos (RN-02 / item iii)

1. Declare no `harness.toml`:
   ```toml
   [regen]
   command = "echo regenerando && touch _regen_marker.txt"
   ```
2. Rode:
   ```bash
   ./harness cmd regen ; echo "exit=$?"
   ```
   Esperado: executa o comando (cria `_regen_marker.txt`), exit 0.
3. **Falha barulhenta:** troque por `command = "exit 3"` e rode `./harness cmd regen` → exit ≠ 0 e mensagem; no fluxo "faz tudo", o fechamento **não** ocorre.
4. **Ausente:** remova a seção `[regen]` → `./harness cmd regen` é no-op, exit 0.

## D. Commit do trabalho pendente (RN-03 / item ii)

1. Crie trabalho solto fora de `.harness/`:
   ```bash
   echo "rascunho" > nota_de_trabalho.txt
   ```
2. Rode o fechamento (contexto sem TTY, como num slash command):
   ```bash
   ./harness cmd encerrar-sessao
   ```
   Esperado: **não fecha**; emite o marker `[HARNESS:COMMIT_PENDENTE arquivos=… acao="git add + commit"]` listando `nota_de_trabalho.txt`.
3. O agente (ou você) commita por caminho com mensagem descritiva:
   ```bash
   git add -- nota_de_trabalho.txt && git commit -m "docs: nota de trabalho"
   ```
4. Re-rode `./harness cmd encerrar-sessao` → árvore limpa fora de `.harness/` → fecha normalmente.
5. **Derivados regeneráveis:** se o regen produzir artefatos que você não quer versionar, adicione-os ao `.gitignore` (ex.: `site/`, `*.portavel.html`); eles deixam de aparecer no marker.

## E. Fluxo "faz tudo" via slash command

No Claude, rode `/encerrar-sessao`. A skill sequencia `cmd regen` → `cmd encerrar-sessao`; o agente reage ao marker (commita o pendente) e re-roda. Resultado: regenera, commita, fecha — num gesto só.

## F. Raiz: hook de resume plantado por init/upgrade (RN-05)

Em um sandbox (cópia de projeto consumidor):

```bash
<upstream>/harness init <sandbox>     # ou: cd <sandbox> && ./harness upgrade
cat <sandbox>/.claude/settings.json   # deve conter SessionStart → harness cmd resume
```

Esperado: o `.claude/settings.json` passa a conter o hook de resume (criado se ausente; mesclado sem apagar chaves/hook de terceiros). Reexecutar `init`/`upgrade` converge ao mesmo resultado (idempotente).
