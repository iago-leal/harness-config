# Data Delta: feature 018

> Feature `018-encerrar-sessao-como-skill` · 2026-06-27

Esta feature **não toca banco de dados** nem cria modelo de domínio novo. O delta é de **artefato materializado** (a forma da entrega muda) e da constante de versão. Os formatos de estado, microdecisão e commit do legado são **reusados sem alteração**.

## 1. Artefato de entrega por harness

| Aspecto     | Antes                                        | Depois                                                                          |
| ----------- | -------------------------------------------- | ------------------------------------------------------------------------------- |
| Forma       | Um arquivo `.md` que delega ao binário       | Um **diretório de skill** (`SKILL.md` + `scripts/`)                             |
| Claude      | `.claude/commands/encerrar-sessao.md`        | `.claude/skills/encerrar-sessao/{SKILL.md,scripts/…}`                           |
| Antigravity | `.agents/workflows/encerrar-sessao.md` (017) | `.agents/skills/encerrar-sessao/{SKILL.md,scripts/…}`                           |
| Lógica      | No core, invocada via CLI                    | No core (intacta), invocada pelos scripts finos da skill via serviço de fachada |

## 2. Formatos do legado reusados (sem delta)

- **Estado-da-sessão**: `.harness/estado-da-sessao.md`, serializer round-trip de 4 seções (RN-N2). Inalterado.
- **Microdecisão**: ficha `MD-NNNN.md` em `.harness/decisoes/` + índice derivado `.harness/microdecisoes.md`. Inalterado.
- **Commit de fechamento**: commit isolado do `state_file` via `GitPort.commit_paths` (RN-N31/N32). Inalterado.

## 3. Constante de versão do core

| Campo                              | Antes    | Depois                           | Local                                |
| ---------------------------------- | -------- | -------------------------------- | ------------------------------------ |
| `HarnessSection.version`           | `1.2.54` | `1.2.55` (a confirmar no coding) | `src/core/domain/config.py`          |
| `BootstrapService.current_version` | `1.2.54` | `1.2.55`                         | `src/core/bootstrap/init_service.py` |
| asserção de versão                 | `1.2.54` | `1.2.55`                         | `tests/test_init.py`                 |

## 4. Migração

Aplicada pelo `upgrade` (reusa `apply_local_materializers`, feature 012):

1. Gravar a árvore da skill em `.claude/skills/encerrar-sessao/` e `.agents/skills/encerrar-sessao/`.
2. Remover os artefatos antigos (`.claude/commands/encerrar-sessao.md`, `.agent(s)/workflows/encerrar-sessao.md`) via `stale_session_command_paths`.
3. Preservar terceiros: remove só os arquivos nomeados pelo perfil; nunca diretórios alheios.

Idempotência: reexecutar reescreve a árvore (atômico) e os caminhos legados, uma vez removidos, deixam de existir.
