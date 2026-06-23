# Actions: Instalação do Harness por Prompt Estruturado

> Identificador: `003-instalacao-por-prompt`
> Data: `2026-06-23`
> Roadmap: `_reversa_forward/003-instalacao-por-prompt/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 9 |
| Paralelizáveis (`[//]`) | 8 |
| Maior cadeia de dependência | 4 (T001 → T005 → T007 → T008) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Criar o esqueleto do módulo `core/install/` (`__init__.py` + `service.py` com a classe `InstallPromptService(fs: FileSystemPort)`, construtor e a assinatura vazia de `render(active_harness)`). | - | `[//]` | `harness-core/src/core/install/service.py` | 🟢 | `[X]` |
| T002 | Criar o template do prompt `core/install/template.md` com placeholders para venv/dependências, wrapper, bloco de ganchos e seção de health-check. | - | `[//]` | `harness-core/src/core/install/template.md` | 🟢 | `[X]` |
| T003 | Adicionar um carregador de `HarnessConfig` em `core/domain/config.py` que lê o `harness.toml` via pydantic e expõe `active_harness` (fecha o config ocioso). | - | `[//]` | `harness-core/src/core/domain/config.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T004 | Criar `tests/test_install.py` cobrindo: presença das etapas obrigatórias no prompt, parametrização por harness (claude/gemini), referência ao `.claude/settings.json` do projeto, ausência de instrução a `~/.claude`, e sinalização da lacuna do `SessionStart`. | T001 | `[//]` | `harness-core/tests/test_install.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Implementar no `InstallPromptService` a introspecção da CLI (reusar o padrão de `DocumentationService.extract_commands`) para compor a seção de comandos/health-check do prompt. | T001 | `[//]` | `harness-core/src/core/install/service.py` | 🟢 | `[X]` |
| T006 | Implementar os perfis de ganchos por harness (Strategy) em `core/install/harness_profiles.py`: claude (`settings.json` hooks), gemini (ponte `context.*`), antigravity (placeholder a confirmar). | T001 | `[//]` | `harness-core/src/core/install/harness_profiles.py` | 🟡 | `[X]` |
| T007 | Implementar `InstallPromptService.render(active_harness)`: carrega o template (T002), injeta a superfície introspectada (T005) e o bloco do perfil (T006), e produz o texto final com idempotência (detect-then-complete), sinalização da lacuna do `SessionStart` e aviso de escopo de projeto. | T002, T005, T006 | - | `harness-core/src/core/install/service.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T008 | Registrar o subcomando `install-prompt` no `main.py` (parser sem argumentos) e o handler que lê `active_harness` via o carregador (T003), instancia o serviço e imprime o prompt no stdout. | T003, T007 | `[//]` | `harness-core/src/main.py` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Refinar as mensagens do health-check no template para saída legível item-a-item (aprovado/pendente) e o resumo final que distingue "instalação concluída" de "pendência conhecida (SessionStart)". | T007 | `[//]` | `harness-core/src/core/install/template.md` | 🟢 | `[X]` |

## Notas de execução

<!-- Reservado para /reversa-coding. -->

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-to-do` | reversa |
