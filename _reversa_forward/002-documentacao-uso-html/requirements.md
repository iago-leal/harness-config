# Requirements: Documentação de Uso Autogerada em HTML

> Identificador: `002-documentacao-uso-html`
> Data: `2026-06-23`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Esta feature entrega um gerador de documentação em HTML autossuficiente para o `harness`, permitindo aos desenvolvedores e novos agentes de IA compreenderem rapidamente como instalar, configurar e operar a CLI local e seus ganchos de automação. Ela resolve a ausência de uma central explicativa legível para humanos e máquinas sobre o ambiente local do `harness`, garantindo atualização automática sempre que a interface da CLI ou as microdecisões mudarem.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/inventory.md#📂 Estrutura de Diretórios e Arquivos` | Mapeamento do script executável `harness` na raiz e da pasta `harness-core` contendo os comandos e adaptadores. | 🟢 |
| `_reversa_sdd/domain.md#📖 1. Glossário de Domínio` | Conceitos de Wrapper Executável, opt-out de formatação e integridade da sessão do agente. | 🟢 |
| `_reversa_sdd/architecture.md#🗺️ 1. Estilo de Arquitetura` | Detalhes de injeção de dependências e portas de entrada (CLI Python `main.py` e MCP Server). | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objective | Cenário-chave |
|---------|----------|---------------|
| Desenvolvedor do Projeto | Aprender a usar a CLI e seus comandos utilitários locais. | Consulta a documentação no navegador após clonar o repositório para entender como iniciar o ambiente. |
| Agente de IA (Antigravity/Claude Code) | Descobrir as regras de negócio ativas e comandos disponíveis sem varrer todo o repositório. | Lê o HTML de documentação gerado localmente para obter comandos e regras estruturadas de uso do wrapper. |
| Integrador de CI/CD / Automatizador | Garantir que a documentação distribuída esteja sempre sincronizada com o código. | O pipeline ou hook local executa a regeneração automática do HTML a cada modificação na CLI ou nas regras de negócio. |

## 4. Regras de negócio novas ou alteradas

1. **RN-08: Sincronização Automática da Documentação (Build)** 🟢
   - Origem no legado: n/a
   - Tipo: nova
   - Descrição: O arquivo HTML gerado deve ser atualizado de forma síncrona ou assíncrona na raiz do projeto (`harness-docs.html`) toda vez que a interface CLI, comandos, ou microdecisões forem alterados, ou através de comandos explícitos de regeneração.
2. **RN-09: Autossuficiência e Portabilidade do HTML** 🟢
   - Origem no legado: n/a
   - Tipo: nova
   - Descrição: A documentação gerada deve consistir em um único arquivo HTML contendo todos os estilos (CSS inline ou internal) e scripts necessários, sem dependências de rede externas obrigatórias (como CDNs de fontes ou bibliotecas de visualização bloqueantes) que impeçam a leitura offline.
