# Legacy Impact — 022-hook-registro-decisoes

> Data: 2026-07-15 · Feature: `022-hook-registro-decisoes`
> Base da extração: `_reversa_sdd/` (reconciliação de 2026-07-05) + MD-0014 (commit `9c9d52f`, pré-condição desta feature)

## Arquivos afetados

| Arquivo afetado | Componente (`_reversa_sdd/architecture.md`) | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `.harness/harness-core/src/core/decisions/gate.py` (novo) | `core/decisions` (§code-analysis.md#4) | componente-novo | MEDIUM | Avaliação pura de pendência de registro (`GateVerdict`, `evaluate_registration_gate`, `compute_fingerprint`); o `service.py` existente permanece intocado. |
| `.harness/harness-core/src/core/session/close_flow.py` | `core/session` (§8) | regra-nova | HIGH | 3º portão do encerramento (`DECISAO_PENDENTE`), escape `--sem-decisao` com rastro na narrativa, anti-loop por fingerprint. Muda o comportamento default do `encerrar-sessao` em toda a base. |
| `.harness/harness-core/src/core/domain/models.py` | `core/domain` (§9) | delta-de-dados | MEDIUM | `SessionState` ganha `gate_lembrete_fingerprint`/`gate_encerramento_fingerprint` (opcionais); `close_session` os zera. |
| `.harness/harness-core/src/core/session/serializer.py` | `core/session` (§8) | delta-de-dados | MEDIUM | Round-trip dos campos novos; chaves emitidas só quando preenchidas (arquivo pré-022 byte-compatível). |
| `.harness/harness-core/src/core/domain/config.py` | `core/domain` (§9) | delta-de-dados | MEDIUM | `DecisionsSection.require_registration` (default `True`) + bump `CORE_VERSION` 2.0.1 → 2.1.0. |
| `.harness/harness-core/src/core/ports/git.py` + `src/adapters/git/subprocess.py` | `core/ports` / `adapters` (§10-11) | contrato-novo | MEDIUM | `GitPort.list_changed_paths_since` (`git diff --name-only <ref> HEAD`) — enxerga trabalho commitado na sessão. |
| `.harness/harness-core/src/main.py` | driver CLI (§11) | contrato-alterado | HIGH | `decisions --gate` (soft-block JSON no stdout, informativos em stderr, exit 0 sempre); `cmd encerrar-sessao --sem-decisao`; avaliador do gate injetado no `agy-hook`. Sem `--gate`, o subcomando permanece byte-idêntico (MD-0006 preservada). |
| `.harness/harness-core/src/core/install/harness_profiles.py` | `core/install` (§7) | regra-alterada | MEDIUM | `ClaudeProfile` emite `Stop → harness decisions --gate` (sobre o estado pós-MD-0014). |
| `.harness/harness-core/src/adapters/antigravity/hook_bridge.py` | `adapters/antigravity` (§12) | regra-alterada | LOW | `_handle_stop` ganha advisory opcional (`gate_evaluator`); stdout `{}` e o contrato RN-N26 intocados. |
| `.harness/harness-core/src/core/install/assets/skills/encerrar-sessao/` | `core/install` (§7, RN-N28) | contrato-alterado | MEDIUM | `SKILL.md` v1.3.0 documenta o marker `DECISAO_PENDENTE` e o escape; `scripts/encerrar_sessao.py` repassa `--sem-decisao`. |
| `.claude/settings.json`, `.reversa/settings.json.snippet`, `.claude/skills/encerrar-sessao/`, `harness-docs.html` | artefatos materializados (inventory.md) | regra-alterada | LOW | Regenerados a partir do perfil/código novos (lição "materializadores stale"). |

## Diff conceitual por componente

- **`core/decisions`:** ganha uma segunda responsabilidade IRMÃ (não acoplada) do grafo: decidir se falta registro. O serviço clássico (carga/validação/índice) não mudou; o gate é módulo novo, puro, consumido pelas três bordas.
- **`core/session`:** o encerramento passa de dois para **três portões** (pendência → narrativa → decisão), todos no protocolo abortar-e-reexecutar. O estado de sessão vira também o veículo do anti-loop (fingerprints no front-matter — a exceção consagrada do pré-check é reutilizada em vez de criar artefato novo).
- **Bordas:** cada harness recebe o veredito no seu grau — Claude bloqueia (uma vez) no `Stop` e duro no `encerrar-sessao`; Antigravity só avisa (RN-N26); Gemini fora do escopo desta iteração.

## Preservadas (regras 🟢 do `_reversa_sdd/domain.md` intactas)

- RN-N12 (índice derivado, não editado à mão), RN-N13/N14 (integridade e front-matter das fichas) — o gate não escreve fichas nem mexe no índice.
- RN-N31/N32 (commit de fechamento isolado, falha barulhenta) — o fechamento em si não mudou.
- RN-N34 (pendência restrita ao arquivo de estado) — reutilizada, não alterada; motivou o D-03.
- RN-N26 (Stop do Antigravity nunca bloqueia) — advisory respeita o contrato; stdout `{}` verificado por teste e smoke.
- RN-N5 (core agnóstico ao harness), RN-N17 (footprint per-projeto), RN-N2/N4 (round-trip, ausente ≠ malformado — estendidas, não violadas).
- RN-N41 (resume ancorado no índice) — intocada; esta feature aumenta a fidelidade do índice que a 021 injeta.
- MD-0006 (post-merge chama `decisions` sem args) — sem `--gate`, saída e exit codes byte-idênticos.
- MD-0014 (sem `PostToolUse` no perfil Claude) — preservada e fixada por teste.

## Modificadas

- **Sequência do `encerrar-sessao` (RN-N33/§2.15):** ganhou o 3º portão; a transição `ATIVA → INATIVA` agora exige também ficha nova/atualizada, escape declarado ou anti-loop consumido (`state-machines.md#1` precisa de nota na próxima re-extração).
- **Gancho `Stop` do Claude (architecture.md#4):** de `harness decisions` para `harness decisions --gate`, com semântica nova de stdout (JSON de hook) sob a flag.
- **`SessionState` (erd-complete.md):** dois campos opcionais novos no front-matter.
- **`DecisionsSection` (RN-N11 vizinha):** campo novo `require_registration` (default ligado).
- **`GitPort`:** método novo `list_changed_paths_since`.
- **Perfil/skill materializados:** `hooks_block()` do Claude e a skill `encerrar-sessao` (v1.3.0) mudaram de conteúdo — projetos-alvo convergem no próximo `upgrade`/`migrate`.
