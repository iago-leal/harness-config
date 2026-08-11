# Comandos Customizados (Commands) — Requisitos (Requirements)

> Regenerado pelo Writer em 2026-06-24 (Re-extração após a feature 004)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`.harness/harness-core/src/core/commands/service.py`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/core/commands/service.py); consome `core/session/*`. Driver: `src/main.py` (subcomando `cmd`, hook `SessionStart`).

> ⚠️ **Reescrita vs versão anterior:** os comandos **deixaram de ser** arquivos Markdown em `harness-config/commands/` (purgados, commit `5624f78`) e passaram a ser o `CommandService` Python em `harness-core`. O estado de sessão saiu de `ESTADO-DA-SESSAO.md` (raiz) para `.harness/estado-da-sessao.md` (feature 004). Não há mais `~/.agent-memory/BASTAO.md` nem ponte de memória; `handoff`/`resume` operam sobre o estado local.

## Visão Geral

Despacha slash commands de sessão agnósticos à IDE: `resume`, `encerrar-sessao`, `handoff`, `clarificar`. Carrega/grava o estado de sessão em `.harness/estado-da-sessao.md`, valida a âncora Git na retomada e reinjeta a narrativa preservada. O serviço não conhece o harness — a seleção do _sink_ fica na borda (`main.py`).

> ✨ **f010 → skill ✨f018 — `encerrar-sessao` exposto como skill de IDE:** além do acionamento por `./harness cmd encerrar-sessao` e pela tool MCP, o `init`/`upgrade` materializa a capacidade direto na IDE do agente. ✨f018 trocou a forma do artefato de slash command/workflow `.md` para uma **skill versionável** (`SKILL.md` + `scripts/` finos) gravada sob `.claude/skills/encerrar-sessao/` (Claude) e `.agents/skills/encerrar-sessao/` (Antigravity, ativação semântica), sempre os dois — `materialize_session_skills` itera os perfis e copia a mesma árvore agnóstica dos assets do core; os órfãos legados (command/workflow) são removidos na migração, preservando terceiros. Os scripts **não reimplementam** o fechamento — consomem o `SessionCloseFlow` do core (RN-N5/RN-N33 preservadas). Ver `_reversa_sdd/domain.md#2.12` (RN-N28/RN-N29) e `#2.15` (RN-N33), e ADR 0018 (que substitui a 0017).
>
> ✨ **f019 — Pré-check de pendência restrito ao arquivo de estado (reconciliação 2026-07-05):** `SessionCloseFlow.pending_work_paths` (a orquestração em volta de `encerrar-sessao`, RN-N33) excluía **todo** o diretório `.harness/` da oferta de commit pendente; passou a excluir só o caminho exato de `session_file`. Consequência: decisões (`.harness/decisoes/MD-*.md`) e o índice (`.harness/microdecisoes.md`) sujos agora **entram** na oferta (`COMMIT_PENDENTE` sem TTY, listagem `[s/N]` com TTY) antes de `encerrar-sessao` prosseguir. `RF-02` abaixo passa a exigir esse pré-check limpo como precondição. Ver `domain.md#2.16` (RN-N34/RN-N35), ADR 0019.
>
> ✨ **f021 — Apêndice do índice de decisões no `resume` (reconciliação 2026-07-05):** quando `active_harness == "claude"` e `session.inject_decisions_index` (default `True`) estão satisfeitos, o `resume` (RF-01) anexa `.harness/microdecisoes.md` ao texto reinjetado, **depois** da narrativa — função pura `build_decisions_appendix` em `core/session/resume_context.py`, gate calculado em `main.py`. Não-bloqueante: índice ausente → aviso em `stderr`, resume segue só com o estado. Ver `domain.md#2.18` (RN-N41), ADR 0021.

> ✨ **f028 — Apêndice trocado pela visão compacta (reconciliação 2026-08-11-b):** `build_decisions_appendix(fs, index_file, enabled, compact_file=None)` passa a injetar a **visão compacta** `.harness/decisoes-recentes.md` (contagem, ponteiros, K=10 títulos mais recentes) em vez do índice integral — o custo do resume vira O(K), não mais O(N fichas). Precedência autoresolvente: compacta ausente (instalação pré-028) → cai para o índice completo com `Aviso:` em stderr, corrigido na primeira compilação seguinte; ambos ausentes → só o estado, exit 0. Corte Claude-only da 021 preservado. Ver RN-N41 revisada (`domain.md#2.18`), `domain.md#2.26`, ADR 0028 / MD-0022.
>
> ✨ **f022/f023 — 3º portão: registro obrigatório de microdecisões (reconciliação 2026-07-15):** `SessionCloseFlow.run(..., sem_decisao=False)` ganhou, depois do pré-check e do gate de narrativa, o portão de registro (`evaluate_registration_gate`, unit `microdecisoes/`): trabalho substantivo desde a âncora sem ficha `MD-*.md` tocada → aborta com marker `[HARNESS:DECISAO_PENDENTE ...]` (protocolo abortar-e-reexecutar) e persiste o fingerprint **fino** no estado; a reexecução com o mesmo estado avisa "não sanada" e libera (anti-loop); trabalho novo **rearma** (teste-guarda da f023); `--sem-decisao` (novo flag do `cmd`) satisfaz o gate gravando a declaração na narrativa (rastro auditável, RN-N3 preservada). Desativável por `decisions.require_registration`. Ver `domain.md#2.20-2.21` (RN-N43..N47), ADRs 0022/0023.

