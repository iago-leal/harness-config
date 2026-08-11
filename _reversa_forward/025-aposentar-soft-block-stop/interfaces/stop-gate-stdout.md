# Contrato: saída do hook `Stop → harness decisions --gate`

> Identificador: `025-aposentar-soft-block-stop`
> Data: `2026-08-11`
> Tipo: contrato de processo (stdout/stderr/exit code consumidos pelo runner de hooks do Claude Code)
> Substitui: contrato as-built das features 022/023 (`_reversa_sdd/code-analysis.md#11`)

## 1. Invocação

- Chamador: runner de hooks do Claude Code, evento `Stop`, conforme `.claude/settings.json` materializado (`{"type":"command","command":"./harness decisions --gate","timeout":10}`).
- A linha de comando **não muda** nesta feature: nenhuma rematerialização de settings é necessária.
- Cwd: raiz do projeto instalado. Sem stdin relevante (o payload JSON do evento é ignorado pelo comando).

## 2. Resposta (depois da 025)

| Situação | stdout | stderr | exit |
|---|---|---|---|
| Sem pendência (fichas em dia, ou sem mudança substantiva) | vazio | apenas linhas informativas da reindexação, quando houver | 0 |
| Pendência inédita na sessão (fingerprint grosso ≠ persistido) | **vazio** | linhas informativas + 1 linha: `Aviso: [HARNESS:DECISAO_PENDENTE mudancas=<resumo>] Registre a decisão como ficha MD-NNNN em <decisoes_dir>/ (ou declare a ausência ao encerrar com --sem-decisao).` | 0 |
| Pendência já avisada na sessão (fingerprint grosso == persistido) | vazio | sem o marker `DECISAO_PENDENTE` (informativas podem aparecer) | 0 |
| Sessão inexistente/fechada | vazio | idem | 0 |
| Erro interno (git indisponível, estado corrompido) | vazio | diagnóstico do fail-open barulhento (comportamento pré-existente, inalterado) | 0 |

Nota as-built: em modo `--gate` as mensagens informativas da reindexação (`Grafo de microdecisões validado...`, `Índice de decisões compilado...`) já saíam em **stderr** para manter o stdout limpo; isso não muda. O invariante de idempotência é a ausência do marker `DECISAO_PENDENTE`, não o stderr vazio.

Invariantes:

- **stdout é sempre vazio.** O comando jamais volta a emitir `{"decision":"block",...}` nem qualquer JSON de controle: o runner do Claude Code nunca recebe instrução de bloqueio deste hook.
- **exit é sempre 0** (fail-open preservado): nenhuma combinação de erro converte o hook em bloqueio de turno.
- O marker segue o contrato da 022 (`_reversa_forward/022-gate-registro-microdecisoes/interfaces/decisao-pendente-marker.md`), gerado por `render_decisao_pendente_marker`; a única mudança é o canal (stderr) e o prefixo `Aviso:`.

## 3. Resposta (antes da 025, para referência)

Pendência inédita emitia no **stdout** o JSON `{"decision": "block", "reason": "[HARNESS:DECISAO_PENDENTE ...] Registre ... e conclua o turno."}`, que o runner reinjetava no modelo, travando a conclusão do turno uma vez por sessão. Este é o comportamento aposentado.

## 4. Efeitos colaterais (inalterados)

Independentemente do canal de saída, o comando continua a:

1. Reindexar o índice derivado de decisões (RN-N12);
2. Persistir `gate_lembrete_fingerprint` no estado da sessão quando emite o aviso (idempotência de uma emissão por sessão);
3. Nunca escrever fora de `.harness/`.

## 5. Idempotência e timeout

- Idempotente por sessão: a segunda invocação com o mesmo estado não produz saída alguma.
- Timeout do runner: 10 s (configurado no settings, inalterado). O comando opera muito abaixo disso; estourar o timeout no Claude Code não bloqueia o turno em hook `Stop`.

## 6. Consumidores conhecidos

| Consumidor | Efeito |
|---|---|
| Runner de hooks do Claude Code | Nenhum (stdout vazio + exit 0 ⇒ turno conclui); stderr aparece ao usuário em transcript/verbose |
| Antigravity (`hook_bridge.py`) | Não usa este contrato: já era advisory por construção; inalterado |
| Testes (`test_cli.py:841-957`) | Passam a asserir stdout vazio e advisory em stderr |
