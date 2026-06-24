# Instalação do Harness ({{ACTIVE_HARNESS}})

Cole este prompt no agente. Ele executa a instalação local do harness-core, etapa por etapa, de forma **idempotente**: antes de cada passo, verifique o que já existe e complete apenas o que falta. Em caso de falha, **pare e reporte de forma explícita** — nunca siga em silêncio.

## Passo 1 — Ambiente virtual e dependências

- Verifique se `harness-core/.venv` existe. Se não, crie: `python3 -m venv harness-core/.venv`.
- Instale as dependências fixadas: `harness-core/.venv/bin/pip install -r harness-core/requirements.txt`.

## Passo 2 — Wrapper de raiz

- Garanta que o arquivo `./harness` existe na raiz do projeto e é executável (`chmod +x harness`).
- Teste: `./harness --help` deve listar os subcomandos.

## Passo 3 — Ganchos de ciclo de vida ({{ACTIVE_HARNESS}})

{{APPLY_HOOKS}}

```
{{HOOKS_BLOCK}}
```

## Passo 4 — Índice de decisões

- Rode `./harness decisions`. Deve validar o grafo e derivar `.harness/microdecisoes.md` sem erros.

## Passo 5 — Verificação de saúde

Comandos disponíveis na CLI (referência):

{{COMMANDS}}

Confira cada item e reporte aprovado/pendente:

- [ ] `harness-core/.venv` presente e com dependências instaladas
- [ ] `./harness` existe na raiz e é executável
- [ ] Ganchos aplicados conforme o Passo 3 (escopo do harness ativo)
- [ ] `./harness decisions` retorna verde

## Resultado

Resuma ao final: a **instalação está concluída** quando todos os itens do Passo 5 estão aprovados. Se algum ficar pendente, reporte-o de forma explícita — nunca siga em silêncio.
