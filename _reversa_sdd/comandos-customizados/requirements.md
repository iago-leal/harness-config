# Comandos Customizados (Commands) — Requisitos (Requirements)

> Regenerado pelo Writer em 2026-06-24 (Re-extração após a feature 004)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`.harness/harness-core/src/core/commands/service.py`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/core/commands/service.py); consome `core/session/*`. Driver: `src/main.py` (subcomando `cmd`, hook `SessionStart`).

> ⚠️ **Reescrita vs versão anterior:** os comandos **deixaram de ser** arquivos Markdown em `harness-config/commands/` (purgados, commit `5624f78`) e passaram a ser o `CommandService` Python em `harness-core`. O estado de sessão saiu de `ESTADO-DA-SESSAO.md` (raiz) para `.harness/estado-da-sessao.md` (feature 004). Não há mais `~/.agent-memory/BASTAO.md` nem ponte de memória; `handoff`/`resume` operam sobre o estado local.

## Visão Geral

Despacha slash commands de sessão agnósticos à IDE: `resume`, `encerrar-sessao`, `handoff`, `clarificar`. Carrega/grava o estado de sessão em `.harness/estado-da-sessao.md`, valida a âncora Git na retomada e reinjeta a narrativa preservada. O serviço não conhece o harness — a seleção do _sink_ fica na borda (`main.py`).

> ✨ **f010 → skill ✨f018 — `encerrar-sessao` exposto como skill de IDE:** além do acionamento por `./harness cmd encerrar-sessao` e pela tool MCP, o `init`/`upgrade` materializa a capacidade direto na IDE do agente. ✨f018 trocou a forma do artefato de slash command/workflow `.md` para uma **skill versionável** (`SKILL.md` + `scripts/` finos) gravada sob `.claude/skills/encerrar-sessao/` (Claude) e `.agents/skills/encerrar-sessao/` (Antigravity, ativação semântica), sempre os dois — `materialize_session_skills` itera os perfis e copia a mesma árvore agnóstica dos assets do core; os órfãos legados (command/workflow) são removidos na migração, preservando terceiros. Os scripts **não reimplementam** o fechamento — consomem o `SessionCloseFlow` do core (RN-N5/RN-N33 preservadas). Ver `_reversa_sdd/domain.md#2.12` (RN-N28/RN-N29) e `#2.15` (RN-N33), e ADR 0018 (que substitui a 0017).

## Responsabilidades

- Normalizar e despachar o comando (`strip().lower().lstrip("/")`). 🟢
- `resume`: criar/reativar a sessão preservando a narrativa; alertar se HEAD ≠ âncora. 🟢
- `encerrar-sessao`: capturar a âncora (HEAD de trabalho), desativar a sessão e **versionar** o registro num commit isolado (só o `state_file`) por cima do trabalho. 🟢
- `handoff` / `clarificar`: produzir blocos de texto (handoff com feature+HEAD; clarificar com texto fixo de limite de rodadas). 🟢
- Distinguir estado **ausente** de **malformado** (falha barulhenta). 🟢

## Regras de Negócio

- **RN-07 — Âncora Git de integridade:** em `resume`, se HEAD ≠ `commit_hash` do estado, monta `⚠️ ALERTA` que antecede a narrativa; reativa mesmo assim. 🟢
- **RN-N3 — Narrativa preservada:** `start_session` reativa preservando a narrativa escrita pelo agente; a CLI reinjeta o corpo dela, nunca o inventa. 🟢
- **RN-N4 — Ausente ≠ malformado:** arquivo ausente → `None` (sessão nova); malformado → `MalformedSessionStateError`. 🟢
- **RN-N5 — Core não conhece o harness:** o serviço produz texto puro; a seleção do mecanismo de entrega por `active_harness` vive na borda (`get_sink` + `main.py`). 🟢
- **Isolamento no fechamento:** `encerrar-sessao` exige sessão ativa (senão erro), captura a âncora com `get_head_commit` **antes** das escritas, `close_session(ancora)`, salva atomicamente e então cria um commit contendo **só** o `state_file` via `GitPort.commit_paths` (nunca `git add -A`); a âncora segue no trabalho, o commit de encerramento por cima. Falha de commit → `SessionCommitError` (barulhento), sem reverter o estado salvo; a saída reporta os dois hashes. ✨f013 (ver `domain.md#2.14`). 🟢

## Requisitos Funcionais

