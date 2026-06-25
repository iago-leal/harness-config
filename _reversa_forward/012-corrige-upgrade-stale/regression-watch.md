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

### Re-extração 2026-06-25 13:39

| ID   | Veredito | Observação                                                                                                                                                                                  |
| ---- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | `upgrade_project` invoca `materialize` por subprocesso do python de destino; nenhuma materialização in-process no upgrade; `domain.md#2.13` (RN-N30)                                        |
| W002 | 🟢 verde | `_get_upstream_version` levanta `UpstreamVersionUndeterminedError` (sem fallback `current_version`); `upgrade` aborta exit ≠ 0 sem "Sucesso"; confirmado em smoke; `domain.md#2.9` (RN-N21) |
| W003 | 🟢 verde | `check_version_update` e `_get_upstream_version` usam `CORE_CONFIG_CANDIDATE_RELPATHS` (`layout.py`); caminho fixo único eliminado                                                          |
| W004 | 🟢 verde | `init` e `upgrade` materializam pela função única `apply_local_materializers` (`install/local_apply.py`); `domain.md#2.13` (RN-N30)                                                         |

## Arquivadas

> (vazia)
