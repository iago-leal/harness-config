# Onboarding: testar "Versionar o estado da sessão ao encerrar"

> Identificador: `013-commit-encerrar-sessao`
> Data: `2026-06-26`
> Público: humano testando a feature pela primeira vez, do zero.

Todos os caminhos assumem a raiz do core em `.harness/harness-core/` a partir do
projeto. Ajuste se o seu checkout diferir.

## 0. Pré-requisitos

- Python da venv do core disponível (a mesma usada pela suíte).
- `git` instalado e com identidade configurada (`user.name`/`user.email`), senão o
  commit de encerramento falha de propósito — útil para o teste negativo do passo 5.

## 1. Rodar a suíte de testes

```bash
cd .harness/harness-core
python -m pytest -q
```

Esperado: verde, incluindo os testes novos/ajustados de `tests/test_commands.py`
(âncora pré-commit, commit só do `state_file`, dois hashes na saída, `SessionCommitError`).

## 2. Montar um sandbox com sessão ativa e ruído no working tree

```bash
cd /tmp && rm -rf sess-test && mkdir sess-test && cd sess-test
git init -q && git config user.email t@t && git config user.name t
mkdir -p .harness
printf 'trabalho inicial\n' > arquivo.txt
git add arquivo.txt && git commit -q -m "trabalho"          # este é o commit de TRABALHO
ANCORA_ESPERADA=$(git rev-parse HEAD)

# ruído que NÃO deve entrar no commit de encerramento:
printf 'pendente\n' > AGENTS.md
printf 'pendente\n' > CLAUDE.md

# sessão ativa apontando para o commit de trabalho:
HARNESS=/Users/iagoleal/dev/harness/.harness/harness-core
PY=$HARNESS/.venv/bin/python   # ajuste para a venv real do core
cd /tmp/sess-test
$PY $HARNESS/src/main.py cmd resume 013-commit-encerrar-sessao
```

Esperado: "Nova sessão iniciada..." e o arquivo `.harness/estado-da-sessao.md` criado.

## 3. Encerrar a sessão

```bash
cd /tmp/sess-test
$PY $HARNESS/src/main.py cmd encerrar-sessao
```

Esperado na saída: a **âncora** (= `$ANCORA_ESPERADA`, o commit de trabalho) **e** o
**hash do commit de encerramento** (diferente da âncora), distinguíveis na mensagem.

## 4. Verificar os invariantes

```bash
cd /tmp/sess-test
echo "Âncora esperada (trabalho): $ANCORA_ESPERADA"
echo "HEAD agora (encerramento):  $(git rev-parse HEAD)"          # deve diferir da âncora
echo "Pai do HEAD:                $(git rev-parse HEAD~1)"         # deve == âncora
echo "--- arquivos no commit de encerramento (deve listar SÓ o estado) ---"
git show --name-only --pretty=format: HEAD
echo "--- working tree: AGENTS.md/CLAUDE.md continuam pendentes ---"
git status --short
echo "--- mensagem do commit (sem co-autoria) ---"
git log -1 --pretty=%B
```

Esperado:

- HEAD ≠ âncora; `HEAD~1` == âncora (encerramento por cima do trabalho).
- `git show --name-only` lista **apenas** `.harness/estado-da-sessao.md`.
- `git status --short` ainda mostra `AGENTS.md` e `CLAUDE.md` como não rastreados/pendentes.
- A mensagem é `chore(sessao): encerrar sessão 013-commit-encerrar-sessao; âncora <ancora>`, **sem** trailer `Co-Authored-By`.

## 5. Teste negativo: falha barulhenta preserva o estado

```bash
cd /tmp && rm -rf sess-fail && mkdir sess-fail && cd sess-fail
git init -q && git config user.name t && git config user.email t
mkdir -p .harness
printf 'x\n' > a.txt && git add a.txt && git commit -q -m "base"
$PY $HARNESS/src/main.py cmd resume f
# remover a identidade para forçar a falha do commit de encerramento:
git config --unset user.email; git config --unset user.name
$PY $HARNESS/src/main.py cmd encerrar-sessao ; echo "exit=$?"
```

Esperado: erro **nomeado** (`SessionCommitError`) e `exit != 0`; **não** imprime
"sucesso". O `.harness/estado-da-sessao.md` permanece em disco (estado salvo, não
revertido) — confira com `git status --short`.

## 6. Verificar o texto do slash command rematerializado

```bash
cd /Users/iagoleal/dev/harness
sed -n '1,12p' .claude/commands/encerrar-sessao.md
sed -n '1,12p' .agents/workflows/encerrar-sessao.md 2>/dev/null || true
```

Esperado: a `description`/corpo descreve que o encerramento cria um commit de registro
por cima do último commit de trabalho — não mais o texto antigo "gravando o
commit-âncora" isolado.

## 7. Limpeza

```bash
rm -rf /tmp/sess-test /tmp/sess-fail
```
