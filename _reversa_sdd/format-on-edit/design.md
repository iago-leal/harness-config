# Format-on-Edit, Design Técnico

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [format-on-edit.sh](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh)

## Interface

O script de formatação é disparado no pós-uso de ferramentas do Claude Code consumindo payload via STDIN.

| Símbolo | Assinatura | Retorno | Observação |
| :--- | :--- | :--- | :--- |
| `format-on-edit.sh` | `./hooks/format-on-edit.sh` | `JSON` no stdout (ou nada) | Retorna status exit `0` de forma irrestrita. |

---

## Fluxo Principal
1. **Configuração Unix & PATH:** Configura o ambiente e injeta `$HOME/.local/bin`, `/opt/homebrew/bin` e caminhos estáveis no `PATH` local.
2. **Extração de Arquivo:**
   * Lê STDIN e extrai `.tool_input.file_path` ou `.tool_response.filePath` usando `jq`.
   * Resolve o caminho absoluto correspondente.
3. **Verificação de Denylist (`DENY_PREFIXES`):**
   * Compara o caminho absoluto do arquivo com prefixos blindados (Notas Obsidian, diretórios de runtime do Claude). Aborta com exit `0` se houver match.
4. **Resolução de Raiz (`find_project_root`):**
   * Sobe recursivamente os níveis de diretórios.
   * Valida se a pasta corrente está contida no array `NON_ROOT_DIRS` (impedindo que `$HOME` seja raiz).
   * Se contiver um arquivo listado em `PROJECT_MARKERS`, assume o diretório como a raiz do projeto de software.
5. **Verificação de Opt-out:**
   * Aborta se o arquivo `.no-autoformat` estiver presente na raiz detectada.
6. **Despacho por Extensão:**
   * Calcula o hash SHA-1 do arquivo físico antes de alterar.
   * Resolve o formatador preferindo caminho relativo à raiz (ex: `node_modules/.bin/prettier`) antes de recorrer a busca global.
   * Case de Extensões:
     * `.py`, `.pyi`: Executa `ruff format` + `ruff check --fix --quiet`.
     * `.js`, `.ts`, `.json`, `.css`, `.html`, `.vue`, `.md`, `.yaml`, etc: Executa `prettier --write --log-level warn`.
     * `.rs`: Executa `rustfmt`.
     * `.sh`, `.bash` (ou arquivos sem extensão com shebang compatível): Executa `shfmt -w`.
7. **Cálculo Diferencial e Alerta:**
   * Compara o hash pós-execução. Se modificado, imprime no stdout o payload JSON `systemMessage`.

---

## Dependências
* `jq` — Utilitário de formatação e parse de payloads.
* Formatadores externos instalados local ou globalmente (`ruff`, `prettier`, `rustfmt`, `shfmt`).

---

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
| :--- | :--- | :---: |
| Retorno incondicional status `0` ao fim do fluxo | `format-on-edit.sh:173` | 🟢 |
| Dedução de script shell para arquivos sem extensão analisando shebang | `format-on-edit.sh:151` | 🟢 |

---

## Observabilidade
* O script escreve o log de todas as operações formatadas ou abortadas no arquivo local `~/.claude/hooks/format-on-edit.log`.
* As saídas de erros de compiladores são direcionadas a este arquivo de log de execução, preservando o stdout limpo apenas para o JSON de saída.
