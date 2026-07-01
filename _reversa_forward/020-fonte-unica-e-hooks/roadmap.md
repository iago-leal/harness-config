# Roadmap: fonte única de execução (venv/core central) + materialização de hooks não-destrutiva

> Identificador: `020-fonte-unica-e-hooks`
> Data: `2026-07-01`
> Requirements: `_reversa_forward/020-fonte-unica-e-hooks/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A mudança é um delta cirúrgico, não uma reescrita. O `harness init` deixa de replicar o core e de criar `.venv` no alvo (RN-N19) e passa a gravar um **shim** bash que executa o core do **upstream** com o cwd do projeto. A viabilidade repousa num fato verificado nesta análise (auditoria RF-08): **todos** os comandos resolvem os dados do projeto pelo cwd (`os.getcwd()`, `load_config("harness.toml")` relativo); os únicos usos de `__file__` apontam para **assets do próprio core** (template da doc, `template.md` do install-prompt, `assets/skills/`, `sys.path` do `src`) — que corretamente devem vir do upstream. Logo, apontar o shim para o upstream **não exige tocar o core**. Em paralelo, corrigem-se dois materializadores destrutivos — o merge dos hooks do Claude (por-item, não por-evento) e a instalação dos hooks git (por assinatura, não-destrutiva) — e adiciona-se o subcomando `harness migrate` para converter a base instalada. O `upgrade` sobrevive como no-op barulhento; `sync/`, `version` e a detecção de versão do upstream são removidos. Camadas hexagonais e portas (`fs`/`git`/`process`) preservadas; testes com `FakeFs` + smoke com git real.

## 2. Princípios aplicados

> O projeto não possui `.reversa/principles.md`. A tabela relaciona a feature aos princípios do mantenedor (`~/dev` / global), que governam as decisões.

| Princípio                                | Como a feature se relaciona                                                                               | Status                                                   |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Longevidade / baixa dívida (nº 5)        | Remove código morto (`sync/`, `upgrade` físico, `version`); uma fonte de verdade                          | respeita                                                 |
| Baixo acoplamento / alta coesão (nº 5)   | Shim isola o alvo do layout do core; hooks passam a chamar o shim, não o python local                     | respeita                                                 |
| Footprint reversível (ADR-0013 / RN-N17) | Escrita continua só no repo do projeto; o upstream é repo versionado, não diretório de fornecedor (RN-02) | respeita (autocontenção física relaxada conscientemente) |
| Erros barulhentos (nº operacional)       | Shim e migrate falham com erro nomeado e exit ≠ 0; nada degradado em silêncio                             | respeita                                                 |
| Estabilidade > novidade (nº 3)           | Zero dependência nova (descartadas as opções `uv`/symlink); só bash + core existente                      | respeita                                                 |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                                      | Justificativa                                                                                                             | Alternativas descartadas                                                                                                                                                                         | Confidência |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| D-01 | Shim bash: lê `upstream_path` do `harness.toml`, `cd` para a raiz do projeto, `exec` do `python3`+`main.py` do upstream, repassando `$@`                                                     | Alvo passa a executar a fonte única sem cópia; cwd garante que o core opere sobre o `.harness/`/`harness.toml` do projeto | Caminho do upstream chumbado no shim (frágil a mover); variável de ambiente/XDG (estado global, fere RN-N17); symlink só da venv com scripts copiados (Opção A — mantém redundância dos scripts) | 🟢          |
| D-02 | Não refatorar o core: mantê-lo cwd-relativo                                                                                                                                                  | Auditoria RF-08 provou que nenhum comando resolve dado do projeto por `__file__`; refatorar seria risco sem ganho         | Injetar `--project-dir` em todos os comandos (superfície grande, desnecessária)                                                                                                                  | 🟢          |
| D-03 | Merge do `settings.json` **por-item** dentro do array de cada evento, identificando o item do harness por substring no `command` (`harness cmd resume`/`harness format`/`harness decisions`) | Preserva hooks próprios do usuário no mesmo evento; espelha o merge por named-hook já usado no Antigravity (RN-N27)       | Marca em campo extra do JSON (schema do Claude pode ignorar/rejeitar); usar `matcher` como chave (colide com matchers do usuário)                                                                | 🟢          |
| D-04 | Hooks git não-destrutivos por assinatura `— Harness Core`: ausente→cria, próprio→atualiza, alheio→encadeia (`<hook>.local`); e passam a invocar o shim                                       | Nunca descarta hook do projeto; desacopla o hook do layout do core                                                        | `core.hooksPath` (substitui `.git/hooks` inteiro, silencia hooks do projeto); sobrescrever incondicional (RN-N15 atual, destrutivo)                                                              | 🟢          |
| D-05 | `upgrade` vira **no-op barulhento** (aviso + exit 0), não removido do parser                                                                                                                 | Transição sem quebrar hábito/doc dos 17 projetos                                                                          | Remover do parser já (quebra `./harness upgrade` existente)                                                                                                                                      | 🟢          |
| D-06 | `harness migrate` como **subcomando versionado** com serviço no core                                                                                                                         | Testável, reutilizável, coeso; migração é operação repetível                                                              | Script one-shot descartável (não testável, vira dívida)                                                                                                                                          | 🟢          |
| D-07 | Remover `sync/service.py`, o alerta passivo (main.py), `version` do `harness.toml`, `_get_upstream_version`/`UpstreamVersionUndeterminedError`/`CORE_CONFIG_CANDIDATE_RELPATHS`              | Sob fonte única viva não há "versão do upstream a comparar"                                                               | Manter inertes (código morto, contradiz o objetivo de menos maquinaria)                                                                                                                          | 🟢          |

## 4. Premissas

| Premissa                                                                                       | Origem (`requirements.md` seção)  | Risco se errada                                                                                                          |
| ---------------------------------------------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Execução sempre na mesma máquina, com `~/dev/harness` (upstream) presente (H1 travada no PCCP) | §6 RNF Portabilidade; RN-01/RN-03 | Clonar/rodar um projeto em máquina sem o upstream faz o shim falhar (barulhento, sem execução) — sem clones alhures hoje |
| Todas as instalações compartilham o mesmo `requirements.txt`/deps do upstream                  | §6 Reprodutibilidade              | Se um projeto exigisse deps divergentes, a fonte única não o atenderia (não é o caso — deps são idênticas)               |

> Nenhuma premissa deriva de `[DÚVIDA]` pendente: as duas dúvidas do requirements foram resolvidas no `/reversa-clarify` (§9).

## 5. Delta arquitetural

| Componente                                     | Arquivo de origem no legado                                   | Tipo de mudança    | Resumo                                                                                                                                                               |
| ---------------------------------------------- | ------------------------------------------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Wrapper `harness`                              | `harness` (raiz) + `domain.md#2.9` (RN-N19)                   | contrato-alterado  | Cópia executora → **shim** que aponta para o core do upstream                                                                                                        |
| `initialize_project`                           | `bootstrap/init_service.py` · `domain.md#2.9` (RN-N19)        | regra-alterada     | Remove cópia do core (passo 3) e criação de venv (passo 7); grava o shim; mantém `.harness/`, `harness.toml` (sem `version`), bootstrap, `apply_local_materializers` |
| `upgrade_project`                              | `bootstrap/init_service.py` · `domain.md#2.9` (RN-N20)        | componente-extinto | Removido; o comando `upgrade` vira no-op barulhento no `main.py` (D-05)                                                                                              |
| `materialize_claude_settings`                  | `install/claude_settings.py` · `domain.md#2.13` (RN-N30)      | regra-alterada     | `hooks[event] = value` → merge por-item por assinatura (D-03)                                                                                                        |
| `install_hooks`                                | `bootstrap/service.py` · `domain.md#2.7` (RN-N15)             | regra-alterada     | Sobrescrita incondicional → criar/atualizar/encadear por assinatura; scripts chamam o shim (D-04)                                                                    |
| `SyncService` + alerta passivo                 | `core/sync/service.py` · `main.py` · `domain.md#2.9` (RN-N21) | componente-extinto | Removidos (D-07)                                                                                                                                                     |
| Detecção de versão do upstream                 | `bootstrap/init_service.py` · `domain/layout.py`              | componente-extinto | `_get_upstream_version`, `UpstreamVersionUndeterminedError`, `CORE_CONFIG_CANDIDATE_RELPATHS` removidos (D-07)                                                       |
| `MigrateService` (novo) + subcomando `migrate` | novo: `core/migrate/service.py` · `main.py`                   | componente-novo    | Converte instalações do layout copiado para a fonte única (RN-08)                                                                                                    |
| Config `harness.toml` (`version`)              | `core/domain/config.py` · `domain.md#2.9` (RN-N18)            | contrato-alterado  | Campo `version` aposentado; `upstream_path` é a única âncora                                                                                                         |

