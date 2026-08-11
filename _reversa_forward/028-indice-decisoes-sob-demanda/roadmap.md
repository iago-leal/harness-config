# Roadmap: Índice de microdecisões leve com consulta sob demanda

> Identificador: `028-indice-decisoes-sob-demanda`
> Data: `2026-08-11`
> Requirements: `_reversa_forward/028-indice-decisoes-sob-demanda/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A mesma passada de reindexação que hoje compila o índice completo (`DecisionService.compile_index`, disparada pelo hook Stop nas duas bordas) passa a derivar um SEGUNDO artefato: a visão compacta, com as K fichas mais recentes (só títulos), a contagem total e os ponteiros de consulta. O `cmd resume` troca a injeção do índice integral pela injeção da visão compacta, com fallback não-bloqueante para o índice integral enquanto a visão ainda não existir (janela entre o upgrade e a primeira reindexação). As duas escritas ganham regravação condicionada a mudança de conteúdo, alinhando o componente ao padrão de artefato derivado das features 026/027. Por fim, o `harness init` passa a gravar um trecho curto e idempotente de guidance no `CLAUDE.md` do projeto, situando o agente sobre o acervo e a consulta sob demanda. Nenhum hook materializado muda: tudo propaga pela fonte única (RN-N36).

## 2. Princípios aplicados

n/a — `.reversa/principles.md` não existe neste projeto. Os princípios operacionais do mantenedor (longevidade, baixo acoplamento, erros barulhentos, footprint mínimo) foram observados nas decisões D-01..D-07.

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | A visão compacta é um segundo artefato derivado, em arquivo próprio (`decisions.compact_file`, default `.harness/decisoes-recentes.md`), gerado pelo `DecisionService` na MESMA passada de reindexação, nas DUAS bordas que hoje compilam o índice (ramo `decisions` do `main.py` e reindexação da bridge Antigravity). | Uma única fonte de derivação (as fichas), um único serviço; a visão fica pronta antes do próximo SessionStart sem custo no caminho crítico do `resume`. | Derivar on-the-fly no `resume` (acopla parse de fichas ao SessionStart e multiplica modos de falha num hook); parsear o índice completo no `resume` (segunda implementação do formato, frágil). | 🟢 |
| D-02 | O `cmd resume` injeta `compact_file`; se ausente, cai no comportamento atual (injeta o índice integral) com aviso em stderr, não-bloqueante. O `init` não semeia a visão compacta: a primeira reindexação a cria e o sistema converge sozinho (RN-07). | Migração autoresolvente sem código de migração (padrão das features 016/023); nenhum projeto fica sem orientação na janela de transição. | Falhar com erro (bloquearia sessão); injetar nada (perderia a âncora de busca que a feature 021 instituiu); semear placeholder no init (artefato a mais sem ganho real). | 🟢 |
| D-03 | Composição do bloco compacto: cabeçalho de orientação (o que é o acervo, onde está o índice completo e onde estão as fichas), linha `Total: N fichas`, e as K mais recentes por ID em ordem decrescente (a mais nova primeiro), apenas `- **MD-NNNN** — título`. Sem timestamp, sem valor volátil. | Decisões recentes são as mais úteis à sessão corrente; ordem decrescente põe a mais nova no topo; determinismo pinado pelo padrão 026/027. | Incluir backlinks (metade do peso do índice, dispensável na visão); filtrar por vigência (o campo `estado:` não reflete supersessão — MD-0016 segue `ativo` — e derivar vigência das relações adiciona complexidade sem demanda). | 🟢 |
| D-04 | Dois campos novos na `DecisionsSection`: `compact_file: str = ".harness/decisoes-recentes.md"` e `compact_index_size: int = 10`. `K = 0` é válido e degrada para só cabeçalho + contagem + ponteiros; negativo é erro de configuração (barulhento). | Caminhos e teto por configuração, coerente com RN-N11; default calibrado pela decisão do clarify (10). | Teto fixo no código (recalibrar exigiria versão nova do core); teto em linhas/bytes (pode cortar ficha ao meio; unidade menos legível). | 🟢 |
| D-05 | As escritas do índice completo E da visão compacta tornam-se write-only-when-changed: ler o arquivo existente, comparar, gravar (atômico) só quando difere. | Satisfaz RF-03; hoje `compile_index` regrava incondicionalmente a cada Stop, sujando mtime sem mudança real; padrão consolidado nas features 026/027. | Manter regravação incondicional (viola RF-03 e o padrão do projeto). | 🟢 |
| D-06 | O `harness init` grava um trecho curto de guidance no `CLAUDE.md` do projeto (cria o arquivo se não existir; senão, anexa ao final), delimitado por um marcador estável de seção; a idempotência é por detecção do marcador (presente → não regrava). O `upgrade` nunca toca o trecho. | Decisão do clarify (D3): escrita única na instalação, à maneira do Reversa, sem criar classe de artefato com merge contínuo. | Guidance gerenciada com merge idempotente e upgrade (custo estrutural desproporcional); nenhuma guidance fora do bloco injetado (perderia agentes que não passam pelo SessionStart). | 🟢 |
| D-07 | Para `active_harness = "antigravity"`, o mesmo trecho vai para o arquivo de guidance da engine (`AGENTS.md`), pela mesma regra de marcador. | RN-04 pede as duas engines; a nota do requirements marca o arquivo exato como inferência a confirmar no coding. | Escrever sempre e só em `CLAUDE.md` (deixaria a engine Antigravity sem guidance). | 🟡 |
| D-08 | Nenhum campo novo no `SessionState`, nenhum hook regravado, nenhuma mudança no gate de registro (RN-N43..N47) nem nos exit codes do ramo `decisions`. | Contratos preservados (RN-05 do requirements); a mudança propaga pela fonte única (RN-N36). | — | 🟢 |

## 4. Premissas

n/a — as três `[DÚVIDA]` do requirements foram resolvidas no clarify de 2026-08-11; nenhuma premissa pendente.

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Decisions (serviço) | `.harness/harness-core/src/core/decisions/service.py` (`_reversa_sdd/architecture.md#2`, unit `microdecisoes/`) | regra-alterada | Método novo de derivação da visão compacta; write-only-when-changed nas duas escritas. |
| Session (resume) | `.harness/harness-core/src/core/session/resume_context.py` | regra-alterada | `build_decisions_appendix` passa a receber a visão compacta; fallback para o índice integral quando ausente. |
| CLI (bordas) | `.harness/harness-core/src/main.py` (ramos `decisions` e `cmd resume`) | regra-alterada | Ramo `decisions` deriva as duas visões; `cmd resume` injeta a compacta com fallback e aviso. |
| Bridge Antigravity | `.harness/harness-core/src/adapters/antigravity/hook_bridge.py` | regra-alterada | A reindexação de fim de turno também deriva a visão compacta (mesma chamada de serviço). |
| Config | `.harness/harness-core/src/core/domain/config.py` (`DecisionsSection`) | delta-de-dados | Campos `compact_file` e `compact_index_size` com defaults. |
| Bootstrap (init) | `.harness/harness-core/src/core/bootstrap/init_service.py` | regra-nova | Trecho de guidance idempotente no `CLAUDE.md` (ou `AGENTS.md`, D-07) do projeto. |

