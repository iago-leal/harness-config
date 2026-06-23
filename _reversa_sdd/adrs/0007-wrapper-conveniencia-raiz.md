# MD-0007 — Script Wrapper de Conveniência na Raiz

> Data: 2026-06-23
> Estado: **aceito**

## D: Decisão
Introduzir o script Bash wrapper `harness` na raiz do projeto local (/Users/iagoleal/dev/harness) que valida localmente a existência do ambiente virtual dedicado (`harness-core/.venv/bin/python3`) e encaminha todas as chamadas de parâmetros para o ponto de entrada principal do núcleo (`harness-core/src/main.py`).

## PORQUÊ: Justificativa
* **Isolamento de dependências:** Evita poluir o ambiente Python global do host com bibliotecas específicas do Harness (como `toml`).
* **Erros Amigáveis (Fail-fast):** Se a venv estiver ausente ou corrompida, o wrapper exibe instruções claras de setup em vez de estourar erros crípticos do interpretador do host.
* **Simplicidade de Invocação:** O usuário humano e os hooks de ciclo de vida da IDE podem chamar simplesmente `./harness <comando>` em vez de caminhos longos de venv.

## DESCARTADO: Alternativas consideradas
* **Aliases de Terminal:** Definir `alias harness='harness-core/.venv/bin/python3 harness-core/src/main.py'`. Descartado porque aliases não são herdados em sub-shells não interativos iniciados por ganchos Git ou pela IDE.
