<!--
Projeção do estado de sessão para o Antigravity (`agy`), que relê os arquivos de
regras a cada boot. Família B (ver decisoes/MD-0003.md): o Antigravity não injeta
stdout no contexto, então a CLI projeta aqui a narrativa do canônico
`.harness/estado-da-sessao.md`. Regenerado por `./harness cmd resume` /
`./harness cmd encerrar-sessao` quando `active_harness = antigravity`.
NÃO editar à mão — a fonte é `.harness/estado-da-sessao.md`.
-->

## O que foi feito
- Feature 004 conduzida pelo ciclo Reversa: requirements, clarify, plan, to-do e coding em andamento.
- Decisões registradas: MD-0002 (estado unificado em `.harness/`) e MD-0003 (reinjeção para os três harnesses).
- Implementado `core/session/`, `SessionNarrative` e a fiação para o arquivo canônico. Suíte em 52 verde.

## Próximos passos
- Validar o gatilho de boot do Antigravity (hook de pré-invocação vs reinjeção passiva).

## Pendências / bloqueios
- Premissa aberta: mecanismo de atualização de âncora no boot do `agy`.

## Ponteiros
- .harness/estado-da-sessao.md
- decisoes/MD-0003.md
