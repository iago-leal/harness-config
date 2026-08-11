# Investigation: aposentar o soft-block do Stop

> Identificador: `025-aposentar-soft-block-stop`
> Data: `2026-08-11`

## 1. Pergunta de fundo

Como remover a interrupção de turno causada pelo lembrete de microdecisão sem perder (a) a garantia de registro, (b) a reindexação do índice no fim de turno e (c) a observabilidade da pendência?

## 2. O canal do hook Stop no Claude Code (fundamento)

Documentado na MD-0015 e reconfirmado pelo código as-built (`main.py:345-351`): no hook `Stop`, o único canal que alcança o modelo é o JSON `{"decision":"block","reason":...}` no stdout. Stdout sem JSON com exit 0 conclui o turno normalmente; stderr com exit 0 é visível ao usuário (transcript/verbose), não ao modelo. Disso decorrem as duas pontas desta feature:

- rebaixar o canal de stdout-JSON para stderr **elimina por construção** a possibilidade de interrupção;
- o custo é o aviso deixar de alcançar o modelo no fim de turno — o agente só reencontra a pendência no portão do `encerrar-sessao`, que é exatamente onde a MD-0016 já situava "a garantia real".

## 3. Histórico da decisão (o que muda em relação às MD-0015/0016)

A MD-0015 criou o enforcement híbrido (portão + lembrete + advisory) e a MD-0016 o atenuou (um lembrete por sessão). A alternativa "remover o lembrete e confiar só no portão" foi **descartada** na MD-0016 item (d) com o argumento do "aviso com contexto fresco". A experiência subsequente derrubou o argumento na prática: mesmo um único bloqueio por sessão interrompe o turno em andamento no momento errado (evidência viva: o soft-block disparou no meio da fase de diagnóstico desta própria refatoração, apontando 100 mudanças herdadas que não eram trabalho da sessão). O mantenedor decidiu em 2026-08-11 readotar a alternativa descartada, com a atenuante do advisory em stderr — que a MD-0015 item (b) havia rejeitado como *substituto* do enforcement, não como complemento do portão, que é o desenho desta feature.

## 4. Alternativas avaliadas

| Alternativa | Veredito | Razão |
|---|---|---|
| Rebaixar o block a advisory em stderr, mesmo comando de hook (escolhida) | ✅ | Zero interrupção, zero rematerialização, propagação automática pela fonte única, observabilidade preservada |
| Remover o hook `Stop` do `ClaudeProfile` | ❌ | Perde a reindexação do índice de decisões no fim de turno (RN-N12) e exige regravar `settings.json` em toda a base |
| Desligar por config (`require_registration = false`) | ❌ | Desligaria também o portão do encerramento — a garantia dura que se quer manter; o botão é único por decisão da 022 |
| Flag nova de política no toml (lembrete on/off) | ❌ | YAGNI, já descartada na MD-0016 item (e); a decisão do mantenedor é definitiva, não configurável |
| Suprimir o veredito por completo no Stop | ❌ | Perde a observabilidade sem ganho: stderr não interrompe nada; requirements §10 |

## 5. Efeito na base instalada (análise de propagação)

- **Projetos na fonte única (020/migrados):** o shim executa `main.py` do upstream; o comportamento novo vale no commit seguinte do upstream, sem qualquer ação por projeto.
- **Projetos no layout copiado (pré-migrate):** seguem com o core antigo (e o soft-block) até `harness upgrade`/`harness migrate` — mesmo fluxo de propagação já pendente das MD-0015/0016/0017 (T028 da feature 024, pausada).
- **Raiz `~/dev` (instalação adaptada):** converge via `.harness/upgrade-raiz.sh`, que desde o commit `536577c` sincroniza a versão do toml e deduplica ganchos.
- **Nenhum `settings.json` muda**: o item `Stop → decisions --gate` permanece correto em todas as bordas.

## 6. Padrões aplicáveis do próprio projeto

- **Mudança na fonte, não nos materializados** (MD-0014): alterar o comportamento onde ele nasce, para que `init`/`upgrade` futuros não reintroduzam o indesejado.
- **Transição autoresolvente sem migração** (023): reuso de campo existente; valores antigos convergem sozinhos.
- **Supersessão explícita no regression-watch** (padrão MD-0014 na re-extração de 2026-07-15): itens das features 022/023 que vigiam o block JSON serão marcados como supersedidos pela 025, nunca deixados vermelhos sem explicação.

## 7. Fontes

- Código as-built: `.harness/harness-core/src/main.py:375-416`, `src/core/decisions/gate.py`, `tests/test_cli.py:841-957`, `tests/test_close_flow.py:481`.
- Specs: `_reversa_sdd/domain.md#2.20-2.21` (RN-N43..N47), `_reversa_sdd/code-analysis.md#11`.
- Fichas: `.harness/decisoes/MD-0015.md`, `MD-0016.md` (políticas revertidas), `MD-0014.md` (precedente de aposentadoria na fonte).
- Inventário de pontos de pausa da sessão 2026-08-11 (diagnóstico que originou a feature).
