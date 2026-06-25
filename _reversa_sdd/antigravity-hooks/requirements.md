# Antigravity Hooks (Driver de Ganchos do Antigravity) — Requisitos (Requirements)

> Gerado pelo Archaeologist em 2026-06-24 15:19 (Re-extração após a feature 009-hooks-antigravity). Âncora (HEAD): `e30b9a6`.
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`.harness/harness-core/src/adapters/antigravity/hook_bridge.py`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/adapters/antigravity/hook_bridge.py), [`.harness/harness-core/src/core/install/antigravity_hooks.py`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/core/install/antigravity_hooks.py), [`.harness/harness-core/src/core/install/harness_profiles.py`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/core/install/harness_profiles.py). Drivers: `src/main.py` (subcomando `agy-hook`), `src/core/bootstrap/init_service.py` (materialização no `init`/`upgrade`).

## Visão Geral

Esta unit é o **terceiro driver de entrada** do hexágono, irmão da CLI e do servidor MCP. Traduz o protocolo de ganchos de ciclo de vida do Antigravity — um `.agents/hooks.json` declarativo e um diálogo stdin/stdout JSON (camelCase) por evento — e **delega aos serviços de domínio já existentes** (`FormattingService`, `DecisionService`), sem que o core conheça o harness ativo. A capacidade tem duas faces: (i) o **adaptador de borda** (`AntigravityHookBridge`), invocado pelo subcomando fino `./harness agy-hook <evento>`; e (ii) a **materialização** do `.agents/hooks.json` no projeto-alvo (`materialize_hooks_json`), compartilhada por `init` e `upgrade`.

## Responsabilidades

- Falar o protocolo de ganchos do Antigravity por evento (`PreToolUse`/`PostToolUse`/`Stop`), lendo o payload JSON no stdin e emitindo o JSON exigido no stdout. 🟢
- Recuperar o caminho do arquivo editado por **captura no `PreToolUse` + formatação no `PostToolUse`**, usando `artifactDirectoryPath` como scratch para o mapa `stepIdx → TargetFile`. 🟢
- Delegar a formatação a `FormattingService.format_file` e a indexação de decisões a `DecisionService`, sem duplicar lógica nem ramificar o core por harness. 🟢
- Nunca bloquear o laço do agente: capturar toda exceção, logar em stderr (erro barulhento) e ainda emitir o stdout exigido com exit 0. 🟢
- Emitir o `.agents/hooks.json` canônico (named-hook `harness`) via `AntigravityProfile.hooks_block()`, e materializá-lo no projeto-alvo por **merge por named-hook**, preservando chaves de terceiros e escrevendo só sob o projeto. 🟢

## Regras de Negócio

- **RN-N5 — O core não conhece o harness:** toda a lógica do Antigravity vive no adaptador, no perfil e no materializador; nenhum serviço de domínio é ramificado por `active_harness`. 🟢
- **RN-03 — Não-bloqueio absoluto:** os ganchos nunca emitem `"decision": "deny"` nem `"decision": "continue"`. Falha é logada, não abortada; o stdout exigido por evento é sempre emitido, com exit 0. 🟢
- **RN-N9 — Quatro placeholders preservados:** a feature não acrescenta placeholders ao prompt de instalação; o escopo dos ganchos flui por `{{APPLY_HOOKS}}`. 🟢
- **RN-N17 — Footprint global zero:** `materialize_hooks_json` escreve apenas dentro do projeto-alvo (`<project>/.agents/hooks.json`), via `FileSystemPort`; nunca em diretório global do usuário. 🟢
- **Merge por named-hook:** a materialização substitui apenas a chave `harness` do `hooks.json`, preservando quaisquer outras chaves de terceiros (idempotência). 🟢
- **Caminho absoluto no `command`:** o `command` dos ganchos é gravado por caminho absoluto (`<ABS>` resolvido no `init`); o `upgrade` reescreve-o caso o repositório tenha sido movido. 🟢

## Requisitos Funcionais

| ID    | Requisito                               | Prioridade | Critério de Aceite                                                                                                 |
| ----- | --------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------ |
| RF-01 | Captura no `PreToolUse`.                | Must       | `agy-hook pre-tool-use` grava `{ "<stepIdx>": "<TargetFile>" }` no scratch e emite `{"decision": "allow"}`.        |
| RF-02 | Formatação no `PostToolUse`.            | Must       | `agy-hook post-tool-use` resolve o caminho pelo `stepIdx`, chama `format_file` se elegível, e emite `{}`.          |
| RF-03 | Indexação de decisões no `Stop`.        | Must       | `agy-hook stop` valida e recompila o índice de microdecisões e emite `{}` (nunca `"continue"`).                    |
| RF-04 | Materialização do `.agents/hooks.json`. | Must       | `init`/`upgrade` com `active_harness = antigravity` escrevem o named-hook `harness` por merge, sob o projeto.      |
| RF-05 | Não-bloqueio sob qualquer falha.        | Must       | Config corrompida, stdin ilegível ou exceção no handler ainda emitem o stdout exigido por evento e encerram com 0. |
| RF-06 | Subcomando `agy-hook` na CLI.           | Must       | `./harness agy-hook <evento>` aceita `pre-tool-use`/`post-tool-use`/`stop` e instancia o adaptador na borda.       |

