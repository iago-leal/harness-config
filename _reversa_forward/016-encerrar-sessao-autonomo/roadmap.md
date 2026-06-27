# Roadmap: encerrar-sessao autônomo — auto-reativa, regenera artefatos e commita o trabalho

> Identificador: `016-encerrar-sessao-autonomo`
> Data: `2026-06-27`
> Requirements: `_reversa_forward/016-encerrar-sessao-autonomo/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

O fechamento deixa de depender do estado ativa/inativa e ganha um fluxo "faz tudo" montado na **borda**, sem ferir os invariantes do core. O conserto crítico é tornar o `encerrar-sessao` **tolerante** (RN-01/D1): sessão inativa reativa e fecha; sessão ausente vira no-op ruidoso; só o estado **malformado** continua falhando barulhento (RN-N4 preservada). Isso já resolve a dor mesmo onde o hook de boot nunca dispara. Em paralelo, planta-se de fato o hook `SessionStart → cmd resume` para o Claude (raiz do bug no `contrato-fotos-higor`), pois hoje `init`/`upgrade` **não** escrevem `.claude/settings.json` — só emitem o bloco como texto colável. O item (iii) entra como capacidade fina e desacoplada: um `cmd regen` que executa um comando declarado no `harness.toml` via o `ProcessPort` já existente, falhando barulhento sem fechar. O item (ii) reusa a dualidade TTY × não-TTY da feature 014: um pré-check da working tree (fora de `.harness/`) emite o marker `[HARNESS:COMMIT_PENDENTE …]`, o agente commita por caminho e re-roda. A skill `.md` apenas sequencia `cmd regen` → `cmd encerrar-sessao`; o core permanece agnóstico ao harness (RN-N5) e single-purpose por comando.

## 2. Princípios aplicados

Não há `.reversa/principles.md` no projeto; valem os princípios do mantenedor (CLAUDE.md global).

| Princípio                           | Como a feature se relaciona                                                                                | Status   |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------- | -------- |
| Baixo acoplamento                   | Core não conhece o regen do projeto; depende do contrato declarado e do `ProcessPort`                      | respeita |
| Alta coesão / SRP                   | `cmd regen` e `cmd encerrar-sessao` são comandos distintos e de propósito único; a sequência vive na borda | respeita |
| Erros barulhentos                   | regen falho, commit falho e estado malformado falham com exit ≠ 0; ausente/inativa são anunciados          | respeita |
| Longevidade / config fora do código | `regen` é declarado no `harness.toml` tipado; determinístico                                               | respeita |
| OOP / contratos explícitos          | Novo `RegenService`, novo verbo no `GitPort`, materializador único para o `settings.json`                  | respeita |
| Footprint global zero               | Toda escrita (settings.json, regen) sob `project_path`/cwd                                                 | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                                                                                                                                                                                       | Justificativa                                                                                | Alternativas descartadas                                                                                                                                    | Confidência |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| D-01 | Campo de regen no `harness.toml` tipado: nova seção `[regen]` com `command: Optional[str] = None` em `config.py`; exemplo comentado no template de `harness.toml` (`init_service.py`)                                                                                                                                                         | Coesão (regen ≠ sessão); config fora do código (RN-N16)                                      | Campo em `SessionSection` (acopla conceitos distintos); arquivo de config separado (rompe a via única)                                                      | 🟢          |
| D-02 | `cmd regen` via novo `RegenService(process)` usando o `ProcessPort.run_command` **existente**, invocando `["sh","-c", command]` para suportar comandos compostos (`&&`, pipes). Ausente → no-op exit 0; falha → exit ≠ 0, não fecha                                                                                                           | `ProcessPort` já abstrai subprocesso; shell habilita comando composto declarado              | Criar port de subprocesso novo (já existe); rodar sem shell (não suportaria `&&`); pôr regen no `CommandService` (acoplaria o serviço git ao `ProcessPort`) | 🟢          |
| D-03 | Reescrever o ramo `encerrar-sessao` no `CommandService`: ausente (`None`) → mensagem "não havia sessão para encerrar", sem commit; inativa → `start_session` (reativa, RN-N3) + `close_session` + commit; ativa → como hoje. `NoActiveSessionError` deixa de ser levantada nesses dois casos                                                  | RN-01/D1: elimina o atrito ativa/inativa; espírito ruidoso preservado (anuncia)              | Manter o erro barulhento da 015 (é o atrito que o usuário pediu para remover); auto-reparar silencioso (violaria observabilidade)                           | 🟢          |
| D-04 | Novo verbo `GitPort.list_dirty_paths(repo_path) -> list[str]` (porcelain) + adapter; pré-check na borda (`main.py`) filtra `.harness/` e, havendo trabalho solto, emite `[HARNESS:COMMIT_PENDENTE …]` (sem TTY) ou pergunta (TTY) e **não fecha** (early return); o agente commita por caminho e re-roda                                      | Espelha a dualidade da feature 014; mensagem descritiva é responsabilidade do agente (borda) | Auto-commit pelo core (risco de capturar lixo; mensagem genérica); `git add -A` (proibido, RN-N32)                                                          | 🟢          |
| D-05 | Novo materializador `materialize_claude_settings(fs, project_path)` que **garante de forma idempotente** a presença do hook `SessionStart → cmd resume` em `.claude/settings.json`, preservando demais chaves e hooks do usuário; ligado em `apply_local_materializers` com gate `active_harness == "claude"` (espelha o gate do Antigravity) | Fecha a raiz do RN-05; `init`/`upgrade` passam a plantar o hook do Claude                    | Manter só a instrução de colar à mão (é a causa do bug); substituir a chave `hooks` inteira (apagaria hooks de terceiros)                                   | 🟡          |
| D-06 | A skill `.md` "faz tudo" apenas **sequencia** `cmd regen` → `cmd encerrar-sessao`; o core não orquestra entre comandos                                                                                                                                                                                                                        | RN-N5 / SRP; mantém cada comando testável isoladamente                                       | `encerrar-sessao` chamar regen internamente (acoplaria encerramento ao `ProcessPort` e à config de regen)                                                   | 🟢          |
| D-07 | Recuperação D2: nenhuma etapa faz rollback. Falha de regen ou de commit aborta **antes** do fechamento; commits/regen já feitos permanecem; sessão não é marcada encerrada; re-executável                                                                                                                                                     | Espelha RN-N32 (`SessionCommitError` não reverte estado salvo); rollback é frágil            | Rollback automático (surpreendente, contra longevidade)                                                                                                     | 🟢          |
| D-08 | Bump 1.2.52 → 1.2.53 em `config.py`, `init_service.py` e `tests/test_init.py`                                                                                                                                                                                                                                                                 | RF-09; propagação via `upgrade`                                                              | —                                                                                                                                                           | 🟢          |

## 4. Premissas

Nenhuma premissa pendente: as duas dúvidas (D1, D2) foram resolvidas no `/reversa-clarify`. A única lacuna do requirements (raiz do RN-05) foi **confirmada por inspeção** nesta fase (ver `investigation.md`), deixando de ser premissa.

## 5. Delta arquitetural

| Componente                         | Arquivo de origem no legado                                     | Tipo de mudança   | Resumo                                                                            |
| ---------------------------------- | --------------------------------------------------------------- | ----------------- | --------------------------------------------------------------------------------- |
| `HarnessConfig`                    | `_reversa_sdd/architecture.md` · `src/core/domain/config.py`    | regra-alterada    | Nova seção tipada `[regen]` (`command: Optional[str]`)                            |
| `CommandService` (ramo encerrar)   | `src/core/commands/service.py`                                  | regra-alterada    | Tolerância a ausente/inativa (D1); `NoActiveSessionError` recua                   |
| `RegenService`                     | (novo) `src/core/regen/service.py`                              | componente-novo   | Executa o comando de regen via `ProcessPort`; falha barulhenta                    |
| `GitPort` / `SubprocessGitAdapter` | `src/core/ports/git.py` · `src/adapters/git/subprocess.py`      | contrato-alterado | Novo verbo `list_dirty_paths`                                                     |
| Dispatch CLI (`cmd`)               | `src/main.py`                                                   | regra-alterada    | Novo `cmd regen`; pré-check + marker `COMMIT_PENDENTE` no `encerrar-sessao`       |
| Materialização de IDE              | `src/core/install/local_apply.py` (+ novo `claude_settings.py`) | componente-novo   | `materialize_claude_settings` ligado ao `apply_local_materializers` (gate claude) |
| Versão                             | `config.py`, `bootstrap/init_service.py`, `tests/test_init.py`  | regra-alterada    | 1.2.52 → 1.2.53                                                                   |

## 6. Delta no modelo de dados

- Resumo das mudanças: apenas configuração — nova seção `[regen]` no `harness.toml` (campo opcional). Sem mudança no `estado-da-sessao.md` nem em qualquer banco.
- Detalhe completo em: `_reversa_forward/016-encerrar-sessao-autonomo/data-delta.md`

## 7. Delta de contratos externos

| Contrato                             | Tipo                                  | Arquivo de detalhe                     |
| ------------------------------------ | ------------------------------------- | -------------------------------------- |
| Marker `[HARNESS:COMMIT_PENDENTE …]` | arquivo / protocolo de borda (agente) | `interfaces/commit-pendente-marker.md` |
| `cmd regen` + seção `[regen]`        | CLI / arquivo de config               | `interfaces/regen-config-contract.md`  |

## 8. Plano de migração

1. Consumidores recebem a 1.2.53 via `./harness upgrade`; o `upgrade` passa a plantar/garantir o hook do Claude em `.claude/settings.json` (idempotente, não-destrutivo).
2. Quem quiser o regen declara `[regen] command = "…"` no `harness.toml`; ausente, nada muda.
3. Sessões já `inactive` em consumidores deixam de bloquear o fechamento na primeira execução pós-upgrade (D3).

## 9. Riscos e mitigações

| Risco                                                                         | Impacto | Probabilidade | Mitigação                                                                                                                                     |
| ----------------------------------------------------------------------------- | ------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| R1 — Testes da 015 afirmam `NoActiveSessionError`/exit≠0 para ausente/inativa | médio   | alto          | Atualizar esses testes para a nova semântica tolerante; manter os testes de malformado-barulhento (RN-N4)                                     |
| R2 — Merge no `.claude/settings.json` apagar hooks/chaves do usuário          | alto    | médio         | Merge idempotente "garantir presença": preserva chaves não-`hooks` e eventos de terceiros; só adiciona o hook de resume do harness se ausente |
| R3 — `cmd regen` via shell executar comando perigoso                          | médio   | baixo         | Comando é declarado pelo próprio dono do projeto; documentado; sem `git add -A`; escrita só sob cwd                                           |
| R4 — regen produzir artefatos que entram indevidamente no commit do trabalho  | baixo   | médio         | Pré-check lista os caminhos; agente decide o split; derivados podem ir ao `.gitignore` (documentado no onboarding)                            |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Suíte do core verde, incluindo testes novos (TDD) e os da 015 adaptados
- [ ] Smoke end-to-end: inativa→reativa+fecha; ausente→no-op exit 0; malformado→exit≠0; regen falho→não fecha; trabalho solto→marker e fechamento só após commit
- [ ] `init`/`upgrade` em sandbox plantam o hook de resume no `.claude/settings.json` (idempotente)
- [ ] `regression-watch.md` gerado
- [ ] Bump 1.2.53 nos três pontos; re-extração reversa (recomendada)

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-06-27 | Versão inicial gerada por `/reversa-plan` | reversa |
