# Requirements: Hook de busca ancorada no estado da sessão e no índice de decisões

> Identificador: `021-hook-busca-ancorada`
> Data: `2026-07-05`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

A reinjeção de contexto do boot — o hook `SessionStart → ./harness cmd resume`, que hoje entrega apenas a narrativa da sessão — passa a anexar também o índice `.harness/microdecisoes.md`, orientando o agente aos dois artefatos condensados do projeto (estado + índice de decisões) antes de qualquer varredura ampla do repositório. Como esses artefatos concentram o "estado" e o "porquê" num punhado de kilobytes, o agente se orienta gastando poucos tokens e ganha um ponto de partida dirigido, do qual aprofunda sob demanda em fichas `MD-NNNN` específicas. O ganho é medível: injeta-se o índice (~1,7 KB), não a pasta `decisoes/` inteira (~31 KB), que sobrecarregaria o contexto e estouraria o teto de reinjeção. Neste primeiro corte a entrega cobre o harness Claude; para o mantenedor intermitente, a retomada fica mais barata e rápida.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#4` (Integrações de Borda) | Os ganchos de ciclo de vida do agente (`SessionStart`/`PostToolUse`/`Stop` no Claude) já invocam o wrapper `./harness`; o `SessionStart` já está fiado ao `cmd resume`, que é o ponto de extensão desta feature | 🟢 |
| `_reversa_sdd/domain.md#2.3` (RN-N1, RN-07) | O estado da sessão é fonte canônica única em `.harness/estado-da-sessao.md`; o hook `SessionStart` → `./harness cmd resume` **já reinjeta** essa narrativa no contexto do agente ("Reinjeção de Contexto") | 🟢 |
| `_reversa_sdd/domain.md#2.3` (RN-N8) | O `HookContextSink` **trunca** o `additionalContext` em `MAX_CHARS = 10000` (teto do Claude), anexando aviso de truncamento — limite duro que o conteúdo injetado precisa respeitar | 🟢 |
| `_reversa_sdd/domain.md#2.5` (RN-N11, RN-N12) | `.harness/microdecisoes.md` é o índice **DERIVADO** do grafo de decisões (backlinks), regenerado pelo hook `Stop` → `./harness decisions`; os caminhos vêm de `[decisions]` no `harness.toml`, não são chumbados | 🟢 |
| `_reversa_sdd/domain.md#2.3` (RN-N5, RN-N6) | O core não conhece o harness: produz texto puro e a entrega varia por família — **hook** (Claude/Gemini, via stdout) ou **arquivo** (Antigravity). Preserva a extensão futura a outros harnesses como aditiva, sem ramificar o domínio | 🟢 |
| `_reversa_sdd/domain.md#2.2` (RN-03) e `#2.8` (RN-N17) | Não-bloqueio (todo gancho retorna 0, erro em `stderr`) e footprint global zero (escrita só dentro do repositório) são invariantes que a extensão herda | 🟢 |
| Medição factual (2026-07-05) | `estado-da-sessao.md` = 4,2 KB · `microdecisoes.md` = 1,7 KB · `decisoes/` (12 fichas) = 31,2 KB — o índice é ~18× menor que a pasta e cabe, somado ao estado (~5,9 KB), dentro do teto de 10 KB | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Agente de IA (Claude, neste corte) trabalhando no repo | Orientar-se sobre o estado e as decisões do projeto gastando o mínimo de tokens | Ao retomar a sessão, recebe estado + índice de decisões no contexto e só então decide se precisa buscar mais fundo |
| Mantenedor intermitente (iagoleal) | Retomar um projeto após semanas com custo baixo e resposta rápida | Reabre o projeto e o agente já parte do resumo condensado, sem varrer o repositório inteiro |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** Antes de recorrer a buscas amplas no repositório, o agente deve ser dirigido aos artefatos-âncora condensados — a narrativa da sessão e o índice de decisões — entregues na retomada da sessão. 🟢
   - Origem no legado: estende `_reversa_sdd/domain.md#2.3` (RN-07, "Reinjeção de Contexto")
   - Tipo: nova
2. **RN-02:** Os artefatos-âncora são o **estado da sessão** (`session.state_file`, default `.harness/estado-da-sessao.md`) e o **índice de decisões** (`decisions.index_file`, default `.harness/microdecisoes.md`) — nunca as fichas `decisoes/*.md` na íntegra, que ficam como aprofundamento sob demanda. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.5` (RN-N11 caminhos por config, RN-N12 índice derivado)
   - Tipo: nova
3. **RN-03:** O conteúdo injetado respeita o teto de reinjeção (`MAX_CHARS = 10000` no Claude); se estourar, trunca com aviso, como já faz o sink existente. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.3` (RN-N8)
   - Tipo: alterada (reusa a salvaguarda existente)
