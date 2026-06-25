# Instalação do Harness ({{ACTIVE_HARNESS}})

Cole este prompt no agente. Ele executa a instalação local do harness-core, etapa por etapa, de forma **idempotente**: antes de cada passo, verifique o que já existe e complete apenas o que falta. Em caso de falha, **pare e reporte de forma explícita** — nunca siga em silêncio.

## Passo 1 — Ambiente virtual e dependências

- Verifique se `.harness/harness-core/.venv` existe. Se não, crie: `python3 -m venv .harness/harness-core/.venv`.
- Instale as dependências fixadas: `.harness/harness-core/.venv/bin/pip install -r .harness/harness-core/requirements.txt`.

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

- [ ] `.harness/harness-core/.venv` presente e com dependências instaladas
- [ ] `./harness` existe na raiz e é executável
- [ ] Ganchos aplicados conforme o Passo 3 (escopo do harness ativo)
- [ ] `./harness decisions` retorna verde

## Manutenção — atualização e recuperação

- **Atualizar o core:** `./harness upgrade` copia o core do `upstream_path` (registrado no `harness.toml`) e rematerializa os artefatos de IDE com o **código recém-copiado**. Se a versão do upstream não puder ser determinada, o comando **aborta com erro claro** (exit ≠ 0) em vez de fingir sucesso — siga a instrução de recuperação que ele imprime.
- **Forçar a reidratação:** `./harness upgrade --force` ignora a comparação de versão e força recópia + rematerialização. Útil após edição local do core ou quando os artefatos divergem, sem precisar do caminho absoluto do `init`.
- **Recuperar uma instalação no layout antigo** (core órfão `harness-core/` na raiz e nada em `.harness/harness-core/`, sintoma de uma instalação pré-relocação que não consegue se atualizar sozinha): rode o `init` do upstream por **caminho absoluto** e remova o órfão:

  ```bash
  <caminho-absoluto-do-upstream>/harness init <caminho-absoluto-deste-projeto>
  rm -rf <caminho-absoluto-deste-projeto>/harness-core   # órfão, gitignored e não rastreado
  ```

  O `init` copia com o código novo e não compara versão; `.reversa/` e `.harness/decisoes/` são preservados.

## Resultado

Resuma ao final: a **instalação está concluída** quando todos os itens do Passo 5 estão aprovados. Se algum ficar pendente, reporte-o de forma explícita — nunca siga em silêncio.
