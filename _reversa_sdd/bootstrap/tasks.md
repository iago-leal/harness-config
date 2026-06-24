# Bootstrap (Ganchos Git Locais) — Tarefas de Implementação

> Regenerado pelo Writer em 2026-06-24 (Re-extração)
> Sequência executável para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

> ⚠️ Reescrita: a unit agora é o `BootstrapService` Python (`harness-core`), não o script shell legado `bin/bootstrap.sh` (purgado). Sem `verify-prerequisites.sh` nem ponte de memória Gemini.

## Pré-requisitos

- [ ] `FileSystemPort` disponível (criação de diretório + gravação).
- [ ] Permissões de escrita em `.git/hooks/` do repositório.

## Tarefas

- [ ] T-01, Implementar `_pre_commit_script` e `_post_merge_script`
  - Origem no legado: `core/bootstrap/service.py`
  - Critério de pronto: retornam corpos Bash que invocam `harness-core/.venv/bin/python3 harness-core/src/main.py` com `format`/`decisions` e fazem `exit 0` se o interpretador não existir.
  - Confiança: 🟢

- [ ] T-02, Implementar `install_hooks(repo_path)`
  - Origem no legado: `core/bootstrap/service.py`
  - Critério de pronto: cria `.git/hooks/`, grava os dois scripts idempotentemente e retorna a lista de caminhos.
  - Confiança: 🟢

- [ ] T-03, Expor o subcomando `bootstrap` na CLI
  - Origem no legado: `src/main.py`
  - Critério de pronto: `./harness bootstrap` instala os ganchos no repositório corrente.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Happy path: após `install_hooks`, os dois scripts existem e referenciam a CLI.
- [ ] TT-02, Idempotência: reexecutar regrava os scripts sem erro.

## Ordem Sugerida

1. T-01 (corpos dos scripts) antes de T-02 (instalação).
2. T-03 fecha a integração CLI.

## Lacunas Pendentes (🔴)

- Nenhuma 🔴.
