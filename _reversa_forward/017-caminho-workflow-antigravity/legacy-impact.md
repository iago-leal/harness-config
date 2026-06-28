# Legacy Impact: feature 017

> Feature `017-caminho-workflow-antigravity` · 2026-06-28
> Extração de referência: `_reversa_sdd/` (architecture.md, domain.md, comandos-customizados/)

## 1. Arquivos afetados

| Arquivo afetado                                                                                                                                                                 | Componente (legado)                                                                                                               | Tipo                      | Severidade | Justificativa                                                                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/install/harness_profiles.py`                                                                                                                                          | Comandos Customizados — materialização de slash command de IDE (`AntigravityProfile`), `_reversa_sdd/comandos-customizados/#f010` | delta-de-contrato-externo | MEDIUM     | Muda o caminho do artefato de workflow do Antigravity de `.agents/workflows/` (plural) para `.agent/workflows/` (singular) e remove `name:` do frontmatter. Corrige defeito de reconhecimento. |
| `src/core/install/session_commands.py`                                                                                                                                          | Materializador de session commands (feature 010/012)                                                                              | regra-nova                | LOW        | Acrescenta limpeza não-destrutiva de órfãos legados declarados pelo perfil.                                                                                                                    |
| `src/core/domain/config.py`                                                                                                                                                     | Configuração canônica (`HarnessSection.version`)                                                                                  | regra-alterada            | LOW        | Bump 1.2.53 → 1.2.54 (propagação via upgrade).                                                                                                                                                 |
| `src/core/bootstrap/init_service.py`                                                                                                                                            | Bootstrap/`init` (`current_version`)                                                                                              | regra-alterada            | LOW        | Bump 1.2.53 → 1.2.54 sincronizado.                                                                                                                                                             |
| `tests/test_antigravity_profile.py`, `tests/test_session_commands_materializer.py`, `tests/test_local_apply.py`, `tests/test_session_command_profiles.py`, `tests/test_init.py` | Cobertura de testes                                                                                                               | —                         | LOW        | Asserções adaptadas ao caminho singular + novos testes de migração/limpeza e versão.                                                                                                           |

## 2. Diff conceitual por componente

**`AntigravityProfile.session_command_artifact`** — antes devolvia `(".agents/workflows/encerrar-sessao.md", content)` com frontmatter `name:` + `description:`. Agora devolve `(".agent/workflows/encerrar-sessao.md", content)` com frontmatter só `description:`. O corpo (delegação a `./harness cmd …`) é idêntico — a lógica de fechamento não muda (RN-N5 intacta).

**`HarnessProfile` (base) + override Antigravity** — novo método `stale_session_command_paths()` (default `[]`); o Antigravity declara `[".agents/workflows/encerrar-sessao.md"]`. O conhecimento dos caminhos legados vive no perfil, mantendo a rotina de materialização agnóstica ao harness.

**`materialize_session_commands`** — após gravar o artefato no caminho atual, remove cada caminho legado existente declarado pelo perfil (`fs.exists` → `fs.remove`), nunca diretórios. É a migração executada na própria passada do `init`/`upgrade` (feature 012), sem script dedicado.

**Versão do core** — 1.2.53 → 1.2.54 nos dois pontos sincronizados; o `upgrade` regrava materializadores quando detecta versão nova, propagando o caminho corrigido aos consumidores.

## 3. Preservadas (regras 🟢 do `domain.md` intactas)

- **RN-N5 — Core não conhece o harness** (`domain.md#2.12`): a lógica de fechamento segue no `CommandService`; a borda/perfil decide a entrega. O workflow só delega. ✅
- **RN-N17 — Footprint global zero**: toda escrita e remoção ocorre sob `project_path`. Verificado por `test_nada_e_escrito_fora_do_project_path` e pelo smoke real. ✅
- **RN-N27 — Gate do `.agents/hooks.json` por harness ativo**: inalterado; hooks fora do escopo (clarify). ✅
- **Non-destructive (Reversa/Harness)**: reforçada — a limpeza remove só o arquivo nomeado, preservando terceiros e diretórios. ✅

## 4. Modificadas (regras 🟢 alteradas)

- **RN-N28 / RN-N29 — Materialização do par de slash commands de sessão** (`domain.md#2.12`, `comandos-customizados/#f010`): a regra de materializar o par (Claude + Antigravity) permanece; **muda o caminho do artefato do Antigravity** para `.agent/workflows/` (singular) e o **frontmatter** passa a expor só `description`. A spec extraída (`comandos-customizados/requirements.md#f010`) e o ADR 0017 ainda registram o caminho plural — **reconciliar na próxima re-extração**.
