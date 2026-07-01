# Spec: Skill `encerrar-sessao`

## Propósito

Esta é a especificação determinística e reproduzível da skill `encerrar-sessao`.
Qualquer agente que receba este documento e execute o Skill Creator DEVE produzir
a mesma skill, sem ambiguidade. A skill conduz o agente a **consolidar a narrativa
da sessão** e, então, a invocar um script fino que delega o fechamento ao Harness
Core. Ela não reimplementa a lógica de fechamento; reage aos markers que o core
emite.

---

## 1. Identidade da Skill

| Campo           | Valor                                                                                                                                                     |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nome**        | `encerrar-sessao`                                                                                                                                        |
| **Diretório**   | `encerrar-sessao/` (sob `.agents/skills/` ou `.claude/skills/` do projeto)                                                                               |
| **Propósito**   | Encerrar a sessão do Harness de forma autônoma: atualizar a narrativa, regenerar artefatos, oferecer commit do trabalho pendente e gravar o commit de registro do fechamento. |
| **Domínio**     | Automação de sessão / ferramentas de desenvolvimento (harness multi-IDE)                                                                                 |
| **Privacidade** | Local — opera apenas sob a raiz do projeto; não envia dados a serviços externos.                                                                         |
| **Versão**      | `1.1.0`                                                                                                                                                  |

---

## 2. Estrutura de Arquivos (Obrigatória)

```
encerrar-sessao/
├── SKILL.md
├── SPEC.md
└── scripts/
    ├── encerrar_sessao.py   # ponto de entrada fino: chama os serviços do core
    └── _bootstrap.py        # resolve a raiz do projeto e localiza o Harness Core
```

Os scripts são **finos** e não contêm regra de domínio: resolvem o ambiente e
delegam ao Harness Core (`RegenService`, `SessionCloseFlow`). O corpo do `SKILL.md`
não reimplementa o fechamento; conduz o agente a atualizar a narrativa e a rodar o
script.

---

## 3. SKILL.md — Conteúdo Obrigatório

### 3.1 Frontmatter YAML (literal)

```yaml
---
name: encerrar-sessao
description: >-
  Encerra a sessão do Harness — atualiza a narrativa da sessão, regenera os
  artefatos derivados, oferece commitar o trabalho pendente e grava o commit de
  registro do fechamento por cima do último commit de trabalho. Ative quando o
  usuário pedir para "encerrar a sessão", "fechar a sessão", "finalizar a
  sessão", "encerrar sessão do Harness" ou digitar "/encerrar-sessao". NÃO ative
  para iniciar ou retomar a sessão (isso é função do resume), nem para apenas
  commitar trabalho sem encerrar.
license: MIT
compatibility: Antigravity, Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills.
metadata:
  author: iagoleal
  version: "1.1.0"
  framework: harness
  role: session
---
```

Requisitos do frontmatter, verificados empiricamente no Antigravity:

- O arquivo DEVE se chamar `SKILL.md` (MAIÚSCULAS).
- O frontmatter DEVE conter `name` **e** `description` (só `description` não basta).
- A `description` DEVE conter gatilhos de ativação semântica e ao menos uma cláusula `NÃO ative`.

### 3.2 Corpo do SKILL.md (sub-seções obrigatórias, em ordem)

#### Seção: Cabeçalho

- Um título H1 `# Encerrar sessão do Harness`.
- Um parágrafo explicando que o `estado-da-sessao.md` tem duas metades — o
  front-matter (mantido pelo core) e a narrativa (as 4 seções `##`, escritas pelo
  agente) — e que a narrativa desatualizada é recusada pelo gate.

#### Seção: Passos (lista ordenada, da raiz do projeto)

- Passo 1 — **Atualizar a narrativa**: editar `.harness/estado-da-sessao.md`,
  reescrevendo as quatro seções (`## O que foi feito`, `## Próximos passos`,
  `## Pendências / bloqueios`, `## Ponteiros`) com o trabalho REAL da sessão,
  preservando o front-matter.
- Passo 2 — **Encerrar**: `python3 scripts/encerrar_sessao.py`. O script regenera
  artefatos → pré-check de pendência → gate de narrativa → fechamento (commit de
  registro por cima do trabalho) → ofertas. Se a regeneração falhar (exit ≠ 0),
  para antes de fechar e mostra o erro.

#### Seção: Tratamento do marker COMMIT_PENDENTE

- Se a saída trouxer `[HARNESS:COMMIT_PENDENTE …]`, commitar o trabalho real por
  caminho (`git add -- <arquivo>`), nunca `git add -A`, e repetir o passo 2.

#### Seção: Tratamento do marker NARRATIVA_PENDENTE

- Se a saída trouxer `[HARNESS:NARRATIVA_PENDENTE …]`, a narrativa está vazia ou
  idêntica à do início da sessão: voltar ao Passo 1, reescrever de fato as quatro
  seções e repetir o passo 2.

#### Seção: Ofertas pós-fechamento

- Conduzir as ofertas de `git push` e `./harness upgrade` se aparecerem markers;
  mostrar a saída ao usuário.

---

## 4. Scripts — Especificação Detalhada

| Script               | Papel                                                                                                                                                                                                 |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `encerrar_sessao.py` | Ponto de entrada. Faz o bootstrap, roda da raiz do projeto e, em ordem: `RegenService.run` (aborta barulhento se exit ≠ 0) e `SessionCloseFlow.run`. Não reimplementa regra.                          |
| `_bootstrap.py`      | Resolve a raiz via `git rev-parse --show-toplevel`, localiza o core em `.harness/harness-core`, re-executa sob o venv do core quando preciso (pydantic/toml) e o insere no `sys.path`. `CoreNotFoundError` barulhento quando o core não existe. |

