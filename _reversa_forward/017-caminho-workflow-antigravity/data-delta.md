# Data Delta: feature 017

> Feature `017-caminho-workflow-antigravity` · 2026-06-27

Esta feature **não toca banco de dados** nem modelo de domínio de runtime. O `harness-core` não tem persistência relacional; o "estado" relevante são artefatos materializados no filesystem do projeto consumidor e a constante de versão. Registro aqui o diff conceitual desses artefatos.

## 1. Artefato de workflow do Antigravity

| Aspecto          | Antes                                           | Depois                                           |
| ---------------- | ----------------------------------------------- | ------------------------------------------------ |
| Caminho relativo | `.agents/workflows/encerrar-sessao.md` (plural) | `.agent/workflows/encerrar-sessao.md` (singular) |
| Frontmatter      | `name:` + `description:`                        | `description:` apenas                            |
| Corpo            | inalterado (delega ao `CommandService`)         | inalterado                                       |

Origem no legado: `_reversa_sdd/comandos-customizados/requirements.md#f010` (✨f010), que documenta o caminho plural — a reconciliar por re-extração.

## 2. Constante de versão do core

| Campo                              | Antes    | Depois   | Local                                |
| ---------------------------------- | -------- | -------- | ------------------------------------ |
| `HarnessSection.version`           | `1.2.53` | `1.2.54` | `src/core/domain/config.py`          |
| `BootstrapService.current_version` | `1.2.53` | `1.2.54` | `src/core/bootstrap/init_service.py` |
| asserção de versão                 | `1.2.53` | `1.2.54` | `tests/test_init.py`                 |

## 3. Migração

Aplicada pelo próprio `upgrade` (sem script dedicado):

1. **Gravar-no-novo:** `materialize_session_commands` escreve `.agent/workflows/encerrar-sessao.md`.
2. **Remover-o-velho:** a mesma rotina remove `.agents/workflows/encerrar-sessao.md` se existir.
3. **Preservar terceiros:** remove apenas o arquivo nomeado; nunca o diretório nem outros `.md`.

Idempotência: rodar o `upgrade` repetidamente converge — o arquivo novo é reescrito (atômico) e o órfão, uma vez removido, deixa de existir (a remoção verifica existência antes).

## 4. Sem mudanças

- Sem novas tabelas, colunas, índices ou constraints (não há BD).
- Sem mudança no estado de sessão (`.harness/estado-da-sessao.md`).
- Sem mudança no `.claude/commands/encerrar-sessao.md` nem nos hooks (`.agents/hooks.json`) — fora do escopo (clarify).
