# Contexto: encerramento-de-sessao — grafo de relações

> View gerada em 2026-08-11. Não edite à mão. Arestas `proposed` são hipótese, nunca fato,
> e ficam fora de priorização automática.

```mermaid
graph LR
    XZ3B["BUG-20260811-XZ3B (#1)<br/>Encerramento direto não deriva as visões<br/>medium / P2"]
    OYKV["BUG-20260811-OYKV (#2)<br/>Memória stale reintroduz ritual do vault<br/>low / P3"]
    TVCP["BUG-20260811-TVCP (#3)<br/>Wrapper do upstream sem âncora de cwd<br/>medium / P2"]
    OYKV -. "related-to (proposed)" .- XZ3B
    TVCP -. "related-to (proposed)" .- XZ3B
```

## Arestas

| De | Tipo | Para | Estado | Evidência |
|----|------|------|--------|-----------|
| BUG-20260811-OYKV | related-to | BUG-20260811-XZ3B | proposed | (mesmo episódio de encerramento no comentarios-concursos) |
| BUG-20260811-TVCP | related-to | BUG-20260811-XZ3B | proposed | (descoberto durante a correção do XZ3B; mesma família de bordas do ciclo de sessão) |
