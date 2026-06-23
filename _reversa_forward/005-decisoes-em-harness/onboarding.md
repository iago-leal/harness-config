# Onboarding: testar a feature `005-decisoes-em-harness`

> Passo a passo executável para validar a relocação dos artefatos de decisão para `.harness/`.
> Pré-requisito: estar na raiz do repo (`/Users/iagoleal/dev/harness`) com a branch da feature.

## 1. Estado antes (baseline)

```bash
ls decisoes/ microdecisoes.md          # devem existir na raiz
./harness decisions                    # deve validar zero erros (baseline verde)
```

## 2. Após a implementação

```bash
# a) os artefatos saíram da raiz e estão em .harness/
test ! -e decisoes && test ! -e microdecisoes.md && echo "raiz limpa: OK"
ls .harness/decisoes/ .harness/microdecisoes.md

# b) o subcomando valida e regenera no novo local
./harness decisions
#   esperado: "Grafo de microdecisões validado com sucesso (zero erros)."
#             "Índice de decisões compilado com sucesso em '.harness/microdecisoes.md'."

# c) histórico preservado pelo git mv
git log --follow --oneline .harness/decisoes/MD-0001.md | head
#   esperado: commits anteriores ao move aparecem

# d) o hook Stop continua funcionando sem mudança de comando
#    (o .claude/settings.json chama "./harness decisions" — destino interno mudou, comando não)
```

## 3. Adapter MCP (se exposto)

```bash
# o tool process_decisions deve operar no novo default .harness/ sem argumentos explícitos
# (validar via cliente MCP, ou inspecionar server.py: defaults apontam para .harness/)
grep -n "process_decisions" harness-core/src/adapters/mcp/server.py
```

## 4. Testes

```bash
cd harness-core && python -m pytest -q     # suíte verde
```

## 5. Critério de "passou"

- Raiz sem `decisoes/` nem `microdecisoes.md`.
- `./harness decisions` verde e índice em `.harness/microdecisoes.md`.
- `git log --follow` com histórico pré-move.
- Suíte de testes verde.
