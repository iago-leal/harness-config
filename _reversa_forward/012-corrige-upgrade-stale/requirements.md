# Requirements: Upgrade resiliente do harness-core (materialização com código novo + detecção de versão à prova de relayout)

> Identificador: `012-corrige-upgrade-stale`
> Data: `2026-06-25`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O comando `upgrade` tem dois modos de falha confirmados que corroem a reprodutibilidade — o filtro número um do mantenedor único intermitente. **Modo 1 (stale):** depois de copiar o core novo ao disco com `_copy_tree`, `upgrade_project` chama os materializadores (`materialize_session_commands` e, sob Antigravity, `materialize_hooks_json`) **in-process**, com os módulos Python antigos ainda carregados em memória; então um upgrade que carrega a correção de um materializador regrava o artefato com a versão **stale** (confirmado em campo: regravou o slash command com `${CLAUDE_PROJECT_DIR}`). **Modo 2 (upgrade fantasma):** quando o upstream relocou o core (feature 011, raiz → `.harness/harness-core/`), uma instalação ainda no layout antigo não consegue se atualizar — `_get_upstream_version` procura o `config.py` no caminho velho, não acha, cai no fallback `current_version`, iguala a versão local e o upgrade retorna sem copiar nada, imprimindo "Sucesso". Esta feature faz o `upgrade` materializar e bootstrappar **sempre com o código recém-copiado**, torna a detecção de versão **resiliente e barulhenta** (nunca um no-op silencioso quando a versão do upstream é indeterminada) e fixa um caminho de recuperação oficial para instalações já presas no layout antigo. O bootstrap de ganchos Git já roda via subprocesso com o código novo e serve de molde para o restante.

## 2. Contexto a partir do legado

| Fonte                                                                 | Trecho relevante                                                                                                                                                                         | Confidência |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `_reversa_sdd/domain.md#2.9` (RN-N20)                                 | `upgrade` atualiza fisicamente código e wrapper a partir do upstream, preservando `.reversa/` e `.harness/decisoes/` — invariante não-destrutivo que esta feature deve manter            | 🟢          |
| `_reversa_sdd/domain.md#2.9` (RN-N21)                                 | Checagem passiva de versão local vs upstream, não-bloqueante e tolerante a erro de leitura; é o mesmo mecanismo de leitura de versão que falha silenciosamente no Modo 2                 | 🟢          |
| `_reversa_sdd/domain.md#2.12` (RN-N28)                                | `materialize_session_commands` é rotina única chamada por `init`/`upgrade` **sempre**; hoje roda in-process — alvo do Modo 1                                                             | 🟢          |
| `_reversa_sdd/domain.md#2.11` (RN-N27)                                | `materialize_hooks_json` é rotina única chamada por `init`/`upgrade` apenas sob `active_harness == "antigravity"`; hoje roda in-process — alvo do Modo 1                                 | 🟢          |
| `_reversa_sdd/adrs/0014-bootstrap-e-evolucao-do-tooling.md`           | Bootstrap e evolução do tooling: `upgrade` reescreve o core do `upstream_path`; o bootstrap de ganchos Git já é delegado a subprocesso do python de destino (molde para o fix do Modo 1) | 🟢          |
| `_reversa_sdd/adrs/0013-harness-core-modulo-per-projeto-footprint.md` | Core é módulo per-projeto "a um `git checkout` de distância de sumir e reaparecer" — propriedade que a recuperação do Modo 2 (`init`/`upgrade`) precisa honrar                           | 🟢          |
| Feature `011-harness-core-em-dot-harness` (concluída)                 | Introduziu `CORE_REL_PATH = ".harness/harness-core"` e a relocação do core; a mudança de layout do upstream é exatamente o gatilho do Modo 2                                             | 🟢          |

## 3. Personas e cenários de uso

| Persona                                           | Objetivo                                                                                          | Cenário-chave                                                                                                             |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Mantenedor único intermitente                     | Atualizar o core de um projeto e confiar que o upgrade realmente aplicou a versão nova            | Roda `./harness upgrade`; ou o core é atualizado de fato, ou recebe erro claro com instrução — nunca "Sucesso" sem efeito |
| Mantenedor com projeto em layout antigo           | Migrar uma instalação pré-feature-011 (core na raiz) para o layout canônico                       | Roda o caminho de recuperação oficial e a instalação passa a `.harness/harness-core/` sem perder estado versionado        |
| Autor do harness propagando fix de materializador | Garantir que um upgrade aplique a versão **nova** de um slash command / `hooks.json`, não a stale | Bumpa a versão, roda `upgrade` num alvo e o artefato materializado reflete o código recém-copiado                         |

