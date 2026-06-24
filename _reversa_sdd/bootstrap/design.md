# Bootstrap (Ganchos Git Locais) — Design Técnico

> Regenerado pelo Writer em 2026-06-24 (Re-extração)
> Foca no COMO a unit é construída, a partir do código legado lido. Escala: 🟢 / 🟡 / 🔴

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `BootstrapService.install_hooks` | `(repo_path: str)` | `List[str]` | Lista de caminhos dos ganchos instalados. |
| `BootstrapService._pre_commit_script` | `()` (`@staticmethod`) | `str` | Corpo Bash do `pre-commit` (chama `format`). |
| `BootstrapService._post_merge_script` | `()` (`@staticmethod`) | `str` | Corpo Bash do `post-merge` (chama `decisions`). |

## Fluxo Principal

1. `install_hooks(repo_path)` cria `.git/hooks/` (via `FileSystemPort.makedirs`) se ausente. 🟢
2. Grava `pre-commit` com o corpo de `_pre_commit_script()`, que invoca `harness-core/.venv/bin/python3 harness-core/src/main.py format "$@"`. 🟢
3. Grava `post-merge` com o corpo de `_post_merge_script()`, que invoca a mesma CLI com `decisions "$@"`. 🟢
4. Cada script gravado checa a existência do interpretador (`$PYTHON_CLI`); se ausente, `exit 0` (não bloqueia). 🟢
5. Retorna a lista de caminhos instalados. 🟢

Fluxo **linear, sem condicionais de negócio**; único efeito colateral é I/O em `.git/hooks/`.

## Fluxos Alternativos

- **Reexecução:** os scripts são reescritos idempotentemente a cada chamada. 🟢
- **Interpretador ausente em runtime do gancho:** o próprio script faz `exit 0` (salvaguarda dentro do Bash gravado). 🟢

## Dependências

- `FileSystemPort` — criação do diretório e gravação dos scripts.
- (Em runtime do gancho) o interpretador `harness-core/.venv/bin/python3` e a CLI `src/main.py`.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Caminhos do interpretador e da CLI literais nos scripts gravados | `service.py` (`_pre_commit_script`/`_post_merge_script`) | 🟢 |
| `pre-commit`→`format`, `post-merge`→`decisions` (ganchos Git, não de agente) | `service.py` | 🟢 |
| Não-bloqueio: `exit 0` se o interpretador não existir | corpo Bash gravado | 🟢 |

## Estado Interno

Sem estado em memória. O efeito persistente são os dois arquivos em `.git/hooks/`.

## Observabilidade

Sem logging estruturado. O retorno da lista de caminhos é a confirmação de instalação; a não-existência do interpretador degrada para no-op silencioso no runtime do gancho.

## Riscos e Lacunas

- 🟡 Coexistência de dois mecanismos de gancho (Git pre-commit/post-merge vs hooks de agente nos `settings.json`) — possível confusão sobre qual caminho está ativo num dado fluxo.
- 🟡 Os caminhos do interpretador/CLI são chumbados nos scripts; mudança da localização da venv exige re-bootstrap.
