# Cross-check: Oferta de commit consentida

> Identificador: `024-oferta-commit-consentida`
> Data: `2026-07-24` (terceira rodada, sobre os artefatos saneados após a segunda auditoria)
> Artefatos analisados:
> - `_reversa_forward/024-oferta-commit-consentida/requirements.md`
> - `_reversa_forward/024-oferta-commit-consentida/roadmap.md`
> - `_reversa_forward/024-oferta-commit-consentida/actions.md`
> - Apoio: `data-delta.md`, `investigation.md`, `onboarding.md`, `interfaces/*`
> - Referência do legado: `_reversa_sdd/domain.md`, `_reversa_sdd/code-analysis.md`, `_reversa_sdd/state-machines.md` e código as-built

**Este relatório é estritamente leitor. Nenhum dos artefatos analisados foi alterado.**

Os IDs `A001`–`A015` conservam o significado das rodadas anteriores. Esta rodada
verifica o saneamento que os artefatos registram nos seus próprios changelogs
(`roadmap.md#11`, `actions.md` histórico, `requirements.md#9`) contra o conteúdo
atual e o código as-built. A tabela de encerramento das rodadas anteriores está na
seção final.

## Resumo

| Severidade | Quantidade |
|------------|------------|
| CRITICAL | 1 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| **Total** | **1** |

Comparação com a segunda rodada: **os quatro MEDIUM (A011–A014) e os quatro LOW
(A008–A010, A015) foram fechados** por edição dos artefatos, verificada abaixo item
a item. Permanece o único CRITICAL — a dívida deliberada da RN-N31 (A001) —, que
por natureza só se salda depois da implementação, por re-extração dirigida. Nenhum
achado desta rodada questiona o desenho, e nenhum é impedimento para o coding.

## Findings

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A001 | CRITICAL | Coerência com o legado | A feature altera a RN-N31, regra 🟢 CONFIRMADA, tornando condicional um commit hoje incondicional. Dívida assumida por decisão do mantenedor; reconciliação agendada para depois da implementação | `requirements.md#4` (RN-04) · `roadmap.md#2` · `_reversa_sdd/domain.md:227` |

## Findings CRITICAL e HIGH, em detalhe

### A001 — Alteração de regra 🟢 do legado (RN-N31)

Único achado remanescente, e por decisão do mantenedor, não por descuido. A RN-N31
nasceu na feature 013 para resolver um problema concreto: antes dela, o registro de
encerramento ficava como mudança pendente eterna no working tree. Esta feature
reintroduz esse desfecho como possibilidade e, sob a RN-08, como **default** do
caminho sem terminal.

O impacto não é de corretude — o `data-delta.md#4.2` mostra que o pré-check
(RN-N34), a âncora (RN-07/D-11) e o gate (RN-N43) absorvem o efeito —, e sim de
fonte de verdade: enquanto o `_reversa_sdd/domain.md` afirmar em 🟢 que o
encerramento versiona o estado, a extração reversa descreverá um comportamento que
o código não terá mais.

O `roadmap.md#2` assume a dívida, o `#8` (passo 6) a agenda como reconciliação por
re-extração dirigida, e o critério de pronto (`roadmap.md#10`) exige a ficha de
microdecisão `MD-0017` (ação `T024`) registrando a inversão de política. Direção
sugerida ao humano: manter a decisão, codar, e agendar a reconciliação do
`_reversa_sdd/` por `/reversa` após a implementação. **Não é impedimento para
começar.**

## Verificação do saneamento (achados fechados nesta rodada)

