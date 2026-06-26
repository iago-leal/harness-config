# Requirements: Ofertas de fim de sessão — publicar (push) e atualizar (upgrade) o Harness Core

> Identificador: `014-oferta-upgrade-ao-encerrar`
> Data: `2026-06-26`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Ao encerrar a sessão, o harness hoje fecha o trabalho num commit local do estado (feature 013) e, no máximo, imprime um aviso passivo de que há versão nova do núcleo. Esta feature
acrescenta duas **ofertas acionáveis** logo após o fechamento bem-sucedido: publicar o
trabalho (`git push`) e atualizar o Harness Core (`upgrade`). Quando há terminal
interativo, cada oferta é uma pergunta `[s/N]` que, aceita, executa a ação; sem terminal
(acionamento por slash command), o comando não bloqueia e emite uma instrução estruturada
que o agente de IA medeia no chat. O push olha o `origin` do **projeto** e só aparece se
houver commits a publicar; o upgrade olha o **upstream** do harness, consultado pela rede.
O alvo é o mantenedor intermitente, que fecha a sessão deixando o trabalho publicado e o
núcleo atualizado sem comandos manuais. O fechamento da sessão permanece intocado: as
ofertas são etapa posterior e não-bloqueante.

## 2. Contexto a partir do legado

| Fonte                                                           | Trecho relevante                                                                                                                                                                                                                       | Confidência |
| --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `_reversa_sdd/domain.md#2.14` (RN-N31/N32)                      | O `encerrar-sessao` captura a âncora, grava o estado e o versiona num commit isolado por cima do trabalho, falhando barulhento se o commit não puder ser criado. É o efeito que **não pode** ser comprometido por esta feature.        | 🟢          |
| `_reversa_sdd/domain.md#2.9` (RN-N21)                           | Hoje a checagem de atualização é **passiva e estritamente local**: compara a `version` local com a do `upstream_path` no filesystem e só imprime "Execute './harness upgrade'".                                                        | 🟢          |
| `_reversa_sdd/domain.md#2.9` (RN-N18/RN-N20)                    | A seção `[harness]` registra `version` e `upstream_path`; o comando `upgrade` já atualiza o core a partir do upstream, preservando `.reversa/` e `.harness/decisoes/`, rematerializando com o código novo (012) e aceitando `--force`. | 🟢          |
| `_reversa_sdd/domain.md#2.1` (RN-01/RN-02)                      | Padrão de sincronia: resiliência offline — qualquer erro de rede/git degrada para um caminho seguro, nunca trava.                                                                                                                      | 🟢          |
| `_reversa_sdd/sync-check/contracts.md#3`                        | O `GitPort` fala com o git só pela porta; `get_remote_commit` faz `git ls-remote origin main`. Não há, hoje, capacidade de `fetch`, de `push`, de comparar ahead/behind, nem de ler a `version` publicada numa ref remota.             | 🟢          |
| `_reversa_sdd/comandos-customizados/requirements.md`            | `encerrar-sessao` vive no `CommandService` compartilhado (CLI/slash command e tool MCP); os slash commands materializados apenas delegam ao wrapper.                                                                                   | 🟢          |
| Preferência operacional do mantenedor (fora do `_reversa_sdd/`) | "Push na branch principal exige aval consciente"; o core vendorizado é `.gitignore`-ado nos projetos-alvo (`CORE_GITIGNORE_ENTRY`), logo o `upgrade` não suja o working tree versionado.                                               | 🟡          |

Âncoras de código atuais (estado pré-feature, confirmadas): o alerta passivo roda na
borda (`main.py`) via `SyncService.check_version_update`, que lê a `version` do upstream
**no filesystem**; a oferta de `git init` (`main.py#offer_git_init`) é o **molde** de
pergunta `[s/N]` guardada por `sys.stdin.isatty()`; `upgrade_project` copia o core do
`upstream_path` **no filesystem** (`_copy_tree`), não de uma ref remota; o `GitPort` só
lê e commita, não publica.

## 3. Personas e cenários de uso

