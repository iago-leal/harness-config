# Onboarding — testar a feature 004 pela primeira vez

> Passo a passo executável. Tudo roda local; nenhuma ação fora do terminal.

## Pré-requisitos

1. `cd /Users/iagoleal/dev/harness`
2. Ambiente Python do core ativo: `harness-core/.venv` (o wrapper `./harness` já usa a venv).
3. (Para testar o Gemini) `gemini --version` deve reportar **≥ 0.25**.
4. (Para testar o Antigravity) o binário `agy` instalado e um diretório `.agents/` no projeto.

## Verificação da CLI (independe de harness)

5. Round-trip e parse barulhento (testes):
   ```
   ./harness  # (se houver atalho de testes) ou:
   harness-core/.venv/bin/python -m pytest harness-core/tests/test_commands.py harness-core/tests/test_domain.py -q
   ```
   Esperado: verde, incluindo `parse(render(x)) == x` e o caso "estado presente mas malformado → erro nomeado".

6. Saída de reinjeção manual:
   ```
   ./harness cmd resume
   ```
   Esperado: **somente** um JSON no stdout no formato `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}`. Avisos/erros (ex.: divergência de âncora) NÃO devem poluir o stdout — vão para stderr e/ou para dentro do `additionalContext`.

7. Encerramento (produz a narrativa):
   ```
   ./harness cmd encerrar-sessao
   ```
   Esperado: `.harness/estado-da-sessao.md` atualizado, com front-matter YAML (commit/feature/timestamp/status) e o corpo da narrativa. Repo sujo deve ser sinalizado (regra existente do `encerrar-sessao`).

## Claude Code

8. Abrir uma nova sessão no projeto e confirmar que o estado da sessão anterior aparece no contexto (como system reminder), sem apontar o arquivo à mão.

## Gemini CLI (≥ 0.25)

9. Conferir `.gemini/settings.json` com o hook `SessionStart` apontando para `./harness cmd resume`.
10. Rodar `gemini` no projeto e confirmar que o estado entra no contexto no boot. Se nada aparecer, checar a versão (`gemini --version`) e o log em stderr do hook.

## Antigravity (`agy`)

11. Após um `cmd encerrar-sessao` com `active_harness = antigravity`, confirmar que `.agents/rules/estado-sessao.md` foi gerado com a projeção do canônico.
12. Abrir `agy` no projeto e confirmar que o agente lê o estado (vem dos arquivos de regras relidos no boot).
13. Teste de fumaça do gatilho de âncora: confirmar se há hook de pré-invocação capaz de rodar `cmd resume`; se não houver, registrar que o ramo opera em reinjeção passiva (sem validação ativa de âncora).

## Critério de sucesso

- A suíte passa.
- `./harness cmd resume` emite JSON válido e isolado no stdout.
- Em cada harness disponível, o estado da última sessão chega ao contexto sem intervenção manual.
- `.harness/estado-da-sessao.md` é o único arquivo de estado; os dois antigos não existem mais.
