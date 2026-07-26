# Investigation: Oferta de commit consentida

> Identificador: `024-oferta-commit-consentida`
> Data: `2026-07-23`

## 1. Pergunta de fundo

O pedido de superfície é "tirar o commit automático". O problema por trás é de
**mandato**: o encerramento da sessão escreve no histórico do git sem que o
usuário tenha autorizado aquela escrita específica, e escrita em histórico é
custosa de desfazer — sobretudo em repositórios da mesma raiz que guardam dados
sensíveis (`chagas-ms`, `experimento`). A feature devolve ao usuário o ponto de
decisão, sem devolver o trabalho manual.

## 2. Como o legado chegou aqui

A automação atual não foi descuido; foi acúmulo de três decisões defensáveis,
cada uma resolvendo um problema real:

| Feature | O que introduziu | Problema que resolvia |
|---------|------------------|------------------------|
| 013 | Commit de registro do fechamento (RN-N31) | Antes, o registro ficava como mudança pendente eterna no working tree |
| 016 | Pré-check de pendência com marker e protocolo abortar-e-reexecutar | Encerrar sobre árvore suja produzia âncora mentirosa |
| 019 | Alargamento do pré-check para cobrir `.harness/` exceto o `state_file` | Decisões e índice ficavam num vão sem oferta e sem captura |

O que nenhuma das três decidiu foi **quem autoriza**. A instrução "commite e rode
novamente", escrita no campo `acao` do marker, foi lida pelo agente como ordem —
e é, literalmente. A feature 024 não desfaz nenhuma das três; insere o
consentimento onde ele nunca esteve.

## 3. Precedente interno decisivo

A feature 014 já resolveu exatamente este problema para o `git push`:
`conduct_end_session_offers` pergunta `[s/N]` antes de publicar, com aviso
reforçado quando a branch é a principal, tudo por `asker` injetável e com
degradação para markers quando não há terminal. **Não há nada a inventar**: o
padrão existe, é testado, e esta feature o estende a dois pontos que ficaram de
fora. Quando duas ações de mesma natureza — escrever no repositório remoto,
escrever no repositório local — têm regimes de consentimento diferentes, a
assimetria é o defeito, não a simetria.

## 4. Alternativas avaliadas

### 4.1 Onde a pergunta vive

| Alternativa | Avaliação |
|-------------|-----------|
| Só na skill (texto do `SKILL.md` e do campo `acao`) | Mais barato e reversível, mas deixa o usuário de terminal puro sem nada: pela linha de comando o comportamento seguiria idêntico. Descartada por quebrar a paridade da RN-N33 |
| Só no core, com o core executando o commit autorizado | Daria paridade total, ao custo de violar a RN-N5 e de obrigar o core a gerar mensagem de commit — exatamente o tipo de invenção que a RN-N3 proíbe para a narrativa |
| **Core pergunta o que pode cumprir; agente pergunta o que ele cumpre** | Escolhida. Cada borda pergunta dentro do seu mandato; nenhuma oferta falsa |

### 4.2 Canal de resposta sem terminal interativo

| Alternativa | Avaliação |
|-------------|-----------|
| **Flags de linha de comando** | Escolhida. Já consagrada pelo `--sem-decisao` (022); o agente re-roda o script com a flag, e o rastro fica visível na conversa |
| Arquivo de resposta sob `.harness/` | Descartada. Scratch novo em `.harness/` foi tentado e revertido na MD-0015: vira `COMMIT_PENDENTE` perpétuo ou exige `.gitignore` em toda a base instalada |
| Leitura de `stdin` sem TTY | Descartada. No fluxo de hook não há entrada interativa; `input()` sem TTY levanta `EOFError` |
| Variável de ambiente | Descartada. Decisão invisível no histórico da conversa e no rastro do comando |

### 4.3 O que fazer quando não há a quem perguntar (achado A002 da auditoria)

