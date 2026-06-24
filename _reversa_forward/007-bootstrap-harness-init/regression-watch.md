# Monitoramento de Regressão (Regression Watch) — Feature 007

> Identificador: `007-bootstrap-harness-init`
> Data: `2026-06-24`

Este arquivo define os itens de verificação (watch items) que devem permanecer verdadeiros nas próximas re-extrações do Reversa para garantir que não haja regressão nas regras introduzidas.

## 🛡️ 1. Tabela de Watch Items

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
| :--- | :--- | :--- | :--- | :--- |
| `W001` | `init_service.py` (upgrade) | O comando `upgrade` não deve sobrescrever ou remover a pasta `.reversa/` e a pasta `.harness/decisoes/` no destino. | `presença` | Remoção de arquivos ou pastas de decisão pré-existentes no repositório de destino após o upgrade. |
| `W002` | `init_service.py` (init) | O comando `init` deve inicializar o Harness copiando fisicamente os arquivos necessários e ignorando pastas de desenvolvimento (`.git`, `.venv`, `.pytest_cache`, `.ruff_cache`). | `presença` | Presença de diretórios do repositório original (ex. `.git`, `.venv` de desenvolvimento) copiados para o destino. |
| `W003` | `sync/service.py` (check) | A checagem de versão no boot deve ser passiva, não concorrente e resiliente a falhas se o upstream for ilegível ou inexistente. | `presença` | Travamento no boot da CLI/MCP caso o upstream_path esteja inacessível ou corrompido. |

---

## 📈 2. Histórico de re-extrações

### Re-extração 2026-06-24 11:15

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | regra preservada em _reversa_sdd/domain.md#RN-N20 |
| W002 | 🟢 verde | regra preservada em _reversa_sdd/domain.md#RN-N19 |
| W003 | 🟢 verde | regra preservada em _reversa_sdd/domain.md#RN-N21 |

### Re-extração 2026-06-24 14:45 (pós-feature 008)

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | regra de upgrade preservada em _reversa_sdd/domain.md#RN-N20 |
| W002 | 🟢 verde | regra de init preservada em _reversa_sdd/domain.md#RN-N19 |
| W003 | 🟢 verde | regra de checagem de versão passiva preservada em _reversa_sdd/domain.md#RN-N21 |


---

## 🗄️ 3. Arquivadas

*(Itens de watch arquivados ou obsoletos após mudanças estruturais de longo prazo)*
