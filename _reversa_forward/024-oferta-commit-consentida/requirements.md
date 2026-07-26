# Requirements: Oferta de commit consentida (fim do commit automático)

> Identificador: `024-oferta-commit-consentida`
> Data: `2026-07-23`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Ao encerrar a sessão, o Harness escreve no histórico do git em dois momentos — o
agente commita o trabalho pendente ao ver o marker de pendência, e o core grava o
commit de encerramento — e nenhum dos dois pergunta antes. Esta feature
transforma ambos em **ofertas**: uma indicação enxuta, *"há X mudanças não
commitadas, quer fazer o commit?"*, e escrita no git apenas mediante aval
explícito. Recusado o commit, uma segunda pergunta decide se a sessão encerra
assim mesmo. No terminal, o core pergunta o que ele mesmo executa; sem terminal,
o default se inverte — nada é versionado sem autorização declarada.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/domain.md#RN-N34` (feature 019) | `pending_work_paths` exclui **apenas** o `state_file`, não o diretório `.harness/`; decisões e índice entram na oferta de commit | 🟢 |
| `_reversa_sdd/domain.md#RN-N31` (feature 013) | O encerramento cria commit contendo **exclusivamente** o `state_file` (`chore(sessao): encerrar sessão …; âncora …`), por cima do trabalho; antes da 013 esse registro ficava como mudança pendente no working tree | 🟢 |
| `_reversa_sdd/domain.md#RN-N33` (feature 018) | `SessionCloseFlow.run` é a fonte única do encerramento (linha de comando + script fino da skill), com entrada e saída injetáveis: markers quando não há terminal interativo, perguntas `[s/N]` quando há | 🟢 |
| `_reversa_sdd/code-analysis.md#session/close_flow` | `conduct_commit_pendente` NÃO commita nem fecha em nenhum dos dois modos; devolve `0` e delega ao agente/usuário (protocolo abortar-e-reexecutar) | 🟢 |
| `_reversa_forward/019-oferta-commit-cobre-harness/interfaces/commit-pendente-marker.md#2` | Formato estável do marker: `arquivos`, `total`, `truncado`, `acao="git add -- <arquivos> e git commit …; depois rode novamente encerrar-sessao"` | 🟢 |
| `.claude/skills/encerrar-sessao/SKILL.md#Passos-3` | Passo 3 manda o agente commitar "apenas o que for trabalho real, por caminho" e rodar de novo — **sem etapa de consulta ao usuário** | 🟢 |
| `_reversa_sdd/code-analysis.md#session/offers` (feature 014) | Precedente do padrão desejado: `conduct_end_session_offers` **pergunta** `[s/N]` antes de `git push`, com aviso reforçado na branch principal | 🟢 |
| `_reversa_sdd/domain.md#RN-N5` | O core é agnóstico ao harness e **nunca** faz `git add` do trabalho — só lista caminhos sujos | 🟢 |
| `_reversa_sdd/domain.md#RN-N4` | Erros e recusas são barulhentos; o fluxo nunca degrada em silêncio | 🟢 |

Observação de coerência interna: o `git push` (014) já é consentido; os dois
commits, não. A feature elimina essa assimetria. 🟢

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor intermitente (iagoleal) | Manter controle sobre tudo que entra no histórico do repositório | Ao encerrar a sessão, ver "há 7 mudanças não commitadas, quer fazer o commit?" e responder antes de qualquer escrita no git |
| Agente do harness (Claude/Antigravity/Gemini) | Encerrar a sessão sem exceder o mandato recebido | Recebe o marker de pendência, **pergunta** ao usuário, e só então commita por caminho e reexecuta o fechamento com a flag de autorização |
| Mantenedor em terminal puro (sem agente) | Encerrar pela linha de comando | Vê a contagem e os caminhos, decide, commita à mão e reexecuta |

## 4. Regras de negócio novas ou alteradas

1. **RN-01: Commit de trabalho pendente exige consentimento explícito.** 🟢
   Nenhum `git add`/`git commit` de trabalho pendente ocorre por iniciativa do
   agente durante o encerramento; a ação depende de aval do usuário na sessão.
   - Origem no legado: `_reversa_sdd/domain.md#RN-N34` e
     `_reversa_forward/019-.../interfaces/commit-pendente-marker.md#3`
   - Tipo: alterada

