# Roadmap: Oferta de commit consentida (fim do commit automático)

> Identificador: `024-oferta-commit-consentida`
> Data: `2026-07-23`
> Requirements: `_reversa_forward/024-oferta-commit-consentida/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA
> **Regeneração** — esta é a segunda versão, escrita após a auditoria
> (`audit/cross-check.md`) e a segunda rodada de `/reversa-clarify`. A primeira
> versão assumia default afirmativo sem terminal; a RN-08 inverteu isso.

## 1. Resumo da abordagem

A mudança é de **protocolo de consentimento**, não de mecânica git: nenhuma
função que escreve no repositório muda de lugar, muda quem autoriza chamá-la.
Dois pontos de decisão passam a existir no `SessionCloseFlow` — commitar o
trabalho pendente (com a pergunta de segunda ordem em caso de recusa) e gravar o
commit de encerramento —, e cada um resolve-se conforme a borda.

No terminal, o core **pergunta** pelo `asker` já injetado desde a feature 014,
sempre sobre o que ele mesmo executa: como não versiona trabalho alheio (RN-N5),
pergunta o desfecho do encerramento, não o commit do trabalho — este cabe ao
agente, que o cumpre. Sem terminal, não há a quem perguntar, e o silêncio deixa de
autorizar: o commit de encerramento **só ocorre com flag explícita** (RN-08), e a
ausência produz um estado não versionado mais um marker de aviso. Esquecimento do
agente, portanto, erra para o lado de não escrever no histórico.

## 2. Princípios aplicados

`.reversa/principles.md` não existe neste projeto — nenhum princípio formal a
confrontar. Valem as regras do próprio legado, tratadas como invariantes.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| RN-N5 — core agnóstico, não versiona trabalho alheio | O core ganha perguntas, não ganha `git add`; a pergunta que ele faz é sempre sobre ação própria (D-02) | respeita |
| RN-N4 — erro e recusa barulhentos | Todo desfecho sem versionamento é anunciado, com o que ficou pendente e o que fazer depois | respeita |
| RN-N33 — fonte única do encerramento (CLI + skill) | Ambas as bordas expõem as mesmas flags e consomem o mesmo `SessionCloseFlow` | respeita |
| RN-N34 — pendência restrita ao arquivo de estado | Preservada intacta; é ela que impede o estado sujo de virar pendência em cascata na sessão seguinte | respeita |
| RN-N31 — encerramento versiona o estado num commit isolado | **Alterada por decisão do usuário**: o commit deixa de ser incondicional. A regra sobrevive como "quando versiona, versiona exclusivamente o `state_file`" | conflita (deliberado) |

O conflito com a RN-N31 é o achado A001 da auditoria. Não é impedimento: é dívida
de documentação, a saldar por reconciliação do `_reversa_sdd/` depois da
implementação, mais uma ficha de microdecisão registrando a inversão de política.

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Respostas do modo não interativo trafegam por **flags** (`--com-pendencias`, `--com-commit-encerramento`, `--sem-commit-encerramento`), não por novo canal de entrada | Reaproveita o protocolo abortar-e-reexecutar e a família do `--sem-decisao` (022); a decisão fica visível na conversa e no rastro do comando | (a) ler `stdin` sem TTY — `EOFError` no fluxo de hook; (b) arquivo de resposta em `.harness/` — scratch novo, erro já cometido e revertido na MD-0015; (c) variável de ambiente — decisão invisível | 🟢 |
| D-02 | No terminal, o core pergunta **"encerrar mesmo com N mudanças não commitadas?"**; a pergunta "quer que eu commite?" fica com o agente | O core não pode cumprir a segunda sem violar a RN-N5; perguntar o que não se pode executar produz oferta falsa | (a) core commitar o autorizado, com mensagem gerada — viola RN-N5 e obriga o core a inventar mensagem; (b) core só listar, como hoje — não atende ao pedido | 🟢 |
| D-03 | `CommandService.execute_command` ganha `versionar_estado: bool = True`; a decisão chega pronta do `SessionCloseFlow` | Mantém o serviço de comandos livre de IO e preserva por default todos os chamadores atuais | (a) o próprio `CommandService` perguntar — injeta IO em serviço puro; (b) método `close_without_commit` — duplica o fechamento | 🟢 |
| D-04 | O adaptador MCP (`src/adapters/mcp/server.py:98`) mantém o default `versionar_estado=True` e não ganha pergunta | Borda sem interlocutor; mudar seu default produziria fechamento não versionado silencioso, oposto do pedido. Ressalva já declarada na RN-04 do requirements | (a) propagar flag ao MCP — não há onde perguntar; (b) desabilitar encerramento via MCP — regressão gratuita | 🟢 |
| D-05 | Fechamento sem versionar grava na **narrativa** a declaração do que ficou pendente, no molde do `--sem-decisao` | Reusa o único mecanismo já aceito de o core escrever na narrativa (ato deliberado vira rastro), sem campo novo | (a) campo novo no front-matter — schema para registrar evento; (b) só stderr — some do histórico | 🟢 |
| D-06 | Marker `[HARNESS:ENCERRAMENTO_NAO_VERSIONADO …]`, **pós**-fechamento e informativo | Sem terminal esse passa a ser o caminho **default** (RN-08), não a exceção: o agente precisa de contrato estável para avisar o usuário e oferecer o commit manual | (a) só texto livre — sem contrato para reagir; (b) reusar `COMMIT_PENDENTE` — semântica pré-fechamento, oposta | 🟢 |
| D-07 | **Default assimétrico por borda**: no terminal a pergunta do commit de encerramento tem default afirmativo (`[S/n]`); sem terminal o default é **não versionar** | No terminal há um humano presente e um Enter distraído não deve suprimir o registro; sem terminal não há resposta, e omissão não pode valer como autorização (RN-08) | (a) afirmativo nas duas bordas — versão anterior deste roadmap, derrubada pelo achado A002; (b) negativo nas duas — hostiliza o uso interativo sem ganho de segurança | 🟢 |
| D-08 | Flags de autorização e recusa mutuamente exclusivas, com erro barulhento se ambas vierem | `argparse` resolve com grupo mutuamente exclusivo; ambiguidade em decisão sobre histórico não pode ser resolvida por precedência silenciosa | (a) precedência fixa (uma vence a outra) — silencioso e memorizável errado | 🟢 |
| D-09 | Bump **minor** do core (2.1.1 → 2.2.0) e da skill `encerrar-sessao` (1.3.0 → 1.4.0) | Mudança de comportamento observável em três materializadores da base instalada; a memória do projeto registra que propagar exige bump | (a) patch — o upgrade não regravaria os artefatos e a base ficaria stale | 🟢 |
| D-10 | Terminologia alinhada ao legado: **"commit de encerramento"** em todos os artefatos, contratos e mensagens | Achado A006; o código já usa `commit_encerramento` e a RN-N31 usa o termo. Vocabulário novo para conceito existente envelhece mal | (a) manter "commit de registro" — cria sinônimo desnecessário na fonte de verdade | 🟢 |
| D-11 | A âncora exibida no marker novo vem de `GitPort.get_head_commit` chamado pelo `SessionCloseFlow` **antes** do fechamento | É exatamente o valor que o `execute_command` grava no estado — nada é commitado entre os dois pontos — e o fluxo já injeta o `GitPort`; o serviço continua devolvendo só a mensagem de saída | (a) parsear a âncora da mensagem devolvida — contrato de texto, frágil por natureza; (b) reler o estado do disco depois de fechar — IO extra para um dado que o fluxo já tem em mãos | 🟢 |

## 4. Premissas

Nenhuma. O `requirements.md` está sem `[DÚVIDA]` após a segunda rodada de
clarificação; toda decisão acima se apoia em requisito fechado ou em regra 🟢 do
legado.

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `session/close_flow` (orquestração) | `_reversa_sdd/architecture.md#session` · `code-analysis.md#session/close_flow` | regra-alterada | `run` ganha `com_pendencias` e `versionar_estado` tri-estado (autorizado / recusado / não respondido), resolvendo o default por borda |
| `session/close_flow` (pré-check) | `code-analysis.md#session/close_flow` | regra-alterada | `conduct_commit_pendente` passa a anunciar contagem antes da lista e a perguntar o desfecho pelo `asker` |
| `session/close_flow` (renderizadores) | `code-analysis.md#session/close_flow` | contrato-alterado | `render_commit_pendente_marker` muda o texto de `acao`; nasce `render_encerramento_nao_versionado_marker` |
| `commands/service` | `code-analysis.md#commands/service` | regra-alterada | `execute_command` ganha `versionar_estado`; quando falso, grava o estado, pula `commit_paths` e declara na narrativa (D-05) |
| Borda CLI (`src/main.py`) | `code-analysis.md#main` | contrato-alterado | Três flags novas no subparser `cmd`, duas delas em grupo mutuamente exclusivo |
| Script fino da skill | `_reversa_sdd/comandos-customizados` | contrato-alterado | Mesmas três flags, repassadas ao mesmo fluxo (paridade RN-N33) |
| Skill `encerrar-sessao` (`SKILL.md` ×3) | `_reversa_sdd/comandos-customizados` | regra-alterada | Passo 3 vira "pergunte antes de commitar"; passo novo para a decisão do encerramento, a flag de autorização e o marker de aviso |
| Adaptador MCP | `code-analysis.md#adapters/mcp` | inalterado | Segue com o default `versionar_estado=True` (D-04) |

