# Data delta: Oferta de commit consentida

> Identificador: `024-oferta-commit-consentida`
> Data: `2026-07-23`
> Base: `_reversa_sdd/erd-complete.md` · `_reversa_sdd/data-dictionary.md` · `_reversa_sdd/state-machines.md`
> **Regeneração** — segunda versão, alinhada à RN-08 e à terminologia "commit de encerramento"

## 1. Veredito

**Sem mudança de schema.** Nenhum campo é criado, renomeado ou removido no
`SessionState`, no serializador do `estado-da-sessao.md` ou nas fichas de
microdecisão. A feature 024 altera o **ciclo de vida** do arquivo de estado, não
a sua forma — ao contrário da 022, que precisou dos campos
`gate_lembrete_fingerprint`/`gate_encerramento_fingerprint`.

Consequência prática: um `estado-da-sessao.md` produzido antes ou depois desta
feature é lido pelas duas versões do core sem conversão. Não há migração.

## 2. Entidades tocadas

| Entidade | Arquivo no legado | Mudança |
|----------|-------------------|---------|
| `SessionState` | `_reversa_sdd/data-dictionary.md#SessionState` | Nenhuma no schema. Passa a existir um desfecho de fato novo: *fechado no arquivo, não versionado no histórico* |
| `SessionNarrative.feito` | `_reversa_sdd/data-dictionary.md#SessionNarrative` | Ganha novas linhas declarativas escritas pelo core (D-05), ao lado da já existente "Declarado: sem decisão não óbvia nesta sessão (gate de registro)" |
| Fichas `MD-*.md` | `_reversa_sdd/data-dictionary.md#Decision` | Inalteradas |

## 3. Novas linhas declarativas na narrativa

Formato proposto, análogo ao do `--sem-decisao` (feature 022):

```
Encerramento não versionado: o estado de sessão ficou como mudança pendente no
working tree (motivo: <sem autorização | recusa do usuário>).
```

Quando o encerramento ocorre com trabalho sujo autorizado (`--com-pendencias`),
soma-se:

```
Sessão encerrada com N mudança(s) não commitada(s) por escolha do usuário.
```

Regras:

1. Escrita apenas em desfecho fora do caminho feliz — nunca no fechamento normal.
   Preserva a RN-N3 (o core não inventa narrativa; registra ato).
2. Acrescentada em `narrative.feito`, sem apagar o que o agente escreveu.
3. Visível na retomada seguinte, pela reinjeção já existente (RN-N6). **É a
   principal mitigação do risco da RN-08**: se um encerramento automatizado
   deixar de versionar, a próxima sessão começa vendo o registro disso.

## 4. Efeitos no ciclo de vida (o que de fato muda)

### 4.1 Transição `ATIVA → INATIVA`

A máquina de estado de `_reversa_sdd/state-machines.md` ganha um **desfecho**
novo, não um estado novo:

| Desfecho | Estado do arquivo | Estado do histórico | Como se chega |
|----------|-------------------|---------------------|---------------|
| Fechamento versionado | fechado | commit de encerramento por cima do trabalho | Aval no terminal, `--com-commit-encerramento`, ou borda MCP (D-04) |
| **Fechamento não versionado (novo)** | fechado | intocado | Sem terminal e sem flag (default, RN-08); recusa explícita; `n` no terminal |

Os **três portões** de aborto (pendência → narrativa → registro de decisões)
continuam idênticos e anteriores a ambos os desfechos.

### 4.2 Sessão seguinte

Ponto de atenção real da feature — e o legado já o neutraliza por construção:

| Efeito temido | Realidade | Fonte |
|---------------|-----------|-------|
| O `estado-da-sessao.md` sujo dispara o pré-check de pendência em cascata, impedindo encerrar a sessão seguinte | **Não ocorre.** `pending_work_paths` exclui o `session_file` por caminho exato, não por diretório | `code-analysis.md#session/close_flow`, RN-N34 |
| A âncora diverge do HEAD e o `resume` alerta a cada retomada | **Não ocorre — melhora.** Sem commit de encerramento, o HEAD permanece no último commit de trabalho, que é exatamente a âncora gravada | RN-07, RF-12 |
| O gate de registro de microdecisões (022) enxerga o diff da âncora inflado | **Não ocorre.** O gate exclui o `state_file` do universo de mudanças (`gate.py:84-85`, RN-N43); a árvore suja deixada pelo encerramento não realimenta o terceiro portão | `domain.md#RN-N43` · código as-built — ainda assim, cobrir com teste de duas sessões encadeadas |
| Estados sujos se acumulam ao longo de várias sessões automatizadas | **Possível** sob a RN-08 | Mitigado pela linha declarativa (§3) e pelo marker de aviso; é risco assumido, registrado no `roadmap.md#9` |

### 4.3 Fingerprints do gate

`close_session` zera `gate_lembrete_fingerprint` e `gate_encerramento_fingerprint`
(feature 023). Isso continua acontecendo **no fechamento do arquivo**, portanto
também no desfecho não versionado — os fingerprints não vazam para a sessão
seguinte em nenhum dos caminhos. Nada a mudar; registrado para o teste confirmar.

## 5. Migração

**n/a.** Sem schema novo, sem backfill, sem conversão. A propagação à base
instalada é de código e de skill (ver `roadmap.md#8`), não de dados.
