# Requirements: Medidor de progresso de entregáveis (termômetro read-only do ciclo forward)

> Identificador: `026-medidor-progresso-entregaveis`
> Data: `2026-08-11`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O harness responde hoje "o quê" e "por quê" (estado de sessão, microdecisões), mas não "quanto falta": o desenvolvedor intermitente retoma o projeto sem uma visão medida do progresso dos entregáveis. Esta feature adiciona ao core um **medidor de progresso read-only**, reproduzindo o padrão validado do `make estado` de `~/dev/comentarios-concursos`: toda linha da saída é **derivada** das fontes de verdade (checkboxes do `actions.md`, estágio físico das features, pendências do regression-watch, estado de sessão e gate de registro), nunca armazenada. A saída markdown vive em `.harness/progresso.md`, sem timestamp de geração, de modo que o diff só aparece quando o estado real muda. Divergência entre medida declarada e medida física é achado, não erro; o alerta existe enquanto o problema existir.

**Escopo negativo:** o medidor não escreve fora de `.harness/progresso.md`; não modifica nenhum artefato do Reversa (`.reversa/`, `_reversa_forward/`, `_reversa_sdd/` são só-leitura); não materializa hook novo em `settings.json`/git hooks nesta feature; não mede entregáveis arbitrários do projeto-alvo (apenas as fontes que o harness e o Reversa conhecem); não substitui o `estado-da-sessao.md` nem o índice de microdecisões.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#1` | Hexagonal em três anéis; serviços de capacidade puros sob `src/core/`, um por pasta; drivers de entrada (CLI/MCP/Antigravity) delegam a serviços injetados com portas | 🟢 |
| `_reversa_sdd/domain.md#2.5` (RN-N12) | Precedente do artefato derivado: o índice `microdecisoes.md` é compilado das fichas, nunca editado à mão — mesmo princípio do medidor | 🟢 |
| `_reversa_sdd/domain.md#2.17` (RN-N36..N40) | Fonte única: projetos migrados executam o core do upstream via shim; um comando novo na CLI propaga à base instalada sem rematerializar nada | 🟢 |
| `_reversa_sdd/domain.md#2.19-2.21` (RN-N43, RN-N47) | `evaluate_registration_gate` é avaliação pura reutilizável (universo `changed ∪ dirty`, fail-open com `aviso`) — insumo pronto para a seção "pendência de registro" do medidor | 🟢 |
| `.claude/skills/reversa-requirements/SKILL.md` (detecção de estágio físico) | Tabela autoritativa de estágio por artefatos (`vazio`/`requirements`/`plan`/`coding-em-progresso`/`done`) e regra de contagem de checkboxes em linhas de tabela — semântica que o medidor deve reproduzir fielmente | 🟢 |
| `~/dev/comentarios-concursos` (`tools/estado.py`, `ESTADO.md`, `.pre-commit-config.yaml`) | Padrão de referência: termômetro read-only, markdown sem timestamp, `--json` pode carimbar, `--em-hook` (arquivo stale falha o commit; alerta grave não falha), duas medidas cuja divergência é achado | 🟢 |
| `_reversa_sdd/architecture.md#4` | Bordas existentes: `bootstrap` instala pre-commit/post-merge; `resume_context` injeta o índice de decisões no resume — pontos de integração futuros, não desta feature | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor intermitente (iagoleal) | Retomar o projeto após semanas sabendo quanto falta e onde parou | Roda `harness progress` (ou lê `.harness/progresso.md` versionado) e vê feature ativa, fase, N/M ações, pausadas e alertas |
| Agente de IA (Claude/Antigravity) | Contextualizar-se no início da sessão sem varrer `_reversa_forward/` inteiro | Lê `.harness/progresso.md` como mapa de progresso antes de retomar o ciclo forward |
| Revisor do histórico | Auditar quando o progresso de fato mudou | `git log -p .harness/progresso.md` mostra diffs apenas nos commits em que o estado real avançou (sem ruído de timestamp) |

## 4. Regras de negócio novas ou alteradas

1. **RN-01 (termômetro derivado):** o medidor é read-only sobre as fontes de verdade; **nenhuma** linha da saída representa estado armazenado pelo próprio medidor. Recomputar com as mesmas fontes produz bytes idênticos. 🟢
   - Origem no legado: padrão `tools/estado.py` de comentarios-concursos; princípio irmão da RN-N12 (`_reversa_sdd/domain.md#2.5`)
   - Tipo: nova
