# ADR 0002: Formatação Automática Pós-Edição de Código

* **Status:** Aceito
* **Data:** 2026-06-21
* **Contexto Técnico:** Módulo `hooks` (`format-on-edit.sh`)
* **Escala de Confiança:** 🟢 CONFIRMADO

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

* **Pre-commit Hooks Padrão:** Rejeitado como solução única porque os ganchos do pre-commit só são executados no momento do commit, permitindo que a IA continue trabalhando com arquivos desformatados durante a sessão ativa, gerando desvios de estilo no histórico de modificação.

## Consequências

* **Positivas:**
  * Padronização de código automática e silenciosa em tempo real durante a execução da tarefa da IA.
  * Commits limpos e focados puramente na lógica funcional.
  * Flexibilidade para desabilitar por repositório.
* **Negativas:**
  * Dependência do ambiente local do host possuir os formatadores instalados e mapeados de forma correta (como symlink estável para o prettier global por conta do nvm).
