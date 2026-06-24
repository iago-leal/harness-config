# Format-on-Edit (Formatting) — Requisitos (Requirements)

> Regenerado pelo Writer em 2026-06-24 (Re-extração)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`harness-core/src/core/formatting/service.py`](file:///Users/iagoleal/dev/harness/harness-core/src/core/formatting/service.py); adaptador `adapters/process/formatter.py`. Driver: `src/main.py` (subcomando `format`, hook `PostToolUse`).

> ⚠️ **Reescrita vs versão anterior:** a implementação **deixou de ser** o script `harness-config/hooks/format-on-edit.sh` (purgado, commit `5624f78`) e passou a ser o `FormattingService` Python em `harness-core`. O serviço atual **não** trata `shfmt`, nem grava `~/.claude/hooks/format-on-edit.log`, nem emite `systemMessage` — diferenças do legado.

## Visão Geral

Formata um arquivo após edição do agente, por linguagem, sempre de modo **não-bloqueante** (retorna sempre 0). Blinda diretórios pessoais, respeita opt-out por projeto, descobre a raiz por manifesto e prioriza executáveis locais.

## Responsabilidades

- Selecionar e disparar o formatador adequado por extensão (`ruff`/`prettier`/`rustfmt`). 🟢
- Blindar diretórios pessoais (`~`, `~/Notas`, `~/.claude`). 🟢
- Respeitar o opt-out `.no-autoformat` na pasta do arquivo ou em qualquer diretório superior. 🟢
- Descobrir a raiz do projeto por manifesto (`.git`/`harness.toml`) e priorizar binários locais. 🟢
- Nunca abortar a operação de escrita do agente (sempre retorna 0). 🟢

## Regras de Negócio

- **RN-03 — Não-bloqueio absoluto:** `format_file` **sempre** retorna `0`, com `try/except Exception` envolvendo todo o corpo. 🟢
- **RN-04 — Proteção de diretórios críticos:** aborta sem alterar se o caminho absoluto for `~`, começar por `~/Notas` ou por `~/.claude`. Blindagens chumbadas. 🟢
- **RN-05 — Precedência de executáveis locais:** prioriza `<root>/.venv/bin/ruff`, `venv/bin/ruff`, `<root>/node_modules/.bin/prettier` antes do PATH. 🟢
- **RN-06 — Opt-out do projeto:** presença de `.no-autoformat` na pasta do arquivo ou em diretório superior cancela a formatação. Nome chumbado. 🟢
- **RN-N7 — Descoberta da raiz por manifesto:** raiz = primeiro diretório (subindo a árvore) com `.git` **ou** `harness.toml`; fallback `os.getcwd()`. Seleção por extensão: `.py`→ruff; `.js/.ts/.json/.css/.md`→prettier; `.rs`→rustfmt; demais → no-op. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Formatação por extensão. | Must | `.py`→ruff, `.js/.ts/.json/.css/.md`→prettier, `.rs`→rustfmt; extensão não suportada → no-op. |
| RF-02 | Não-bloqueio absoluto. | Must | `format_file` retorna `0` mesmo sob exceção ou falha do formatador. |
| RF-03 | Blindagem de diretórios pessoais. | Must | Arquivo em `~`, `~/Notas` ou `~/.claude` não é formatado. |
| RF-04 | Opt-out por `.no-autoformat`. | Must | Presença do arquivo na pasta ou acima cancela a formatação. |
| RF-05 | Precedência de binário local. | Should | Se houver binário local do formatador, ele é usado antes do PATH. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Robustez | Falha do formatador nunca trava a escrita do agente. | `core/formatting/service.py` (`try/except` + `return 0`) | 🟢 |
| Segurança de dados | Diretórios pessoais protegidos por blindagem. | `core/formatting/service.py` | 🟢 |
| Portabilidade | Resolução de executáveis com fallback ao PATH. | `core/formatting/service.py`, `adapters/process/formatter.py` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que um arquivo .py foi gravado num projeto com harness.toml
Quando o hook PostToolUse aciona `./harness format`
Então o serviço dispara ruff sobre o arquivo (via ProcessPort) e retorna 0.

Dado que um arquivo foi alterado em ~/Notas
Quando format_file é chamado
Então o serviço aborta sem formatar e retorna 0.

Dado que existe .no-autoformat na raiz do projeto
Quando format_file é chamado para um arquivo desse projeto
Então a formatação é cancelada e o serviço retorna 0.
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Não-bloqueio absoluto (RN-03) | Must | Salvaguarda crítica; impede pane de escrita. |
| Blindagem de diretórios (RN-04) | Must | Protege dados pessoais. |
| Opt-out por projeto (RN-06) | Must | Consentimento explícito do projeto. |
| Precedência local de binários (RN-05) | Should | Mantém o estilo do projeto; degrada ao PATH. |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `core/formatting/service.py` | `FormattingService.format_file` | 🟢 |
| `adapters/process/formatter.py` | `HostFormatterAdapter.execute_formatter` | 🟢 |
| `src/main.py` | Subcomando `format` (🟡 T3: `json` sem import no caminho stdin) | 🟡 |

> 🟡 **Conhecida (T4):** `[formatting]` do `harness.toml` (`exclude_paths`, `opt_out_file`) **não** alimenta o serviço — blindagens e opt-out estão chumbados no código. Mudar o `harness.toml` não muda o comportamento. Documentado como contexto, não corrigido.
> 🟡 **Conhecida (T3):** `main.py:63` usa `json.loads` sem `import json`; no caminho do hook (`PostToolUse`, caminho via stdin) isso levanta `NameError` capturado pelo `except`, e o autoformat por hook não ocorre. Documentado, não corrigido.
