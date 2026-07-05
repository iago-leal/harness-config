# Migrate (Conversão da Base Instalada para a Fonte Única) — Requisitos (Requirements)

> Gerado pelo Writer em 2026-07-05 (Re-extração de reconciliação — feature 020-fonte-unica-e-hooks; unit NOVA, sem cobertura anterior)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`.harness/harness-core/src/core/migrate/service.py`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/core/migrate/service.py) (`MigrateService`); usa `core/bootstrap/shim.py` (`render_shim`), `core/bootstrap/service.py` (`BootstrapService`), `core/install/claude_settings.py` (`materialize_claude_settings`), `core/domain/layout.py` (`CORE_REL_PATH`, `CORE_MAIN_REL_PATH`). Driver: `src/main.py`, subcomando `migrate [root] [--dry-run]`.

## Visão Geral

Converte instalações do harness que ainda estão no **layout copiado** (cópia local do `harness-core` + `.venv` própria por projeto, modelo pré-feature-020) para a **fonte única** (shim `./harness` + core executado a partir do repositório upstream). Varre uma raiz (default `~/dev`), identifica cada instalação por `harness.toml`, e converte cada uma na ordem shim → ganchos Git → settings do Claude → remoção de `version` → remoção da cópia local do core (por último, para nunca deixar o projeto sem executor). É uma ferramenta de **manutenção da base já instalada**, não uma operação automática disparada por outra feature — o mantenedor a executa deliberadamente, com `--dry-run` disponível para inspeção prévia.

## Responsabilidades

- Varrer uma raiz por subpastas que contenham `harness.toml`. 🟢
- Para cada instalação encontrada, decidir se é elegível para migração (guardas de segurança) ou deve ser pulada, com o motivo. 🟢
- Converter instalações elegíveis: escrever o shim, instalar ganchos Git não-destrutivos, mesclar `.claude/settings.json`, remover o campo `version` do `harness.toml`, e só então remover a(s) cópia(s) locais do core. 🟢
- Nunca remover o core do próprio upstream nem cair numa autorreferência circular. 🟢
- Suportar `--dry-run`: relatar o que seria feito (diretórios a remover) sem escrever ou remover nada. 🟢

## Regras de Negócio

- **RN-N38 — Migração da base instalada via comando dedicado:** `harness migrate [root] [--dry-run]` converte instalações no layout copiado para a fonte única; é a exceção consciente ao footprint per-projeto (RN-N17), pois atua sobre _outros_ projetos por design. 🟢 (`domain.md#2.17`)
- **Guarda 1 — Nunca migrar o próprio upstream:** se o projeto avaliado for, ele mesmo, o `upstream_self` informado (a fonte real do core), a migração é pulada com o motivo `"upstream (fonte do core)"`. 🟢
- **Guarda 2 — Nunca migrar autorreferência:** se o `upstream_path` do projeto apontar para dentro dele mesmo (`up_abs == proj_abs` ou `up_abs` é subcaminho de `proj_abs`), ou se não houver `upstream_path` configurado, a migração é pulada. 🟢
- **Guarda 3 — Upstream precisa existir:** se o core do upstream declarado não existir no caminho esperado (`CORE_MAIN_REL_PATH`), a migração é pulada — o shim ficaria quebrado. 🟢
- **Ordem segura de conversão:** shim + ganchos + settings são escritos **antes** de qualquer remoção; a(s) cópia(s) do core são removidas **por último**, garantindo que o projeto nunca fique sem um `./harness` funcional durante o processo. 🟢
- **Guarda de remoção (`_safe_remove_core`):** recusa remover qualquer diretório cujo nome-base não seja literalmente `harness-core` — proteção contra um `remove_tree` malformado apagar o alvo errado. 🟢
- **`--dry-run` não tem efeito colateral:** relata `status: "would-migrate"` e a lista de diretórios que seriam removidos, sem escrever nem remover nada. 🟢

## Requisitos Funcionais

| ID    | Requisito                                     | Prioridade | Critério de Aceite                                                                                                                    |
| ----- | --------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| RF-01 | Varredura de instalações sob uma raiz.        | Must       | Toda subpasta direta de `root` com `harness.toml` é avaliada; ausência de `harness.toml` → ignorada silenciosamente.                  |
| RF-02 | Guarda contra automigração do upstream.       | Must       | Projeto igual a `upstream_self` → `status: "skipped"`, `reason: "upstream (fonte do core)"`.                                          |
| RF-03 | Guarda contra autorreferência / sem upstream. | Must       | `upstream_path` ausente ou apontando para dentro do próprio projeto → `status: "skipped"`.                                            |
| RF-04 | Guarda contra upstream inacessível.           | Must       | Core do upstream ausente no caminho esperado → `status: "skipped"`, `reason: "core do upstream ausente"`.                             |
| RF-05 | Conversão na ordem segura.                    | Must       | Shim escrito e ganchos/settings aplicados antes de qualquer `remove_tree`; a cópia local do core é o último passo.                    |
| RF-06 | Modo `--dry-run`.                             | Must       | Nenhuma escrita nem remoção ocorre; retorno inclui `status: "would-migrate"` e a lista de diretórios que seriam removidos.            |
| RF-07 | Guarda de remoção por nome-base.              | Must       | `_safe_remove_core` levanta `ValueError` se o `basename` do caminho a remover não for `harness-core`.                                 |
| RF-08 | Suporte ao layout duplo (legado + pós-011).   | Should     | Detecta e remove tanto `harness-core/` (raiz, pré-011) quanto `.harness/harness-core/` (pós-011) se ambos existirem no mesmo projeto. |

