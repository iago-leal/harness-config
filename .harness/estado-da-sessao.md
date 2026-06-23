---
commit: 4338813ba5f23bd5da3659adf92729c5d612b653
feature: 005-decisoes-em-harness
start_time: 2026-06-23T21:55:00+00:00
status: active
---

## O que foi feito
- Feature 004 (estado de sessão unificado em `.harness/` + reinjeção de contexto no SessionStart) implementada, testada (52 verde) e com smoke test do `cmd resume` OK. Fecha a regressão do MD-0001.
- Decisões MD-0002 e MD-0003 registradas; índice regenerado.
- Feature 005 (mover `decisoes/` e `microdecisoes.md` para `.harness/`) preparada: `requirements.md` pronto, com 2 dúvidas de escopo abertas. Decisão do mantenedor: preparar agora, rodar o coding na próxima sessão.

## Próximos passos
- Rodar `/reversa-clarify` da 005 para resolver as 2 dúvidas: escopo dos ganchos externos (guardrail global `~/.agent-memory/bin/guardrail-decisoes.sh` e o hook `UserPromptSubmit` do lembrete) e a localização exata desse hook.
- Seguir `/reversa-plan`, `/reversa-to-do`, `/reversa-coding` da 005.
- Nota: o HEAD avançou após esta narrativa (dois commits desta sessão), então o `resume` da próxima sessão deve alertar divergência de âncora — esperado.

## Pendências / bloqueios
- Bug latente pré-existente: `json` não importado em `harness-core/src/main.py` (`resolve_format_target`). Fora do escopo; corrigir à parte.
- Premissa aberta da 004: gatilho de boot do Antigravity (`agy`) — validar no onboarding.

## Ponteiros
- _reversa_forward/005-decisoes-em-harness/requirements.md
- decisoes/MD-0002.md
- decisoes/MD-0003.md
- _reversa_forward/004-estado-sessao-unificado/
