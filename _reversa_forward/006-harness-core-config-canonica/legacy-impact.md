# Legacy Impact: harness-core como módulo per-projeto autocontido

> Identificador: `006-harness-core-config-canonica`
> Data: `2026-06-24`
> Base de comparação: `_reversa_sdd/` (extração de 2026-06-24, pós-features 003/004/005)

## 1. Tabela de impacto

| Arquivo afetado                                         | Componente (`_reversa_sdd/architecture.md`) | Tipo            | Severidade | Justificativa                                                                                                |
| ------------------------------------------------------- | ------------------------------------------- | --------------- | ---------- | ------------------------------------------------------------------------------------------------------------ |
| `harness-core/src/core/domain/config.py`                | Loader de config tipada (`#1`)              | componente-novo | LOW        | Nova `SessionSection` + campo `session` em `HarnessConfig`; aditivo, default igual ao literal anterior       |
| `harness-core/harness.toml`                             | Configuração do projeto                     | regra-nova      | LOW        | Nova seção `[session]`; sem ela o loader resolve para o mesmo default                                        |
| `harness-core/src/main.py`                              | CLI / composition root (`#1`)               | regra-alterada  | MEDIUM     | Remove `load_harness_config` (dívida T5); branch `cmd` lê `session_file` e `active_harness` de `load_config` |
| `harness-core/src/adapters/mcp/server.py`               | Adapter MCP (`#4`)                          | regra-alterada  | LOW        | `session_command` lê `session_file` de `config.session.state_file`; default idêntico                         |
| `harness-core/tests/helpers.py`                         | Suíte de testes                             | componente-novo | LOW        | `RecordingFileSystem` (Spy de `FileSystemPort`) + `FootprintViolation`                                       |
| `harness-core/tests/test_footprint.py`                  | Suíte de testes                             | componente-novo | LOW        | Contrato de footprint global zero (RF-03)                                                                    |
| `harness-core/tests/{test_domain,test_cli,test_mcp}.py` | Suíte de testes                             | regra-nova      | LOW        | Testes de `[session]`, da remoção de `load_harness_config` e do caminho de sessão via config                 |
| `.harness/decisoes/MD-0005.md`                          | Sistema de decisões (`#1`, ADR 0012)        | regra-nova      | LOW        | Reverte a intenção "config canônica global" do `MD-0004`                                                     |
| `.harness/microdecisoes.md`                             | Índice derivado de decisões                 | delta-de-dados  | LOW        | Reindexado por `./harness decisions` (derivado, não editado à mão)                                           |

## 2. Diff conceitual por componente

- **Loader de config (`config.py`):** ganha `SessionSection(state_file=".harness/estado-da-sessao.md")` e o campo `session` em `HarnessConfig`, espelhando exatamente `DecisionsSection`/`decisions` (padrão do ADR 0012). Mudança puramente aditiva.
- **CLI (`main.py`):** o dict legado `load_harness_config` (segunda via de config, dívida T5) foi removido junto com o `import toml` que só ele usava. O branch `cmd` passou a derivar `session_file` de `config.session.state_file` e `active_harness` de `config.harness.active_harness` (atributo tipado em vez de acesso por chave de dict). O branch `decisions` já usava `load_config` e segue intacto.
- **MCP (`server.py`):** `session_command` deixou de chumbar o caminho do estado de sessão e passou a lê-lo de `load_config(fs).session.state_file`. Fonte única com o CLI elimina o resíduo do antigo T2.
- **Contrato de footprint (`tests/`):** novo `RecordingFileSystem` intercepta toda escrita pela porta hexagonal e levanta `FootprintViolation` se o caminho resolver para fora do repositório ou sob `~/.claude`/`~/.agent-memory`. Quatro testes fixam o invariante; é teste, não guard de runtime (sem mudança de comportamento de produção).
- **Decisão (`MD-0005`):** registra a reversão da premissa global do `MD-0004` (que permanece válido quanto à remoção do sync), com relação `refina MD-0004`.

## 3. Preservadas (regras 🟢 do `_reversa_sdd/domain.md` intactas)

- **BR-MIGRAR-007 (zona protegida):** `formatting/service.py` segue blindando `~`, `~/Notas` e `~/.claude` contra o autoformat. Não tocada; agora também fixada pelo espírito do contrato de footprint.
- **Round-trip de sessão (`parse(render(x)) == x`):** `core/session/serializer.py` intacto; só a origem do caminho mudou, não o formato nem o valor default.
- **Sistema de microdecisões (`MD-NNNN`, índice derivado, backlinks):** inalterado; `MD-0005` segue o mesmo esquema e foi validado/indexado sem erros.
- **`DecisionService` agnóstico ao local:** inalterado; recebe caminhos por parâmetro.
- **Seleção de Sink por `active_harness`:** inalterada; só a leitura do valor passou de dict para atributo tipado.

## 4. Modificadas (regras 🟢 alteradas ou removidas)

- **Origem do caminho de estado de sessão:** era literal chumbado em dois drivers (`main.py`, `server.py`); passou a ser configuração (`[session]`). O VALOR canônico (`.harness/estado-da-sessao.md`) é preservado; muda a FONTE.
- **Via de configuração:** as duas vias coexistentes (dívida T5, `load_harness_config` dict × `load_config` tipada) foram unificadas numa só via tipada. `load_harness_config` deixou de existir.
- **Intenção "harness-core substituto da config global" (`MD-0004`):** revertida por `MD-0005`. A parte do `MD-0004` que removeu o sync cross-harness permanece válida; apenas a premissa de canonicidade global foi revista para "módulo per-projeto".
