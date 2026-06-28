# Spec: Skill `encerrar-sessao`

## Propósito

Esta é a especificação determinística e reproduzível da skill `encerrar-sessao`.
Qualquer agente que receba este documento e execute o Skill Creator DEVE produzir
a mesma skill, sem ambiguidade. A skill é conversacional/instrucional: não traz
scripts, dependências nem persistência próprios — ela conduz o agente a executar o
wrapper `./harness` do projeto e a reagir aos markers que ele emite.

---

## 1. Identidade da Skill

| Campo           | Valor                                                                                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Nome**        | `encerrar-sessao`                                                                                                                                      |
| **Diretório**   | `encerrar-sessao/` (sob `.agents/skills/` do projeto)                                                                                                  |
| **Propósito**   | Encerrar a sessão do Harness de forma autônoma: regenerar artefatos, oferecer commit do trabalho pendente e gravar o commit de registro do fechamento. |
| **Domínio**     | Automação de sessão / ferramentas de desenvolvimento (harness multi-IDE)                                                                               |
| **Privacidade** | Local — opera apenas sob a raiz do projeto via `./harness`; não envia dados a serviços externos.                                                       |
| **Versão**      | `1.0.0`                                                                                                                                                |

---

## 2. Estrutura de Arquivos (Obrigatória)

```
encerrar-sessao/
├── SKILL.md
└── SPEC.md
```

Skill de arquivo único: sem `scripts/`, `references/` ou `assets/` — espelha a forma
de todas as skills do Reversa em `.agents/skills/` (cada uma é um diretório com um só
`SKILL.md`).

---

## 3. SKILL.md — Conteúdo Obrigatório

### 3.1 Frontmatter YAML (literal)

