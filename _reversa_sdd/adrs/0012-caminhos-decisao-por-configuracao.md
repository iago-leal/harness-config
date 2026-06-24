# ADR 0012: Caminhos de decisão e estado fora do código — configuração via `[decisions]` no `harness.toml`

- **Status:** Aceito
- **Data:** feature 005 — commit `c548223`
- **Contexto Técnico:** Módulos `core/domain/config.py`, `core/decisions`, drivers `main.py` e `adapters/mcp/server.py`
- **Escala de Confiança:** 🟢 CONFIRMADO
- **Decisões relacionadas:** MD-0004 (relaciona MD-0002); watch item **W001** da feature 005
- **Completada por:** ADR 0013 (feature 006 — adota a seção `[session]` aqui adiada e fecha T2)
- **Supera (parcialmente):** ADR 0001 (localização e compilador do índice)

## Contexto e Problema

Ao mover as decisões para `.harness/decisoes/` (ADR 0009), havia o risco de simplesmente trocar um literal chumbado (`decisoes/`) por outro (`.harness/decisoes/`) espalhado pelos drivers — perpetuando o acoplamento entre a regra de negócio e o layout físico do repositório. O `DecisionService` precisava ignorar onde os arquivos moram; e o mantenedor precisava poder mudar o layout sem editar código (Princípio nº 5.1: configuração fora do código).

## Decisão

Tornar os caminhos de decisão **configuração tipada**, lida do `harness.toml` e injetada nos serviços:

1. **`HarnessConfig` ganha a seção `[decisions]`** (`DecisionsSection`): `dir = .harness/decisoes`, `index_file = .harness/microdecisoes.md`, `header_file = .harness/decisoes/_cabecalho.md` (defaults). Carregada por `load_config(fs)`.
2. **`DecisionService` recebe os três caminhos por parâmetro** — `load_decisions(directory)`, `compile_index(decisions, output, header)` — e **não chumba** `decisoes/`.
3. **Drivers derivam de `load_config().decisions`:** a CLI (`main.py`, subcomando `decisions`) e o MCP (`server.py`, `process_decisions`) leem a config; nenhum literal de caminho de decisão sobrevive nos drivers.
4. **Índice derivado:** `.harness/microdecisoes.md` é compilado pelo `./harness decisions` (hook `Stop`), com backlinks por verbos inversos; o cabeçalho declara "Não edite à mão". Substitui o antigo `bin/gerar-index-decisoes.sh` do ADR 0001.

## Alternativas Consideradas

- **Literal `.harness/decisoes/` chumbado nos drivers:** descartada — só troca o acoplamento de lugar; mudar o layout exigiria editar código.
- **Seção `[session]` análoga para o estado de sessão:** **não** adotada _nesta_ feature — o escopo da 005 foi deliberadamente restrito a `decisoes/` → `.harness/`, deixando o caminho do estado chumbado em `main.py` e divergente no MCP (origem de T2). 🟢 **Resolvido depois:** a feature 006 (ADR 0013) adotou exatamente esta alternativa — `HarnessConfig` ganhou `SessionSection` (`state_file = .harness/estado-da-sessao.md`) e tanto a CLI (`main.py:169`) quanto o MCP (`server.py:94`) passaram a ler `config.session.state_file`. Nenhum literal de caminho de sessão sobrevive nos drivers; T2 fechado.

## Consequências

- **Positivas:**
  - Regra de negócio (`DecisionService`) desacoplada do layout físico — substituível e testável sem tocar disco real.
  - Layout configurável sem editar código (W001 satisfeito).
  - `harness-core` consolidado como referência canônica de decisões (efeito de MD-0004).
- **Negativas:**
  - 🟡 **Inconsistência menor:** a CLI honra `config.decisions.header_file` (configurável); o MCP **deriva** o header de `os.path.join(dir, "_cabecalho.md")`, ignorando override — coincide com o default, mas não com um override eventual.
  - 🟢 **Dívida (T1) RESOLVIDA (commit `cf73980`):** à época da 005 o caminho configurável **nunca era exercido via MCP** — `server.py` chamava `load_config` sem importá-lo (`NameError`), quebrando `process_decisions`; a configuração só funcionava pela CLI. O fix `cf73980` adicionou `from src.core.domain.config import load_config` em `server.py`, e `process_decisions` passou a exercer o caminho configurável também pelo MCP. Registro histórico preservado; bug corrigido.
