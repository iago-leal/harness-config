# Install (Prompt de Instalação Colável) — Requisitos (Requirements)

> Regenerado pelo Writer em 2026-06-24 (Re-extração; feature 003)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`harness-core/src/core/install/`](file:///Users/iagoleal/dev/harness/harness-core/src/core/install/) — `service.py`, `harness_profiles.py`, `template.md`. Driver: `src/main.py` (subcomando `install-prompt`).

## Visão Geral

Esta unit gera, por **composição**, um prompt Markdown que o usuário cola no agente de IA para instalar o harness-core localmente, passo a passo e de forma idempotente. A lista de comandos vem da introspecção do `argparse` (fonte única com a CLI real) e o bloco de ganchos vem do **perfil** do harness ativo (`Claude`/`Gemini`/`Antigravity`), via padrão Strategy. Nada é mantido à mão em paralelo (feature 003).

## Responsabilidades

- Renderizar o `template.md` substituindo quatro placeholders: `{{ACTIVE_HARNESS}}`, `{{APPLY_HOOKS}}`, `{{HOOKS_BLOCK}}`, `{{COMMANDS}}`. 🟢
- Resolver o **perfil de instalação** do harness ativo (estratégia que encapsula o bloco de ganchos e as instruções de aplicação). 🟢
- Falhar cedo (fail-fast) quando o harness ativo for inválido, antes de qualquer I/O. 🟢
- Reusar a introspecção do `argparse` (mesmo padrão de `DocumentationService`) para listar os comandos da CLI. 🟢

## Regras de Negócio

- **RN-N9 — Geração por composição (fonte única):** o prompt é montado por substituição de 4 placeholders no `template.md`; a lista de comandos vem da introspecção do `argparse`. Exposto **apenas pela CLI** (`install-prompt`), não pelo MCP. 🟢
- **RN-N10 — Resolução de perfil fail-fast:** o perfil do harness é resolvido **antes** de ler o template; harness inválido levanta `ValueError` barulhento. `get_profile` resolve via dict `_PROFILES`. 🟢
- **Bloco de ganchos específico por perfil:** `ClaudeProfile` emite o JSON `hooks` real (`SessionStart`→`harness cmd resume`; `PostToolUse` Write|Edit→`harness format`; `Stop`→`harness decisions`, com `${CLAUDE_PROJECT_DIR}` e timeouts); `GeminiProfile` orienta a ponte `context.*` do settings do Gemini; `AntigravityProfile` emite aviso de mecanismo ainda não confirmado. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Renderizar o prompt de instalação para o harness ativo. | Must | `./harness install-prompt` imprime Markdown com os 4 placeholders resolvidos (nenhum `{{...}}` residual). |
| RF-02 | Resolver o perfil por nome de harness. | Must | `claude`/`gemini`/`antigravity` retornam blocos de ganchos distintos; nome fora do conjunto → `ValueError`. |
| RF-03 | Fail-fast antes de I/O. | Must | Com harness inválido, o `ValueError` ocorre **antes** de ler `template.md` (nenhuma leitura de arquivo). |
| RF-04 | Lista de comandos por introspecção do argparse. | Should | `{{COMMANDS}}` lista cada subcomando como `- \`<name>\` — <help>`, igual à CLI real. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Manutenibilidade | Fonte única do prompt (template + perfil + introspecção), sem duplicação manual. | `core/install/service.py` | 🟢 |
| Extensibilidade | Novo harness = nova subclasse de `HarnessProfile` registrada em `_PROFILES`. | `core/install/harness_profiles.py` | 🟢 |
| Robustez | Harness inválido falha de forma explícita (fail-fast), nunca gera prompt incoerente. | `core/install/service.py` (`get_profile` antes de ler template) | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que o harness ativo é "claude"
Quando executo `./harness install-prompt`
Então o prompt contém o bloco JSON de hooks do Claude (SessionStart/PostToolUse/Stop)
E a lista de comandos da CLI aparece no Passo 5
E nenhum placeholder {{...}} permanece no texto.

Dado um harness ativo inválido (ex.: "vscode")
Quando o InstallPromptService.render é chamado
Então um ValueError é levantado antes de o template.md ser lido.
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Render por composição (RN-N9) | Must | Único caminho de geração do prompt; sem ele a unit não entrega nada. |
| Resolução fail-fast de perfil (RN-N10) | Must | Garante coerência do prompt e erro barulhento; precede todo I/O. |
| Introspecção do argparse para comandos | Should | Mantém o prompt sincronizado com a CLI; degradaria para lista manual. |
| Bloco de ganchos do Antigravity | Could | Mecanismo ainda não confirmado; emite apenas aviso. 🟡 |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `core/install/service.py` | `InstallPromptService.render` | 🟢 |
| `core/install/harness_profiles.py` | `HarnessProfile` (ABC), `ClaudeProfile`, `GeminiProfile`, `AntigravityProfile`, `get_profile` | 🟢 |
| `core/install/template.md` | Template com 4 placeholders | 🟢 |
| `src/main.py` | Subcomando `install-prompt` (resolve `active_harness` via `load_config`) | 🟢 |
| `tests/test_install.py` | Cobertura de teste | 🟢 |
