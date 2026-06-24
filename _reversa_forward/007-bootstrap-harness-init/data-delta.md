# Data Delta: Configuração e Metadados do Bootstrapper e Upstream

> Identificador: `007-bootstrap-harness-init`
> Data: `2026-06-24`

Este documento especifica o impacto no modelo de dados local da aplicação (representada por arquivos de configuração e estado) provocado pela introdução do subcomando de inicialização e evolução do core.

## 1. Modificações em Modelos de Configuração

### 1.1 Configuração Tipada `HarnessConfig` (`src/core/domain/config.py`)
A classe de configuração Pydantic `HarnessConfig` ganhará ou refinará atributos na seção `[harness]`.

*   **Novos Campos na classe Pydantic `HarnessSection`:**
    *   `upstream_path: Optional[str] = None`: Caminho absoluto de origem da instalação do core. Usado para rastrear onde baixar atualizações no host.
    *   `version: str`: Versão local atual do core (e.g. `"1.2.43"`). Mapeada a partir de metadados internos.

### 1.2 Impacto no arquivo `harness.toml`
O arquivo `harness.toml` do projeto de destino passará a aceitar e gravar estes campos na inicialização.

**Exemplo do `harness.toml` gerado pelo `init` no destino:**
```toml
[harness]
active_harness = "claude"
upstream_path = "/Users/iagoleal/dev/harness"
version = "1.2.43"

[session]
state_file = ".harness/estado-da-sessao.md"

[decisions]
dir = ".harness/decisoes"
index_file = ".harness/microdecisoes.md"
header_file = ".harness/decisoes/_cabecalho.md"
```

---

## 2. Inicialização dos Arquivos de Dados do Destino

A inicialização do destino deve criar os seguintes arquivos na pasta `.harness/` se os mesmos não existirem. Eles iniciam vazios ou com cabeçalhos padrão.

### 2.1 Índice de Decisões (`.harness/microdecisoes.md`)
O arquivo inicial do índice será gravado com o cabeçalho padrão de autogeração para que o interpretador de decisões local funcione corretamente.
```markdown
# Índice de Microdecisões

> Gerado automaticamente. Não edite este arquivo diretamente.
```

### 2.2 Cabeçalho de Decisões (`.harness/decisoes/_cabecalho.md`)
O arquivo inicial do cabeçalho de decisões é gerado para estruturar a compilação do grafo:
```markdown
# Microdecisões do Projeto
```

### 2.3 Estado de Sessão Padrão (`.harness/estado-da-sessao.md`)
Gravado em formato nulo/inicial, sem features ativas:
```markdown
---
commit: null
feature: null
start_time: null
status: null
---
# Estado de Sessão
```

---

## 3. Plano de Migração de Dados

Não há necessidade de migrar projetos legados ativos. No entanto, se o usuário rodar `./harness init <caminho>` apontando para um repositório que já usa o harness, o script:
1. Detecta o arquivo `harness.toml` preexistente.
2. Atualiza de forma idempotente a seção `[harness]` inserindo o `upstream_path` apontando para o core de origem da chamada e a `version` atual.
3. Não modifica as seções `[session]`, `[decisions]` ou dados em `.harness/decisoes/` que já existam.
