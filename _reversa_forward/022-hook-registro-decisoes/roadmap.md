# Roadmap: Registro obrigatório de microdecisões via gancho de sessão

> Identificador: `022-hook-registro-decisoes`
> Data: `2026-07-15`
> Requirements: `_reversa_forward/022-hook-registro-decisoes/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

O gate de registro entra como **terceiro portão** do `SessionCloseFlow` (`_reversa_sdd/code-analysis.md#8`), reutilizando o protocolo abortar-e-reexecutar já provado pelos markers `COMMIT_PENDENTE` (016/019) e `NARRATIVA_PENDENTE` (018): pendência de ficha → marker `DECISAO_PENDENTE`, o agente registra ou declara o escape (`--sem-decisao`) e re-roda. A avaliação vive num serviço puro novo (`core/decisions/gate.py`): trabalho substantivo = (diff `âncora..HEAD` ∪ working tree sujo) − artefatos de estado do próprio harness; satisfeito por qualquer `MD-*.md` novo/modificado sob `decisions.dir`. O anti-loop e o rastro persistem em campos opcionais do front-matter do estado de sessão (nunca em arquivo novo, que viraria `COMMIT_PENDENTE`). No fim de turno do Claude, o comando do gancho `Stop` passa a `harness decisions --gate`, emitindo um **soft-block único por estado de pendência** (JSON `{"decision":"block","reason":...}`) — o único canal do `Stop` que alcança o modelo. No Antigravity, o mesmo veredito vira aviso em `stderr` dentro do `_handle_stop`, com stdout `{}` intocado (RN-N26). Flag `decisions.require_registration` (default `True`) liga tudo; a propagação usa o perfil + merge por-item existentes.

## 2. Princípios aplicados

