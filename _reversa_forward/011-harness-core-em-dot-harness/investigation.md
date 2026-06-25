# Investigação: harness-core dentro de `.harness/`

> Feature `011-harness-core-em-dot-harness` · 2026-06-25

## 1. Pesquisa de fundo

O harness é uma instalação de si mesmo: o repositório-fonte contém `.harness/` (estado e decisões versionados), `harness-core/` (código + venv) e o wrapper `harness`. O comando `init` replica esse layout em projetos-alvo (`_reversa_sdd/domain.md#2.9`, RN-N19). O incômodo relatado é a presença de **dois diretórios** do tooling na raiz; a feature os colapsa em um, movendo `harness-core/` para dentro de `.harness/`.

O levantamento de acoplamento (grep por `harness-core` no código, fora de SDD/forward) encontrou o literal em sete pontos:

- `harness` (wrapper): `VENV_PYTHON`, `MAIN_PY` e três mensagens de erro.
- `core/bootstrap/service.py`: o script dos ganchos pre-commit/post-merge embute `PYTHON_CLI="harness-core/src/main.py"` e `PYTHON_BIN="harness-core/.venv/bin/python3"` (duas ocorrências cada).
- `core/bootstrap/init_service.py`: `src_core`/`dst_core` (init e upgrade), a subida de 5 níveis para resolver o upstream e o caminho de `_get_upstream_version`.
- `core/sync/service.py`: caminho do `config.py` do upstream na checagem passiva de versão (RN-N21).
- `core/install/template.md` e `core/documentation/template.html`: texto de instalação e snippet `cd harness-core`.

Esse espalhamento é o que motiva a fonte única de verdade (D-01): sem ela, o novo caminho viraria sete literais a manter em sincronia.

## 2. Alternativas avaliadas

| Alternativa                                      | Veredito                | Razão                                                                                                                                                                     |
| ------------------------------------------------ | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Mover em fonte e alvo, gitignore só no alvo**  | **Escolhida**           | Layout canônico único; wrapper copiável verbatim; resolve o incômodo no próprio repo. É o Alcance 1 confirmado pelo mantenedor                                            |
| Mover só no alvo (fonte intacto)                 | Descartada              | Criaria assimetria fonte×alvo, forçando reescrita de caminhos do wrapper na cópia — acoplamento e dívida; e não resolveria os dois diretórios no repo que o mantenedor vê |
| Gitignore também no fonte                        | Descartada              | Deixaria de versionar o código canônico do produto                                                                                                                        |
| Não gitignorar no alvo (alvo autocontido)        | Considerada e preterida | Mantém o alvo clonável-e-roda sem upstream, mas carrega churn do core no histórico a cada `upgrade`; contraria o footprint-zero pedido                                    |
| Versionar só `requirements.*` no alvo            | Preterida               | Não torna o clone executável (falta o código), então não compra reprodutibilidade real                                                                                    |
| Caminho do core configurável em `harness.toml`   | Descartada              | O caminho é estrutural e fixo, não preferência de usuário; configuração aqui é complexidade sem ganho                                                                     |
| Resolver upstream por busca ascendente do `.git` | Fora de escopo          | Mais robusto que contar níveis, porém amplia o raio de mudança; fica como melhoria futura                                                                                 |

## 3. Padrões aplicáveis

- **Single source of truth** para o caminho do core (`CORE_REL_PATH`): um módulo de domínio coeso, consumido por serviços e interpolado nos templates de script (ganchos Git) e no wrapper à mão.
- **Idempotent file append**: o `_ensure_gitignore_entry` lê, verifica presença da linha e só então acrescenta; reexecutar `init`/`upgrade` converge — mesmo padrão dos materializadores `materialize_hooks_json`/`materialize_session_commands` (RN-N27/RN-N28).
- **Escrita atômica via porta**: toda escrita continua por `FileSystemPort.write_file_atomic`, preservando a inversão de dependência e o contrato de footprint (RN-N17).
- **Fail-fast observável**: o wrapper já falha quando a venv falta; a feature estende a mensagem para cobrir o core ausente e apontar a restauração (RN-07).

## 4. Nota técnica externa — venvs não são realocáveis

Ambientes virtuais do Python embutem caminhos absolutos nos shebangs dos executáveis em `.venv/bin/*` e no `pyvenv.cfg`. Mover a pasta da venv com `git mv`/`mv` quebra esses caminhos. Por isso o move físico (D-06) **recria** a venv no novo local em vez de movê-la. Como a `.venv` já é gitignorada (`.gitignore` do projeto tem `.venv/`), o `git mv harness-core .harness/harness-core` sequer a carrega — ela some no move e é reconstruída com `python3 -m venv` + `pip install -r requirements.txt`.

## 5. Pontos a confirmar na implementação

- Conferir se `CLAUDE.md`, `GEMINI.md` e `AGENTS.md` citam o caminho `harness-core` em instruções de setup (o grep inicial cobriu `settings.json`, não os `.md` de instrução de agente na raiz); se citarem, atualizar no lote.
- Conferir o comportamento de `upgrade` em uma instalação alvo já existente: o core novo nasce em `.harness/harness-core/`, mas o `harness-core/` antigo permanece órfão na raiz — tratar como remoção manual documentada (não-destrutivo).
