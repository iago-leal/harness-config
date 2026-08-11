# harness

> Camada de governança de sessão para agentes de código (Claude, Gemini, Antigravity), instalada por projeto, com footprint global zero. Este repositório é o **upstream**: o código vive aqui e os projetos-alvo executam-no por um shim (fonte única).

**Versão do core:** 2.6.0 · **Categoria:** Aplicação (Princípio nº 4) · **Suíte:** 389 testes

## O que ele resolve

Um mantenedor intermitente perde contexto entre sessões e entre semanas. O harness ataca isso com três mecanismos, todos versionados dentro do próprio projeto-alvo, sob `.harness/`:

1. **Estado de sessão** (`.harness/estado-da-sessao.md`): o que foi feito, próximos passos e pendências. Reinjetado automaticamente no início de cada sessão (`cmd resume`, via hook `SessionStart` do Claude) e regravado no encerramento consentido (skill `encerrar-sessao`).
2. **Microdecisões** (`.harness/decisoes/MD-NNNN.md`): fichas de decisão técnica com grafo de relações (`refina`, `depende-de`, `estende`, `substitui`, `relaciona`, `bloqueia`). Dois artefatos derivados, nunca editados à mão: o índice completo com backlinks (`.harness/microdecisoes.md`) e a **visão compacta** (`.harness/decisoes-recentes.md`) — contagem, ponteiros e as 10 fichas mais recentes. É a compacta que entra no início da sessão; o índice completo fica a um passo de leitura, sob demanda.
3. **Formatação e ganchos**: formatador por extensão nos ganchos git (`pre-commit`) e nos eventos do agente, com opt-out e exclusões configuráveis no `harness.toml`.

## Instalação num projeto

O destino precisa ser um repositório git. A partir da raiz deste upstream:

```bash
./harness init /caminho/do/projeto              # perfil claude (padrão)
./harness init /caminho/do/projeto --harness antigravity
```

O `init` grava no destino: o shim `harness` (executa o core daqui, com o cwd do projeto), a árvore `.harness/`, o `harness.toml`, os ganchos git, os artefatos da IDE (slash commands; `hooks.json` no Antigravity) e um trecho de guidance sobre microdecisões no arquivo da engine (`CLAUDE.md`, `AGENTS.md` ou `GEMINI.md`), gravado uma única vez e idempotente pelo marcador `<!-- harness:decisoes -->`.

Instalações antigas com core copiado convertem-se com `./harness migrate <raiz>` (execução manual e consciente: reescreve várias instalações de uma vez).

## Comandos principais

| Comando | Função |
|---|---|
| `./harness decisions` | Valida o grafo de microdecisões e deriva o índice e a visão compacta (escrita só quando há mudança). Com `--gate` (hook Stop do Claude), avalia pendência de registro e avisa em stderr, sem nunca bloquear o turno. |
| `./harness cmd resume` | Reinjeta o estado da sessão; no Claude, anexa a visão compacta de decisões (fallback para o índice completo, com aviso). |
| `./harness cmd encerrar-sessao` | Encerra a sessão: pré-check de trabalho pendente, regravação do estado e ofertas de fim de sessão. Escrita no git só com consentimento; `--sem-decisao` declara sessão sem decisão não óbvia. |
| `./harness progress` | Mede o progresso dos entregáveis (ciclo forward + harness) e regrava `.harness/progresso.md` e o board kanban quando o estado mudou. |
| `./harness init` / `upgrade` / `migrate` | Ciclo de vida das instalações (fonte única: o alvo executa o core do upstream). |
| `./harness bootstrap` / `format` / `agy-hook` / `materialize` | Ganchos git, formatação pontual, driver de borda do Antigravity e rematerialização dos artefatos de IDE. |
| `./harness doc-gen` / `doc-serve` / `install-prompt` | Documentação HTML local e prompt de instalação colável. |

`./harness --help` é a referência completa e sempre atual.

## Arquitetura em uma linha

Hexagonal (portas e adaptadores): regras de negócio em `.harness/harness-core/src/core/` (uma pasta por capacidade), contratos em `core/ports/` (`FileSystemPort`, `GitPort`, `ProcessPort`) e três drivers de entrada em `src/adapters/` — a CLI (`main.py`), o servidor MCP e a ponte de ganchos do Antigravity. O core é agnóstico ao harness ativo; diferenças por engine vivem nos perfis e nas bordas. A extração completa (C4, regras de negócio RN-NN, ADRs, specs) está em `_reversa_sdd/`; o ciclo forward de features, em `_reversa_forward/`.

## Princípios operacionais

- **Erros barulhentos, nunca bloqueantes nas bordas de hook**: falha vira aviso em stderr com exit 0; o laço do agente jamais trava por causa do harness.
- **Artefatos derivados não se editam à mão** e só são regravados quando os bytes mudam (índice, visão compacta, progresso, board).
- **Escrita no git só com consentimento**: o encerramento pergunta no terminal e exige flag explícita fora dele.
- **Footprint zero fora do projeto-alvo**: nada na config global do usuário.

## Desenvolvimento (neste upstream)

```bash
cd .harness/harness-core
.venv/bin/python -m pytest -q      # suíte completa (CI roda pytest em Python 3.12/3.13)
ruff check src tests               # lint local (o CI não roda ruff; dívida antiga é tolerada)
```

A versão do core é o literal `version` em `src/core/domain/config.py` (o `upgrade` a lê por regex: manter literal). O processo de evolução é o ciclo Reversa: `/reversa-requirements` → `clarify` → `plan` → `to-do` → `coding`, com re-extração `/reversa` fechando o ciclo — cada feature deixa `legacy-impact.md` e `regression-watch.md` como rastro auditável.
