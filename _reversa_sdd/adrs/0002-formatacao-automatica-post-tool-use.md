# ADR 0002: Formatação Automática Pós-Edição de Código

- **Status:** Parcialmente revertido (gatilho `PostToolUse` aposentado no perfil Claude — ver nota de 2026-07-07)
- **Data:** 2026-06-21
- **Contexto Técnico:** Módulo `hooks` (`format-on-edit.sh`)
- **Escala de Confiança:** 🟢 CONFIRMADO

> ⚠️ **Atualização (2026-07-05, fechamento do G-05):** a decisão de fundo **permanece** (formatação automática no `PostToolUse`, não-bloqueante, com preferência por binários locais e opt-out por projeto). O que foi superado é o mecanismo: o roteador shell `hooks/format-on-edit.sh` deu lugar ao `FormattingService` (`src/core/formatting/service.py`), invocado pelo comando `harness format` — que continua alimentado pelo JSON do hook `PostToolUse` via stdin (`tool_input.file_path`) e, no Antigravity, por um adaptador de borda em `.agents/` (ADR 0016). As salvaguardas e o opt-out passaram do arquivo `.no-autoformat` para exclusões configuradas no `harness.toml` (ADR 0015, feature 008). Porta shell→Python sob a arquitetura hexagonal do ADR 0006.
>
> ⛔ **Atualização (2026-07-07) — gatilho `PostToolUse` aposentado no perfil Claude:** a formatação *on-edit* deixou de ser materializada no `.claude/settings.json`. O `ClaudeProfile.hooks_block()` não emite mais o item `PostToolUse → harness format`, e a assinatura `"harness format"` saiu de `_HARNESS_COMMAND_SIGNATURES` (`src/core/install/claude_settings.py`). Motivo: em máquina com dezenas de projetos, o hook — herdado inclusive pelo `.claude/settings.json` da pasta-mãe `~/dev` — reescrevia arquivos (notadamente `.md` via prettier) a cada edição, em diretórios onde o usuário não pediu formatação, repetindo o incômodo que a descontinuação do `format-on-edit.sh` global já havia tratado. **Preservados:** (1) o `harness format` no **git pre-commit** (`bootstrap/service.py`), gatilho deliberado no commit; (2) o `PostToolUse` do **perfil Antigravity** (`agy-hook`), mecanismo à parte. Reintrodução é **opt-in manual** por diretório. O comando `harness format` e o `FormattingService` seguem intactos para uso sob demanda e para o pre-commit.

## Contexto e Problema

Manter padrões de estilo consistentes (como ruff, prettier, rustfmt, shfmt) em um repositório evoluído de forma colaborativa por múltiplos agentes de IA e desenvolvedores humanos é um desafio. Se a formatação for delegada a uma tarefa manual ou commit tardio, há o risco de commits poluídos por problemas de formatação dispersos.

## Decisão

Adotar um script roteador centralizado (`hooks/format-on-edit.sh`) que intercepta o gancho de ciclo de vida `PostToolUse` (especificamente os matchers de escrita e edição de arquivos `Write|Edit`) do Claude Code.

Toda vez que o agente de IA edita ou grava um arquivo, o script intercepta o evento, determina se o arquivo faz parte de um projeto de software legítimo (subindo a árvore em busca de arquivos de manifesto) e despacha o arquivo para o formatador adequado com as seguintes premissas:

1. **Preferência Local:** Executa binários contidos no projeto (ex: `.venv/bin/ruff`, `node_modules/.bin/prettier`) antes de recorrer a binários instalados globalmente na máquina.
2. **Salvaguarda do Home e Vaults:** Impede a formatação de arquivos no `$HOME`, diretórios de configuração (`~/.claude`) ou notas Obsidian (`~/Notas`) para evitar danos em dados pessoais ou corporativos que não sejam código.
3. **Garantia de Não-Bloqueio:** O script retorna sempre status exit `0`, mesmo se houver falhas internas ou ferramentas de formatação ausentes, para evitar que problemas de estilo impeçam a gravação do progresso das tarefas do agente.
4. **Desativação Local (Opt-out):** Permite desligar o comportamento por projeto inserindo um arquivo vazio `.no-autoformat` na raiz do projeto.

## Alternativas Consideradas

- **Pre-commit Hooks Padrão:** Rejeitado como solução única porque os ganchos do pre-commit só são executados no momento do commit, permitindo que a IA continue trabalhando com arquivos desformatados durante a sessão ativa, gerando desvios de estilo no histórico de modificação.

## Consequências

- **Positivas:**
  - Padronização de código automática e silenciosa em tempo real durante a execução da tarefa da IA.
  - Commits limpos e focados puramente na lógica funcional.
  - Flexibilidade para desabilitar por repositório.
- **Negativas:**
  - Dependência do ambiente local do host possuir os formatadores instalados e mapeados de forma correta (como symlink estável para o prettier global por conta do nvm).
