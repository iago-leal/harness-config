# Onboarding: testar a feature `011-harness-core-em-dot-harness`

> Passo a passo executável para validar a feature pela primeira vez.
> Pré-requisito: feature implementada (actions.md concluído) e `pytest` verde.

## A. Validação no repositório-fonte (pós-move)

1. Confirmar que a raiz tem **um** diretório do tooling, não dois:
   ```bash
   ls -d .harness harness-core 2>/dev/null
   # esperado: lista apenas .harness  (harness-core/ não existe mais na raiz)
   ```
2. Confirmar que o core está versionado no novo caminho:
   ```bash
   git ls-files .harness/harness-core/ | head
   # esperado: arquivos-fonte do core (src/, harness.toml, requirements.txt)
   ```
3. Confirmar que o wrapper resolve o core e roda da raiz:
   ```bash
   ./harness decisions
   ./harness format <algum-arquivo>
   # esperado: execução sem erro de caminho
   ```
4. Suíte de testes verde:
   ```bash
   cd .harness/harness-core && .venv/bin/python -m pytest -q
   ```

## B. Validação do `init` num alvo descartável

1. Criar um repositório git temporário:
   ```bash
   mkdir -p /tmp/harness-alvo && cd /tmp/harness-alvo && git init
   ```
2. Inicializar o harness a partir do upstream (este repo):
   ```bash
   /Users/iagoleal/dev/harness/harness init /tmp/harness-alvo
   ```
3. Conferir o layout de um diretório só:
   ```bash
   test -f /tmp/harness-alvo/.harness/harness-core/src/main.py && echo OK-core-aninhado
   test ! -d /tmp/harness-alvo/harness-core && echo OK-sem-core-na-raiz
   ```
4. Conferir o `.gitignore` do alvo (idempotente):
   ```bash
   grep -c '\.harness/harness-core/' /tmp/harness-alvo/.gitignore   # esperado: 1
   cd /tmp/harness-alvo && git status --porcelain | grep harness-core   # esperado: vazio (ignorado)
   ```
5. Rodar `upgrade` e reconferir que a linha não duplica:
   ```bash
   /tmp/harness-alvo/harness upgrade
   grep -c '\.harness/harness-core/' /tmp/harness-alvo/.gitignore   # esperado: 1
   ```

## C. Validação da falha barulhenta (RN-07)

1. Simular um clone sem o core (cópia vendored ausente por estar gitignorada):
   ```bash
   rm -rf /tmp/harness-alvo/.harness/harness-core
   /tmp/harness-alvo/harness format /tmp/harness-alvo/exemplo.py; echo "exit=$?"
   # esperado: mensagem clara instruindo rodar upgrade/init a partir do upstream
   #           e exit diferente de zero
   ```
2. Restaurar via upgrade e confirmar que volta a funcionar:
   ```bash
   /tmp/harness-alvo/harness upgrade
   test -f /tmp/harness-alvo/.harness/harness-core/src/main.py && echo OK-restaurado
   ```

## D. Migração de uma instalação antiga (se aplicável)

Para um alvo já instalado no layout antigo, após `upgrade` o diretório `harness-core/` antigo fica **órfão** na raiz (a diretriz não-destrutiva não o apaga). Remoção manual:

```bash
# conferir primeiro que o novo caminho existe e funciona
test -f <alvo>/.harness/harness-core/src/main.py && rm -rf <alvo>/harness-core
```

## E. Limpeza

```bash
rm -rf /tmp/harness-alvo
```
