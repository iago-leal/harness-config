# Roadmap: Upgrade resiliente do harness-core

> Identificador: `012-corrige-upgrade-stale`
> Data: `2026-06-25`
> Requirements: `_reversa_forward/012-corrige-upgrade-stale/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A correção é um delta cirúrgico sobre o `InitializationService` (`bootstrap/init_service.py`), a CLI (`main.py`), o `SyncService` (`sync/service.py`) e o `layout.py`, sem tocar a arquitetura hexagonal nem os contratos de domínio. **Modo 1 (stale):** a materialização de artefatos de IDE no `upgrade` passa a rodar com o **código recém-copiado**, via um subcomando interno da CLI invocado por subprocesso do python de destino — exatamente o molde que o `bootstrap` de ganchos Git já usa. **Modo 2 (upgrade fantasma):** a leitura da versão do upstream passa a tentar uma lista de **caminhos-candidato** (canônico `.harness/harness-core/` + legado raiz `harness-core/`) e, quando nenhuma versão é determinável, o `upgrade` **aborta barulhento** com instrução de `init`, em vez de cair no fallback `current_version` que igualava versões e gerava o no-op silencioso. Acrescenta-se a flag `upgrade --force` como escape hatch (recópia + rematerialização ignorando a comparação de versão) e o mesmo helper de candidatos é reusado pela checagem passiva (RN-N21), para que o alerta de nova versão também sobreviva a relayouts. A recuperação das instalações já presas no layout antigo é o `init` do upstream por caminho absoluto, documentado.

## 2. Princípios aplicados

> O projeto não possui `.reversa/principles.md` (princípios formais não definidos). A feature é avaliada contra os princípios globais do mantenedor (erros barulhentos, reprodutibilidade, footprint zero, baixo acoplamento), refletidos nas decisões abaixo.

| Princípio                       | Como a feature se relaciona                                                                            | Status   |
| ------------------------------- | ------------------------------------------------------------------------------------------------------ | -------- |
| Erros barulhentos               | RN-04: versão indeterminada aborta com mensagem clara e exit ≠ 0, nunca no-op silencioso               | respeita |
| Reprodutibilidade temporal      | Mesmo upstream + alvo → mesmo resultado, independentemente da versão que executou o `upgrade` (Modo 1) | respeita |
| Footprint global zero (RN-N17)  | Toda escrita segue sob `project_path`; o subprocesso roda com `cwd=target_path`                        | respeita |
| Baixo acoplamento / fonte única | Caminhos-candidato centralizados em `layout.py`; materialização compartilhada por `init`/`upgrade`     | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                                                                                                                                           | Justificativa                                                                                                                                                | Alternativas descartadas                                                                                                                            | Confidência |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| D-01 | Extrair a materialização local (session commands sempre; `hooks.json` sob Antigravity) para uma função única chamada por `init` (in-process, já fresco) e por `upgrade` via **subcomando interno** rodado por subprocesso do python de destino (`[dst_python, dst_main, <subcmd>]`, `cwd=target`) | Mata o Modo 1 com o molde já existente do `bootstrap`; testável com processo real; preserva footprint zero; SRP e DRY (uma lógica de materialização)         | (a) `os.execv` re-exec do processo de upgrade — complica fluxo/print e teste; (b) `importlib.reload` — frágil, não recarrega submódulos transitivos | 🟢          |
| D-02 | `_get_upstream_version` passa a varrer uma lista de caminhos-candidato do `config.py` (canônico + legado raiz); na ausência de todos, **levanta erro** em vez de retornar `current_version`                                                                                                       | Resolve o gatilho do Modo 2 (relayout root→`.harness/`) e elimina o fallback que igualava versões; alinha a erros barulhentos                                | Ler a versão do `harness.toml` do upstream — o repo-fonte não mantém `harness.toml` na raiz, fonte inexistente                                      | 🟢          |
| D-03 | Centralizar os caminhos-candidato do `config.py` em `layout.py` (ex.: `CORE_CONFIG_CANDIDATE_RELPATHS`) como fonte única                                                                                                                                                                          | Um único ponto de mudança quando o layout evoluir; baixo acoplamento; reusado por `_get_upstream_version` e pelo `SyncService`                               | Duplicar a lista no serviço e no sync — acoplamento e divergência                                                                                   | 🟢          |
| D-04 | Flag `--force` no subparser `upgrade`; `upgrade_project(target, force=False)`; quando `force`, pula a comparação de versão e o abort por versão indeterminada (vira aviso), sempre copia + rematerializa                                                                                          | Escape hatch explícito (RN-07/RF-07) sem exigir o caminho absoluto do `init`; útil após edição local ou drift                                                | Só `init` como reidratação — exige caminho absoluto e recria venv, mais pesado que o necessário                                                     | 🟢          |
| D-05 | `SyncService.check_version_update` (RN-N21) passa a usar o mesmo helper de candidatos, mantendo a tolerância a erro não-bloqueante                                                                                                                                                                | O alerta passivo de nova versão também sobrevive a relayout, sem regressão de comportamento                                                                  | Deixar o sync com caminho fixo — voltaria a falhar silenciosamente o alerta na próxima relocação                                                    | 🟡          |
| D-06 | Guardar a presença do python de destino antes do subprocesso de materialização; se ausente, abortar barulhento com instrução de reidratação                                                                                                                                                       | O `upgrade` não recria a venv; um destino sem venv deve falhar claro, não com traceback de subprocesso                                                       | Recriar a venv no `upgrade` — fora de escopo e mais lento; o `init` é o caminho de reidratação completa                                             | 🟡          |
| D-07 | Documentar a recuperação (init do upstream por caminho absoluto + remoção do `harness-core/` órfão) e a flag `--force` no material de instalação/uso                                                                                                                                              | RF-05 exige caminho de recuperação documentado; local exato a confirmar no `/reversa-to-do`                                                                  | Não documentar — deixaria a recuperação como conhecimento tácito desta sessão                                                                       | 🟡          |
| D-08 | Bump de versão `1.2.47 → 1.2.48` em `config.py` e `InitializationService.current_version` ao final                                                                                                                                                                                                | A propagação por `upgrade` exige `upstream_version != local_version`; sem o bump, alvos no `1.2.47` não puxam o fix (ver [[upgrade-materializadores-stale]]) | Não bumpar — o fix não chegaria aos alvos via `upgrade`                                                                                             | 🟢          |

## 4. Premissas

> Nenhuma premissa derivada de `[DÚVIDA]` não resolvida — as três dúvidas foram fechadas no `/reversa-clarify` (requirements §9).

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
| -------- | -------------------------------- | --------------- |
| n/a      | n/a                              | n/a             |

## 5. Delta arquitetural

| Componente                                    | Arquivo de origem no legado                                | Tipo de mudança   | Resumo                                                                                                         |
| --------------------------------------------- | ---------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------- |
| `InitializationService.upgrade_project`       | `.harness/harness-core/src/core/bootstrap/init_service.py` | regra-alterada    | Materialização via subprocesso do código novo; abort em versão indeterminada; parâmetro `force`                |
| `InitializationService._get_upstream_version` | `.harness/harness-core/src/core/bootstrap/init_service.py` | regra-alterada    | Varre caminhos-candidato; levanta erro em vez de fallback silencioso (RN-N20/`_reversa_sdd/domain.md#2.9`)     |
| Função de materialização local (nova)         | `.harness/harness-core/src/core/install/`                  | componente-novo   | Une `materialize_session_commands` + `materialize_hooks_json` (gate Antigravity); chamada por `init`/`upgrade` |
| CLI `upgrade` + subcomando interno            | `.harness/harness-core/src/main.py`                        | contrato-alterado | `upgrade` ganha `--force`; novo subcomando interno roda a materialização com o código de destino               |
| `SyncService.check_version_update`            | `.harness/harness-core/src/core/sync/service.py`           | regra-alterada    | Usa o helper de candidatos (RN-N21/`_reversa_sdd/domain.md#2.9`)                                               |
| `layout.py`                                   | `.harness/harness-core/src/core/domain/layout.py`          | componente-novo   | Fonte única dos caminhos-candidato do `config.py` (canônico + legado)                                          |

