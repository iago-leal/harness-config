# Documentação de Uso Autogerada em HTML

> Foca no QUE a unit de documentação faz, não no como.

## Visão Geral
Esta unit é responsável por coletar metadados dos comandos da CLI, regras de domínio e progresso dos checkpoints do Reversa, compilando tudo em um HTML único autossuficiente e permitindo expor localmente a documentação por um servidor HTTP integrado.

## Responsabilidades
- Compilar programaticamente as rotas e argumentos dos comandos do `harness-core` a partir do `argparse.ArgumentParser`.
- Extrair as regras de negócio em formato Markdown de `domain.md` e checkpoints de `state.json`.
- Injetar os metadados consolidados em um template HTML (`template.html`) e gravar atomicamente o arquivo final (`harness-docs.html` na raiz).
- Iniciar um servidor HTTP local simples para expor a documentação gerada em rede local.

## Regras de Negócio
- **RN-08: Sincronização Automática da Documentação (Build)** 🟢
  - A build da documentação cria/atualiza `harness-docs.html` na raiz do projeto com as definições mais recentes de comandos e checkpoints.
- **RN-09: Autossuficiência e Portabilidade do HTML** 🟢
  - O HTML gerado deve carregar estilos e comportamentos sem dependências de rede externas (offline).
- **RN-10: Introspecção Dinâmica dos Comandos** 🟢
  - O gerador extrai metadados do parser da CLI principal em tempo de execução para garantir consistência.

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Comando de geração de documentação | Must | Executar `./harness doc-gen` gera com sucesso o HTML. |
| RF-02 | Comando de servidor de documentação | Must | Executar `./harness doc-serve` abre servidor HTTP local na porta de rede. |
| RF-03 | Introspecção do parser do CLI | Must | O gerador mapeia os comandos da CLI em tempo de execução do parser de argparse. |
| RF-04 | Parsing de regras de negócio em Markdown | Should | Extrai regras ativas de `domain.md` e `architecture.md`. |
| RF-05 | Timeline de progresso do Reversa | Should | Carrega a timeline e o percentual de checkpoints concluídos. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | Tempo de compilação da documentação imediato (<1s) | `harness-core/src/core/documentation/service.py` | 🟢 |
| Segurança | Execução offline sem chamadas externas a CDNs | `harness-core/src/core/documentation/template.html` | 🟢 |
| Portabilidade | Servidor local HTTP nativo em Python (`http.server`) | `harness-core/src/main.py` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que o desenvolvedor executa o comando "./harness doc-gen"
Quando o processo termina com sucesso
Então o arquivo "harness-docs.html" deve ser gerado na raiz do projeto

Dado que o arquivo "harness-docs.html" existe na raiz
Quando o desenvolvedor roda o comando "./harness doc-serve" na porta 8000
Então o servidor local inicia em "http://localhost:8000" servindo a documentação offline
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Compilação e build da documentação HTML | Must | Funcionalidade crítica para expor o manual de uso do framework. |
| Introspecção programática da CLI | Must | Garante consistência livre de erros manuais. |
| Servidor HTTP nativo em Python | Must | Facilita a exposição visual do manual localmente. |
| Parsing e rendering de regras do legado | Should | Adiciona contexto semântico importante, mas com fallback textual. |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `harness-core/src/core/documentation/service.py` | `DocumentationService` | 🟢 |
| `harness-core/src/main.py` | `build_parser`, `main` | 🟢 |
| `harness-core/src/core/documentation/template.html` | n/a (HTML visual) | 🟢 |
| `harness-core/tests/test_documentation.py` | n/a (Suíte de testes) | 🟢 |
