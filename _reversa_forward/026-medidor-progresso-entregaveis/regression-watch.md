# Regression Watch: medidor de progresso de entregáveis

> Identificador: `026-medidor-progresso-entregaveis`
> Data: `2026-08-11`
> Fonte: `legacy-impact.md` desta feature; ficha `.harness/decisoes/MD-0019.md`

## Watch items

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|
| W001 | `core/progress/render.py` (026/RN-02) | O markdown derivado NÃO carrega timestamp de geração, hora, hash volátil nem caminho absoluto da máquina; duas medições do mesmo estado produzem bytes idênticos | ausência | Qualquer valor volátil no `progresso.md`; diff do artefato em commit que não mudou o estado medido |
| W002 | `src/main.py`, ramo `progress` (026/D-06) | O modo padrão grava somente quando o conteúdo muda (`regravado` / `já estava em dia`); escrita atômica; segunda invocação consecutiva é sempre `em dia` | presença | Regravação incondicional; mtime do artefato mudando sem mudança de conteúdo |
| W003 | `src/main.py`, ramo `progress --em-hook` (026/D-03; MD-0018) | Exit 1 APENAS por artefato defasado, com a regravação já aplicada e instrução de re-commit em stderr; alerta grave vira aviso e sai 0; o exit 3 do medidor original nunca é transplantado | ausência | `--em-hook` falhando por alerta (segundo portão de commit); exit 1 sem regravar antes; qualquer exit 3 |
| W004 | `src/main.py`, ramo `progress` (026/RN-N43 aplicada) | Falha real de leitura (fonte presente mas ilegível) ecoa `Erro de leitura:` em stderr e sai com 2 SEM tocar o artefato; o `progresso.md` bom nunca é sobrescrito por medição degradada | presença | Artefato regravado num run com falha; exit 0/1 com fonte corrompida |
| W005 | `core/progress/service.py` (026/D-05) | O serviço é leitura pura: nenhuma escrita em disco, nenhum fingerprint do gate persistido a partir da medição (o reuso de `evaluate_registration_gate` é só-leitura) | ausência | Qualquer `write_*` chamado pelo serviço (teste-guarda `test_harness_medido_com_sessao_fichas_e_gate_puro`, asserção `fs.writes == []`); estado de sessão mudando após `harness progress` |
| W006 | `core/progress/stages.py` × skill `reversa-requirements`, seção "Detecção de feature em andamento" (026/D-04) | A tabela de estágio físico (`vazio`/`requirements`/`plan`/`coding-em-progresso`/`done`) e a regra de contagem (só linhas de tabela terminadas em `\| [ ] \|`/`\| [X] \|`, com ou sem crase) são idênticas nos dois lugares; `stages.py` é o único módulo de paridade | redação | Skill e código divergindo em estágio ou contagem; segunda implementação da tabela surgindo fora de `stages.py` |
| W007 | `core/progress/service.py`, alertas (026/RN-03) | Divergência entre estágio declarado e físico é alerta alta PERSISTENTE (existe enquanto a causa existir), jamais reconciliada silenciosamente pelo medidor; `coding` declarado casa com `coding-em-progresso` físico sem alerta; sem estado de ack | presença | Medidor "corrigindo" metadado sozinho; alerta sumindo sem a fonte ter mudado; campo de ack surgindo sem microdecisão |

## Reconciliação do `_reversa_sdd/` — ✅ resolvida em 2026-08-11

- `architecture.md` / `c4-components.md`: descrevem o componente `core/progress/` (serviço, `stages.py`, renderizadores) e o subcomando `progress` (13º da CLI).
- `domain.md` §2.24: seção nova com as regras do medidor (RN-N50/N51/N52 — derivação pura, artefato sem valor volátil, exit codes, alerta persistente, paridade `stages.py` ↔ skill); unit `progress/` criada (requirements/design/tasks).
- `code-analysis.md` / `inventory.md`: seguem congelados pré-026 — defasagem estrutural **deliberada** desde a f009, registrada em memória e no `confidence-report.md`; não integrava o escopo desta rodada.
- Executada na re-extração dirigida de 2026-08-11, na mesma rodada das features 024/025/027.

## Observações (sem peso de regressão)

- 🟡 Premissa de formato: a contagem de checkboxes assume o formato real dos `actions.md` gerados (checkbox na última coluna da tabela, com ou sem crase). Se um template futuro mover a coluna ou mudar o marcador, `stages.py` e o skill precisam mudar JUNTOS (W006 pega a divergência).
- O modo `--em-hook` existe na CLI, mas nenhum hook git foi instalado nesta feature; a adoção no pre-commit de cada projeto é decisão separada do mantenedor.
- Achado do smoke real: o próprio medidor apontou o `current-stage` do `active-requirements.json` parado em `requirements`; a FONTE foi corrigida para `coding` (o achado não foi suprimido). Ilustra a RN-03 funcionando no primeiro uso.
- A integração com o vscode-kanban do mantenedor foi deliberadamente adiada para a feature 027 (exportador derivado da mesma `Medicao`), por decisão registrada na MD-0019(f).

## Histórico de re-extrações

### Re-extração 2026-08-11 11:26

> Primeira verificação da 026, na re-extração dirigida de reconciliação das features 024-027. Vereditos por leitura direta de `core/progress/{service,stages,render}.py` e do ramo `progress` de `main.py`, cruzada com os artefatos recém-gerados (unit nova `progress/` — requirements/design/tasks —, `domain.md` §2.24, `architecture.md`, `c4-components.md`, `spec-impact-matrix.md`, `code-spec-matrix.md`). Suíte 372 verde. A seção de reconciliação abaixo foi **resolvida nesta rodada**: `architecture.md` e `domain.md` agora descrevem o componente `core/progress/` e o 13º subcomando; a defasagem estrutural de `code-analysis.md`/`inventory.md` (congelados pré-026, conhecida desde a f009) permanece como dívida deliberada e está anotada como tal.

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | `render_markdown` sem timestamp, hora, hash volátil ou caminho absoluto; hora só no `render_json` (`aferido_em`). RN-N51 na unit `progress/`. |
| W002 | 🟢 verde | Modo padrão write-only-when-changed com escrita atômica; segunda invocação consecutiva é sempre "em dia" (idempotência pinada por teste). |
| W003 | 🟢 verde | `--em-hook` sai 1 apenas por artefato defasado; alerta grave vira aviso em stderr com exit 0; nenhum exit 3 no código (D-03). |
| W004 | 🟢 verde | Fonte ilegível → `Erro de leitura:` em stderr, exit 2, nenhum artefato regravado. RN-N51. |
| W005 | 🟢 verde | Serviço em leitura pura: tripwire `fs.writes == []` presente na suíte (`test_progress_service.py:227/321`); gate reavaliado sem persistir fingerprint (RN-N52). |
| W006 | 🟢 verde | `stages.py` é o ponto único de paridade com o skill (tabela de estágio + `_CHECKBOX_ROW` compartilhado por contagem e listagem). Registro 🟡 em `gaps.md#G-18`: a paridade é convenção vigiada por teste, não derivação automática. |
| W007 | 🟢 verde | Divergência declarado × físico é alerta alta persistente, sem ack e sem correção silenciosa; `coding` casa com `coding-em-progresso`. RN-N50/N52. |

## Arquivadas

_(vazio)_
