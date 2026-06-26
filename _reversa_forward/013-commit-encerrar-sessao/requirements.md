# Requirements: Versionar o estado da sessão ao encerrar

> Identificador: `013-commit-encerrar-sessao`
> Data: `2026-06-26`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Hoje o comando `encerrar-sessao` grava o estado da sessão em disco mas deixa essa
gravação como mudança pendente no working tree: o "commit-âncora" anunciado é apenas
um hash escrito _dentro_ do arquivo, nunca um commit de fato. Esta feature faz o
próprio comando versionar o registro de encerramento, criando um commit que captura
**exclusivamente** o arquivo de estado, por cima do último commit de trabalho. O alvo
é o operador que encerra a sessão e espera que o fechamento fique reproduzível no
histórico, sem depender de lembrar de um `git commit` manual e sem arrastar mudanças
alheias do working tree.

## 2. Contexto a partir do legado

| Fonte                                                                  | Trecho relevante                                                                                                                                                                                | Confidência |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `_reversa_sdd/comandos-customizados/requirements.md#regras-de-negócio` | `encerrar-sessao` exige sessão ativa, lê HEAD, `close_session(commit)` e salva atomicamente — **sem** `git add`/`git commit`.                                                                   | 🟢          |
| `_reversa_sdd/domain.md#2.3`                                           | RN-07 (Âncora Git): SHA-1 do HEAD gravado no fechamento, usado na retomada para detectar divergência da base local.                                                                             | 🟢          |
| `_reversa_sdd/session/requirements.md#regras-de-negócio`               | RN-N1: o estado vive num único artefato **versionado** `.harness/estado-da-sessao.md`; caminho lido de `config.session.state_file`.                                                             | 🟢          |
| `_reversa_sdd/comandos-customizados/requirements.md#✨-f010`           | `init`/`upgrade` materializam os slash commands (`.claude/commands/encerrar-sessao.md`, `.agents/workflows/encerrar-sessao.md`) que apenas **delegam** ao `CommandService` via wrapper (RN-N5). | 🟢          |
| `_reversa_sdd/domain.md#RN-N5`                                         | O core não conhece o harness nem a infraestrutura concreta: o domínio fala com Git apenas pela porta `GitPort`.                                                                                 | 🟢          |
| `_reversa_sdd/domain.md#RN-N4`                                         | Falha barulhenta é o padrão do projeto: estados anômalos levantam erro nomeado, nunca degradam em silêncio.                                                                                     | 🟢          |

Âncoras de código atuais (estado pré-feature, todas confirmadas): `execute_command`
ramo `encerrar-sessao` salva sem versionar; `GitPort` expõe apenas `get_head_commit`,
`get_remote_commit`, `init_repo`; o `SubprocessGitAdapter` só lê; e cada
`session_command_artifact` materializa um corpo que roda `./harness cmd encerrar-sessao`.

## 3. Personas e cenários de uso

| Persona                           | Objetivo                                                        | Cenário-chave                                                                                                       |
| --------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Mantenedor intermitente           | Encerrar a sessão e deixar o registro reproduzível no histórico | Roda `/encerrar-sessao` ao fim do dia e o fechamento já fica commitado, sem `git` manual.                           |
| Agente de IA (Claude/Antigravity) | Fechar a sessão a partir do chat                                | Aciona o slash command materializado, que delega ao mesmo `CommandService`.                                         |
| Eu-de-daqui-a-meses               | Reconstruir o que aconteceu                                     | Lê o histórico e encontra um commit de encerramento por cima do último commit de trabalho, com a âncora preservada. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** O comando `encerrar-sessao` passa a **versionar** o registro de encerramento, criando um commit por cima do estado salvo. Vale para **toda** superfície de acionamento (CLI/slash command e tool MCP), por residir no `CommandService` compartilhado. 🟢
   - Origem no legado: `_reversa_sdd/comandos-customizados/requirements.md` (RF-02, hoje sem commit)
   - Tipo: alterada
2. **RN-02:** O commit de encerramento inclui **somente** o caminho do arquivo de estado (`state_file`); jamais usa `git add -A` nem arrasta qualquer outra mudança pendente do working tree (ex.: `AGENTS.md`, `CLAUDE.md`, regras da Mira). 🟢
   - Tipo: nova