## 6. Delta no modelo de dados

- Resumo das mudanças: o `harness.toml` perde o campo `version` da seção `[harness]`; `upstream_path` permanece como única âncora. O estado por-projeto em `.harness/` (decisões, índice, estado-da-sessão) é **inalterado**. Nenhum schema de dados de negócio é afetado.
- Detalhe completo em: `_reversa_forward/020-fonte-unica-e-hooks/data-delta.md`

## 7. Delta de contratos externos

| Contrato                                             | Tipo             | Arquivo de detalhe                    |
| ---------------------------------------------------- | ---------------- | ------------------------------------- |
| Execução shim ↔ core do upstream                     | arquivo/processo | `interfaces/shim-execution.md`        |
| Merge dos hooks do Claude em `.claude/settings.json` | arquivo          | `interfaces/claude-settings-merge.md` |
| Instalação não-destrutiva dos hooks git              | arquivo          | `interfaces/git-hooks-merge.md`       |

## 8. Plano de migração

Executado pelo `harness migrate` (idempotente, não-destrutivo; suporta `--dry-run`). Para cada instalação sob a raiz alvo (default `~/dev`, descoberta por `harness.toml`):

1. Ler `upstream_path` do `harness.toml`; validar que o core do upstream existe (senão, pular com aviso).
2. Substituir o wrapper `harness` pelo **shim** (D-01).
3. Reescrever os hooks git `pre-commit`/`post-merge` para invocar o shim, preservando hooks alheios (D-04).
4. Re-materializar `.claude/settings.json` com o merge por-item (D-03) — preserva hooks próprios.
5. Remover o campo `version` do `harness.toml`.
6. **Por último**, remover `.harness/harness-core/` (código + venv) — libera ~108 MB por instalação.
7. Caso especial `livro-mfc`: remover também o layout legado `harness-core/` na raiz (duplo).
8. Relatar por instalação: espaço liberado, hooks preservados, e o total agregado (~1,78 GB esperado).

