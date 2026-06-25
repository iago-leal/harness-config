# Documentação de Uso Autogerada em HTML, Design Técnico

> Foca no COMO a unit de documentação é construída, com base no código lido.

## Interface

Para a CLI e comandos (expresso pelo wrapper `harness` e `main.py`):

| Comando | Parâmetro | Entrada | Saída | Observação |
|---------|-----------|---------|-------|------------|
| `./harness doc-gen` | n/a | n/a | Escreve `harness-docs.html` na raiz | Compila metadados em JSON e injeta no template. |
| `./harness doc-serve` | `--port` | Porta (Integer, default: 8000) | Abre socket local | Inicia servidor HTTP nativo. |

Para classes/funções:

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `DocumentationService.extract_commands` | `(parser: argparse.ArgumentParser)` | `List[Dict[str, Any]]` | Extrai comandos, ajuda, flags e valores padrões de subparsers. |
| `DocumentationService.parse_markdown_rules` | `(domain_filepath: str)` | `List[Dict[str, Any]]` | Extrai regras de negócio via regex de `domain.md`. |
| `DocumentationService.load_checkpoints` | `(state_filepath: str)` | `Dict[str, Any]` | Carrega JSON de checkpoints e progresso do Reversa. |
| `DocumentationService.generate_html` | `(parser, template_path: str, domain_path: str, state_path: str, output_path: str)` | `None` | Combina dados lidos no template HTML e escreve atomicamente. |

## Fluxo Principal (Geração do HTML)
1. **Instanciação**: A CLI em `main.py` cria o parser do argparse e chama `build_parser()` para obter a árvore do parser.
2. **Início do doc-gen**: `main.py` instancia `DocumentationService` repassando o adaptador local do sistema de arquivos (`LocalFileSystemAdapter`).
3. **Coleta de metadados**:
   - `extract_commands()` faz a introspecção recursiva das propriedades `_actions` do parser de subparsers.
   - `parse_markdown_rules()` abre o `domain.md` e lê strings correspondentes ao padrão `**RN-XX: ...** 🟢|🟡|🔴` via regex.
   - `load_checkpoints()` serializa o `.reversa/state.json` para dict Python.
4. **Interpolação**: O arquivo `template.html` é lido do disco em string, e o bloco de script de dados `/* INJECTED_DATA_PLACEHOLDER */` é substituído por `const HARNESS_DOC_DATA = <JSON>;`.
5. **Persistência**: Grava de forma segura `harness-docs.html` na raiz do projeto local.

## Fluxos Alternativos
- **Ausência de arquivos do Reversa**: Se `state.json` ou `domain.md` estiverem ausentes durante a compilação, o `DocumentationService` retorna listas/dicionários vazios sem quebrar a execução, permitindo que a CLI termine e gere documentação apenas de comandos.
- **Iniciação de doc-serve sem HTML pré-gerado**: Se o desenvolvedor chamar `doc-serve` e o arquivo `harness-docs.html` não existir na raiz, o `main.py` intercepta a chamada, executa o fluxo completo do `doc-gen` primeiro e depois inicia o servidor local.

## Dependências
- `LocalFileSystemAdapter` (`src/adapters/fs/local.py`), usado para leitura de templates/markdowns e gravação do HTML.
- `argparse` (biblioteca padrão Python), para introspecção programática da interface.
- `http.server` e `socketserver` (biblioteca padrão Python), para rodar o servidor HTTP local sem dependências de rede.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Injeção dinâmica de metadados em variável javascript global | `.harness/harness-core/src/core/documentation/service.py:100` | 🟢 |
| Layout CSS standalone (sem CDNs) | `.harness/harness-core/src/core/documentation/template.html:15` | 🟢 |
| Reuso de porta socket TCP habilitado (`allow_reuse_address`) | `.harness/harness-core/src/main.py:214` | 🟢 |

## Estado Interno
O `DocumentationService` em si é stateless. O estado final da documentação é persistido fisicamente no arquivo `harness-docs.html` na raiz do projeto local e exposto de forma síncrona.

## Observabilidade
- A CLI emite mensagens de sucesso no terminal ao gerar o HTML: `Sucesso: Documentação compilada e salva em 'harness-docs.html'.`
- O console do terminal do `doc-serve` registra logs de acessos HTTP à documentação, com timestamps e códigos de retorno TCP.

## Riscos e Lacunas
- 🟡 Caso o formato da declaração de regras de negócio em `domain.md` mude drasticamente (ex: abandono do padrão de marcadores em negrito `**RN-XX: ...**`), a regex de extração de regras pode não mapear itens, gerando seção de regras vazia no HTML.