| Persona                            | Objetivo                                                         | Cenário-chave                                                                                                                                           |
| ---------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mantenedor intermitente (terminal) | Fechar a sessão publicando o trabalho e atualizando a ferramenta | Roda `encerrar-sessao` no terminal; aceita a oferta de push, depois a de upgrade, ambas via `[s/N]`.                                                    |
| Mantenedor via agente de IA        | Decidir push e upgrade pelo chat                                 | Aciona `/encerrar-sessao`; o agente lê as ofertas estruturadas na saída, pergunta no chat e executa o que for aceito.                                   |
| Eu-de-daqui-a-meses                | Reabrir sem trabalho perdido nem ferramenta defasada             | Ao encerrar, é convidado a publicar os commits da sessão e a atualizar o núcleo, em vez de descobrir depois que faltou push ou que a versão está velha. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** Ao encerrar uma sessão **com sucesso**, e somente então, o harness apresenta
   as ofertas de fim de sessão (push e upgrade), como etapa **posterior e separada** do
   fechamento. A oferta acionável é **exclusiva** do `encerrar-sessao`; os demais comandos
   mantêm apenas o alerta passivo atual. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.9` (RN-N21, hoje só passiva) e `#2.14` (RN-N31, o fechamento)
   - Tipo: nova
2. **RN-02:** Nenhuma oferta compromete o encerramento. Se uma verificação, oferta ou ação
   (push/upgrade) falhar, o fechamento da sessão (commit do estado, feature 013) permanece
   válido e o comando não regride a um estado de erro por causa das ofertas. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.1` (RN-02, resiliência) e `#2.14` (RN-N31)
   - Tipo: nova
3. **RN-03:** As ofertas operam em **dupla camada**, decidida pela presença de terminal
   interativo: com terminal, cada oferta é uma pergunta `[s/N]` que, aceita, executa a ação;
   sem terminal (slash command/agente), o comando **não** bloqueia esperando entrada — emite
   uma instrução estruturada e legível que o agente reconhece para conduzir a confirmação no
   chat e disparar a ação. Vale igualmente para push e upgrade. 🟢
   - Origem no legado: `main.py#offer_git_init` (molde de oferta guardada por TTY)
   - Tipo: nova
4. **RN-04:** A oferta de **push** mira o remoto do **projeto** (o `origin`/upstream de
   rastreamento do branch corrente) e só aparece quando o branch local está **à frente** do
   seu remoto (há commits a publicar). Publica o commit de encerramento e os commits de
   trabalho da sessão ainda não publicados. Sem commits à frente, nenhuma oferta de push é
   exibida. 🟢
   - Tipo: nova
5. **RN-05:** Quando o branch corrente é o **principal** do repositório (ex.: `main`), a
   oferta de push é mantida, porém com **aviso reforçado** de que a publicação é direta na
   branch principal, exigindo confirmação consciente. 🟢
   - Origem: preferência operacional do mantenedor ("push na principal exige aval")
   - Tipo: nova
6. **RN-06:** O push **nunca** é forçado (sem `--force`) e usa o rastreamento e a
   autenticação git já configurados no host. Falha de push degrada de forma barulhenta (erro
   claro), sem desfazer o encerramento nem reverter o commit local. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#RN-N4` (falha barulhenta) e `#2.1` (resiliência)
   - Tipo: nova
7. **RN-07:** A verificação de **upgrade** consulta o **upstream do harness** pela **rede**
   (um `fetch`) a **cada** encerramento, sem cache nem janela de TTL, refletindo o que está
   publicado, e não apenas a cópia local do upstream. A consulta é **resiliente**: erro de
   rede, ausência de remoto ou credencial expirada degradam sem oferta enganosa e sem travar
   o comando. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.9` (RN-N21, hoje local) e `_reversa_sdd/sync-check/requirements.md` (RN-02, degradar com segurança)
   - Tipo: alterada
8. **RN-08:** Aceitar a oferta de upgrade reusa o comando `upgrade` existente; a feature
   **não** reimplementa a lógica de cópia/rematerialização do núcleo. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.9` (RN-N20, upgrade não-destrutivo)
   - Tipo: nova
9. **RN-09:** Como o `upgrade` copia do `upstream_path` **no filesystem** (RN-N20), aceitar
   a oferta **sincroniza o clone do upstream** (traz o publicado para o filesystem) **antes**
   da cópia, para que a atualização reflita de fato a versão detectada pela rede. A
   sincronização é **não-destrutiva**: se o working tree do upstream tiver mudanças locais ou
   conflito, aborta de forma barulhenta sem sobrescrever trabalho, e o upgrade não aplica uma
   versão fantasma. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.9` (RN-N20) e `#2.13` (RN-N30, abortar barulhento sob estado incompleto)
   - Tipo: nova
10. **RN-10:** Quando ambas as ofertas se aplicam na mesma sessão, a ordem é **primeiro o
    push, depois o upgrade**: publica-se o trabalho da sessão antes de atualizar a ferramenta
    para a próxima. 🟢
    - Tipo: nova
