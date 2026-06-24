# Install (Prompt de Instalação Colável) — Design Técnico

> Regenerado pelo Writer em 2026-06-24 (Re-extração; feature 003)
> Foca no COMO a unit é construída, a partir do código legado lido. Escala: 🟢 / 🟡 / 🔴

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `InstallPromptService.render` | `(active_harness: str, parser: ArgumentParser)` | `str` | Prompt Markdown pronto para colar. Resolve o perfil **antes** de ler o template (fail-fast). |
| `HarnessProfile.hooks_block` | `()` (abstrato) | `str` | Bloco de ganchos específico do harness (corpo do code fence `{{HOOKS_BLOCK}}`). |
| `HarnessProfile.apply_instructions` | `()` (abstrato) | `str` | Texto que instrui como aplicar os ganchos (`{{APPLY_HOOKS}}`). |
| `get_profile` | `(name: str)` | `HarnessProfile` | Resolve via dict `_PROFILES`; nome fora do conjunto → `ValueError`. |

Placeholders substituídos no `template.md`:

| Placeholder | Origem |
|---|---|
| `{{ACTIVE_HARNESS}}` | `active_harness` recebido |
| `{{APPLY_HOOKS}}` | `profile.apply_instructions()` |
| `{{HOOKS_BLOCK}}` | `profile.hooks_block()` |
| `{{COMMANDS}}` | introspecção do `argparse` → `- \`<name>\` — <help>` por subcomando |

## Fluxo Principal

1. `render` chama `get_profile(active_harness)` **primeiro** — se inválido, `ValueError` aqui, antes de qualquer leitura de arquivo (RN-N10). 🟢 (`service.py`)
2. Lê `template.md` (do diretório da própria unit) via `FileSystemPort`. 🟢
3. Extrai a lista de comandos por introspecção do `parser` (varre `_actions`, acha o `_SubParsersAction`, lê `help`/`description` de cada subparser) — mesmo padrão de `DocumentationService.extract_commands`. 🟢
4. Substitui os 4 placeholders e retorna o Markdown final. 🟢
5. O driver `main.py` (subcomando `install-prompt`) resolve `active_harness` via `load_config(fs).harness.active_harness`, instancia o serviço com `FileSystemPort` e imprime o resultado em stdout. 🟢

## Fluxos Alternativos

- **Harness inválido:** `get_profile` levanta `ValueError` com o nome recebido; o `render` nem chega a ler o template. 🟢
- **Template ausente:** `FileSystemPort.read_file` propaga o erro de I/O (não há `try/except` silencioso aqui). 🟡 INFERIDO (comportamento padrão da porta).

## Dependências

- `FileSystemPort` — leitura de `template.md`. Injetada no construtor.
- `argparse.ArgumentParser` — recebido em `render`, fonte da lista de comandos (introspecção).
- `harness_profiles.get_profile` — resolução da estratégia por harness.
- `core/domain/config.load_config` — usado pelo **driver** (`main.py`) para descobrir `active_harness`, não pelo serviço.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Strategy/OOP para o bloco de ganchos por harness (uma classe por perfil) | `harness_profiles.py` (`ABC` + 3 concretas + `_PROFILES`) | 🟢 |
| Resolução do perfil antes de I/O (fail-fast) | `service.py` (ordem de `get_profile` × `read_file`) | 🟢 |
| Reuso do padrão de introspecção do argparse do `DocumentationService` | `service.py` × `documentation/service.py` | 🟢 |
| Exposição apenas pela CLI (não há tool MCP de instalação) | `main.py` (subcomando), ausência em `mcp/server.py` | 🟢 |

## Estado Interno

A unit é **sem estado persistente**: produz texto a cada chamada. O único "estado" é o registro estático de perfis `_PROFILES` em `harness_profiles.py`.

## Observabilidade

Sem logging dedicado. O fail-fast (`ValueError`) é a sinalização barulhenta de erro de configuração; a saída é o próprio prompt em stdout.

## Riscos e Lacunas

- 🟡 `AntigravityProfile` emite um bloco-aviso ("mecanismo ainda não confirmado") — o ganchamento real do Antigravity não está validado no código.
- 🟡 O `template.md` traz uma "pendência conhecida" textual sobre o `SessionStart` (referente à feature 004) — texto histórico do template, não comportamento de código.
