# Roadmap: Medidor de progresso de entregáveis (`harness progress`)

> Identificador: `026-medidor-progresso-entregaveis`
> Data: `2026-08-11`
> Requirements: `_reversa_forward/026-medidor-progresso-entregaveis/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Feature aditiva, sem alterar nenhuma regra existente: nasce um serviço puro novo (`src/core/progress/`) e um subcomando novo na CLI (`harness progress`); nada mais no core muda além do literal de versão e da seção de config nova com default. O serviço computa uma `Medicao` (dataclass) a partir de quatro fontes só-leitura — `.reversa/active-requirements.json`, os `actions.md`/artefatos físicos de `_reversa_forward/*`, os `regression-watch.md` das features e o estado do harness (sessão via `CommandService.load_session`, fichas MD, pendência via `evaluate_registration_gate`) — e renderiza em dois formatos: markdown estável (sem timestamp, gravado em `.harness/progresso.md` apenas quando os bytes mudam) e JSON no stdout (com `aferido_em`). O modo `--em-hook` reproduz o `_no_hook` do padrão de referência: regrava e reprova (exit 1) somente se o arquivo estava defasado; alerta de severidade alta nunca reprova. Propagação automática pela fonte única (RN-N36): nenhum materializador, hook ou settings muda.

## 2. Princípios aplicados

n/a — o projeto não possui `.reversa/principles.md`. Filtros operacionais do mantenedor atendidos: **retomabilidade** (o artefato versionado é o mapa de retomada), **erros barulhentos** (falha real de leitura vai a stderr com caminho e causa; divergência vira alerta persistente), **estabilidade** (stdlib apenas, padrão já validado em produção em outro projeto do mantenedor).

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Serviço puro novo `src/core/progress/` (medição em `service.py`, renderizadores em `render.py`), portas `FileSystemPort`/`GitPort` injetadas; borda fina em `main.py` | Décima capacidade do hexágono, no padrão das nove existentes (`_reversa_sdd/architecture.md#1`); testável com FakeFs/FakeGit | Script em `tools/` do projeto (não propaga pela fonte única, duplica infra — descartado no requirements §10); lógica na borda da CLI (viola o anel de domínio) | 🟢 |
| D-02 | Subcomando `harness progress` com grupo mutuamente exclusivo `--json` / `--em-hook`; modo padrão regrava `.harness/progresso.md` só-quando-muda e informa `regravado`/`em dia` | Espelha a CLI de referência (`tools/estado.py`), já validada; gravação condicional preserva mtime e o invariante de diff limpo (RN-02) | Flag `--markdown` separada (no harness o markdown É o modo padrão; flag seria ruído); imprimir no stdout por padrão (o artefato versionado é o entregável) | 🟢 |
| D-03 | Códigos de saída: 0 no fluxo normal (com ou sem alertas), 1 exclusivo do `--em-hook` defasado, 2 para falha real de leitura (fonte corrompida/ilegível) | Alerta é informação, não falha (RN-03/RN-05); o exit 3 da referência (alerta alto) não migra porque o harness tem canais próprios de enforcement (gate/portão) e o medidor não deve virar um segundo gate | Exit ≠ 0 por alerta alto no modo padrão (transformaria o termômetro em bloqueio — exatamente o que a 025 acabou de aposentar) | 🟢 |
| D-04 | Paridade de semântica com a detecção física do Reversa: um módulo único (`stages.py`) implementa a tabela de estágios e a contagem de checkboxes (linhas de tabela terminadas em `\| [ ] \|`/`\| [X] \|`, com ou sem crases envolvendo o checkbox) | RN-06; a regra hoje vive em prosa no skill `reversa-requirements` — concentrar o parsing num módulo com testes de borda é a única defesa contra deriva | Reaproveitar por import algo do skill (skills são markdown, não código); duas implementações ad-hoc espalhadas | 🟢 |
| D-05 | Pendência de registro reusa `evaluate_registration_gate` em modo leitura pura (sem persistir fingerprint algum); reportada como booleano + contagem, sem listar arquivos | RN-N43 já entrega a avaliação pronta; listar arquivos sujos no markdown churnaria o diff a cada save (viola RN-02) | Reimplementar a avaliação (duplicação); listar os caminhos (diff instável) | 🟢 |
| D-06 | `ProgressSection` nova na config canônica com um campo `file: str = ".harness/progresso.md"`; tomls existentes herdam o default (padrão `require_registration`, 022) | Caminho configurável por projeto sem migração; consistente com `DecisionsSection`/`SessionSection` | Caminho hardcoded (destoa da config canônica); seção rica em opções (YAGNI) | 🟢 |
| D-07 | Alertas com severidade (`alta`/`media`): divergência declarado×físico e `feature-dir` inexistente são `alta`; pendência de reconciliação em regression-watch é `media`. Alerta existe enquanto a causa existir; nenhum estado de "alerta visto" | RN-03; o padrão de referência mede, não memoriza | Supressão/ack de alertas (exigiria estado próprio, violando RN-01) | 🟢 |
| D-08 | RF-08 (apêndice no `resume`) fica FORA desta feature; se vier, será feature própria sobre `resume_context` | Could no MoSCoW; toca o contrato do resume e o ruído de contexto merece avaliação isolada | Embutir já (escopo cresce sem critério de aceite próprio) | 🟢 |
| D-09 | Bump minor 2.3.0 → 2.4.0; ficha `MD-0019` | Comando novo em borda pública; padrão das features anteriores | — | 🟢 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| A tabela de estágio físico e a regra de contagem do skill `reversa-requirements` são a semântica autoritativa e estável do ciclo forward | §2, RN-06 | Se o skill mudar a tabela sem tocar `stages.py`, o medidor mente; mitigação: watch item na 026 + comentário cruzado nos dois lugares |
| `_reversa_forward/` e `.reversa/` na raiz do repositório do projeto (mesmos defaults do `state.json` do Reversa) | §2 | Projetos com `output_folder`/`forward_folder` customizados mediriam n/a; aceito (fail-soft) e registrado no contrato |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Serviço de progresso | novo: `src/core/progress/{service,render,stages}.py` | componente-novo | Décima capacidade do hexágono; medição pura + renderizadores md/json |
| Borda CLI | `.harness/harness-core/src/main.py` | regra-nova | Subcomando `progress` (parser + despacho fino); nenhum ramo existente muda |
| Config canônica | `src/core/domain/config.py` | delta-de-dados | `ProgressSection` com default; bump de versão (D-09) |
| Gate de decisões | `src/core/decisions/gate.py` | inalterado (reuso só-leitura) | `evaluate_registration_gate` consumido sem persistência |
| Sessão | `src/core/session/*` | inalterado (reuso só-leitura) | `load_session` para status/âncora |
| Materializadores/perfis/hooks | `harness_profiles.py`, `claude_settings.py`, bootstrap | inalterado (escopo negativo) | Nenhum hook materializado nesta feature (RN-07) |

## 6. Delta no modelo de dados

- Resumo: nenhum campo em `SessionState` ou fichas MD; nasce um artefato **derivado** (`.harness/progresso.md`, análogo ao `microdecisoes.md`/RN-N12) e uma seção de config com default herdado. Detalhe completo em: `data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| CLI `harness progress` (modos, exit codes, formato do markdown e do JSON) | arquivo/processo | `_reversa_forward/026-medidor-progresso-entregaveis/interfaces/progress-cli.md` |

## 8. Plano de migração

1. Dados: n/a (artefato derivado, regenerável a qualquer momento; primeira execução cria o arquivo).
2. Config: tomls existentes herdam `ProgressSection` default; nenhuma regravação.
3. Propagação: fonte única (shim) no ato para migrados; pré-020 no próximo `upgrade`; raiz `~/dev` via `upgrade-raiz.sh` (fluxo acumulado, T028 da 024).

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Deriva de semântica entre `stages.py` e a tabela do skill `reversa-requirements` | médio | média | Módulo único com testes de borda usando fixtures no formato real (crases, tabelas, linhas livres); watch item; comentário cruzado nos dois artefatos |
| Valor volátil vazando para o markdown (lista de sujos, contagens flutuantes) e churnando o diff | médio | média | Revisão explícita do renderizador contra RN-02 no coding; teste de idempotência byte a byte |
| Medição lenta em `_reversa_forward/` grande (26+ features) | baixo | baixa | Leitura direta de arquivos conhecidos, sem varredura recursiva; ~26 `actions.md` é trivial |
| `--em-hook` usado antes de existir integração no bootstrap gera expectativa de guarda automática | baixo | média | Documentar no contrato que a flag é para uso manual/integração futura (RN-07) |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Suíte completa verde (320 + novos)
- [ ] `.harness/progresso.md` gerado neste repositório medindo o estado real (024 pausada, 025 done, 026 ativa)
- [ ] Idempotência byte a byte verificada
- [ ] Ficha `MD-0019` registrada e índice recompilado
- [ ] `regression-watch.md` e `legacy-impact.md` gerados

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-08-11 | Versão inicial gerada por `/reversa-plan` | reversa |
