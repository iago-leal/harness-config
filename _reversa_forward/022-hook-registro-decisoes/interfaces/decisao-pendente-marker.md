# Interface: marker `DECISAO_PENDENTE`

> Contrato consumido pelo agente (skill `encerrar-sessao`) no modo sem TTY, na família dos markers `COMMIT_PENDENTE` (016/019) e `NARRATIVA_PENDENTE` (018). Protocolo abortar-e-reexecutar.

## Emissor

`SessionCloseFlow.run` (3º portão), quando `GateVerdict.pendente` é verdadeiro, o fingerprint difere do já registrado e `--sem-decisao` não foi passado.

## Formato (uma linha, stdout, exit 0)

```
[HARNESS:DECISAO_PENDENTE mudancas="<até 20 caminhos separados por vírgula>" total=<N>[ truncado=true mostrados=<M>] acao="registre a(s) decisão(ões) não óbvia(s) desta sessão como ficha .harness/decisoes/MD-NNNN.md (front-matter id/gancho/estado/relacoes + seções D/PORQUÊ/DESCARTADO/ESTADO), commite e rode novamente encerrar-sessao; se não houve decisão não óbvia, rode encerrar-sessao --sem-decisao"]
```

- `mudancas`: caminhos substantivos detectados (diff âncora..HEAD ∪ sujos, já filtrados), cap de 20 como no `COMMIT_PENDENTE`.
- `total`: contagem completa antes do cap; `truncado`/`mostrados` só quando excede.
- Com TTY, a mesma informação sai como texto legível (dualidade padrão dos portões).

## Semântica de re-execução

| Situação na re-execução | Comportamento |
|---|---|
| Ficha `MD-*.md` nova/modificada sob `decisions.dir` | Gate satisfeito; encerramento segue. |
| `--sem-decisao` | Gate satisfeito; linha de declaração anexada a "O que foi feito"; encerramento segue. |
| Nada mudou (mesmo fingerprint) | Anti-loop: encerramento segue com aviso em stderr (RF-04). |
| Mudança nova (fingerprint difere) | Gate reavalia normalmente (pode bloquear de novo, 1 vez). |

## Invariantes

- Exit 0 no bloqueio (padrão dos portões: abortar não é falhar).
- O core nunca cria a ficha nem faz `git add` — só orienta (RN-03 da 016 preservada).
- Emitido só quando `decisions.require_registration` é `True`.
