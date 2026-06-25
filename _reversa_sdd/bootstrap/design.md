# Bootstrap e Evolução — Design Técnico

> Regenerado pelo Writer em 2026-06-24 (Re-extração pós-feature 007)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA

Este documento descreve as interfaces, fluxogramas de controle, dependências e decisões de design implementadas para inicialização e evolução do framework nos ambientes locais de destino.

## Interface

| Classe / Símbolo | Assinatura | Retorno | Observação |
|:---|:---|:---|:---|
| `BootstrapService.install_hooks` | `(repo_path: str)` | `List[str]` | Instala os ganchos git pre-commit e post-merge. |
| `InitService.init_target` | `(fs: FileSystemPort, process: ProcessPort, target_path: str, active_harness: str, upstream_path: str, version: str)` | `None` | Copia fisicamente o core/wrapper, cria a `.venv` local e instala ganchos Git. |
| `InitService.upgrade_target` | `(fs: FileSystemPort, process: ProcessPort, target_path: str, upstream_path: str, version: str)` | `None` | Atualiza core e wrapper no destino de forma não destrutiva. |

## Fluxo Principal de Inicialização (`init_target`)

1. Cria o diretório `target_path` recursivamente (via `FileSystemPort.makedirs`) caso não exista. 🟢
2. Executa a replicação física do `.harness/harness-core/` e do wrapper `harness` da raiz do upstream para o destino. 🟢
3. Descarta arquivos e diretórios pertencentes a caches locais ou ganchos de versionamento do upstream (`.git/`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `tmp/`). 🟢
4. Grava o arquivo de configuração de destino `harness.toml` incluindo as chaves `upstream_path` (caminho absoluto do upstream) e `version` (versão do core instalado) na seção `[harness]`. 🟢
5. Provisiona o ambiente virtual local disparando `python3 -m venv .venv` via `ProcessPort.run_command` na pasta `harness-core` do destino. 🟢
6. Se o provisionamento falhar por ausência de interpretador python ou venv no host do desenvolvedor, interrompe com erro fail-fast explicitando a ação humana corretiva. 🟢
7. Instala os ganchos locais Git de forma automática e idempotente chamando `BootstrapService.install_hooks`. 🟢

## Fluxo Principal de Atualização (`upgrade_target`)

1. Atualiza o wrapper executável `harness` na raiz do destino. 🟢
2. Replicação recursiva não destrutiva do `.harness/harness-core/` a partir do `upstream_path` configurado. 🟢
3. Garante a preservação absoluta das pastas locais de dados de engenharia reversa (`.reversa/`) e decisões arquiteturais locais (`.harness/decisoes/`). Os arquivos e subpastas dessas duas estruturas são ignorados na substituição recursiva. 🟢
4. Atualiza o `harness.toml` com o novo identificador de versão do upstream. 🟢

## Dependências

- **`FileSystemPort`**: criação de diretórios, cópia recursiva de arquivos físicos e persistência do `harness.toml` e ganchos Git.
- **`ProcessPort`**: execução do interpretador Python do host para provisionar o ambiente virtual `.venv` no destino.
- **`BootstrapService`**: reaproveitado no fluxo de inicialização para setup automático de ganchos Git locais.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|:---|:---|:---|
| Cópia física de arquivos sem recorrer a symlinks | `init_service.py` (cópia recursiva via fs) | 🟢 CONFIRMADO |
| Preservação seletiva de `.reversa/` e `.harness/decisoes/` no upgrade | `init_service.py` (blacklist de pastas no upgrade) | 🟢 CONFIRMADO |
| Setup da venv no host de destino via subprocesso direto | `init_service.py` (chamada a run_command) | 🟢 CONFIRMADO |
| Detecção fail-fast e tratamento verboso sob falha de python/venv no host | `init_service.py` (try/except CalledProcessError com dicas de instalação) | 🟢 CONFIRMADO |

## Observabilidade

- Erros na criação da `.venv` são interceptados e geram mensagens amigáveis instruindo o mantenedor a instalar pacotes faltantes (ex. `python3-venv` ou `python3-pip`).
- Mensagens discretas e passivas de versão desatualizada são renderizadas no boot do CLI e do servidor MCP sem acoplamento a requisições de rede lentas (RN-N21).
