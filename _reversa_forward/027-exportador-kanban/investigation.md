# Investigation: Exportador kanban derivado da Medicao

> Identificador: `027-exportador-kanban`
> Data: `2026-08-11`

## Fontes examinadas

1. **Board real do fork** (`~/dev/vscode-kanban/.vscode/vscode-kanban.json`): colunas `todo`/`in-progress`/`testing`/`done`; cards com `id` (string numérica no exemplo, mas string livre), `title`, `type` (`bug` observado; `note` é o default da extensão), `prio` (numérico), `creation_time` (ISO 8601 com milissegundos), `description`/`details` como `{content, mime: "text/markdown"}`, `category` (string livre). É a única fonte normativa do schema usada; nenhum campo além dos observados será emitido.
2. **Medidor da 026** (`src/core/progress/`): a `Medicao` já carrega tudo que o mapeamento precisa (ações por fase com status, features com estágio e papel, alertas com severidade). O exportador não exige mudança no que já é medido, apenas o acréscimo das demandas (quinta fonte).
3. **Achados de segurança do próprio fork** (cards do board lido): `workspaces.ts:769` executa `.vscode/vscode-kanban.js` do workspace; motivou o D-11 (o exportador nunca cria nem toca esse arquivo) e o RNF de segurança do requirements.

## Alternativas de integração avaliadas

| Alternativa | Veredito | Razão |
|-------------|----------|-------|
| Exportador no core, acoplado ao `harness progress` (escolhida) | ✅ | Propaga pela fonte única; uma invocação atualiza os dois artefatos derivados; zero TypeScript |
| Mudar a extensão (fork) para ler o `progresso.md`/`--json` | ❌ | Empurra manutenção para o TypeScript do fork; quebra para outros consumidores do board; o board deixaria de ser editável como canal de demandas |
| Script `tools/kanban.py` por projeto | ❌ | Mesmo defeito rejeitado na MD-0019(a): não propaga, duplica |
| Watcher/daemon sincronizando em tempo real | ❌ | Complexidade de processo residente contra o perfil de mantenedor intermitente; `harness progress` já é o momento natural de atualização |

## Padrões aplicados

- **Renderer puro sobre modelo transitório** (026): função sem I/O, borda escreve.
- **Namespace de posse por categoria** (padrão comum em geradores que coabitam com conteúdo manual, ex.: blocos `BEGIN/END generated`): aqui via `category: "harness"`, que o fork já exibe como etiqueta visual.
- **Derived-file-as-input-channel**: a ilha manual do arquivo derivado vira fila de entrada (demandas), lida como fonte própria e nunca confundida com a projeção.

## Pontos verificados a validar no smoke (RF-06)

- 🟡 Tolerância do fork a cards sem campos opcionais (`references`, `assignedTo`).
- 🟡 Renderização de `id` não numérico (`hns:026:T003`) na UI refatorada.
- 🟡 Comportamento do fork ao reordenar/mover cards gerenciados (a exportação seguinte os devolve ao lugar derivado; confirmar que não há efeito colateral no arquivo além do movimento).