11. **RN-11:** A oferta de upgrade só ocorre onde há `upstream_path` configurado (sem ele —
    ex.: o próprio repositório canônico do harness — não há verificação nem oferta de
    upgrade). A oferta de push **independe** do `upstream_path`: depende apenas de o projeto
    ter remoto de rastreamento e commits à frente. 🟢
    - Origem no legado: `_reversa_sdd/domain.md#2.9` (RN-N18/RN-N21)
    - Tipo: nova

## 5. Requisitos Funcionais

| ID    | Requisito                                                                                                             | Prioridade | Critério de aceite                                                                                                                                                                                                                         | Confidência |
| ----- | --------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| RF-01 | Após um `encerrar-sessao` bem-sucedido, o harness avalia e apresenta as ofertas de fim de sessão.                     | Must       | Concluído o fechamento, o comando avalia push (se há commits à frente) e upgrade (se há `upstream_path` e versão nova) e exibe as ofertas cabíveis; sem condição satisfeita, nenhuma oferta aparece.                                       | 🟢          |
| RF-02 | A oferta de push aparece somente quando o branch está à frente do seu remoto e publica para o rastreamento do branch. | Must       | Com commits à frente, a saída traz a oferta de push do branch corrente; com o branch em dia, nenhuma oferta de push aparece.                                                                                                               | 🟢          |
| RF-03 | Na branch principal, a oferta de push traz aviso reforçado.                                                           | Should     | Quando o branch corrente é o principal, a oferta destaca que a publicação é direta na principal antes de confirmar.                                                                                                                        | 🟢          |
| RF-04 | O push nunca é forçado e sua falha é barulhenta, sem desfazer o encerramento.                                         | Must       | O caminho de push não usa `--force`; uma falha de push exibe erro claro e o commit de encerramento permanece intacto.                                                                                                                      | 🟢          |
| RF-05 | A verificação de upgrade consulta o upstream pela rede a cada encerramento, sem cache.                                | Must       | A comparação reflete a versão publicada no remoto do upstream (não apenas a `version` no filesystem) e ocorre em todo encerramento, sem reaproveitar TTL.                                                                                  | 🟡          |
| RF-06 | Aceitar o upgrade sincroniza o clone do upstream antes da cópia, de forma não-destrutiva.                             | Must       | Antes do upgrade, o clone do upstream é atualizado para o publicado; se houver mudanças locais/conflito no upstream, o processo aborta barulhento e o upgrade não aplica versão indeterminada.                                             | 🟢          |
| RF-07 | A atualização aceita reusa o `upgrade` existente, sem reimplementar a lógica.                                         | Must       | O caminho de atualização invoca o mesmo comando/serviço de `upgrade` já validado; não há nova rotina de cópia/rematerialização.                                                                                                            | 🟢          |
| RF-08 | Ambas as ofertas operam em dupla camada (TTY × slash command).                                                        | Must       | No terminal, cada oferta é `[s/N]` e a ação aceita é executada; sem terminal, o comando termina sem esperar entrada e a saída traz marcações inequívocas de "push disponível" e/ou "atualização disponível" com a ação correspondente.     | 🟢          |
| RF-09 | Verificações e ofertas são não-bloqueantes e o fechamento é íntegro independentemente delas.                          | Must       | Com rede indisponível, sem remoto ou credencial inválida, o comando encerra normalmente (estado já versionado), sem travar, sem exceção propagada e sem oferta enganosa.                                                                   | 🟢          |
| RF-10 | Quando ambas se aplicam, a oferta de push precede a de upgrade.                                                       | Should     | Na mesma sessão com push e upgrade cabíveis, a oferta/execução de push ocorre antes da de upgrade.                                                                                                                                         | 🟢          |
| RF-11 | O comportamento é coberto por testes de unidade.                                                                      | Must       | Há testes com git fake/dublê cobrindo: branch à frente → oferta de push; em dia → sem push; upstream à frente → oferta de upgrade; versões iguais → sem upgrade; falha de rede/push → degradação sem exceção; ordem push antes de upgrade. | 🟢          |
| RF-12 | O texto dos slash commands materializados reflete as ofertas de push e upgrade ao encerrar.                           | Should     | A `description`/corpo dos artefatos (Claude e Antigravity) menciona que o encerramento pode oferecer publicar o trabalho e atualizar o núcleo, de forma consistente entre os perfis.                                                       | 🟡          |