## 4. Regras de negócio novas ou alteradas

1. **RN-01: Materialização com o código recém-copiado.** No `upgrade`, a materialização de slash commands e de `hooks.json` deve usar o código **já copiado para o destino**, não os módulos Python carregados em memória no início do processo. O resultado de um upgrade não pode depender de qual versão do core estava rodando o comando. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.11-2.12` (RN-N27, RN-N28)
   - Tipo: alterada
2. **RN-02: Paridade com o bootstrap.** O bootstrap de ganchos Git já roda via subprocesso do python+código de destino (não-stale); os materializadores devem alcançar a mesma garantia de "código novo", por subprocesso equivalente ou por re-exec pós-cópia. 🟢
   - Origem no legado: `_reversa_sdd/adrs/0014-bootstrap-e-evolucao-do-tooling.md`
   - Tipo: nova (uniformiza a etapa pós-cópia)
3. **RN-03: Detecção de versão do upstream resiliente a relayout.** A leitura da versão do upstream não pode quebrar silenciosamente quando o layout do upstream muda. Deve localizar a versão por caminhos-candidato (layout canônico atual e o legado da raiz) ou por fonte alternativa estável, em vez de assumir um único caminho fixo. 🟡
   - Origem no legado: `_reversa_sdd/domain.md#2.9` (RN-N21), feature `011`
   - Tipo: nova
4. **RN-04: Sem no-op silencioso quando a versão é indeterminada.** Se a versão do upstream não puder ser determinada nem mesmo após tentar as fontes resilientes (RN-03), o `upgrade` **não** pode concluir "já atualizado" por igualar a versão local ao próprio fallback. Deve **abortar barulhento** — erro claro, instrução de recuperação via `init` e exit ≠ 0 —, nunca imprimir "Sucesso" sem efeito nem forçar a cópia às cegas (decisão de 2026-06-25: na dúvida, segurança sobre disponibilidade). 🟢
   - Origem no legado: princípio de erros barulhentos do mantenedor; `_reversa_sdd/domain.md#2.9`
   - Tipo: nova
5. **RN-05: Recuperação oficial para instalações presas no layout antigo.** Uma instalação que já rodou o código antigo e ficou presa (core órfão na raiz, nada em `.harness/harness-core/`) tem um caminho de recuperação suportado e documentado: rodar o `init` do upstream com caminho absoluto, que copia com o código novo e não compara versão. A documentação registra a remoção do `harness-core/` órfão (gitignored, não rastreado). 🟢
   - Origem no legado: `_reversa_sdd/adrs/0013-harness-core-modulo-per-projeto-footprint.md`
   - Tipo: nova
6. **RN-06: Não-destrutividade preservada.** A correção mantém o `upgrade`/`init` escrevendo apenas sob o repositório/`project_path` (footprint global zero, RN-N17) e preservando o estado versionado (`.reversa/`, `.harness/decisoes/`, `microdecisoes.md`, `estado-da-sessao.md`) intacto (RN-N20). 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.8` (RN-N17), `#2.9` (RN-N20)
   - Tipo: inalterada (invariante a respeitar)
7. **RN-07: Escape hatch `upgrade --force`.** O `upgrade` ganha uma flag `--force` que ignora a comparação de versão e força recópia do core + rematerialização (com o código novo, RN-01/RN-02). Útil após edição local ou drift, sem exigir o caminho absoluto do `init`. Escopo: só socorre instalações que **já** rodam o código novo; não substitui o `init` como recuperação das presas no código antigo. 🟢
   - Origem no legado: decisão de 2026-06-25; reforça `_reversa_sdd/domain.md#2.9` (RN-N20)
   - Tipo: nova

> **Decisão de escopo do Modo 2 (🟢, esclarecida em 2026-06-25):** a feature **não** implementa auto-migração do layout antigo (raiz `harness-core/` → `.harness/harness-core/`) dentro do `upgrade`. Esse caminho só dispararia quando o código novo já estivesse em execução — o que, por definição, não é o caso da instalação presa, que roda o código antigo. O escopo do Modo 2 é, portanto: (a) detecção de versão resiliente e barulhenta (RN-03/RN-04) para que uma **próxima** relocação não volte a fazer no-op silencioso; e (b) o `init` do upstream como recuperação oficial e documentada das instalações já presas (RN-05).