3. **RN-03:** A âncora gravada no estado é capturada do HEAD **antes** de criar o commit de encerramento e segue apontando para o último commit de **trabalho**; o commit de encerramento fica por cima, nunca é a própria âncora. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.3` (RN-07 — âncora de integridade)
   - Tipo: alterada
4. **RN-04:** A mensagem do commit de encerramento é limpa: sem trailer de co-autoria nem qualquer atribuição de autoria ao assistente. 🟢
   - Tipo: nova
5. **RN-05:** Se o commit de encerramento não puder ser criado, o comando falha de forma **barulhenta**, com erro nomeado, e não devolve mensagem de sucesso. O `state_file` já gravado é **preservado** (não revertido): o estado fica salvo-porém-não-versionado e o erro avisa que faltou versionar. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#RN-N4` (falha barulhenta é o padrão)
   - Tipo: nova
6. **RN-06:** A mensagem de retorno do comando reporta **dois** hashes: a âncora (último commit de trabalho) e o hash do commit de encerramento criado por cima. 🟡
   - Origem no legado: `_reversa_sdd/comandos-customizados/requirements.md` (mensagem atual cita só a âncora)
   - Tipo: alterada

## 5. Requisitos Funcionais

| ID    | Requisito                                                                                                       | Prioridade | Critério de aceite                                                                                                                                                                             | Confidência |
| ----- | --------------------------------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | A porta de Git ganha a capacidade de criar um commit restrito a caminhos dados, devolvendo o hash do novo HEAD. | Must       | Existe no contrato da porta uma operação `commit_paths(repo_path, paths, message) -> str` que adiciona **apenas** os caminhos informados e cria um commit, retornando o hash resultante.       | 🟢          |
| RF-02 | Ao encerrar uma sessão ativa, o estado é gravado **e** versionado num commit.                                   | Must       | Após `/encerrar-sessao`, `git status` do `state_file` fica limpo (sem pendência); existe um novo commit no HEAD contendo esse arquivo.                                                         | 🟢          |
| RF-03 | O commit de encerramento contém exclusivamente o `state_file`.                                                  | Must       | O diff do commit criado lista **um único** arquivo (o `state_file`); mudanças pendentes alheias permanecem no working tree, não commitadas.                                                    | 🟢          |
| RF-04 | A âncora reportada/gravada é o HEAD anterior ao commit de encerramento.                                         | Must       | O `commit_hash` do estado e a âncora exibida são iguais ao HEAD imediatamente **antes** do commit de encerramento.                                                                             | 🟢          |
| RF-05 | A saída do comando reporta âncora e hash do commit de encerramento.                                             | Must       | A mensagem de sucesso contém os dois hashes, distinguíveis (âncora vs. encerramento).                                                                                                          | 🟡          |
| RF-06 | Falha barulhenta com erro nomeado quando o commit não puder ser criado, preservando o estado salvo.             | Must       | Se a criação do commit falhar, o comando levanta erro nomeado (não imprime sucesso) e o `state_file` gravado permanece em disco.                                                               | 🟢          |
| RF-07 | O comportamento é coberto por testes de unidade com um Git fake.                                                | Must       | Há testes que verificam: âncora = HEAD pré-commit; commit inclui só o `state_file`; saída reporta os dois hashes.                                                                              | 🟢          |
| RF-08 | O texto exibido pelos slash commands materializados é reescrito para refletir o commit de encerramento.         | Should     | A `description`/corpo dos artefatos (Claude e Antigravity) descreve que o encerramento cria um commit de registro por cima do último commit de trabalho, de forma consistente entre os perfis. | 🟢          |

## 6. Requisitos Não Funcionais

| Tipo                   | Requisito                                                                                             | Evidência ou justificativa                                                              | Confidência |
| ---------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ----------- |
| Reprodutibilidade      | O registro de encerramento fica no histórico versionado, não como mudança pendente fácil de esquecer. | Objetivo central da feature; alinhado a RN-N1 (estado é artefato versionado).           | 🟢          |
| Isolamento / Segurança | O commit nunca arrasta mudanças alheias do working tree; só o `state_file` entra.                     | RN-02; `git add -A` contaminaria o commit com `AGENTS.md`/`CLAUDE.md`/regras pendentes. | 🟢          |
| Observabilidade        | Falha de commit é explícita, com erro nomeado, sem mensagem de sucesso enganosa.                      | RN-05; padrão de falha barulhenta do projeto (`_reversa_sdd/domain.md#RN-N4`).          | 🟢          |
| Baixo acoplamento      | O domínio comita apenas pela porta `GitPort`; o `git` concreto fica no adapter.                       | RN-N5; preserva o core agnóstico à infraestrutura.                                      | 🟢          |
| Conformidade           | Mensagem de commit sem trailer de co-autoria.                                                         | RN-04; preferência absoluta do mantenedor.                                              | 🟢          |

