# Actions: Script de Bootstrap Simples (harness-init)

> Identificador: `007-bootstrap-harness-init`
> Data: `2026-06-24`
> Roadmap: `_reversa_forward/007-bootstrap-harness-init/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 12 |
| Paralelizáveis (`[//]`) | 4 |
| Maior cadeia de dependência | 7 (T002 → T003 → T004 → T007 → T009 → T010 → T012) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Adicionar suporte a `upstream_path` e `version` no modelo de configuração `HarnessConfig` | - | `[//]` | `harness-core/src/core/domain/config.py` | 🟢 | `[X]` |
| T002 | Criar arquivo de domínio para o serviço de inicialização e evolução | - | `[//]` | `harness-core/src/core/bootstrap/init_service.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Escrever testes automatizados para inicialização do destino em diretório temporário Git | T002 | - | `harness-core/tests/test_init.py` | 🟢 | `[X]` |
| T004 | Escrever testes automatizados para a rotina de evolução (upgrade) e detecção de versão | T003 | - | `harness-core/tests/test_init.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Implementar a rotina de cópia física do core e wrapper para o destino com exclusão de lixo local | T002, T003 | - | `harness-core/src/core/bootstrap/init_service.py` | 🟢 | `[X]` |
| T006 | Adicionar a criação da `.venv` (via `ProcessPort`) e o disparo de ganchos Git locais no fluxo do `init` | T005 | - | `harness-core/src/core/bootstrap/init_service.py` | 🟢 | `[X]` |
| T007 | Implementar a rotina `./harness upgrade` para atualização não destrutiva do core e wrapper no destino | T005, T004 | - | `harness-core/src/core/bootstrap/init_service.py` | 🟢 | `[X]` |
| T008 | Criar método rápido para leitura de versão local e do upstream sem impactos de performance no boot | T001 | `[//]` | `harness-core/src/core/sync/service.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Integrar os subcomandos `init` (apenas upstream) e `upgrade` no argparse da CLI | T006, T007 | - | `harness-core/src/main.py` | 🟢 | `[X]` |
| T010 | Adicionar avisos de versão desatualizada na inicialização da CLI e do servidor MCP se houver upstream | T008, T009 | - | `harness-core/src/main.py` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T011 | Documentar o subcomando `init` e `upgrade` nas instruções dos agentes na raiz | T009 | `[//]` | `CLAUDE.md`, `GEMINI.md` | 🟢 | `[X]` |
| T012 | Executar toda a suíte de testes do pytest no core original para confirmar estabilidade e cobertura | T003, T004, T010 | - | `harness-core/` | 🟢 | `[X]` |

## Notas de execução

<!-- Reservado para /reversa-coding. -->

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-24 | Versão inicial gerada por `/reversa-to-do` | reversa |
