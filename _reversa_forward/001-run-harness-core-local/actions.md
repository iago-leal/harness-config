# Actions: Execução Local do Harness Core

> Identificador: `001-run-harness-core-local`
> Data: `2026-06-23`
> Roadmap: `_reversa_forward/001-run-harness-core-local/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 7 |
| Paralelizáveis (`[//]`) | 4 |
| Maior cadeia de dependência | 5 |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Validar a presença e a integridade da venv em `harness-core/.venv` | - | `[//]` | `harness-core/requirements.txt` | 🟢 | `[X]` |
| T002 | Mapear os ganchos do agente local que serão substituídos | - | `[//]` | `claude-config/settings.json` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Criar caso de teste rápido de validação do wrapper | T001 | `[//]` | `harness-core/tests/test_wrapper.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T004 | Escrever o script wrapper `./harness` na raiz validando a venv e executando o core Python | T001 | - | `harness` | 🟢 | `[X]` |
| T005 | Dar permissão de execução ao script wrapper `./harness` | T004 | - | `harness` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T006 | Atualizar os hooks de SessionStart e PostToolUse no arquivo do agente local | T002, T005 | - | `.reversa/settings.json.snippet` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T007 | Executar validação de fumaça local chamando `./harness decisions` e conferindo compilação de índices | T006 | `[//]` | `ESTADO-DA-SESSAO.md` | 🟢 | `[X]` |

## Notas de execução

Nenhuma nota inserida ainda.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-to-do` | reversa |