## 5. Requisitos Funcionais

| ID    | Requisito                                                                                      | Prioridade | Critério de aceite                                                                                                                                                                        | Confidência |
| ----- | ---------------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | `upgrade` materializa slash commands e `hooks.json` com o código recém-copiado                 | Must       | Teste de integração: upstream com materializador alterado; após `upgrade` o artefato produzido é o **novo**, não o stale                                                                  | 🟢          |
| RF-02 | Etapa de materialização pós-cópia uniformizada com o bootstrap (mesma garantia de código novo) | Must       | A materialização ocorre após `_copy_tree` usando o python+código de destino; nenhum materializador é chamado in-process sobre os módulos antigos                                          | 🟢          |
| RF-03 | Detecção de versão do upstream resiliente a mudança de layout                                  | Should     | Dado um upstream cujo core mudou de caminho, a leitura de versão ainda encontra a versão (via candidatos ou fonte alternativa) em vez de cair no fallback                                 | 🟡          |
| RF-04 | `upgrade` aborta barulhento (sem "Sucesso") quando a versão do upstream é indeterminada        | Must       | Dado um upstream cuja versão não pode ser lida nem por fontes resilientes, `upgrade` falha com erro claro, instrução de `init` e exit ≠ 0 — nunca imprime "Sucesso" nem copia às cegas    | 🟢          |
| RF-05 | Caminho de recuperação documentado para instalações presas no layout antigo                    | Must       | Documentação descreve `init` do upstream por caminho absoluto + remoção do órfão; seguir o passo a passo migra a instalação para `.harness/harness-core/` preservando o estado versionado | 🟢          |
| RF-06 | Regressão zero nos invariantes de footprint e não-destrutividade                               | Must       | `pytest` verde, incluindo footprint estendido; `.reversa/` e `.harness/decisoes/` intactos após `upgrade`                                                                                 | 🟢          |
| RF-07 | Flag `upgrade --force` ignora a comparação de versão e força recópia + rematerialização        | Should     | `./harness upgrade --force` recopia o core e rematerializa mesmo com versões iguais, usando o código novo (RF-01/RF-02); sem a flag, o comportamento de comparação de versão é preservado | 🟢          |

## 6. Requisitos Não Funcionais

| Tipo                  | Requisito                                                                                                                                                  | Evidência ou justificativa                                       | Confidência |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ----------- |
| Observabilidade       | Falha de upgrade (versão indeterminada, upstream inacessível, core ausente) produz log claro com instrução de recuperação; nunca falha silenciosa          | Princípio de erros barulhentos; `_reversa_sdd/domain.md#2.9`     | 🟢          |
| Reprodutibilidade     | Mesmo upstream + mesmo alvo → mesmo resultado de upgrade, independentemente da versão do core que executou o comando                                       | Elimina a dependência de estado em memória (Modo 1); RN-N20      | 🟢          |
| Manutenibilidade      | A etapa pós-cópia (bootstrap + materializadores) compartilha um único mecanismo de "rodar com o código novo", sem duplicar a lógica de re-exec/subprocesso | Alta coesão e baixo acoplamento; molde já existente no bootstrap | 🟡          |
| Segurança / Footprint | A correção não introduz nenhuma escrita fora do repositório/`project_path`                                                                                 | RN-N17 fixada por teste; `_reversa_sdd/domain.md#2.8`            | 🟢          |
| Compatibilidade       | A correção vale para os perfis Claude, Gemini e Antigravity sem ramificar serviço de domínio por harness                                                   | RN-N5/RN-N27/RN-N28; `_reversa_sdd/domain.md#2.11-2.12`          | 🟡          |

## 7. Critérios de Aceitação