## 7. Critérios de Aceitação

```gherkin
Cenário: Encerramento versiona apenas o estado
  Dado uma sessão ativa e mudanças pendentes alheias no working tree
  Quando executo `encerrar-sessao`
  Então um commit é criado contendo exclusivamente o arquivo de estado
  E as mudanças pendentes alheias permanecem não commitadas no working tree.

Cenário: Âncora é o trabalho, não o encerramento
  Dado uma sessão ativa sobre o HEAD de trabalho H
  Quando executo `encerrar-sessao`
  Então a âncora gravada e exibida é H
  E o commit de encerramento fica por cima de H, sem se tornar a âncora.

Cenário: Saída reporta os dois hashes
  Dado uma sessão ativa
  Quando executo `encerrar-sessao` com sucesso
  Então a mensagem informa a âncora (commit de trabalho) e o hash do commit de encerramento.

Cenário: Mensagem de commit limpa
  Dado uma sessão ativa
  Quando o commit de encerramento é criado
  Então sua mensagem não contém trailer de co-autoria nem atribuição ao assistente.

Cenário: Falha de commit é barulhenta e preserva o estado
  Dado uma sessão ativa
  E que a criação do commit não pode ser concluída
  Quando executo `encerrar-sessao`
  Então o comando levanta um erro nomeado e não devolve mensagem de sucesso
  E o arquivo de estado gravado permanece em disco (não é revertido).

Cenário: Sem sessão ativa
  Dado que não há sessão ativa
  Quando executo `encerrar-sessao`
  Então o comando retorna o erro de "nenhuma sessão ativa" e nenhum commit é criado.
```

## 8. Prioridade MoSCoW

| Item                                               | MoSCoW | Justificativa                                                                   |
| -------------------------------------------------- | ------ | ------------------------------------------------------------------------------- |
| RF-01 (capacidade de commit por caminhos na porta) | Must   | Pré-condição para versionar o encerramento sem acoplar o domínio ao `git`.      |
| RF-02 / RF-03 (versiona só o state_file)           | Must   | Coração da feature; o isolamento é o ponto mais fácil de errar.                 |
| RF-04 (âncora pré-commit)                          | Must   | Sem isso a âncora aponta para o próprio encerramento e a retomada perde a base. |
| RF-06 (falha barulhenta)                           | Must   | Padrão do projeto; sucesso silencioso sobre commit falho é dívida.              |
| RF-05 (dois hashes na saída)                       | Should | Melhora a legibilidade do fechamento; não bloqueia o efeito principal.          |
| RF-08 (texto do slash command)                     | Should | Coerência da documentação exibida com o efeito real; baixo custo.               |

## 9. Esclarecimentos

### Sessão 2026-06-26

- **Q:** A persistência por commit deve valer para qual(is) superfície(s) de acionamento de `encerrar-sessao` (o `CommandService` é compartilhado por CLI/slash command e tool MCP)?
  **R:** Todas. O commit é implementado no `CommandService`, valendo igualmente para CLI/slash command e para a tool MCP — escolha mais coesa (um só lugar, SRP). Registrado em RN-01.
- **Q:** Quando o commit de encerramento falha mas o `state_file` já foi gravado, qual o comportamento esperado?
  **R:** Manter o estado salvo (não reverter) e levantar erro nomeado. O registro de fechamento não se perde; o erro barulhento avisa que faltou versionar. Registrado em RN-05/RF-06.
- **Q:** A `description` atual dos slash commands ("gravando o commit-âncora") deve ser reescrita?
  **R:** Sim, reescrever para refletir que o encerramento cria um commit de registro por cima do último commit de trabalho. O texto atual já é impreciso e ficaria enganoso; o custo de corrigir é mínimo (strings nos `HarnessProfile`, sem acoplamento novo). Registrado em RF-08.

## 10. Lacunas

> Nenhuma lacuna em aberto. As três dúvidas iniciais foram resolvidas na Sessão 2026-06-26 (ver Esclarecimentos).

## 11. Histórico de alterações

| Data       | Alteração                                                                                                                | Autor   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------ | ------- |
| 2026-06-26 | Versão inicial gerada por `/reversa-requirements`                                                                        | reversa |
| 2026-06-26 | Três dúvidas resolvidas por `/reversa-clarify` (escopo CLI+MCP, falha preserva estado, texto do slash command reescrito) | reversa |
