# Regression Watch: Upgrade resiliente do harness-core

> Identificador: `012-corrige-upgrade-stale`
> Data: `2026-06-25`
> Gerado por `/reversa-coding`. Os itens abaixo precisam continuar verdadeiros nas próximas extrações reversas.

## Itens de regressão

| ID   | Origem (arquivo, seção)                                                        | Regra esperada após a mudança                                                                                                         | Tipo de verificação | Sinal de violação                                                                                                     |
| ---- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------- |
| W001 | `src/core/bootstrap/init_service.py` — `upgrade_project` (RN-N20)              | No `upgrade`, a materialização de artefatos de IDE roda via subprocesso do python de destino (`materialize`), nunca in-process        | presença            | Reaparecimento de `materialize_session_commands(`/`materialize_hooks_json(` chamados diretamente em `upgrade_project` |
| W002 | `src/core/bootstrap/init_service.py` — `_get_upstream_version` (RN-N20/RN-N04) | Versão do upstream indeterminada faz o `upgrade` abortar barulhento (exit ≠ 0), sem fallback para `current_version` nem "Sucesso"     | redação             | `_get_upstream_version` voltar a `return self.current_version`; `upgrade` imprimir "Sucesso" sem copiar               |
| W003 | `src/core/sync/service.py` + `src/core/domain/layout.py` (RN-N21)              | A leitura de versão (sync passivo e upgrade) usa `CORE_CONFIG_CANDIDATE_RELPATHS` (canônico + legado), resiliente a relayout          | presença            | Caminho fixo único do `config.py` reaparecer em `check_version_update` ou `_get_upstream_version`                     |
| W004 | `src/core/install/local_apply.py` (RN-N27/RN-N28)                              | `init` e `upgrade` materializam pela função única `apply_local_materializers` (session commands sempre; hooks.json só no Antigravity) | presença            | `init`/`upgrade` voltarem a duplicar a lógica dos materializadores em vez de delegar à função única                   |

## Observações (regras originalmente 🟡/🔄, sem peso de regressão)

- **RN-07 / `--force` (feature 012):** a flag `upgrade --force` força recópia + rematerialização ignorando a comparação de versão. Só socorre instalações que já rodam o código novo — não substitui o `init` como recuperação das presas no código antigo. Watch informativo, não regressivo.
- **Janela de stale 1.2.47 → 1.2.48:** o primeiro `upgrade` de um alvo ainda no 1.2.47 materializa com o código antigo (in-process), porque o fix só passa a valer quando o 1.2.48 está em execução. Como nenhum materializador mudou de conteúdo nesta feature, não há artefato stale a propagar; do 1.2.48 em diante o mecanismo é correto. Mitigação disponível: `./harness upgrade --force` (ou `./harness materialize`) após o primeiro upgrade.

## Histórico de re-extrações

### Re-extração 2026-08-11-b (varredura dirigida pós-feature 028)

> A 028 tocou `init_service.py` apenas com o passo aditivo `_ensure_decisions_guidance` no `init`; nada do circuito de upgrade/materialização mudou.

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | `upgrade_project` segue materializando via subprocesso; sem chamada in-process nova. |
| W002 | 🟢 verde | `_get_upstream_version` aborta barulhento, inalterado. |
| W003 | 🟢 verde | Leitura de versão via `CORE_CONFIG_CANDIDATE_RELPATHS`, inalterada (CORE_VERSION agora 2.6.0). |
| W004 | 🟢 verde | `apply_local_materializers` única para init/upgrade, inalterada — a guidance da 028 é passo do `init`, fora dos materializadores, por design (write-once, RN-N58). |

### Re-extração 2026-06-28 09:45

> Pós-feature 018. O mecanismo de upgrade resiliente (subprocesso do python de destino; aborto barulhento; caminhos-candidatos) está **intacto**. A 018 só troca o _conteúdo_ da função única `apply_local_materializers`: `materialize_session_commands` → `materialize_session_skills`. Verificação factual: suíte 212 passed, `test_local_apply.py` verde.