## Responsabilidades

- Normalizar e despachar o comando (`strip().lower().lstrip("/")`). 🟢
- `resume`: criar/reativar a sessão preservando a narrativa; alertar se HEAD ≠ âncora. 🟢
- `encerrar-sessao`: capturar a âncora (HEAD de trabalho), desativar a sessão e **versionar** o registro num commit isolado (só o `state_file`) por cima do trabalho. 🟢
- `handoff` / `clarificar`: produzir blocos de texto (handoff com feature+HEAD; clarificar com texto fixo de limite de rodadas). 🟢
- Distinguir estado **ausente** de **malformado** (falha barulhenta). 🟢
- **✨f019** Antes de `encerrar-sessao` prosseguir: verificar que não há trabalho pendente (exceto o próprio `session_file`) nem narrativa desatualizada — abortar com marker/prompt caso contrário, sem fechar. 🟢
- **✨f022** Terceiro portão: verificar que a sessão registrou microdecisão (ou recebeu `--sem-decisao`) antes de fechar — abortar com marker `DECISAO_PENDENTE` caso contrário, com anti-loop por fingerprint fino. 🟢
- **✨f021** Ao `resume`, quando habilitado, anexar o índice de decisões condensado ao texto reinjetado, para ancorar a busca do agente antes de varreduras amplas. 🟢

## Regras de Negócio

- **RN-07 — Âncora Git de integridade:** em `resume`, se HEAD ≠ `commit_hash` do estado, monta `⚠️ ALERTA` que antecede a narrativa; reativa mesmo assim. 🟢
- **RN-N3 — Narrativa preservada:** `start_session` reativa preservando a narrativa escrita pelo agente; a CLI reinjeta o corpo dela, nunca o inventa. 🟢
- **RN-N4 — Ausente ≠ malformado:** arquivo ausente → `None` (sessão nova); malformado → `MalformedSessionStateError`. 🟢
- **RN-N5 — Core não conhece o harness:** o serviço produz texto puro; a seleção do mecanismo de entrega por `active_harness` vive na borda (`get_sink` + `main.py`). 🟢
- **Isolamento no fechamento:** `encerrar-sessao` exige sessão ativa (senão erro), captura a âncora com `get_head_commit` **antes** das escritas, `close_session(ancora)`, salva atomicamente e então cria um commit contendo **só** o `state_file` via `GitPort.commit_paths` (nunca `git add -A`); a âncora segue no trabalho, o commit de encerramento por cima. Falha de commit → `SessionCommitError` (barulhento), sem reverter o estado salvo; a saída reporta os dois hashes. ✨f013 (ver `domain.md#2.14`). 🟢
- **RN-N34 — Pendência restrita ao arquivo de estado (✨f019):** `pending_work_paths` exclui da oferta de commit **apenas** `session_file`, não o diretório `.harness/` inteiro; decisões e índice sujos entram na oferta. 🟢
- **RN-N35 — Gate de narrativa viva (✨f018, refinado):** `encerrar-sessao` recusa fechar se a narrativa estiver vazia ou idêntica à do commit-âncora de partida — sinal de que o agente esqueceu de consolidar. Fail-open só sem baseline legível na âncora e narrativa já preenchida. 🟢
- **RN-N41 (revisada na ✨f028) — Apêndice de decisões no resume, visão compacta com fallback:** `enabled = active_harness == "claude" and session.inject_decisions_index`; quando `True`, `build_decisions_appendix` anexa a **visão compacta** (`decisions.compact_file`) ao texto do resume, depois do estado; compacta ausente → fallback para o índice completo com `Aviso:` em stderr (autoresolvente); ambos ausentes/vazios ou gate desligado → string vazia (não-bloqueante, exit 0). 🟢

## Requisitos Funcionais