```yaml
---
name: encerrar-sessao
description: >
  Encerra a sessão do Harness — regenera os artefatos derivados, oferece commitar o
  trabalho pendente e grava o commit de registro do fechamento por cima do último
  commit de trabalho. Ative quando o usuário pedir para "encerrar a sessão", "fechar
  a sessão", "finalizar a sessão", "encerrar sessão do Harness" ou digitar
  "/encerrar-sessao". NÃO ative para iniciar ou retomar a sessão (isso é função do
  resume), nem para apenas commitar trabalho sem encerrar.
license: MIT
compatibility: Antigravity, Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills.
metadata:
  author: iagoleal
  version: "1.0.0"
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

#### Seção: Sequência de encerramento

- Lista ordenada com 4 passos, da raiz do projeto.
- Passo 1: `./harness cmd regen` — se exit code ≠ 0, parar e mostrar o erro; não encerrar.
- Passo 2: `./harness cmd encerrar-sessao` — fechamento vira commit de registro por cima do trabalho.

#### Seção: Tratamento do marker COMMIT_PENDENTE

- Se a saída trouxer `[HARNESS:COMMIT_PENDENTE …]`, commitar o trabalho real por caminho (`git add -- <arquivo>`), nunca `git add -A`, e repetir o passo 2.

#### Seção: Ofertas pós-fechamento

- Conduzir as ofertas de `git push` e `./harness upgrade` se aparecerem markers; mostrar a saída ao usuário.

---

## 4. Scripts — Especificação Detalhada

N/A — skill conversacional/instrucional. Ela não define scripts próprios; conduz o
agente a invocar o wrapper `./harness` (subcomandos `cmd regen`, `cmd encerrar-sessao`),
que pertence ao projeto e é especificado fora desta skill (harness-core).

---

## 5. Dependências (Versões Fixas)

N/A — a skill não tem dependências de runtime próprias. Ela pressupõe apenas o wrapper
executável `./harness` presente na raiz do projeto, fornecido pelo harness-core.

### 5.1 Dependências Python

N/A — nenhuma.

### 5.2 Dependências de Sistema

N/A — nenhuma além do `git` e do `./harness`, já assumidos pelo ambiente do projeto.

---

## 6. Armazenamento de Dados

N/A — a skill não persiste dados próprios. O estado de sessão é gerido pelo
`./harness cmd encerrar-sessao`, que grava em `.harness/estado-da-sessao.md` (fora do
escopo desta skill).

---

## 7. Padrões de Implementação Obrigatórios

### 7.1 Delegação (não-reimplementação)

A skill NÃO reimplementa o fechamento: o corpo apenas instrui a chamar
`./harness cmd encerrar-sessao`, que exige sessão ativa e grava o commit de registro.
Espelha a delegação dos slash commands de sessão do harness (RN-N5: o core é agnóstico).

### 7.2 Sequência ordenada e barulhenta

Ordem fixa: `regen` → `encerrar-sessao` → tratamento de `COMMIT_PENDENTE` → ofertas.
Falha em qualquer comando é barulhenta (exit code ≠ 0 interrompe a sequência).

### 7.3 Tratamento de Erros

| Condição                                   | Exit code | Comportamento                                                                    |
| ------------------------------------------ | --------- | -------------------------------------------------------------------------------- |
| `./harness cmd regen` falha                | ≠ 0       | Parar, mostrar o erro, não encerrar a sessão                                     |
| `./harness cmd encerrar-sessao` falha      | ≠ 0       | Reportar a saída ao usuário; não mascarar                                        |
| saída contém `[HARNESS:COMMIT_PENDENTE …]` | 0         | Commitar trabalho por caminho (nunca `git add -A`) e repetir o passo de encerrar |
| caminho feliz                              | 0         | Commit de registro criado; mostrar âncora e commit de fechamento                 |

---

## 8. Fluxo Interativo

N/A — a skill não conduz um questionário com defaults. A única ramificação é reativa
(presença ou ausência do marker `COMMIT_PENDENTE` na saída), já especificada na Seção 7.3.

---

## 9. Critérios de Aceite

A skill está PRONTA quando:

- [ ] O diretório `.agents/skills/encerrar-sessao/` contém `SKILL.md` (MAIÚSCULAS) e `SPEC.md`
- [ ] O frontmatter do `SKILL.md` contém `name: encerrar-sessao` e uma `description` não-vazia com cláusula `NÃO ative`
- [ ] O corpo do `SKILL.md` instrui rodar `./harness cmd regen` antes de `./harness cmd encerrar-sessao`
- [ ] O corpo trata o marker `[HARNESS:COMMIT_PENDENTE …]` commitando por caminho, nunca `git add -A`
- [ ] Ativada por contexto no Antigravity ("encerre a sessão"), o agente executa a sequência e mostra a saída

Cada critério tem resultado binário (passa/falha) por inspeção do arquivo ou da execução.

Happy path que a skill conduz, a partir da raiz do projeto:

```bash
# 1) regenerar artefatos derivados (no-op se não houver [regen])
cd /Users/iagoleal/dev/harness && ./harness cmd regen
# 2) encerrar a sessão (cria o commit de registro por cima do trabalho)
cd /Users/iagoleal/dev/harness && ./harness cmd encerrar-sessao
```

---

## 10. O que esta Skill NÃO faz

- NÃO reimplementa a lógica de fechamento de sessão; delega ao `./harness cmd encerrar-sessao`
- NÃO registra um slash command visual no Antigravity — o catálogo de barra é estático na plataforma; a ativação é semântica por contexto
- NÃO inicia nem retoma a sessão; iniciar/retomar é função do `resume`
- NÃO executa `git add -A` nem commita trabalho sem separar fonte de artefato regenerável
- NÃO publica (`git push`) nem atualiza o core (`./harness upgrade`) sem oferta ou confirmação do usuário

---

## 11. Changelog

| Versão | Data       | Mudança                                                          |
| ------ | ---------- | ---------------------------------------------------------------- |
| 1.0.0  | 2026-06-28 | Versão inicial (extraída da skill por `skill-spec` modo EXTRAIR) |
