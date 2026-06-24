# Install (Prompt de Instalação Colável) — Tarefas de Implementação

> Regenerado pelo Writer em 2026-06-24 (Re-extração; feature 003)
> Sequência executável para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

## Pré-requisitos

- [ ] `FileSystemPort` disponível (porta `core/ports/fs.py`).
- [ ] `argparse.ArgumentParser` da CLI montado e passável ao serviço.
- [ ] `template.md` presente no diretório da unit.

## Tarefas

- [ ] T-01, Definir a hierarquia de perfis (`HarnessProfile` ABC + 3 concretas)
  - Origem no legado: `core/install/harness_profiles.py`
  - Critério de pronto: `ClaudeProfile`/`GeminiProfile`/`AntigravityProfile` implementam `hooks_block()` e `apply_instructions()`; `ClaudeProfile` retorna o JSON real de hooks (SessionStart/PostToolUse/Stop com `${CLAUDE_PROJECT_DIR}` e timeouts).
  - Confiança: 🟢

- [ ] T-02, Implementar `get_profile(name)` com fail-fast
  - Origem no legado: `core/install/harness_profiles.py`
  - Critério de pronto: resolve via dict `_PROFILES`; nome fora do conjunto levanta `ValueError`.
  - Confiança: 🟢

- [ ] T-03, Implementar `InstallPromptService.render`
  - Origem no legado: `core/install/service.py`
  - Critério de pronto: chama `get_profile` **antes** de ler o template; substitui os 4 placeholders; retorna Markdown sem `{{...}}` residual.
  - Confiança: 🟢

- [ ] T-04, Reusar introspecção do argparse para `{{COMMANDS}}`
  - Origem no legado: `core/install/service.py` (espelha `documentation/service.py:extract_commands`)
  - Critério de pronto: cada subcomando vira `- \`<name>\` — <help>`, refletindo a CLI real.
  - Confiança: 🟢

- [ ] T-05, Expor o subcomando `install-prompt` na CLI
  - Origem no legado: `src/main.py`
  - Critério de pronto: `./harness install-prompt` resolve `active_harness` por `load_config` e imprime o prompt em stdout.
  - Confiança: 🟢

- [ ] T-06, Escrever o `template.md`
  - Origem no legado: `core/install/template.md`
  - Critério de pronto: 5 passos (venv, wrapper, ganchos, índice de decisões, verificação de saúde) com os 4 placeholders.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Happy path: render para `claude` produz o JSON de hooks e a lista de comandos, sem placeholder residual.
- [ ] TT-02, Caso de erro: harness inválido levanta `ValueError` antes de ler o template (fail-fast).
- [ ] TT-03, Render para `gemini` e `antigravity` produzem blocos de ganchos distintos do Claude.
  - Cobertura existente: `tests/test_install.py`.

## Ordem Sugerida

1. T-01 e T-02 (perfis + resolução) antes de T-03 (o render depende deles).
2. T-04 pode ser paralela a T-01/T-02.
3. T-05 e T-06 fecham a integração CLI + template.

## Lacunas Pendentes (🔴)

- Nenhuma 🔴. Ressalva 🟡: o `AntigravityProfile` descreve mecanismo de ganchos ainda não confirmado.
