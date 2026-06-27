---
commit: 0ca68c7d0986c99c9bd968c54d5f0754c39a3cdd
feature: reversa-forward (roteamento) + brief da feature 015
start_time: '2026-06-27T11:07:57.881090+00:00'
status: inactive
---

## O que foi feito
- **Feature 015 (`corrige-encerrar-sessao-noop`) implementada e verificada.** Corrigido o no-op silencioso do `encerrar-sessao`: dois caminhos saíam com `exit 0` sem fechar — hash curto legado (`MalformedSessionStateError` mascarada pela borda) e sessão `inactive` (string "Erro" + `exit 0` no `main.py`). Agora comandos explícitos falham barulhento (`exit ≠ 0`) com mensagem orientadora; `resume`/boot segue não-bloqueante. Nova exceção `NoActiveSessionError`; a borda `cmd` ramifica por nome do comando (o core segue agnóstico, RN-N5). Bump **1.2.51 → 1.2.52** (config, bootstrap, test_init).
- **Verificação real:** suíte do core **185 passed** (4 testes novos eram red contra o código antigo); smoke end-to-end OK — hash curto/inativa → `exit≠0`, `resume` malformado → `exit 0`, caminho feliz → `exit 0` + commit de encerramento com âncora correta.
- **Pipeline forward completo da 015** em uma sessão: requirements (escopo ampliado p/ os 2 no-ops) → clarify (2 dúvidas decididas: falha barulhenta + orientar, sem comando de "abrir"; hash curto sem auto-reparo) → plan → to-do → coding. Artefatos em `_reversa_forward/015-corrige-encerrar-sessao-noop/`.
- **Trabalho commitado manualmente antes do fechamento** (a feature-irmã que automatiza isso ainda não existe).

## Próximos passos
- **PRIORIDADE — leveza do `microdecisoes`.** Investigar por que registrar uma MD virou um mini-ADR (front-matter + 4 seções `D/PORQUÊ/DESCARTADO/ESTADO` + relações + validação de grafo) e propor enxugar. Decisão do mantenedor: priorizar isto **à frente** da oferta-commit-pendente.
- **Depois — feature `oferta-commit-pendente-ao-encerrar`** (brief na raiz): `encerrar-sessao` oferece commitar trabalho solto da working tree (fora de `.harness/`) antes de fechar — exatamente o atrito que tornou este commit manual.
- **Push do bump 1.2.52** para o `harness-config` (pendente de aval) → consumidores recebem via `./harness upgrade`.
- **Re-extração** (`/reversa`) para reconciliar o `_reversa_sdd/` com a 015.
- **Avaliar `.gitignore`** para `.claude/commands/` e `.agents/workflows/` (materializações locais untracked recorrentes).

## Pendências / bloqueios
- O defeito do no-op (hash curto + sessão inativa) está **RESOLVIDO** nesta sessão — era a pendência da sessão anterior.
- Push ainda não feito (aguarda aval); o trabalho está commitado localmente na `main`.

## Ponteiros
- Trilha SDD da 015: `_reversa_forward/015-corrige-encerrar-sessao-noop/` (requirements, roadmap, investigation, data-delta, onboarding, interfaces, actions, legacy-impact, regression-watch).
- Contrato de saída do `cmd`: `_reversa_forward/015-corrige-encerrar-sessao-noop/interfaces/session-command-exit-contract.md`.
- Brief da próxima feature de commit: `BRIEF-oferta-commit-pendente-ao-encerrar.md` (raiz).
- Âncora desta sessão: o commit de trabalho da 015 (gravado pelo fechamento).
