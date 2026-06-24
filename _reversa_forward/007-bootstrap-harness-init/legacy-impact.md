# Impacto de Regras e Legado (Legacy Impact) — Feature 007

> Identificador: `007-bootstrap-harness-init`
> Data: `2026-06-24`

Este documento mapeia o impacto das alterações da feature `007-bootstrap-harness-init` nos componentes arquiteturais e nas regras de negócio documentadas na extração reversa ativa.

## 📋 1. Tabela de Arquivos Afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
| :--- | :--- | :--- | :--- | :--- |
| `harness-core/src/core/domain/config.py` | `domain` | `regra-nova` | `LOW` | Adiciona campos `upstream_path` e `version` para suportar bootstrap e evolução. |
| `harness-core/src/core/bootstrap/init_service.py` | `bootstrap` | `componente-novo` | `MEDIUM` | Novo serviço de domínio para gerenciar inicialização e evolução do Harness no repositório de destino. |
| `harness-core/src/core/ports/fs.py` | `ports` | `delta-de-contrato-externo` | `LOW` | Adiciona o método abstrato `is_dir` à porta `FileSystemPort`. |
| `harness-core/src/core/ports/process.py` | `ports` | `delta-de-contrato-externo` | `LOW` | Adiciona o método abstrato `run_command` à porta `ProcessPort`. |
| `harness-core/src/adapters/fs/local.py` | `adapters` | `regra-nova` | `LOW` | Implementação concreta do método `is_dir` no adaptador de sistema de arquivos local. |
| `harness-core/src/adapters/process/formatter.py` | `adapters` | `regra-nova` | `LOW` | Implementação concreta do método `run_command` no adaptador de processos. |
| `harness-core/src/core/sync/service.py` | `sync` | `regra-nova` | `LOW` | Adiciona suporte para detecção passiva e comparação rápida de versões (local vs upstream). |
| `harness-core/src/main.py` | `CLI` | `delta-de-contrato-externo` | `MEDIUM` | Expõe os subcomandos `init` e `upgrade` no argparse e injeta aviso de atualização no boot se o upstream estiver à frente. |
| `harness-core/tests/test_init.py` | `testes` | `componente-novo` | `LOW` | Testes automatizados cobrindo os caminhos de sucesso e erro do bootstrap e upgrade. |
| `CLAUDE.md` / `GEMINI.md` | `documentacao` | `regra-nova` | `LOW` | Documenta os comandos `./harness init` e `./harness upgrade` para uso dos agentes. |

## 🏗️ 2. Diff Conceitual por Componente

### Componente `bootstrap`
- **Antes**: Responsável apenas por `install_hooks` (RN-N15).
- **Depois**: Estendido para suportar a inicialização completa do Harness em um diretório de destino (cópia recursiva, configuração padrão do `harness.toml`, criação da `.venv`, instalação dos ganchos Git). Também implementa a evolução do core (`upgrade`) de forma estritamente não destrutiva, preservando pastas de dados (`.reversa/`, `.harness/decisoes/`).

### Componente `domain` (Configuração)
- **Antes**: Configuração restrita a `harness`, `formatting`, `sync`, `decisions` e `session` (RN-N16).
- **Depois**: Configuração estendida para registrar o caminho do `upstream_path` e a `version` corrente do Harness instalado.

### Componente `sync`
- **Antes**: Verificação de sincronia restrita a comparar o hash local com o repositório remoto via rede (RN-01, RN-02).
- **Depois**: Adicionado suporte para verificação passiva e rápida de versões locais em relação ao upstream local (sem chamadas de rede externas ou subprocessos caros no boot do MCP/CLI).

### Componente `CLI` (Drivers de Entrada)
- **Antes**: Expunha comandos para formatação, decisões, ganchos e documentação.
- **Depois**: Expõe os comandos `./harness init <caminho>` e `./harness upgrade`, injetando avisos no fluxo do boot quando a versão estiver desatualizada.

---

## 🟢 3. Regras Preservadas

Todas as regras fundamentais extraídas do legado continuam intactas. Destacam-se:
- **RN-01 e RN-02 (Sincronização e Resiliência)**: O fluxo original de sincronia via Git não foi alterado.
- **RN-03 a RN-06 (Integridade na Formatação)**: A blindagem de diretórios críticos e a precedência de executáveis locais continuam inalteradas.
- **RN-N1 a RN-N4 (Estado de Sessão)**: O formato físico, o invariante de round-trip do serializer e a falha barulhenta em arquivos malformados de estado de sessão continuam garantidos.
- **RN-N17 (Footprint Global Zero)**: A garantia de footprint global zero do `harness-core` foi totalmente preservada. A inicialização e a evolução respeitam estritamente a localidade per-projeto, operando exclusivamente nos limites dos diretórios fornecidos.

---

## 🔴 4. Regras Modificadas / Novas Regras

Esta feature introduz novas regras de negócio, sem modificar as anteriores de forma destrutiva:
- **RN-N18 (Configuração de Upstream e Versão)**: O `harness.toml` agora armazena a versão instalada do core e o caminho físico para o repositório upstream original.
- **RN-N19 (Inicialização de Repositório Alvo)**: A rotina `./harness init` realiza cópia idempotente excluindo arquivos temporários e dependências locais de desenvolvimento (`.venv`, `.pytest_cache`, `.git`, etc.), cria o ambiente virtual local e instala ganchos locais Git de forma fail-fast caso falte dependências no host.
- **RN-N20 (Evolução Não-Destrutiva)**: O comando `./harness upgrade` atualiza o wrapper e os arquivos do core, mas preserva a pasta de dados `.harness/decisoes/` e os arquivos de estado de sessão / histórico de engenharia reversa.
- **RN-N21 (Checagem Passiva de Atualização)**: O boot da CLI e do servidor MCP faz leitura imediata e de baixo custo comparando a versão instalada contra a versão no upstream, exibindo alertas se houver defasagem, sem bloquear a operação do agente.