## Requisitos Não Funcionais

| Tipo           | Requisito inferido                                                                                                                          | Evidência no código                               | Confiança |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | --------- |
| Segurança      | Nunca remove o core do upstream nem de uma autorreferência circular.                                                                        | `MigrateService._migrate_one` (guardas 1 e 2)     | 🟢        |
| Segurança      | Remoção física restrita a diretórios `harness-core` por nome-base.                                                                          | `MigrateService._safe_remove_core`                | 🟢        |
| Auditabilidade | `--dry-run` permite inspecionar o efeito antes de qualquer escrita real.                                                                    | `MigrateService.migrate(dry_run=True)`            | 🟢        |
| Idempotência   | Reexecutar sobre uma instalação já migrada não deveria reencontrar nada a converter (sem `harness-core` local, o passo de remoção é no-op). | Inferido da ordem de checagem por `fs.exists`     | 🟡        |
| Resiliência    | Falha ao listar `root` (ex.: permissão) não interrompe com traceback cru.                                                                   | `MigrateService._safe_list` (`try/except` → `[]`) | 🟢        |

## Critérios de Aceitação

```gherkin
Dado um projeto cujo harness.toml aponta upstream_path para o próprio harness em execução
Quando `harness migrate ~/dev`
Então esse projeto aparece no resultado com status "skipped" e motivo "upstream (fonte do core)".

Dado um projeto no layout copiado (com .harness/harness-core/ local) e upstream_path válido
Quando `harness migrate ~/dev --dry-run`
Então o resultado indica status "would-migrate" e lista .harness/harness-core/ entre os diretórios a remover, sem nenhuma escrita ocorrer.

Dado o mesmo projeto, sem --dry-run
Quando `harness migrate ~/dev`
Então o projeto passa a ter um shim executável em ./harness, os ganchos git apontam para o shim, .claude/settings.json foi mesclado, o campo version foi removido do harness.toml, e .harness/harness-core/ não existe mais mesmo assim.

Dado um projeto sem harness.toml na raiz avaliada
Quando `harness migrate ~/dev`
Então esse diretório é ignorado silenciosamente (não aparece nos resultados).
```

## Prioridade (MoSCoW)

| Requisito                                      | MoSCoW | Justificativa                                                                              |
| ---------------------------------------------- | ------ | ------------------------------------------------------------------------------------------ |
| Guardas contra autodestruição (RF-02/03/04/07) | Must   | Sem elas, um `remove_tree` mal disparado apaga a fonte real do core ou o alvo errado.      |
| Ordem segura de conversão (RF-05)              | Must   | Garante que nenhum projeto fique sem `./harness` executável em nenhum momento do processo. |
| `--dry-run` (RF-06)                            | Must   | Única forma de auditar o efeito antes de rodar contra a base real de projetos.             |
| Suporte a layout duplo (RF-08)                 | Should | Cobre o caso conhecido (`livro-mfc`) de projeto com os dois layouts simultâneos.           |

## Rastreabilidade de Código

| Arquivo                                    | Função / Classe                                                                                         | Cobertura |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------- | --------- |
| `core/migrate/service.py`                  | `MigrateService.migrate`, `_migrate_one`, `_safe_remove_core`, `_safe_list`, `_field`, `_strip_version` | 🟢        |
| `core/bootstrap/shim.py`                   | `render_shim` (conteúdo do shim gravado)                                                                | 🟢        |
| `core/bootstrap/service.py`                | `BootstrapService.install_hooks` (reusado, não-destrutivo desde a f020)                                 | 🟢        |
| `core/install/claude_settings.py`          | `materialize_claude_settings` (merge por-item)                                                          | 🟢        |
| `core/domain/layout.py`                    | `CORE_REL_PATH`, `CORE_MAIN_REL_PATH`                                                                   | 🟢        |
| `core/ports/fs.py`, `adapters/fs/local.py` | `FileSystemPort.remove_tree` (novo método, feature 020)                                                 | 🟢        |
| `src/main.py`                              | Subcomando `migrate`, parser de `root`/`--dry-run`                                                      | 🟢        |
| `tests/test_migrate.py`                    | Cobertura de teste (instalação simulada, `--dry-run`, caso duplo)                                       | 🟢        |

> 🟡 **Não executado nos 17 projetos reais até esta reconciliação** — é ação deliberada e separada do mantenedor, fora do escopo automático de qualquer feature. Ver `domain.md#2.17` e ADR 0020 (Consequências).
