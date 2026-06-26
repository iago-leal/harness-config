# Legacy Impact: Versionar o estado da sessão ao encerrar

> Identificador: `013-commit-encerrar-sessao`
> Data: `2026-06-26`
> Base: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`, `_reversa_sdd/comandos-customizados/`

## 1. Arquivos afetados

| Arquivo afetado                                                                                                    | Componente (`_reversa_sdd/`)                             | Tipo                  | Severidade | Justificativa                                                                                            |
| ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------- | --------------------- | ---------- | -------------------------------------------------------------------------------------------------------- |
| `src/core/ports/git.py`                                                                                            | `GitPort` (porta) — `architecture.md`, `domain.md#RN-N5` | regra-nova (contrato) | MEDIUM     | Novo método abstrato `commit_paths`; qualquer adapter de `GitPort` passa a precisar implementá-lo.       |
| `src/adapters/git/subprocess.py`                                                                                   | `SubprocessGitAdapter`                                   | regra-nova            | LOW        | Implementa `commit_paths` (`git add -- <paths>` + `git commit`); leitura existente intacta.              |
| `src/core/commands/service.py`                                                                                     | `CommandService` (Comandos Customizados)                 | regra-alterada        | MEDIUM     | Ramo `encerrar-sessao` passa a versionar o `state_file` e reportar dois hashes; falha vira erro nomeado. |
| `src/core/commands/errors.py`                                                                                      | Erros de Comandos                                        | componente-novo       | LOW        | `SessionCommitError` (falha barulhenta de commit), no padrão de `MalformedSessionStateError`.            |
| `src/core/install/harness_profiles.py`                                                                             | Perfis / Materializador de session commands              | regra-alterada        | LOW        | `description`/corpo dos slash commands reescritos para descrever o commit de encerramento.               |
| `src/core/domain/config.py`                                                                                        | Configuração (versão)                                    | regra-alterada        | MEDIUM     | Bump 1.2.48 → 1.2.49; gate de rematerialização não-stale no `upgrade`.                                   |
| `src/core/bootstrap/init_service.py`                                                                               | Bootstrap (`current_version`)                            | regra-alterada        | MEDIUM     | Bump 1.2.48 → 1.2.49 espelhado.                                                                          |
| `tests/test_commands.py`, `tests/test_adapters.py`, `tests/test_session_command_profiles.py`, `tests/test_init.py` | Suíte de testes                                          | cobertura             | LOW        | Novos testes (Git fake, isolamento do commit, falha barulhenta, texto) e ajuste do assert de versão.     |

> Nenhum impacto em modelo de dados (`SessionState` intacto) nem em contrato externo
> HTTP/fila/gRPC/GraphQL. Detalhe em `data-delta.md`.

## 2. Diff conceitual por componente

**`CommandService` (ramo `encerrar-sessao`).** Antes: capturava o HEAD, `close_session`,
`save_session` e retornava a mensagem — deixando o `estado-da-sessao.md` pendente no
working tree. Agora: a âncora segue capturada **antes** das escritas (último commit de
trabalho); após `save_session`, o serviço chama `commit_paths(repo_path, [state_file], ...)`,
commitando **exclusivamente** o arquivo de estado por cima do trabalho; a saída reporta
âncora **e** hash de encerramento; se o commit não nasce, levanta `SessionCommitError`
sem reverter o estado salvo. Vale para CLI e MCP, que compartilham o serviço.

**`GitPort` + `SubprocessGitAdapter`.** A porta ganha `commit_paths`; o adapter o
implementa com `git add -- <paths>` (pathspec explícito, nunca `-A`) seguido de
`git commit`, devolvendo o HEAD resultante. O domínio continua falando com Git só pela
porta (RN-N5 intacta).

**Perfis de harness.** Os `session_command_artifact` de Claude e Antigravity passam a
descrever que o encerramento cria um commit de registro por cima do último commit de
trabalho; o acionamento (`!`-bash do Claude, caminho absoluto do Antigravity) é
preservado. Bump de versão garante que o `upgrade` rematerialize o texto novo (não stale).

## 3. Preservadas (regras 🟢 do `domain.md` que continuam intactas)

- **RN-07 (Âncora Git):** a âncora gravada continua sendo o HEAD do **trabalho**; o commit de encerramento fica por cima sem alterar a semântica da âncora na retomada.
- **RN-N5 (core não conhece a infra):** o commit acontece via porta `GitPort`; o domínio não toca `subprocess`/`git` direto.
- **RN-N4 (ausente ≠ malformado / falha barulhenta):** estendida coerentemente — a nova falha de commit também é barulhenta e nomeada.
- **RN-N1 (estado é artefato versionado):** reforçada — o fechamento agora versiona de fato o artefato.
- **RN-N2 / RN-N3 (round-trip e narrativa preservada):** inalteradas; o formato do artefato não muda.
- **Footprint per-projeto (RN-N17):** o commit ocorre sob `repo_path` e só toca o `state_file`.

## 4. Modificadas (regras 🟢 alteradas)

- **Isolamento no fechamento (`comandos-customizados`):** antes `encerrar-sessao` lia HEAD, `close_session` e salvava **sem** versionar; agora também cria um commit contendo só o `state_file`.
- **Saída do `encerrar-sessao`:** antes reportava só a âncora; agora reporta âncora **e** hash do commit de encerramento.
- **Texto dos slash commands materializados:** antes "gravando o commit-âncora"; agora descreve o commit de registro por cima do trabalho.
- **Versão do core:** 1.2.48 → 1.2.49 (gate de rematerialização não-stale).
