# Bootstrap (Ganchos Git Locais) — Requisitos (Requirements)

> Regenerado pelo Writer em 2026-06-24 (Re-extração)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`harness-core/src/core/bootstrap/service.py`](file:///Users/iagoleal/dev/harness/harness-core/src/core/bootstrap/service.py). Driver: `src/main.py` (subcomando `bootstrap`).

> ⚠️ **Reescrita vs versão anterior:** a implementação **deixou de ser** o script `harness-config/bin/bootstrap.sh` (purgado, commit `5624f78`) e passou a ser o `BootstrapService` Python em `harness-core`. Não há mais `verify-prerequisites.sh`, ponte de memória Gemini, nem `core.hooksPath`; o serviço apenas grava dois scripts Bash em `.git/hooks/`.

## Visão Geral

Instala ganchos Git locais de forma idempotente: grava `pre-commit` (→ `format`) e `post-merge` (→ `decisions`) em `.git/hooks/`, reescrevendo a cada execução. Cada gancho só age se o interpretador Python da venv existir; senão `exit 0` (não bloqueia).

## Responsabilidades

- Criar `.git/hooks/` (se ausente) e gravar os scripts `pre-commit` e `post-merge`. 🟢
- Tornar os scripts idempotentes (reescritos a cada execução). 🟢
- Garantir que os ganchos não bloqueiem caso o interpretador esteja ausente. 🟢
- Retornar a lista de caminhos instalados. 🟢

## Regras de Negócio

- **RN-N15 — Bootstrap idempotente e não-bloqueante:** `install_hooks` grava `pre-commit` (→ `format`) e `post-merge` (→ `decisions`) reescrevendo a cada execução; cada script só roda se o interpretador (`$PYTHON_CLI`) existir, senão `exit 0`. 🟢
- **Mecanismo distinto dos hooks de ciclo de vida:** estes ganchos Git (pre-commit/post-merge) coexistem com — e são separados de — os hooks de agente (`SessionStart`/`PostToolUse`/`Stop`) configurados nos `settings.json`. 🟡

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Instalar `pre-commit` e `post-merge`. | Must | Após `./harness bootstrap`, os dois scripts existem em `.git/hooks/` e invocam a CLI (`format`/`decisions`). |
| RF-02 | Idempotência. | Must | Reexecutar o bootstrap regrava os scripts sem erro nem duplicação. |
| RF-03 | Não-bloqueio sob interpretador ausente. | Must | Se o interpretador não existir, o gancho faz `exit 0` sem abortar o commit/merge. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Robustez | Não bloqueia operações Git se o ambiente estiver incompleto. | `core/bootstrap/service.py` (`exit 0` condicional) | 🟢 |
| Reprodutibilidade | Scripts reescritos deterministicamente a cada execução. | `core/bootstrap/service.py` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado um repositório sem ganchos instalados
Quando executo `./harness bootstrap`
Então `.git/hooks/pre-commit` e `.git/hooks/post-merge` são criados e invocam a CLI (format/decisions).

Dado que a venv do harness-core não existe
Quando um commit dispara o pre-commit instalado
Então o gancho faz exit 0 sem bloquear o commit.
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Instalação dos ganchos | Must | Razão de existir da unit. |
| Idempotência | Must | Permite reexecução segura no setup. |
| Não-bloqueio | Must | Salvaguarda: ambiente incompleto não trava o Git. |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `core/bootstrap/service.py` | `BootstrapService.install_hooks`, `_pre_commit_script`, `_post_merge_script` | 🟢 |
| `src/main.py` | Subcomando `bootstrap` | 🟢 |