Referências de domínio: RN-N20 (evolução não-destrutiva), RN-N21 (checagem passiva), RN-N27/RN-N28 (materializadores únicos) em `_reversa_sdd/domain.md#2.9`, `#2.11-2.12`; ADRs `0014` (bootstrap e evolução do tooling), `0017` (slash commands materializados no init/upgrade).

## 6. Delta no modelo de dados

- Resumo das mudanças: não há banco de dados nem entidades persistidas. O único "dado" afetado é a **resolução da versão do upstream** (de caminho fixo para lista de candidatos) e a semântica do campo `version` no `harness.toml`, que permanece inalterada. Sem migração de dados.
- Detalhe completo em: `_reversa_forward/012-corrige-upgrade-stale/data-delta.md`

## 7. Delta de contratos externos

> n/a — a feature não toca contratos HTTP, fila, gRPC ou GraphQL. A única superfície é a CLI local (`./harness upgrade [--force]` e o subcomando interno de materialização), tratada no delta arquitetural. Diretório `interfaces/` omitido.

## 8. Plano de migração

1. `layout.py`: adicionar a fonte única dos caminhos-candidato do `config.py` (D-03).
2. `_get_upstream_version`: varrer candidatos; levantar erro na ausência de todos (D-02). Atualizar testes.
3. Extrair a função de materialização local compartilhada e expô-la como subcomando interno na CLI (D-01). `init` chama in-process; `upgrade` chama via subprocesso do python de destino, com guarda de presença da venv (D-06).
4. `upgrade`: adicionar `--force` no subparser e o parâmetro `force` em `upgrade_project` (D-04).
5. `SyncService.check_version_update`: reusar o helper de candidatos (D-05).
6. Testes de integração: stale materializer, abort em versão indeterminada, `--force`, detecção resiliente; manter `test_footprint.py` e a suíte verdes.
7. Bump `1.2.47 → 1.2.48` (D-08).
8. Documentar recuperação e `--force` (D-07).