2. **RN-02 (saída estável no tempo):** o markdown gerado **não contém** timestamp de geração nem qualquer valor volátil; o diff de `.harness/progresso.md` aparece somente quando o estado medido muda. O modo `--json` (stdout) pode carimbar hora. 🟢
   - Tipo: nova
3. **RN-03 (divergência é achado):** quando duas medidas do mesmo fato discordam (ex.: `current-stage` declarado no `active-requirements.json` versus estágio físico por artefatos), o medidor **reporta ambas** e emite alerta; nunca "corrige" a fonte nem esconde a discrepância. O alerta persiste enquanto a divergência existir. 🟢
   - Origem no legado: princípio da detecção física do Reversa ("resistente a skills que esquecem metadados") + padrão comentarios-concursos
   - Tipo: nova
4. **RN-04 (footprint de escrita):** o medidor grava exatamente um artefato, `.harness/progresso.md`; trata `.reversa/`, `_reversa_forward/` e `_reversa_sdd/` como só-leitura (regra não-negociável do projeto). 🟢
   - Tipo: nova
5. **RN-05 (fail-soft por fonte ausente):** fonte legitimamente ausente (projeto sem Reversa, sem sessão ativa, sem regression-watch) gera seção "n/a" sem erro; falha **real** de leitura (JSON corrompido, permissão) gera aviso barulhento em stderr sem abortar as demais seções. 🟢
   - Origem no legado: fail-open barulhento do gate (`_reversa_sdd/domain.md#2.19`, RN-N43)
   - Tipo: nova
6. **RN-06 (paridade de semântica com a detecção física):** o estágio físico e a contagem de checkboxes seguem exatamente a tabela do skill `reversa-requirements` (linhas de tabela terminadas em `| [ ] |`/`| [X] |`, com os checkboxes eventualmente envoltos em crase); qualquer refinamento futuro deve mudar os dois lugares. 🟢
   - Tipo: nova
7. **RN-07 (integração pela fonte única, sem contrato novo):** o comando nasce na CLI do core e propaga à base migrada pelo shim (RN-N36); nenhum hook é materializado nesta feature — o modo `--em-hook` existe como flag para uso manual ou integração futura pelo `bootstrap`. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.17`
   - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Novo subcomando `harness progress` que computa o progresso e grava `.harness/progresso.md` (escrita atômica); serviço puro em `src/core/` com portas injetadas, na arquitetura hexagonal vigente | Must | Rodar duas vezes sem mudança nas fontes produz arquivo byte-idêntico; rodar após marcar um checkbox altera apenas as linhas pertinentes | 🟢 |
| RF-02 | Seção "Ciclo forward": feature ativa (id, nome, estágio físico, ações `[X]`/total por fase), features pausadas (id, estágio de pausa), total de features concluídas | Must | Com a 026 ativa e a 024 pausada, o markdown lista ambas com os números reais extraídos dos `actions.md` | 🟢 |
| RF-03 | Seção "Alertas": divergência estágio declarado × físico; `feature-dir` inexistente; `actions.md` com checkbox aberto em feature apontada como concluída; pendências de reconciliação registradas nos `regression-watch.md` das features | Must | Simular `current-stage` divergente gera alerta; corrigir a fonte faz o alerta desaparecer na recomputação | 🟢 |
| RF-04 | Seção "Harness": status da sessão (ativa/fechada, âncora), microdecisões (total de fichas, id da última) e pendência de registro do gate (reuso de `evaluate_registration_gate`, leitura pura) | Must | Com sessão ativa e trabalho sem ficha, a seção reporta a pendência; com fichas em dia, reporta "em dia" | 🟢 |
| RF-05 | Modo `--json`: emite a mesma medição como JSON no stdout (sem gravar arquivo), com carimbo de hora permitido | Must | `harness progress --json` devolve JSON parseável com os mesmos números do markdown | 🟢 |
| RF-06 | Modo `--em-hook`: recomputa e compara com `.harness/progresso.md`; arquivo divergente (stale) → exit 1 com instrução de regenerar; alertas graves presentes **não** falham (aviso em stderr, exit 0) | Should | Teste cobre os três desfechos: em dia (0), stale (1), alerta sem staleness (0 + stderr) | 🟢 |
| RF-07 | TDD com testes de unidade do serviço puro (FakeFs/FakeGit) e de borda da CLI; bump minor 2.3.0 → 2.4.0; ficha `MD-0019` registrando a decisão de residência no core | Should | Suíte verde; ficha validada pelo grafo | 🟢 |
| RF-08 | Apêndice de progresso no `resume` (uma linha-resumo no contexto reinjetado), desativável por config, no padrão do índice de decisões (`resume_context`, f021) | Could | Fora do critério de pronto; se entrar, segue o botão `session.inject_*` existente | 🟡 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Execução em ~1 s no pior caso local (leitura de arquivos + `git status`); sem rede, sem varredura recursiva fora de `_reversa_forward/` e `.harness/` | Roda a cada retomada e potencialmente em hook de commit | 🟢 |
| Observabilidade | Erros barulhentos: falha real de leitura vai a stderr com caminho e causa; nunca falha silenciosa que produza medição parcial sem aviso | Filtro operacional do mantenedor (erros barulhentos > performance) | 🟢 |
| Manutenibilidade | Serviço puro isolado (`src/core/progress/`), sem dependência de adaptadores concretos; parsing de `actions.md` concentrado numa função com testes de borda (crases, tabelas, linhas livres) | Arquitetura hexagonal vigente (`_reversa_sdd/architecture.md#1`) | 🟢 |
| Reprodutibilidade | Nenhuma dependência nova; stdlib apenas, como o resto do core | Estabilidade > novidade | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: medição idempotente sem mudança de estado
  Dado um projeto com feature ativa e progresso.md recém-gerado
  Quando rodo harness progress novamente sem tocar nenhuma fonte
  Então .harness/progresso.md permanece byte-idêntico (git diff vazio)

