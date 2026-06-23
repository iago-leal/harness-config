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

> **Escopo:** aplique SEMPRE no `.claude/settings.json` do **projeto**. Nunca edite a configuração global em `~/.claude`.

## Passo 4 — Índice de decisões

- Rode `./harness decisions`. Deve validar o grafo e derivar `.harness/microdecisoes.md` sem erros.

## Passo 5 — Verificação de saúde

Comandos disponíveis na CLI (referência):

{{COMMANDS}}

Confira cada item e reporte aprovado/pendente:

- [ ] `harness-core/.venv` presente e com dependências instaladas
- [ ] `./harness` existe na raiz e é executável
- [ ] Ganchos aplicados no `.claude/settings.json` do projeto
- [ ] `./harness decisions` retorna verde

> **Pendência conhecida (não é falha de instalação):** o `SessionStart` ainda não reinjeta o estado da última sessão no contexto — regressão registrada em `.harness/decisoes/MD-0001.md`, a ser fechada na feature 004. Reporte-a como **pendente conhecida**, não como erro.

## Resultado

Resuma ao final, distinguindo os dois desfechos:

- **Instalação concluída:** todos os itens do Passo 5 aprovados.
- **Concluída com pendência conhecida:** todos aprovados, exceto a reinjeção de estado do `SessionStart` (feature 004) — desfecho esperado, não invalida a instalação.