## 9. Riscos e mitigações

| Risco                                                                                              | Impacto | Probabilidade | Mitigação                                                                                                                                       |
| -------------------------------------------------------------------------------------------------- | ------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Subprocesso de materialização falha porque o destino não tem venv (upgrade não recria venv)        | médio   | baixo         | D-06: guardar a presença do python de destino e abortar barulhento com instrução de reidratação via `init`                                      |
| Caminhos-candidato não cobrem um relayout **futuro** arbitrário                                    | médio   | médio         | O abort de RN-04 garante que, mesmo sem candidato, não há no-op silencioso — o usuário é instruído ao `init`                                    |
| `--force` com versão indeterminada não consegue atualizar o `version` do `harness.toml`            | baixo   | médio         | `--force` copia mesmo assim; mantém o `version` existente e emite aviso de versão não-resolvida                                                 |
| Bump de versão materializa com código stale (o próprio bug que estamos corrigindo) na primeira vez | médio   | médio         | Validar o fix rodando o `upgrade` **a partir do código já corrigido** (regenerar artefatos após o bump); ver [[upgrade-materializadores-stale]] |
| Regressão em `init` ao compartilhar a função de materialização                                     | médio   | baixo         | `init` mantém a chamada in-process (código já fresco); testes de `test_init.py` cobrem o caminho                                                |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] `pytest` verde, incluindo footprint estendido e os novos testes de integração do `upgrade`
- [ ] Teste de integração do Modo 1 (materializador alterado no upstream → artefato novo após `upgrade`) verde
- [ ] `upgrade` aborta com exit ≠ 0 e sem "Sucesso" quando a versão do upstream é indeterminada
- [ ] `upgrade --force` recopia e rematerializa com versões iguais
- [ ] Recuperação do layout antigo via `init` do upstream documentada
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-06-25 | Versão inicial gerada por `/reversa-plan` | reversa |