4. **RN-04:** A extensão preserva os invariantes do harness: não-bloqueante (retorna 0, erro em `stderr`), footprint global zero e core agnóstico ao harness (a entrega vive na borda, no sink). 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.2` (RN-03), `#2.8` (RN-N17), `#2.3` (RN-N5/RN-N6)
   - Tipo: nova
5. **RN-05:** O comportamento nasce **habilitado por padrão** e é desativável por um flag em `harness.toml`; os caminhos dos artefatos são herdados de `[decisions]`/`[session]`, sem literais chumbados. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.8` (RN-N16, via única tipada de configuração)
   - Tipo: nova · Decidido em `/reversa-clarify` (Sessão 2026-07-05)
6. **RN-06:** A entrega estende o fluxo do `cmd resume` disparado no `SessionStart` — **uma injeção por sessão**, no boot/retomada —, reusando o `HookContextSink`. Não há disparo por prompt nem por operação de busca. Escopo desta iteração: harness **Claude**. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.3` (RN-07/RN-N8, reinjeção via `HookContextSink`)
   - Tipo: nova · Decidido em `/reversa-clarify` (Sessão 2026-07-05)

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Na retomada da sessão (boot, hook `SessionStart`), o agente recebe no contexto o conteúdo condensado do estado da sessão e do índice de decisões, antes de qualquer varredura ampla do repositório | Must | Dado um repositório com `estado-da-sessao.md` e `microdecisoes.md`, quando a sessão inicia/retoma, então ambos os conteúdos chegam ao contexto do agente sem que nenhuma busca ampla tenha sido executada | 🟢 |
| RF-02 | O material entregue referente a decisões é o **índice** (`microdecisoes.md`), não o conjunto de fichas `decisoes/*.md` | Must | O conteúdo injetado corresponde ao índice derivado; o volume fica na casa de ~2 KB, não de ~30 KB | 🟢 |
| RF-03 | O volume total injetado respeita o teto de reinjeção e, ao excedê-lo, trunca com aviso explícito em vez de falhar | Must | Dado conteúdo somado acima de 10.000 caracteres, quando o gancho entrega, então o texto é truncado e um aviso de truncamento é anexado | 🟢 |
| RF-04 | O índice preserva os ponteiros que permitem ao agente abrir uma ficha `MD-NNNN` específica sob demanda | Should | A partir do conteúdo injetado, o agente consegue identificar e localizar uma ficha de decisão individual sem varredura ampla | 🟢 |
| RF-05 | O comportamento nasce habilitado por padrão, é desativável por flag no `harness.toml` e lê os caminhos dos artefatos da configuração tipada | Should | Numa instalação nova o conteúdo é injetado sem configuração extra; um flag de desativação suprime a injeção; alterar `decisions.index_file`/`session.state_file` muda a origem do conteúdo | 🟢 |
| RF-06 | O core permanece agnóstico ao harness (a entrega vive no sink da borda), de modo que estender a cobertura a Antigravity (família arquivo) e Gemini depois seja aditivo, sem ramificar domínio | Must | Nenhum serviço de domínio é ramificado por `active_harness`; a extensão a outro harness não exige alterar o core | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho / Custo | O conteúdo injetado deve poupar tokens frente à alternativa de varredura — ordem de ~6 KB (estado + índice), não ~30 KB+ (fichas) | Medição 2026-07-05; teto RN-N8 = 10 KB | 🟢 |
| Observabilidade | Não-bloqueante: retorna 0 sempre; qualquer erro (arquivo ausente, leitura falha) é logado em `stderr` e o agente prossegue | `_reversa_sdd/domain.md#2.2` RN-03, `#2.1` RN-02 | 🟢 |
| Segurança / Localidade | Footprint global zero: só lê/escreve dentro do repositório; não expõe conteúdo de fora das zonas canônicas | `_reversa_sdd/domain.md#2.8` RN-N17 | 🟢 |
| Compatibilidade | Não quebra os ganchos já configurados (`resume`/`format`/`decisions`); por estender o `resume`, o estado não é injetado em duplicidade | `_reversa_sdd/domain.md#2.3` (RN-07), `#2.11` (merge por-item) | 🟢 |
| Reprodutibilidade | Estado ausente ou malformado falha de forma barulhenta e explícita, nunca silenciosa | `_reversa_sdd/domain.md#2.3` RN-N4 | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Orientação barata na retomada da sessão
  Dado um repositório com ".harness/estado-da-sessao.md" e ".harness/microdecisoes.md" presentes
  Quando a sessão inicia (hook "SessionStart" → "./harness cmd resume")
  Então o agente recebe no contexto a narrativa do estado e o índice de decisões
  E o volume entregue referente a decisões é o índice (~2 KB), não as fichas (~30 KB)
  E nenhuma varredura ampla do repositório precede essa orientação

