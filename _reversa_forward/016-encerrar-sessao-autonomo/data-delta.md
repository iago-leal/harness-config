# Data Delta: encerrar-sessao autônomo

> Identificador: `016-encerrar-sessao-autonomo`
> Data: `2026-06-27`

Não há banco de dados. O "modelo" afetado é a **configuração tipada** (`HarnessConfig`) e, indiretamente, o estado de sessão (sem mudança de schema).

## 1. Configuração — `harness.toml` / `HarnessConfig`

Novo campo opcional, retrocompatível (ausente → comportamento atual).

| Entidade              | Campo     | Tipo            | Default | Origem                      |
| --------------------- | --------- | --------------- | ------- | --------------------------- |
| `RegenSection` (nova) | `command` | `Optional[str]` | `None`  | `src/core/domain/config.py` |

Exemplo no `harness.toml`:

```toml
[regen]
command = "python gerar_site.py && python empacotar.py"
```

- Ausente a seção/campo → `RegenSection().command is None` → `cmd regen` é no-op (exit 0).
- O template gerado por `init` (`init_service.py:134`) pode incluir a seção comentada para descoberta, sem ativá-la.

## 2. Estado de sessão — `.harness/estado-da-sessao.md`

**Sem mudança de schema.** O front-matter (`commit`, `feature`, `start_time`, `status`) e o corpo de 4 seções permanecem (RN-N1/N2). O delta é só de **comportamento de transição**:

| Estado de entrada no `encerrar-sessao` | Antes (015)                            | Depois (016)                                                           |
| -------------------------------------- | -------------------------------------- | ---------------------------------------------------------------------- |
| `status: active`                       | fecha + commit                         | inalterado                                                             |
| `status: inactive`                     | `NoActiveSessionError`, exit ≠ 0       | reativa (`start_session`) + fecha + commit, exit 0, anuncia reativação |
| ausente (`None` / campos `null`)       | `NoActiveSessionError`, exit ≠ 0       | no-op ruidoso, exit 0, sem commit                                      |
| malformado                             | `MalformedSessionStateError`, exit ≠ 0 | inalterado (continua barulhento)                                       |

## 3. Artefato de IDE — `.claude/settings.json`

Não é "dado" de domínio, mas passa a ser **escrito** por `init`/`upgrade` (antes, nunca). Merge idempotente: preserva chaves existentes e só garante o hook `SessionStart → cmd resume`. Sem migração destrutiva.

## 4. Migrações necessárias

Nenhuma migração de dados. A propagação é por `./harness upgrade` (bump 1.2.53). Consumidores sem `[regen]` não percebem diferença além da tolerância no fechamento e do hook plantado.