## 6. Requisitos Não Funcionais

| Tipo              | Requisito                                                                                                                                                                                                          | Evidência ou justificativa                                                                     | Confidência |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------- | ----------- |
| Resiliência       | Verificações e ofertas degradam com segurança em qualquer falha de rede/git/credencial, jamais travando o encerramento.                                                                                            | RN-02/RN-06/RN-07; espelha a política offline do `SyncService` (`_reversa_sdd/domain.md#2.1`). | 🟢          |
| Segurança         | Push sem `--force`; nenhuma credencial nova é solicitada ou persistida; aviso reforçado na branch principal.                                                                                                       | RN-05/RN-06; evita sobrescrever histórico remoto e publicação inadvertida na principal.        | 🟢          |
| Desempenho        | A consulta de rede e o push ao encerrar não devem tornar o fechamento perceptivelmente lento; o custo é pontual (evento de fim de sessão), não no boot de cada invocação.                                          | RN-01 (gatilho exclusivo do encerramento).                                                     | 🟡          |
| Baixo acoplamento | A lógica de verificação/comparação de versões e de estado do branch fica no domínio (porta de git + serviço de sincronia), testável; a interação (TTY, entrada do usuário, disparo de push/upgrade) fica na borda. | RN-N5; o domínio não conhece `stdin`/terminal nem o harness ativo.                             | 🟢          |
| Observabilidade   | Cada oferta declara a ação e o alvo (branch a publicar; versão atual → versão alvo); uma verificação que não pôde confirmar não exibe oferta.                                                                      | RN-06/RN-07; evita sugerir ação sobre dado não confirmado.                                     | 🟢          |
| Footprint         | Toda escrita local permanece sob o projeto; nenhuma alteração em configuração global.                                                                                                                              | RN-N17 (footprint global zero).                                                                | 🟢          |

## 7. Critérios de Aceitação

```gherkin
Cenário: Branch à frente, terminal, push aceito
  Dado uma sessão ativa e o branch corrente à frente do seu remoto
  Quando executo `encerrar-sessao` num terminal interativo e aceito a oferta de push
  Então a sessão é encerrada e versionada normalmente
  E os commits à frente (incluindo o de encerramento) são publicados no remoto do projeto.

Cenário: Branch em dia não oferece push
  Dado uma sessão ativa e o branch corrente sem commits à frente do remoto
  Quando executo `encerrar-sessao`
  Então a sessão é encerrada normalmente
  E nenhuma oferta de push é exibida.

Cenário: Aviso reforçado ao publicar na branch principal
  Dado uma sessão ativa, o branch corrente sendo o principal e há commits à frente
  Quando executo `encerrar-sessao` num terminal interativo
  Então a oferta de push destaca que a publicação é direta na branch principal antes de pedir confirmação.

Cenário: Upstream à frente, upgrade aceito, sincroniza antes
  Dado uma sessão ativa, `upstream_path` configurado e o upstream publicado mais recente que a versão local
  Quando executo `encerrar-sessao` num terminal e aceito a oferta de upgrade
  Então o clone do upstream é sincronizado com o publicado antes da cópia
  E o upgrade é executado refletindo a versão detectada, com seu resultado reportado.

Cenário: Upstream com trabalho local não é sobrescrito
  Dado uma sessão ativa e upgrade aceito
  E que o clone do upstream tem mudanças locais ou conflito ao sincronizar
  Quando a sincronização é tentada
  Então ela aborta de forma barulhenta sem sobrescrever o trabalho no upstream
  E nenhuma versão fantasma é aplicada.

Cenário: Ordem das ofertas
  Dado uma sessão ativa com commits à frente E upstream à frente
  Quando executo `encerrar-sessao`
  Então a oferta de push é apresentada antes da oferta de upgrade.

Cenário: Sem terminal (slash command)
  Dado uma sessão ativa com push e/ou upgrade cabíveis
  Quando aciono `encerrar-sessao` por slash command (sem terminal interativo)
  Então o comando encerra sem esperar entrada
  E a saída traz marcações inequívocas das ofertas cabíveis, cada uma com sua ação.

Cenário: Falha de rede degrada com segurança
  Dado uma sessão ativa e `upstream_path` configurado
  E que a rede está indisponível ou a credencial expirou
  Quando executo `encerrar-sessao`
  Então a sessão é encerrada e versionada normalmente
  E nenhuma oferta enganosa é exibida e nenhuma exceção das verificações interrompe o comando.

Cenário: Recusa das ofertas no terminal
  Dado uma sessão ativa com push e upgrade cabíveis
  Quando executo `encerrar-sessao` num terminal e respondo "não" a ambas
  Então a sessão permanece encerrada e nem push nem upgrade são executados.
```

