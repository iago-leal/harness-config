# Legacy-impact: feature `005-decisoes-em-harness`

> Data: `2026-06-23`
> Âncora reversa: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`, `_reversa_sdd/code-analysis.md#2.4`

## 1. Arquivos afetados

| Arquivo afetado | Componente (legado) | Tipo | Severidade | Justificativa |
|-----------------|---------------------|------|------------|---------------|
| `.harness/decisoes/` (de `decisoes/`) | Repositório de microdecisões (`code-analysis.md#2.4`) | delta-de-dados | LOW | Relocação física via `git mv`; conteúdo e formato preservados |
| `.harness/microdecisoes.md` (de `microdecisoes.md`) | Índice derivado (`code-analysis.md#2.4`) | delta-de-dados | LOW | Mesmo índice, novo local; regenerado idêntico |
| `harness-core/src/core/domain/config.py` | Loader de config | componente-novo + regra-alterada | MEDIUM | Nova `DecisionsSection`; e correção de `load_config` (faltavam `import toml` e `FileSystemPort` — estava quebrado em runtime) |
| `harness-core/src/main.py` | Composition root CLI, branch `decisions` | regra-alterada | LOW | Caminhos vêm de `load_config().decisions`; comportamento preservado |
| `harness-core/src/adapters/mcp/server.py` | Adapter MCP `process_decisions` | delta-de-contrato-externo | LOW | Defaults `None` resolvidos via config; assinatura compatível |
| `harness-core/harness.toml` | Configuração | regra-nova | LOW | Seção `[decisions]` (override explícito) |
| `harness-core/tests/test_domain.py` | Testes de domínio | regra-nova | LOW | 3 testes do `DecisionsSection`/`load_config` |
| `harness-core/src/core/install/template.md`, `.../session/sinks.py`, `.harness/decisoes/_cabecalho.md` | Documentação/comentários | regra-alterada | LOW | Referências realinhadas a `.harness/` |

## 2. Diff conceitual por componente

- **Repositório e índice de microdecisões.** Saíram da raiz (`decisoes/`, `microdecisoes.md`) para `.harness/` (`.harness/decisoes/`, `.harness/microdecisoes.md`). O `DecisionService` não mudou — continua agnóstico ao local; só a borda passou os novos caminhos.
- **Loader de config.** Ganhou `DecisionsSection` (defaults `.harness/decisoes`, `.harness/microdecisoes.md`, `.harness/decisoes/_cabecalho.md`). Ao ativá-lo, descobriu-se que `load_config` estava latentemente quebrado: usava `toml.loads` e anotava `FileSystemPort` sem importar nenhum (no Python 3.14 a anotação é adiada, então o import "passava", mas `toml.loads` estourava `NameError` em runtime com `harness.toml` presente). Corrigido — isso também conserta o `install-prompt`, que chamava `load_config`.
- **CLI e MCP (dois pontos de entrada).** Ambos passaram a ler os três caminhos de `load_config(fs).decisions` — fonte única, sem caminho chumbado. No `main.py`, removeu-se um import lazy redundante de `load_config` que tornava o nome local e quebrava o branch `decisions` com `UnboundLocalError`.
- **Documentação.** `_cabecalho.md`, `template.md` e o comentário em `sinks.py` agora apontam para `.harness/`.

## 3. Preservadas (regras 🟢 de `domain.md` intactas)

- Formato `MD-NNNN` com front-matter YAML (`id`, `gancho`, `relacoes`, `estado`).
- Derivação do índice: títulos H1, relações de saída e backlinks invertidos (sub-linha `↳`).
- Validação de integridade do grafo: auto-relação e aresta órfã (zero erros após a mudança).
- Máquina de estados da `Decisão` (`state-machines.md#2`) — não tocada.
- Hook `Stop` (`.claude/settings.json`) opera com o mesmo comando `./harness decisions`.

## 4. Modificadas (regras 🟢 alteradas)

- **Local canônico dos artefatos de decisão:** raiz → `.harness/`. É a única regra estrutural alterada de propósito pela feature.
- **`load_config` (config loader):** de código morto/quebrado para funcional. Mudança de correção, não de contrato (assinatura preservada).
