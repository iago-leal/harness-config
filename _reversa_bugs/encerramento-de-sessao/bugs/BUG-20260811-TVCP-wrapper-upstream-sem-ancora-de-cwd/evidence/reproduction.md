# Cápsula de reprodução — BUG-20260811-TVCP

## Ambiente

- **Commit base (defeito):** repo upstream em `39ccdd4` (wrapper sem âncora).
- **Commit da verificação:** repo upstream em `325e4ca` (wrapper corrigido em `8b3533f`).
- **SO:** macOS (Darwin 25.5.0). **Runtime:** bash real invocado pelo teste; core em
  Python 3.14 (venv local), CI em 3.12 e 3.13.
- **Classificação:** deterministic. **Taxa:** 1/1 no episódio real; 100% no teste.

## Reprodução original (episódio real, 2026-08-11)

Um SessionStart disparado no compact (matcher estendido pela MD-0024) executou
`${CLAUDE_PROJECT_DIR}/harness cmd resume` com o cwd do shell da sessão em
`.harness/harness-core/`. O core resolveu `harness.toml` e `.harness/` pelo cwd e semeou
`.harness/harness-core/.harness/estado-da-sessao.md` (227 bytes, feature
`default_feature`), preservado íntegro em `estado-espurio-harness-core.md`.

Reprodução manual equivalente: `cd .harness/harness-core && ../../harness cmd resume`.

## Reprodução em teste (prova vermelho → verde)

`tests/test_shim.py::test_wrapper_local_do_upstream_ancora_o_cwd`: copia os bytes REAIS
do wrapper `harness` da raiz para um layout fake de upstream (python3 falso que ecoa
ARGS e CWD) e o executa de uma SUBPASTA com bash real; o teste passa somente se o CWD
reportado for a raiz do layout.

Comando executado (da raiz do core):

```
.venv/bin/python -m pytest -q tests/test_shim.py
```

- **Vermelho comprovado:** com o wrapper antigo no lugar (restaurado via
  `git show 39ccdd4:harness`, isto é, o HEAD anterior à correção), o teste FALHOU:
  o CWD reportado era a subpasta, não a raiz.
- **Verde:** com o wrapper corrigido (`cd "$SCRIPT_DIR" || exit 1`), o teste passa;
  suíte completa em 2026-08-11 (exit code 0): **405 passed in 22.28s**.
- CI verde no commit `8b3533f`, Python 3.12 e 3.13.
