# Regression Watch: harness-core dentro de `.harness/`

> Feature `011-harness-core-em-dot-harness`
> Itens a confirmar nas próximas extrações reversas (`/reversa`). Só regras originalmente 🟢 entram no watch principal; regras novas/inferidas vão para "Observações".

## Watch principal

| ID   | Origem (arquivo, seção)                         | Regra esperada após a mudança                                                                                                                                   | Tipo de verificação | Sinal de violação                                                                                 |
| ---- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------- |
| W001 | `_reversa_sdd/domain.md#2.9` (RN-N19)           | `init` copia o core para `<alvo>/.harness/harness-core/` (não mais a raiz) e registra `.harness/harness-core/` no `.gitignore` do alvo                          | presença            | `init` copiando para `<alvo>/harness-core/`, ou ausência da linha no `.gitignore` do alvo         |
| W002 | `_reversa_sdd/domain.md#2.9` (RN-N20)           | `upgrade` copia para `<alvo>/.harness/harness-core/`, preserva `.reversa/` e `.harness/decisoes/`, e garante (idempotente) a entrada no `.gitignore`            | presença            | `upgrade` escrevendo na raiz, tocando `.harness/decisoes/`, ou duplicando a linha do `.gitignore` |
| W003 | `_reversa_sdd/domain.md#2.9` (RN-N21)           | A checagem passiva de versão lê o `config.py` do upstream em `.harness/harness-core/src/core/domain/config.py`                                                  | redação             | Caminho `harness-core/src/core/domain/config.py` sem o prefixo `.harness/`                        |
| W004 | `_reversa_sdd/domain.md#wrapper-executavel`     | O wrapper `harness` (na raiz) resolve o core em `.harness/harness-core/`; o diretório do core vive em `.harness/harness-core/` (layout de um diretório na raiz) | presença            | Diretório `harness-core/` na raiz, ou wrapper apontando para `harness-core/...`                   |
| W005 | `_reversa_sdd/inventory.md` (`core/bootstrap/`) | Os ganchos Git pre-commit/post-merge embutem `.harness/harness-core/src/main.py` e `.harness/harness-core/.venv/bin/python3`                                    | redação             | Ganchos instalados referenciando `harness-core/...` sem o prefixo `.harness/`                     |

## Observações (sem peso de regressão — comportamentos novos/inferidos)

- **Gitignore só no alvo (D-04, 🟡 novo).** Nos projetos-alvo, `.harness/harness-core/` é gitignorado; no repo-fonte o core permanece **versionado** (`git ls-files .harness/harness-core/` não vazio). Confirmar que uma extração futura não interprete o gitignore como "core ausente".
- **Falha barulhenta do wrapper (RN-07, 🟡 novo).** Com o core ausente, o wrapper encerra com código ≠ 0 e instrui restauração via `upgrade`/`init`. Verificado no smoke do `init`.
- **`harness.toml` operativo na raiz (D-05, 🟢).** Permanece lido cwd-relative; só o template `harness-core/harness.toml` acompanha o core. Sem mudança em `load_config`.
- **Instalações antigas com `harness-core/` órfão.** Após `upgrade`, alvos antigos mantêm o diretório `harness-core/` na raiz até remoção manual (não-destrutivo). Não é regressão; é dívida de migração documentada em `onboarding.md`.

## Histórico de re-extrações

<!-- Preenchido pelo agente reverso quando `/reversa` rodar novamente. -->

### Re-extração 2026-06-25 14:32

> Re-confirmação na rodada completa 001–012 (a rodada cirúrgica de 13:39 já cobrira esta feature). Verificação factual: filesystem + suíte.

| ID   | Veredito | Observação                                                                                                                                 |
| ---- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| W001 | 🟢 verde | `init` copia para `.harness/harness-core/` e grava a entrada no `.gitignore`; raiz do repo-fonte limpa (sem resíduo `harness-core/`).      |
| W002 | 🟢 verde | `upgrade` copia para `.harness/harness-core/`, preserva `.reversa/`/`.harness/decisoes/`, `.gitignore` idempotente; coberto pela suíte.    |
| W003 | 🟢 verde | Leitura de versão usa `CORE_CONFIG_CANDIDATE_RELPATHS` com o canônico `.harness/harness-core/src/core/domain/config.py` como 1º candidato. |
| W004 | 🟢 verde | Wrapper da raiz resolve `.harness/harness-core/src/main.py`; venv em `.harness/harness-core/.venv`; `domain.md`/`inventory.md` coerentes.  |
| W005 | 🟢 verde | Ganchos Git embutem `.harness/harness-core/src/main.py` e `.harness/harness-core/.venv/bin/python3`.                                       |

### Re-extração 2026-06-25 13:39

| ID   | Veredito | Observação                                                                                                                                                                                                   |
| ---- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| W001 | 🟢 verde | `init` copia para `.harness/harness-core/` (`CORE_REL_PATH`) e grava a entrada no `.gitignore`; RN-N19 reconciliada                                                                                          |
| W002 | 🟢 verde | `upgrade` copia para `.harness/harness-core/`, exclui `.harness` da cópia, preserva `.reversa/`/`.harness/decisoes/` e mantém o `.gitignore` idempotente; RN-N20 reconciliada                                |
| W003 | 🟢 verde | A leitura de versão lê o canônico `.harness/harness-core/src/core/domain/config.py` — agora como **primeiro candidato** (feature 012 generalizou para `CORE_CONFIG_CANDIDATE_RELPATHS`); essência preservada |
| W004 | 🟢 verde | Wrapper da raiz resolve `MAIN_PY=.harness/harness-core/src/main.py`; `domain.md#wrapper-executavel` e `inventory.md` reconciliados                                                                           |
| W005 | 🟢 verde | Ganchos Git embutem `.harness/harness-core/src/main.py` e `.harness/harness-core/.venv/bin/python3` via `CORE_MAIN_REL_PATH`/`CORE_VENV_PYTHON_REL_PATH`                                                     |

## Arquivadas

_(vazio)_
