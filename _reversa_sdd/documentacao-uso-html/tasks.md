# Documentação de Uso Autogerada em HTML, Tarefas de Implementação

> Foca em uma sequência de tarefas executáveis para reimplementar a unit a partir do legado.

## Pré-requisitos
- [ ] Módulo `main.py` de CLI estruturado com `argparse`.
- [ ] Pasta virtual `.harness/harness-core/.venv` configurada e dependências instaladas.
- [ ] Metadados do Reversa disponíveis (`state.json` e `domain.md`).

## Tarefas

- [ ] T-01, Criar o esqueleto do serviço de documentação `DocumentationService`
  - Origem no legado: `.harness/harness-core/src/core/documentation/service.py:1`
  - Critério de pronto: O serviço é instanciado recebendo a interface `FileSystemPort`.
  - Confiança: 🟢
- [ ] T-02, Criar o template HTML com design visual responsivo e JavaScript interativo
  - Origem no legado: `.harness/harness-core/src/core/documentation/template.html:1`
  - Critério de pronto: O arquivo HTML possui o estilo CSS dark mode inline e comportamento JavaScript para abas de comandos e regras.
  - Confiança: 🟢
- [ ] T-03, Implementar introspecção recursiva do `argparse.ArgumentParser`
  - Origem no legado: `.harness/harness-core/src/core/documentation/service.py:11`
  - Critério de pronto: Retorna lista com os comandos CLI e seus argumentos a partir da introspecção dinâmica do parser.
  - Confiança: 🟢
- [ ] T-04, Implementar extração de regras de negócio a partir do `domain.md`
  - Origem no legado: `.harness/harness-core/src/core/documentation/service.py:37`
  - Critério de pronto: Extrai as strings de regras (`RN-*`), títulos, detalhes e confidência via expressões regulares.
  - Confiança: 🟡
- [ ] T-05, Implementar a geração atômica do arquivo HTML final
  - Origem no legado: `.harness/harness-core/src/core/documentation/service.py:67`
  - Critério de pronto: Substitui o placeholder de dados em `template.html` com o JSON unificado e escreve o arquivo `harness-docs.html` na raiz do projeto de forma atômica.
  - Confiança: 🟢
- [ ] T-06, Integrar os novos comandos `doc-gen` e `doc-serve` na CLI `main.py`
  - Origem no legado: `.harness/harness-core/src/main.py:175`
  - Critério de pronto: A CLI expõe os comandos `doc-gen` e `doc-serve` para o terminal.
  - Confiança: 🟢
- [ ] T-07, Implementar o servidor HTTP local simples com `http.server`
  - Origem no legado: `.harness/harness-core/src/main.py:200`
  - Critério de pronto: Inicia com sucesso o servidor HTTP local e expõe o HTML gerado na porta padrão 8000.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Teste unitário para introspecção de CLI e comandos do parser (`test_documentation.py:test_extract_commands`)
- [ ] TT-02, Teste unitário do parser de Markdown de regras (`test_documentation.py:test_parse_markdown_rules`)
- [ ] TT-03, Teste unitário do compilador e build atômico (`test_documentation.py:test_generate_html`)
- [ ] TT-04, Teste de integração do parser global da CLI do core (`test_documentation.py:test_parser_integration`)

## Tarefas de Migração de Dados (se aplicável)
n/a (sem persistência de banco de dados).

## Ordem Sugerida
1. T-01 e T-02 (esqueleto e template visual) de forma paralela.
2. T-03, T-04, T-05 (serviço e compilador core).
3. T-06 e T-07 (integração e servidor local).
4. Suíte de testes (TT-01 a TT-04) pode ser implementada em paralelo com as lógicas ou logo após a finalização da Fase 3.

## Lacunas Pendentes (🔴)
Nenhuma lacuna pendente de aprovação humana.
