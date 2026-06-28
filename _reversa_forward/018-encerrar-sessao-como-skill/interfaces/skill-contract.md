# Contrato: skill `encerrar-sessao` como adaptador (Claude Code + Antigravity)

> Feature `018-encerrar-sessao-como-skill` · 2026-06-27
> Tipo: contrato de **diretório de skill** consumido por duas ferramentas externas.

A capacidade passa a ser entregue como uma skill (Agent Skill), reconhecida por Claude Code e Antigravity. Este é o contrato que o materializador do harness deve satisfazer.

## Localização (por harness)

| Harness     | Diretório                                   | Reconhecimento                                            |
| ----------- | ------------------------------------------- | --------------------------------------------------------- |
| Claude Code | `<projeto>/.claude/skills/encerrar-sessao/` | Skill do projeto (o Reversa vive aqui).                   |
| Antigravity | `<projeto>/.agents/skills/encerrar-sessao/` | Ativação **semântica** por contexto (não slash visual).   |
| Gemini      | —                                           | Sem superfície de skill definida (perfil devolve `None`). |

A **árvore** da skill é idêntica nos dois; só o diretório-prefixo muda (fornecido pelo `HarnessProfile`).

## Estrutura da skill (árvore)

```
encerrar-sessao/
├── SKILL.md
└── scripts/
    ├── <orquestrador>.py        # ponto de entrada; chama o serviço de fachada do core
    └── <responsabilidades>.py   # finas: commit de trabalho, microdecisão, estado+commit
```

## SKILL.md (front-matter mínimo)

```yaml
---
name: encerrar-sessao
description: >
  <gatilhos de ativação: "encerrar a sessão", "fechar a sessão", … + cláusula NÃO ative>
version: "1.0.0"
---
```

- Obrigatório: `name` + `description` (verificado empiricamente no Antigravity). `version` para rastreabilidade.
- O corpo descreve a sequência e aponta os scripts.

## Comportamento (contrato de execução)

- Ativada (por contexto ou invocação), a skill conduz: regen → (se trabalho pendente) commit por caminho → (quando aplicável) microdecisão → gravação do estado + commit isolado.
- Os scripts **não reimplementam** a lógica: chamam o serviço de fachada do core (`CommandService`/`GitPort`/`DecisionService` via o fluxo extraído).

## Erros e bordas

- **Core não encontrado / não importável**: falha barulhenta (exit ≠ 0 + mensagem), nunca silenciosa.
- **Trabalho pendente fora de `.harness/`**: emite/age sobre o marker `[HARNESS:COMMIT_PENDENTE …]` (contrato da 016), commitando por caminho e repetindo.
- **Falha de commit do estado**: reportada (exit ≠ 0), sem fechar silenciosamente (RN-N31/N32).

## Idempotência e versionamento

- **Idempotência**: materializar repetidamente reescreve a árvore (atômico) e remove o órfão dos caminhos antigos uma vez.
- **Versionamento**: a `version` no front-matter evolui com a skill; a lógica de domínio segue versionada no core.

## Migração

- `upgrade` substitui `.claude/commands/encerrar-sessao.md` e `.agent(s)/workflows/encerrar-sessao.md` pela skill, preservando artefatos de terceiros.
