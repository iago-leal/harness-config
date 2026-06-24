# ADR 0011: Reinjeção e instalação multi-harness por Strategy (Sink de sessão e Perfil de instalação)

* **Status:** Aceito
* **Data:** 2026-06-23 (decidido) / features 003 e 004 (implementado)
* **Contexto Técnico:** Módulos `core/session/sinks.py` e `core/install/harness_profiles.py` — commits `b2adcf4` (install-prompt) e `e1a2f75` (sessão)
* **Escala de Confiança:** 🟢 CONFIRMADO
* **Decisões relacionadas:** MD-0003 (refina MD-0002)

## Contexto e Problema

O mantenedor usa **três** harnesses — Claude Code, Gemini CLI e Antigravity (`agy`). Dois pontos do core dependem do mecanismo específico de cada agente: (1) a reinjeção do estado de sessão no boot e (2) a geração do bloco de ganchos para instalação. Esses mecanismos divergem: Claude e Gemini compartilham o envelope `hookSpecificOutput.additionalContext` num hook `SessionStart`; o Antigravity **não** expõe hook que injete stdout no contexto (os hooks dele decidem allow/deny/ask de tool calls), exigindo projeção em arquivo estático relido a cada boot. Espalhar `if active_harness == ...` pelo core violaria a neutralidade do domínio e acoplaria a regra de negócio aos harnesses.

## Decisão

Manter o **core agnóstico a harness** e isolar a variação por harness em **Strategies na borda**, selecionadas pelo `active_harness` do `harness.toml`:

1. **Sink de sessão (`SessionSink`, feature 004):** `core/commands`/`serializer` produzem texto puro; `get_sink(active_harness, fs)` resolve a estratégia de entrega. Duas famílias — `HookContextSink` (Claude e Gemini, mesmo envelope `additionalContext`, truncado em `MAX_CHARS = 10000`) e `FileProjectionSink` (Antigravity, projeta em `.agents/rules/estado-sessao.md`). A fonte canônica `.harness/estado-da-sessao.md` permanece única; a projeção do Antigravity é derivada dela.
2. **Perfil de instalação (`HarnessProfile`, feature 003):** `ABC` com `hooks_block()` + `apply_instructions()`, concretas `ClaudeProfile`/`GeminiProfile`/`AntigravityProfile`. `get_profile(name)` resolve via dict; reusado pelo `install-prompt`.
3. **Falha barulhenta:** harness desconhecido em `get_sink`/`get_profile` levanta `ValueError` — nunca um padrão silencioso.

## Alternativas Consideradas

* **Só Claude, com Gemini/Antigravity como follow-up:** recusada pelo mantenedor — paridade imediata de retomada preferida; cobrir Gemini é incremento barato sobre o Claude (mesmo envelope).
* **Um mecanismo único para os três:** impossível — o Antigravity não injeta stdout no contexto; forçar caminho único quebraria.
* **Antigravity via MCP resource servindo o estado:** mais "vivo", mas exige o agente decidir chamar (não é injeção garantida no boot) e adiciona um servidor a manter; preterido pela projeção em arquivo, mais simples e versionável.
* **`if`s espalhados no core (sem Strategy):** descartado — acoplaria o domínio aos harnesses e violaria RN-N5 ("o core não conhece o harness"). A Strategy, antes YAGNI com um só consumidor, justifica-se com três consumidores reais.

## Consequências

* **Positivas:**
  * Paridade de retomada e de instalação entre os três harnesses, com o core puro.
  * Novo harness = nova Strategy na borda, sem tocar a regra de negócio (ponto de extensão explícito).
  * Reuso do mesmo padrão Strategy entre sessão (sink) e instalação (profile).
* **Negativas:**
  * Mecanismo do Antigravity ainda **não confirmado** na prática — o `AntigravityProfile.hooks_block()` emite aviso de "mecanismo não confirmado", e o caminho de atualização de âncora no boot do agy segue como pendência (MD-0003).
  * Pré-requisito do Gemini (≥ 0.25 para hooks `SessionStart`) precisa ser checado no ambiente.
