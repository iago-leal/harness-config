# Investigation: Ganchos de ciclo de vida para o Antigravity

> Identificador: `009-hooks-antigravity`
> Data: `2026-06-24`

## 1. Pesquisa de fundo

A documentação oficial do Antigravity (`https://antigravity.google/docs/hooks`) é uma SPA renderizada em JavaScript: o fetch simples só captura o título. O conteúdo foi obtido renderizando a página em browser headless (snapshot da árvore de acessibilidade) e cruzado com o README do SDK Python (`github.com/google-antigravity/antigravity-sdk-python`) e o tópico do fórum oficial.

Existem **dois** sistemas de ganchos no Antigravity, e a distinção é decisiva:

1. **Ganchos declarativos (`hooks.json`)** — comandos de shell disparados em pontos do laço de execução. É o análogo direto ao nosso `hooks.yml` e ao bloco `hooks` do Claude. **É o sistema-alvo desta feature.**
2. **Ganchos do SDK (Python)** — decoradores programáticos em três categorias (Inspect, read-only não-bloqueante; Decide, read-only bloqueante; Transform, modificador bloqueante), com contextos `SessionContext`/`TurnContext`. Fora de escopo: exigiria acoplar o harness ao SDK Python do Antigravity, contrariando o footprint enxuto.

### Contrato declarativo (resumo normativo)

- **Localização:** `hooks.json` em `.agents/` (workspace, por-projeto) ou `~/.gemini/config/` (global). Escolhemos `.agents/` por footprint zero.
- **Eventos:** `PreToolUse`, `PostToolUse` (com `matcher` regex sobre nome de tool), `PreInvocation`, `PostInvocation`, `Stop` (estes três ignoram `matcher`).
- **Handler:** `{ "type": "command", "command": "<shell>", "timeout": <int, default 30> }`; `enabled: false` desliga o named-hook.
- **I/O:** stdin JSON → stdout JSON, camelCase. Campos comuns a todos os eventos: `conversationId`, `workspacePaths`, `transcriptPath`, `artifactDirectoryPath`.
- **Tools de escrita (para o `matcher`):** `write_to_file`, `replace_file_content`, `multi_replace_file_content`.

Detalhe completo por evento em `interfaces/antigravity-hook-io.md`.

## 2. Alternativas avaliadas

### Onde mora a tradução de protocolo (decisão D-02)

| Alternativa                                                                           | Coesão/Acoplamento                                                   | Veredito      |
| ------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------- |
| Terceiro driver de entrada em `src/adapters/` que delega aos serviços de domínio      | Protocolo de terceiro no anel de adaptadores; domínio intacto        | **Escolhida** |
| Estender `resolve_format_target` (`main.py`) para dois schemas (Claude + Antigravity) | Mistura dois contratos numa função; baixa coesão                     | Descartada    |
| Script shell externo em `.agents/`                                                    | Fora do core Python testável; lógica de parse não coberta por pytest | Descartada    |
| Ramificar `FormattingService`/`DecisionService` por `active_harness`                  | `if`s de harness no domínio — exatamente o que o ADR 0011 elimina    | Descartada    |

### Como recuperar o caminho do arquivo editado (decisão D-03)

O `PostToolUse` do Antigravity entrega só `stepIdx` e `error` — **não** os argumentos da tool. Avaliado:

| Alternativa                                                                                                                      | Fragilidade                                                                  | Veredito                 |
| -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------ |
| Captura no `PreToolUse` (`toolCall.args.TargetFile`) → mapa `stepIdx→path` em `artifactDirectoryPath` → formata no `PostToolUse` | Usa só campos documentados; preserva granularidade por-edição                | **Escolhida (primária)** |
| Parsear `transcriptPath` no `stepIdx`                                                                                            | Depende do formato interno de `transcript.jsonl`, não documentado em detalhe | Descartada               |
| Formatar o diff do git no `Stop`                                                                                                 | Granularidade grosseira (1×/turno); desvia da RN-02                          | **Fallback**             |

### Escopo do MVP (decisão de `/reversa-clarify`)

O Antigravity não tem evento `SessionStart`. A reinjeção de estado já é resolvida pelo `FileProjectionSink` (`.agents/rules/estado-sessao.md`). Acrescentar um `PreInvocation` para reinjetar estado duplicaria a responsabilidade — recriaria a classe de divergência da dívida histórica T2. Por isso o MVP cobre só formatação (`PostToolUse`) e decisões (`Stop`).

## 3. Padrões aplicáveis

- **Ports & Adapters (hexágono):** o adaptador é um _driver_ de entrada, irmão da CLI e do servidor MCP. A regra "o core não conhece harness; a seleção por `active_harness` vive na borda" já está escrita em `session/sinks.py:9`.
- **Strategy:** `get_profile`/`get_sink` resolvem mecanismo por harness sem `if`s no domínio (ADR 0011). `AntigravityProfile` passa de placeholder a estratégia concreta.
- **Boundary translation:** envelopar entrada e saída no protocolo do agente, num único ponto trocável.

## 4. Fontes externas

- Documentação oficial de hooks do Antigravity — `https://antigravity.google/docs/hooks` (renderizada via browser headless nesta sessão).
- README de hooks do SDK Python — `github.com/google-antigravity/antigravity-sdk-python` (caminho `google/antigravity/hooks/`).
- Fórum oficial Google AI Developers — tópico "Hooks in Antigravity" (`discuss.ai.google.dev`).
- Legado interno: `_reversa_sdd/adrs/0011-reinjecao-multi-harness-strategy-sink.md`, `_reversa_sdd/adrs/0002-formatacao-automatica-post-tool-use.md`, `harness-core/src/core/install/harness_profiles.py`, `harness-core/src/core/session/sinks.py`.
