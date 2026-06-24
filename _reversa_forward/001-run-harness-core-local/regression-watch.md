# Regression Watch: Execução Local do Harness Core

> Identificador: `001-run-harness-core-local`
> Data: `2026-06-23`

## 1. Watch Items de Regressão

Estes itens devem ser monitorados nas próximas rodadas da extração reversa para garantir que a evolução técnica permaneça intacta e não sofra regressões silenciosas:

| ID   | Origem (arquivo, seção)                            | Regra esperada após mudança                                                                  | Tipo de verificação | Sinal de violação                                                      |
| :--- | :------------------------------------------------- | :------------------------------------------------------------------------------------------- | :------------------ | :--------------------------------------------------------------------- |
| W001 | `legacy-impact.md#mapeamento-de-impacto-no-legado` | O arquivo wrapper `./harness` existe na raiz do repositório e possui flag de execução ativa. | presença            | O script `./harness` está ausente ou não executável (`chmod -x`).      |
| W002 | `legacy-impact.md#interface-executavel-nucleo`     | O ambiente virtual Python do núcleo está configurado e com dependências instaladas.          | presença            | A pasta `harness-core/.venv` está ausente ou falta o módulo `toml`.    |
| W003 | `legacy-impact.md#ganchos-do-ciclo-de-vida`        | O snippet de ganchos recomendados está disponível para consulta do agente de IA local.       | presença            | O arquivo `.reversa/settings.json.snippet` está ausente ou corrompido. |

## 2. Histórico de re-extrações

### Re-extração 2026-06-24 08:10

| ID   | Veredito | Observação                                                                                                                |
| ---- | -------- | ------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | Arquivo wrapper `./harness` existe na raiz com permissão de execução (-rwxr-xr-x). Verificado contra sistema de arquivos. |
| W002 | 🟢 verde | Diretório `harness-core/.venv` presente e operacional. Módulo `toml` instalado no ambiente virtual conforme histórico.    |
| W003 | 🟢 verde | Arquivo `.reversa/settings.json.snippet` presente com conteúdo JSON válido (hooks configurados).                          |

### Re-extração 2026-06-23 21:58

| ID   | Veredito | Observação                                                 |
| ---- | -------- | ---------------------------------------------------------- |
| W001 | 🟢 verde | `./harness` existe na raiz e é executável (`-x`).          |
| W002 | 🟢 verde | `harness-core/.venv` presente; `toml` importável (0.10.2). |
| W003 | 🟢 verde | `.reversa/settings.json.snippet` presente e não-vazio.     |

> **Nota de arquivamento:** com esta rodada, W001/W002/W003 acumulam **3 vereditos verdes consecutivos** (13:38 · 16:15 · 21:58), atingindo o limiar `setup.json#watch.archive-after = 3`. São candidatos a mover para `## 3. Arquivadas`. O Reversa não altera a tabela principal automaticamente (regra absoluta); a ação fica a critério do mantenedor.

### Re-extração 2026-06-23 13:38

| ID   | Veredito | Observação                                                                          |
| ---- | -------- | ----------------------------------------------------------------------------------- |
| W001 | 🟢 verde | O arquivo wrapper `./harness` existe na raiz e possui permissão de execução ativa.  |
| W002 | 🟢 verde | O ambiente virtual `harness-core/.venv` está presente com dependências completas.   |
| W003 | 🟢 verde | O snippet `.reversa/settings.json.snippet` está presente na pasta de configurações. |

### Re-extração 2026-06-23 16:15

| ID   | Veredito | Observação                                                                                           |
| ---- | -------- | ---------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | O arquivo wrapper `./harness` existe na raiz do projeto e possui permissão de execução.              |
| W002 | 🟢 verde | O ambiente virtual `harness-core/.venv` está presente e operacional.                                 |
| W003 | 🟢 verde | O snippet `.reversa/settings.json.snippet` foi verificado sob \_reversa_sdd/run-harness-core-local/. |

## 3. Arquivadas

_Nenhuma regra arquivada nesta rodada._

## 4. Observações

_Não há watch items baseados em regras com confidência rebaixada (amarela ou vermelha) para esta rodada._
