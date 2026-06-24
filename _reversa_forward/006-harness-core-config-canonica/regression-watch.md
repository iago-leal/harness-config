# Regression Watch: harness-core como módulo per-projeto autocontido

> Identificador: `006-harness-core-config-canonica`
> Data: `2026-06-24`
> Itens que precisam continuar verdadeiros nas próximas extrações reversas. Derivados das regras 🟢 alteradas no `legacy-impact.md`.

## Watch items

| ID   | Origem (arquivo, seção)                                                                                   | Regra esperada após a mudança                                                                                                              | Tipo de verificação | Sinal de violação                                                                                                                    |
| ---- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| W001 | `harness-core/src/main.py` (branch `cmd`) e `harness-core/src/adapters/mcp/server.py` (`session_command`) | O caminho de estado de sessão é lido de `config.session.state_file`, não de literal chumbado                                               | presença            | Literal `".harness/estado-da-sessao.md"` reaparecer como atribuição de `session_file` em qualquer um dos dois drivers                |
| W002 | `harness-core/src/main.py`                                                                                | Via única de configuração: `load_harness_config` permanece removido; tudo por `load_config` tipada                                         | ausência            | `def load_harness_config` ou `load_harness_config(` reaparecer no código                                                             |
| W003 | `_reversa_forward/006.../requirements.md#5` (RF-03), `harness-core/tests/test_footprint.py`               | Footprint global zero: nenhuma escrita do harness mira `~/.claude` ou `~/.agent-memory`; o contrato de footprint existe e falha barulhento | presença            | Escrita do harness sob `~/.claude`/`~/.agent-memory`; ausência do teste de footprint ou do `RecordingFileSystem`                     |
| W004 | `.harness/decisoes/MD-0005.md`                                                                            | A intenção "harness-core substituto da config global" segue revertida; `MD-0005` (módulo per-projeto) ativo                                | presença            | Reintrodução de mecanismo de substituição global (symlink/env/XDG/cópia de `~/.claude`) sem uma nova decisão que substitua `MD-0005` |

## Observações (sem peso de regressão)

- **Cobertura do contrato de footprint (confidência 🟡 da decisão D-03):** o teste cobre os serviços efetivamente exercitados (decisões e os guard-checks diretos). Ao adicionar novos serviços que escrevem artefatos, inclua-os no teste para não criar falsa cobertura. O contrato é teste, não guard de runtime — um caminho de escrita global novo só falha se for exercitado sob `RecordingFileSystem`.
- **RF-04 diferido (fora do escopo da 006):** ensinar os scripts globais `~/.agent-memory/bin/{guardrail-decisoes.sh,microdecisoes-guard.py}` a reconhecer `.harness/` permanece como mudança futura no repo `agent-memory`, não neste repositório.

## Histórico de re-extrações

<!-- Preenchido pelo agente reverso quando `/reversa` rodar de novo. -->

## Arquivadas

<!-- Vazio. Watch items que acumularem vereditos verdes consecutivos suficientes migram para cá. -->