3. **RN-10: Introspecção Dinâmica dos Comandos** 🟡
   - Origem no legado: `_reversa_sdd/architecture.md#🗺️ 1. Estilo de Arquitetura`
   - Tipo: nova
   - Descrição: O conteúdo de ajuda dos comandos CLI do `harness-core` deve ser extraído diretamente das definições do interpretador Python (metadados da CLI), garantindo consistência sem necessidade de reescrever descrições no HTML manualmente.

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Comando CLI para geração de HTML | Must | Executar `./harness doc-gen` na raiz gera o arquivo HTML `harness-docs.html` na raiz do projeto. | 🟢 |
| RF-02 | Exposição offline de comandos CLI | Must | O HTML gerado deve listar todos os comandos disponíveis no `harness-core`, seus parâmetros de entrada, e as descrições dos mesmos obtidas via introspecção do módulo CLI. | 🟢 |
| RF-03 | Listagem dinâmica de regras de negócio legadas | Should | O gerador deve ler os arquivos sob `_reversa_sdd/` (ex: `domain.md` e `architecture.md`) e compilar uma seção no HTML resumindo os comportamentos e RNs legadas vigentes. | 🟡 |
| RF-04 | Atualização por Hook Git / Reversa | Should | Integrar a geração da documentação a um gancho pós-commit local ou após ganchos forward do Reversa, reescrevendo o HTML de modo transparente sempre que arquivos sob `harness-core/src/core` ou `_reversa_sdd` sofrerem alteração. | 🟡 |
| RF-05 | Visualização de Microdecisões | Should | Listar e vincular as microdecisões catalogadas (em `claude-config/decisoes/` ou `_reversa_sdd/adrs/`) no HTML, permitindo leitura direta no navegador. | 🟢 |
| RF-06 | Comando CLI para servir o HTML localmente | Must | Executar `./harness doc-serve` inicia um servidor HTTP local simples exposto por padrão em `http://localhost:8000` servindo o arquivo `harness-docs.html`. | 🟢 |
| RF-07 | Dashboard com Checkpoints do Reversa | Should | Integrar o progresso dos checkpoints do Reversa (a partir de `.reversa/state.json`) com gráficos interativos (Highcharts/D3 se aplicável) no próprio HTML gerado. | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Tempo de geração do HTML inferior a 2 segundos | A compilação local de comandos e leitura de arquivos MD deve ser imediata para não impactar hooks locais. | 🟢 |
| Usabilidade | Layout responsivo e legível em dispositivos desktop e mobile | Facilita a consulta em diferentes dispositivos e contextos de tela sem necessidade de zoom. | 🟢 |
| Segurança | Ausência de JavaScript externo não auditado | Para atender a ambientes locais restritos, o HTML não deve importar scripts CDN externos. O CSS e JS de busca interna devem ser locais. | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Geração manual bem-sucedida do HTML de documentação
  Dado que o desenvolvedor possui a CLI harness em execução local
  Quando ele executa o comando `./harness doc-gen` no terminal
  Então um arquivo HTML autossuficiente chamado `harness-docs.html` deve ser gerado na raiz do projeto
  E o arquivo deve conter a lista atualizada de todos os comandos do harness-core

Cenário: Execução offline da documentação gerada
  Dado que o arquivo HTML foi gerado com sucesso
  Quando o desenvolvedor abre o arquivo `harness-docs.html` no navegador sem conexão de rede
  Então todos os estilos visuais, seções de navegação, comandos e microdecisões devem ser renderizados e visualizados corretamente, sem erros de recursos ausentes

Cenário: Atualização automática de comandos na documentação
  Dado que um novo comando foi inserido na CLI do harness-core em Python
  Quando a geração de documentação é executada por um hook local ou manualmente
  Então o comando novo com seus parâmetros de ajuda deve constar automaticamente no HTML gerado

Cenário: Servidor de documentação integrado
  Dado que o arquivo HTML foi gerado com sucesso
  Quando o desenvolvedor executa o comando `./harness doc-serve`
  Então a CLI deve iniciar um servidor HTTP local simples
  E o link `http://localhost:8000` deve abrir o HTML de documentação no navegador
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | Mecanismo básico de geração manual do HTML. |
| RF-02 | Must | Apresentação fiel das funcionalidades e parâmetros da CLI de uso. |
| RF-06 | Must | Servidor HTTP local integrado para facilidade de visualização. |
| RF-03 | Should | Adiciona valor ao centralizar as regras de negócio legadas. |
| RF-04 | Should | Facilita a consistência da documentação à medida que a aplicação evolui. |
| RF-05 | Should | Permite consultar o histórico de microdecisões de design arquitetural diretamente. |
| RF-07 | Should | Facilita visualização do status e checkpoints da engenharia reversa executados. |
| RNF Usabilidade | Should | Garante legibilidade em diferentes janelas de navegador. |

## 9. Esclarecimentos

### Sessão 2026-06-23

- **Q:** Qual deve ser o nome padrão do arquivo HTML gerado e o seu diretório final no projeto?
  **R:** `harness-docs.html` na raiz do projeto.
- **Q:** O gerador de HTML deve ler também os arquivos do Reversa para incluir um dashboard de checkpoints do projeto?
  **R:** Sim, a documentação deve incluir o progresso e checkpoints do Reversa (com Highcharts/D3 se aplicável).
- **Q:** Devemos prever um comando na própria CLI do `harness` para servir a documentação gerada localmente?
  **R:** Sim, adicionar o comando `./harness doc-serve` (inicia um servidor HTTP local simples).

## 10. Lacunas

Nenhuma lacuna pendente.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-06-23 | Integração das respostas da sessão de esclarecimento pelo `/reversa-clarify` | reversa |
