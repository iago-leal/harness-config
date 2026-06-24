# Comandos Customizados (Commands) — Requisitos (Requirements)

> Regenerado pelo Writer em 2026-06-24 (Re-extração após a feature 004)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`harness-core/src/core/commands/service.py`](file:///Users/iagoleal/dev/harness/harness-core/src/core/commands/service.py); consome `core/session/*`. Driver: `src/main.py` (subcomando `cmd`, hook `SessionStart`).

> ⚠️ **Reescrita vs versão anterior:** os comandos **deixaram de ser** arquivos Markdown em `harness-config/commands/` (purgados, commit `5624f78`) e passaram a ser o `CommandService` Python em `harness-core`. O estado de sessão saiu de `ESTADO-DA-SESSAO.md` (raiz) para `.harness/estado-da-sessao.md` (feature 004). Não há mais `~/.agent-memory/BASTAO.md` nem ponte de memória; `handoff`/`resume` operam sobre o estado local.

## Visão Geral

Despacha slash commands de sessão agnósticos à IDE: `resume`, `encerrar-sessao`, `handoff`, `clarificar`. Carrega/grava o estado de sessão em `.harness/estado-da-sessao.md`, valida a âncora Git na retomada e reinjeta a narrativa preservada. O serviço não conhece o harness — a seleção do _sink_ fica na borda (`main.py`).

## Responsabilidades

- Normalizar e despachar o comando (`strip().lower().lstrip("/")`). 🟢
- `resume`: criar/reativar a sessão preservando a narrativa; alertar se HEAD ≠ âncora. 🟢
- `encerrar-sessao`: gravar o commit-âncora e desativar a sessão. 🟢
- `handoff` / `clarificar`: produzir blocos de texto (handoff com feature+HEAD; clarificar com texto fixo de limite de rodadas). 🟢
- Distinguir estado **ausente** de **malformado** (falha barulhenta). 🟢

## Regras de Negócio

- **RN-07 — Âncora Git de integridade:** em `resume`, se HEAD ≠ `commit_hash` do estado, monta `⚠️ ALERTA` que antecede a narrativa; reativa mesmo assim. 🟢
- **RN-N3 — Narrativa preservada:** `start_session` reativa preservando a narrativa escrita pelo agente; a CLI reinjeta o corpo dela, nunca o inventa. 🟢
- **RN-N4 — Ausente ≠ malformado:** arquivo ausente → `None` (sessão nova); malformado → `MalformedSessionStateError`. 🟢
- **RN-N5 — Core não conhece o harness:** o serviço produz texto puro; a seleção do mecanismo de entrega por `active_harness` vive na borda (`get_sink` + `main.py`). 🟢
- **Isolamento no fechamento:** `encerrar-sessao` exige sessão ativa (senão erro), lê HEAD, `close_session(commit)` e salva atomicamente. 🟢

## Requisitos Funcionais

| ID    | Requisito                  | Prioridade | Critério de Aceite                                                                                                                          |
| ----- | -------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| RF-01 | Comando `resume`.          | Must       | Sem sessão → cria com HEAD e feature `args[0]` (ou `default_feature`); com sessão → reativa, reinjeta narrativa, alerta se âncora divergir. |
| RF-02 | Comando `encerrar-sessao`. | Must       | Exige sessão ativa; grava commit-âncora via `close_session`; salva atomicamente.                                                            |
| RF-03 | Comando `handoff`.         | Should     | Monta bloco Markdown com feature ativa + HEAD.                                                                                              |
| RF-04 | Comando `clarificar`.      | Should     | Retorna texto fixo (limite de 2 rodadas de diálogo).                                                                                        |
| RF-05 | Comando desconhecido.      | Must       | Retorna `"Comando desconhecido: <command>"`.                                                                                                |

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

> 🟢 **T2 — RESOLVIDO (feature 006):** via MCP (`server.py:94`), `session_command` lê o caminho de sessão de `config.session.state_file`, o mesmo `.harness/estado-da-sessao.md` que a CLI usa. Não há mais literal `ESTADO-DA-SESSAO.md` na raiz nem divergência CLI×MCP; o estado converge.