`.reversa/principles.md` não existe neste projeto — não há princípios formais do Reversa a verificar. Os princípios globais do mantenedor (CLAUDE.md) foram usados como filtro:

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Erros barulhentos > silêncio | Pendência vira marker/aviso explícito; falha interna do gate avisa em `stderr` e nunca degrada em silêncio | respeita |
| Software retomável após pausa | A própria razão da feature: grafo de decisões completo para o "eu de daqui a 12 meses" | respeita |
| Estabilidade > novidade | Nenhuma dependência nova; reusa portas, markers e materializadores existentes | respeita |
| RN-N5 (core agnóstico ao harness, `_reversa_sdd/domain.md#2.3`) | Serviço puro decide o veredito; **como** interceptar vive na borda por harness | respeita |
| RN-N17 (footprint per-projeto, `_reversa_sdd/domain.md#2.8`) | Toda escrita nova ocorre no estado de sessão sob `.harness/` do projeto | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Gate como 3º portão do `SessionCloseFlow`, após `NARRATIVA_PENDENTE`, com marker `[HARNESS:DECISAO_PENDENTE ...]` e protocolo abortar-e-reexecutar | Reusa o mecanismo provado das features 016/018/019; a skill `encerrar-sessao` já sabe mediar markers; ordem após o pré-check garante que o trabalho já foi commitado e o diff da âncora o enxerga | Gate dentro do `CommandService` (mistura domínio de transição com orquestração de borda); hook git independente (não alcança o agente) | 🟢 |
| D-02 | Sinal físico = `git diff --name-only <âncora>..HEAD` ∪ `list_dirty_paths`, excluindo `session.state_file`, `decisions.index_file`, `decisions.header_file`; satisfeito por qualquer `MD-*.md` sob `decisions.dir` no mesmo conjunto. Novo método `GitPort.list_changed_paths_since` | O pré-check de pendência (RN-N34) força commit antes do fechamento, então só o diff da âncora enxerga o trabalho da sessão; dirty paths cobrem o caminho do `Stop` (turno em andamento). Sem filtro por tipo de arquivo (esclarecimento de 2026-07-15) | Só `list_dirty_paths` (cego a trabalho já commitado na sessão); parsear o transcript do agente (acoplamento a formato de terceiro) | 🟢 |
| D-03 | Anti-loop e rastro por **fingerprint** (hash de âncora + HEAD + caminhos sujos ordenados) persistido em campos opcionais do front-matter do estado de sessão | O estado de sessão já é excluído do pré-check de pendência — um arquivo novo sob `.harness/` viraria `COMMIT_PENDENTE` eterno ou exigiria nova entrada de `.gitignore` em toda a base instalada. Campos opcionais preservam o round-trip do serializer (RN-N2) e a retrocompatibilidade | Scratch `.harness/decision-gate.json` (vira pendência ou exige gitignore novo); estado em memória (não sobrevive entre invocações do processo) | 🟢 |
| D-04 | Lembrete no `Stop` do Claude = **soft-block único por fingerprint**: `harness decisions --gate` emite `{"decision":"block","reason":"[HARNESS:DECISAO_PENDENTE ...]"}` na primeira detecção; fingerprint igual na chamada seguinte → sem bloqueio | Restrição física do protocolo de ganchos: no `Stop`, stdout com exit 0 **não** é reinjetado ao modelo — o único canal que o alcança é o bloqueio com `reason`. O fingerprint torna o bloqueio um lembrete de custo limitado (uma rodada extra no máximo). RF-08 reconciliado no requirements | `systemMessage` (só chega ao usuário, não ao modelo); stdout puro exit 0 (invisível ao agente); adiar o lembrete para o próximo `resume` (perde o "no turno" escolhido no esclarecimento) | 🟡 |
| D-05 | Escape via flag explícita no encerramento (`encerrar-sessao --sem-decisao`); o core anexa linha padrão à seção "O que foi feito" da narrativa antes de fechar | Declaração deliberada e auditável no estado da sessão (escolha 5a de 2026-07-15); anexar registro de uma declaração explícita não viola "o core nunca inventa a narrativa" (RN-N3) | Frase-sentinela escrita pelo agente na narrativa e detectada por scan (frágil, acoplada a texto livre); campo só no front-matter (invisível na leitura humana da narrativa) | 🟢 |
| D-06 | Antigravity advisory: `_handle_stop` do `AntigravityHookBridge` ganha avaliação do gate (git + config injetados na borda `agy-hook`) e loga pendência via `_log` em `stderr`; stdout permanece `{}` | Contrato RN-N26 proíbe bloquear/reentrar no laço; o aviso preserva a observabilidade sem violá-lo. A injeção na borda mantém o adaptador testável com dublês | Emitir `{"decision":"continue"}` para forçar registro (violaria RN-N26 e o desenho da 009) | 🟢 |
| D-07 | Flag `decisions.require_registration: bool = True` em `DecisionsSection`; o serviço puro recebe `enabled` calculado na borda | Default ligado em toda instalação (escolha 3a); mesmo padrão do `inject_decisions_index` da 021 (retrocompatível: tomls sem o campo herdam `True`) | Opt-in (contraria a escolha do mantenedor); flag por harness (complexidade sem demanda) | 🟢 |
| D-08 | `ClaudeProfile.hooks_block()` passa a emitir `Stop → ${CLAUDE_PROJECT_DIR}/harness decisions --gate`; o merge por-item reconhece o item pela assinatura `harness decisions` e o substitui | Mudança na FONTE (lição da MD-0014): `init`/`upgrade`/`migrate` propagam sem reintroduzir o item antigo; a assinatura por substring cobre a forma com e sem flag | Segundo item de hook separado só para o gate (dois processos por `Stop`, ruído); mudar só os settings materializados à mão (regride no próximo upgrade) | 🟢 |
| D-09 | Sob `--gate`, toda saída informativa do subcomando `decisions` migra para `stderr`; `stdout` fica reservado ao JSON do hook (ou vazio) | O protocolo de hooks do Claude parseia o stdout; texto humano misturado quebraria o JSON. Sem `--gate` (uso manual, git post-merge da MD-0006), nada muda | Emitir JSON sempre (quebraria o post-merge e o uso manual) | 🟢 |

## 4. Premissas

Nenhuma — o `requirements.md` está sem marcadores `[DÚVIDA]` (sessão de esclarecimentos de 2026-07-15).

| Premissa | Origem | Risco se errada |
|----------|--------|-----------------|
| n/a | — | — |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `core/decisions` | `_reversa_sdd/code-analysis.md#4` | componente-novo | `gate.py`: veredito puro de pendência de registro + fingerprint (nenhuma mudança no `service.py` existente) |
| `core/session` (`close_flow.py`) | `_reversa_sdd/code-analysis.md#8` | regra-alterada | 3º portão (decisão pendente) entre o gate de narrativa e o fechamento; escape `--sem-decisao`; anti-loop por fingerprint |
| `core/domain` (`models.py`, `config.py`) | `_reversa_sdd/code-analysis.md#9` | contrato-alterado | `SessionState` ganha 2 campos opcionais de fingerprint; `DecisionsSection` ganha `require_registration` (default `True`) |
| `core/session/serializer.py` | `_reversa_sdd/code-analysis.md#8` | regra-alterada | Round-trip dos novos campos opcionais do front-matter (ausente → `None`, RN-N2/RN-N4 preservadas) |
| `core/ports/git.py` + `adapters/git/subprocess.py` | `_reversa_sdd/code-analysis.md#10-11` | contrato-novo | `list_changed_paths_since(repo_path, ref)` (`git diff --name-only <ref> HEAD`) |
| `src/main.py` (CLI) | `_reversa_sdd/code-analysis.md#11` | contrato-alterado | Flag `--gate` no subcomando `decisions` (JSON de soft-block no stdout); passthrough `--sem-decisao` no `cmd encerrar-sessao` |
| `core/install/harness_profiles.py` | `_reversa_sdd/code-analysis.md#7` | regra-alterada | `ClaudeProfile` emite `Stop → harness decisions --gate` (sobre o estado pós-MD-0014, sem `PostToolUse`) |
| `core/install/claude_settings.py` | `_reversa_sdd/domain.md#2.17` (RN-N39) | regra-alterada | Assinatura do merge por-item confirmada/ajustada para casar `harness decisions` com e sem flag |
| `adapters/antigravity/hook_bridge.py` | `_reversa_sdd/code-analysis.md#12` | regra-alterada | `_handle_stop` avalia o gate (advisory) e loga pendência em `stderr`; stdout `{}` intocado |
| Assets da skill `encerrar-sessao` | `_reversa_sdd/domain.md#2.12` (RN-N28) | contrato-alterado | `SKILL.md` + scripts documentam/mediam o marker `DECISAO_PENDENTE` e o escape |
| `.claude/settings.json` + `.reversa/settings.json.snippet` (este repo) | `_reversa_sdd/inventory.md#configuração-de-ganchos-por-harness` | regra-alterada | Regenerados a partir do perfil novo (lição da memória "upgrade regrava materializadores stale") |

