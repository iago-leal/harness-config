# Investigation: Índice de microdecisões leve com consulta sob demanda

> Identificador: `028-indice-decisoes-sob-demanda`
> Data: `2026-08-11`

## 1. Diagnóstico do problema

A queixa original ("o índice ficou muito inchado e a consulta gastava muito token") tem duas componentes distintas, e só uma delas é o custo dominante:

1. **Crescimento do índice.** Cada ficha nova adiciona 1-2 linhas ao `.harness/microdecisoes.md` (título + sublinha de backlinks). Com 20 fichas, o índice tem 45 linhas / ~3,1 KB. O crescimento é linear e inevitável: é a natureza de um acervo append-only.
2. **Reinjeção integral a cada SessionStart.** A feature 021 (`build_decisions_appendix`, `core/session/resume_context.py`) injeta o índice COMPLETO no contexto de toda sessão via `cmd resume`, gated por `active_harness == "claude"` e `session.inject_decisions_index` (default `True`). Este é o multiplicador real: um índice de N linhas custa N linhas POR SESSÃO, para sempre, mesmo quando a sessão não toca em decisão nenhuma.

O projeto citado como precedente sofreu exatamente a combinação: acervo grande × injeção integral × sessões frequentes. Atacar só o tamanho do arquivo não resolveria; atacar só a injeção perderia a âncora de busca que a 021 instituiu de propósito (RN-N12: o agente precisa saber que o acervo existe antes de fazer buscas amplas).

## 2. Alternativas avaliadas

| Alternativa | Avaliação | Veredito |
|-------------|-----------|----------|
| **A. Particionar o índice em vários arquivos** (por tema, por faixa de ID, por vigência) | Multiplica os artefatos derivados e os pontos de consulta; o grafo de relações cruza partições (backlinks apontariam para arquivos diferentes); o agente precisaria de heurística para saber QUAL partição abrir. Complexidade estrutural alta para um ganho que a visão compacta entrega mais barato. | ❌ descartada (confirmada no clarify, D1b: arquivo único) |
| **B. Comprimir o índice atual** (remover backlinks, abreviar títulos) | Reduziria o peso por linha, mas mantém o custo linear por sessão e sacrifica os backlinks, que são a materialização do grafo (RN-N13/N14). Perde informação sem mudar a curva. | ❌ descartada |
| **C. Desligar a injeção** (`inject_decisions_index = false`) | Botão que já existe. Zera o custo, mas zera também a orientação: agente novo não descobre o acervo. É o extremo oposto do problema, não a solução. | ❌ descartada como default (o botão continua existindo para quem quiser) |
| **D. Visão compacta injetada + índice completo sob demanda** | Injeção vira O(K) fixo (K=10 default) em vez de O(N); o índice completo continua existindo, num arquivo único, a um passo de leitura; a guidance (bloco injetado + trecho no CLAUDE.md) ensina o agente a consultá-lo quando precisar. Custo por sessão fica CONSTANTE, independente do crescimento do acervo. | ✅ escolhida |
| **E. Filtrar por vigência** (só fichas `ativo` na visão) | O campo `estado:` não é confiável: MD-0016 está supersedida pela MD-0018 e segue `estado: ativo`; derivar vigência das relações `substitui` exigiria semântica nova no serviço. Recência é proxy suficiente e determinística. | ❌ descartada (registrada como evolução possível) |

## 3. Padrões do próprio projeto aplicados

- **Artefato derivado determinístico (features 026/027):** sem timestamp, sem valor volátil, escrita atômica, regravação só quando o conteúdo muda. A visão compacta nasce dentro desse padrão, e a escrita do índice completo é retrofitada nele (hoje `compile_index` regrava incondicionalmente a cada Stop).
- **Migração autoresolvente (features 016/023):** nenhum código de migração; o `resume` cai no comportamento antigo (índice integral, com aviso em stderr) até a primeira reindexação criar a visão compacta.
- **Fonte única (RN-N36, feature 020/021):** a mudança inteira propaga pelo shim; nenhum hook materializado é regravado.
- **Trecho de guidance à maneira do Reversa (decisão do clarify, D3):** escrita única na instalação, delimitada por marcador estável, idempotente por detecção do marcador; o `upgrade` nunca toca.

## 4. Fontes consultadas

- `.harness/harness-core/src/core/decisions/service.py` — `compile_index` (regravação incondicional, extração de título, `inverso_verbos`)
- `.harness/harness-core/src/core/session/resume_context.py` — `build_decisions_appendix` (injeção integral da 021)
- `.harness/harness-core/src/main.py` — ramos `decisions` e `cmd resume`
- `.harness/harness-core/src/adapters/antigravity/hook_bridge.py` — reindexação de fim de turno (usa o índice só para derivar, nunca injeta)
- `.harness/harness-core/src/core/domain/config.py` — `DecisionsSection`, `SessionSection.inject_decisions_index`
- `_reversa_sdd/microdecisoes/requirements.md` — RN-N11..N14, RN-N43..N47
- `_reversa_sdd/architecture.md` §2 — unit `microdecisoes/`
- `.harness/microdecisoes.md` — estado real do índice (20 fichas, 45 linhas, 3.105 bytes)

## 5. Nenhuma dependência externa nova

A feature usa apenas stdlib e os serviços existentes do core. Nada a instalar, nada a pinar.
