# Onboarding: testar a aposentadoria do soft-block do Stop

> Identificador: `025-aposentar-soft-block-stop`
> Data: `2026-08-11`
> Pré-requisito: estar na raiz do repositório `harness` com a venv do core íntegra.

## 1. Rodar a suíte

```sh
cd .harness/harness-core && .venv/bin/python -m pytest -q
```

Esperado: tudo verde, incluindo `test_close_flow.py::test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio` (o teste-guarda do portão, que esta feature não pode tocar).

## 2. Smoke manual em repositório descartável

```sh
# monta um repo de teste já inicializado pelo harness
cd "$(mktemp -d)" && git init -q . && git commit -q --allow-empty -m init
/Users/iagoleal/dev/harness/harness init .   # instala shim + .harness/

# abre sessão e cria trabalho substantivo sem ficha MD
./harness cmd resume >/dev/null
echo x > trabalho.txt

# 1ª avaliação: stdout deve sair VAZIO; o aviso aparece no stderr
./harness decisions --gate 1>saida.txt 2>erros.txt
test -s saida.txt && echo "FALHOU: stdout não está vazio" || echo "ok: stdout vazio"
grep -q 'HARNESS:DECISAO_PENDENTE' erros.txt && echo "ok: advisory no stderr"

# 2ª avaliação: nem advisory (fingerprint grosso já gravado)
./harness decisions --gate 2>erros2.txt
grep -q 'DECISAO_PENDENTE' erros2.txt && echo "FALHOU: advisory repetiu" || echo "ok: sem repetição"

# a garantia dura permanece: o encerramento ainda bloqueia
./harness cmd encerrar-sessao --com-pendencias --sem-commit-encerramento; echo "exit=$?"
# esperado: marker [HARNESS:DECISAO_PENDENTE ...] e sessão NÃO fechada
```

Observação: os subcomandos/flags acima seguem a superfície atual da CLI (`./harness --help` confirma os nomes exatos; em caso de divergência, o help é a fonte).

## 3. Verificar no uso real (este repositório)

1. Abra uma sessão do Claude Code no `harness`, toque um arquivo qualquer e conclua um turno.
2. O turno deve concluir **sem** o bloco de "Stop hook feedback"; o aviso fica visível apenas no transcript/modo verboso.
3. Ao rodar `encerrar-sessao` sem ficha nova, o 3º portão deve bloquear como antes; `--sem-decisao` continua sendo o escape auditável.

## 4. Verificar a não-regressão dos materializadores

```sh
git -C /Users/iagoleal/dev/harness status --porcelain -- .claude/settings.json
```

Esperado: vazio (nenhum settings regravado pela feature).
