# Requirements: Comando de IDE para encerrar a sessão (materializado pelo `init`)

> Identificador: `010-command-encerrar-sessao`
> Data: `2026-06-24`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Hoje a capacidade `encerrar-sessao` existe no núcleo (`CommandService`) mas só é acionável por linha de comando (`./harness cmd encerrar-sessao`) ou pela tool MCP `session_command` — não há um atalho visível dentro da IDE do agente. Esta feature faz o `./harness init` **materializar arquivos de slash command** que, ao serem digitados pelo usuário no chat, disparam o `encerrar-sessao` já existente. O comando é gravado **sempre para os dois harnesses** — Claude Code (`.claude/commands/`) e Antigravity (`.agents/workflows/`) — independentemente do `active_harness`, sem o usuário criar nada à mão. O alvo é fechar a sessão e gravar o commit-âncora com um gesto único, alinhando a experiência de encerramento à de retomada (que já sobe automática pelo gancho `SessionStart`).

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/comandos-customizados/requirements.md#visão-geral` | `encerrar-sessao` é despachado pelo `CommandService.execute_command`: exige sessão ativa, lê HEAD, `close_session(commit)` e salva atomicamente. Acionado por `./harness cmd encerrar-sessao` e pela tool MCP `session_command`. | 🟢 |
| `_reversa_sdd/domain.md#2.11` (RN-N26/RN-N27) | A integração com o Antigravity já segue um contrato **declarativo + de borda**; `materialize_hooks_json` é a **rotina única** de materialização de `.agents/hooks.json`, chamada por `init` e `upgrade`, com escrita atômica sob `project_path`. É o molde a reusar para os arquivos de comando. | 🟢 |
| `_reversa_sdd/architecture.md#5-arquitetura` (HarnessProfile / MD-0005) | Estratégia por harness (`ClaudeProfile`/`GeminiProfile`/`AntigravityProfile`) encapsula o mecanismo de cada agente sem `if`s espalhados; o harness-core é módulo per-projeto de **footprint global zero** (RN-N17): escreve só dentro do repositório. | 🟢 |
| `_reversa_sdd/domain.md#2.9` (RN-N19/RN-N20) | `init` replica wrapper+core e instala ganchos; `upgrade` evolui de forma **não-destrutiva**, preservando pastas locais. A materialização dos novos comandos deve obedecer a esse contrato. | 🟢 |
| `_reversa_sdd/domain.md#RN-N5` | O Core **não conhece o harness**: produz texto puro; a seleção do mecanismo por `active_harness` vive na borda. Os novos comandos são atalhos de IDE para o `encerrar-sessao` do core, não uma nova regra de domínio. | 🟢 |
| Docs do Antigravity (`antigravity.google/docs`, codelabs de Skills, guia de migração gcli) | Salvar um arquivo em `.agents/workflows/` **registra um comando direto no chat** do Antigravity — o equivalente fiel ao `.claude/commands/<nome>.md` do Claude Code. (A skill `.agents/skills/<nome>/SKILL.md` também surge como slash command, mas foi descartada para este comando — ver Esclarecimentos.) | 🟡 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor intermitente (single maintainer) | Encerrar a sessão sem lembrar a sintaxe da CLI | Ao terminar o trabalho, digita `/encerrar-sessao` no chat e a sessão fecha com o commit-âncora gravado. |
| Mantenedor instalando o harness num projeto novo | Ter o atalho pronto logo após instalar | Roda `./harness init <destino>` e o comando já existe para Claude e Antigravity, sem passo manual. |
| Mantenedor que migra de harness ou move o repo | Continuar com o atalho funcionando após `upgrade` | Roda `./harness upgrade` e os comandos são (re)materializados/conferidos, com o caminho do wrapper correto. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** O `init` materializa, dentro do repositório-alvo, **arquivos de slash command** que acionam a capacidade `encerrar-sessao` existente. 🟢
   - Origem no legado: estende `_reversa_sdd/domain.md#RN-N19` (init) e reusa `encerrar-sessao` de `_reversa_sdd/comandos-customizados/requirements.md`
   - Tipo: nova
