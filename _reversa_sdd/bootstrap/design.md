# Bootstrap, Design Técnico

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [bootstrap.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/bootstrap.sh)

## Interface

O módulo é disparado diretamente via linha de comando (CLI) sem passagem de parâmetros adicionais obrigatórios.

| Símbolo | Assinatura | Retorno | Observação |
| :--- | :--- | :--- | :--- |
| `bootstrap.sh` | `./bin/bootstrap.sh` | `void` (exit status) | Retorna status `0` se concluído com sucesso; `1` se houver erros impeditivos de configuração. |

---

## Fluxo Principal
1. **Configuração de Ambiente Unix:** Inicializa configurações de shell com diretivas portáveis (`set -uo pipefail`).
2. **Resolução de Caminhos Relativos:** Detecta a raiz física do repositório utilizando comandos Git locais (`git rev-parse --show-toplevel`).
3. **Verificação de Pré-requisitos:** Executa o script complementar `.reversa/scripts/sh/verify-prerequisites.sh` (ou `.ps1` no Windows) para certificar a presença de binários essenciais (`jq`, `git`, etc.).
4. **Instalação física de Hooks:**
   * Copia ou cria symlinks dos scripts de ganchos locais para a pasta `.git/hooks/` do repositório.
   * Aplica permissão de execução (`chmod +x`) aos arquivos de ganchos configurados.
5. **Configuração da Ponte Gemini:** Instala ganchos específicos para sincronização do repositório de memória compartilhada em background (`~/.agent-memory/`).

---

## Fluxos Alternativos
* **Falha de Dependência Crítica:** Se `verify-prerequisites.sh` retornar status de falha (código diferente de 0), o bootstrap exibe mensagens de erro em stderr e encerra sua execução de forma precoce com status `1`.
* **Sem repositório Git:** Se executado fora de um repositório git válido, aborta no passo de detecção de raiz e encerra exibindo erro estruturado.

---

## Dependências
* `.reversa/scripts/sh/verify-prerequisites.sh` — Script complementar de validação do ambiente do host.
* `.reversa/scripts/sh/prepare-roadmap.sh` — Utilizado para sincronia funcional.

---

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
| :--- | :--- | :---: |
| Execução condicional de shebangs baseados em ambiente Unix | `bootstrap.sh:1` | 🟢 |
| Instalação de hook post-merge para manter IAs sincronizadas após pulls | `bootstrap.sh:72` | 🟢 |

---

## Observabilidade
* O script escreve mensagens de progresso legíveis em `stdout` (ex: `"Aplicando ponte de memória..."`, `"Instalando ganchos..."`).
* Falhas e erros de dependência são direcionados exclusivamente para `stderr`.

---

## Riscos e Lacunas
* 🟡 **Suposição de PATH:** O bootstrap assume que interpretador `bash` está presente em localizações Unix padrão (`/usr/bin/env bash`), o que pode falhar em ambientes minimalistas de containers Docker Alpine.
