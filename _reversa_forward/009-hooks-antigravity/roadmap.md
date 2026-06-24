# Roadmap: Ganchos de ciclo de vida para o Antigravity

> Identificador: `009-hooks-antigravity`
> Data: `2026-06-24`
> Requirements: `_reversa_forward/009-hooks-antigravity/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

O harness já resolve mecanismos por engine via duas Strategies — `get_sink` (`session/sinks.py`) e `get_profile` (`install/harness_profiles.py`) —, mas o `AntigravityProfile` é só um placeholder de texto. A abordagem é um delta em três frentes, sem reescrever nada do legado. Primeiro, preencher o `AntigravityProfile` para emitir um `hooks.json` real. Segundo — e este é o núcleo —, adicionar um **terceiro driver de entrada** em `src/adapters/`, simétrico à CLI (`main.py`) e ao servidor MCP (`adapters/mcp/server.py`): um adaptador que fala o protocolo de ganchos do Antigravity (stdin JSON, stdout JSON por evento) e **delega aos serviços de domínio já existentes** (`FormattingService`, `DecisionService`), deixando o core agnóstico ao harness. Terceiro, ensinar o `init_service` e o `template.md` de instalação a materializar/documentar o `hooks.json` em `.agents/`, removendo a suposição chumbada de `.claude/`. A reinjeção de estado permanece com o `FileProjectionSink` (decidido em `/reversa-clarify`).

## 2. Princípios aplicados

> Não há `.reversa/principles.md` neste projeto. Aplico os princípios estruturais já registrados nos ADRs do `_reversa_sdd/` e as prioridades declaradas pelo mantenedor (longevidade, baixo acoplamento, alta coesão, OOP, TDD).

| Princípio                                           | Como a feature se relaciona                                                                       | Status   |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------- | -------- |
| Arquitetura hexagonal (ADR 0006)                    | O protocolo do Antigravity entra como driver no anel de adaptadores; o domínio não muda           | respeita |
| Strategy multi-harness sem `if`s no core (ADR 0011) | A seleção por harness fica em `harness_profiles.py`/`sinks.py`/novo adaptador, nunca nos serviços | respeita |
| Footprint global zero (MD-0005 / BR-MIGRAR-007)     | `hooks.json` é escrito só dentro do repositório-alvo (`.agents/`), nunca em `~/.gemini/config/`   | respeita |
| Não-bloqueante e erro barulhento (ADR 0002)         | Ganchos de formatação/decisão nunca emitem `decision: "deny"`; falha é logada, não abortada       | respeita |
| Reprodutibilidade (ADR 0015)                        | Nenhuma dependência nova: o adaptador usa só `json`/`sys` da stdlib                               | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                                                                                     | Justificativa                                                                                                                                                                          | Alternativas descartadas                                                                                                                                                                       | Confidência |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| D-01 | Preencher `AntigravityProfile.hooks_block()` com um `hooks.json` real (named-hook `harness` cobrindo `PostToolUse`, `Stop` e — se D-03 confirmar — `PreToolUse`)                                                                            | O contrato `hooks.json` está documentado oficialmente; o placeholder deixa de ser necessário                                                                                           | Manter placeholder até "confirmar em produção" (a doc já é a confirmação)                                                                                                                      | 🟢          |
| D-02 | Adicionar um **terceiro driver de entrada** (`src/adapters/antigravity/hook_bridge.py`), invocado por subcomando fino `./harness agy-hook <evento>`, que traduz o protocolo do Antigravity e delega a `FormattingService`/`DecisionService` | Protocolo de terceiro pertence ao anel de adaptadores (hexágono); reusa os serviços de domínio sem duplicar lógica; mantém `resolve_format_target` (schema Claude) intacto             | (a) estender `resolve_format_target` para dois schemas → baixa coesão; (b) script shell externo → fora do core testável; (c) ramificar serviços por harness → `if`s espalhados (anti-ADR-0011) | 🟢          |
| D-03 | Recuperar o caminho do arquivo editado por **captura no `PreToolUse` + formatação no `PostToolUse`**, usando `artifactDirectoryPath` (do payload) como scratch para o mapa `stepIdx → TargetFile`                                           | Usa apenas campos documentados do contrato; preserva a granularidade por-edição da RN-02; evita parsear o `transcript.jsonl` (formato interno frágil)                                  | (a) parsear `transcriptPath` no `stepIdx` → acoplamento a formato não documentado; (b) formatar diff do git no `Stop` → granularidade grosseira, desvia da RN-02 (mantida como fallback)       | 🟡          |
| D-04 | Tornar o `template.md` de instalação e os `apply_instructions` harness-aware (placeholder de escopo por perfil), substituindo `.claude/settings.json` chumbado                                                                              | Sem isso o prompt de instalação do Antigravity instruiria o caminho errado                                                                                                             | Deixar o texto Claude-cêntrico e corrigir à mão (frágil, contradiz a Strategy)                                                                                                                 | 🟢          |
| D-05 | Estender o `init_service` para **materializar `.agents/hooks.json`** quando `active_harness == "antigravity"`, com merge por named-hook (preserva chaves de terceiros)                                                                      | `hooks.json` é arquivo dedicado (ao contrário do `.claude/settings.json`, que mescla com outras chaves), seguro de escrever no `init`; satisfaz RF-04 e melhora a UX vs colagem manual | Aplicar só via `install-prompt` colável (mantém simetria com o Claude, mas não cumpre RF-04)                                                                                                   | 🟡          |
| D-06 | O `command` do `hooks.json` aponta para o `./harness` do projeto por **caminho absoluto** resolvido no `init` (o `upgrade` reescreve se o repo mover)                                                                                       | O Antigravity expõe `workspacePaths` no payload, não uma variável de shell como `${CLAUDE_PROJECT_DIR}`; caminho absoluto é determinístico e footprint-safe                            | `${CLAUDE_PROJECT_DIR}` (não existe no Antigravity); caminho relativo (depende do cwd do gancho, indefinido na doc)                                                                            | 🟡          |

## 4. Premissas

> Nenhuma premissa herdada de `[DÚVIDA]`: as três dúvidas foram resolvidas em `/reversa-clarify`. Restam premissas técnicas sobre o runtime do Antigravity, não verificáveis sem o agente real (ver Riscos).

| Premissa                                                                                                                                               | Origem (`requirements.md` seção) | Risco se errada                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------- | ----------------------------------------------------------------------------- |
| O `PreToolUse` de uma tool de escrita expõe `toolCall.args.TargetFile` com o caminho do arquivo, e o `stepIdx` casa com o `PostToolUse` correspondente | §4 RN-02, §10 (diferido)         | D-03 cai para o fallback Stop+git-diff                                        |
| O `command` do gancho roda com acesso de leitura ao `artifactDirectoryPath` informado no payload                                                       | §5 RF-05                         | scratch do mapa precisa de outro diretório (ex.: `/tmp` por `conversationId`) |
| O Antigravity tolera, no `PostToolUse`, stdout `{}` e exit 0 sem interromper o laço                                                                    | §6 RNF robustez                  | revisar contrato de saída por evento                                          |

## 5. Delta arquitetural

| Componente                             | Arquivo de origem no legado                                                       | Tipo de mudança   | Resumo                                                                                                                       |
| -------------------------------------- | --------------------------------------------------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `AntigravityProfile`                   | `_reversa_sdd/architecture.md#6-adrs-pertinentes` (`install/harness_profiles.py`) | regra-alterada    | `hooks_block()`/`apply_instructions()` deixam de ser placeholder e passam a emitir `hooks.json` + instruções para `.agents/` |
| Adaptador Antigravity (novo)           | `_reversa_sdd/architecture.md#1-estilo-de-arquitetura` (anel de adaptadores)      | componente-novo   | Terceiro driver de entrada que traduz o protocolo de ganchos e delega aos serviços de domínio                                |
| `main.py` (CLI)                        | `_reversa_sdd/architecture.md#2-modelagem-c4`                                     | contrato-alterado | Novo subcomando fino `agy-hook <evento>` que instancia o adaptador                                                           |
| `InitializationService`                | `_reversa_sdd/inventory.md#núcleo-python` (`bootstrap/init_service.py`)           | regra-alterada    | `initialize_project` passa a escrever `.agents/hooks.json` quando o harness é `antigravity`                                  |
| `template.md` de instalação            | `_reversa_sdd/architecture.md#4-integrações-de-borda` (`install/template.md`)     | contrato-alterado | Escopo de aplicação dos ganchos vira por-perfil (remove `.claude/` chumbado)                                                 |
| `FormattingService`, `DecisionService` | `_reversa_sdd/architecture.md#1-estilo-de-arquitetura`                            | **inalterado**    | Reusados pelo adaptador; agnósticos ao harness por design                                                                    |
| `FileProjectionSink`                   | `_reversa_sdd/adrs/0011-...md`                                                    | **inalterado**    | Continua sendo o mecanismo único de reinjeção de estado no Antigravity (RN-05)                                               |

