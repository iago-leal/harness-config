# Requirements: Reprodutibilidade e Configuração Viva de Formatação

> Identificador: `008-reprodutibilidade-e-config`
> Data: `2026-06-24`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Estabiliza e profissionaliza o ecossistema `harness-core` sob os pilares de saúde e manutenibilidade contínua. Para tal, implementa o gerenciamento determinístico de dependências e bloqueio de versões via `uv`, configura um pipeline de CI simples via GitHub Actions para testar cada alteração física de forma contínua, e remove a dívida técnica do serviço de formatação (`FormattingService`), fazendo com que ele passe a respeitar dinamicamente as exclusões e caminhos de opt-out configurados no arquivo `harness.toml` do projeto.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#5. Dívidas Técnicas e Bugs Latentes` | T4 (formatting/service.py ignores [formatting]) e T6 (sem lock file, pins >=) listados como abertos. | 🟢 CONFIRMADO |
| `_reversa_sdd/domain.md#2.2 Integridade e Salvaguarda na Formatação` | RN-04 (Proteção de Diretórios Críticos) e RN-06 (Opt-out do Projeto) descrevem comportamentos atualmente chumbados em código. | 🟢 CONFIRMADO |
| `_reversa_sdd/code-analysis.md#2. core/formatting` | Nota residual T4 e loop de subida da árvore confirmam blindagens chumbadas e divergência de configuração com `harness.toml`. | 🟢 CONFIRMADO |
| `_reversa_sdd/inventory.md#Raiz do Projeto` | `requirements.txt` especifica dependências de forma flexível sem travar as sub-dependências com arquivo de lock. | 🟢 CONFIRMADO |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor do Projeto | Garantir que o setup do projeto seja idêntico e reprodutível no tempo em qualquer máquina nova. | Um novo desenvolvedor clona o repositório e executa o bootstrap (`init`) sem risco de atualizações de dependências quebrarem a instalação. |
| Agente de IA / Editor | Formatar arquivos respeitando as preferências específicas do projeto. | O agente edita um arquivo em um diretório configurado em `exclude_paths` no TOML, e a formatação automática é prevenida dinamicamente sem necessidade de alterar o código do core. |
| Integrador Contínuo | Assegurar que nenhuma alteração de código quebre os testes unitários da aplicação. | Executar automaticamente toda a suíte pytest no GitHub Actions sob commit ou pull request. |

## 4. Regras de negócio novas ou alteradas

1. **RN-N22 (Lock de Dependências Determinístico):** O projeto passa a gerenciar suas dependências de desenvolvimento e runtime utilizando o arquivo `requirements.txt` compilado e travado deterministicamente por `uv pip compile` (gerando um lock implícito em `requirements.txt` ou utilizando a infraestrutura de Workspace do `uv` com `uv.lock`). 🟢
   - Origem no legado: `_reversa_sdd/architecture.md#5. Dívidas Técnicas e Bugs Latentes` (T6)
   - Tipo: nova
