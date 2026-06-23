# Requirements: Estado de sessão unificado em `.harness/` com reinjeção de contexto

> Identificador: `004-estado-sessao-unificado`
> Data: `2026-06-23`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA
> Decisão de entrada (travada): `decisoes/MD-0002.md` — refina `decisoes/MD-0001.md`

## 1. Resumo executivo

A feature fecha a regressão aceita no `MD-0001`: hoje o `cmd resume` da CLI grava um `ESTADO-DA-SESSAO.md` pobre na raiz e **não reinjeta** o estado anterior no contexto do agente, enquanto a narrativa rica de retomada vive, à parte, em `.claude/ESTADO-DA-SESSAO.md`. A 004 unifica os dois num único artefato canônico e versionado `.harness/estado-da-sessao.md` (kebab ASCII, neutro a qualquer harness de IA), faz a CLI reinjetar a narrativa no `SessionStart`, e porta o `/encerrar-sessao` para a CLI como produtor dessa narrativa. Beneficiário direto: o mantenedor intermitente, que retoma o projeto após semanas sem ter de apontar o arquivo de estado à mão.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#1-estilo-de-arquitetura` | Arquitetura hexagonal; serviços recebem portas (`FileSystemPort`, `GitPort`) por injeção — o `CommandService` é o ponto de extensão natural | 🟢 |
| `_reversa_sdd/domain.md#2.3-tomada-de-decisão-e-consistência-de-sessão` | RN-07: ao retomar, HEAD ≠ âncora de fechamento → alerta explícito de inconsistência | 🟢 |
| `_reversa_sdd/domain.md#1.1-conceitos-e-entidades-chave` | "Sessão do Agente" e "Âncora Git de Sessão" hoje ancoradas ao nome legado `ESTADO-DA-SESSAO.md` | 🟢 |
| `_reversa_sdd/code-analysis.md#2.5-módulo-commands` | `SessionState` = entidade atômica (âncora git, feature ativa, início, status active/inactive); sem narrativa | 🟢 |
| `decisoes/MD-0001.md` | Regressão aceita: `cmd resume` não reinjeta contexto e materializa formato próprio na raiz | 🟢 |
| `decisoes/MD-0002.md` | Decisão de entrada travada: arquivo único `.harness/estado-da-sessao.md`, `SessionState` + `SessionNarrative`, round-trip, versionado | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor intermitente | Retomar o projeto após semanas sem reler tudo | Abre o agente; o estado da última sessão (feito, próximos passos, pendências, ponteiros) aparece no contexto automaticamente |
| Agente de IA (claude/gemini) | Carregar estado durável no boot | O hook `SessionStart` chama `./harness cmd resume`, que devolve a narrativa para o contexto |
| Mantenedor ao encerrar | Persistir a memória da sessão | Roda `./harness cmd encerrar-sessao`, que grava a narrativa rica e a âncora git no arquivo único |

## 4. Regras de negócio novas ou alteradas

1. **RN-N1: Local canônico único e neutro** 🟢
   - O estado de sessão passa a viver exclusivamente em `.harness/estado-da-sessao.md`, versionado. Deixam de existir `.claude/ESTADO-DA-SESSAO.md` e o `ESTADO-DA-SESSAO.md` da raiz.
   - Tipo: nova
2. **RN-N2: Reinjeção de contexto no boot** 🟢
   - `cmd resume` passa a devolver a narrativa da última sessão ao contexto do agente no `SessionStart` (hoje só imprime uma linha de status).
   - Tipo: nova
