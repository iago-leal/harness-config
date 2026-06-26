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

<!-- Preenchido pelo agente reverso quando `/reversa` rodar de novo. -->

## Arquivadas

<!-- Vazio. -->