2. **RN-02:** O comando é materializado **sempre para os dois harnesses**, independentemente do `active_harness`: Claude Code em `.claude/commands/encerrar-sessao.md` e Antigravity em `.agents/workflows/encerrar-sessao.md`. 🟢
   - Origem no legado: estende `_reversa_sdd/architecture.md` (HarnessProfile) e `_reversa_sdd/domain.md#RN-N26`
   - Tipo: nova
   - Decisão: Esclarecimentos · Sessão 2026-06-24 (escopo e superfície)
3. **RN-03:** A materialização escreve **apenas dentro do repositório-alvo** (footprint global zero), nunca em diretório global do usuário. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#RN-N17`
   - Tipo: nova (aplicação de regra confirmada)
4. **RN-04:** A escrita é **não-destrutiva e idempotente**: não apaga nem sobrescreve conteúdo de terceiros nos diretórios de comando; reexecutar `init`/`upgrade` converge ao mesmo resultado. 🟡
   - Origem no legado: `_reversa_sdd/domain.md#RN-N20` e o merge por named-hook de `RN-N27`
   - Tipo: nova
5. **RN-05:** Ao ser disparado, o comando **executa diretamente** `./harness cmd encerrar-sessao` (no Claude, via `!`-bash embutido no corpo do comando), produzindo efeito imediato e determinístico; **não reimplementa** a lógica de encerramento, delegando ao core e preservando RN-N5 e a exigência de sessão ativa (`_reversa_sdd/comandos-customizados/requirements.md#RF-02`). 🟢
   - Origem no legado: `_reversa_sdd/domain.md#RN-N5`
   - Tipo: nova
   - Decisão: Esclarecimentos · Sessão 2026-06-24 (acionamento direto)
6. **RN-06:** A rotina de materialização dos comandos deve ser **única e compartilhada** por `init` e `upgrade`, à semelhança de `materialize_hooks_json`. 🟡
   - Origem no legado: `_reversa_sdd/domain.md#RN-N27`
   - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | `init` materializa os arquivos de comando do `encerrar-sessao` para os dois harnesses, em qualquer `active_harness`. | Must | Após `init`, existem `.claude/commands/encerrar-sessao.md` **e** `.agents/workflows/encerrar-sessao.md` no destino. | 🟢 |
| RF-02 | Disparado no chat, o comando executa `./harness cmd encerrar-sessao` diretamente. | Must | Acionar o comando produz o mesmo efeito de `./harness cmd encerrar-sessao` (grava commit-âncora, desativa a sessão), sem intermediação do agente. | 🟢 |
| RF-03 | O comando aparece como slash command no Claude Code (`.claude/commands/`) e no Antigravity (`.agents/workflows/`). | Must | Em cada harness, o arquivo materializado fica no diretório que aquele agente lê para expor slash commands. | 🟡 |
| RF-04 | A materialização não toca arquivos fora do repositório-alvo. | Must | Teste de footprint (`RecordingFileSystem`) acusa zero escrita fora de `project_path` ao materializar os comandos. | 🟢 |
| RF-05 | A materialização é não-destrutiva perante conteúdo pré-existente nos diretórios de comando. | Must | Se já houver outros arquivos de comando do usuário, eles permanecem intactos após `init`/`upgrade`. | 🟡 |
| RF-06 | `upgrade` (re)materializa/concilia os comandos, mantendo o caminho do wrapper correto se o repo foi movido. | Should | Após mover o repo e rodar `upgrade`, o comando continua acionando o `./harness` do projeto correto. | 🟡 |
| RF-07 | A rotina de materialização é única e reusada por `init` e `upgrade`. | Should | Existe uma única função responsável pela escrita dos comandos, invocada pelos dois fluxos (sem duplicação). | 🟡 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Footprint | Escrita restrita ao repositório-alvo (footprint global zero). | `_reversa_sdd/domain.md#RN-N17`; teste `test_footprint.py` | 🟢 |
| Baixo acoplamento | Mecanismo por harness encapsulado, sem `if`s espalhados pelo serviço. | `_reversa_sdd/architecture.md` (HarnessProfile); `_reversa_sdd/domain.md#RN-N5` | 🟢 |
| Manutenibilidade | Rotina única de materialização compartilhada por `init`/`upgrade`. | Espelha `RN-N27` (`materialize_hooks_json`) | 🟡 |
| Robustez | Reexecução idempotente; conteúdo de terceiros preservado (não-destrutivo). | `_reversa_sdd/domain.md#RN-N20`/`RN-N27` | 🟡 |
| Observabilidade | Falha de materialização é barulhenta e legível. | `_reversa_sdd/domain.md#RN-N10` (fail-fast antes de I/O) | 🟡 |