3. **RN-N3: Âncora git sobre o novo artefato** 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.3` (RN-07). O alerta de divergência de âncora é preservado, agora lendo a âncora de fechamento de `.harness/estado-da-sessao.md`.
   - Tipo: alterada
4. **RN-N4: Falha barulhenta no parse de estado** 🟡
   - Estado de sessão presente mas malformado deve falhar de modo explícito (erro nomeado), não retornar silenciosamente como "sem sessão". Alinha à preferência de erros barulhentos.
   - Tipo: alterada (hoje `load_session` degrada em silêncio para `None`)
5. **RN-N5: Core agnóstico a harness; mecanismo na borda** 🟢
   - `cmd resume`/`cmd encerrar-sessao` produzem o texto puro da narrativa; o mecanismo de entrega ao contexto é aplicado na borda (CLI), selecionado pelo `active_harness` do `harness.toml`. O core de sessão não conhece nenhum harness.
   - Tipo: nova
6. **RN-N6: Strategy de reinjeção por-harness (duas famílias)** 🟢
   - A entrega ao contexto segue uma Strategy por-harness (reusa o padrão de `core/install/harness_profiles.py`), com duas famílias confirmadas: (i) **hook `SessionStart` + `hookSpecificOutput.additionalContext`** — comum a Claude e Gemini CLI (formato idêntico; gatilho nos respectivos `settings.json`); (ii) **projeção em arquivo estático relido a cada boot** (`.agents/rules/estado-sessao.md` ou bloco no `AGENTS.md`) — Antigravity (`agy`), que não expõe hook de injeção de contexto. A fonte canônica `.harness/estado-da-sessao.md` é única; a projeção do Antigravity é derivada dela.
   - Tipo: nova
   - Detalhe e fontes em `decisoes/MD-0003.md`

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | `cmd resume` reinjeta a narrativa da última sessão no contexto, no boot do harness ativo (claude, gemini-cli ou antigravity) | Must | Ao iniciar/retomar a sessão, o corpo de `.harness/estado-da-sessao.md` chega ao contexto do agente sem intervenção manual, pelo mecanismo do harness ativo (ver RN-N6) | 🟢 |
| RF-02 | Estado unificado num único `.harness/estado-da-sessao.md` versionado | Must | git rastreia apenas o novo arquivo; `.claude/ESTADO-DA-SESSAO.md` e a raiz `ESTADO-DA-SESSAO.md` não existem mais | 🟢 |
| RF-03 | `SessionState` + value-object `SessionNarrative` (header machine + corpo em seções) com round-trip | Must | Teste de propriedade `parse(render(x)) == x` verde para estado com e sem narrativa | 🟢 |
| RF-04 | Preservar o alerta de divergência de âncora git (RN-07) sobre o novo arquivo | Must | HEAD ≠ âncora de fechamento → alerta explícito impresso na retomada | 🟢 |
| RF-05 | Portar `/encerrar-sessao` para `./harness cmd encerrar-sessao`: agente edita a prosa, CLI sela | Must | O agente escreve a narrativa em `.harness/estado-da-sessao.md`; o comando valida o formato e carimba o header-máquina (commit-âncora via GitPort, feature, timestamp, status), sem inventar prosa | 🟢 |
| RF-06 | Migração não-destrutiva do conteúdo legado | Must | A narrativa hoje em `.claude/ESTADO-DA-SESSAO.md` é migrada para `.harness/`; os arquivos antigos saem do git; nenhum dado de retomada é perdido | 🟢 |
| RF-07 | Atualizar a fiação da CLI para o novo caminho | Must | `main.py` (`session_file`) e o `CommandService` operam em `.harness/estado-da-sessao.md`; os demais comandos (`format`, `decisions`, `doc-gen`) seguem intactos | 🟢 |
| RF-08 | Parse malformado falha barulhento (RN-N4) | Should | Estado presente e inválido produz erro nomeado e código de saída não-zero no uso manual, sem mascarar como "sem sessão" | 🟡 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Manutenibilidade | Uma só fonte e um só parser para o estado de sessão | Fecha o drift de dois formatos do `MD-0001`; alta coesão | 🟢 |
| Acoplamento | Local neutro a harness; o core não depende do schema do Reversa | `MD-0002`; estado é conceito da CLI multi-harness, não do Claude | 🟢 |
| Testabilidade | Propriedade `parse∘render` coberta por teste; estender `tests/test_commands.py` e `tests/test_domain.py` | TDD; suíte hexagonal já existente | 🟢 |
| Desempenho | A reinjeção deve caber bem abaixo do timeout do hook | `.claude/settings.json`: `SessionStart` tem `timeout: 12` | 🟢 |
| Observabilidade | Erros de parse/IO do estado são explícitos e nomeados | Preferência de erros barulhentos; corrige o silêncio atual | 🟡 |
| Limite de payload | Narrativa enxuta: teto de 10.000 caracteres no Claude; Gemini sem limite documentado; Antigravity via arquivo (manter denso) | Doc de hooks Claude Code e Gemini CLI (2026) | 🟢 |
| Compatibilidade de harness | Reinjeção por hook exige Gemini CLI ≥ 0.25 (hooks desde a 0.24; regressão #16697 já corrigida) | Investigação web 2026-06-23; `decisoes/MD-0003.md` | 🟢 |
| Compatibilidade | Não quebrar `format`/`decisions`/`doc-gen`/`bootstrap` | Suíte de 41 testes deve permanecer verde | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: retomada reinjeta a narrativa no contexto
  Dado um .harness/estado-da-sessao.md com narrativa da sessão anterior
  Quando o SessionStart dispara ./harness cmd resume
  Então o corpo narrativo é devolvido ao contexto do agente
  E o arquivo é reescrito com a nova âncora e status active

Cenário: divergência de âncora git alerta o usuário
  Dado um estado de sessão cujo commit de fechamento difere do HEAD atual
  Quando a sessão é retomada
  Então um alerta explícito de inconsistência é impresso antes do resumo

Cenário: ausência de estado não quebra o boot
  Dado que .harness/estado-da-sessao.md não existe
  Quando o SessionStart dispara ./harness cmd resume
  Então uma nova sessão é criada para a feature padrão sem erro

Cenário (negativo): estado malformado falha barulhento
  Dado um .harness/estado-da-sessao.md presente mas com header inválido
  Quando ./harness cmd resume é executado manualmente
  Então um erro nomeado é emitido e o código de saída é não-zero
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 reinjeção de contexto | Must | É o objetivo que fecha o `MD-0001` |
| RF-02 arquivo único `.harness/` | Must | Unificação é o coração da decisão `MD-0002` |
| RF-03 round-trip `SessionState`/`SessionNarrative` | Must | Sustenta o TDD e a corretude do formato |
| RF-04 âncora git (RN-07) | Must | Não pode haver regressão da regra confirmada do legado |
| RF-06 migração não-destrutiva | Must | Preservar a memória de retomada existente |
| RF-07 fiação da CLI | Must | Sem ela, nada funciona ponta a ponta |
| RF-05 `cmd encerrar-sessao` | Must | Sem produtor da narrativa, a unificação não fecha o ciclo |
| RF-08 falha barulhenta | Should | Melhoria de robustez alinhada à preferência; não bloqueia o fluxo feliz |
| Paridade Claude + Gemini CLI | Must | Mesmo mecanismo (`additionalContext`); incremento barato e paridade de retomada |
| Paridade Antigravity | Must | Decisão do mantenedor; mecanismo distinto (projeção em arquivo), com gap de gatilho a investigar (ver Lacunas) |

## 9. Esclarecimentos

### Sessão 2026-06-23

- **Q (dúvida 1):** Envelope da reinjeção no `SessionStart` — `additionalContext` JSON ou stdout?
  **R:** `hookSpecificOutput.additionalContext` com `hookEventName: "SessionStart"` e exit 0 — confirmado na doc oficial de hooks do Claude Code (22/06/2026). O texto entra como system reminder, sem virar mensagem de chat; teto de 10.000 caracteres. Plain stdout também injeta em `SessionStart`, mas o JSON é o canal estruturado e estável (isola conteúdo de status/erro). Desenho: o core emite texto puro; o envelope JSON fica na borda (CLI), mantendo o core agnóstico a harness (ver RN-N5).
- **Q (dúvida 2):** Como o `cmd encerrar-sessao` recebe a narrativa rica?
  **R:** Agente edita, CLI sela. O agente escreve a prosa direto no `.harness/estado-da-sessao.md`; a CLI valida o formato (round-trip) e carimba o header-máquina (commit-âncora via GitPort, feature, timestamp, status). Porquê: menor acoplamento e SRP — o agente é o autor natural da prosa, a CLI é a guardiã do contrato/âncora; espelha o fluxo manual atual sem inventar transporte (stdin/arquivo). Enriquecimento derivado extra (ex.: commits desde a abertura) fica como follow-up (YAGNI).
- **Q (dúvida 3):** Escopo multi-harness — quais harnesses a 004 cobre?
  **R:** Os três: Claude, Gemini CLI e Antigravity (`agy`) — decisão do mantenedor. Investigação web (23/06) confirmou os mecanismos: Claude e Gemini CLI usam o mesmo envelope `hookSpecificOutput.additionalContext` via hook `SessionStart` (Gemini exige ≥ 0.25), então cobrir o Gemini é incremento barato sobre o Claude; o Antigravity não expõe hook de injeção e recebe o estado por projeção em arquivo estático relido a cada boot. Isso valida a Strategy plugável por-harness (RN-N6) — agora há três consumidores reais, então o argumento YAGNI anterior caiu. Detalhe e fontes em `decisoes/MD-0003.md`.

## 10. Lacunas

- 🟡 [DÚVIDA] Antigravity: como atualizar a âncora/status no boot, já que o `agy` não tem hook de injeção? Opções a confirmar na investigação do `/reversa-plan`: reinjeção passiva (estado materializado no `cmd encerrar-sessao`, relido pelo `agy` no próximo boot) versus hook `PreInvocation` do `agy` rodando `cmd resume`. Não bloqueia a decisão de escopo; é detalhe de implementação do ramo Antigravity.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-06-23 | Dúvidas 1–3 resolvidas por `/reversa-clarify` (contrato do hook confirmado; narrativa por edição + selo; escopo só Claude com core agnóstico) | reversa |
| 2026-06-23 | Escopo ampliado para os três harnesses (Claude, Gemini CLI, Antigravity); mecanismos confirmados por investigação web; `decisoes/MD-0003.md` | reversa |
