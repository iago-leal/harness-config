# Cápsula de reprodução — BUG-20260811-XZ3B

## Ambiente

- **Commit base (defeito):** core 2.6.1 (repo upstream em `72019de`); episódio original no projeto instalado `comentarios-concursos`.
- **Commit da verificação:** repo upstream em `325e4ca` (core 2.6.4).
- **SO:** macOS (Darwin 25.5.0). **Runtime:** Python 3.14 no venv local do core; CI em 3.12 e 3.13.
- **Classificação:** deterministic. **Taxa:** 1/1 no episódio real; 100% nos testes.

## Reprodução original (episódio real, 2026-08-11)

No `comentarios-concursos`, com a ficha `MD-0001` criada e commitada, a sessão foi
encerrada pela borda direta (script da skill `encerrar-sessao` no terminal). Resultado:
`.harness/microdecisoes.md` seguia com "Total: 0 fichas" e `.harness/decisoes-recentes.md`
não existia. Fotografia completa em `estado-observado-20260811.md`; o erro de glob
colateral está em `erro-encerramento-direto.txt`.

## Reprodução em teste (prova vermelho → verde)

Dois níveis de teste reproduzem o defeito nas duas bordas que não derivavam:

1. **Fluxo interativo (`SessionCloseFlow`)** — `tests/test_close_flow.py`, 4 testes novos
   (MD-0025). Antes da correção: FALHAVAM (nenhuma visão derivada no encerramento).
   Smoke com git real em `tests/test_cli.py::test_encerrar_deriva_visoes_com_git_real`
   (o FakeGit mascarava o comportamento do porcelain; o smoke usa `git` de verdade).
2. **Borda MCP (`session_command("encerrar-sessao")`)** — `tests/test_mcp.py::
   test_mcp_encerrar_sessao_deriva_visoes_e_versiona_junto` e
   `tests/test_commands.py::test_execute_encerrar_sessao_caminhos_extras_entram_no_commit`
   (MD-0026). Antes da correção: FALHAVAM (a borda executava pelo `CommandService`, fora
   do flow, e nada derivava nem versionava as visões).

Comando executado (da raiz do core):

```
.venv/bin/python -m pytest -q
```

- Vermelho comprovado em sessão: 4 falhas em `test_close_flow.py` (pré-MD-0025) e 6
  falhas intencionais na rodada da MD-0026, exatamente nos testes novos.
- Verde final (2026-08-11, pós-correção, exit code 0): **405 passed in 22.28s**.
- CI verde nos commits `a904a32` (MD-0025) e `e4a0faf` (MD-0026), Python 3.12 e 3.13.
