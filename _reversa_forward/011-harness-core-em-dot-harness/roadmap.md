# Roadmap: harness-core dentro de `.harness/` (footprint de um diretório na raiz)

> Identificador: `011-harness-core-em-dot-harness`
> Data: `2026-06-25`
> Requirements: `_reversa_forward/011-harness-core-em-dot-harness/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A mudança é essencialmente de **layout físico mais um ponto único de verdade para o caminho do core**. Hoje o literal `harness-core` está chumbado em ~7 lugares: o wrapper `harness`, o gerador de ganchos Git (`bootstrap/service.py`), o `init_service.py` (cópia, resolução do upstream e leitura de versão), a checagem passiva de versão (`sync/service.py`) e dois artefatos de documentação. Em vez de propagar o novo caminho `.harness/harness-core` por todos esses pontos como literais soltos, introduzo uma constante única em `core/domain/` consumida por todo o código Python; o wrapper Bash e o template de instalação — que não importam Python — recebem a string atualizada à mão. Sobre isso, adiciono um comportamento novo restrito ao **alvo**: o `init` registra `.harness/harness-core/` no `.gitignore` do projeto-alvo, de forma idempotente, tornando a cópia vendored um artefato regenerável; no repo-fonte o core permanece versionado. Por fim, endureço a falha do wrapper para instruir a restauração via `upgrade`/`init` quando o core estiver ausente, protegendo a reprodutibilidade que o gitignore tensiona. O move no próprio repositório-fonte é um `git mv` seguido de **recriação** da `.venv` (venvs não são realocáveis) e re-execução do `bootstrap`.

## 2. Princípios aplicados

> O projeto não possui `.reversa/principles.md`. A tabela mapeia os princípios operacionais vigentes (contexto global do mantenedor) que esta feature toca diretamente. Nenhum conflito identificado.

| Princípio                      | Como a feature se relaciona                                                                                                             | Status   |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Baixo acoplamento              | Substitui ~7 literais espalhados por uma constante única (`CORE_REL_PATH`); o caminho do core passa a ter um ponto de mudança           | respeita |
| Alta coesão / SRP              | A constante de layout vive num módulo próprio de domínio; a escrita do `.gitignore` é um método coeso no `InitializationService`        | respeita |
| OOP e contratos                | Toda escrita continua via `FileSystemPort`; o novo método e a constante não rompem a inversão de dependência do hexágono                | respeita |
| TDD                            | `test_init.py` e `test_footprint.py` são atualizados **antes** da implementação; novo teste cobre a escrita idempotente do `.gitignore` | respeita |
| Footprint global zero (RN-N17) | Cópia e escrita do `.gitignore` ocorrem sob `target_path`; o contrato testado é estendido ao novo caminho                               | respeita |
| Erros barulhentos              | Wrapper falha com exit ≠ 0 e instrução de restauração quando o core some (RN-07)                                                        | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                                                                                                                                                                       | Justificativa                                                                                                                   | Alternativas descartadas                                                                                                                            | Confidência |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| D-01 | Introduzir uma fonte única do caminho relativo do core (`CORE_REL_PATH = ".harness/harness-core"`) em `core/domain/` (p.ex. `layout.py`), consumida por `init_service`, `sync/service` e o gerador de ganchos de `bootstrap/service`                                                                                          | O literal `harness-core` está hoje em ~7 pontos; centralizar reduz acoplamento e dá ponto único de mudança                      | (a) repetir o literal novo em cada ponto — frágil; (b) ler de `harness.toml` — overkill, o caminho é estrutural e fixo, não configuração de usuário | 🟢          |
| D-02 | Wrapper `harness` permanece **arquivo na raiz**, apontando para `.harness/harness-core/.venv/bin/python3` e `.harness/harness-core/src/main.py`; mensagens de erro passam a instruir `upgrade`/`init` (RN-07)                                                                                                                 | Decisão de escopo esclarecida (seção 9 do requirements); preserva `./harness` e todas as referências de ganchos                 | Migrar o wrapper para `.harness/` — exigiria revisar todas as referências a `./harness` nos ganchos e slash commands                                | 🟢          |
| D-03 | `init`/`upgrade` copiam o core para `<alvo>/.harness/harness-core/`; a resolução do `upstream_path` sobe **um nível a mais** (o `init_service.py` passa a residir em `.harness/harness-core/src/core/bootstrap/`); `_get_upstream_version` e `sync/service` leem `<upstream>/.harness/harness-core/src/core/domain/config.py` | Consequência direta do novo layout; mantém init/upgrade simétricos entre fonte e alvo (RN-N19/RN-N20)                           | Resolver o upstream por busca ascendente do `.git` — mais robusto, porém fora do escopo e maior raio de mudança                                     | 🟢          |
| D-04 | Novo método `_ensure_gitignore_entry(target_path, ".harness/harness-core/")` no `InitializationService`: lê o `.gitignore` do alvo (vazio se ausente), acrescenta a linha se faltar (idempotente) e grava atômico sob `target_path`. Chamado por `init` **e** `upgrade` (auto-cura). Só no alvo                               | Atende ao segundo pedido (gitignore no alvo) sem tocar o `.gitignore` do repo-fonte, que mantém o core versionado (RN-05/RN-06) | Editar o `.gitignore` do fonte — descartado: perderia o código canônico                                                                             | 🟡          |
| D-05 | O `harness.toml` operativo permanece na raiz, lido cwd-relative por `load_config(fs, config_path="harness.toml")`; `load_config` e call-sites inalterados. Só o `harness-core/harness.toml` (template) acompanha o core                                                                                                       | Decisão técnica esclarecida (seção 9); menor superfície de alteração                                                            | Mover o `harness.toml` operativo para `.harness/` — exigiria passar `config_path` em CLI, MCP e ponte Antigravity                                   | 🟢          |
| D-06 | Mover o core no repo-fonte via `git mv harness-core .harness/harness-core`, **recriar** a `.venv` no novo caminho e re-rodar `./harness bootstrap` para regenerar os ganchos Git                                                                                                                                              | Venvs não são realocáveis (shebangs absolutos em `.venv/bin/*`); ganchos Git embutem o caminho do core                          | `git mv` da `.venv` junto — descartado: quebraria os shebangs e a CLI                                                                               | 🟢          |
| D-07 | Estender `test_footprint.py` e `test_init.py` ao novo caminho e adicionar teste do `_ensure_gitignore_entry`                                                                                                                                                                                                                  | Regressão zero é condição de aceite (RF-08); o contrato de footprint deve cobrir o novo materializador                          | —                                                                                                                                                   | 🟢          |

## 4. Premissas

> Nenhuma. As três dúvidas iniciais foram resolvidas em `/reversa-clarify` (seção 9 do `requirements.md`) e entram aqui como decisões (D-02, D-04, D-05), não como premissas.

## 5. Delta arquitetural

| Componente                       | Arquivo de origem no legado                                                        | Tipo de mudança | Resumo                                                                                            |
| -------------------------------- | ---------------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------- |
| Módulo de layout                 | `_reversa_sdd/architecture.md#1` (anel de domínio `core/`)                         | componente-novo | `core/domain/layout.py` com `CORE_REL_PATH = ".harness/harness-core"`, fonte única do caminho     |
| Wrapper Executável (`harness`)   | `_reversa_sdd/domain.md#wrapper-executavel`, `architecture.md#4`                   | regra-alterada  | Aponta para `.harness/harness-core/...`; mensagem de erro instrui restauração (RN-07)             |
| `InitializationService`          | `_reversa_sdd/domain.md#2.9` (RN-N19/RN-N20), `architecture.md#2.9`                | regra-alterada  | Destino `.harness/harness-core/`; sobe um nível no upstream; novo `_ensure_gitignore_entry`       |
| `BootstrapService` (ganchos Git) | `_reversa_sdd/inventory.md#nucleo-python` (`core/bootstrap/`)                      | regra-alterada  | O script dos ganchos pre-commit/post-merge embute `.harness/harness-core/...` via `CORE_REL_PATH` |
| `SyncService`                    | `_reversa_sdd/domain.md#2.9` (RN-N21)                                              | regra-alterada  | Lê a versão do upstream em `.harness/harness-core/src/core/domain/config.py`                      |
| Documentação                     | `_reversa_sdd/inventory.md` (`install/template.md`, `documentation/template.html`) | regra-alterada  | Trocar `harness-core/...` por `.harness/harness-core/...` no texto de instalação e no snippet     |
| Suíte de testes                  | `harness-core/tests/test_init.py`, `tests/test_footprint.py`                       | regra-alterada  | Caminhos esperados atualizados; novo teste do `.gitignore`                                        |

## 6. Delta no modelo de dados

- Resumo das mudanças: não há banco de dados. A "persistência" afetada é a árvore de arquivos (relocação de `harness-core/` para `.harness/harness-core/`), uma linha nova no `.gitignore` do alvo e a localização inalterada do `harness.toml` operativo. Há também o caso de **instalações já existentes** que rodarem `upgrade` neste novo nível.
- Detalhe completo em: `_reversa_forward/011-harness-core-em-dot-harness/data-delta.md`

## 7. Delta de contratos externos

n/a — a feature não toca contratos HTTP, fila, gRPC nem GraphQL. Os contratos internos de invocação (ganchos Claude/Gemini em `settings.json`, `.agents/hooks.json`, slash commands) referenciam o wrapper `./harness` por caminho e permanecem válidos, pois o wrapper continua na raiz (`_reversa_sdd/domain.md#2.11-2.12`). Diretório `interfaces/` omitido.

## 8. Plano de migração

1. Criar `core/domain/layout.py` com `CORE_REL_PATH = ".harness/harness-core"` (e derivados úteis: caminho do `main.py` e do `python3` da venv).
2. **TDD:** atualizar `test_init.py` e `test_footprint.py` para o novo caminho; adicionar teste do `_ensure_gitignore_entry` (escrita e idempotência). Suíte vermelha esperada.
3. Implementar em `init_service.py`: destino `.harness/harness-core/`, subida de um nível na resolução do upstream, `_get_upstream_version` no novo caminho, e o `_ensure_gitignore_entry` chamado por `init` e `upgrade`.
4. Atualizar `sync/service.py` (caminho do config do upstream) e `bootstrap/service.py` (caminho embutido nos ganchos) via `CORE_REL_PATH`.
5. Atualizar o wrapper `harness` (caminhos + mensagem de restauração) e os artefatos de doc (`install/template.md`, `documentation/template.html`, e as instruções `CLAUDE.md`/`GEMINI.md`/`AGENTS.md` se citarem o caminho).
6. Suíte `pytest` verde.
7. **Move físico no repo-fonte:** `git mv harness-core .harness/harness-core`; recriar a `.venv` em `.harness/harness-core/.venv` (`python3 -m venv` + `pip install -r requirements.txt`); re-rodar `./harness bootstrap` para regenerar os ganchos Git com o novo caminho.
8. Smoke manual: `./harness decisions`, `./harness format <arquivo>` a partir da raiz; e o roteiro de `onboarding.md` num alvo descartável.
9. (Recomendado) Re-extração reversa cirúrgica para reconciliar `inventory.md`/`architecture.md`/`domain.md` ao novo caminho.

## 9. Riscos e mitigações

| Risco                                                                           | Impacto | Probabilidade | Mitigação                                                                                                                   |
| ------------------------------------------------------------------------------- | ------- | ------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `.venv` movida com `git mv` quebra os shebangs absolutos e a CLI                | alto    | média         | **Recriar** a venv no novo caminho, nunca movê-la (D-06); a venv é gitignorada, então o `git mv` não a carrega              |
| Ganchos Git instalados apontam para o caminho antigo até re-bootstrap           | médio   | alta          | Passo explícito de re-rodar `./harness bootstrap` após o move (passo 7)                                                     |
| Transição quebra `./harness` em uso no próprio repo durante o move              | médio   | média         | Executar o move como sequência atômica e fora de uma sessão ativa; validar com smoke logo após                              |
| Instalação alvo já existente deixa `harness-core/` órfão na raiz após `upgrade` | baixo   | alta          | Não-destrutivo: não apagar automaticamente; documentar remoção manual em `onboarding.md` e na mensagem de `upgrade`         |
| Reprodutibilidade do alvo gitignorado depende do `upstream_path` host-local     | médio   | média         | Aceito (seção 9 do requirements): RN-07 falha barulhenta com instrução; `harness.toml` registra `upstream_path` e `version` |
| Referências stale em docs/instruções de agente                                  | baixo   | média         | Atualizar `install/template.md`, `template.html`, `CLAUDE.md`/`GEMINI.md`/`AGENTS.md` no mesmo lote (passo 5)               |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `pytest` verde, incluindo footprint estendido e o teste do `.gitignore` idempotente
- [ ] No repo-fonte, `harness-core/` não existe mais na raiz e `.harness/harness-core/` está versionado; `./harness` funciona da raiz
- [ ] `init` num alvo limpo produz `<alvo>/.harness/harness-core/`, sem `<alvo>/harness-core/`, com a linha no `.gitignore`
- [ ] Wrapper falha com exit ≠ 0 e instrução de restauração quando o core está ausente
- [ ] `regression-watch.md` gerado
- [ ] (Recomendado) Re-extração reversa sem regressão vermelha

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-06-25 | Versão inicial gerada por `/reversa-plan` | reversa |
