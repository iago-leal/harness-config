# Regression Watch: Ofertas de fim de sessão — push e upgrade

> Identificador: `014-oferta-upgrade-ao-encerrar`
> Data: `2026-06-26`

Itens que devem permanecer verdadeiros nas próximas extrações reversas. A feature é aditiva:
os watch items cobrem os **novos invariantes** e a **preservação** do fechamento da 013.

## Watch items

| ID   | Origem (arquivo, seção)                    | Regra esperada após a mudança                                                                                                                                      | Tipo de verificação | Sinal de violação                                                                                                       |
| ---- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| W001 | `src/core/commands/service.py` (RN-N31)    | O `CommandService.execute_command('encerrar-sessao')` continua só fechando + commitando o estado; **não** faz push/upgrade nem I/O interativo.                     | presença            | Código de push/upgrade/`input` dentro do `CommandService`.                                                              |
| W002 | `src/main.py` (RN-01)                      | As ofertas (push/upgrade) rodam **apenas** após `encerrar-sessao` com sucesso, como etapa posterior; os demais comandos mantêm só o alerta passivo.                | presença            | Ofertas disparadas noutro comando ou antes do fechamento.                                                               |
| W003 | `src/main.py` (RN-02)                      | A etapa de ofertas é não-bloqueante: falha de detecção/rede/push/upgrade vira aviso e nunca regride o encerramento já versionado.                                  | redação             | Exceção da oferta propagando e abortando o comando; encerramento marcado como falho pela oferta.                        |
| W004 | `src/core/session/offers.py` (RN-04/RN-11) | A oferta de push só existe com upstream tracking e commits à frente (`count_commits_ahead > 0`).                                                                   | presença            | Oferta de push sem tracking ou com branch em dia.                                                                       |
| W005 | `src/adapters/git/subprocess.py` (RN-06)   | O `push` nunca usa `--force`.                                                                                                                                      | ausência            | Presença de `--force`/`-f` no comando de push.                                                                          |
| W006 | `src/core/sync/service.py` (RN-07)         | `check_version_update_remote` consulta a rede (fetch) e degrada para `None` em qualquer falha, sem levantar.                                                       | redação             | Exceção propagada da verificação remota; ausência do fetch.                                                             |
| W007 | `src/main.py` (RN-09)                      | Aceitar o upgrade sincroniza o upstream por `merge_ff_only` antes de copiar; não-FF aborta sem sobrescrever e o `upgrade_project` standalone permanece inalterado. | presença            | Upgrade aplicado sem sincronizar; sincronização embutida no `upgrade_project`; sobrescrita de working tree do upstream. |
| W008 | `src/core/session/offers.py` (RN-N5)       | A detecção fala com git só pela porta `GitPort`; sem `subprocess`/`git` direto no serviço.                                                                         | ausência            | `import subprocess` ou chamada a `git` no serviço de ofertas.                                                           |
| W009 | `src/main.py` (RN-10)                      | Quando ambas se aplicam, a ordem é push → upgrade.                                                                                                                 | redação             | Upgrade conduzido antes do push.                                                                                        |

## Observações (originalmente 🟡 / 🔴, sem peso de regressão)

- A detecção do branch principal (`get_default_branch`) é heurística (`symbolic-ref` + fallback
  `{main,master}`); afeta apenas o aviso reforçado, não a existência do push (D-07, 🟡).
- O disparo das ofertas depende de detectar o "sucesso" do encerramento por inspeção da
  mensagem (D-10, 🟡); um refactor futuro para resultado tipado removeria a fragilidade.
- O comportamento exato dos marcadores no workflow do Antigravity não é verificável localmente
  (alinha ao amarelo herdado de 009/010).

## Histórico de re-extrações

### Re-extração 2026-08-11 11:26

