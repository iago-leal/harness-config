# Data-delta: Upgrade resiliente do harness-core

> Identificador: `012-corrige-upgrade-stale`
> Data: `2026-06-25`

## 1. Escopo de dados

A feature **não** possui banco de dados, ORM, migrations nem entidades persistidas. O harness-core opera sobre o sistema de arquivos do projeto. O "modelo de dados" relevante são arquivos de configuração e o **contrato de resolução de versão** do upstream. Não há migração de dados de usuário.

## 2. Diff conceitual sobre o modelo extraído

| Artefato                        | Hoje (`_reversa_sdd/`)                                                                | Depois                                                                                                                          | Tipo                   |
| ------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| Resolução da versão do upstream | Caminho **fixo** do `config.py` do core no upstream (`_get_upstream_version`, RN-N21) | Lista de **caminhos-candidato** (canônico `.harness/harness-core/...` + legado raiz `harness-core/...`); erro se nenhum resolve | contrato-alterado      |
| Fonte dos caminhos do core      | `CORE_REL_PATH` único em `layout.py` (feature 011)                                    | `+ CORE_CONFIG_CANDIDATE_RELPATHS` (ou equivalente): lista ordenada de relpaths candidatos do `config.py`                       | campo-novo (constante) |
| `harness.toml` campo `version`  | String semântica da versão instalada (RN-N18); atualizada no `upgrade`                | **Inalterado** em forma e semântica; sob `--force` com versão indeterminada, é **preservado** (não sobrescrito)                 | inalterado             |
| `.gitignore` do alvo            | Entrada `.harness/harness-core/` idempotente (feature 011)                            | **Inalterado**                                                                                                                  | inalterado             |

## 3. Campos novos

- **`CORE_CONFIG_CANDIDATE_RELPATHS`** (constante em `layout.py`): tupla ordenada de caminhos relativos do `config.py` a tentar, do canônico ao legado. Único ponto de mudança quando o layout evoluir.

## 4. Campos removidos

- Nenhum. O fallback `return self.current_version` em `_get_upstream_version` é **comportamento removido** (passa a levantar erro), não um campo.

## 5. Migrações necessárias

- **Dados:** n/a (sem persistência).
- **Instalações no layout antigo:** não é migração de dados, mas de **layout físico** — coberta pela recuperação via `init` do upstream (RF-05), documentada no `onboarding.md`. Não-destrutiva: preserva `.reversa/` e `.harness/decisoes/`.

## 6. Índices, constraints, triggers

- n/a.
