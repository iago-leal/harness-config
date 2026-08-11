# Onboarding: testar o medidor de progresso pela primeira vez

> Identificador: `026-medidor-progresso-entregaveis`
> Data: `2026-08-11`
> Pré-requisito: raiz do repositório `harness`, venv do core íntegra.

## 1. Rodar a suíte

```sh
cd .harness/harness-core && .venv/bin/python -m pytest -q
```

Esperado: tudo verde (320 pré-existentes + os novos de `progress`).

## 2. Medir este próprio repositório (cenário mais rico disponível)

```sh
cd "$(git rev-parse --show-toplevel)"
./harness progress            # 1ª vez: "regravado"
cat .harness/progresso.md
```

Confira contra a realidade: feature ativa `026` com o estágio físico atual; `024` pausada em `coding-em-progresso` (27/28 ações); `025` entre as concluídas; seção Harness com a sessão ativa e a última ficha MD; alertas coerentes (a pendência de reconciliação do `_reversa_sdd/` registrada pelas 025/017 deve aparecer como `media`).

## 3. Idempotência e estabilidade do diff

```sh
./harness progress            # 2ª vez: "já estava em dia"
git diff --stat .harness/progresso.md   # esperado: vazio
```

## 4. Modo JSON

```sh
./harness progress --json | python3 -m json.tool | head -30
```

Esperado: mesmos números do markdown + campo `aferido_em`; nenhum arquivo tocado.

## 5. Modo hook (manual)

```sh
# suje o arquivo de propósito
echo "linha espúria" >> .harness/progresso.md
./harness progress --em-hook; echo "exit=$?"    # esperado: regrava, instrui, exit=1
./harness progress --em-hook; echo "exit=$?"    # esperado: em dia, exit=0
git checkout -- .harness/progresso.md 2>/dev/null || true
```

## 6. Degradação sem Reversa

```sh
cd "$(mktemp -d)" && git init -q . && git commit -q --allow-empty -m init
/Users/iagoleal/dev/harness/harness init .
./harness progress; echo "exit=$?"   # esperado: seção forward n/a, Harness medido, exit=0
```

## 7. Verificar o escopo negativo

```sh
git -C /Users/iagoleal/dev/harness status --porcelain -- .claude/settings.json .reversa _reversa_sdd
```

Esperado: nenhuma mudança (o medidor só escreve `.harness/progresso.md`).
