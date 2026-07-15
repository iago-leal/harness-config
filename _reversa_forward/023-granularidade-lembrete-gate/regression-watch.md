# Regression watch: 023-granularidade-lembrete-gate

> Identificador: `023-granularidade-lembrete-gate`
> Gerado por `/reversa-coding` em 2026-07-15.

## Watch items

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|
| W001 | `core/decisions/gate.py` (023/D-02) | Existe `compute_lembrete_fingerprint(anchor) = sha1(âncora)` e o `GateVerdict` carrega `fingerprint_lembrete` preenchido pelo avaliador | presença | Função ou campo ausentes; identidade grossa voltando a compor HEAD/sujos |
| W002 | `main.py`, ramo `decisions --gate` (023/D-01) | O lembrete compara e persiste `verdict.fingerprint_lembrete` em `gate_lembrete_fingerprint` — no máximo 1 soft-block por sessão | redação | Ramo `--gate` comparando `verdict.fingerprint` (fino); usuários reportando soft-block por arquivo tocado |
| W003 | `close_flow.py`, 3º portão (023/D-06, RF-03) | O portão do encerramento segue comparando `verdict.fingerprint` FINO — trabalho novo sem ficha rearma o bloqueio | redação | Portão usando `fingerprint_lembrete`; teste `test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio` removido ou enfraquecido |
| W004 | `interfaces/stop-gate-lembrete.md` (023) | Contrato do stdout do `--gate` byte-idêntico à 022: JSON `{"decision":"block",...}` único, silêncio nos demais, stderr para avisos, exit 0 sempre | redação | Qualquer mudança no formato do JSON ou vazamento de texto humano no stdout sob `--gate` |
| W005 | `data-delta.md` (023/D-03, RF-05) | Nenhum campo novo no `SessionState` para o lembrete; transição do formato antigo é autoresolvente (comparação por desigualdade), sem código de migração | ausência | Campo de estado novo para política de lembrete; código de migração de fingerprint aparecendo no core |
| W006 | `config.py` (023/D-04) | Não existe flag de configuração para a política do lembrete; `decisions.require_registration` é o único botão do gate | ausência | Chave nova tipo `lembrete_policy`/`reminder_*` na `DecisionsSection` sem microdecisão que a justifique |

## Observações (sem peso de regressão)

- Nenhuma regra de origem 🟡/🔴 foi tocada por esta feature; todos os itens acima derivam de decisões 🟢 verificadas em código nesta sessão.
- A re-extração pendente (pós-022) deve incorporar o gate a `domain.md`/`state-machines.md` já com a dupla identidade da 023 — se incorporar só a semântica da 022 (fingerprint único fino), os itens W001–W003 acusam a defasagem.

## Histórico de re-extrações

### Re-extração 2026-07-15 19:22

> Primeira verificação da 023, na re-extração de reconciliação pós-022/023. A dupla identidade foi incorporada aos artefatos de uma vez (não houve extração intermediária "só-022") — o cenário de defasagem que W001–W003 vigiavam não se materializou.

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | `compute_lembrete_fingerprint(anchor) = sha1(anchor or "")` presente em `gate.py`; `GateVerdict.fingerprint_lembrete` preenchido por `evaluate_registration_gate`. Refletido em `domain.md#2.21` (RN-N47) e `data-dictionary.md` §9. |
| W002 | 🟢 verde | Ramo `--gate` do `main.py` compara `session.gate_lembrete_fingerprint != verdict.fingerprint_lembrete` e persiste a grossa (`main.py:362-365`) — máx. 1 soft-block por sessão. |
| W003 | 🟢 verde | 3º portão compara `verdict.fingerprint` (fino) em `close_flow.py`; teste-guarda `test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio` presente (`test_close_flow.py:481`). |
| W004 | 🟢 verde | Contrato do stdout sob `--gate` byte-idêntico à 022: `json.dumps({"decision": "block", "reason": ...}, ensure_ascii=False)` único; avisos em stderr; `sys.exit(0)` sempre. |
| W005 | 🟢 verde | Nenhum campo novo no `SessionState` (o lembrete reusa `gate_lembrete_fingerprint`); nenhum código de migração — transição por desigualdade, documentada como autoresolvente (ADR 0023). |
| W006 | 🟢 verde | `DecisionsSection` tem apenas `dir`/`index_file`/`header_file`/`require_registration`; nenhuma chave de política de lembrete. |

## Arquivadas

_(vazio)_