Cenário: progresso do ciclo forward medido por fase
  Dado uma feature ativa com 7 ações [X] de 11 no actions.md
  Quando rodo harness progress
  Então a seção "Ciclo forward" reporta 7/11 com a quebra por fase e o estágio físico coding-em-progresso

Cenário: divergência entre declarado e físico vira alerta persistente
  Dado active-requirements.json com current-stage "requirements" e roadmap.md já presente na feature-dir
  Quando rodo harness progress duas vezes
  Então ambas as execuções emitem o mesmo alerta de divergência, que só desaparece quando a fonte é corrigida

Cenário: projeto sem Reversa degrada com elegância
  Dado um projeto com harness instalado e sem .reversa/
  Quando rodo harness progress
  Então a seção "Ciclo forward" reporta n/a, a seção "Harness" é medida normalmente e o exit code é 0

Cenário (negativo): arquivo stale detectado pelo modo hook
  Dado .harness/progresso.md desatualizado em relação às fontes
  Quando rodo harness progress --em-hook
  Então o comando sai com código 1 e instrui a regenerar; com o arquivo em dia, sai com 0 mesmo havendo alertas
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-02 | Must | São o medidor em si; sem eles não há feature |
| RF-03, RF-04 | Must | O valor está nos alertas e no cruzamento com o que o harness já sabe; medição sem achado é dashboard morto |
| RF-05 | Must | Consumo programático (agentes, scripts) sem parsear markdown |
| RF-06 | Should | O guarda-freio contra progresso.md podre; não bloqueia o valor central |
| RF-07 | Should | Higiene do projeto (TDD, versão, ficha), padrão das features anteriores |
| RF-08 | Could | Ganho real, mas toca o resume e merece avaliação de ruído no contexto; pode ser feature própria |

## 9. Esclarecimentos

> Nenhuma sessão de dúvidas registrada ainda. Rode `/reversa-clarify` quando houver `[DÚVIDA]` pendente.

## 10. Lacunas

Nenhuma lacuna aberta. As três decisões que o pedido delegou ("avaliar", "decidir") foram resolvidas no corpo com justificativa: residência no **harness-core** (RN-07: propagação pela fonte única; `tools/` do projeto não propagaria e duplicaria infraestrutura), modo hook como **flag sem materialização** (RN-07: mexer no `bootstrap`/base instalada é passo separado e adiável) e nome `harness progress` com artefato `.harness/progresso.md` (CLI em inglês como os demais subcomandos; artefato em português como os irmãos `estado-da-sessao.md`/`microdecisoes.md`; "estado" ficou fora do nome para não colidir com o estado de sessão).

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-08-11 | Versão inicial gerada por `/reversa-requirements` | reversa |
