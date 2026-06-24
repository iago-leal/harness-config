# Interface: arquivos de slash command de encerrar-sessao

> Identificador: `010-command-encerrar-sessao`
> Data: `2026-06-24`
> Tipo de contrato: artefato de arquivo consumido pela IDE do agente (não é contrato de rede)

Contrato dos dois arquivos que `materialize_session_commands` grava no projeto-alvo. Cada harness lê o seu diretório para expor o slash command. O conteúdo é produzido pelo respectivo `HarnessProfile` (D-02); este documento fixa o formato esperado.

## 1. Claude Code — `.claude/commands/encerrar-sessao.md`

- **Caminho:** `<project>/.claude/commands/encerrar-sessao.md`
- **Gatilho:** o usuário digita `/encerrar-sessao` no chat do Claude Code.
- **Execução:** direta e determinística, via `!`-bash embutido.
- **Caminho do wrapper:** `./harness` (relativo). O `!`-bash de slash command roda com cwd na raiz do projeto, então o caminho relativo resolve o wrapper e sobrevive a repo movido. `${CLAUDE_PROJECT_DIR}` **não** é expandida nesse contexto — ao contrário dos hooks, viraria `/harness` (bug conhecido do Claude Code, issue #33815) — por isso não é usada aqui.

Formato de referência (a forma final é responsabilidade do `ClaudeProfile`):

```markdown
---
description: Encerra a sessão de trabalho do Harness, gravando o commit-âncora.
allowed-tools: Bash(./harness cmd encerrar-sessao:*)
---

Encerrando a sessão do Harness e gravando o commit-âncora:

!`./harness cmd encerrar-sessao`
```

- **Saída esperada ao usuário:** a mensagem do `CommandService` (sucesso com feature + commit-âncora, ou "Nenhuma sessão ativa encontrada para encerrar").
- **Idempotência:** o arquivo é dono do nome `encerrar-sessao`; reescrito a cada `init`/`upgrade` sem alterar outros comandos do diretório.

## 2. Antigravity — `.agents/workflows/encerrar-sessao.md`

- **Caminho:** `<project>/.agents/workflows/encerrar-sessao.md`
- **Gatilho:** salvar o arquivo registra `encerrar-sessao` como comando no chat do Antigravity.
- **Execução:** invoca `<command_path>/harness cmd encerrar-sessao`, onde `command_path` é o **caminho absoluto** do projeto resolvido na materialização (mesmo padrão de `<ABS>` em `materialize_hooks_json`). Se o modelo de workflow do Antigravity não executar shell embutido, o corpo instrui o agente a rodar o comando (degradação prevista em D-06).

Formato de referência (a forma final é responsabilidade do `AntigravityProfile`):

```markdown
---
name: encerrar-sessao
description: Encerra a sessão de trabalho do Harness, gravando o commit-âncora.
---

Execute, a partir da raiz do projeto, o comando abaixo e mostre a saída ao usuário:

`<command_path>/harness cmd encerrar-sessao`
```

- **`<command_path>`:** substituído pelo caminho absoluto na materialização; o `upgrade` reescreve se o repositório foi movido.
- **Idempotência:** mesma do Claude — dono do nome `encerrar-sessao`, demais workflows intocados.

## Invariantes comuns

- Toda escrita ocorre sob `<project>` (footprint global zero, RN-N17).
- Escrita atômica via `FileSystemPort.write_file_atomic`.
- Nenhum dos dois arquivos reimplementa a lógica de encerramento: ambos delegam ao `./harness cmd encerrar-sessao`, que exige sessão ativa e grava o commit-âncora (`_reversa_sdd/comandos-customizados/requirements.md#RF-02`).

## Pendência de verificação

- 🟡 O comportamento exato do workflow do Antigravity (execução de shell embutida vs instrução ao agente) não é verificável localmente; validar contra o Antigravity real quando disponível, alinhado ao watch-item amarelo herdado da feature 009.
