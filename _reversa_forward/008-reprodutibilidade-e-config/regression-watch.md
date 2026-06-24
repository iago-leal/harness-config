# Monitoramento de Regressão (Regression Watch) — Feature 008

> Identificador: `008-reprodutibilidade-e-config`
> Data: `2026-06-24`

Este arquivo define os itens de verificação (watch items) que devem permanecer verdadeiros nas próximas re-extrações do Reversa para garantir que não haja regressão nas regras de negócio introduzidas nesta feature.

## 🛡️ 1. Tabela de Watch Items

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
| :--- | :--- | :--- | :--- | :--- |
| `W001` | `src/core/formatting/service.py` (blindagem) | O formatador deve impedir formatação em caminhos de segurança chumbados (`~`, `~/Notas`, `~/.claude`) de forma incondicional. | `presença` | Formatação permitida e executada em arquivos dentro de pastas de segurança. |
| `W002` | `src/core/formatting/service.py` (opt-out) | O arquivo de opt-out deve respeitar o nome configurado em `config.formatting.opt_out_file` com fallback para `.no-autoformat`. | `redação` | O formatador busca apenas pelo nome padrão `.no-autoformat`, ignorando o customizado configurado. |
| `W003` | `src/core/formatting/service.py` (exclusão) | A exclusão de caminhos deve validar padrões com curingas (`*`, `?`, `[`, `]`) usando glob matching (`fnmatch`) sobre o caminho relativo à raiz. | `presença` | Falha ao ignorar arquivos mapeados por glob patterns no campo `exclude_paths`. |

---

## 📈 2. Histórico de re-extrações

### Re-extração 2026-06-24 14:45 (pós-feature 008)

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | regra de blindagem preservada em _reversa_sdd/domain.md#RN-04 |
| W002 | 🟢 verde | regra de opt-out dinâmico preservada em _reversa_sdd/domain.md#RN-N24 |
| W003 | 🟢 verde | regra de glob matching preservada em _reversa_sdd/domain.md#RN-N23 |

---

## 🗄️ 3. Arquivadas

*(Itens de watch arquivados ou obsoletos após mudanças estruturais de longo prazo)*
