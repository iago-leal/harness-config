# Actions: Correção do no-op silencioso no `encerrar-sessao`

> Identificador: `015-corrige-encerrar-sessao-noop`
> Data: `2026-06-27`
> Roadmap: `_reversa_forward/015-corrige-encerrar-sessao-noop/roadmap.md`

## Resumo

| Métrica                     | Valor                                       |
| --------------------------- | ------------------------------------------- |
| Total de ações              | 8                                           |
| Paralelizáveis (`[//]`)     | 3                                           |
| Maior cadeia de dependência | 6 (T001 → T002 → T004 → T005 → T006 → T008) |

## Fase 1, Preparação

| ID   | Descrição                                                                                                                                                         | Dependências | Paralelismo | Arquivo alvo                  | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ----------------------------- | ----------- | ------ |
| T001 | Adicionar a exceção nomeada `NoActiveSessionError` (docstring no espírito de `SessionCommitError`: falha barulhenta ao tentar encerrar sessão ausente ou inativa) | -            | -           | `src/core/commands/errors.py` | 🟢          | `[X]`  |

## Fase 2, Testes

| ID   | Descrição                                                                                                                                                                                                                                 | Dependências | Paralelismo | Arquivo alvo             | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------ | ----------- | ------ |
| T002 | Teste de unidade do serviço: `execute_command("encerrar-sessao", ...)` sobre sessão ausente e sobre sessão com `is_active=False` levanta `NoActiveSessionError` (hoje retorna string)                                                     | T001         | `[//]`      | `tests/test_commands.py` | 🟢          | `[X]`  |
| T003 | Testes da borda `cmd` (exit codes): hash curto + `encerrar-sessao` → exit ≠ 0 e stderr; sessão inativa + `encerrar-sessao` → exit ≠ 0; `resume` sobre estado malformado → exit 0 não-bloqueante. Todos devem falhar contra o código atual | T001         | `[//]`      | `tests/test_cli.py`      | 🟢          | `[X]`  |

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                                                                                                                                                                                              | Dependências | Paralelismo | Arquivo alvo                   | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ----------- | ------------------------------ | ----------- | ------ |
| T004 | No ramo `encerrar-sessao` de `execute_command`, substituir o `return "Erro: Nenhuma sessão ativa..."` por `raise NoActiveSessionError(...)` com mensagem que distingue "nada a encerrar" e orienta o boot/`resume` (D-01, RN-03)                                                                                                                       | T001, T002   | -           | `src/core/commands/service.py` | 🟢          | `[X]`  |
| T005 | Na borda `cmd` de `main.py`, ramificar o tratamento de erro pelo nome do comando: para `resume`, `MalformedSessionStateError` segue `exit 0` + aviso em stderr; para comandos explícitos, capturar `MalformedSessionStateError` (hash curto) e `NoActiveSessionError` e terminar com `exit ≠ 0` + mensagem orientadora (D-02, D-03, RN-01/RN-02/RN-04) | T004, T003   | -           | `src/main.py`                  | 🟢          | `[X]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                                                                              | Dependências | Paralelismo | Arquivo alvo                                  | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | --------------------------------------------- | ----------- | ------ |
| T006 | Localizar e atualizar os testes existentes que casavam a string `"Erro: Nenhuma sessão ativa..."` ou assumiam `exit 0` no encerrar sobre estado problemático, adaptando-os à nova semântica de exceção/exit (risco R1) | T004, T005   | -           | `tests/test_commands.py`, `tests/test_cli.py` | 🟡          | `[X]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                                                                   | Dependências     | Paralelismo | Arquivo alvo                                                                               | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------- | ------------------------------------------------------------------------------------------ | ----------- | ------ |
| T007 | Bump de versão 1.2.51 → 1.2.52 nos três pontos sincronizados: `version` em `config.py`, `current_version` em `init_service.py` e a asserção em `test_init.py` (D-05)                        | -                | `[//]`      | `src/core/domain/config.py` (+ `src/core/bootstrap/init_service.py`, `tests/test_init.py`) | 🟢          | `[X]`  |
| T008 | Validação final: suíte do core verde (com os novos testes); rematerializar Claude+Antigravity em sandbox e rodar o smoke dos cenários (caminho feliz + os dois no-ops + `resume` tolerante) | T005, T006, T007 | -           | (verificação; sem arquivo único)                                                           | 🟢          | `[X]`  |

## Notas de execução

<!-- Reservado para /reversa-coding. -->

## Histórico de alterações

| Data       | Alteração                                  | Autor   |
| ---------- | ------------------------------------------ | ------- |
| 2026-06-27 | Versão inicial gerada por `/reversa-to-do` | reversa |
