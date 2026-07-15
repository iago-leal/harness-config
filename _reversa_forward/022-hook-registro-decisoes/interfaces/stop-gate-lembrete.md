# Interface: soft-block do `Stop` do Claude (`harness decisions --gate`)

> Contrato entre o subcomando `decisions --gate` e o protocolo de ganchos `Stop` do Claude Code. Materializado pelo `ClaudeProfile` como `Stop → ${CLAUDE_PROJECT_DIR}/harness decisions --gate` (timeout 10).

## Entrada

- stdin: payload do hook (ignorado nesta iteração; lido com guarda `isatty()` como no `agy-hook`).
- Estado consultado: sessão ativa (âncora), working tree, fichas sob `decisions.dir`, `gate_lembrete_fingerprint` do estado.

## Saída (stdout)

| Condição | stdout | Efeito no agente |
|---|---|---|
| Pendência detectada **e** fingerprint ≠ último lembrado | `{"decision": "block", "reason": "[HARNESS:DECISAO_PENDENTE ...] Registre a decisão como ficha MD-NNNN em .harness/decisoes/ (ou declare a ausência ao encerrar com --sem-decisao) e conclua o turno."}` (JSON único, nada mais no stdout) | O agente é impedido de parar **uma vez** e recebe a instrução como `reason`. |
| Pendência com fingerprint já lembrado | vazio | Turno conclui normalmente (lembrete não repete). |
| Sem pendência / gate desligado / sem sessão / âncora ilegível | vazio | Turno conclui normalmente. |
| Erro interno (git indisponível, config corrompida) | vazio | Turno conclui; erro em stderr (RN-05). |

- Em **todos** os casos o processo sai com **exit 0** — o bloqueio é expresso só pelo JSON, nunca por exit 2 (mantém o padrão não-bloqueante dos hooks do harness e evita ambiguidade com falha real).
- Informativos da validação/reindexação (que o `decisions` já fazia) migram para **stderr** sob `--gate`; o stdout é reservado ao JSON (D-09).
- Efeito colateral persistido: ao emitir o bloqueio, grava `gate_lembrete_fingerprint` no estado de sessão (é o que garante "no máximo um lembrete por estado de pendência").

## Sem a flag `--gate`

Comportamento byte-idêntico ao pré-022 (saída humana no stdout): preserva o uso manual e o gancho git `post-merge` (MD-0006).

## Racional do desenho

No `Stop`, stdout com exit 0 não é reinjetado ao modelo; o único canal que o alcança é o bloqueio com `reason` (ver `investigation.md#1`). O fingerprint converte esse bloqueio em lembrete de custo limitado: no pior caso, uma rodada extra por pendência.
