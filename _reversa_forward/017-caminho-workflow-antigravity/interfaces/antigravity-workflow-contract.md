# Contrato: arquivo de workflow do Antigravity

> Feature `017-caminho-workflow-antigravity` · 2026-06-27
> Tipo: contrato de **arquivo** (convenção consumida por ferramenta externa — Antigravity IDE e CLI).

O Antigravity não expõe um endpoint; o "contrato" é o arquivo de workflow que ele lê do projeto para registrar um slash command. Esta feature alinha a materialização do Harness a esse contrato.

## Localização (request)

- **Diretório:** `<project-root>/.agent/workflows/` (singular). Arquivos fora dele são ignorados pelo registro de slash commands.
- **Arquivo:** `<nome>.md`. O nome do comando deriva do nome do arquivo: `encerrar-sessao.md` → `/encerrar-sessao`.
- **Extensão:** exclusivamente `.md`.

## Formato (payload)

```markdown
---
description: <uma linha; máx. 250 caracteres>
---

<corpo em Markdown; passos/instruções; máx. 12.000 caracteres>
```

- **Obrigatório:** `description`. **Removido nesta feature:** `name` (não exigido pela doc).
- **Corpo:** instruções para o agente. No caso do Harness, delega ao `CommandService` via `./harness cmd …` (a lógica de fechamento não é reimplementada — RN-N5).

## Resposta esperada (comportamento)

- Ao salvar/abrir o projeto, o Antigravity indexa o arquivo e registra `/encerrar-sessao` no chat (IDE e CLI).
- Ao invocar `/encerrar-sessao`, o agente executa os passos do corpo.

## Erros e bordas

- **Arquivo em diretório errado** (`.agents/workflows/`, plural): silenciosamente ignorado pelo registro — sintoma original desta feature.
- **Frontmatter sem `description`:** comportamento indefinido; por isso mantemos `description` sempre presente.
- **Corpo > 12.000 caracteres:** rejeitado; o corpo materializado tem poucas centenas, folga ampla.

## Idempotência e timeouts

- **Idempotência:** materializar repetidamente reescreve o mesmo arquivo (gravação atômica); não acumula duplicatas. A migração remove o órfão do caminho plural numa passada idempotente.
- **Timeouts:** n/a (operação de filesystem local, sem rede).

## Compatibilidade de versões

- `.agent/workflows/` (singular) é reconhecido por todas as versões observadas do Antigravity (o seletor do app aceita `.agent/`, `_agent/` e `.agents/` para edição, mas o registro efetivo de comando observado usa o singular).
- _Rules_ e _skills_ seguem outra convenção (`.agents/`, plural) e estão **fora do escopo** desta feature.
