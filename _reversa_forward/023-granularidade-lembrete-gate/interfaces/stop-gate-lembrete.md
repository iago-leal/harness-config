# Contrato: soft-block do fim de turno (`decisions --gate`) — delta da 023

> Base: `_reversa_forward/022-hook-registro-decisoes/interfaces/stop-gate-lembrete.md`
> Este arquivo descreve APENAS o que muda. Tudo que não está aqui permanece como na 022.

## O que NÃO muda (reafirmado)

- Gatilho: hook `Stop` do perfil Claude → `${CLAUDE_PROJECT_DIR}/harness decisions --gate`, timeout 10 s.
- Formato do bloqueio: stdout contendo **só** o JSON `{"decision": "block", "reason": "[HARNESS:DECISAO_PENDENTE mudancas=... total=N acao=...] ..."}`.
- Silêncio: stdout vazio quando não há pendência ou quando o lembrete já foi emitido para o estado corrente.
- Falhas: aviso em stderr, stdout vazio, exit 0 sempre (fail-open barulhento).
- Sem `--gate`: saída humana do `decisions` byte-idêntica (MD-0006).

## O que muda: política de emissão

| Aspecto | 022 (antes) | 023 (depois) |
|---------|-------------|--------------|
| Identidade anti-loop comparada/persistida em `gate_lembrete_fingerprint` | `sha1(âncora + HEAD + sujos ordenados)` — muda a cada arquivo tocado | `sha1(âncora)` — estável durante a sessão |
| Frequência máxima observável | 1 bloqueio por conjunto-de-mudanças (na prática, ~1 por arquivo novo) | **1 bloqueio por sessão** com pendência |
| Rearme intra-sessão | qualquer mudança no working tree | nunca (ficha registrada anula a pendência; a garantia dura fica no portão do encerramento) |
| Transição de formato | — | valor antigo nunca coincide → no máximo 1 bloqueio pós-atualização, depois converge |

## Idempotência

Chamadas repetidas de `decisions --gate` sem mudança de âncora são idempotentes após a primeira emissão: mesmo veredito, nenhuma escrita de estado adicional, stdout vazio.
