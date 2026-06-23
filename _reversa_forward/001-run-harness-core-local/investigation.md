# Investigation: Execução Local do Harness Core

> Identificador: `001-run-harness-core-local`
> Data: `2026-06-23`

## 1. Pesquisa de Fundo e Contexto

No legado (`harness-config`), as automações de ganchos Git e do ciclo de vida da IDE eram gerenciadas por scripts em Bash (`bin/*`, `hooks/*`) localizados em diretórios globais no `$HOME` do usuário. Isso introduzia problemas de portabilidade e dependência do interpretador Bash com versões incompatíveis, além de complexidade de manutenção.

Com a reescrita do núcleo do sistema em Python (`harness-core`), as mesmas lógicas de validação de microdecisões, comandos e formatação de código foram portadas para uma estrutura estruturada orientada a objetos. Contudo, para rodar na raiz do projeto local de forma simples, precisamos contornar dois desafios técnicos:
1. **Isolamento de dependências:** O núcleo usa pacotes adicionais (como `toml`). Precisamos garantir que ele execute usando a venv dedicada localizada em `harness-core/.venv` sem exigir instalação de pacotes no ambiente global Python do host.
2. **Facilidade sintática e portabilidade:** A IDE/agente e o desenvolvedor humano precisam chamar os comandos do núcleo usando caminhos relativos ao projeto, compatíveis com qualquer máquina (macOS/Linux).

## 2. Alternativas Avaliadas

### Alternativa 1: Invocar Python diretamente com caminho relativo
```bash
python3 harness-core/src/main.py <comando>
```
* **Prós:** Simples, não requer novos arquivos na raiz.
* **Contras:** Falha se o interpretador Python padrão do host não possuir a biblioteca `toml` instalada (o que é o padrão de distribuições limpas). Não isola o ambiente de desenvolvimento.

### Alternativa 2: Exigir instalação global ou ferramentas de empacotamento (Poetry/Pipenv)
* **Prós:** Gerencia dependências de forma rígida.
* **Contras:** Adiciona dependência de software externo (Poetry ou Pipenv) no host local. Se o host não tiver a ferramenta instalada, o pipeline quebra. Adiciona complexidade desnecessária para scripts de automação.

### Alternativa 3: Script Wrapper POSIX na Raiz (`./harness`) (Escolhida)
```bash
#!/bin/bash
# Localiza e executa com a venv
```
* **Prós:**
  - Encapsula o caminho do interpretador Python correto (`harness-core/.venv/bin/python3`) de forma transparente.
  - Portátil entre macOS e Linux (POSIX compliant).
  - Permite adicionar validações amigáveis antes de iniciar a execução (ex: verificar se a venv existe e orientar o usuário sobre o setup).
  - Sintaxe de uso idêntica à de um executável tradicional (`./harness decisions`).
* **Contras:** Adiciona um arquivo a mais na raiz do repositório.

## 3. Padrões Aplicáveis

* **POSIX Compliance:** O wrapper deve utilizar sintaxe padrão Bash/Sh compatível com macOS e Linux, tratando o repasse de argumentos via `"$@"`.
* **Fail-fast:** O wrapper deve abortar rapidamente com código `1` caso o interpretador Python na venv não exista, exibindo mensagens de diagnóstico no canal de erro padrão (`stderr`).
