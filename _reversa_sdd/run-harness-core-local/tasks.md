# Execução Local do Harness Core, Tarefas de Implementação

> Identificador: `run-harness-core-local`
> Data: `2026-06-23`
> Requirements: `_reversa_sdd/run-harness-core-local/requirements.md`
> Design: `_reversa_sdd/run-harness-core-local/design.md`

## Pré-requisitos
- [x] O sub-módulo `harness-core` está presente no repositório.
- [x] Python 3 e venv configurados localmente em `harness-core/.venv`.
- [x] Dependências do `harness-core` instaladas no ambiente virtual.

## Tarefas

- [x] T-01, Criar o script wrapper de conveniência Bash `harness` na raiz do projeto 🟢
  - Origem no legado: `_reversa_sdd/inventory.md#wrapper-de-conveniencia-raiz-do-projeto` e `_reversa_sdd/adrs/0007-wrapper-conveniencia-raiz.md`
  - Critério de pronto: Executar `./harness` na raiz encaminha a chamada para `harness-core/src/main.py` usando `harness-core/.venv/bin/python3`.
  - Confiança: 🟢 CONFIRMADO

- [x] T-02, Adicionar fail-fast e instruções para venv ausente 🟢
  - Origem no legado: `_reversa_sdd/run-harness-core-local/requirements.md` (RN-02)
  - Critério de pronto: Ao deletar ou renomear temporariamente a pasta `harness-core/.venv`, executar `./harness` falha com código 1, escrevendo erro instrutivo no stderr.
  - Confiança: 🟢 CONFIRMADO

- [x] T-03, Definir snippet de ganchos do agente local 🟢
  - Origem no legado: `.reversa/settings.json.snippet`
  - Critério de pronto: O snippet `.reversa/settings.json.snippet` define regras para os hooks `SessionStart`, `PostToolUse` e `Stop` apontando para o wrapper `./harness`.
  - Confiança: 🟢 CONFIRMADO

## Tarefas de Teste

- [x] TT-01, Teste do happy path do wrapper 🟢
  - Origem no legado: `harness-core/tests/test_wrapper.py:4-19` (`test_wrapper_help`)
  - Critério de pronto: Rodar `PYTHONPATH=harness-core harness-core/.venv/bin/pytest harness-core/tests/test_wrapper.py` e validar se a chamada com `--help` retorna código de saída 0 e imprime o texto correto de ajuda.
  - Confiança: 🟢 CONFIRMADO

- [x] TT-02, Teste do happy path para comandos específicos do core 🟢
  - Origem no legado: `harness-core/tests/test_wrapper.py:21-33` (`test_wrapper_cmd_clarificar`)
  - Critério de pronto: Rodar pytest e validar que chamas a `cmd clarificar` via wrapper executam corretamente sem erros.
  - Confiança: 🟢 CONFIRMADO

## Ordem Sugerida
1. Criar o wrapper `./harness` básico e garantir permissão executável (`chmod +x`).
2. Adicionar validação de caminho absoluto e verificação de venv ausente.
3. Desenvolver o snippet de hooks `.reversa/settings.json.snippet`.
4. Implementar testes automatizados em `harness-core/tests/test_wrapper.py`.

## Lacunas Pendentes (🔴)
* Nenhuma lacuna identificada para esta unit.
