# Onboarding: testar a feature 018 pela primeira vez

> Feature `018-encerrar-sessao-como-skill` · 2026-06-27
> Comandos a partir da raiz do repo do harness.

## Pré-requisitos

- Suíte do core verde antes de começar: `cd .harness/harness-core && .venv/bin/python -m pytest -q`
- Um diretório de sandbox descartável (no scratchpad).

## Cenário A — `init` materializa a skill nos dois harnesses

1. Crie um sandbox e rode o `init` para `active_harness = claude`; repita para `antigravity`.
2. Verifique:
   - Existe `<sandbox>/.claude/skills/encerrar-sessao/SKILL.md` e `<sandbox>/.claude/skills/encerrar-sessao/scripts/`.
   - Existe `<sandbox>/.agents/skills/encerrar-sessao/SKILL.md` e `scripts/`.
   - O `SKILL.md` tem `name`, `description` e `version` no front-matter.

```bash
test -f "<sandbox>/.claude/skills/encerrar-sessao/SKILL.md" && echo OK-claude
test -f "<sandbox>/.agents/skills/encerrar-sessao/SKILL.md" && echo OK-antigravity
test -d "<sandbox>/.claude/skills/encerrar-sessao/scripts" && echo OK-scripts
```

## Cenário B — os scripts finos importam o core e executam

1. Numa sessão ativa com trabalho commitável, ative a skill (ou rode o script de entrada diretamente).
2. Verifique:
   - O trabalho foi commitado por caminho (nunca `git add -A`).
   - O estado-da-sessão foi gravado e versionado em commit isolado.
   - Uma microdecisão foi registrada quando aplicável (`.harness/decisoes/MD-NNNN.md`).
3. Teste de fumaça do import: rodar o script com o core ausente deve falhar barulhento (mensagem clara), não silencioso.

## Cenário C — `upgrade` migra do artefato antigo para a skill

1. Num sandbox, simule a instalação anterior: crie `.agents/workflows/encerrar-sessao.md` e `.claude/commands/encerrar-sessao.md`, mais um workflow de terceiro.
2. Rode `./harness upgrade`.
3. Verifique:
   - Passaram a existir as skills em `.claude/skills/` e `.agents/skills/`.
   - Os artefatos antigos (`workflows/encerrar-sessao.md`, `commands/encerrar-sessao.md`) sumiram.
   - O workflow de terceiro permanece intacto.

## Cenário D — reconhecimento real (manual, último recurso)

1. No **Claude Code**, confirme que a skill `encerrar-sessao` aparece/ativa.
2. No **Antigravity**, recarregue a janela e peça "encerre a sessão" (ativação semântica). Confirme que a skill conduz o fluxo.

## Verificação de saúde

- Suíte verde: `cd .harness/harness-core && .venv/bin/python -m pytest -q`
- `skill-spec` na skill materializada: score ≥ 80.
- Versão propagada: `harness.toml` do sandbox mostra a nova versão após `upgrade`.
