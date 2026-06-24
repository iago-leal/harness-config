# Onboarding: testar a feature 006 pela primeira vez

> Identificador: `006-harness-core-config-canonica`
> Data: `2026-06-24`
> Público: humano que vai validar a feature manualmente após a codificação.

## Pré-requisitos

- Estar na raiz do repositório: `/Users/iagoleal/dev/harness`
- A venv do core existe: `harness-core/.venv` (se não, ver README do `harness-core`)

## 1. Suíte verde (linha de base)

```bash
cd harness-core
.venv/bin/python -m pytest -q
```

Esperado: todos os testes passam, incluindo os novos (contrato de footprint, seção `[session]`, via única de config).

## 2. Caminho de sessão dirigido por configuração

```bash
# Na raiz do repo
./harness cmd resume        # deve carregar o estado de .harness/estado-da-sessao.md (default)
```

Para provar que o caminho vem da config, edite temporariamente `harness-core/harness.toml`:

```toml
[session]
state_file = ".harness/estado-da-sessao.md"   # troque por um caminho de teste e confirme que CLI e MCP o seguem
```

Esperado: tanto `./harness cmd resume` quanto o tool MCP `session_command` leem do caminho declarado em `[session]`, sem literal chumbado. Reverta a edição ao final.

## 3. Via única de configuração

```bash
grep -rn "load_harness_config" harness-core/src    # esperado: nenhum resultado
./harness cmd resume                               # active_harness vem de load_config tipado
```

## 4. Contrato de footprint (footprint global zero)

```bash
cd harness-core
.venv/bin/python -m pytest -q -k footprint
```

Esperado: o teste passa, afirmando que nenhuma operação do harness escreve fora do repositório de teste, nem sob `~/.claude` ou `~/.agent-memory`. O teste deve **falhar de forma barulhenta** se alguém introduzir uma escrita global (verifique apontando uma escrita para `~/...` num branch de experimento e confirmando a falha).

## 5. Decisão de reversão indexada

```bash
# Na raiz do repo
./harness decisions
```

Esperado: grafo validado com zero erros e `.harness/microdecisoes.md` regenerado, já incluindo a nova ficha `MD-NNNN` que reverte o `MD-0004`, com o backlink correto.

## 6. Zona protegida intacta

Confirme que o autoformat continua recusando tocar a config global:

```bash
./harness format ~/.claude/settings.json   # esperado: no-op (retorna 0, não formata)
```

## Checklist de aceite manual

- [ ] `pytest` verde
- [ ] CLI e MCP leem o caminho de sessão de `[session]`
- [ ] `load_harness_config` não existe mais
- [ ] teste de footprint passa e falha alto quando provocado
- [ ] `./harness decisions` indexa a `MD-NNNN` de reversão sem erro
- [ ] `~/.claude` segue protegido do autoformat
