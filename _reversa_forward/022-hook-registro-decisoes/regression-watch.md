# Regression Watch — 022-hook-registro-decisoes

> Feature: `022-hook-registro-decisoes` · Gerado em 2026-07-15
> Regras que precisam continuar verdadeiras nas próximas extrações reversas.

| ID | Origem (arquivo, seção) | Regra esperada após a mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|-------------------------------|---------------------|-------------------|
| W001 | `core/session/close_flow.py` (`SessionCloseFlow.run`) | O encerramento tem TRÊS portões na ordem: pendência de commit → narrativa viva → registro de decisão; o 3º emite `[HARNESS:DECISAO_PENDENTE ...]` e não fecha (exit 0) | presença | Fechamento com trabalho substantivo sem ficha e sem marker; ou marker com exit ≠ 0 |
| W002 | `core/decisions/gate.py` | `evaluate_registration_gate` é puro (só consulta git), sem filtro por tipo de arquivo; exclui apenas `state_file`/`index_file`/`header_file` e as fichas; fail-open com `aviso` em erro de git | redação | Filtro por extensão/diretório de código; exceção vazando; exclusões além das três + fichas |
| W003 | `core/session/close_flow.py` + `models.py` | Escape `--sem-decisao` anexa `"Declarado: sem decisão não óbvia nesta sessão (gate de registro)."` a "O que foi feito" e fecha; anti-loop: mesmo `gate_encerramento_fingerprint` → fecha com aviso, nunca re-bloqueia | presença | Escape sem rastro na narrativa; segundo bloqueio para o mesmo fingerprint |
| W004 | `core/session/serializer.py` + `models.py` | `gate_lembrete_fingerprint`/`gate_encerramento_fingerprint` opcionais com round-trip; ausentes → `None`; não emitidos quando vazios; zerados por `close_session` | presença | Estado pré-022 quebrando o parse; chaves emitidas em estado sem gate; fingerprints vazando entre sessões |
| W005 | `src/main.py` (ramo `decisions`) | Sob `--gate`: stdout é só o JSON `{"decision":"block",...}` (ou vazio), informativos em stderr, exit 0 SEMPRE, no máximo um bloqueio por fingerprint. SEM `--gate`: saída humana e exit codes byte-idênticos ao pré-022 (contrato do post-merge, MD-0006) | redação | Texto humano no stdout sob `--gate`; exit ≠ 0 sob `--gate`; mudança de comportamento sem a flag |
| W006 | `core/install/harness_profiles.py` (`ClaudeProfile.hooks_block`) | O `Stop` materializado invoca `harness decisions --gate`; sem `PostToolUse` (MD-0014); assinatura `harness decisions` do merge casa com e sem flag (substitui instalação pré-022 sem duplicar) | presença | Item `Stop` sem `--gate` reintroduzido; `PostToolUse` de volta; item duplicado após upgrade |
| W007 | `adapters/antigravity/hook_bridge.py` (`_handle_stop`) | Advisory: pendência vira `_log` em stderr; stdout permanece exatamente `{}`; falha do avaliador não descarta a reindexação nem o stdout (RN-N26) | presença | `{"decision": ...}` no stdout do stop; exceção do avaliador vazando |
| W008 | `core/ports/git.py` + `adapters/git/subprocess.py` | `list_changed_paths_since` = `git diff --name-only <ref> HEAD`; ref inválida → `RuntimeError` (nunca lista vazia silenciosa) | presença | Fallback silencioso para `[]` em falha real |
| W009 | `core/domain/config.py` | `DecisionsSection.require_registration` default `True`; flag `false` restaura integralmente o comportamento pré-022 | presença | Default virando opt-in sem microdecisão; flag desligada com gate ainda ativo |
| W010 | assets `skills/encerrar-sessao/` (v1.3.0) | `SKILL.md` documenta o marker `DECISAO_PENDENTE` + escape; `scripts/encerrar_sessao.py` repassa `--sem-decisao` ao `SessionCloseFlow` | presença | Skill rematerializada sem o passo 5; script sem o argumento |

## Observações (sem peso de regressão)

