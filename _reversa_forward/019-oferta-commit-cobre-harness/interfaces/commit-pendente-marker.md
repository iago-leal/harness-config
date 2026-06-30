# Contrato (delta 019): marker `[HARNESS:COMMIT_PENDENTE …]`

> Identificador: `019-oferta-commit-cobre-harness`
> Tipo: protocolo de borda (core → agente), pré-fechamento
> Base: `_reversa_forward/016-encerrar-sessao-autonomo/interfaces/commit-pendente-marker.md` (a 019 **altera a semântica**, não o formato)

## 1. O que muda

A 019 mantém o **formato** do marker e a dualidade TTY × não-TTY da 016. Muda apenas a **definição do conjunto `arquivos`** e os textos que a descrevem.

| Aspecto                                                   | 016 (antes)                            | 019 (depois)                                                              |
| --------------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------- |
| Conjunto `arquivos`                                       | caminhos sujos **fora** de `.harness/` | caminhos sujos **exceto** `.harness/estado-da-sessao.md` (o `state_file`) |
| Inclui decisões/índice de `.harness/`?                    | não (vão)                              | **sim** (`.harness/decisoes/MD-*.md`, `.harness/microdecisoes.md`)        |
| Caches de runtime de `.harness/` (ex.: `sync-cache.json`) | excluídos pelo filtro de diretório     | excluídos pelo `.gitignore` (omitidos por `git status --porcelain`)       |
| Mensagem TTY de `conduct_commit_pendente`                 | "fora de .harness/"                    | "exceto o estado de sessão"                                               |

## 2. Formato (inalterado)

```
[HARNESS:COMMIT_PENDENTE arquivos="<lista separada por vírgula>" total=<n> acao="git add -- <arquivos> e git commit (mensagem descritiva); depois rode novamente encerrar-sessao"]
```

- `arquivos`: caminhos sujos relativos à raiz, **exceto** o `state_file`; lista truncável (`truncado=true mostrados=<k>`) acima do teto (`cap=20`).
- `total`: número total de caminhos no conjunto (mesmo se a lista for truncada).
- `acao`: instrução curta e estável; o agente commita **por caminho** (`git add -- <path>`, nunca `-A`) e re-roda.

## 3. Regras de processamento (lado do agente) — inalteradas

1. Para cada arquivo, julgar se é trabalho real (versionar) ou lixo/derivado (ignorar / mandar ao `.gitignore`).
2. Commitar por caminho, com mensagem descritiva. **Split sensato** entre governança (`.harness/decisoes/*`, `microdecisoes.md`) e código fora de `.harness/` é **sugerido, não imposto** (decisão §9 do requirements; herda 016 §4).
3. Re-rodar `./harness cmd encerrar-sessao`; com a árvore limpa exceto o `state_file`, o fechamento procede.

## 4. Invariantes preservados

- O marker é **anterior** ao fechamento; não altera `commit_paths` (RN-N31/N32): o commit de marcador continua versionando só `.harness/estado-da-sessao.md`.
- O core **lista** via `list_dirty_paths`, nunca faz `git add` do trabalho (RN-N5).
- Idempotência: árvore suja → re-emite o marker; limpa (exceto `state_file`) → fecha.

## 5. Borda

- `.harness/estado-da-sessao.md` como único sujo → conjunto vazio → trata como limpo (não dispara marker).
- `list_dirty_paths` com falha de execução real → erro barulhento, sem fechar.