Cenário: Aprofundamento dirigido sob demanda
  Dado que o agente recebeu o índice de decisões
  Quando precisa do detalhe de uma decisão específica
  Então localiza e abre a ficha "MD-NNNN" correspondente pelo ponteiro do índice
  E não varre a pasta "decisoes/" inteira

Cenário: Teto de contexto respeitado
  Dado que estado + índice somados excedem 10.000 caracteres
  Quando o resume entrega o conteúdo
  Então o texto é truncado no teto
  E um aviso de truncamento é anexado

Cenário (negativo): Artefato ausente não trava o agente
  Dado um repositório sem ".harness/microdecisoes.md"
  Quando a sessão inicia
  Então a ausência é registrada em "stderr"
  E o resume retorna com sucesso (código 0), reinjetando ao menos o estado, sem interromper o agente

Cenário: Habilitado por padrão e desativável por configuração
  Dado uma instalação nova, sem configuração extra
  Quando a sessão inicia
  Então o conteúdo estado + índice é injetado
  E, com o flag de desativação ligado no "harness.toml", nenhum conteúdo de índice é injetado
  E alterar "decisions.index_file" muda a origem do índice entregue

Cenário: Entrega no Claude preservando o core agnóstico
  Dado um projeto configurado para o harness Claude
  Quando a sessão inicia
  Então o conteúdo chega pelo "additionalContext" do resume (família hook)
  E nenhum serviço de domínio é ramificado por "active_harness"
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 (orientar na retomada, antes de varrer) | Must | É o coração da feature e a razão de existir da extensão |
| RF-02 (índice, não fichas) | Must | Sem isso a feature contradiz o próprio objetivo (poupar tokens) |
| RF-03 (teto de contexto) | Must | Salvaguarda já exigida pelo legado; ignorá-la reintroduz truncamento cego |
| RF-06 (core agnóstico ao harness) | Must | Mantém a extensão futura a Antigravity/Gemini aditiva, sem ramificar domínio (RN-N5) |
| RF-04 (ponteiros p/ ficha) | Should | Preserva o acesso ao detalhe sem inflar o custo base |
| RF-05 (habilitado por padrão, desativável) | Should | Coerência com a via única tipada; permite desligar por projeto |
| RNF de custo/tokens | Must | É a métrica de sucesso declarada |
| Cobertura de entrega para Antigravity e Gemini | Won't (this time) | Adiada por decisão do `/reversa-clarify`; o corte é Claude-first. O core agnóstico (RF-06) deixa a extensão aditiva numa iteração posterior |

## 9. Esclarecimentos

### Sessão 2026-07-05

- **Q:** Como o gancho deve entregar os âncoras ao agente (mecanismo e frequência)?
  **R:** Estender o `cmd resume` disparado no `SessionStart`: na retomada, além do estado, anexa também o índice `microdecisoes.md`. Uma injeção por sessão, reusando o `HookContextSink`. (→ RN-06, RF-01)
- **Q:** Quais harnesses a feature deve cobrir neste primeiro corte?
  **R:** Só o Claude — é o harness ativo deste repo. Antigravity (família arquivo) e Gemini ficam para iteração posterior, mantida a agnosticidade do core. (→ RN-06, RF-06, MoSCoW "Won't this time")
- **Q:** Qual o estado padrão do gancho numa instalação nova?
  **R:** Ligado por padrão, desativável por flag no `harness.toml`. (→ RN-05, RF-05)

## 10. Lacunas

> Nenhuma lacuna bloqueante pendente — as três `[DÚVIDA]` da versão inicial foram resolvidas na Sessão 2026-07-05 de `/reversa-clarify`.
>
> **Escopo adiado (não bloqueante):** a entrega para Antigravity (projeção em arquivo, família `RN-N6`) e Gemini fica para uma iteração posterior, registrada como "Won't (this time)" na seção MoSCoW. O contrato exato dessa projeção será desenhado quando a cobertura entrar em escopo.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-07-05 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-07-05 | Refinamento do escopo: injetar o índice `microdecisoes.md` em vez da pasta `decisoes/` inteira, por decisão do mantenedor (evita sobrecarga de contexto) | reversa |
| 2026-07-05 | `/reversa-clarify` (Sessão 2026-07-05): mecanismo = estender o `cmd resume` no `SessionStart` (RN-06); escopo = Claude-first (RF-06, MoSCoW); default = ligado, desativável (RN-05/RF-05). As três `[DÚVIDA]` resolvidas | reversa |