## 6. Delta no modelo de dados

- Resumo: dois campos opcionais no front-matter do estado de sessão (fingerprints de lembrete e de encerramento) e uma flag booleana em `[decisions]` no `harness.toml`. Sem banco, sem migração de arquivo: campos ausentes herdam defaults (retrocompatível nos dois sentidos).
- Detalhe completo em: `_reversa_forward/022-hook-registro-decisoes/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Marker `DECISAO_PENDENTE` (agente ↔ close flow) | arquivo/stdout | `_reversa_forward/022-hook-registro-decisoes/interfaces/decisao-pendente-marker.md` |
| Soft-block do `Stop` do Claude (`decisions --gate`) | stdout JSON de hook | `_reversa_forward/022-hook-registro-decisoes/interfaces/stop-gate-lembrete.md` |

## 8. Plano de migração

1. Base instalada (fonte única, pós-020): o core novo vale imediatamente via shim; o item `Stop` dos settings de cada projeto é atualizado no próximo `upgrade`/`migrate` (merge por-item). Até lá, `harness decisions` sem `--gate` segue funcionando como hoje (gate inativo no turno, ativo no `encerrar-sessao` — que roda pelo core novo).
2. Instalações pré-020 (cópia local): ganham o gate só após `upgrade` (comportamento padrão de qualquer feature).
3. Este repo: regenerar `.claude/settings.json` e `.reversa/settings.json.snippet` a partir do perfil novo, junto com o trabalho em curso da MD-0014 (working tree compartilhado — coordenar o commit).
4. Sem migração de dados: campos novos são opcionais com default.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Falso positivo incomoda (mudança trivial exige ficha) | médio | médio | Escape `--sem-decisao` auditável + anti-loop (2ª tentativa passa com aviso) + flag de opt-out por projeto |
| Loop de bloqueio no `Stop` do Claude | alto | baixo | Fingerprint persistido: mesmo estado nunca bloqueia duas vezes (D-04) |
| JSON do hook poluído por texto informativo no stdout | alto | médio | D-09: sob `--gate`, informativos vão para `stderr`; teste de contrato do stdout |
| Trabalho da MD-0014 em curso no working tree (mesmos arquivos: `harness_profiles.py`, `claude_settings.py`) | médio | alto | Commitar/fechar a MD-0014 antes de codar a 022; o plano já assume o perfil pós-MD-0014 (sem `PostToolUse`) |
| Mock de git mascara comportamento do porcelain (lição da 019) | médio | médio | Smoke com git real para `list_changed_paths_since` e para o fluxo do gate (memória `smoke-git-real-vs-mock-porcelain`) |
| `cmd resume` sem nenhum commit já estoura traceback (achado pré-existente, `_reversa_sdd/inventory.md#achados-de-saúde`) — o gate adiciona mais um consumidor de âncora | baixo | baixo | Gate trata âncora ausente/inválida como "sem baseline" → permissivo com aviso (RN-05); não corrige o achado pré-existente (fora de escopo) |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Suíte do core verde (incl. round-trip do serializer com e sem campos novos)
- [ ] Smoke real: `encerrar-sessao` bloqueia sem ficha, passa com ficha, escape registra na narrativa, 2ª tentativa passa com aviso
- [ ] Contrato do `Stop`: stdout de `decisions --gate` é JSON válido ou vazio; sem `--gate`, comportamento atual intocado
- [ ] `.claude/settings.json` e snippet deste repo regenerados do perfil novo
- [ ] `regression-watch.md` gerado

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-07-15 | Versão inicial gerada por `/reversa-plan` | reversa |
