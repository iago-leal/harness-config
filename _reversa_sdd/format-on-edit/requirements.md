# Format-on-Edit, Requisitos (Requirements)

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [format-on-edit.sh](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh)

## Visão Geral
Intercepte e formate de forma automatizada e transparente os arquivos de código editados pelo agente de IA no final de cada operação de escrita/gravação de ferramentas, assegurando que o repositório permaneça padronizado de acordo com as regras de cada projeto, sem causar interrupções operacionais.

## Responsabilidades
* Identificar se o arquivo alterado pertence a um projeto de software válido. 🟢
* Selecionar e disparar o formatador adequado de acordo com a extensão do arquivo modificado (ruff, prettier, rustfmt, shfmt). 🟢
* Notificar o Claude Code caso o arquivo tenha sofrido alterações de conteúdo pós-formatação. 🟢

## Regras de Negócio
* **Não-Bloqueio Absoluto:** O script de formatação deve sempre encerrar com código de retorno `0`, garantindo que eventuais problemas de formatação ou linting nunca resultem em travamento ou cancelamento da escrita do agente. 🟢 [format-on-edit.sh:14](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh#L14)
* **Blindagem de Diretórios Pessoais:** Arquivos que residam sob diretórios listados em `DENY_PREFIXES` (ex: Notas Obsidian, diretórios de configuração do Claude) ou no próprio `$HOME` (sem subpastas) nunca devem ser formatados. 🟢 [format-on-edit.sh:38](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh#L38)
* **Precedência Local:** O script deve resolver os executáveis de formatação priorizando pastas internas do projeto (ex: `.venv/bin/ruff`, `node_modules/.bin/prettier`) antes de cair para instalações globais da máquina. 🟢 [format-on-edit.sh:119](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh#L119)
* **Cancelamento Local (Opt-out):** O comportamento de formatação automatizada é desabilitado instantaneamente para um projeto se houver o arquivo vazio `.no-autoformat` na raiz do mesmo. 🟢 [format-on-edit.sh:111](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh#L111)

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
| :--- | :--- | :---: | :--- |
| **RF-01** | Detecção automática de projeto. | Must | Validar se o arquivo alterado reside sob um diretório que contenha um manifesto de linguagem conhecido. |
| **RF-02** | Formatação por extensão de arquivo. | Must | Disparar prettier para JSON/JS/TS/Markdown, ruff para Python, rustfmt para Rust e shfmt para Shell scripts. |
| **RF-03** | Notificação de alteração. | Should | Emitir JSON `systemMessage` caso o shasum do arquivo seja modificado pós-formatação. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
| :--- | :--- | :--- | :---: |
| Estabilidade | Caminhos de executáveis resolvidos com PATH estável, evitando dependências de variáveis locais. | `format-on-edit.sh:34` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que um arquivo .py foi gravado em um subdiretório de projeto contendo pyproject.toml
Quando o hook de edição for acionado
Então o format-on-edit deve acionar ruff format e ruff check --fix.

Dado que um arquivo de texto foi alterado no diretório ~/Notas
Quando o hook de edição interceptar a gravação
Então ele deve abortar a execução de imediato sem alterar o arquivo e sem emitir erro em stdout.
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
| :--- | :---: | :--- |
| Não-bloqueio operacional | Must | Regra crítica de infraestrutura; evitar pane de escrita na IDE. |
| Blindagem de diretórios | Must | Evita perda acidental de dados pessoais e de documentação Obsidian. |
| Resolução local de binários | Should | Mantém compatibilidade com as versões de estilo adotadas no projeto do usuário. |