A primeira versão deste plano assumia que, sem terminal, o commit de encerramento
seguiria sendo gravado por default, e que a skill instruiria o agente a perguntar
antes. A auditoria mostrou o buraco: no caminho mais usado — encerramento
conduzido pelo agente —, o consentimento seria apenas textual, e um agente
desatento produziria exatamente o commit automático que a feature veio eliminar.

| Alternativa | Avaliação |
|-------------|-----------|
| **Inverter o default sem terminal** | Escolhida. Sem autorização declarada, não versiona. Erro de esquecimento passa a ser conservador: nada entra no histórico, e o marker torna a omissão visível |
| Quarto portão abortivo | Garantia mais forte, mas empilha um terceiro round-trip sobre os portões existentes; o encerramento chegaria a exigir três reexecuções em série |
| Aceitar o automático sem terminal | Mais barato, porém a garantia volta a ser textual — a mesma fragilidade que a feature 022 já concluiu ser insuficiente quando criou um portão no core |

### 4.4 Desfecho do encerramento recusado

| Alternativa | Avaliação |
|-------------|-----------|
| **Fechar no arquivo, não versionar, declarar na narrativa** | Escolhida. Reusa o mecanismo do `--sem-decisao`, único caso já aceito de o core escrever na narrativa por ato deliberado do usuário |
| Não fechar (abortar) | Descartada. Confunde duas coisas: encerrar a sessão e versionar o encerramento |
| Fechar e guardar a intenção num campo novo do front-matter | Descartada. Campo de schema para registrar evento pontual; a narrativa já é o lugar de eventos |

## 5. Padrões aplicáveis

- **Command–Query com consentimento na borda**: o serviço de domínio
  (`CommandService`) recebe a decisão pronta por parâmetro (`versionar_estado`) e
  segue livre de IO; toda pergunta fica no orquestrador de borda
  (`SessionCloseFlow`), que já é o lugar do `asker`.
- **Protocolo abortar-e-reexecutar**: consagrado nas features 016/019/022, é a
  forma de "pergunta" disponível quando não há terminal — o processo termina, o
  agente conversa, o processo reinicia com a resposta embutida no argumento.
- **Default seguro assimétrico por borda**: no terminal, a pergunta do commit de
  encerramento usa `[S/n]`, porque há um humano presente e o "não" é que deixa
  rastro pendente; sem terminal não há resposta possível, e a omissão passa a
  significar recusa (RN-08). O mesmo ponto de decisão, portanto, tem defaults
  opostos conforme exista ou não alguém a quem perguntar — o critério não é o
  desfecho preferido, é quem está presente para escolher.

## 6. Fontes

Todas internas ao repositório — esta feature não depende de biblioteca, serviço
ou padrão externo:

- `_reversa_sdd/domain.md` §RN-N5, §RN-N31, §RN-N33, §RN-N34, §RN-N4
- `_reversa_sdd/state-machines.md` — nota dos três portões antes de `ATIVA → INATIVA`
- `_reversa_sdd/code-analysis.md` — seções `session/close_flow`, `commands/service`, `main`
- `_reversa_forward/019-oferta-commit-cobre-harness/interfaces/commit-pendente-marker.md`
- `.harness/decisoes/MD-0015.md` — porquê do scratch dedicado ter sido descartado
- Código as-built: `src/core/session/close_flow.py`, `src/core/commands/service.py:38-88`,
  `src/main.py:409-414`, `.claude/skills/encerrar-sessao/scripts/encerrar_sessao.py`

## 7. Questão que fica para o futuro

Se a fricção de perguntar duas vezes por sessão incomodar na prática, o caminho
natural **não** é voltar ao automático, e sim permitir uma resposta persistente
por projeto (`harness.toml`, seção `[session]`, algo como
`commit_registro = "sempre" | "perguntar" | "nunca"`). Isso é feature própria e
fica fora deste escopo — registrado aqui para não se perder.
