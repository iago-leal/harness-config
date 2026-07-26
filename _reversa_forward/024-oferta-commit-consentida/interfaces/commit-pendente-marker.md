# Contrato (delta 024): marker `[HARNESS:COMMIT_PENDENTE …]`

> Identificador: `024-oferta-commit-consentida`
> Tipo: protocolo de borda (core → agente), pré-fechamento
> Base: `_reversa_forward/019-oferta-commit-cobre-harness/interfaces/commit-pendente-marker.md`
> A 024 altera a **semântica da ação** e a **saída interativa**; o formato dos campos é preservado

## 1. O que muda

| Aspecto | 019 (antes) | 024 (depois) |
|---------|-------------|--------------|
| Campo `acao` | Ordem: "git add -- <arquivos> e git commit (mensagem descritiva); depois rode novamente encerrar-sessao" | Oferta: pergunte ao usuário se deve commitar; só então commite e reexecute; se ele recusar e ainda assim quiser encerrar, reexecute com `--com-pendencias` |
| Conjunto `arquivos` | Sujos exceto o `state_file` (RN-N34) | **inalterado** |
| `total`, `truncado`, `mostrados`, teto de 20 | — | **inalterados** |
| Saída no terminal | Lista os caminhos + instrução imperativa | **Contagem primeiro** ("há 7 mudanças não commitadas"), lista abaixo, e então a pergunta "encerrar mesmo assim? `[s/N]`" |
| Efeito sobre o fechamento | Sempre aborta | Aborta, **exceto** com `--com-pendencias` ou resposta afirmativa no terminal |

A lista permanece no terminal porque ali não há agente que resuma por quem lê
(achado A005 da auditoria). Para o agente, o enxuto vale: ele anuncia o `total` e
mostra os caminhos só se o usuário pedir.

## 2. Formato (campos inalterados)

```
[HARNESS:COMMIT_PENDENTE arquivos="<lista separada por vírgula>" total=<n> acao="<texto de oferta>"]
```

Com truncamento acima do teto:

```
[HARNESS:COMMIT_PENDENTE arquivos="…" total=34 truncado=true mostrados=20 acao="…"]
```

- `arquivos`: caminhos sujos relativos à raiz, exceto o `state_file`.
- `total`: total real do conjunto, mesmo quando a lista é truncada. **É o número
  que o agente deve anunciar**, não o de itens exibidos.
- `acao`: texto de oferta (novo conteúdo, mesmo campo).

## 3. Regras de processamento (lado do agente) — **alteradas**

1. **Perguntar primeiro.** Anunciar: *"há `<total>` mudanças não commitadas, quer
   fazer o commit?"*. Não executar nada antes da resposta.
2. Mostrar a lista de `arquivos` se o usuário pedir, ou se o julgamento do item 3
   exigir vê-la para decidir.
3. **Aval concedido:** julgar cada caminho (trabalho real × derivado descartável),
   commitar **por caminho** (`git add -- <path>`, nunca `-A`), com mensagem
   descritiva. O split entre governança (`.harness/decisoes/*`,
   `microdecisoes.md`) e código segue sugerido, não imposto. Reexecutar o
   encerramento.
4. **Aval negado:** perguntar se o usuário quer encerrar assim mesmo.
   - Sim → reexecutar com `--com-pendencias`.
   - Não → não reexecutar; informar que a sessão segue aberta.
5. Nunca inferir o aval a partir do silêncio, nem tratar um pedido anterior de
   autonomia como autorização permanente para escrever no git.

## 4. Invariantes preservados

- O marker é **anterior** ao fechamento.
- O core **lista** via `list_dirty_paths` e **nunca** faz `git add` do trabalho (RN-N5).
- Idempotência: árvore suja → re-emite o marker; limpa (exceto `state_file`) → segue o fluxo.
- `.harness/estado-da-sessao.md` como único sujo → conjunto vazio → tratado como limpo.
- Falha real de `list_dirty_paths` → erro barulhento, sem fechar.

## 5. Compatibilidade

Parsers que extraem `arquivos`, `total`, `truncado` e `mostrados` continuam
válidos sem alteração. Só quebram consumidores que casem o **texto literal** de
`acao` — dentro do repo, os testes das features 016 e 019, ajustados por esta
feature.
