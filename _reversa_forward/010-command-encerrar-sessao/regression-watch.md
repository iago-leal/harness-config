# Regression Watch: Comando de IDE para encerrar a sessão

> Identificador: `010-command-encerrar-sessao`
> Data: `2026-06-24`
> Gerado por `/reversa-coding`. A próxima `/reversa` (re-extração) confere estes itens e preenche o histórico.

## Itens de vigilância

| ID   | Origem (arquivo, seção)                                                                          | Regra esperada após a mudança                                                                                                                                         | Tipo de verificação | Sinal de violação                                                                                       |
| ---- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------- |
| W001 | `domain.md#2.9` RN-N19 · `src/core/bootstrap/init_service.py`                                    | `init` materializa `.claude/commands/encerrar-sessao.md` **e** `.agents/workflows/encerrar-sessao.md`, para qualquer `active_harness`                                 | presença            | Após `init`, um dos dois arquivos não existe no projeto-alvo                                            |
| W002 | `domain.md#2.9` RN-N20 · `src/core/bootstrap/init_service.py`                                    | `upgrade` (re)materializa os dois comandos, com o caminho absoluto do wrapper correto                                                                                 | presença            | Após `upgrade`, arquivo ausente ou com caminho de wrapper desatualizado                                 |
| W003 | `domain.md#2.8` RN-N17 · `src/core/install/session_commands.py`                                  | A materialização dos comandos escreve apenas sob `project_path`                                                                                                       | presença            | `FootprintViolation` no teste, ou escrita fora do repositório / em `~/.claude`                          |
| W004 | `comandos-customizados/requirements.md#RF-02` · `src/core/commands/service.py`                   | O comando aciona o `encerrar-sessao` do core sem reimplementá-lo (delegação a `./harness cmd encerrar-sessao`)                                                        | redação             | Arquivo de comando contém lógica de fechamento própria em vez de chamar o wrapper                       |
| W005 | `interfaces/session-command-files.md` · `src/core/install/harness_profiles.py` (`ClaudeProfile`) | O slash command do Claude usa `./harness` (relativo à raiz); **nunca** `${CLAUDE_PROJECT_DIR}` (não expande no `!`-bash de slash command, só em hooks — issue #33815) | redação             | `.claude/commands/encerrar-sessao.md` contém `${CLAUDE_PROJECT_DIR}` → expande para `/harness` e quebra |

## Observações (confidência 🟡, sem peso de regressão)

- **D-06 — execução no Antigravity:** o comportamento exato do workflow do Antigravity (execução de shell embutida vs instrução ao agente) não é verificável localmente. O corpo do `.agents/workflows/encerrar-sessao.md` instrui a execução de `<command_path>/harness cmd encerrar-sessao`; validar contra o Antigravity real quando disponível. Alinha ao watch-item amarelo herdado da feature 009 (premissas de runtime do Antigravity).

## Histórico de re-extrações

### Re-extração 2026-06-25 14:32

| ID   | Veredito | Observação                                                                                                                                                         |
| ---- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| W001 | 🟢 verde | `init` materializa `.claude/commands/encerrar-sessao.md` e `.agents/workflows/encerrar-sessao.md` — coberto por `test_init` na suíte; `domain.md#RN-N28`.          |
| W002 | 🟢 verde | `upgrade` (re)materializa os dois comandos — agora via `apply_local_materializers`/subprocesso (fix da 012), com o caminho de wrapper correto; coberto pela suíte. |
| W003 | 🟢 verde | Materialização escreve só sob `project_path` — `test_session_commands_materializer.py` (`RecordingFileSystem`) verde; RN-N17/RN-N28.                               |
| W004 | 🟢 verde | O comando delega ao `encerrar-sessao` do core sem reimplementá-lo (RN-N5/RN-N29).                                                                                  |
| W005 | 🟢 verde | Slash command do Claude usa `./harness` (não `${CLAUDE_PROJECT_DIR}`); coberto por `test_session_command_profiles.py`. Inalterado por 011/012.                     |

### Re-extração 2026-06-24 19:30 (pós-feature 010)

| ID   | Veredito | Observação                                                                                                                                                                                                                                                                  |
| ---- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | `init` materializa `.claude/commands/encerrar-sessao.md` e `.agents/workflows/encerrar-sessao.md` para qualquer `active_harness` — reconciliado em `_reversa_sdd/domain.md#RN-N28`; coberto por `test_init.py::test_init_materializes_session_commands_for_both_harnesses`. |
| W002 | 🟢 verde | `upgrade` (re)materializa os dois comandos — `test_upgrade_materializes_session_commands` verde.                                                                                                                                                                            |
| W003 | 🟢 verde | Materialização escreve só sob `project_path` — `test_session_commands_materializer.py` (`RecordingFileSystem`) verde; RN-N28/RN-N17.                                                                                                                                        |
| W004 | 🟢 verde | O comando delega ao `encerrar-sessao` do core sem reimplementá-lo (RN-N5/RN-N29).                                                                                                                                                                                           |

### Verificação manual 2026-06-24 (conclusão da 010)

| ID   | Veredito | Observação                                                                                                                                                                                                                                             |
| ---- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| W005 | 🟢 verde | Corpo do command corrigido para `./harness`; `${CLAUDE_PROJECT_DIR}` removido. Verificado de dentro de `dev/TECH+` (caminho feliz encerra e grava o âncora). Coberto por `test_session_command_profiles.py` e `test_session_commands_materializer.py`. |

**Achados adjacentes (fora da 010, surgidos na verificação):**

- **Hooks do Claude:** `${CLAUDE_PROJECT_DIR}` expande corretamente em hooks — verificado nos logs reais de TECH+ (Claude Code 2.1.191): 19 carregamentos de estado, zero `hookErrors`. O `hooks_block` do `ClaudeProfile` está correto e não muda.
- **Parser de estado (feature 004):** o template inicial do `init` (campos todos `null`) era lido como malformado, fazendo `/encerrar-sessao` sem sessão ativa emitir "estado malformado" em vez de "Nenhuma sessão ativa". Corrigido em `serializer.parse` (commit `dcc8905`): sentinela todos-null → "sem sessão"; corrupção parcial segue barulhenta (RN-N4).

## Arquivadas

> Vazio.
