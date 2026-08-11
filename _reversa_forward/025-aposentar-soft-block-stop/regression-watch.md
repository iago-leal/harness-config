# Regression Watch: aposentar o soft-block do Stop

> Identificador: `025-aposentar-soft-block-stop`
> Data: `2026-08-11`
> Fonte: `legacy-impact.md` desta feature; ficha `.harness/decisoes/MD-0018.md`

## Watch items

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|
| W001 | `src/main.py`, ramo `decisions --gate` (025/D-01) | O stdout sob `--gate` é SEMPRE vazio; nenhum JSON `{"decision":...}` é emitido em nenhum cenário; exit 0 incondicional | ausência | Qualquer JSON de controle voltando ao stdout do `--gate`; turno de Claude bloqueado por este comando |
| W002 | `src/main.py`, ramo `decisions --gate` (025/D-02, D-06) | Pendência inédita emite UMA linha em stderr: `Aviso: [HARNESS:DECISAO_PENDENTE ...] ... (ou declare a ausência ao encerrar com --sem-decisao).`, limitada por `gate_lembrete_fingerprint` (identidade grossa, persistida antes da emissão) | redação | Advisory a cada turno; advisory sem o marker do contrato da 022; fingerprint não persistido (aviso repetindo) |
| W003 | `src/main.py`, ramo `decisions` (025, escopo negativo; RN-N12) | A reindexação do índice derivado continua rodando no fim de turno, com informativos em stderr; sem `--gate`, saída humana e exit codes byte-idênticos ao pré-022 (MD-0006) | presença | Hook `Stop` sem reindexar; texto humano vazando no stdout sob `--gate` |
| W004 | `core/session/close_flow.py`, 3º portão (025/D-04; RN-N44 parte dura) | O portão do encerramento segue intocado: identidade FINA (`verdict.fingerprint`), rearme com trabalho novo, escape `--sem-decisao` com rastro na narrativa; teste-guarda `test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio` presente e sem alteração | redação | Portão rebaixado a advisory; teste-guarda removido/enfraquecido; portão usando identidade grossa |
| W005 | `core/install/harness_profiles.py` + `.claude/settings.json` materializado (025/D-01) | O contrato do hook não mudou: item `Stop → harness decisions --gate` idêntico, nenhuma rematerialização de settings, nenhuma flag nova de política em `DecisionsSection` | ausência | Item de hook alterado/duplicado após upgrade; chave nova tipo `lembrete_*`/`advisory_*` no toml sem microdecisão |
| W006 | `src/main.py` (helps do argparse), `core/domain/config.py` (comentário da `DecisionsSection`) | Os textos gerenciados descrevem o gate como "aviso em stderr, sem bloquear o turno"; nenhuma menção operante a "soft-block JSON" fora de fichas MD e artefatos históricos | redação | Help do `decisions`/`--gate` reprometendo bloqueio; documentação gerada descrevendo o canal antigo |

## Supersessões deliberadas (features 022/023)

Itens de watch anteriores que vigiavam exatamente o comportamento agora aposentado. Na próxima re-extração, devem ser movidos para "Arquivadas" nos arquivos de origem com referência à MD-0018, **não** relatados como regressão:

| Item de origem | O que vigiava | Status pós-025 |
|----------------|----------------|----------------|
| 022 `regression-watch.md` W005 | stdout sob `--gate` reservado ao JSON `{"decision":"block",...}` | Supersedido: o stdout agora é sempre vazio (MD-0018). A metade do item sobre o modo SEM `--gate` continua válida e migra para o W003 desta feature |
| 023 `regression-watch.md` W002 | Máximo 1 soft-block por sessão via identidade grossa | Supersedido no canal (block → advisory); a mecânica de identidade grossa persiste e é vigiada pelo W002 desta feature |
| 023 `regression-watch.md` W004 | Contrato do stdout byte-idêntico à 022 (JSON único) | Supersedido integralmente pelo contrato novo (`interfaces/stop-gate-stdout.md` da 025) |
| 022 `regression-watch.md`, Observação sobre D-04 | Semântica de plataforma do soft-block (`decision: block` alcança o modelo) | Sem objeto: o core não emite mais o JSON; a premissa de plataforma relevante agora é a inversa (ver Observações) |