| ID | Sev. orig. | Situação | Verificação no artefato / as-built |
|----|-----------|----------|-------------------------------------|
| A011 | MEDIUM | **Fechado** | `roadmap.md#3` D-01 grafa `--com-commit-encerramento` / `--sem-commit-encerramento`, alinhada à D-10; a grafia aposentada (`--com-commit-registro`) não ocorre em nenhum artefato. D-11 nova documenta o canal da âncora, encerrando a lacuna que restava da D-10 |
| A012 | MEDIUM | **Fechado** | `investigation.md:48` invoca a **RN-N33** para a paridade CLI+skill e `:104` a lista entre as fontes; nenhuma ocorrência de RN-N38 remanesce no `investigation.md`. A correção está anotada em `requirements.md#9` |
| A013 | MEDIUM | **Fechado** | `roadmap.md#3` D-11 fixa a âncora vinda de `GitPort.get_head_commit` chamado pelo `SessionCloseFlow` **antes** do fechamento; a ação `T015` implementa esse canal ("âncora obtida por `get_head_commit` antes do fechamento (D-11)"). O contrato `interfaces/encerramento-nao-versionado-marker.md#3` recebe o valor por essa via |
| A014 | MEDIUM | **Fechado** | `actions.md` T008 asserta a ordem exigida pelo contrato: "o marker sai depois da mensagem de sucesso e antes da oferta de push", cobrindo os invariantes #5 e #6 de `interfaces/encerramento-nao-versionado-marker.md` |
| A008 | LOW | **Fechado** | `actions.md` T020 declara alvo `src/main.py` **+ script fino da skill** e textos "idênticos nas duas bordas", removendo a omissão da segunda borda |
| A009 | LOW | **Fechado** | `actions.md` T006 asserta, no modo interativo, que "a contagem anunciada é o total real (34), não o número de exibidos (20)" |
| A010 | LOW | **Fechado** | `actions.md` T007 inclui "o cenário de **árvore limpa**, em que o fluxo pula a oferta de commit do trabalho e vai direto a esta decisão" |
| A015 | LOW | **Fechado** | `actions.md` T009 está a 🟢 e cita `gate.py:84-85` (o `state_file` excluído do universo do gate), alinhando a confidência ao que o legado já garante (RN-N43) |

## Verificações que passaram

### Cobertura

- Os doze requisitos funcionais (RF-01 a RF-12) têm ao menos uma decisão no
  roadmap e ao menos uma ação correspondente. O RF-11 é satisfeito pelo próprio
  `interfaces/`, entregue pelo `/reversa-plan`.
- As **onze** decisões técnicas têm ação: D-01 → T008/T016/T017/T025; D-02 → T014;
  D-03 → T013; D-04 → T019; D-05 → T005/T013; D-06 → T004/T012; D-07 →
  T007/T008/T015; D-08 → T025/T016; D-09 → T018/T021; D-10 → T011/T016/T017/T018
  (renomeação para "commit de encerramento" nas superfícies); D-11 → T015. A D-10,
  antes sem ação dedicada (achado A011), consome-se nas ações de renomeação das
  bordas e do marker.
- Os treze cenários Gherkin têm ação de teste, incluindo os quatro nascidos da
  RN-08, o anúncio do total truncado (T006), a árvore limpa (T007) e a ordem do
  marker (T008).
- O passo 5 do plano de migração (propagação à base instalada) tem ação própria
  (T028); o passo 6 (reconciliação do `_reversa_sdd/`) fica fora do `actions.md`
  por pertencer ao pipeline de re-extração — omissão correta.
- O `data-delta.md` conclui "sem mudança de schema" e, coerentemente, não há ação
  de migração de dados.

### Consistência

- Os três contratos de `interfaces/` aparecem no `roadmap.md#7` e cada um tem ação
  que o consome (T003/T011, T004/T012, T008/T016/T017/T025).
- A terminologia "commit de encerramento" está uniforme nos três artefatos
  principais, no `data-delta.md`, no `onboarding.md` e nos contratos; a grafia das
  flags é única em toda a superfície (A011 fechado).
- Nenhum RF, RN ou D é citado sem existir no documento que o define.
- As citações de regra do legado conferem nos três artefatos principais **e** no
  `investigation.md` (A012 fechado): RN-N34 (`domain.md:245`) para o filtro de
  pendência, RN-N33 (`:236`) para a fonte única, RN-N31 (`:227`), RN-N5 (`:105`) e
  RN-N4 (`:102`).

### Coerência com o legado

- Componentes citados existem no código as-built: `pending_work_paths`
  (`close_flow.py:20`), `render_commit_pendente_marker` (`:33`),
  `conduct_commit_pendente` (`:50`), `SessionCloseFlow.run` (`:298`), `__all__`
  (`:477`), `CommandService.execute_command` (`commands/service.py:29`), o
  adaptador MCP (`adapters/mcp/server.py`) e o script fino da skill.