## Requisitos Não Funcionais

| Tipo              | Requisito inferido                                                            | Evidência no código                                     | Confiança |
| ----------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------- | --------- |
| Robustez          | Falha do gancho nunca interrompe o laço do agente Antigravity.                | `hook_bridge.py` (`_safe`), `main.py` (ramo `agy-hook`) | 🟢        |
| Baixo acoplamento | Adaptador recebe `fs` e serviços por injeção; instanciação concreta na borda. | `hook_bridge.py` (`__init__`), `main.py`                | 🟢        |
| Idempotência      | Captura, formatação e indexação reexecutam sem efeito colateral.              | `hook_bridge.py`, `antigravity_hooks.py`                | 🟢        |
| Reprodutibilidade | Sem dependência nova: só `json`/`os`/`sys` da stdlib.                         | `hook_bridge.py`, `antigravity_hooks.py`                | 🟢        |
| Observabilidade   | Erro barulhento em stderr; stdout reservado ao contrato.                      | `hook_bridge.py` (`_log`)                               | 🟢        |

## Critérios de Aceitação

```gherkin
Dado um payload de PreToolUse com stepIdx=3 e toolCall.args.TargetFile="src/a.py"
Quando `./harness agy-hook pre-tool-use` recebe o JSON no stdin
Então grava {"3": "src/a.py"} em <artifactDirectoryPath>/.harness-agy/pending-format.json
E imprime {"decision": "allow"} no stdout.

Dado um payload de PostToolUse com stepIdx=3, error vazio, e o scratch contendo {"3": "src/a.py"}
Quando `./harness agy-hook post-tool-use` é acionado
Então FormattingService.format_file("src/a.py") é chamado
E imprime {} no stdout.

Dado um payload de Stop qualquer
Quando `./harness agy-hook stop` é acionado
Então as microdecisões são validadas e o índice recompilado
E imprime {} (sem "decision": "continue").

Dado que o harness.toml está corrompido ou o stdin é ilegível
Quando qualquer evento agy-hook é acionado
Então o stdout exigido por evento é emitido mesmo assim
E o processo encerra com exit 0.

Dado um projeto-alvo com active_harness = "antigravity"
Quando `./harness init <destino> --harness antigravity` roda
Então <destino>/.agents/hooks.json contém o named-hook `harness` com o caminho absoluto resolvido
E quaisquer outras chaves preexistentes do arquivo são preservadas.
```

## Prioridade (MoSCoW)

| Requisito                                  | MoSCoW | Justificativa                                                            |
| ------------------------------------------ | ------ | ------------------------------------------------------------------------ |
| Não-bloqueio sob qualquer falha (RN-03)    | Must   | Salvaguarda crítica; o gancho jamais pode travar o laço do agente.       |
| O core não conhece o harness (RN-N5)       | Must   | Mantém a Strategy multi-harness sem `if`s nos serviços de domínio.       |
| Captura + formatação por edição (RF-01/02) | Must   | Preserva a granularidade por-edição sem acoplar ao `transcript.jsonl`.   |
| Materialização por merge (RF-04)           | Must   | Footprint zero e idempotência; preserva ganchos de terceiros.            |
| Indexação de decisões no Stop (RF-03)      | Should | Equivale a `harness decisions`; mantém o índice de microdecisões fresco. |

## Rastreabilidade de Código

| Arquivo                               | Função / Classe                                                       | Cobertura |
| ------------------------------------- | --------------------------------------------------------------------- | --------- |
| `adapters/antigravity/hook_bridge.py` | `AntigravityHookBridge.handle` e handlers por evento                  | 🟢        |
| `core/install/antigravity_hooks.py`   | `materialize_hooks_json`, `_resolve_harness_block`, `_read_existing`  | 🟢        |
| `core/install/harness_profiles.py`    | `AntigravityProfile.hooks_block` / `apply_instructions`               | 🟢        |
| `src/main.py`                         | Subcomando `agy-hook` (instanciação na borda, fallback pré-computado) | 🟢        |
| `src/core/bootstrap/init_service.py`  | `initialize_project` / `upgrade_project` (passo de materialização)    | 🟢        |

## Premissas e Lacunas

- 🟡 **Runtime do Antigravity não verificável localmente:** a estabilidade do `stepIdx` entre `PreToolUse` e `PostToolUse`, e o acesso de leitura ao `artifactDirectoryPath`, são premissas do contrato documentado, cobertas por testes de fixtures, não por integração real.
- 🟢 **Caminho absoluto no `command`:** se o repositório for movido sem rodar `upgrade`, os ganchos apontam para o caminho antigo. Mitigado pelo `upgrade` (reescreve o `hooks.json`).