## 6. Delta no modelo de dados

- Resumo das mudanças: **nenhum campo novo**. O `SessionState` e o serializador
  ficam intactos; o que muda é o **ciclo de vida** do arquivo de estado — passa a
  existir o desfecho "fechado no arquivo, não versionado", cuja marca é uma linha
  na narrativa (D-05), não um campo. Sob a RN-08, esse desfecho deixa de ser
  exceção no fluxo do agente e passa a ser o default quando não há autorização.
- Detalhe completo em: `_reversa_forward/024-oferta-commit-consentida/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Marker `COMMIT_PENDENTE` (delta 024 sobre a 019) | arquivo / protocolo core→agente | `interfaces/commit-pendente-marker.md` |
| Marker `ENCERRAMENTO_NAO_VERSIONADO` (novo) | arquivo / protocolo core→agente | `interfaces/encerramento-nao-versionado-marker.md` |
| Flags de encerramento | linha de comando (CLI + script da skill) | `interfaces/flags-encerramento.md` |

## 8. Plano de migração

1. Implementar o delta no core com testes primeiro (renderizadores → `CommandService` → `SessionCloseFlow` → bordas), mantendo verde a suíte das features 013/014/016/018/019/022/023.
2. Atualizar as **três** cópias do `SKILL.md` e o script fino, com bump de versão da skill.
3. Bump do core para 2.2.0 e regeneração dos materializadores; conferir que o `hook command` do Stop não muda (o gate da 022 é ortogonal).
4. Smoke manual com git real, seguindo `onboarding.md` — mock de git esconde o colapso do porcelain em subpasta não rastreada (lição da 019).
5. Propagar à base instalada por `upgrade`/`migrate`, incluindo o core-raiz de `~/dev` via `.harness/upgrade-raiz.sh`.
6. Reconciliar a RN-N31 no `_reversa_sdd/` por re-extração dirigida, saldando o achado A001.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| **Novo (RN-08):** encerramento disparado sem agente atento — hook, script, automação — deixa de versionar o estado, e a sujeira se acumula silenciosamente entre sessões | alto | média | Marker de aviso obrigatório (RF-09) + linha declarativa na narrativa, visível na retomada seguinte pela reinjeção de contexto; o `resume` mostra o estado sujo ao usuário |
| Sessão fechada sem versionar deixa o estado sujo; a sessão seguinte o vê como trabalho pendente | alto | alta | Neutralizado por construção: `pending_work_paths` exclui o `session_file` por caminho exato (RN-N34). Cobrir com teste de duas sessões encadeadas |
| Âncora diverge do HEAD e o `resume` alerta a cada retomada | médio | média | Sem commit de encerramento, HEAD e âncora coincidem — o alerta some, não aumenta. Verificar no smoke |
| Fricção nova: mais uma pergunta antes de fechar, em toda sessão | médio | alta | Default afirmativo no terminal (D-07) e ausência de pergunta quando não há pendência; o agente pode fundir as duas perguntas numa interação |
| Base instalada com core e skill em versões cruzadas durante a propagação | médio | média | Flags desconhecidas falham barulhento no `argparse`; skill nova sem core novo aborta com erro legível em vez de commitar por engano |
| Regressão nos testes que assertam o texto literal de `acao` | baixo | alta | Ajuste pontual; o formato dos demais campos é preservado (RF-10) |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` regenerado sem CRITICAL nem HIGH remanescentes além do A001 (dívida assumida)
- [ ] `regression-watch.md` gerado
- [ ] Suíte completa verde, sem regressão nas features 013/014/016/018/019/022/023
- [ ] Smoke manual com git real cobrindo os cenários do `onboarding.md`, incluindo o default invertido sem terminal
- [ ] Três cópias do `SKILL.md` e o script fino em paridade de flags
- [ ] Ficha de microdecisão registrando a inversão de política sobre a RN-N31
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-07-23 | Versão inicial gerada por `/reversa-plan` | reversa |
| 2026-07-23 | Regeneração após auditoria e segunda clarificação: D-07 reformulado (default assimétrico por borda), D-08 e D-10 novos, marker renomeado, premissas zeradas | reversa |
| 2026-07-23 | Saneamento pós-auditoria da segunda rodada: grafia das flags na D-01 alinhada à D-10 (achado A011) e D-11 nova, fixando o canal da âncora do marker (achado A013) | reversa |
