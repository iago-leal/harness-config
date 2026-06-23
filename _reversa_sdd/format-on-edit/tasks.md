# Format-on-Edit, Tarefas de Implementação

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [format-on-edit.sh](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh)

## Pré-requisitos
* [ ] Permissões de escrita no caminho de logs `~/.claude/hooks/`.
* [ ] Binários dos formatadores instalados (local ou global).

---

## Tarefas

- [ ] **T-01: Parse de Evento e Validação de Caminho**
  * Origem no legado: `hooks/format-on-edit.sh:75-87`
  * Critério de pronto: Extrair com sucesso o caminho absoluto do arquivo a partir de `.tool_input.file_path` ou `.tool_response.filePath` usando `jq`.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-02: Filtro de Denylist e NON_ROOT_DIRS**
  * Origem no legado: `hooks/format-on-edit.sh:88-94` e `hooks/format-on-edit.sh:69-73`
  * Critério de pronto: Abortar imediatamente sem alterar arquivos se pertencer à denylist ou se bater em restrições de diretórios não-raiz.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-03: Algoritmo de Busca Recursiva de Raiz de Projeto**
  * Origem no legado: `hooks/format-on-edit.sh:96-112`
  * Critério de pronto: Subir recursivamente diretórios e retornar a raiz se encontrar um arquivo contido em `PROJECT_MARKERS`, ou abortar se não encontrar.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-04: Lógica de Resolução e Despacho de Formatadores**
  * Origem no legado: `hooks/format-on-edit.sh:114-162`
  * Critério de pronto: Resolver executáveis na prioridade local > global, rodar o formatador associado de forma silenciosa direcionando logs para `format-on-edit.log`.
  * Confiança: 🟢 CONFIRMADO
- [ ] **T-05: Validação Diferencial de Hashes (shasum)**
  * Origem no legado: `hooks/format-on-edit.sh:164-173`
  * Critério de pronto: Comparar hashes pré e pós-formatação, emitindo a notificação JSON em stdout apenas em caso de divergência.
  * Confiança: 🟢 CONFIRMADO

---

## Tarefas de Teste

- [ ] **TT-01: Teste de Formatação de Código Prettier**
  * Critério de pronto: Modificar propositalmente o espaçamento de um arquivo JSON do projeto e verificar se o hook o padroniza e gera o JSON de notificação.
- [ ] **TT-02: Teste de Resiliência contra Erros do Formatador**
  * Critério de pronto: Introduzir um erro de sintaxe física num arquivo temporário do projeto que quebre o formatador, e certificar que o script encerra retornando status `0` sem bloquear a escrita.