> Re-verificação dirigida pós-features 024-027 (escopo por diff: `main.py` e o entorno do `CommandService` foram tocados pela 024/025). Itens não listados (W004-W008) têm origem intocada e mantêm o veredito anterior. Suíte 372 verde.

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | `CommandService` segue sem push/upgrade/`input` (grep vazio); o consentimento da 024 é resolvido na borda e chega ao serviço como o bool `versionar_estado` (D-04) — a fronteira domínio × borda ficou ainda mais nítida. |
| W002 | 🟢 verde | Ofertas só após `encerrar-sessao` com sucesso; o marker `ENCERRAMENTO_NAO_VERSIONADO` da 024 é emitido **antes** da oferta de push, preservando a ordem da cadeia. |
| W009 | 🟢 verde | Ordem push → upgrade inalterada. |


### Re-extração 2026-07-15 19:22

> Re-verificação dirigida pós-feature 022: o delta inseriu o 3º portão em `SessionCloseFlow.run` ANTES do fechamento — quando o portão aborta, o fechamento não ocorre e as ofertas não rodam, o que preserva (e reforça) W002. `offers.py`/`sync` intocados.

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | `CommandService.execute_command('encerrar-sessao')` inalterado. |
| W002 | 🟢 verde | Ofertas só após sucesso: o 3º portão aborta antes do fechamento (return 0 sem ofertas); ordem pré-check → narrativa → registro → fechamento → ofertas. |
| W003 | 🟢 verde | Não-bloqueio das ofertas inalterado. |
| W004 | 🟢 verde | `offers.py` intocado. |
| W005 | 🟢 verde | `push` sem `--force`: adapter inalterado nesse ponto (delta só adicionou `list_changed_paths_since`). |
| W006 | 🟢 verde | `check_version_update_remote` inalterado. |
| W007 | 🟢 verde | `merge_ff_only` e o fluxo de upgrade inalterados. |
| W008 | 🟢 verde | Detecção só pela porta `GitPort` (RN-N5); nenhum subprocess novo no serviço de ofertas. |
| W009 | 🟢 verde | Ordem push → upgrade preservada. |

### Re-extração 2026-06-28 09:45

> Primeira verificação dos watch da 014. A feature 018 **moveu** a condução das ofertas (e os helpers `render_offer_markers`/`conduct_end_session_offers`/`run_upgrade`) de `main.py` para `SessionCloseFlow` (`close_flow.py`), reexportados por `src.main` — comportamento **preservado**, testes da 014 verdes na suíte 212. `offers.py`/`sync` intactos. Verificação factual: suíte 212 passed.

| ID   | Veredito | Observação                                                                                                                                                                                            |
| ---- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | `CommandService.execute_command('encerrar-sessao')` segue só fechando+commitando, sem push/upgrade nem I/O — `CommandService` inalterado.                                                             |
| W002 | 🟢 verde | Ofertas só após sucesso, etapa posterior: `close_flow.run` chama `_conduct_offers` apenas quando `result_msg.startswith("Sessão encerrada com sucesso")`.                                             |
| W003 | 🟢 verde | Etapa não-bloqueante: `_conduct_offers` roda sob `try/except` que vira aviso sem regredir o encerramento já versionado.                                                                               |
| W004 | 🟢 verde | Oferta de push só com upstream tracking e commits à frente: `offers.py` inalterado.                                                                                                                   |
| W005 | 🟢 verde | `push` nunca usa `--force`: `subprocess.py` inalterado.                                                                                                                                               |
| W006 | 🟢 verde | `check_version_update_remote` consulta a rede e degrada para `None` sem levantar: `sync/service.py` inalterado.                                                                                       |
| W007 | 🟢 verde | Aceitar upgrade sincroniza por `merge_ff_only` antes de copiar; não-FF aborta sem sobrescrever: lógica migrada para `_conduct_offers.run_upgrade`, idêntica; `upgrade_project` standalone inalterado. |
| W008 | 🟢 verde | Detecção fala com git só pela porta `GitPort`: `offers.py` inalterado (RN-N5).                                                                                                                        |
| W009 | 🟢 verde | Ordem push → upgrade quando ambas se aplicam: preservada em `conduct_end_session_offers` (push antes de upgrade).                                                                                     |

## Arquivadas

<!-- Vazio. -->