2. **RN-02: A indicação é enxuta e quantificada.** 🟢
   A mensagem principal é a **contagem** de mudanças pendentes seguida da
   pergunta. No terminal, os caminhos acompanham a contagem, porque ali não há
   agente que resuma por quem lê; para o agente, os caminhos seguem no campo
   `arquivos` do marker, e cabe a ele anunciar o total, não despejar a lista.
   - Origem no legado: `_reversa_sdd/code-analysis.md#session/close_flow`
   - Tipo: alterada

3. **RN-03: O core não executa o commit do trabalho.** 🟢
   O core **formula** perguntas apenas sobre o que ele mesmo executa. Como não
   versiona trabalho alheio, sua pergunta no terminal é sobre o desfecho do
   encerramento; a pergunta "quer que eu commite?" pertence ao agente, que a
   cumpre.
   - Origem no legado: `_reversa_sdd/domain.md#RN-N5`
   - Tipo: preservada

4. **RN-04: O commit de encerramento também exige consentimento.** 🟢
   O commit que versiona somente o `state_file` deixa de ser automático. Recusado,
   a sessão é **encerrada no arquivo** (front-matter atualizado, âncora
   preservada) mas **não versionada** — o estado fica como mudança pendente no
   working tree, situação equivalente à anterior à feature 013, agora por escolha
   deliberada e anunciada.
   - Origem no legado: `_reversa_sdd/domain.md#RN-N31`
   - Tipo: alterada
   - Ressalva: a borda MCP, que não tem interlocutor a quem perguntar, permanece
     versionando por default. A exceção é declarada, não omissão.

5. **RN-05: Nada de `git add -A`.** 🟢
   Autorizado o commit, ele continua sendo feito **por caminho**, com separação
   sensata entre governança (`.harness/`) e código.
   - Origem no legado: `_reversa_forward/019-.../interfaces/commit-pendente-marker.md#3`
   - Tipo: preservada

6. **RN-06: Recusa dispara pergunta de segunda ordem.** 🟢
   Recusado o commit do trabalho, o fluxo não decide sozinho o destino da sessão:
   pergunta se deve encerrar mesmo com trabalho não commitado. "Sim" encerra com
   aviso barulhento; "não" aborta sem fechar, como hoje.
   - Origem no legado: `_reversa_sdd/domain.md#RN-N34` (hoje o pré-check nunca
     fecha com árvore suja) e `#RN-N4` (recusa barulhenta)
   - Tipo: alterada

7. **RN-07: Sessão encerrada sem versionamento é anunciada, nunca silenciosa.** 🟢
   Quando o fechamento ocorre sem o commit de encerramento (RN-04) ou com
   trabalho sujo (RN-06), a saída diz explicitamente o que ficou pendente e o que
   o usuário precisa fazer depois.
   - Origem no legado: `_reversa_sdd/domain.md#RN-N4`
   - Tipo: nova

8. **RN-08: Sem terminal, o silêncio significa "não escreva".** 🟢
   Na ausência de terminal interativo não há como perguntar, e a omissão não pode
   valer como autorização: o commit de encerramento **só** ocorre mediante
   autorização declarada por flag. Se o agente esquecer de perguntar, o desfecho é
   conservador — nada entra no histórico —, e o marker de aviso torna o
   esquecimento visível.
   - Origem no legado: `_reversa_sdd/domain.md#RN-N33` (dualidade terminal ×
     marker) e `#RN-N4`
   - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | O campo `acao` do marker `COMMIT_PENDENTE` deixa de ser uma ordem de commit e passa a descrever uma **oferta** ("pergunte ao usuário se deve commitar; só então …") | Must | Teste do renderizador verifica o novo texto de `acao`; campos `arquivos`/`total`/`truncado` inalterados | 🟢 |
