# Onboarding: Exportador kanban derivado da Medicao

> Identificador: `027-exportador-kanban`
> Data: `2026-08-11`
> Público: o mantenedor daqui a 12 meses, testando a feature pela primeira vez.

## Pré-requisitos

- Harness Core ≥ 2.5.0 (fonte única) e projeto com ciclo forward do Reversa.
- Fork do vscode-kanban instalado no VS Code (para os passos visuais 4 e 6).

## Passos

1. **Suíte.** `cd .harness/harness-core && .venv/bin/python -m pytest -q` → tudo verde.
2. **Opt-in.** No `harness.toml` do projeto, acrescente:

   ```toml
   [progress.kanban]
   enabled = true
   ```

3. **Primeira exportação.** `./harness progress` → stdout informa o markdown E `.vscode/vscode-kanban.json regravado.`. Confira no arquivo: cards com `category: "harness"`, ações da feature ativa em `todo`/`done`, resumo da ativa em `in-progress`, pausadas em `todo`, alertas como `type: "bug"`.
4. **Visual.** Abra o board no VS Code (comando do fork). As colunas devem espelhar o `progresso.md`.
5. **Idempotência.** `./harness progress` de novo → ambos os artefatos `já estava em dia.`; `git status` sem diff.
6. **Canal de demandas.** Crie um card À MÃO no board (sem categoria `harness`), coluna `todo`, título livre. Rode `./harness progress`:
   - o card manual permanece intacto no arquivo;
   - o `progresso.md` ganha a demanda em `## Demandas do board`;
   - `./harness progress --json` lista `demandas` com o título.
7. **Sobrescrita do gerenciado.** Edite o título de um card `category: "harness"` e rode `./harness progress` → a edição some (card recomputado); o seu card manual do passo 6 continua lá.
8. **Falha real.** Corrompa o JSON do board (apague uma vírgula), rode `./harness progress` → `Erro de leitura:` em stderr, exit 2, nenhum artefato regravado. Restaure (git checkout do arquivo).
9. **Opt-out.** `enabled = false` (ou remova a seção) → `./harness progress` volta a tocar só o `progresso.md`; o board fica como está.

## Escopo negativo (conferência rápida)

- Nenhum arquivo além do board configurado é criado sob `.vscode/` (em particular, NÃO existe `vscode-kanban.js` novo).
- Editar card gerenciado não altera `actions.md` nem qualquer fonte.
- A coluna `testing` não recebe cards do harness.