## 6. Delta no modelo de dados

- Resumo das mudanças: não há banco relacional. O delta é em arquivos de configuração: nasce o `.agents/hooks.json` (novo artefato versionável no projeto-alvo) e um arquivo-scratch efêmero `stepIdx → TargetFile` sob `artifactDirectoryPath`. O `harness.toml` **não muda** (o `active_harness = "antigravity"` já é suportado).
- Detalhe completo em: `_reversa_forward/009-hooks-antigravity/data-delta.md`

## 7. Delta de contratos externos

| Contrato                                                           | Tipo               | Arquivo de detalhe                                                         |
| ------------------------------------------------------------------ | ------------------ | -------------------------------------------------------------------------- |
| Protocolo de ganchos do Antigravity (stdin/stdout JSON por evento) | arquivo / processo | `_reversa_forward/009-hooks-antigravity/interfaces/antigravity-hook-io.md` |

## 8. Plano de migração

1. Preencher `AntigravityProfile` (D-01) com testes de `hooks_block()` parseável e `apply_instructions()` sem o aviso de placeholder.
2. Criar o adaptador de borda e seu subcomando `agy-hook` (D-02), com testes que injetam payloads de exemplo no stdin e asseguram (i) a chamada ao serviço de domínio certo e (ii) o stdout JSON exigido por evento.
3. Implementar a recuperação do caminho (D-03) por captura `PreToolUse` + formatação `PostToolUse`; manter o fallback Stop+git-diff atrás do mesmo adaptador.
4. Estender `init_service` (D-05/D-06) para escrever `.agents/hooks.json` com caminho absoluto e merge por named-hook; teste com `--harness antigravity` análogo ao `test_init.py` existente.
5. Tornar o `template.md`/`apply_instructions` harness-aware (D-04).
6. Rodar a suíte pytest completa e confirmar que os caminhos do Claude/Gemini permanecem verdes (sem regressão).

