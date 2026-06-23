# Microdecisões, Design Técnico

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [decisoes/](file:///Users/iagoleal/dev/harness/harness-config/decisoes/) e [gerar-index-decisoes.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/gerar-index-decisoes.sh)

## Interface

O compilador de índices opera via CLI e aceita flags de validação passiva.

| Símbolo | Assinatura | Retorno | Observação |
| :--- | :--- | :--- | :--- |
| `gerar-index-decisoes.sh` | `./bin/gerar-index-decisoes.sh [--check]` | `void` (exit status) | Retorna status `0` se ok; `1` se houver erros de parse ou defasagem (em modo check). |

---

## Fluxo Principal
1. **Varredura Física:** Localiza e lista todos os arquivos Markdown no formato `decisoes/MD-*.md` ordenando de forma sequencial pelo ID.
2. **Leitura e Extração de Metadados:**
   * Faz o parse das linhas de metadados extraindo chaves de gatilho (`gancho`) e relacionamentos declarados (`relacoes`).
   * Valida se a declaração de cada relação de design possui exatamente 2 tokens (ex: `refina MD-0002`). Se violar, aborta o processamento emitindo erro em stderr.
3. **Mapeamento de Backlinks (Inversão de Grafo):**
   * Armazena as arestas originais direcionadas.
   * Executa a rotação lógica do grafo:
     * `depende-de` $\rightarrow$ `dependência-de`
     * `substitui` $\rightarrow$ `substituído-por`
     * `refina` $\rightarrow$ `refinado-por`
     * `relaciona` $\rightarrow$ `relacionado-com`
4. **Construção do Markdown Consolidado (`microdecisoes.md`):**
   * Escreve o cabeçalho base extraído de `decisoes/_cabecalho.md`.
   * Monta a tabela de índices navegáveis listando ID, Título, Gancho e Status.
   * Adiciona para cada decisão a árvore hierárquica formatada de dependências diretas e backlinks inversos computados (usando o recuo visual `↳`).
5. **Gravação ou Validação Passiva:**
   * **Modo Padrão:** Grava o conteúdo gerado sob o arquivo físico `microdecisoes.md`.
   * **Modo Check (`--check`):** Compara o conteúdo em buffer temporário contra o arquivo `microdecisoes.md` existente em disco. Retorna status `1` se houver alguma diferença conceitual de conteúdo.

---

## Dependências
* Interpretadores GNU Coreutils (`sed`, `awk`, `grep`) para parsing de arquivos texto e blocos Markdown.

---

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
| :--- | :--- | :---: |
| Uso da flag `--check` para desacoplar a validação da escrita do índice | `gerar-index-decisoes.sh:40` | 🟢 |
| Inversão de grafo de backlinks utilizando hashing associativo em shell scripts (awk) | `gerar-index-decisoes.sh:65` | 🟡 |

---

## Observabilidade
* Se houver erros de formato de metadados, o script emite a linha defeituosa e o arquivo de origem em `stderr` para ação imediata do desenvolvedor.
