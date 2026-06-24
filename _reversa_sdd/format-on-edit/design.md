# Format-on-Edit (Formatting) — Design Técnico

> Regenerado pelo Writer em 2026-06-24 (Re-extração pós-feature 008-reprodutibilidade-e-config)
> Foca no COMO a unit é construída, a partir do código legado lido. Escala: 🟢 / 🟡 / 🔴

## Interface

| Símbolo                                  | Assinatura                            | Retorno                  | Observação                                                                            |
| ---------------------------------------- | ------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------- |
| `FormattingService.__init__`             | `(fs: FileSystemPort, process: ProcessPort, config: Optional[HarnessConfig] = None)` | `None`                   | Recebe `fs`, `process` e `config` (fallback para `HarnessConfig()` se omitido).       |
| `FormattingService.format_file`          | `(file_path: str)`                    | `int`                    | **Sempre `0`**. `try/except Exception` em todo o corpo.                               |
| `HostFormatterAdapter.execute_formatter` | `(formatter, file_path, executable?)` | `(exit, stdout, stderr)` | `ruff format`, `prettier --write`, `rustfmt <file>`. `FileNotFoundError`→`(127,...)`. |

## Fluxo Principal

1. **Blindagem de diretórios pessoais (RN-04):** se `abs_path == ~`, ou começa por `~/Notas` ou `~/.claude`, retorna 0 sem formatar. 🟢
2. **Descoberta da raiz + opt-out (RN-06/RN-N7):** sobe a árvore a partir do arquivo; em cada nível, se existir o arquivo indicador configurado em `config.formatting.opt_out_file` (default `.no-autoformat`), aborta (retorna 0); marca como raiz o nível que contiver `.git` **ou** `harness.toml`. Fallback `os.getcwd()`. 🟢
3. **Exclusão dinâmica (RN-N22/N23):** calcula o caminho relativo à raiz e valida contra as regras de `config.formatting.exclude_paths`. Padrões com curingas são validados via `fnmatch` contra o caminho relativo ou nome base do arquivo; se bater com algum, aborta (retorna 0). 🟢
4. **Seleção por extensão:** `.py`→`ruff`; `.js/.ts/.json/.css/.md`→`prettier`; `.rs`→`rustfmt`; não suportada → retorna 0. 🟢
5. **Precedência de executável local (RN-05):** para `ruff` procura `<root>/.venv/bin/ruff` e `venv/bin/ruff`; para `prettier`, `<root>/node_modules/.bin/prettier`. Se achar, passa o caminho; senão deixa o adaptador resolver no PATH. 🟢
6. **Execução** via `ProcessPort.execute_formatter(...)`, **ignorando o código de retorno** (não-bloqueio). 🟢

## Fluxos Alternativos

- **Qualquer exceção no corpo:** capturada pelo `try/except`; retorna 0 (RN-03). 🟢
- **Formatador ausente no host:** `HostFormatterAdapter` devolve `(127, ...)`; o serviço ignora. 🟢
- **Extensão não suportada:** no-op (retorna 0). 🟢

## Dependências

- `ProcessPort` / `HostFormatterAdapter` — execução do formatador em subprocesso.
- `FileSystemPort` — verificação de existência (`.no-autoformat`, manifestos, binários locais).
- Formatadores de host: `ruff`, `prettier`, `rustfmt`.

## Decisões de Design Identificadas

| Decisão                                                                     | Evidência no código                            | Confiança |
| --------------------------------------------------------------------------- | ---------------------------------------------- | --------- |
| Retorno incondicional `0` (não-bloqueio)                                    | `service.py` (`try/except` + `return 0`)       | 🟢        |
| Raiz por manifesto (`.git`/`harness.toml`), não por marcadores de linguagem | `service.py` (subida da árvore)                | 🟢        |
| Precedência local > PATH para binários                                      | `service.py` (caminhos `.venv`/`node_modules`) | 🟢        |
| Consumo dinâmico de configurações de formatação                             | `service.py` (`self.config` carregado)         | 🟢        |

## Estado Interno

Sem estado em memória. O efeito é o arquivo formatado no disco (via subprocesso). Não há log persistente (diferente do legado, que escrevia `format-on-edit.log`).

## Observabilidade

- O serviço **não** emite `systemMessage` nem grava log (comportamento do legado removido).
- O não-bloqueio é silencioso por design; falhas degradam para no-op.

## Riscos e Lacunas

- 🟢 **T3 (resolvido):** o caminho do hook (`PostToolUse` via stdin) fazia `json.loads` sem `import json` → `NameError` capturado, e o autoformat por hook não ocorria; corrigido no commit `cf73980` (`import json` em `main.py:5`). O autoformat por hook voltou a operar.
- 🟢 **T4 (resolvido):** o `[formatting]` do `harness.toml` agora alimenta o serviço de formatação (`FormattingService`), permitindo exclusão dinâmica de diretórios por glob pattern e definição de opt-out dinâmico.
- 🟢 **T6 (resolvido):** o build e a instalação agora são reprodutíveis com dependências trancadas pelo `requirements.txt` gerado com `uv` e testado continuamente via GitHub Actions.
