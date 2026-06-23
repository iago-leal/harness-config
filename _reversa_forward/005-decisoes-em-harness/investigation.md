# Investigação: Artefatos de decisão dentro de `.harness/`

> Feature `005-decisoes-em-harness` · 2026-06-23

## 1. Pesquisa de fundo (no próprio legado)

- `harness-core/src/core/decisions/service.py` — `DecisionService` é **path-agnóstico**: `load_decisions(directory)` e `compile_index(decisions, output_filepath, header_filepath)`. Diretório ausente → lista vazia (`exists` guard, linha 17). Logo, a relocação não exige tocar o domínio. 🟢
- `harness-core/src/main.py:159-183` — composition root do subcomando `decisions`. Chumba `decisoes_dir`, `output_file`, `header_file` (linhas 161-163). 🟢
- `harness-core/src/adapters/mcp/server.py:42-64` — **segundo** ponto de composição: o tool MCP `process_decisions(decisoes_dir="decisoes", output_file="microdecisoes.md")`, com `header_file` derivado (`os.path.join(decisoes_dir, "_cabecalho.md")`). Não citado no requirements; descoberto na investigação. O mesmo arquivo já usa `.harness/sync_cache.json` (linha 32), então `.harness/` já é convenção ali. 🟢
- `harness-core/src/core/domain/config.py` — `load_config(fs, "harness.toml")` → `HarnessConfig` pydantic com `HarnessSection`, `FormattingSection`, `SyncSection`. Adicionar `DecisionsSection` segue o padrão exato existente. 🟢
- `harness.toml` — já tem `[harness]`, `[formatting]`, `[sync]`. Há precedente de config-fora-do-código no projeto. 🟢
- `.claude/settings.json` — hook `Stop` chama `${CLAUDE_PROJECT_DIR}/harness decisions`. O comando não muda; só o destino interno. RF-03 satisfeito sem editar o settings. 🟢

## 2. Alternativas avaliadas (D-01)

| Opção | Descrição | Prós | Contras |
|-------|-----------|------|---------|
| **A — chumbar** | `.harness/...` direto em `main.py` e `server.py` | Mínimo; fiel ao RN-N2 ("apenas o `main.py`"); zero superfície nova | Mantém **2 sites** com a mesma string → risco de drift; tensiona Princípio 5.1 |
| **B — config** | `[decisions]` no `harness.toml` + `DecisionsSection`; ambos os pontos leem do config | Fonte única para os 2 entry points; honra Princípio 5.1; usa loader já existente; baixo custo | Adiciona uma seção de config para o que é convenção fixa (`.harness/`) — possível over-config (Princípio 4) |

**Recomendação:** B. O fator decisivo é a descoberta do 2º site (MCP): com os paths em config, CLI e MCP compartilham uma fonte única e o drift deixa de ser possível. O custo é ~10 linhas num padrão que o projeto já adota. **Pende de `/travar` do mantenedor** (decisão compartilhada).

## 3. Padrões aplicáveis

- **Configuration as code-out / 12-factor (config no ambiente/arquivo, não no binário):** sustenta a opção B.
- **Single Source of Truth:** os dois entry points consumindo o mesmo config eliminam duplicação.
- **`git mv` para relocação versionada:** preserva `--follow`.

## 4. Fontes

- Internas (código do próprio repo, citadas acima). Sem dependência de fonte externa para esta feature.
- Decisões relacionadas: `decisoes/MD-0002.md` (`.harness/` como diretório neutro), `decisoes/MD-0004.md` (direção de harness-core canônico).
