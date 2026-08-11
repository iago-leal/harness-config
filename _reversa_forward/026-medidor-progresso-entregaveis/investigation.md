# Investigation: medidor de progresso de entregáveis

> Identificador: `026-medidor-progresso-entregaveis`
> Data: `2026-08-11`

## 1. Pergunta de fundo

Como dar ao mantenedor intermitente (e aos agentes) uma visão medida de "quanto falta" sem criar uma segunda fonte de verdade, sem ruído de diff e sem transformar o termômetro num novo mecanismo de bloqueio?

## 2. O padrão de referência (comentarios-concursos, estudado em 2026-08-11)

`tools/estado.py` (659 linhas, stdlib apenas) + `ESTADO.md` versionado + hook `pre-commit` (`estado-do-produto`, `always_run: true`). Propriedades transplantáveis, todas confirmadas por leitura do código:

- **Toda linha derivada**: a medição lê acervo/config/entregas e nunca grava estado próprio; recomputar é sempre seguro.
- **Markdown sem carimbo de hora**: o diff de `ESTADO.md` só existe quando o estado do produto mudou; `--json` carimba `aferido_em` porque stdout não é versionado.
- **Gravação só-quando-muda** (`_regravar`): escrever bytes idênticos sujaria o mtime à toa.
- **Semântica invertida no hook** (`_no_hook`): alerta de severidade alta NÃO reprova o commit ("um guardrail que impede a correção do que ele denuncia é pior que guardrail nenhum"); reprova só o arquivo defasado, e o remédio já vem aplicado (regrava antes de reprovar, o autor confere e repete).
- **Divergência é achado**: duas medidas do mesmo fato que discordam viram alerta, jamais reconciliação silenciosa.
- Detalhe não transplantado: exit 3 para alerta alto no modo padrão — no harness, enforcement tem canais próprios (portão do encerramento; advisory da 025) e o medidor não deve virar um segundo gate (roadmap D-03).

## 3. Fontes de medição no harness (mapeamento)

| Fonte | O que dá | Acesso |
|---|---|---|
| `.reversa/active-requirements.json` | Feature ativa declarada, pausadas, metadados informativos | JSON simples; o campo `current-stage` é declarado, não autoritativo — cruza com o físico (alerta RN-03) |
| `_reversa_forward/<NNN>-*/` (artefatos físicos) | Estágio físico (tabela do skill `reversa-requirements`) e progresso por checkbox no `actions.md` | Parsing de markdown; os checkboxes reais estão envoltos em crase (`` `[X]` ``) dentro de células de tabela — pegadinha já documentada na sessão de 2026-08-11 |
| `regression-watch.md` das features | Pendências de reconciliação e supersessões abertas | Parsing leve (seções "Pendência de reconciliação") |
| Estado de sessão + fichas MD + `evaluate_registration_gate` | Sessão ativa/fechada, âncora, total/última ficha, pendência de registro | Serviços existentes, reuso puro sem persistência |

## 4. Alternativas avaliadas

| Alternativa | Veredito | Razão |
|---|---|---|
| Serviço novo no harness-core, comando `harness progress` (escolhida) | ✅ | Propaga pela fonte única, arquitetura testável, mede também as fontes do próprio harness |
| Script `tools/estado.py` copiado para o projeto harness | ❌ | Não propaga, duplica parsing de sessão/decisões que o core já tem, cria segunda stack de manutenção |
| Skill/comando do Reversa (markdown executado pelo agente) | ❌ | Medição por agente é não-determinística e cara; o valor do padrão é ser código auditável e barato de rodar |
| Estender `harness cmd resume` com a medição inline | ❌ | Mistura capacidades (resume é reinjeção de contexto); RF-08 fica como Could para feature própria (D-08) |
| Materializar já o hook pre-commit com `--em-hook` | ❌ (adiado) | Mexe no `bootstrap` e na base instalada; a flag nasce agora, a integração é passo próprio (RN-07) |

## 5. Padrões aplicáveis do próprio projeto

- **Artefato derivado com fonte única** (RN-N12, índice de microdecisões): `progresso.md` é o segundo exemplar do padrão.
- **Config com default herdado** (022, `require_registration`): `ProgressSection` entra sem migração.
- **Fail-open/fail-soft barulhento** (RN-N43): fonte ausente é n/a; fonte corrompida é aviso em stderr sem derrubar o resto.
- **Smoke com git real** (lição da 019): o smoke roda no próprio repositório harness, que tem o cenário mais rico disponível (024 pausada, 025 done, 026 ativa).

## 6. Fontes

- Código de referência: `~/dev/comentarios-concursos/tools/estado.py` (l.28-33, 582-639), `ESTADO.md`, `.pre-commit-config.yaml`, `CLAUDE.md` §medidor.
- Specs do legado: `_reversa_sdd/architecture.md#1` (hexágono), `_reversa_sdd/domain.md#2.5` (RN-N12), `#2.17` (RN-N36..N40), `#2.19-2.21` (RN-N43/N47).
- Semântica do ciclo forward: `.claude/skills/reversa-requirements/SKILL.md` (tabela de estágio físico e contagem de checkboxes).
