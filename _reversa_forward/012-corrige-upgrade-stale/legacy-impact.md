# Legacy Impact: Upgrade resiliente do harness-core

> Identificador: `012-corrige-upgrade-stale`
> Data: `2026-06-25`
> Base: extração reversa em `_reversa_sdd/`

## 1. Arquivos afetados

| Arquivo afetado                                                                   | Componente (`_reversa_sdd/`)                                              | Tipo              | Severidade | Justificativa                                                                                                                                         |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ----------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/bootstrap/init_service.py`                                              | Bootstrap e Evolução do Tooling — `_reversa_sdd/domain.md#2.9` (RN-N20)   | regra-alterada    | HIGH       | `upgrade_project` passa a rematerializar via subprocesso e a abortar em versão indeterminada; `_get_upstream_version` varre candidatos e levanta erro |
| `src/core/install/local_apply.py` (novo)                                          | Materializadores de IDE — `_reversa_sdd/domain.md#2.11-2.12`              | componente-novo   | MEDIUM     | Função única `apply_local_materializers` compartilhada por `init` (in-process) e `upgrade` (subprocesso)                                              |
| `src/main.py`                                                                     | CLI / Apresentação — `_reversa_sdd/architecture.md#2`                     | contrato-alterado | MEDIUM     | Novo subcomando interno `materialize`; flag `--force` no `upgrade`                                                                                    |
| `src/core/sync/service.py`                                                        | Checagem Passiva de Atualização — `_reversa_sdd/domain.md#2.9` (RN-N21)   | regra-alterada    | LOW        | `check_version_update` lê a versão por caminhos-candidato (resiliente a relayout), mantendo a não-bloqueância                                         |
| `src/core/domain/layout.py`                                                       | Fonte única de caminhos do core (feature 011)                             | componente-novo   | LOW        | Constante `CORE_CONFIG_CANDIDATE_RELPATHS` (canônico + legado)                                                                                        |
| `src/core/domain/config.py`                                                       | Configuração de Upstream e Versão — `_reversa_sdd/domain.md#2.9` (RN-N18) | delta-de-config   | LOW        | Bump `version` 1.2.47 → 1.2.48 (necessário para a propagação por `upgrade`)                                                                           |
| `src/core/install/template.md`                                                    | Instalação por Prompt — `_reversa_sdd/domain.md#2.4`                      | regra-nova        | LOW        | Documenta `--force` e a recuperação do layout antigo                                                                                                  |
| `tests/test_init.py`, `test_sync.py`, `test_cli.py`, `test_local_apply.py` (novo) | Suíte de testes                                                           | regra-nova        | LOW        | Cobertura dos dois modos de falha, `--force` e detecção resiliente                                                                                    |

## 2. Diff conceitual por componente

- **`InitializationService.upgrade_project`** — antes, a materialização dos artefatos de IDE rodava in-process (módulos antigos em memória), e a versão indeterminada do upstream caía no fallback `current_version`, igualando versões e gerando um upgrade fantasma. Agora, a materialização é delegada a um subcomando interno rodado por subprocesso do python de destino (código recém-copiado), e a versão indeterminada propaga um erro barulhento. Acrescenta-se o parâmetro `force`, que ignora a comparação de versão e tolera versão indeterminada (vira aviso), sempre recopiando e rematerializando.
- **`InitializationService._get_upstream_version`** — passou de um caminho fixo do `config.py` para uma varredura de caminhos-candidato (canônico + legado da raiz), levantando `UpstreamVersionUndeterminedError` quando nenhum resolve, em vez de devolver `current_version` silenciosamente.
- **`apply_local_materializers` (novo)** — encapsula a regra "session commands sempre; hooks.json só no Antigravity", consumida tanto por `init` quanto pelo subcomando `materialize`. As rotinas subjacentes (`materialize_session_commands`, `materialize_hooks_json`) não mudaram.
- **CLI (`main.py`)** — `upgrade` ganha `--force`; novo subcomando interno `materialize` aplica os materializadores com o código local (e é o que o `upgrade` invoca por subprocesso).
- **`SyncService.check_version_update`** — leitura passiva da versão agora resiliente a relayout (mesmos candidatos), preservando a tolerância a erro e a não-bloqueância.

## 3. Preservadas (regras 🟢 do `_reversa_sdd/domain.md` intactas)

- **RN-N17 (Footprint Global Zero)** — toda escrita continua sob `project_path`; o subprocesso de materialização roda com `cwd=target`. Nenhuma escrita nova fora do repositório.
- **RN-N19 (Inicialização de Repositório Alvo)** — `init` segue replicando core + wrapper, criando a venv e instalando ganchos; só trocou as chamadas diretas dos materializadores pela função única (in-process, código já fresco).
- **RN-N27 (Materialização única do `hooks.json`)** — a rotina `materialize_hooks_json` permanece única e inalterada; muda apenas o ponto de invocação (via `apply_local_materializers`/subprocesso).
- **RN-N28 (Materialização única dos slash commands, sempre)** — `materialize_session_commands` permanece única e incondicional; idem quanto à invocação.

## 4. Modificadas (regras 🟢 alteradas)

- **RN-N20 (Evolução Não-Destrutiva — Upgrade)** — a não-destrutividade é preservada, mas o **comportamento do upgrade** mudou: (a) rematerializa com o código recém-copiado, não com os módulos antigos em memória; (b) aborta barulhento quando a versão do upstream é indeterminada, em vez de concluir "Sucesso" sem efeito; (c) ganha o modo `--force`.
- **RN-N21 (Checagem Passiva de Atualização)** — a leitura de versão (no boot e no upgrade) passa de caminho fixo para caminhos-candidato, sobrevivendo a relocações de layout do upstream; permanece passiva, rápida e tolerante a erro.