```gherkin
Cenário: upgrade aplica a versão NOVA de um materializador (Modo 1)
  Dado um upstream cujo materializador de slash command foi alterado e a versão bumpada
  E um alvo já inicializado numa versão anterior
  Quando rodo ./harness upgrade no alvo
  Então o slash command materializado reflete o código novo do upstream
  E não reflete a versão antiga que estava carregada em memória

Cenário: upgrade aborta barulhento quando a versão do upstream é indeterminada (Modo 2)
  Dado um upstream em que a versão do core não pode ser lida nem por fontes resilientes
  Quando rodo ./harness upgrade
  Então o comando não imprime "Sucesso" e não copia nada
  E falha com instrução de recuperação via init e exit diferente de zero

Cenário: upgrade --force recopia e rematerializa mesmo com versões iguais
  Dado um alvo cuja versão coincide com a do upstream
  Quando rodo ./harness upgrade --force
  Então o core é recopiado e os artefatos são rematerializados com o código novo
  E o comando não conclui prematuramente por igualdade de versão

Cenário: recuperação de uma instalação presa no layout antigo (Modo 2)
  Dado um alvo com harness-core/ órfão na raiz e nada em .harness/harness-core/
  Quando rodo o init do upstream por caminho absoluto e removo o órfão
  Então o alvo passa a ter .harness/harness-core/src/main.py
  E .reversa/ e .harness/decisoes/ permanecem intactos
  E o wrapper ./harness executa sem erro de caminho

Cenário: não-destrutividade preservada (invariante)
  Dado um alvo com estado versionado em .harness/decisoes/ e .reversa/
  Quando rodo ./harness upgrade
  Então nenhuma escrita ocorre fora do repositório
  E o estado versionado permanece intacto
```

## 8. Prioridade MoSCoW

| Item                    | MoSCoW | Justificativa                                                                                      |
| ----------------------- | ------ | -------------------------------------------------------------------------------------------------- |
| RF-01, RF-02            | Must   | Núcleo do Modo 1; sem isso o upgrade continua propagando código stale                              |
| RF-04                   | Must   | Sem isso o upgrade segue podendo "fingir sucesso" — o sintoma mais perigoso do Modo 2              |
| RF-05                   | Must   | Recuperação das instalações já presas; é o desbloqueio imediato e de baixo risco                   |
| RF-06                   | Must   | Regressão zero em footprint e não-destrutividade é condição de aceite                              |
| RF-03                   | Should | Torna o upgrade resiliente a relayouts futuros; escopo do Modo 2 confirmado (sem auto-migração)    |
| RF-07                   | Should | `--force` é escape hatch barato e explícito; útil, mas não bloqueia a entrega do núcleo da feature |
| RNF de manutenibilidade | Should | Unificar a etapa pós-cópia reduz dívida, mas a feature entrega valor mesmo sem a unificação total  |

## 9. Esclarecimentos

### Sessão 2026-06-25

- **Q:** Até onde vai o escopo da correção do Modo 2 (upgrade fantasma após relocação de layout)?
  **R:** Resiliência futura + `init`. A feature torna a detecção de versão resiliente e barulhenta (RN-03/RN-04) e adota o `init` do upstream como recuperação oficial documentada das instalações já presas (RN-05). **Não** implementa auto-migração do layout antigo dentro do `upgrade` — esse caminho só rodaria com o código novo já ativo, o que não é o caso da instalação presa (ver decisão de escopo na seção 4).
- **Q:** Quando o upgrade não conseguir determinar a versão do upstream nem por fontes resilientes, o que ele faz?
  **R:** Aborta barulhento — erro claro, instrução de recuperação via `init` e exit ≠ 0 (RN-04/RF-04). Na dúvida, segurança sobre disponibilidade: não força a cópia às cegas nem finge sucesso.
- **Q:** Adicionar uma flag `upgrade --force` que ignora a comparação de versão e força recópia + rematerialização?
  **R:** Sim (RN-07/RF-07, prioridade Should). Escape hatch explícito para reidratar o core sem exigir o caminho absoluto do `init`. Ressalva registrada: só socorre instalações que já rodam o código novo.

## 10. Lacunas

> Nenhuma lacuna em aberto. As três dúvidas iniciais (escopo do Modo 2, comportamento na versão indeterminada e a flag `--force`) foram resolvidas na sessão de esclarecimentos de 2026-06-25 (ver seção 9).

## 11. Histórico de alterações

| Data       | Alteração                                                                                                                                                    | Autor   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| 2026-06-25 | Versão inicial gerada por `/reversa-requirements`                                                                                                            | reversa |
| 2026-06-25 | Três dúvidas resolvidas por `/reversa-clarify` (escopo do Modo 2 sem auto-migração, abortar barulhento na versão indeterminada, adicionar `upgrade --force`) | reversa |
