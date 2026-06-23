# Contrato: MCP tool `process_decisions`

> Feature `005-decisoes-em-harness` · 2026-06-23
> Origem no legado: `harness-core/src/adapters/mcp/server.py:42-64`
> Tipo: ferramenta MCP (tool exposto via `@mcp.tool`)

## 1. Assinatura

```python
@mcp.tool(name="process_decisions",
          description="Carrega, valida integridade do grafo e compila o índice consolidado de microdecisões")
def process_decisions(decisoes_dir: str = "<default>", output_file: str = "<default>") -> str
```

`header_file` é **derivado**: `os.path.join(decisoes_dir, "_cabecalho.md")`.

## 2. Delta desta feature

| Parâmetro | Default ANTES | Default DEPOIS |
|-----------|---------------|----------------|
| `decisoes_dir` | `"decisoes"` | `".harness/decisoes"` |
| `output_file` | `"microdecisoes.md"` | `".harness/microdecisoes.md"` |
| `header_file` (derivado) | `decisoes/_cabecalho.md` | `.harness/decisoes/_cabecalho.md` |

- **A assinatura não muda** (mesmos parâmetros, mesmos tipos). Muda apenas o **valor default**.
- Se D-01=B (config), os defaults passam a vir de `load_config().decisions.*` em vez de literais.
- Chamadas que já passam `decisoes_dir`/`output_file` explicitamente não são afetadas.

## 3. Request / Response

- **Request:** invocação do tool com 0..2 argumentos opcionais (string).
- **Response (sucesso):** texto `"Grafo de microdecisões validado com sucesso (zero erros).\nÍndice de decisões compilado com sucesso em '<output_file>'."`
- **Response (erros de integridade):** lista de erros por linha (`- [MD-NNNN] ...`), sem exceção.
- **Erros:** exceções viram `"Erro ao processar decisões: <e>"` (string, não raise).

## 4. Idempotência / timeouts

- **Idempotente:** reexecutar reproduz o mesmo `.harness/microdecisoes.md` (gravação atômica via `write_file_atomic`).
- **Timeout:** não aplicável no nível do tool (operação local de filesystem, rápida).
- **Efeito colateral:** sobrescreve o índice de saída — por isso a ordem do plano (mover antes de validar) importa.