| ID    | Requisito                  | Prioridade | Critério de Aceite                                                                                                                                                                                  |
| ----- | -------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RF-01 | Comando `resume`.          | Must       | Sem sessão → cria com HEAD e feature `args[0]` (ou `default_feature`); com sessão → reativa, reinjeta narrativa, alerta se âncora divergir.                                                         |
| RF-02 | Comando `encerrar-sessao`. | Must       | Exige sessão ativa; grava a âncora via `close_session`; salva atomicamente; **versiona** só o `state_file` num commit por cima do trabalho e reporta os dois hashes (falha → `SessionCommitError`). |
| RF-03 | Comando `handoff`.         | Should     | Monta bloco Markdown com feature ativa + HEAD.                                                                                                                                                      |
| RF-04 | Comando `clarificar`.      | Should     | Retorna texto fixo (limite de 2 rodadas de diálogo).                                                                                                                                                |
| RF-05 | Comando desconhecido.      | Must       | Retorna `"Comando desconhecido: <command>"`.                                                                                                                                                        |

## Requisitos Não Funcionais

| Tipo              | Requisito inferido                                         | Evidência no código                         | Confiança |
| ----------------- | ---------------------------------------------------------- | ------------------------------------------- | --------- |
| Robustez          | Estado corrompido falha barulhento (distingue de ausente). | `core/commands/service.py` (`load_session`) | 🟢        |
| Baixo acoplamento | Serviço agnóstico a harness; sink na borda.                | `core/commands/service.py`, `main.py`       | 🟢        |
| Atomicidade       | Estado salvo via serializer + gravação atômica.            | `core/commands/service.py`                  | 🟢        |

## Critérios de Aceitação

```gherkin
Dado que não existe estado de sessão
Quando `./harness cmd resume 005-decisoes-em-harness`
Então uma nova sessão é criada com o HEAD atual e a feature informada, e retorna "Nova sessão".

Dado uma sessão existente e HEAD diferente da âncora gravada
Quando `./harness cmd resume`
Então a resposta antecede um ⚠️ ALERTA de divergência de âncora à narrativa reinjetada.

Dado uma sessão ativa
Quando `./harness cmd encerrar-sessao`
Então o commit HEAD é gravado como âncora e a sessão fica inativa.

Dado um arquivo de estado malformado
Quando load_session é chamado
Então um MalformedSessionStateError é levantado (não tratado como sessão nova).
```

## Prioridade (MoSCoW)

| Requisito                               | MoSCoW | Justificativa                                                     |
| --------------------------------------- | ------ | ----------------------------------------------------------------- |
| `resume` com âncora e narrativa (RF-01) | Must   | Coração da retomada do ciclo forward.                             |
| `encerrar-sessao` (RF-02)               | Must   | Fecha a sessão e grava a âncora; sem ele a retomada não tem base. |
| `handoff` / `clarificar` (RF-03/04)     | Should | Apoios ao fluxo; texto derivado/fixo.                             |
| Comando desconhecido (RF-05)            | Must   | Falha previsível e legível.                                       |

## Rastreabilidade de Código

| Arquivo                      | Função / Classe                                                                                                                     | Cobertura |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `core/commands/service.py`   | `CommandService.execute_command`, `load_session`, `save_session`                                                                    | 🟢        |
| `core/session/serializer.py` | `render`, `render_narrative` (consumidos)                                                                                           | 🟢        |
| `core/domain/models.py`      | `SessionState`, `SessionNarrative`                                                                                                  | 🟢        |
| `src/main.py`                | Subcomando `cmd`, caminho de sessão lido de `config.session.state_file` (default `.harness/estado-da-sessao.md`), resolução de sink | 🟢        |

> ✨ **f013 — Encerramento versionado:** `encerrar-sessao` cria um commit isolado do `state_file` via `GitPort.commit_paths` (porta em `core/ports/git.py`, adapter em `adapters/git/subprocess.py`); falha de commit → `SessionCommitError` (`core/commands/errors.py`). A âncora segue no trabalho e a saída reporta os dois hashes. Ver `domain.md#2.14` (RN-N31/RN-N32).

> 🟢 **T2 — RESOLVIDO (feature 006):** via MCP (`server.py:94`), `session_command` lê o caminho de sessão de `config.session.state_file`, o mesmo `.harness/estado-da-sessao.md` que a CLI usa. Não há mais literal `ESTADO-DA-SESSAO.md` na raiz nem divergência CLI×MCP; o estado converge.
