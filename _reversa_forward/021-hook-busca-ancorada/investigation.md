# Investigation: Hook de busca ancorada no estado da sessão e no índice de decisões

> Identificador: `021-hook-busca-ancorada`
> Data: `2026-07-05`

## 1. Pergunta de fundo

Como fazer o agente consultar primeiro os artefatos condensados do projeto (estado + índice de decisões) antes de varrer o repositório, **poupando tokens**, dado que não existe um evento de gancho correspondente a "o agente decidiu buscar"? Os eventos de ciclo de vida disponíveis são `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse` e `Stop`.

## 2. O que já existe no legado (leitura de código)

- **`SessionStart → ./harness cmd resume`** (`.claude/settings.json`; `main.py:353-355`): já reinjeta a narrativa do estado no contexto via `HookContextSink.emit`, montando `hookSpecificOutput.additionalContext` (`sinks.py:30-43`). É o trilho natural a estender.
- **`HookContextSink.MAX_CHARS = 10000`** (`sinks.py:28`): trunca o `additionalContext` com aviso. Qualquer texto que passe pelo sink herda a salvaguarda — não é preciso reimplementar truncamento.
- **`microdecisoes.md`** é o **índice derivado** do grafo de decisões (títulos + backlinks), compilado por `DecisionService.compile_index` (`decisions/service.py:82-147`) e regenerado pelo hook `Stop → ./harness decisions`. É um arquivo estático em disco: a feature só precisa **lê-lo**, não recompilá-lo.
- **`get_sink(active_harness, fs)`** (`sinks.py:69-77`): a seleção do mecanismo de entrega por harness já vive na borda (RN-N5). Um gate por harness na fiação do apêndice é coerente com esse padrão.
- **`execute_command`** (`commands/service.py:30`) é compartilhado por CLI e MCP; alterar sua assinatura propagaria risco ao driver MCP — a evitar.

## 3. Alternativas de mecanismo avaliadas

| Alt. | Descrição | Custo de tokens | Veredito |
|------|-----------|-----------------|----------|
| A — estender o resume/`SessionStart` | Uma injeção por sessão, anexando o índice ao estado já reinjetado | Baixo (1×/sessão) | **Escolhida** (D-01). Reusa sink + teto; menor custo; menor superfície de código |
| B — novo gancho `UserPromptSubmit` | Injeta estado + índice a cada mensagem do usuário | Médio (N× por sessão) | Descartada — repete conteúdo já em contexto; custo cresce com o diálogo |
| C — novo gancho `PreToolUse` sobre Grep/Glob | Injeta um ponteiro antes de cada busca | Alto (muitas vezes) | Descartada — dispara demais e infla tokens, na contramão do objetivo |
| D — diretiva de comportamento (CLAUDE.md) | Instrução textual "consulte os âncoras antes de buscar" | Nulo estrutural | Descartada como mecanismo primário — não-determinística, depende da adesão do agente; pode complementar, não substituir |

## 4. Sub-decisões de desenho

- **O que injetar (D-02):** o índice `microdecisoes.md` (~1,7 KB), não a pasta `decisoes/` (~31 KB). Medição factual de 2026-07-05: injetar a pasta estouraria o teto de 10 KB (truncamento cego) e sobrecarregaria o contexto — o oposto do objetivo. O índice traz os ponteiros para o agente abrir uma ficha `MD-NNNN` específica sob demanda.
- **Onde compor (D-03):** função pura no core (`session/resume_context.py`), testável isoladamente; a borda apenas fia. `execute_command` fica intocada.
- **Gate por harness (D-04):** `active_harness == "claude"` neste corte (Claude-first). Gemini usa o mesmo `HookContextSink` — estendê-lo é trocar o gate por "família hook", trivial. Antigravity é família arquivo (`FileProjectionSink`, sem teto) e exige desenho próprio da projeção; fica para iteração posterior.
- **Ordem e truncamento (D-06/D-07):** estado antes do índice, para que o corte no teto sacrifique o índice antes da narrativa.

## 5. Padrões aplicáveis

- **Reuso de salvaguarda existente** em vez de reimplementá-la (teto do `HookContextSink`).
- **Seleção por harness na borda** (espelha `get_sink`), preservando o core agnóstico (RN-N5).
- **Não-bloqueio** (RN-03/RN-N4): ausência/ilegibilidade do índice degrada para "só estado" com aviso em `stderr`, nunca para falha do boot.
- **Configuração tipada única** (RN-N16): liga/desliga e caminhos por `harness.toml`.

## 6. Fontes

- Código do core lido nesta sessão: `sinks.py`, `commands/service.py`, `config.py`, `main.py`, `decisions/service.py`.
- Extração reversa: `_reversa_sdd/architecture.md#4`, `_reversa_sdd/domain.md#2.3` (RN-07/N1/N5/N6/N8), `#2.5` (RN-N11/N12), `#2.8` (RN-N16/N17).
- Decisões do mantenedor: `/reversa-clarify` Sessão 2026-07-05 (mecanismo, escopo Claude-first, default ligado).
