# Legacy Impact: Ofertas de fim de sessão — push e upgrade

> Identificador: `014-oferta-upgrade-ao-encerrar`
> Data: `2026-06-26`
> Base de comparação: `_reversa_sdd/` (architecture.md, domain.md)

A mudança é **majoritariamente aditiva**: estende contratos e a borda, sem alterar nem
remover nenhuma regra 🟢 confirmada do legado. O fechamento da sessão (013) permanece
intocado.

## 1. Arquivos afetados

| Arquivo afetado                                                               | Componente (`_reversa_sdd/`)                                  | Tipo                      | Severidade | Justificativa                                                                                                                |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `.harness/harness-core/src/core/ports/git.py`                                 | Porta de Git (`domain.md#RN-N5`, `sync-check/contracts.md#3`) | delta-de-contrato-externo | MEDIUM     | Oito métodos novos (fetch, push, ahead, branch, ler ref, ff-only, working-tree). Aditivo; os 4 métodos existentes não mudam. |
| `.harness/harness-core/src/adapters/git/subprocess.py`                        | Adapter de Git                                                | regra-nova                | LOW        | Implementa os métodos novos no molde `CalledProcessError → RuntimeError`.                                                    |
| `.harness/harness-core/src/core/session/offers.py`                            | (novo) Serviço de ofertas de fim de sessão                    | componente-novo           | MEDIUM     | Detecção testável de push/upgrade; consome `GitPort`+`SyncService`.                                                          |
| `.harness/harness-core/src/core/sync/service.py`                              | Sincronização (`domain.md#2.1/2.9`, RN-N21)                   | regra-nova                | LOW        | `check_version_update_remote` adicionado ao lado do `check_version_update` local; este permanece igual.                      |
| `.harness/harness-core/src/main.py`                                           | Borda CLI (`domain.md#2.9`, RN-N21)                           | regra-nova                | MEDIUM     | Nova etapa pós-`encerrar-sessao`: detecção + ofertas (TTY/estruturado) + push/upgrade, sob `try/except` não-bloqueante.      |
| `.harness/harness-core/src/core/install/harness_profiles.py`                  | Materialização de comandos (`domain.md#2.12`, RN-N29)         | regra-alterada            | LOW        | Texto dos slash commands menciona as ofertas; estrutura/caminhos inalterados.                                                |
| `.harness/harness-core/src/core/domain/config.py`                             | Configuração (`domain.md#2.9`, RN-N18)                        | delta-de-dados            | LOW        | Bump `version` 1.2.49 → 1.2.50.                                                                                              |
| `.harness/harness-core/src/core/bootstrap/init_service.py`                    | Bootstrap/upgrade (`domain.md#2.9`, RN-N20)                   | delta-de-dados            | LOW        | Bump `current_version` 1.2.49 → 1.2.50. `upgrade_project` **não** foi alterado.                                              |
| `.claude/commands/encerrar-sessao.md`, `.agents/workflows/encerrar-sessao.md` | Artefatos de IDE materializados                               | regra-alterada            | LOW        | Rematerializados com o texto novo (derivados do código, não fonte).                                                          |

## 2. Diff conceitual por componente

- **Porta/Adapter de Git.** Ganham verbos de rede e de inspeção de estado que faltavam
  (`fetch`, `push` sem `--force`, `count_commits_ahead`, `get_current_branch`,
  `get_default_branch`, `get_file_at_ref`, `is_working_tree_clean`, `merge_ff_only`). As
  consultas sinalizam ausência por valor (`0`/`None`/`False`) em estado normal e só levantam
  em falha real, para a borda degradar sem tratar exceção.
- **Serviço de ofertas (novo).** Concentra a decisão "o que oferecer" no domínio, testável e
  agnóstico a terminal: push quando o branch está à frente do tracking; upgrade quando o
  upstream remoto publica versão nova. Falhas degradam para "sem oferta".
- **Sincronização.** O alerta passivo local (RN-N21) permanece; ao lado dele, a comparação
  **remota** (fetch + leitura da ref publicada) alimenta a oferta de upgrade no encerramento.
- **Borda CLI.** Após um `encerrar-sessao` bem-sucedido, conduz as ofertas (push → upgrade)
  em dupla camada (TTY `[s/N]` / marcadores estruturados), reusando `upgrade_project` e
  sincronizando o upstream por fast-forward antes da cópia. Tudo não-bloqueante.

## 3. Preservadas (regras 🟢 intactas)

- **RN-N31 / RN-N32 (`domain.md#2.14`):** o `encerrar-sessao` versiona o estado num commit
  isolado e falha barulhento — o `CommandService` **não foi tocado**; as ofertas são etapa
  posterior na borda.
- **RN-N21 (`domain.md#2.9`):** o alerta passivo de versão (local, em todos os comandos)
  permanece exatamente como era; a verificação remota é adicional e exclusiva do encerramento.
- **RN-N20 (`domain.md#2.9`):** `upgrade_project` permanece inalterado; a sincronização
  ff-only do upstream vive na borda, não dentro do comando `upgrade` standalone.
- **RN-N5 (`domain.md#2.3`):** o domínio continua falando com git só pela porta; nenhum
  `subprocess`/`git` direto no serviço de ofertas.
- **RN-N17 (`domain.md#2.8`):** footprint global zero — nenhuma escrita fora do projeto.
- **RN-07 (`domain.md#2.3`):** a âncora de integridade do estado segue como na 013.

## 4. Modificadas (regras 🟢 alteradas ou removidas)

- Nenhuma regra 🟢 confirmada foi **alterada** ou **removida**. A RN-N21 é **estendida** de
  forma aditiva (ganha uma verificação remota e acionável no encerramento), sem mudar o
  comportamento passivo existente. Por isso não há item de regressão sobre regra pré-existente
  modificada; os watch items abaixo cobrem os **novos invariantes** que devem persistir.
