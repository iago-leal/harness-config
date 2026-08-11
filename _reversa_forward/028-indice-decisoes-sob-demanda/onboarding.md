# Onboarding: Índice de microdecisões leve com consulta sob demanda

> Identificador: `028-indice-decisoes-sob-demanda`
> Data: `2026-08-11`
> Roteiro para um humano validar a feature pela primeira vez, do zero.

## Pré-requisitos

- Repositório `harness` com o core ≥ versão desta feature; venv em `.harness/harness-core/.venv/`.
- Pelo menos algumas fichas em `.harness/decisoes/` (o próprio projeto tem 20).

## 1. Derivação da visão compacta

```bash
cd ~/dev/harness
./harness decisions
cat .harness/decisoes-recentes.md
```

Esperado: cabeçalho de orientação (o que é o acervo, onde está o índice completo, onde estão as fichas), linha `Total: 20 fichas`, e as 10 fichas mais recentes (MD-0020 primeiro, MD-0011 por último), só `- **MD-NNNN** — título`, sem backlinks, sem timestamp.

## 2. Idempotência e write-only-when-changed

```bash
stat -f "%m" .harness/decisoes-recentes.md .harness/microdecisoes.md
./harness decisions
stat -f "%m" .harness/decisoes-recentes.md .harness/microdecisoes.md
```

Esperado: mtimes IDÊNTICOS na segunda leitura (nada mudou → nada regravado). Hoje o índice completo é regravado a cada chamada; depois da 028, não mais.

## 3. Injeção compacta no SessionStart

```bash
.harness/harness-core/.venv/bin/python .harness/harness-core/src/main.py cmd resume 2>/dev/null | tail -20
```

Esperado: o bloco de decisões injetado é a visão compacta (Total + 10 recentes + ponteiros), NÃO o índice integral de 45 linhas.

## 4. Fallback quando a visão não existe

```bash
mv .harness/decisoes-recentes.md /tmp/decisoes-recentes.bak
.harness/harness-core/.venv/bin/python .harness/harness-core/src/main.py cmd resume 2>&1 >/dev/null | head -3
.harness/harness-core/.venv/bin/python .harness/harness-core/src/main.py cmd resume 2>/dev/null | tail -30
mv /tmp/decisoes-recentes.bak .harness/decisoes-recentes.md
```

Esperado: stderr traz o aviso de fallback; stdout injeta o índice INTEGRAL (comportamento pré-028). Nada bloqueia, exit 0.

## 5. Configuração do K

Edite `harness.toml`, seção `[decisions]`, acrescente `compact_index_size = 3`, rode `./harness decisions` e confira que a visão traz só 3 fichas. Teste também `0` (só cabeçalho + contagem + ponteiros). Remova a chave ao final (default 10 volta a valer). Um valor negativo deve falhar com erro claro, não silenciar.

## 6. Trecho de guidance no init

```bash
mkdir -p /tmp/lab-028 && cd /tmp/lab-028 && git init -q
~/dev/harness/harness init .
grep -A3 "marcador da seção de decisões" CLAUDE.md   # ajuste ao marcador real do contrato
~/dev/harness/harness init .   # re-init
grep -c "marcador da seção de decisões" CLAUDE.md    # esperado: mesma contagem (sem duplicação)
```

Esperado: o `CLAUDE.md` do projeto novo contém o trecho de guidance delimitado pelo marcador; o re-init NÃO duplica. Detalhe do marcador e do texto em `interfaces/trecho-guidance-init.md`.

## 7. Suíte

```bash
cd ~/dev/harness/.harness/harness-core && .venv/bin/python -m pytest -q
```

Esperado: verde, incluindo os testes novos de derivação, fallback, idempotência e guidance.
