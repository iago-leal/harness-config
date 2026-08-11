# Estado observado em 2026-08-11 (comentarios-concursos)

## Antes da recompilação manual

- `.harness/decisoes/` continha `_cabecalho.md` e `MD-0001.md`.
- `.harness/microdecisoes.md` continha apenas o título "# Microdecisões do Projeto", sem entradas.
- `.harness/decisoes-recentes.md` dizia "Total: 0 fichas".
- Histórico git: `cc3d4492` (criação da ficha MD-0001) seguido de `11541993`
  (`chore(sessao): a sessão da re-extração de 11/08 se encerra com âncora em cc3d4492`).
- `harness.toml`: layout fonte única (`upstream_path = /Users/iagoleal/dev/harness`), sem
  `.harness/harness-core` local; o core executado é o atual (2.6.1).
- Skill instalada `.claude/skills/encerrar-sessao/` idêntica byte a byte ao asset atual do core
  (versão 1.4.0), portanto SEM lógica de vault: a lógica espúria veio da memória por-projeto.

## Comando de verificação e resultado

```
$ cd /Users/iagoleal/dev/comentarios-concursos && ./harness decisions
Grafo de microdecisões validado com sucesso (zero erros).
Índice de decisões compilado com sucesso em '.harness/microdecisoes.md'.
Visão compacta derivada em '.harness/decisoes-recentes.md'.
```

## Depois

- `.harness/microdecisoes.md` lista a MD-0001.
- `.harness/decisoes-recentes.md` diz "Total: 1 ficha".

## Varredura no core (quem compila as visões)

`grep -rn "compile_index\|compile_compact_view" src/ (sem testes)`:

- `src/main.py:393-394` (borda CLI `decisions`)
- `src/adapters/mcp/server.py:84-85` (borda MCP, estendida pela MD-0023)
- `src/adapters/antigravity/hook_bridge.py:130-133` (borda Antigravity)
- **Nenhuma ocorrência** em `src/core/session/close_flow.py` nem em
  `src/core/install/assets/skills/encerrar-sessao/scripts/encerrar_sessao.py`.