| RF-02 | A skill `encerrar-sessao` instrui o agente a **perguntar** antes de qualquer escrita no git — tanto do trabalho quanto do encerramento —, no formato "há X mudanças não commitadas, quer fazer o commit?" | Must | `SKILL.md` (3 cópias) sem instrução de commit incondicional; `version` bumpada | 🟢 |
| RF-03 | No terminal, o core pergunta **o que ele executa**: o desfecho do encerramento diante de trabalho pendente (RN-06) e a gravação do commit de encerramento (RN-04). A pergunta sobre commitar o trabalho é do agente | Must | Teste verifica as duas perguntas do core e que nenhum `git add` de trabalho parte dele | 🟢 |
| RF-04 | No terminal, a contagem encabeça a mensagem e os caminhos vêm logo abaixo; para o agente, os caminhos seguem no campo `arquivos` do marker (teto de 20, com `truncado=true`) | Should | Saída interativa traz contagem e lista; marker preserva o teto e o total real | 🟢 |
| RF-05 | Autorizado o commit, o comportamento é o atual: commit por caminho, mensagem descritiva, reexecução do encerramento | Must | Fluxo feliz da 016/019 preservado nos testes existentes | 🟢 |
| RF-06 | Recusado o commit, o fluxo faz a **pergunta de segunda ordem** ("encerrar mesmo com trabalho não commitado?"); "sim" prossegue com aviso, "não" aborta sem fechar | Must | Dois cenários de teste, um por resposta, verificando desfecho e aviso | 🟢 |
| RF-07 | O commit de encerramento é precedido de pergunta no terminal, com default afirmativo; recusado, a sessão é encerrada no arquivo sem ser versionada | Must | Teste verifica estado gravado, ausência de commit novo e aviso explícito | 🟢 |
| RF-08 | **Sem terminal, o default se inverte**: o commit de encerramento não ocorre a menos que a flag de autorização seja passada. A ausência de resposta nunca autoriza escrita | Must | Teste sem TTY: sem flag → sem commit + marker de aviso; com flag → commit criado | 🟢 |
| RF-09 | Um marker pós-fechamento informa que o encerramento não foi versionado, com o caminho do estado e a âncora, para o agente avisar o usuário | Must | Marker emitido em todos os caminhos que fecham sem versionar | 🟢 |
| RF-10 | O contrato do marker `COMMIT_PENDENTE` segue retrocompatível em **formato**; muda só a semântica de `acao` | Should | Testes da 016/019 passam com ajuste apenas no texto de `acao` | 🟢 |
| RF-11 | Os contratos de interface são atualizados como delta versionado, à moda da 019 | Should | `interfaces/` da feature com os deltas e o contrato do marker novo | 🟢 |
| RF-12 | A âncora de integridade continua apontando para o último commit de trabalho, inclusive quando o encerramento não é versionado | Must | Teste verifica que a âncora gravada não muda de semântica na recusa | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Observabilidade | Recusas e pendências produzem saída explícita; nenhuma degradação silenciosa | `_reversa_sdd/domain.md#RN-N4` | 🟢 |
| Reprodutibilidade | Comportamento idêntico entre linha de comando e script fino da skill, por consumo da mesma `SessionCloseFlow` | `_reversa_sdd/domain.md#RN-N33` | 🟢 |
| Segurança do default | Na ausência de resposta, o sistema escolhe **não escrever** no histórico; autorizar é ato positivo | RN-08; princípio de falha conservadora | 🟢 |
| Integridade do histórico | Sessão encerrada sem versionar o estado não pode corromper a retomada seguinte: o `resume` precisa lidar com estado sujo sem confundir âncora | `_reversa_sdd/domain.md#RN-07` | 🟡 |
| Compatibilidade | Base instalada só muda ao rodar `upgrade`/`migrate`; projetos com core antigo seguem funcionando com o texto antigo | Memória do projeto: materializadores stale exigem bump de versão | 🟢 |
| Segurança operacional | Reduz o risco de o agente versionar arquivo indevido (dados sensíveis, artefato derivado) sem revisão humana | Projetos irmãos com dados sensíveis (`chagas-ms`, `experimento`) | 🟡 |
| Testabilidade | Toda pergunta passa por entrada e saída injetáveis (`asker`/`out`), nunca `input()` direto no fluxo | Padrão já estabelecido por `conduct_end_session_offers` (014) | 🟢 |

Tensão registrada: a memória do projeto guarda uma preferência por **autonomia**
no encadeamento de etapas. Esta feature abre uma exceção deliberada e estreita —
parar **apenas** onde a ação escreve no histórico do git.

Riscos registrados, para o plano tratar:

1. A RN-04 reabre, por escolha, a situação que a feature 013 fechou (registro de
   encerramento como mudança pendente). O efeito sobre a retomada, o gate de
   decisões e o cálculo de pendência da sessão seguinte precisa de teste próprio.
2. A RN-08 tem custo: um encerramento disparado sem agente atento — por hook,
   script ou automação — deixará de versionar o estado, e o estado sujo se
   acumula até alguém commitar. O aviso do RF-09 é a mitigação mínima.

## 7. Critérios de Aceitação