## 8. Prioridade MoSCoW

| Item                                                                      | MoSCoW | Justificativa                                                                                     |
| ------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------- |
| RF-01 / RF-09 (avaliar ao encerrar; degradar com segurança)               | Must   | Coração da feature; sem resiliência, as ofertas virariam fonte de travamento no fim da sessão.    |
| RF-02 / RF-04 (push condicional; nunca forçado, falha barulhenta)         | Must   | A publicação é o detalhe acrescentado; precisa ser segura e só aparecer quando há o que publicar. |
| RF-05 / RF-06 / RF-07 (upgrade por rede; sincroniza antes; reusa upgrade) | Must   | Torna a oferta de upgrade honesta e sem duplicar lógica crítica de atualização.                   |
| RF-08 (dupla camada TTY × slash command)                                  | Must   | É a forma de "oferecer e, se aceito, agir" decidida; cobre os dois usos reais.                    |
| RF-11 (testes)                                                            | Must   | Padrão do projeto: comportamento de domínio coberto por teste.                                    |
| RF-03 (aviso na branch principal)                                         | Should | Salvaguarda alinhada à preferência do mantenedor; refina, não habilita, o push.                   |
| RF-10 (ordem push antes de upgrade)                                       | Should | Melhora o fluxo; não altera o efeito de cada ação isolada.                                        |
| RF-12 (texto dos slash commands)                                          | Should | Coerência da documentação exibida com o efeito real; baixo custo.                                 |

## 9. Esclarecimentos

### Sessão 2026-06-26

- **Q:** A oferta acionável deve disparar só no `encerrar-sessao` ou também noutros comandos que hoje exibem o alerta passivo?
  **R:** Exclusiva do `encerrar-sessao`; os demais comandos mantêm o alerta passivo. Registrado em RN-01.
- **Q:** Como garantir que o upgrade aplique a versão detectada pela rede, se o `upgrade` copia do `upstream_path` no filesystem?
  **R:** Aceitar a oferta sincroniza o clone do upstream (traz o publicado ao filesystem) antes da cópia, de forma não-destrutiva e barulhenta em caso de conflito/trabalho local. Registrado em RN-09/RF-06.
- **Q:** A consulta de rede ao encerrar deve respeitar cache/TTL ou buscar sempre?
  **R:** `fetch` a cada encerramento, sem cache; o encerramento é evento pontual e o frescor importa. Registrado em RN-07.
- **Q:** (escopo acrescentado) O encerramento deve também oferecer o push?
  **R:** Sim. Acrescentada a oferta de push como cidadã de primeira classe (RN-04 a RN-06, RN-10 a RN-11; RF-02 a RF-04, RF-10), com a mesma mecânica de dupla camada das demais ofertas.
- **Q:** Quando oferecer o push?
  **R:** Quando o branch corrente está à frente do seu remoto (há commits a publicar); sem isso, sem oferta. Registrado em RN-04.
- **Q:** Como tratar o push na branch principal?
  **R:** Manter a oferta, com aviso reforçado de publicação direta na principal. Registrado em RN-05.
- **Q:** Em que ordem apresentar push e upgrade?
  **R:** Primeiro o push, depois o upgrade. Registrado em RN-10.
- **Nota de mecânica (assumida):** o push usa a mesma dupla camada TTY × slash command definida para o upgrade (RN-03); o push mira o `origin` do projeto, enquanto o upgrade mira o `upstream_path` do harness — remotos e gatilhos distintos (RN-11).

## 10. Lacunas

> Nenhuma lacuna em aberto. As três dúvidas iniciais e a expansão de escopo (oferta de push) foram resolvidas na Sessão 2026-06-26 (ver Esclarecimentos).

## 11. Histórico de alterações

| Data       | Alteração                                                                                                                            | Autor   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| 2026-06-26 | Versão inicial gerada por `/reversa-requirements`                                                                                    | reversa |
| 2026-06-26 | Três dúvidas resolvidas por `/reversa-clarify` (gatilho exclusivo, sincronizar upstream antes do upgrade, fetch a cada encerramento) | reversa |
| 2026-06-26 | Expansão de escopo: acrescentada a oferta de push (condição ahead, aviso na principal, ordem push→upgrade)                           | reversa |
