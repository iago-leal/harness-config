# Onboarding: 023-granularidade-lembrete-gate

> Passo a passo para um humano validar a feature pela primeira vez. Todos os comandos a partir da raiz do repo (`~/dev/harness`). Pré-requisito: sessão do Harness ATIVA (se não houver, abra uma; o gate só avalia sessão ativa).

O "fim de turno" é simulado invocando o hook diretamente: `./harness decisions --gate`.

## A. Um lembrete, e só um, durante trabalho ativo (RF-01)

1. Garanta trabalho substantivo sem ficha: `echo teste >> /tmp/nada && touch smoke-023-a.txt` (arquivo novo na raiz do repo).
2. `./harness decisions --gate` → **stdout deve conter o JSON** `{"decision":"block","reason":"[HARNESS:DECISAO_PENDENTE ..."}`.
3. Toque um segundo arquivo: `touch smoke-023-b.txt`.
4. `./harness decisions --gate` → **stdout vazio** (antes da 023, aqui vinha novo bloqueio).
5. Toque um terceiro e repita → **stdout vazio**.

## B. Silêncio após registro de ficha (RF-04)

1. Crie uma ficha real ou de teste: `.harness/decisoes/MD-9999.md` (front-matter mínimo).
2. `./harness decisions --gate` → **stdout vazio** (ficha anula a pendência).
3. Toque outro arquivo novo e rode de novo → **stdout vazio**.
4. Limpe: remova `MD-9999.md` e os `smoke-023-*.txt`.

## C. Portão do encerramento intacto (RF-03)

1. Com pendência (arquivo novo, sem ficha), rode `./harness cmd encerrar-sessao` → aborta no pré-check de commit ou, com tudo commitado, bloqueia com o marker `DECISAO_PENDENTE`.
2. Sem sanar, rode de novo **sem mudar nada** → encerra com aviso (anti-loop do portão, comportamento da 022).
3. Cenário de rearme: após um bloqueio do portão, faça trabalho novo (arquivo novo, commite) e rode o encerramento → **bloqueia de novo** (a identidade fina do portão mudou). Este é o passo que prova que a 023 não enfraqueceu a garantia.

## D. Transição de formato (RF-05)

1. Com a sessão ativa, edite `.harness/estado-da-sessao.md` e grave em `gate_lembrete_fingerprint` um sha1 qualquer (simulando o formato antigo).
2. Com pendência, `./harness decisions --gate` → **exatamente 1 bloqueio**; confira no front-matter que o campo foi regravado.
3. Rode de novo → **stdout vazio**.

## E. Opt-out absoluto (RN-04)

1. No `harness.toml`, defina `[decisions] require_registration = false`.
2. Com pendência, `./harness decisions --gate` → **stdout vazio**; `encerrar-sessao` não exibe o 3º portão.
3. Restaure o toml.

## Verificação da suíte

```
cd .harness/harness-core && ./venv/bin/python -m pytest -q
```

Esperado: tudo verde; os casos novos da 023 estão em `tests/test_decision_gate.py`, `tests/test_cli.py` e `tests/test_close_flow.py`.