- O soft-block do `Stop` (D-04) apoia-se na semântica do protocolo de hooks do Claude Code (stdout exit 0 não reinjetado; `decision: block` alcança o modelo) — 🟡 conhecimento de plataforma; se o protocolo ganhar canal não-bloqueante ao modelo, revisitar D-04.
- O achado pré-existente "resume sem nenhum commit estoura traceback" (inventory.md) NÃO foi corrigido nem piorado: o gate trata âncora ilegível como fail-open, mas o traceback original do `resume` continua fora do escopo.
- Instalações no layout pré-020 só recebem o gate após `upgrade` — inércia esperada, não regressão.

## Histórico de re-extrações

### Re-extração 2026-07-15 19:22

> Primeira verificação da 022, na re-extração de reconciliação pós-022/023. Vereditos por leitura direta do código as-built (gate.py integral; diffs de close_flow/main/serializer/models/config/hook_bridge/claude_settings/harness_profiles; greps dirigidos na skill e nos testes) cruzada com os artefatos recém-gerados (`domain.md` §2.20, `state-machines.md`, `code-analysis.md` §4/§8/§11/§12, `data-dictionary.md` §1/§9). Suíte 300 verde relatada no fechamento da 023 (não recontada nesta rodada).

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | Três portões na ordem (pré-check → narrativa → registro) confirmados em `SessionCloseFlow.run`; 3º portão emite `conduct_decisao_pendente` (marker sem TTY) e `return 0`. Refletido em `state-machines.md` (nota dos gates) e `domain.md#2.20` (RN-N44). |
| W002 | 🟢 verde | `evaluate_registration_gate` puro: universo `changed ∪ dirty`, exclusões exatamente `{state_file, index_file, header_file}` + fichas por regex; sem filtro por tipo de arquivo (docstring explicita); fail-open com `aviso`. RN-N43. |
| W003 | 🟢 verde | Escape grava `"Declarado: sem decisão não óbvia nesta sessão (gate de registro)."` em `narrative.feito` e prossegue; fingerprint fino idêntico → aviso "não sanada" e encerra (nunca re-bloqueia). RN-N46/RN-N45. |
| W004 | 🟢 verde | Campos opcionais no `parse` (`meta.get`), `render` só quando preenchidos (byte-compat pré-022), `close_session` os zera. `data-dictionary.md` §1 e `erd-complete.md` atualizados. |
| W005 | 🟢 verde | Sob `--gate`: `info` → stderr, stdout reservado ao JSON, `sys.exit(0)` incondicional no fim do ramo; um bloqueio por fingerprint (grosso, 023). Sem a flag: fluxo original com exits 0/1 intactos (MD-0006). |
| W006 | 🟢 verde | `ClaudeProfile.hooks_block()` = `SessionStart` + `Stop → harness decisions --gate`, sem `PostToolUse`; `_HARNESS_COMMAND_SIGNATURES = ("harness cmd resume", "harness decisions")` casa com e sem flag (teste `test_absent_creates_single_item_per_harness_event` + caso de substituição sem duplicar). |
| W007 | 🟢 verde | `_handle_stop`: advisory via `self._log` (stderr), `return {}` intocado; `try/except` em volta do `gate_evaluator` preserva a reindexação. RN-N26. |
| W008 | 🟢 verde | `list_changed_paths_since` = `git diff --name-only <ref> HEAD` com `check=True`; `CalledProcessError` → `RuntimeError` barulhento (nunca `[]` silencioso). Port documentado em `c4-components.md`. |
| W009 | 🟢 verde | `DecisionsSection.require_registration: bool = True`; consultado nas três bordas (close_flow, ramo `--gate`, `gate_evaluator` devolve `None` se desligado). |
| W010 | 🟢 verde | `SKILL.md` v1.3.0 documenta o marker `DECISAO_PENDENTE` (passo 5) e o escape; `scripts/encerrar_sessao.py` declara `--sem-decisao` e repassa `sem_decisao=args.sem_decisao` ao `SessionCloseFlow.run`. |

## Arquivadas

_(vazio)_
