# Onboarding: testar os ganchos do Antigravity pela primeira vez

> Identificador: `009-hooks-antigravity`
> Data: `2026-06-24`
> Público: humano (mantenedor) verificando a feature sem precisar do Antigravity rodando.

Como não há um runtime do Antigravity disponível localmente, a verificação exercita o **contrato** do adaptador por payloads-fixture (exatamente o que o agente entregaria no stdin). Todos os passos rodam no terminal.

## Pré-requisitos

- Repositório do harness com a feature já codada e a `.venv` instalada (`harness-core/.venv`).
- `git` disponível no PATH (já exigido pelo bootstrap).

## Passo 1 — Gerar e inspecionar o `hooks.json`

```bash
# Num diretório de descarte:
mkdir -p /tmp/agy-test && cd /tmp/agy-test && git init -q
/caminho/para/harness/harness init . --harness antigravity
test -f .agents/hooks.json && echo "OK: hooks.json materializado"
python3 -c "import json,sys; json.load(open('.agents/hooks.json')); print('OK: JSON válido')"
```

Esperado: o arquivo `.agents/hooks.json` existe, parseia, e o named-hook `harness` contém `PostToolUse` e `Stop` (e `PreToolUse`, se D-03 ficou na estratégia de captura). Nenhum arquivo criado fora de `/tmp/agy-test`.

## Passo 2 — Conferir o prompt de instalação

```bash
./harness install-prompt --harness antigravity
```

Esperado: o bloco de ganchos é um `hooks.json` (não o aviso "mecanismo … ainda não confirmado"); o texto aponta o caminho `.agents/hooks.json`, não `.claude/settings.json`.

## Passo 3 — Simular `PostToolUse` (formatação)

```bash
# Cria um arquivo Python deformatado e simula o evento de escrita:
printf 'x=1\n' > alvo.py
echo '{"stepIdx": 7, "error": "", "conversationId": "test-uuid",
       "workspacePaths": ["/tmp/agy-test"],
       "transcriptPath": "/tmp/agy-test/.t.jsonl",
       "artifactDirectoryPath": "/tmp/agy-test"}' | ./harness agy-hook post-tool-use
```

Esperado: stdout é `{}` (contrato do `PostToolUse`); exit 0; se a estratégia de captura estiver ativa e houver um `PreToolUse` correspondente para `stepIdx 7`, o `alvo.py` é formatado pelo `ruff`. Sem o par de captura, o passo é no-op silencioso (não bloqueia).

## Passo 4 — Simular o par `PreToolUse` → `PostToolUse`

```bash
echo '{"stepIdx": 8, "conversationId": "test-uuid",
       "toolCall": {"name": "write_to_file", "args": {"TargetFile": "/tmp/agy-test/alvo.py"}},
       "workspacePaths": ["/tmp/agy-test"], "artifactDirectoryPath": "/tmp/agy-test"}' \
  | ./harness agy-hook pre-tool-use
# em seguida, o PostToolUse do mesmo stepIdx:
echo '{"stepIdx": 8, "error": "", "conversationId": "test-uuid",
       "workspacePaths": ["/tmp/agy-test"], "artifactDirectoryPath": "/tmp/agy-test"}' \
  | ./harness agy-hook post-tool-use
cat alvo.py   # deve sair formatado (ruff)
```

Esperado: o `alvo.py` aparece formatado após o `PostToolUse`; ambos os comandos retornam JSON e exit 0.

## Passo 5 — Simular `Stop` (decisões)

```bash
echo '{"executionNum": 1, "terminationReason": "model_stop", "error": "",
       "fullyIdle": true, "conversationId": "test-uuid",
       "workspacePaths": ["/tmp/agy-test"], "artifactDirectoryPath": "/tmp/agy-test"}' \
  | ./harness agy-hook stop
```

Esperado: a indexação de microdecisões roda (equivalente a `./harness decisions`); stdout é um JSON válido que **não** contém `"decision": "continue"` (não queremos prender o laço); exit 0.

## Passo 6 — Verificar respeito ao opt-out

```bash
touch .no-autoformat   # ou o exclude_paths configurado
# repetir o Passo 4; alvo.py NÃO deve ser formatado.
```

Esperado: com `.no-autoformat` presente (ou caminho em `formatting.exclude_paths`), nenhum arquivo é formatado.

## Limpeza

```bash
rm -rf /tmp/agy-test
```

## Critério de aprovação

- `hooks.json` materializado, válido e dentro do repo (Passo 1).
- `install-prompt` sem placeholder e apontando `.agents/` (Passo 2).
- `PostToolUse` devolve `{}` e formata quando há captura (Passos 3–4).
- `Stop` roda decisões sem prender o laço (Passo 5).
- Opt-out respeitado (Passo 6).
- Nada escrito fora do repositório-alvo em nenhum passo.