## 9. Riscos e mitigações

| Risco                                                                                | Impacto | Probabilidade | Mitigação                                                                                     |
| ------------------------------------------------------------------------------------ | ------- | ------------- | --------------------------------------------------------------------------------------------- |
| O runtime real do Antigravity diverge da doc (campos/tempo de vida do `stepIdx`)     | alto    | médio         | Adaptador isola o contrato; teste por payloads-fixture; fallback Stop+git-diff                |
| `command` por caminho absoluto quebra se o repo for movido                           | médio   | baixo         | `./harness upgrade` reescreve o `hooks.json`; documentar no onboarding                        |
| Escrever `.agents/hooks.json` no `init` sobrescreve hooks do usuário                 | médio   | baixo         | Merge por named-hook `harness`, preservando chaves de terceiros; idempotência                 |
| Assimetria de UX entre Claude (colagem manual) e Antigravity (auto-escrita) confunde | baixo   | médio         | Registrar a justificativa (arquivo dedicado vs merge) no `apply_instructions` e no onboarding |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `AntigravityProfile.hooks_block()` retorna JSON parseável; nenhum teste exibe o aviso de placeholder
- [ ] Adaptador cobre `PreToolUse`/`PostToolUse`/`Stop` com testes de payload-fixture (entrada e stdout)
- [ ] `init --harness antigravity` materializa `.agents/hooks.json` válido sem escrever fora do repo (teste de footprint verde)
- [ ] Suíte pytest verde, sem regressão nos caminhos Claude/Gemini
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-06-24 | Versão inicial gerada por `/reversa-plan` | reversa |
