# Legacy impact: 024-oferta-commit-consentida

> Identificador: `024-oferta-commit-consentida`
> Gerado por `/reversa-coding` em 2026-07-24.
> Confidência das origens: todas 🟢 (lidas do `_reversa_sdd/` e do código as-built).

## 1. Arquivos afetados

| Arquivo afetado | Componente (`_reversa_sdd/architecture.md`) | Tipo | Severidade | Justificativa |
|-----------------|----------------------------------------------|------|------------|---------------|
| `src/core/session/close_flow.py` | `session/close_flow` (orquestração) | regra-alterada | HIGH | `run` ganha `com_pendencias` e `versionar_encerramento` tri-estado; resolve o consentimento por borda (D-07/RN-08) e emite o marker pós-fechamento |
| `src/core/session/close_flow.py` | `session/close_flow` (pré-check) | regra-alterada | MEDIUM | `conduct_commit_pendente` passa a devolver `bool` (autorização), anunciar a contagem à frente e perguntar o desfecho de segunda ordem (RN-06) |
| `src/core/session/close_flow.py` | `session/close_flow` (renderizadores) | componente-novo · contrato-alterado | MEDIUM | Nasce `render_encerramento_nao_versionado_marker`/`conduct_encerramento_nao_versionado`; o `acao` do `COMMIT_PENDENTE` vira oferta (RF-01) |
| `src/core/commands/service.py` | `commands/service` | regra-alterada | HIGH | `execute_command` ganha `versionar_estado: bool = True`; quando falso, fecha sem `commit_paths` e grava a linha declarativa (D-03/D-05) |
| `src/main.py` | CLI (`cmd`) | contrato-alterado | MEDIUM | Três flags novas no subparser `cmd`, duas em grupo mutuamente exclusivo; tri-estado repassado ao fluxo |
| `.claude/skills/encerrar-sessao/scripts/encerrar_sessao.py` (+2 cópias) | script fino da skill | contrato-alterado | MEDIUM | Mesmas três flags, repassadas ao mesmo `SessionCloseFlow.run` (paridade RN-N33) |
| `.claude/skills/encerrar-sessao/SKILL.md` (+2 cópias) | skill `encerrar-sessao` | regra-alterada | MEDIUM | Passo 3 "pergunte antes de commitar"; passo novo para a decisão do encerramento, flags e marker; `version` 1.3.0 → 1.4.0 |
| `src/adapters/mcp/server.py` | `adapters/mcp` | inalterado | LOW | Só docstring: assimetria deliberada (D-04); mantém `versionar_estado=True` |
| `src/core/domain/config.py` | `domain/config` | regra-alterada | LOW | Bump minor 2.1.1 → 2.2.0 (D-09); literal lido por regex pela detecção de versão |

## 2. Diff conceitual por componente

### `session/close_flow`

O fluxo de encerramento tinha dois momentos automáticos de escrita no git. O
primeiro — o pré-check de pendência — sempre abortava diante de trabalho sujo,
delegando ao agente commitar e reexecutar. Agora ele **anuncia** e, no terminal,
pergunta o desfecho de segunda ordem (RN-06): `s` autoriza encerrar com o trabalho
fora do histórico (rastro na narrativa), `n` aborta; sem terminal, a autorização
vem só da flag `--com-pendencias`. O segundo momento — o commit de encerramento —
deixa de ser incondicional: `run` resolve um tri-estado (`versionar_encerramento`)
por borda, pergunta `[S/n]` com default afirmativo no terminal e, **sem terminal,
trata o silêncio como recusa** (RN-08). Quando não versiona, emite o novo marker
`ENCERRAMENTO_NAO_VERSIONADO` depois do sucesso e antes da oferta de push. O core
continua sem `git add` de trabalho alheio (RN-N5): toda escrita que ele faz é sobre
ato próprio.

### `commands/service`

`execute_command` ganha o parâmetro `versionar_estado`. O default `True` preserva
todos os chamadores atuais — a CLI (via fluxo), o script fino e a borda MCP. Com
`False`, o serviço fecha o estado no arquivo, **pula** `commit_paths`, acrescenta a
linha declarativa na narrativa (RN-N3: registra ato, não inventa narrativa) e
devolve uma mensagem que anuncia o não-versionamento. A âncora segue capturada
antes de qualquer escrita; sem commit, o HEAD nem se move, e âncora e HEAD
coincidem (RF-12).

### Bordas (CLI, script fino, skill)

As três flags (`--com-pendencias`, `--com-commit-encerramento`,
`--sem-commit-encerramento`) aparecem idênticas nas duas bordas de linha de comando
(RN-N33), com as duas últimas em grupo mutuamente exclusivo (erro de uso barulhento
se ambas vierem, D-08). A skill deixa de prometer commit automático: o passo 3 vira
"pergunte antes de commitar" e um passo novo cobre a decisão do encerramento e a
reação por `motivo` do marker.

## 3. Preservadas (regras 🟢 do `domain.md` intactas)

- **RN-N5** — o core permanece agnóstico ao harness e nunca faz `git add` do
  trabalho alheio; as perguntas que formula são sobre ato próprio.
- **RN-N34** — o pré-check exclui o `session_file` por caminho exato; o estado
  sujo deixado por um fechamento não versionado não vira pendência em cascata.
- **RN-N43** — o gate de decisões exclui o `state_file` do universo; a árvore suja
  do desfecho não versionado não realimenta o 3º portão.
- **RN-N45** — `close_session` zera os dois fingerprints do gate no fechamento do
  arquivo, portanto também no desfecho não versionado.
- **RN-N33** — paridade de superfície entre CLI e script fino da skill, agora com
  as três flags novas.
- **RN-N4** — recusas e desfechos não versionados são anunciados (marker + linha
  na narrativa), nunca silenciosos.

## 4. Modificadas (regras 🟢 alteradas ou removidas)

- **RN-N31** — "o encerramento cria um commit contendo exclusivamente o
  `state_file`". Deixa de ser incondicional: **quando versiona**, segue versionando
  só o `state_file`; mas o versionamento passa a depender de aval (terminal) ou
  flag (sem terminal), e o default sem terminal é **não versionar** (RN-08). É a
  dívida assumida A001 da auditoria — a reconciliação do `_reversa_sdd/domain.md`
  fica para a re-extração dirigida pós-implementação.