| ID    | Requisito                                                   | Prioridade | Critério de Aceite                                                                                                                                                                                  |
| ----- | ----------------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RF-01 | Comando `resume`.                                           | Must       | Sem sessão → cria com HEAD e feature `args[0]` (ou `default_feature`); com sessão → reativa, reinjeta narrativa, alerta se âncora divergir.                                                         |
| RF-02 | Comando `encerrar-sessao`.                                  | Must       | Exige sessão ativa; grava a âncora via `close_session`; salva atomicamente; **versiona** só o `state_file` num commit por cima do trabalho e reporta os dois hashes (falha → `SessionCommitError`). |
| RF-03 | Comando `handoff`.                                          | Should     | Monta bloco Markdown com feature ativa + HEAD.                                                                                                                                                      |
| RF-04 | Comando `clarificar`.                                       | Should     | Retorna texto fixo (limite de 2 rodadas de diálogo).                                                                                                                                                |
| RF-05 | Comando desconhecido.                                       | Must       | Retorna `"Comando desconhecido: <command>"`.                                                                                                                                                        |
| RF-06 | Pré-check de pendência antes de `encerrar-sessao` (✨f019). | Must       | `pending_work_paths` exclui só `session_file`; se restar trabalho sujo, aborta com marker/prompt sem fechar.                                                                                        |
| RF-07 | Gate de narrativa viva antes de `encerrar-sessao` (✨f018). | Must       | Narrativa vazia ou idêntica à da âncora de partida → aborta com marker/prompt sem fechar.                                                                                                           |
| RF-08 | Apêndice de decisões no `resume` (✨f021, revisado ✨f028).  | Should     | Claude + flag ligado → texto do resume ganha o apêndice após o estado, com a **compacta** como fonte primária e o índice completo como fallback (aviso em stderr); nenhum dos dois presente → resume segue normalmente.       |

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

Dado trabalho não commitado em .harness/decisoes/ (exceto o arquivo de estado)
Quando `./harness cmd encerrar-sessao`
Então o comando aborta com o marker/prompt de pendência e a sessão permanece ATIVA (✨f019).

Dado uma narrativa vazia ou idêntica à do commit-âncora de partida
Quando `./harness cmd encerrar-sessao`
Então o comando aborta com o marker/prompt de narrativa pendente e a sessão permanece ATIVA (✨f018).

Dado active_harness "claude", session.inject_decisions_index true e a visão compacta presente
Quando `./harness cmd resume`
Então o texto reinjetado contém o estado seguido da visão compacta de decisões (✨f021, revisado ✨f028).

Dado active_harness "claude", flag ligado, compacta AUSENTE e índice completo presente
Quando `./harness cmd resume`
Então o texto reinjetado contém o estado seguido do índice completo, com `Aviso:` em stderr (fallback autoresolvente, ✨f028).

Dado active_harness "gemini" (ou o índice de decisões ausente)
Quando `./harness cmd resume`
Então o texto reinjetado contém só o estado, sem apêndice, e nenhum erro é levantado (✨f021).
```

## Prioridade (MoSCoW)

| Requisito                               | MoSCoW | Justificativa                                                     |
| --------------------------------------- | ------ | ----------------------------------------------------------------- |
| `resume` com âncora e narrativa (RF-01) | Must   | Coração da retomada do ciclo forward.                             |
| `encerrar-sessao` (RF-02)               | Must   | Fecha a sessão e grava a âncora; sem ele a retomada não tem base. |
| `handoff` / `clarificar` (RF-03/04)     | Should | Apoios ao fluxo; texto derivado/fixo.                             |
| Comando desconhecido (RF-05)            | Must   | Falha previsível e legível.                                       |
| Pré-check de pendência (RF-06)          | Must   | Evita fechar sessão com decisões/índice órfãos de commit.         |
| Gate de narrativa viva (RF-07)          | Must   | Evita encerrar sem consolidar o que a sessão fez.                 |
| Apêndice de decisões no resume (RF-08)  | Should | Valor de orientação; não crítico ao fechamento em si.             |

## Rastreabilidade de Código

| Arquivo                                    | Função / Classe                                                                                                                     | Cobertura |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `core/commands/service.py`                 | `CommandService.execute_command`, `load_session`, `save_session`                                                                    | 🟢        |
| `core/session/close_flow.py` (✨f018/f019/f022) | `SessionCloseFlow.run` (com `sem_decisao`), `pending_work_paths`, `narrative_is_stale`, `conduct_commit_pendente`, `conduct_narrativa_pendente`, `render_decisao_pendente_marker`, `conduct_decisao_pendente` | 🟢        |
| `core/session/resume_context.py` (✨f021)  | `build_decisions_appendix`                                                                                                          | 🟢        |
| `core/session/serializer.py`               | `render`, `render_narrative` (consumidos)                                                                                           | 🟢        |
| `core/domain/models.py`                    | `SessionState`, `SessionNarrative`                                                                                                  | 🟢        |
| `src/main.py`                              | Subcomando `cmd`, caminho de sessão lido de `config.session.state_file` (default `.harness/estado-da-sessao.md`), resolução de sink | 🟢        |

> ✨ **f013 — Encerramento versionado:** `encerrar-sessao` cria um commit isolado do `state_file` via `GitPort.commit_paths` (porta em `core/ports/git.py`, adapter em `adapters/git/subprocess.py`); falha de commit → `SessionCommitError` (`core/commands/errors.py`). A âncora segue no trabalho e a saída reporta os dois hashes. Ver `domain.md#2.14` (RN-N31/RN-N32).

> 🟢 **T2 — RESOLVIDO (feature 006):** via MCP (`server.py:94`), `session_command` lê o caminho de sessão de `config.session.state_file`, o mesmo `.harness/estado-da-sessao.md` que a CLI usa. Não há mais literal `ESTADO-DA-SESSAO.md` na raiz nem divergência CLI×MCP; o estado converge.