- A RN-N45 é respeitada: `close_session` (`models.py:137-142`) zera os dois
  fingerprints do gate, portanto o desfecho não versionado também os limpa
  (`data-delta.md#4.3`, ação T002).
- A RN-N43 é respeitada: o gate exclui o `state_file` do universo de mudanças
  (`gate.py:84-85`), de modo que o estado sujo não realimenta o terceiro portão —
  base para A015 subir a 🟢.
- A RN-N5 é preservada: o core continua sem `git add` de trabalho alheio; a
  pergunta que ele formula é sobre ato próprio (D-02, T014).
- A RN-N34 é preservada intacta — impede o estado sujo de virar pendência em
  cascata na sessão seguinte (ação T009).
- Os códigos de saída do contrato batem com o legado: aborto por portão devolve 0,
  falha de commit autorizado devolve 1, uso indevido de flags devolve 2
  (`interfaces/flags-encerramento.md#5`).
- A RN-N31 é o único conflito, deliberado e registrado (A001).

### Sanidade do actions

- As 28 ações têm IDs sem reciclagem — T001 a T024 preservados, T025 a T028 novos —
  e status inicial `[ ]`.
- Todas as dependências citadas apontam para IDs existentes.
- **Nenhum ciclo**: o grafo é um DAG com raízes em T001/T002 e folha em T028; a
  maior cadeia declarada (10) confere com o grafo.
- As ações `[//]` não compartilham arquivo alvo entre si dentro da fase.
- Nenhuma ação de "configurar IDE", "rodar lint" ou "abrir PR".
- Os alvos de arquivo existem: a versão do core em `src/core/domain/config.py`, as
  três cópias do `SKILL.md` em 1.3.0, os testes em `tests/test_close_flow.py` e
  `tests/test_cli.py`.

## Encerramento dos achados das rodadas anteriores

| ID | Severidade original | Situação | Onde foi resolvido |
|----|--------------------|----------|--------------------|
| A002 | HIGH | **Fechado** (2ª rodada) | RN-08 e RF-08: sem terminal, o default inverte-se e nada é versionado sem flag |
| A003 | HIGH | **Fechado** (2ª rodada) | RF-03 reescrito — o core pergunta o que executa (RN-03) |
| A004 | HIGH | **Fechado** (3ª rodada) | Citações corrigidas nos artefatos principais (2ª) e no `investigation.md` (A012, 3ª) |
| A005 | HIGH | **Fechado** (2ª rodada) | RF-04: no terminal, contagem **e** lista; o marker mantém o campo `arquivos` |
| A006 | MEDIUM | **Fechado** (3ª rodada) | D-10 e renomeação do marker (2ª); grafia da D-01 alinhada (A011, 3ª) |
| A007 | MEDIUM | **Fechado** (2ª rodada) | Ressalva do MCP incorporada à RN-04 do `requirements.md` |
| A008 | LOW | **Fechado** (3ª rodada) | T020 passa a declarar as duas bordas |
| A009 | LOW | **Fechado** (3ª rodada) | T006 asserta o anúncio do total truncado no modo interativo |
| A010 | LOW | **Fechado** (3ª rodada) | T007 cobre o cenário de árvore limpa |
| A011 | MEDIUM | **Fechado** (3ª rodada) | Grafia da D-01 alinhada à D-10; D-11 nova |
| A012 | MEDIUM | **Fechado** (3ª rodada) | `investigation.md` passa a citar RN-N33 |
| A013 | MEDIUM | **Fechado** (3ª rodada) | D-11 fixa o canal da âncora; T015 o implementa |
| A014 | MEDIUM | **Fechado** (3ª rodada) | T008 asserta a ordem do marker |
| A015 | LOW | **Fechado** (3ª rodada) | T009 a 🟢, alinhada à RN-N43 |
| A001 | CRITICAL | **Aberto (dívida assumida)** | Reconciliação da RN-N31 agendada para após a implementação (roadmap #8, ação T024) |
