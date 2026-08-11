# Contrato: bloco de decisões injetado no SessionStart (visão compacta)

> Identificador: `028-indice-decisoes-sob-demanda`
> Tipo: arquivo derivado + stdout do sink de SessionStart (`cmd resume`)
> Substitui o comportamento da feature 021 (injeção do índice integral), preservando a flag e o canal.

## 1. Artefato em disco: `.harness/decisoes-recentes.md`

Caminho configurável por `decisions.compact_file`. Conteúdo determinístico, derivado das fichas na mesma passada que compila o índice completo:

```markdown
# Decisões recentes — <projeto>

> Visão DERIVADA por `./harness decisions` (hook Stop). Não edite à mão.
> Acervo completo: índice em `.harness/microdecisoes.md`; fichas em `.harness/decisoes/MD-NNNN.md`.
> Antes de buscas amplas, consulte o índice completo.

Total: 20 fichas

- **MD-0020** — Exportador kanban derivado da `Medicao`: ...
- **MD-0019** — Medidor de progresso de entregáveis: ...
- (K mais recentes por ID, ordem decrescente, só títulos)
```

Regras:
- Os títulos vêm da mesma extração usada pelo índice completo (regex `^#\s+MD-\d{4}\s+—\s+(.*)`), fatorada num único ponto do serviço.
- Sem backlinks, sem timestamps, sem valores voláteis; a linha `Total: N fichas` é o único agregado.
- `K = decisions.compact_index_size` (default 10). `K = 0` → só cabeçalho + contagem + ponteiros. `K < 0` → erro barulhento na carga da config.
- Escrita atômica e condicionada a mudança de conteúdo (mesma política passa a valer para o índice completo).
- Paths reais no corpo (ponteiros) refletem `decisions.index_file` e `decisions.dir` da config, não literais fixos.

## 2. Injeção no `cmd resume`

| Condição | Comportamento | Canal |
|----------|---------------|-------|
| `session.inject_decisions_index = false` | Nada é injetado (inalterado vs. 021) | — |
| Flag `true`, `compact_file` EXISTE | Injeta cabeçalho `_HEADER` + conteúdo da visão compacta | stdout (bloco de contexto do SessionStart) |
| Flag `true`, `compact_file` AUSENTE | Fallback: injeta o índice integral (comportamento 021) | stdout + aviso em stderr |
| Flag `true`, ambos ausentes | Nada é injetado (inalterado vs. 021) | — |

- O cabeçalho injetado orienta a consulta sob demanda (evolução do header da 021 `"## Índice de decisões (consulte antes de buscas amplas)"` para apontar o índice completo como passo de consulta).
- Aviso de fallback em stderr, uma linha, apontando a causa ("visão compacta ainda não derivada; rode ./harness decisions ou aguarde o próximo Stop"). Nunca bloqueante, exit code inalterado.
- Gate de `active_harness == "claude"` preservado; a bridge Antigravity continua NÃO injetando (ela só deriva).

## 3. Erros e idempotência

- Ficha ilegível ou relação órfã: mesmo comportamento do índice completo (a validação de integridade roda antes; erro barulhento, nada derivado pela metade).
- Duas execuções consecutivas sem mudança nas fichas produzem bytes idênticos e zero escrita.
- Timeout/latência: derivação é local e O(N) sobre as fichas; sem rede, sem lock adicional além da escrita atômica.
