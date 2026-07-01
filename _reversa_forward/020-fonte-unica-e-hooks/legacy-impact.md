# Legacy-impact: fonte única + hooks não-destrutivos

> Feature: `020-fonte-unica-e-hooks` · Data: `2026-07-01`
> **Rodada parcial** — bloco dos materializadores não-destrutivos (T004, T005, T010, T011). Os blocos de shim/init, remoção de sync/version e `migrate` ainda não foram executados; este arquivo será complementado nas próximas rodadas.

## Arquivos afetados

| Arquivo afetado                         | Componente (`_reversa_sdd/`)                                                 | Tipo           | Severidade | Justificativa                                                                                                                                                                                                          |
| --------------------------------------- | ---------------------------------------------------------------------------- | -------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/install/claude_settings.py`   | `materialize_claude_settings` — `domain.md#2.13` (RN-N30), feature 016/RN-05 | regra-alterada | MEDIUM     | Merge do `.claude/settings.json` deixa de substituir o array inteiro do evento (`hooks[event] = value`) e passa a mesclar **por-item** por assinatura no `command`, preservando hooks do usuário no mesmo evento       |
| `src/core/bootstrap/service.py`         | `install_hooks` — `domain.md#2.7` (RN-N15)                                   | regra-alterada | MEDIUM     | Instalação dos hooks git deixa de sobrescrever incondicionalmente `pre-commit`/`post-merge`: agora cria/atualiza/encadeia por assinatura `Harness Core` e os scripts invocam o shim `./harness` em vez do python local |
| `tests/test_install_claude_settings.py` | (suíte)                                                                      | —              | LOW        | +3 testes do merge por-item                                                                                                                                                                                            |
| `tests/test_bootstrap.py`               | (suíte)                                                                      | —              | LOW        | +4 testes de instalação não-destrutiva e via shim                                                                                                                                                                      |

## Diff conceitual por componente

- **`materialize_claude_settings` (por-evento → por-item).** Antes, cada um dos três eventos do harness (`SessionStart`, `PostToolUse`, `Stop`) tinha seu array **substituído por completo**, descartando qualquer hook próprio do usuário no mesmo evento. Agora, para cada evento, localiza-se o item do harness pela substring do `command` (`harness cmd resume`/`harness format`/`harness decisions`) e substitui-se **apenas** esse item (ou insere-se, se ausente), preservando os demais. Chaves de topo e eventos de outro nome seguiam e seguem intactos. Idempotente por assinatura; escrita atômica sob `project_path` mantida (RN-N17).
- **`install_hooks` (sobrescrita → não-destrutivo + shim).** Antes, `pre-commit`/`post-merge` eram reescritos a cada execução, clobbando um hook próprio de mesmo nome. Agora: ausente → cria; com a assinatura `Harness Core` → atualiza no lugar; sem a assinatura (alheio) → preserva o conteúdo em `<hook>.local` e o encadeia. Os scripts passam a chamar `./harness format`/`./harness decisions` (shim), desacoplados de `CORE_MAIN_REL_PATH`/`CORE_VENV_PYTHON_REL_PATH`; o não-bloqueio (RN-N15) é preservado por guarda `[ -x ./harness ]` (shim ausente → `exit 0`).

## Preservadas (regras 🟢 do `domain.md` intactas)

- **RN-N27** (`materialize_hooks_json`, merge por named-hook do Antigravity) — não tocada; serviu de molde.
- **RN-N28/N29** (`session_skills`, materialização não-destrutiva por nome próprio) — não tocadas.
- **RN-N17** (footprint global zero) — preservada: toda escrita segue sob `project_path`/`.git/hooks` do projeto, atômica.
- **RN-N4** (comportamento barulhento/não-silencioso) — preservada.

## Modificadas (regras 🟢 alteradas)

- **RN-N15** (Bootstrap idempotente — "reescreve os arquivos a cada execução") → agora **não-destrutivo por assinatura** e via shim. A idempotência permanece; a sobrescrita cega, não.
- **Materialização do `settings.json` do Claude** (feature 016/RN-05, sob RN-N30) → merge **por-item**, não mais por-evento.
