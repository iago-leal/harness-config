# Onboarding: testar a feature 017 pela primeira vez

> Feature `017-caminho-workflow-antigravity` · 2026-06-27
> Para um humano (ou agente) validar o fix do zero. Comandos a partir da raiz do repo do harness.

## Pré-requisitos

- Suíte do core verde antes de começar: `cd .harness/harness-core && python -m pytest -q`
- Um diretório de sandbox descartável fora do repo (ex.: no scratchpad).

## Cenário A — `init` grava no caminho singular (projeto novo)

1. Crie um projeto sandbox vazio e rode o `init` apontando o harness ativo para `antigravity`.
2. Verifique:
   - **Existe** `<sandbox>/.agent/workflows/encerrar-sessao.md`.
   - **Não existe** `<sandbox>/.agents/workflows/encerrar-sessao.md`.
   - O frontmatter do arquivo tem `description:` e **não** tem `name:`.

```bash
test -f "<sandbox>/.agent/workflows/encerrar-sessao.md" && echo OK-singular
test ! -f "<sandbox>/.agents/workflows/encerrar-sessao.md" && echo OK-sem-plural
grep -q '^name:' "<sandbox>/.agent/workflows/encerrar-sessao.md" && echo "FALHA: name presente" || echo OK-sem-name
```

## Cenário B — `upgrade` migra e limpa o órfão (projeto legado)

1. Num sandbox, simule a instalação anterior: crie `<sandbox>/.agents/workflows/encerrar-sessao.md` (caminho plural) e também um workflow de terceiro `<sandbox>/.agents/workflows/outro-workflow.md`.
2. Rode `./harness upgrade` no sandbox.
3. Verifique:
   - **Passou a existir** `<sandbox>/.agent/workflows/encerrar-sessao.md`.
   - **Deixou de existir** `<sandbox>/.agents/workflows/encerrar-sessao.md`.
   - **Permanece intacto** `<sandbox>/.agents/workflows/outro-workflow.md` (terceiro preservado).

```bash
test -f "<sandbox>/.agent/workflows/encerrar-sessao.md" && echo OK-migrado
test ! -f "<sandbox>/.agents/workflows/encerrar-sessao.md" && echo OK-orfao-removido
test -f "<sandbox>/.agents/workflows/outro-workflow.md" && echo OK-terceiro-preservado
```

## Cenário C — reconhecimento real no Antigravity (manual, último recurso)

Só se quiser confirmar ponta a ponta na ferramenta (os cenários A/B já cobrem o contrato de arquivo):

1. Abra um projeto materializado no **Antigravity IDE** e digite `/encerrar-sessao` no chat. Esperado: o comando é reconhecido e conduz o encerramento.
2. Repita no **Antigravity CLI** no mesmo projeto. Esperado: idem.

## Verificação de saúde

- Suíte verde: `cd .harness/harness-core && python -m pytest -q`
- Versão propagada: o `harness.toml` do projeto após `upgrade` mostra `version = "1.2.54"`.