2. **RN-N23 (Configuração Viva de Formatação - Opt-out):** O nome do arquivo de recusa de formatação automática deixa de ser chumbado e deve ser lido dinamicamente da configuração `formatting.opt_out_file` do `harness.toml`. Se não estiver especificado ou o TOML estiver ausente, deve-se usar o padrão `.no-autoformat`. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.2 Integridade e Salvaguarda na Formatação` (RN-06)
   - Tipo: alterada
3. **RN-N24 (Configuração Viva de Formatação - Caminhos Excluídos):** O formatador deve abortar e retornar 0 sem alterar o arquivo se o seu caminho absoluto coincidir com algum padrão ou prefixo configurado em `formatting.exclude_paths` no `harness.toml`. As blindagens chumbadas (`~`, `~/Notas`, `~/.claude`) continuam valendo como regra de salvaguarda incondicional mínima sobrepostas a quaisquer exclusões configuradas pelo usuário. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.2 Integridade e Salvaguarda na Formatação` (RN-04)
   - Tipo: alterada

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Configurar o gerenciamento de dependências via `uv` no `harness-core` | Must | Existência de configuração funcional de dependências via `uv` e arquivos de dependência travados (com pins estritos ou arquivo de lock). | 🟢 |
| RF-02 | Criar pipeline de Integração Contínua (CI) básico no GitHub Actions | Must | Arquivo `.github/workflows/ci.yml` configurado que instale as dependências via `uv` e execute `pytest` com sucesso em cada commit. | 🟢 |
| RF-03 | Alimentar o `FormattingService` com a configuração `HarnessConfig` | Must | O construtor do `FormattingService` aceita e utiliza um parâmetro `config: Optional[HarnessConfig]`. Se omitido, usa as instâncias padrão (defaults). | 🟢 |
| RF-04 | Validar o arquivo de opt-out configurado dinamicamente | Must | A busca recursiva por opt-out na árvore de diretórios utiliza o valor de `config.formatting.opt_out_file` (ex: `.no-autoformat`). | 🟢 |
| RF-05 | Excluir arquivos contidos em caminhos configurados em `exclude_paths` | Must | Formatação aborta imediatamente se o arquivo coincidir com algum caminho configurado em `config.formatting.exclude_paths`. Suporta caminhos relativos à raiz do projeto ou caminhos absolutos. | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Segurança | Preservar a blindagem incondicional do diretório home do usuário e subdiretórios padrão (`~/Notas`, `~/.claude`) | Evita formatação acidental de arquivos fora do repositório mesmo que a configuração do TOML seja corrompida. | 🟢 |
| Desempenho | Execução rápida de testes na CI | O pipeline deve rodar em menos de 1 minuto usando o cache do `uv`. | 🟢 |
| Manutenibilidade | Sem quebra de compatibilidade nas assinaturas públicas de formatação da CLI/MCP | A CLI e o servidor MCP continuam funcionando exatamente com o mesmo comportamento original de entrada e saída. | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Inicialização de dependências reprodutível
  Dado que o projeto está configurado para uso do uv
  Quando executamos a suíte de testes com dependências travadas
  Então todos os testes passam sem conflito de versões

Cenário: Opt-out de formatação dinâmico por arquivo configurado
  Dado que o arquivo harness.toml configura opt_out_file como ".recusa-formatar"
  E existe um arquivo ".recusa-formatar" no diretório do alvo
  Quando solicitamos a formatação de um arquivo nesse diretório
  Então o formatador aborta com retorno 0 sem alterar o arquivo

Cenário: Exclusão de formatação por caminho configurado
  Dado que o arquivo harness.toml configura exclude_paths como ["excluidos/", "temp/arquivo.py"]
  E solicitamos a formatação de um arquivo dentro de "excluidos/"
  Quando o FormattingService analisa o caminho do arquivo
  Então o formatador aborta com retorno 0 sem alterar o arquivo
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | Essencial para garantir a longevidade e reprodutibilidade do projeto. |
| RF-02 | Must | Saúde do projeto contra regressões semânticas em futuras alterações. |
| RF-03 | Must | Base necessária para injetar e ler configurações dinâmicas no serviço. |
| RF-04 | Must | Corrige a lacuna T4 fazendo o opt-out configurado ter efeito físico. |
| RF-05 | Must | Corrige a lacuna T4 fornecendo exclusão dinâmica de caminhos de formatação. |

## 9. Esclarecimentos

### Sessão 2026-06-24
- **Q:** Qual o escopo de suporte do `exclude_paths`? Deve suportar apenas prefixos simples (ex: `excluidos/`) ou devemos usar correspondência por glob patterns (ex: `**/excluidos/*.py`)?
  **R:** Suportar glob patterns e prefixos simples (ex: `excluidos/` casa com tudo abaixo, `**/*.log` casa com qualquer .log).
- **Q:** A CI deve testar múltiplas versões do Python (ex: 3.10, 3.11, 3.12, 3.13) ou apenas a versão de desenvolvimento padrão do mantenedor?
  **R:** Apenas a versão padrão do projeto (Python 3.12/3.13) para manter a execução do pipeline extremamente rápida.

## 10. Lacunas

Nenhuma lacuna pendente.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-24 | Versão inicial gerada por `/reversa-requirements` | reversa |
