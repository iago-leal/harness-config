# ADR 0015: Reprodutibilidade e Configurações Dinâmicas de Formatação

- **Status:** Aceito
- **Data:** feature 008 — commit pendente (sobre base `1b23498`)
- **Contexto Técnico:** Módulo `core/formatting/service.py` (`FormattingService`), CLI `main.py`, MCP `server.py`, `core/domain/config.py` (seção `[formatting]`), `harness-core/requirements.in`, `harness-core/requirements.txt`, `.github/workflows/ci.yml`, `tests/test_formatting.py`
- **Escala de Confiança:** 🟢 CONFIRMADO
- **Decisões relacionadas:** MD-0002, ADR 0012, ADR 0013; watch items da feature 008

## Contexto e Problema

O `harness-core` possuía anteriormente duas grandes limitações técnicas que geravam débito técnico e risco de quebra silenciosa:
1. **Configurações Chumbadas:** O serviço de formatação automática (`FormattingService`) não lia as chaves da seção `[formatting]` do arquivo `harness.toml`. Isso tornava as regras de exclusão de caminhos e o arquivo indicador de opt-out (anteriormente fixo em `.no-autoformat`) chumbados diretamente no código-fonte do serviço.
2. **Dependências Não Determinísticas:** O repositório não possuía um arquivo de travamento (lock file) de dependências Python. Ele usava pins do tipo `>=` direto no setup/requirements, o que tornava as construções e instalações físicas de novos targets (ADR 0014) não determinísticas. Duas instalações em momentos distintos poderiam baixar versões diferentes de bibliotecas externas (como Pydantic, FastMCP e Pytest), introduzindo instabilidade.

## Decisão

Implementar consumo ativo de configurações no serviço de formatação e travamento de dependências com `uv`:

1. **Injeção de Configuração no FormattingService:** Refatorar o construtor do `FormattingService` para aceitar um parâmetro opcional `HarnessConfig`. O serviço agora lê dinamicamente as chaves `formatting.opt_out_file` e `formatting.exclude_paths` do manifesto local.
2. **Exclusão Dinâmica com Suporte a Glob Patterns:** Implementar no `FormattingService` o suporte a casamento de padrões glob (wildcards como `*`, `?`, `[`, `]`) usando a biblioteca nativa `fnmatch`. Padrões sem wildcards continuam funcionando como prefixos de diretório ou correspondência exata.
3. **Locking Determinístico com `uv`:** Adotar o gerenciador de pacotes rápido `uv`. Criar um arquivo de entrada de dependências abstratas `requirements.in` e compilá-lo deterministicamente para um `requirements.txt` travado via `uv pip compile`. Todas as instalações e testes usam o arquivo travado.
4. **CI/CD de Matriz de Ambientes:** Adicionar um workflow do GitHub Actions em `.github/workflows/ci.yml` para rodar a suíte de testes do Harness sob Python 3.12 e Python 3.13, garantindo estabilidade multiplataforma em todas as alterações futures.

## Alternativas Consideradas

- **Usar Poetry ou Pipenv:** Rejeitado. Embora robustos, Poetry e Pipenv adicionam dependência de ferramentas pesadas no host e possuem tempo de inicialização e compilação mais lentos. O `uv` é extremamente rápido, escrito em Rust, e se integra de forma transparente com o ecossistema simples de `requirements.txt` do Python.
- **Implementar casamento de padrões com Regex manual:** Rejeitado. O uso de `fnmatch` nativo do Python resolve de forma limpa e segura a sintaxe padrão de glob utilizada em manifestos como `.gitignore` e ferramentas de linting, evitando complexidade desnecessária e potenciais brechas de segurança por expressões regulares malformadas.

## Consequências

- **Positivas:**
  - Reprodutibilidade absoluta das instalações físicas locais em novos projetos.
  - Customização total do comportamento de formatação de arquivos (exclusões dinâmicas de diretórios específicos do projeto legado e alteração do arquivo de opt-out).
  - Prevenção ativa de regressões em diferentes versões do Python (3.12 e 3.13) via CI.
- **Negativas:**
  - Adiciona o `uv` como requisito recomendado de desenvolvimento para compilar o arquivo de dependências (embora o `requirements.txt` compilado possa ser instalado com o `pip` padrão).