| ID   | Veredito | Observação                                                                                                                                                                                                                                                                                  |
| ---- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | `upgrade_project` segue materializando via subprocesso (`materialize`), nunca in-process — `materialize_session_commands(`/`materialize_hooks_json(` diretos ausentes de `upgrade_project`. O materializador de sessão agora é `materialize_session_skills`, igualmente fora do in-process. |
| W002 | 🟢 verde | `_get_upstream_version` aborta barulhento (sem fallback `current_version`): inalterado.                                                                                                                                                                                                     |
| W003 | 🟢 verde | Leitura de versão usa `CORE_CONFIG_CANDIDATE_RELPATHS` (`layout.py`): inalterado.                                                                                                                                                                                                           |
| W004 | 🟢 verde | `init`/`upgrade` materializam pela função única `apply_local_materializers` (`install/local_apply.py`): preservada; agora invoca `materialize_session_skills` sempre (✨f018) + `materialize_hooks_json`/`materialize_claude_settings` por harness. `domain.md#2.13` (RN-N30) reconciliado. |

### Re-extração 2026-06-28 00:40

> Pós-feature 017 (reconciliação focada + regressão). A 017 estende `session_commands.py` (chamado por `apply_local_materializers`), sem tocar o mecanismo de upgrade. Verificação: suíte 210 passed, `test_local_apply.py` verde.

| ID   | Veredito | Observação                                                                                                                                                       |
| ---- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | `upgrade_project` segue materializando via subprocesso (`materialize`), nunca in-process; inalterado pela 017.                                                   |
| W004 | 🟢 verde | `init`/`upgrade` seguem pela função única `apply_local_materializers`; a 017 só estendeu `materialize_session_commands` (limpeza do órfão), sem duplicar lógica. |

### Re-extração 2026-06-25 14:32

> Re-confirmação na rodada completa 001–012 (a rodada cirúrgica de 13:39 já cobrira esta feature). Vereditos por leitura direta do código + suíte.

| ID   | Veredito | Observação                                                                                                                                 |
| ---- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| W001 | 🟢 verde | `grep` por `materialize_session_commands(`/`materialize_hooks_json(` diretos em `upgrade_project` = vazio; materialização via subprocesso. |
| W002 | 🟢 verde | `_get_upstream_version` aborta barulhento (sem fallback `current_version`); `template.md:42` documenta o exit ≠ 0; coberto pela suíte.     |
| W003 | 🟢 verde | `check_version_update` e `_get_upstream_version` usam `CORE_CONFIG_CANDIDATE_RELPATHS` (`layout.py`); caminho fixo único eliminado.        |
| W004 | 🟢 verde | `init`/`upgrade` materializam pela função única `apply_local_materializers` (`install/local_apply.py:19`); `domain.md#2.13` (RN-N30).      |

### Re-extração 2026-06-25 13:39

| ID   | Veredito | Observação                                                                                                                                                                                  |
| ---- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | `upgrade_project` invoca `materialize` por subprocesso do python de destino; nenhuma materialização in-process no upgrade; `domain.md#2.13` (RN-N30)                                        |
| W002 | 🟢 verde | `_get_upstream_version` levanta `UpstreamVersionUndeterminedError` (sem fallback `current_version`); `upgrade` aborta exit ≠ 0 sem "Sucesso"; confirmado em smoke; `domain.md#2.9` (RN-N21) |
| W003 | 🟢 verde | `check_version_update` e `_get_upstream_version` usam `CORE_CONFIG_CANDIDATE_RELPATHS` (`layout.py`); caminho fixo único eliminado                                                          |
| W004 | 🟢 verde | `init` e `upgrade` materializam pela função única `apply_local_materializers` (`install/local_apply.py`); `domain.md#2.13` (RN-N30)                                                         |

## Arquivadas

> (vazia)