```gherkin
Cenário: pendência anunciada como oferta, sem terminal interativo
  Dado uma sessão ativa e 7 caminhos sujos além do estado de sessão
  Quando o encerramento roda sem terminal interativo
  Então a saída traz [HARNESS:COMMIT_PENDENTE arquivos="…" total=7 …]
  E o campo acao descreve perguntar ao usuário antes de commitar
  E nenhum commit de trabalho é criado
  E a sessão não é fechada

Cenário: pergunta enxuta no terminal
  Dado uma sessão ativa e 7 caminhos sujos além do estado de sessão
  Quando o encerramento roda em terminal interativo
  Então a saída contém "há 7 mudanças não commitadas" antes da lista de caminhos
  E pergunta se deve encerrar mesmo assim
  E nenhum commit de trabalho é criado

Cenário: agente não commita sem aval
  Dado que o agente recebeu o marker COMMIT_PENDENTE
  Quando ele conduz o encerramento
  Então ele apresenta a contagem e a pergunta ao usuário
  E só executa git add e git commit após resposta afirmativa

Cenário: aval concedido para o trabalho
  Dado que o usuário autorizou o commit
  Quando o agente commita por caminho com mensagem descritiva
  E reexecuta o encerramento
  Então a árvore fica limpa exceto o estado de sessão
  E o fluxo segue para a decisão do commit de encerramento

Cenário: recusa do commit, usuário opta por encerrar assim mesmo
  Dado que o usuário respondeu que não quer commitar agora
  Quando o fluxo pergunta se deve encerrar mesmo com trabalho não commitado
  E o usuário responde que sim
  Então a sessão é encerrada
  E a saída avisa explicitamente quais mudanças ficaram fora do histórico

Cenário: recusa do commit, usuário opta por não encerrar
  Dado que o usuário respondeu que não quer commitar agora
  Quando o fluxo pergunta se deve encerrar mesmo com trabalho não commitado
  E o usuário responde que não
  Então a sessão não é encerrada
  E nenhum commit é criado

Cenário: commit de encerramento consentido no terminal
  Dado uma sessão pronta para fechar em terminal interativo
  Quando o fluxo pergunta se deve gravar o commit de encerramento
  E o usuário autoriza
  Então o commit versiona exclusivamente o arquivo de estado de sessão
  E a âncora segue apontando para o último commit de trabalho

Cenário: commit de encerramento recusado no terminal
  Dado uma sessão pronta para fechar em terminal interativo
  Quando o usuário recusa o commit de encerramento
  Então o estado de sessão é gravado com o fechamento
  E nenhum commit novo é criado
  E a saída avisa que o estado ficou como mudança pendente no working tree

Cenário: sem terminal e sem autorização, nada é versionado
  Dado uma sessão pronta para fechar sem terminal interativo
  Quando o encerramento roda sem a flag de autorização
  Então o estado de sessão é gravado com o fechamento
  E nenhum commit novo é criado
  E a saída traz o marker de encerramento não versionado

Cenário: sem terminal e com autorização declarada
  Dado uma sessão pronta para fechar sem terminal interativo
  Quando o encerramento roda com a flag de autorização do commit de encerramento
  Então o commit versiona exclusivamente o arquivo de estado de sessão
  E nenhum marker de encerramento não versionado é emitido

Cenário: muitas pendências, lista truncada mas rastreável
  Dado uma sessão ativa e 34 caminhos sujos além do estado de sessão
  Quando o encerramento roda sem terminal interativo
  Então o marker traz total=34, truncado=true e mostrados=20
  E a contagem anunciada é 34, não 20

Cenário: parser antigo continua lendo o marker
  Dado um consumidor que extrai os campos arquivos e total do marker
  Quando o encerramento emite o marker com o novo texto de acao
  Então arquivos, total e truncado mantêm o mesmo formato de antes
  E apenas o conteúdo de acao difere

Cenário: árvore limpa
  Dado que só o arquivo de estado de sessão está sujo
  Quando o encerramento roda
  Então nenhuma oferta de commit de trabalho é emitida
  E o fluxo vai direto à decisão do commit de encerramento
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 (marker vira oferta) | Must | É a origem do comportamento: enquanto `acao` mandar commitar, o agente commita |
| RF-02 (skill pergunta) | Must | Camada onde o commit de trabalho de fato acontece hoje |
| RF-03 (core pergunta o que executa) | Must | Paridade entre as duas bordas sem oferta falsa |
| RF-05 (fluxo pós-aval intacto) | Must | Sem isso a feature quebra o encerramento |
| RF-06 (pergunta de segunda ordem) | Must | Caminho negativo não pode ficar indefinido |
| RF-07 (encerramento consentido no terminal) | Must | Segunda metade do pedido |
| RF-08 (default invertido sem terminal) | Must | Sem isso o consentimento não existe no caminho mais usado |
| RF-09 (marker de aviso) | Must | Torna visível o desfecho não versionado |
| RF-12 (âncora preservada) | Must | Integridade da retomada não pode depender da resposta do usuário |
| RF-04 (contagem encabeça, lista abaixo) | Should | Enxugar não pode custar rastreabilidade |
| RF-10 (retrocompat de formato) | Should | Evita quebrar parsers e testes existentes |
| RF-11 (contrato versionado) | Should | Coerência com a prática da 019 |
| Consentimento para `git push` | Won't | Já existe desde a feature 014 |
| Consentimento na borda MCP | Won't | Sem interlocutor a quem perguntar (ressalva da RN-04) |

## 9. Esclarecimentos

### Sessão 2026-07-23 (primeira rodada)

- **Q:** Qual commit deixa de ser automático no encerramento?
  **R:** Ambos — o do trabalho pendente e o de encerramento. Consolidado nas
  RN-01 e RN-04; a RN-N31 passa a ser condicionada ao aval.
- **Q:** Se o usuário responder "não quero commitar agora", o que acontece com o
  encerramento?
  **R:** Pergunta de segunda ordem, sem desfecho implícito. Consolidado na RN-06.
- **Q:** Onde a mudança deve viver?
  **R:** O core formula a pergunta no modo interativo, mas quem commita o
  trabalho continua sendo o agente ou o usuário. Consolidado na RN-03.
- **Q:** Quanto detalhe na indicação?
  **R:** Contagem à frente; lista conforme a borda. Consolidado na RN-02.

### Sessão 2026-07-23 (segunda rodada, sobre os achados da auditoria)

- **Q:** (A002) Sem terminal, como garantir o consentimento do commit de
  encerramento, se o core não tem a quem perguntar?
  **R:** Inverter o default: sem terminal, nada é versionado a menos que a flag de
  autorização seja passada. O agente pergunta e passa a flag; se esquecer, o erro
  é conservador — nada entra no histórico. Consolidado na RN-08 e no RF-08.
- **Q:** (A003) O RF-03 prometia que o core formula a pergunta do commit, mas o
  core não pode commitar. Como resolver?
  **R:** Alinhar o requisito ao comportamento acordado: o core pergunta o que ele
  executa. A regra RN-N5 fica intacta. Consolidado na RN-03 e no RF-03 reescrito.
- **Q:** (A005) No terminal, como oferecer a lista se o prompt só aceita sim ou
  não?
  **R:** Exibir contagem e lista juntas — quem está no terminal não tem agente que
  resuma por ele. Consolidado no RF-04.
- **Q:** (A006) Como chamar o commit que versiona o estado ao encerrar?
  **R:** "commit de encerramento", o nome que o legado e o código já usam.
  Aplicado em todo o documento.

Correções de saneamento aplicadas nesta rodada (achado A004 da auditoria): as
citações de regra foram corrigidas contra o `_reversa_sdd/domain.md` — o filtro
de pendência restrito ao arquivo de estado é **RN-N34** (antes citada como
RN-N33) e a fonte única do encerramento entre as duas bordas é **RN-N33** (antes
citada como RN-N38, que na verdade trata da migração via `harness migrate`).

## 10. Lacunas

Nenhuma lacuna aberta. Os quatro pontos da primeira rodada e os quatro achados
HIGH da auditoria (`audit/cross-check.md`) estão resolvidos e consolidados nas
regras e requisitos acima.

Permanece registrado, sem bloquear esta feature, o achado A001: a alteração da
RN-N31 é conflito deliberado com regra 🟢 do legado e exige reconciliação do
`_reversa_sdd/` após a implementação.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-07-23 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-07-23 | Quatro dúvidas resolvidas por `/reversa-clarify`; RN-04/06/07 e RF-06/07/08/11 consolidados | reversa |
| 2026-07-23 | Segunda rodada de `/reversa-clarify` sobre os achados HIGH da auditoria: RN-08 (default invertido sem terminal), RF-03 realinhado, RF-04 revisto, terminologia "commit de encerramento" e correção das citações de regra | reversa |
