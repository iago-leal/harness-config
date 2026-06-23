# Data Delta — 004 estado de sessão unificado

> Diff conceitual sobre o modelo extraído em `_reversa_sdd/` (`code-analysis.md#2.5`, `models.py`, `state-machines.md#1`).

## 1. Entidade afetada: `SessionState`

### Antes (legado)
Entidade atômica de quatro campos planos, persistida em `ESTADO-DA-SESSAO.md` (raiz) por regex/markdown simples:

| Campo | Tipo | Persistência atual |
|-------|------|--------------------|
| `commit_hash` | str (SHA-1, 40 hex) | `- **Commit Hash:** ...` |
| `active_feature` | str | `- **Active Feature:** ...` |
| `start_time` | datetime (ISO) | `- **Start Time:** ...` |
| `is_active` | bool | `- **Status:** active/inactive` |

### Depois (004)
O `SessionState` mantém os quatro campos-máquina e ganha um value-object `SessionNarrative`:

| Campo novo | Tipo | Observação |
|------------|------|------------|
| `narrative` | `SessionNarrative` | Value-object; opcional (estado sem narrativa é válido) |

`SessionNarrative` (novo):

| Campo | Tipo | Mapeia para a seção do corpo |
|-------|------|------------------------------|
| `feito` | list[str] \| str | `## O que foi feito` |
| `proximos_passos` | list[str] \| str | `## Próximos passos` |
| `pendencias` | list[str] \| str | `## Pendências / bloqueios` |
| `ponteiros` | list[str] \| str | `## Ponteiros` |

Nenhum campo-máquina é removido. A narrativa é aditiva.

## 2. Mudança de formato do artefato persistido

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Local | `ESTADO-DA-SESSAO.md` (raiz, untracked) **e** `.claude/ESTADO-DA-SESSAO.md` (rico, tracked) | `.harness/estado-da-sessao.md` (único, tracked) |
| Header-máquina | 4 linhas `- **Campo:** valor` | front-matter YAML (`commit`, `feature`, `start_time`, `status`) |
| Narrativa | inexistente no arquivo pobre; só no `.claude/` | corpo Markdown em seções `##` |
| Parser | regex linha-a-linha; falha → `None` silencioso | `pyyaml` + `pydantic`; round-trip; ausente → sessão nova, malformado → erro nomeado |

## 3. Migração de dados (one-shot)

1. O conteúdo de seções do `.claude/ESTADO-DA-SESSAO.md` atual (Feito / Estado atual / Próximos passos / Pendências / Ponteiros) mapeia diretamente para o corpo do novo arquivo.
2. O header-máquina é derivado do estado corrente (`git HEAD`, feature ativa, timestamp, status).
3. `git rm` do `.claude/ESTADO-DA-SESSAO.md`; `git add` do `.harness/estado-da-sessao.md`; `rm` do `ESTADO-DA-SESSAO.md` da raiz (untracked).
4. Projeção para o Antigravity (`.agents/rules/estado-sessao.md`) é gerada a partir do canônico quando `active_harness = antigravity`.

## 4. Máquina de estados

Sem alteração. `INACTIVE ↔ ACTIVE` (`state-machines.md#1`) é preservada: `cmd resume` (INACTIVE→ACTIVE, com check de âncora), `cmd encerrar-sessao` (ACTIVE→INACTIVE, grava âncora, exige repo limpo). Apenas o suporte de persistência muda.

## 5. Índices / constraints

- `commit_hash` mantém a validação pydantic existente (SHA-1, 40 hex).
- Novo: validação de integridade do front-matter (campos-máquina obrigatórios presentes) com erro nomeado — não há índice de banco (persistência é arquivo).
