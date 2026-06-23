# Comandos Customizados, Design Técnico

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [commands/](file:///Users/iagoleal/dev/harness/harness-config/commands/)

## Interface

Os comandos customizados são definidos na forma de especificações escritas em Markdown ingeridas nativamente pela CLI do Claude Code através do arquivo global `settings.json`.

| Símbolo | Assinatura | Retorno | Observação |
| :--- | :--- | :--- | :--- |
| `/clarificar` | `commands/clarificar.md` | `void` (Interface interativa) | Guiado via chat de prompts. |
| `/encerrar-sessao` | `commands/encerrar-sessao.md` | `void` (Gravação física e commits) | Roda comandos locais do shell do host. |
| `/handoff` | `commands/handoff.md` | `void` (Gravação física em BASTAO.md) | Sincroniza estado de tarefas. |
| `/resume` | `commands/resume.md` | `void` (Leitura física do BASTAO.md) | Recupera tarefas de memória compartilhada. |

---

## Fluxo Principal

### 💬 1. Fluxo do `/clarificar` (PCCP)
1. Extrai a queixa bruta do usuário.
2. Inspeciona a base local buscando fatos (F) em arquivos e commits.
3. Propõe inferências técnicas (I) e lista as lacunas de conhecimento conceitual (H).
4. Limita a iteração a 2 rodadas. Se o usuário digitar `/travar`, encerra o levantamento e inicia o plano.
5. Se estourar rodadas, adota a hipótese (H) mais simples e segura e força a continuidade do ciclo.

### 🚪 2. Fluxo do `/encerrar-sessao`
1. Localiza a raiz do Git e valida integridade.
2. Identifica arquivos alterados e solicita ao desenvolvedor confirmação para realizar commits pequenos.
3. Registra dados do HEAD (hash, branch) em `ESTADO-DA-SESSAO.md`.
4. Roda `gerar-index-decisoes.sh` para recalcular backlinks e compilar `microdecisoes.md`.
5. Valida e reconcilia ganchos do Git.
6. Atualiza arquivos em vaults de Notas pessoais (se configurados).
7. Pergunta interativamente ao desenvolvedor humano se deseja fazer push dos commits locais.

### 🤝 3. Fluxo de Handoff e Resume
* **`handoff.md`:** Executa o script complementar de arquivamento de bastões velhos, cria o payload consolidado de Objetivo, Estado Atual (Fatos/Inferências) e Tarefas Pendentes, e grava sob `~/.agent-memory/BASTAO.md` realizando o commit físico na memória.
* **`resume.md`:** Lê `~/.agent-memory/BASTAO.md` do repositório local, valida integridade de commits do histórico de handoff, resume o status da atividade para o usuário no chat e retoma a próxima tarefa pendente.

---

## Dependências
* `git` — Controle de versão, ancoragem e commits locais.
* `bin/gerar-index-decisoes.sh` — Compilação e backlinks de decisões de design.
* Repositório físico comum local de memória compartilhada (`~/.agent-memory/`).

---

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
| :--- | :--- | :---: |
| Normalização da terminologia de ADR para microdecisão | `commands/encerrar-sessao.md` (commit `83895b0`) | 🟢 |
| Estrutura de prompt interativa do Claude Code baseada em Markdown descritivo | `commands/clarificar.md` | 🟢 |

---

## Observabilidade
* O andamento e o status de cada passo do encerramento de sessão e do handoff são relatados de forma interativa no terminal para controle e acompanhamento visual do usuário humano.