## 7. Critérios de Aceitação

```gherkin
Cenário: init materializa o comando para os dois harnesses
  Dado um repositório git de destino sem comandos de IDE
  Quando rodo `./harness init <destino>` com qualquer active_harness
  Então existe `.claude/commands/encerrar-sessao.md`
  E existe `.agents/workflows/encerrar-sessao.md`
  E nenhum arquivo fora do repositório de destino foi escrito

Cenário: o comando executa o encerrar-sessao diretamente
  Dado um projeto com o comando materializado e uma sessão ativa
  Quando o usuário dispara o comando no chat
  Então o comando roda `./harness cmd encerrar-sessao`
  E o commit HEAD é gravado como âncora e a sessão fica inativa

Cenário negativo: materialização não destrói comandos de terceiros
  Dado diretórios de comando com arquivos do usuário pré-existentes
  Quando rodo `./harness init` ou `./harness upgrade`
  Então os arquivos pré-existentes permanecem intactos
  E apenas o arquivo do encerrar-sessao é criado ou atualizado em cada harness

Cenário negativo: reexecução é idempotente
  Dado um projeto que já tem os comandos materializados
  Quando rodo `./harness init` ou `./harness upgrade` novamente
  Então o conteúdo dos arquivos de comando converge ao mesmo resultado, sem duplicação
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | Sem materialização no `init`, a feature não existe. |
| RF-02 | Must | O comando precisa de fato encerrar a sessão, não só aparecer. |
| RF-03 | Must | O pedido é explícito: visível no Claude Code **e** no Antigravity. |
| RF-04 | Must | Footprint global zero é princípio inegociável do projeto. |
| RF-05 | Must | Não-destrutividade protege configuração do usuário. |
| RF-06 | Should | Conveniência de evolução; mitiga repo movido. |
| RF-07 | Should | Qualidade interna (rotina única), não muda o comportamento observável. |
| RNF de footprint | Must | Decorre de RN-N17. |

## 9. Esclarecimentos

### Sessão 2026-06-24

- **Q:** O `harness init` deve materializar o comando de encerrar-sessão para qual conjunto de harnesses?
  **R:** Sempre para os dois — Claude Code e Antigravity — independentemente do `active_harness`. (Integrado em RN-02, RF-01, RF-03 e nos cenários de aceitação.)
- **Q:** No Antigravity, em qual superfície o comando deve ser materializado?
  **R:** Workflow em `.agents/workflows/encerrar-sessao.md` (registro direto de comando no chat); a opção de skill foi descartada. (Integrado em RN-02, RF-03 e na linha de contexto do Antigravity.)
- **Q:** Ao digitar o comando no chat, como o encerrar-sessão deve ser disparado?
  **R:** Executa `./harness cmd encerrar-sessao` diretamente (no Claude, via `!`-bash embutido), efeito imediato e determinístico. (Integrado em RN-05 e RF-02.)

## 10. Lacunas

> Nenhuma lacuna em aberto. As três dúvidas iniciais foram resolvidas na Sessão 2026-06-24 (ver Esclarecimentos).

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-24 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-06-24 | Resolução das 3 dúvidas (escopo, superfície Antigravity, acionamento) por `/reversa-clarify` | reversa |