Itens vizinhos que permanecem plenamente válidos: 022 W001–W004/W006–W010 e 023 W001/W003/W005/W006.

## Reconciliação do `_reversa_sdd/` (RF-06) — ✅ resolvida em 2026-08-11

- `domain.md` §2.20 (RN-N44): reescrita — enforcement em DUAS políticas (advisory idêntico nos fins de turno de Claude e Antigravity; bloqueio só no encerramento), propagada pela fonte única (RN-N36).
- `code-analysis.md` §11: atualizado — o ramo `--gate` emite a linha `Aviso:` em stderr, stdout sempre vazio.
- `state-machines.md`: nota dos gates revisada; sem menção operante ao lembrete bloqueante.
- Executada na re-extração dirigida de 2026-08-11, na mesma rodada que sanou a dívida da MD-0017 (RN-N31 revisada).

## Observações (sem peso de regressão)

- 🟡 Premissa de plataforma (roadmap §4): o stderr de um hook `Stop` com exit 0 não alcança o modelo nem trava o turno no Claude Code. Se uma versão futura do runner reinjetar stderr, o advisory volta a interromper; a mitigação é suprimir a emissão (meia dúzia de linhas em `main.py`).
- Descoberta as-built registrada no contrato (`interfaces/stop-gate-stdout.md`): os informativos da reindexação já saíam em stderr sob `--gate`; o invariante de idempotência é a ausência do marker `DECISAO_PENDENTE`, não o stderr vazio.

## Histórico de re-extrações

### Re-extração 2026-08-11 11:26

> Primeira verificação da 025, na re-extração dirigida de reconciliação das features 024-027. Vereditos por greps dirigidos (`main.py` ramo `--gate`, `gate.py`, `settings.json`, testes) cruzados com os artefatos recém-gerados (`microdecisoes/requirements.md` RN-N44 revisada + RF-06, `microdecisoes/design.md`, `spec-impact-matrix.md`). A seção de reconciliação abaixo foi **resolvida nesta rodada**: `domain.md` §2.20 descreve o enforcement em duas políticas, `code-analysis.md` §11 descreve o advisory em stderr e `state-machines.md` foi revisado. As supersessões deliberadas foram registradas nas seções "Arquivadas" das features 022/023 (tabelas principais fisicamente preservadas, conforme a regra do Reversa).

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | stdout sob `--gate` sempre vazio; nenhum JSON `{"decision":...}` no ramo; exit 0 incondicional. Comentário as-built em `main.py:400` ("022→025: advisory em stderr"). |
| W002 | 🟢 verde | Linha única `Aviso: [HARNESS:DECISAO_PENDENTE ...]` em stderr, limitada por `gate_lembrete_fingerprint` (identidade grossa) persistido **antes** da emissão — máximo um aviso por sessão. |
| W003 | 🟢 verde | Reindexação segue no fim de turno com informativos em stderr (`main.py:376`); sem `--gate`, saída humana e exit codes preservados (MD-0006). |
| W004 | 🟢 verde | 3º portão do encerramento intocado: identidade fina, rearme com trabalho novo; teste-guarda `test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio` presente (`test_close_flow.py:509`). `gate.py` byte-idêntico (confirmado na matriz de impacto). |
| W005 | 🟢 verde | Item `Stop → harness decisions --gate` inalterado no `settings.json`; nenhuma flag nova de política em `DecisionsSection`. |
| W006 | 🟢 verde | Helps e comentários descrevem o gate como aviso em stderr sem bloquear; menções a "soft-block JSON" restritas a fichas MD e artefatos históricos. |

## Arquivadas

_(vazio)_