Ambos falham de forma **barulhenta** (exit ≠ 0, mensagem orientadora); nunca em
silêncio.

---

## 5. Dependências (Versões Fixas)

A skill não tem dependências de runtime próprias. Ela pressupõe o **Harness Core**
instalado em `.harness/harness-core` (com o seu venv, que provê `pydantic`/`toml`);
`_bootstrap.py` re-executa o entry point sob esse venv. Requisitos de sistema:
`git` e `python3`, já assumidos pelo ambiente do projeto.

---

## 6. Armazenamento de Dados

A skill não persiste dados próprios. O estado de sessão vive em
`.harness/estado-da-sessao.md`, com duas metades:

- **Front-matter** (âncora, feature, `start_time`, status) — mantido pelo
  `SessionCloseFlow`/`CommandService` do core.
- **Narrativa** (as seções `## O que foi feito`, `## Próximos passos`,
  `## Pendências / bloqueios`, `## Ponteiros`) — **escrita pelo agente**. O core
  nunca a inventa; o gate de narrativa a exige de forma barulhenta antes de fechar.

---

## 7. Padrões de Implementação Obrigatórios

### 7.1 Delegação (não-reimplementação)

A skill NÃO reimplementa o fechamento: os scripts finos chamam `RegenService` e
`SessionCloseFlow` do core, que exigem sessão ativa e gravam o commit de registro
(RN-N5: o core é agnóstico ao harness).

### 7.2 Sequência ordenada e barulhenta

Ordem fixa: **atualizar narrativa** → `encerrar_sessao.py` (regen → pré-check de
pendência → gate de narrativa → fechamento) → tratamento de `COMMIT_PENDENTE` /
`NARRATIVA_PENDENTE` → ofertas. Falha em qualquer etapa é barulhenta (exit ≠ 0 ou
marker que não fecha).

### 7.3 Tratamento de Erros

| Condição                                      | Exit code | Comportamento                                                                    |
| --------------------------------------------- | --------- | -------------------------------------------------------------------------------- |
| regeneração de artefatos falha                | ≠ 0       | Parar, mostrar o erro, não encerrar a sessão                                     |
| Harness Core ausente / não importável         | ≠ 0       | Falha barulhenta do bootstrap; orientar reinstalar com `./harness init`          |
| saída contém `[HARNESS:COMMIT_PENDENTE …]`    | 0         | Commitar trabalho por caminho (nunca `git add -A`) e repetir o passo de encerrar |
| saída contém `[HARNESS:NARRATIVA_PENDENTE …]` | 0         | Reescrever as 4 seções da narrativa e repetir o passo de encerrar                |
| caminho feliz                                 | 0         | Commit de registro criado; mostrar âncora e commit de fechamento                 |

---

## 8. Fluxo Interativo

N/A — a skill não conduz um questionário com defaults. As ramificações são
reativas à presença dos markers `COMMIT_PENDENTE` e `NARRATIVA_PENDENTE` na saída,
já especificadas na Seção 7.3.

---

## 9. Critérios de Aceite

A skill está PRONTA quando:

- [ ] O diretório `encerrar-sessao/` contém `SKILL.md` (MAIÚSCULAS), `SPEC.md` e `scripts/{encerrar_sessao.py,_bootstrap.py}`
- [ ] O frontmatter do `SKILL.md` contém `name: encerrar-sessao` e uma `description` não-vazia com cláusula `NÃO ative`
- [ ] O corpo do `SKILL.md` instrui atualizar a narrativa (as 4 seções) ANTES de rodar `python3 scripts/encerrar_sessao.py`
- [ ] O corpo trata o marker `[HARNESS:COMMIT_PENDENTE …]` commitando por caminho, nunca `git add -A`
- [ ] O corpo trata o marker `[HARNESS:NARRATIVA_PENDENTE …]` reescrevendo a narrativa e repetindo o encerramento
- [ ] Ativada por contexto ("encerre a sessão"), o agente atualiza a narrativa, executa a sequência e mostra a saída

Cada critério tem resultado binário (passa/falha) por inspeção do arquivo ou da execução.

Happy path que a skill conduz, a partir da raiz do projeto:

```bash
# 1) atualizar a narrativa das 4 seções em .harness/estado-da-sessao.md (edição do agente)
# 2) encerrar a sessão (regen → pré-check → gate de narrativa → commit de registro)
python3 scripts/encerrar_sessao.py
```

---

## 10. O que esta Skill NÃO faz

- NÃO reimplementa a lógica de fechamento de sessão; delega ao Harness Core via scripts finos
- NÃO inventa a narrativa: ela é escrita pelo agente; o core só a preserva e a exige
- NÃO registra um slash command visual no Antigravity — o catálogo de barra é estático na plataforma; a ativação é semântica por contexto
- NÃO inicia nem retoma a sessão; iniciar/retomar é função do `resume`
- NÃO executa `git add -A` nem commita trabalho sem separar fonte de artefato regenerável
- NÃO publica (`git push`) nem atualiza o core (`./harness upgrade`) sem oferta ou confirmação do usuário

---

## 11. Changelog

| Versão | Data       | Mudança                                                                                              |
| ------ | ---------- | --------------------------------------------------------------------------------------------------- |
| 1.1.0  | 2026-07-01 | Passo de atualização da narrativa + marker `NARRATIVA_PENDENTE`; SPEC alinhada à implementação de scripts finos (feature 018) |
| 1.0.0  | 2026-06-28 | Versão inicial (extraída da skill por `skill-spec` modo EXTRAIR)                                     |
