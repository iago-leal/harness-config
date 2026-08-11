# Legacy Impact: Índice de microdecisões leve com consulta sob demanda

> Identificador: `028-indice-decisoes-sob-demanda`
> Data: `2026-08-11`
> Base da análise: `_reversa_sdd/architecture.md` e `_reversa_sdd/domain.md` (reconciliação de 2026-07-15; features 024-027 ainda não reconciliadas na extração)

## Arquivos afetados

| Arquivo afetado | Componente (`_reversa_sdd/architecture.md`) | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `.harness/harness-core/src/core/domain/config.py` | Config Pydantic (`DecisionsSection`) | delta-de-dados | LOW | Dois campos novos com default (`compact_file`, `compact_index_size`, `ge=0`); nenhuma chave existente muda; toml antigo continua válido. Inclui o bump 2.5.0 → 2.6.0. |
| `.harness/harness-core/src/core/decisions/service.py` | `DecisionService` (core/decisions) | regra-nova | MEDIUM | Novo método `compile_compact_view` derivado na mesma passada do índice; extração de título fatorada em `_extract_title` (ponto único); `_write_if_changed` aplicado às duas escritas (WOWC). `compile_index` preserva formato byte a byte. |
| `.harness/harness-core/src/core/session/resume_context.py` | `resume_context` (core/session) | regra-alterada | HIGH | `build_decisions_appendix` ganha o parâmetro `compact_file` e passa a preferir a visão compacta, com fallback para o índice integral. Altera o CONTEÚDO da injeção do SessionStart regido pela RN-N41. Pureza e contrato "flag false → vazio" preservados. |
| `.harness/harness-core/src/main.py` | Borda CLI (ramos `decisions`, `cmd resume`, `agy-hook`) | regra-alterada | MEDIUM | Ramo `decisions` deriva as duas visões e emite linha informativa nova; ramo `cmd resume` passa `compact_file` e ganha o aviso de fallback em stderr; ramo `agy-hook` repassa os dois valores novos de config à ponte. Exit codes intocados. |
| `.harness/harness-core/src/adapters/antigravity/hook_bridge.py` | `AntigravityHookBridge` (driver de borda) | regra-alterada | MEDIUM | Construtor ganha `decisions_compact_file`/`decisions_compact_size` (com defaults, compatível); `_handle_stop` deriva a visão compacta após o índice. Garantia não-bloqueante (RN-N26) intocada: tudo sob `_safe`. |
| `.harness/harness-core/src/core/bootstrap/init_service.py` | `InitializationService` (bootstrap) | regra-nova | MEDIUM | `init` grava trecho de guidance idempotente por marcador `<!-- harness:decisoes -->` no arquivo da engine (`CLAUDE.md`/`AGENTS.md`/`GEMINI.md`), escrita única; `upgrade` não toca. Primeiro caso de o init escrever em arquivo de guidance do usuário — mitigado por append preservador e detecção de marcador. |
| `.harness/harness-core/tests/{test_config,test_decisions,test_resume_context,test_init,test_antigravity_hook_bridge}.py` | Suíte de testes | componente-novo | LOW | 17 testes novos cobrindo composição, K=0, determinismo, WOWC, precedência/fallback do resume, idempotência do guidance e paridade da ponte. Suíte total: 389 verdes. |

## Diff conceitual por componente

**`DecisionService`.** O serviço passa a produzir dois artefatos derivados na mesma passada: o índice consolidado (inalterado em formato) e a visão compacta (`# Decisões recentes`, três linhas de orientação, `Total: N ficha(s)`, K mais recentes por ID decrescente, só títulos). A validação de integridade continua precedendo qualquer derivação, de modo que ficha inválida aborta as duas visões juntas: não há estado em que uma esteja atualizada e a outra não. A extração de título, antes inline no `compile_index`, virou método compartilhado, eliminando a possibilidade de as duas visões divergirem de formato.

**`resume_context`.** A precedência inverte o peso da injeção: o que era O(acervo) vira O(K). O índice integral permanece no disco como fonte de consulta sob demanda e como fallback autoresolvente na janela entre um upgrade e a primeira reindexação. A função continua pura; os avisos moram na borda.

**Bordas (CLI e Antigravity).** Ambas derivam a visão compacta pela mesma chamada de serviço, preservando a simetria dos drivers do hexágono (RN-N5). Nenhuma injeção nova na ponte Antigravity: ela só deriva.

**`InitializationService`.** O init passa a semear o protocolo de consulta (guidance) além do mecanismo (arquivos e hooks). A escrita é única por instalação, detectada pelo marcador; o conteúdo pertence ao usuário depois disso.

## Preservadas (regras 🟢 do `_reversa_sdd/domain.md`)

- **RN-N4** (falha barulhenta, não-bloqueante nas bordas de hook): fallback do resume avisa em stderr e segue; `agy-hook` continua sob blindagem total.
- **RN-N5** (core agnóstico ao harness): o gate por harness segue na borda; serviço e composição puros.
- **RN-N8** (teto de contexto na reinjeção): o apêndice continua cedendo sob truncamento; com a visão compacta, a pressão sobre o teto diminui.
- **RN-N11** (caminhos de decisão via config): os dois campos novos seguem o padrão da seção `[decisions]`.
- **RN-N12** (índice derivado, não editado à mão): estendida à visão compacta, que declara a mesma natureza no próprio cabeçalho.
- **RN-N13** (integridade do grafo): validação inalterada, anterior a qualquer derivação.
- **RN-N26** (Stop do Antigravity nunca bloqueia): derivação adicional dentro de `_safe`, stdout por evento intocado.
- **RN-N42..N47** (gate de registro e advisory): intocadas; o `--gate` continua com stdout vazio e exit 0.

## Modificadas

- **RN-N41** (apêndice do índice de decisões no resume, Claude-first) — 🟢 alterada: o apêndice injetado deixa de ser o índice integral e passa a ser a visão compacta (`decisions.compact_file`, cabeçalho `## Decisões recentes (índice completo sob demanda)`); o índice integral vira fallback com aviso em stderr quando a compacta ainda não foi derivada. Gate por harness, opt-out `inject_decisions_index`, precedência do estado e comportamento não-bloqueante permanecem.
