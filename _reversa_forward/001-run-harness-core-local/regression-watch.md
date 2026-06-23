# Regression Watch: Execução Local do Harness Core

> Identificador: `001-run-harness-core-local`
> Data: `2026-06-23`

## 1. Watch Items de Regressão

Estes itens devem ser monitorados nas próximas rodadas da extração reversa para garantir que a evolução técnica permaneça intacta e não sofra regressões silenciosas:

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
| :--- | :--- | :--- | :--- | :--- |
| W001 | `legacy-impact.md#mapeamento-de-impacto-no-legado` | O arquivo wrapper `./harness` existe na raiz do repositório e possui flag de execução ativa. | presença | O script `./harness` está ausente ou não executável (`chmod -x`). |
| W002 | `legacy-impact.md#interface-executavel-nucleo` | O ambiente virtual Python do núcleo está configurado e com dependências instaladas. | presença | A pasta `harness-core/.venv` está ausente ou falta o módulo `toml`. |
| W003 | `legacy-impact.md#ganchos-do-ciclo-de-vida` | O snippet de ganchos recomendados está disponível para consulta do agente de IA local. | presença | O arquivo `.reversa/settings.json.snippet` está ausente ou corrompido. |

## 2. Histórico de re-extrações

### Re-extração 2026-06-23 13:38

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | O arquivo wrapper `./harness` existe na raiz e possui permissão de execução ativa. |
| W002 | 🟢 verde | O ambiente virtual `harness-core/.venv` está presente com dependências completas. |
| W003 | 🟢 verde | O snippet `.reversa/settings.json.snippet` está presente na pasta de configurações. |

### Re-extração 2026-06-23 16:15

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | O arquivo wrapper `./harness` existe na raiz do projeto e possui permissão de execução. |
| W002 | 🟢 verde | O ambiente virtual `harness-core/.venv` está presente e operacional. |
| W003 | 🟢 verde | O snippet `.reversa/settings.json.snippet` foi verificado sob _reversa_sdd/run-harness-core-local/. |

## 3. Arquivadas

*Nenhuma regra arquivada nesta rodada.*

## 4. Observações

*Não há watch items baseados em regras com confidência rebaixada (amarela ou vermelha) para esta rodada.*
