# Legacy Impact: Comando de IDE para encerrar a sessão

> Identificador: `010-command-encerrar-sessao`
> Data: `2026-06-24`
> Base de comparação: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`

## Arquivos afetados

| Arquivo afetado                                            | Componente (`_reversa_sdd/`)                                | Tipo            | Severidade | Justificativa                                                                                                                                             |
| ---------------------------------------------------------- | ----------------------------------------------------------- | --------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `harness-core/src/core/install/session_commands.py`        | Serviço `install` (`architecture.md#1`)                     | componente-novo | LOW        | Novo módulo aditivo, irmão de `antigravity_hooks.py`; rotina única `materialize_session_commands`                                                         |
| `harness-core/src/core/install/harness_profiles.py`        | Estratégia `HarnessProfile` (`architecture.md#5`)           | regra-nova      | LOW        | Novo método `session_command_artifact`; base devolve `None`, Claude e Antigravity sobrescrevem. Nenhum comportamento existente alterado                   |
| `harness-core/src/core/bootstrap/init_service.py`          | Bootstrap `init`/`upgrade` (`domain.md#2.9`, RN-N19/RN-N20) | regra-alterada  | MEDIUM     | `initialize_project` e `upgrade_project` passam a chamar `materialize_session_commands` incondicionalmente (novo efeito colateral de escrita por harness) |
| `harness-core/tests/test_session_commands_materializer.py` | — (cobertura)                                               | componente-novo | LOW        | Testes do materializador, incluindo footprint                                                                                                             |
| `harness-core/tests/test_session_command_profiles.py`      | — (cobertura)                                               | componente-novo | LOW        | Testes do artefato de comando por perfil                                                                                                                  |
| `harness-core/tests/test_init.py`                          | — (cobertura)                                               | regra-alterada  | LOW        | Dois testes de integração novos (init/upgrade materializam os dois comandos)                                                                              |

## Diff conceitual por componente

- **Serviço `install`:** ganha um segundo materializador físico. Antes só `materialize_hooks_json` (gated por `active_harness == "antigravity"`); agora `materialize_session_commands` grava, **sempre**, dois arquivos de slash command (`.claude/commands/encerrar-sessao.md` e `.agents/workflows/encerrar-sessao.md`). Mesmo contrato de footprint e atomicidade do molde da feature 009.
- **Estratégia `HarnessProfile`:** o conhecimento por-harness do arquivo de comando fica encapsulado em cada perfil, sem `if active_harness` no serviço (RN-N5 reforçada). Gemini herda `None` — sem superfície definida, ponto de extensão aberto.
- **Bootstrap `init`/`upgrade`:** o ciclo de instalação/evolução agora também projeta os comandos de IDE. A escrita é incondicional (D-03), diferente do gate da materialização de hooks. A não-destrutividade é preservada: cada comando é um arquivo próprio; arquivos de terceiros nos diretórios não são lidos nem tocados.

## Preservadas (regras 🟢 do `domain.md` intactas)

- **RN-N5 — O Core Não Conhece o Harness:** o comando delega ao `./harness cmd encerrar-sessao`; nenhum serviço de domínio ramifica por harness; a seleção vive nos perfis/borda.
- **RN-N17 — Footprint Global Zero:** toda escrita do novo materializador ocorre sob `project_path`; fixado por teste com `RecordingFileSystem`.
- **RN-N26/RN-N27 — Ganchos do Antigravity:** `materialize_hooks_json` e o driver de borda permanecem inalterados.
- **`encerrar-sessao` (comandos-customizados RF-02):** a lógica de fechamento de sessão no `CommandService` não foi tocada; o comando apenas a aciona.

## Modificadas (regras 🟢 alteradas ou removidas)

- **RN-N19 — Inicialização de Repositório Alvo (Bootstrap):** _alterada (estendida)_ — `init` agora também materializa os comandos de IDE de encerrar-sessão para Claude e Antigravity. Nenhuma remoção; comportamento anterior preservado.
- **RN-N20 — Evolução Não-Destrutiva (Upgrade):** _alterada (estendida)_ — `upgrade` agora (re)materializa os comandos, mantendo o caminho absoluto correto do wrapper. A garantia de não-destrutividade segue válida.

Nenhuma regra 🟢 foi **removida**.