Ordem importa: o core só é apagado (passo 6) após o shim e os hooks já apontarem para o upstream, para nunca deixar o projeto num estado sem executor.

## 9. Riscos e mitigações

| Risco                                                                  | Impacto | Probabilidade | Mitigação                                                                                                            |
| ---------------------------------------------------------------------- | ------- | ------------- | -------------------------------------------------------------------------------------------------------------------- |
| Upstream movido/renomeado quebra os 17 shims                           | alto    | baixo         | Shim falha barulhento com instrução; `upstream_path` no toml; `migrate` re-executável para reapontar                 |
| MCP server iniciado sem cwd na raiz do projeto                         | médio   | baixo         | Já usa `os.getcwd()` (server.py:40,101) — herda o contrato do shim; documentar no onboarding                         |
| Escrita de `.pyc` concorrente no `src` do upstream por vários projetos | baixo   | baixa         | Bytecode é determinístico por versão de código/Python; inócuo. Opção: `PYTHONDONTWRITEBYTECODE` no shim              |
| `migrate` apaga estado ou hook alheio por engano                       | alto    | baixa         | Não-destrutivo por design (só `.harness/harness-core/`); `--dry-run`; testes com `FakeFs` + smoke git real           |
| Perda do pin de versão por-projeto                                     | médio   | —             | Trade-off consciente travado no PCCP; um bug do upstream atinge todos — mitigar com disciplina de commit no upstream |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Suíte do core verde (incl. novos testes de merge por-item, hooks não-destrutivos, shim e `migrate`)
- [ ] Smoke com git real: `init` sem venv/core; shim executa via upstream; erro barulhento sem upstream; `migrate` num projeto de teste preserva estado/hooks e libera disco
- [ ] `regression-watch.md` gerado (atenção a RN-N15/N17/N19/N20/N21/N27/N30)
- [ ] Re-extração reversa recomendada (reconciliar `domain.md` §2.7/2.8/2.9/2.11/2.13)

## 11. Histórico de alterações

| Data       | Alteração                                                                                                      | Autor   |
| ---------- | -------------------------------------------------------------------------------------------------------------- | ------- |
| 2026-07-01 | Versão inicial gerada por `/reversa-plan` (auditoria RF-08 concluída: fonte única viável sem refactor do core) | reversa |
