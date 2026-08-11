# Contexto: encerramento-de-sessao — grafo de relações

> View gerada em 2026-08-11. Não edite à mão. Arestas `proposed` são hipótese, nunca fato,
> e ficam fora de priorização automática. Todos os bugs do contexto estão RESOLVIDOS
> (travados por DONE.md em 2026-08-11).

```mermaid
graph LR
    XZ3B["BUG-20260811-XZ3B (#1) ✅<br/>Encerramento direto não deriva as visões<br/>medium / P2 / fixed"]
    OYKV["BUG-20260811-OYKV (#2) ✅<br/>Memória stale reintroduz ritual do vault<br/>low / P3 / data-repair"]
    TVCP["BUG-20260811-TVCP (#3) ✅<br/>Wrapper do upstream sem âncora de cwd<br/>medium / P2 / fixed"]
    OYKV -- "related-to (supported)" --- XZ3B
    TVCP -- "related-to (supported)" --- XZ3B
```

## Arestas

| De | Tipo | Para | Estado | Evidência |
|----|------|------|--------|-----------|
| BUG-20260811-OYKV | related-to | BUG-20260811-XZ3B | supported | relatados no mesmo episódio real de encerramento no comentarios-concursos (intake 2026-08-11); promovida no fix |
| BUG-20260811-TVCP | related-to | BUG-20260811-XZ3B | supported | achado colateral confirmado da correção do XZ3B: o SessionStart do compact semeou o artefato espúrio durante aquela sessão; promovida no fix |
