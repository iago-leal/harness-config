# Onboarding: testar o upgrade resiliente do harness-core

> Identificador: `012-corrige-upgrade-stale`
> Data: `2026-06-25`
> Público: humano que vai validar a feature pela primeira vez. Passos executáveis, do repo-fonte `/Users/iagoleal/dev/harness`.

## 0. Pré-requisitos

- Estar no repo-fonte: `cd /Users/iagoleal/dev/harness`
- Venv do core ativa para rodar a suíte: `.harness/harness-core/.venv/bin/python3 -m pytest` (ou `cd .harness/harness-core && .venv/bin/pytest`)

## A. Suíte de testes (rede de segurança)

```bash
cd /Users/iagoleal/dev/harness/.harness/harness-core
.venv/bin/pytest -q
```

Esperado: tudo verde, incluindo `test_footprint.py`, `test_init.py` e os novos testes de integração do `upgrade`.

## B. Modo 1 — materializador não pode ficar stale

Cenário: o upstream tem um materializador alterado; um `upgrade` deve produzir o artefato **novo**.

1. Criar um alvo descartável e inicializá-lo a partir do upstream:
   ```bash
   TARGET=$(mktemp -d)/alvo && mkdir -p "$TARGET" && git -C "$TARGET" init -q
   /Users/iagoleal/dev/harness/harness init "$TARGET"
   ```
2. Anotar a versão atual do `harness.toml` do alvo e o conteúdo do slash command materializado:
   ```bash
   grep '^version' "$TARGET/harness.toml"
   cat "$TARGET/.claude/commands/encerrar-sessao.md"
   ```
3. No upstream, alterar o materializador (ou o conteúdo do perfil que ele grava) **e bumpar a versão** em `.harness/harness-core/src/core/domain/config.py`.
4. Rodar o upgrade no alvo e conferir que o artefato reflete o conteúdo **novo**, não o anterior:
   ```bash
   ( cd "$TARGET" && ./harness upgrade )
   cat "$TARGET/.claude/commands/encerrar-sessao.md"   # deve refletir a versão NOVA
   ```

Esperado: o slash command materializado corresponde ao código recém-copiado, não ao que estava em memória no início do `upgrade`.

## C. Modo 2 — sem upgrade fantasma (abort barulhento)

Cenário: a versão do upstream não é determinável; o `upgrade` deve abortar, nunca imprimir "Sucesso".

1. Com o alvo do passo B, tornar a versão do upstream indeterminável (ex.: renomear temporariamente o `config.py` do upstream ou apontar o `upstream_path` do alvo para um diretório sem `config.py` em nenhum candidato).
2. Rodar o upgrade e inspecionar a saída e o exit code:
   ```bash
   ( cd "$TARGET" && ./harness upgrade ); echo "exit=$?"
   ```

Esperado: mensagem de erro clara com instrução de recuperação via `init`, `exit` ≠ 0, e **nenhuma** linha "Sucesso". Reverter a alteração do upstream ao final.

## D. `--force` — recópia com versões iguais

```bash
( cd "$TARGET" && ./harness upgrade )          # 1ª vez aplica
( cd "$TARGET" && ./harness upgrade )           # 2ª vez: versões iguais, no-op legítimo
( cd "$TARGET" && ./harness upgrade --force )   # força recópia + rematerialização
```

Esperado: o `--force` recopia o core e rematerializa os artefatos mesmo com as versões iguais, sem concluir prematuramente por igualdade de versão.

## E. Recuperação de instalação presa no layout antigo (RF-05)

Cenário real (o do incidente). Dado um alvo com `harness-core/` órfão na raiz e nada em `.harness/harness-core/`:

```bash
# Recuperação oficial: init do upstream por caminho ABSOLUTO
/Users/iagoleal/dev/harness/harness init /caminho/abs/do/alvo

# Remover o core órfão da raiz (gitignored, não rastreado)
rm -rf /caminho/abs/do/alvo/harness-core
```

Verificação:

```bash
ls /caminho/abs/do/alvo/.harness/harness-core/src/main.py   # deve existir
( cd /caminho/abs/do/alvo && ./harness --help >/dev/null && echo OK )
git -C /caminho/abs/do/alvo status --short                  # .reversa/ e .harness/decisoes/ intactos
```

Esperado: core no layout canônico, wrapper executa, estado versionado preservado.

## F. Não-destrutividade e footprint (invariante)

Após qualquer `upgrade`/`init` acima, confirmar que nada foi escrito fora do repositório-alvo e que `.reversa/` e `.harness/decisoes/` seguem intactos:

```bash
git -C "$TARGET" status --short
```

Esperado: apenas mudanças sob o próprio alvo (wrapper, `harness.toml`, `.gitignore`, artefatos materializados); nada fora dele.

## Limpeza

```bash
rm -rf "$TARGET"
```