## 6. Delta no modelo de dados

- Resumo das mudanças: dois campos novos na seção `[decisions]` do `harness.toml` (caminho da visão compacta e teto K), com defaults que dispensam edição dos tomls existentes; nenhum campo novo no `SessionState`; nenhuma migração de fichas.
- Detalhe completo em: `_reversa_forward/028-indice-decisoes-sob-demanda/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Bloco de decisões injetado no SessionStart (visão compacta + fallback) | arquivo / stdout do sink | `_reversa_forward/028-indice-decisoes-sob-demanda/interfaces/bloco-resume-decisoes.md` |
| Trecho de guidance gravado pelo `init` no `CLAUDE.md`/`AGENTS.md` | arquivo | `_reversa_forward/028-indice-decisoes-sob-demanda/interfaces/trecho-guidance-init.md` |

## 8. Plano de migração

1. Upgrade da fonte única entrega o comportamento novo a todos os projetos (nenhum hook regravado).
2. Na primeira sessão após o upgrade, o `resume` ainda não encontra a visão compacta → injeta o índice integral com aviso (comportamento idêntico ao atual).
3. No primeiro fim de turno (Stop) ou `harness decisions` manual, a visão compacta é derivada; das sessões seguintes em diante, a injeção é a compacta.
4. O trecho de guidance no `CLAUDE.md` só entra em projetos que rodarem `harness init` (novos ou re-init); projetos existentes podem recebê-lo com um re-init inócuo (idempotente por marcador).

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Projeto que nunca roda Stop nem `decisions` manual fica indefinidamente no fallback (índice integral) | baixo | baixo | O fallback é exatamente o comportamento atual; nada piora. Aviso em stderr aponta a causa. |
| Usuário edita ou remove o marcador do trecho no `CLAUDE.md` e um re-init duplica o conteúdo | baixo | baixo | Marcador estável e curto; detecção por substring do marcador, não do conteúdo; documentado no contrato. |
| K mal calibrado para um projeto específico | baixo | médio | `compact_index_size` configurável por projeto; default 10 decidido no clarify. |
| Divergência de formato entre índice completo e visão compacta (título extraído duas vezes) | médio | baixo | Extração de título fatorada num único ponto do serviço, compartilhada pelas duas derivações. |
| Fallback injeta índice integral gigante justamente no projeto-problema | médio | baixo | Janela dura até a primeira reindexação (um fim de turno); convergência automática. |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Suíte de testes do core verde (inclui novos testes de derivação, fallback, idempotência e guidance)
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-08-11 | Versão inicial gerada por `/reversa-plan` | reversa |
