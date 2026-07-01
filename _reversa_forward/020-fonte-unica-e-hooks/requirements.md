# Requirements: fonte única de execução (venv/core central) + materialização de hooks não-destrutiva

> Identificador: `020-fonte-unica-e-hooks`
> Data: `2026-07-01`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Hoje cada `harness init` replica fisicamente o `harness-core` no destino e cria uma `.venv` própria (RN-N19). Medição em `~/dev`: **17 instalações, ~108 MB de venv cada — ~1,83 GB, dos quais ~97 % são venvs duplicadas**; o código-fonte replicado soma ~3 MB por projeto. A feature colapsa essa duplicação numa **fonte única**: o `init` passa a instalar apenas um **shim** `harness` e a árvore de estado `.harness/`, e o core executável (código + venv) reside **exclusivamente no upstream**; o shim o executa com o cwd do projeto. Como o core já é cwd-relativo (`load_config("harness.toml")` relativo ao cwd; `os.getcwd()` no bootstrap), é troca de wrapper, não refatoração do core. Junto, corrige dois materializadores **destrutivos**: o merge dos hooks do Claude em `.claude/settings.json` (hoje substitui o array inteiro do evento, apagando hooks próprios do usuário) e a instalação dos hooks git (hoje sobrescreve `pre-commit`/`post-merge` incondicionalmente). Escopo travado via PCCP (mesma máquina, upstream sempre presente, sem clones alhures); trade-off aceito: todos os projetos seguem a HEAD única do upstream.

## 2. Contexto a partir do legado

| Fonte                                                                                                         | Trecho relevante                                                                                                                                                                                                                                                  | Confidência |
| ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `_reversa_sdd/domain.md#2.9` (RN-N19)                                                                         | `init` replica wrapper + core para o destino, inicializa uma `.venv` no destino e instala os ganchos git — origem da duplicação de disco.                                                                                                                         | 🟢          |
| `_reversa_sdd/domain.md#2.9` (RN-N20, RN-N21)                                                                 | `upgrade` recopia o core do upstream; `SyncService` faz checagem passiva de versão no boot. Ambos perdem sentido sob fonte única viva.                                                                                                                            | 🟢          |
| `_reversa_sdd/domain.md#2.8` (RN-N17) + `_reversa_sdd/adrs/0013-harness-core-modulo-per-projeto-footprint.md` | Footprint global zero: o core é módulo **per-projeto autocontido**; instalar/executar escreve **apenas** no repositório, nunca em `~/.claude`/`~/.agent-memory`. Esta feature **revisa parcialmente** a autocontenção física, preservando o footprint de escrita. | 🟢          |
| `_reversa_sdd/domain.md#2.9` (RN-N18)                                                                         | `harness.toml` registra `version` e `upstream_path` na seção `[harness]`. O `upstream_path` vira a **única** âncora; `version` é aposentado.                                                                                                                      | 🟢          |
| `_reversa_sdd/domain.md#2.7` (RN-N15)                                                                         | `install_hooks` grava `pre-commit`/`post-merge` **reescrevendo a cada execução** — origem do clobber de hooks git alheios.                                                                                                                                        | 🟢          |
| `_reversa_sdd/domain.md#2.11` (RN-N27)                                                                        | `materialize_hooks_json` (Antigravity) faz **merge por named-hook**, preservando terceiros — é o **padrão-modelo** que o merge do `settings.json` do Claude deve seguir por-item.                                                                                 | 🟢          |
| `_reversa_sdd/domain.md#2.13` (RN-N30)                                                                        | `apply_local_materializers` chama `materialize_claude_settings` só quando `active_harness == "claude"`; `init` in-process, `upgrade` via subprocesso. Removido o `upgrade`, resta o caminho in-process do `init` e o `materialize` avulso.                        | 🟢          |
| `.harness/harness-core/src/core/install/claude_settings.py`                                                   | Bug de merge intra-evento: `hooks[event] = value` (linha ~43) substitui o **array inteiro** de cada evento do harness, descartando itens próprios do usuário no mesmo evento. Chaves de topo e eventos de outro nome já são preservados.                          | 🟢          |
| `.harness/harness-core/src/core/bootstrap/init_service.py`                                                    | `initialize_project` (passos 3 e 7) copia o core e roda `python -m venv` + `pip install`; `upgrade_project`, `_get_upstream_version`, `UpstreamVersionUndeterminedError` a remover.                                                                               | 🟢          |
| `harness` (wrapper) + `.harness/harness-core/src/main.py`                                                     | Wrapper resolve caminhos **relativos ao próprio script**; `main.py` adiciona `src` ao `sys.path` por `__file__`. O shim passa a apontar para o core do upstream, mantendo o cwd no projeto.                                                                       | 🟢          |

## 3. Personas e cenários de uso

| Persona                                          | Objetivo                                                         | Cenário-chave                                                                                                                                               |
| ------------------------------------------------ | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mantenedor intermitente (iago)                   | Parar de gastar SSD com maquinaria duplicada a cada projeto novo | Roda `harness init` num projeto novo; nenhuma venv de ~108 MB é criada — o projeto ganha só o shim e passa a executar o core do upstream                    |
| Mantenedor com projeto que já tem hooks próprios | Instalar/atualizar o harness sem perder seus hooks de Claude/git | Tem um `PostToolUse` próprio no `settings.json` e um `pre-commit` próprio; após `init`/`materialize`, ambos continuam íntegros ao lado dos hooks do harness |
| Mantenedor migrando a base instalada             | Recuperar ~1,78 GB e uniformizar as 17 instalações existentes    | Roda a migração uma vez; as cópias de `.harness/harness-core/` somem, os shims são instalados, e o `livro-mfc` de layout duplo é normalizado                |

## 4. Regras de negócio novas ou alteradas

1. **RN-01: Fonte única de execução (revisa RN-N19).** O `init` deixa de copiar o `harness-core` e de criar `.venv` no alvo; instala apenas o **shim** `harness`, a árvore de estado `.harness/` (decisões, índice, estado-da-sessão) e as materializações de IDE. O core executável (código + venv) reside **exclusivamente no upstream**. 🟢
   - Origem no legado: revisa `_reversa_sdd/domain.md#2.9` (RN-N19) e a autocontenção física de `#2.8` (RN-N17). Tipo: alterada
2. **RN-02: Footprint de escrita global zero preservado (preserva RN-N17).** Executar o core do upstream **lê** de fora do repositório, mas toda **escrita** de estado permanece sob o `.harness/` do projeto (resolvido pelo cwd). Nada é escrito em `~/.claude`/`~/.agent-memory`; o upstream é o repositório-fonte **versionado**, não diretório do fornecedor — a preocupação original do ADR-0013 (não acoplar a layout de fornecedor; não criar estado global invisível/não-versionado) permanece atendida. O teste de footprint (`test_footprint.py`) continua válido. 🟢
   - Origem no legado: `_reversa_sdd/adrs/0013-...`, `#2.8` (RN-N17). Tipo: preservada (com autocontenção física relaxada por RN-01)
3. **RN-03: Shim resolve o upstream e força o cwd; falha barulhenta.** O wrapper `harness` do alvo lê `upstream_path` do `harness.toml`, faz `cd` para a raiz do projeto e executa `"$UPSTREAM/.harness/harness-core/.venv/bin/python3" "$UPSTREAM/.harness/harness-core/src/main.py" "$@"`. Core do upstream ausente/inacessível → erro nomeado, exit ≠ 0, com instrução — nunca execução silenciosa degradada. 🟢
   - Origem no legado: revisa o wrapper `harness` atual e RN-N19. Tipo: alterada
4. **RN-04: Isolamento por-projeto preservado.** Microdecisões (`.harness/decisoes/`), índice (`.harness/microdecisoes.md`), estado-da-sessão (`.harness/estado-da-sessao.md`) e `.git/hooks` permanecem por-projeto, resolvidos pelo cwd. O core compartilhado é **stateless** — cada invocação opera sobre o cwd de seu processo, sem cross-talk entre projetos. 🟢
   - Origem no legado: `#2.8`, `#2.3`; comprovado por `config.py#load_config` e `bootstrap/service.py#os.getcwd`. Tipo: preservada
5. **RN-05: Aposentadoria de upgrade/sync/version (revisa RN-N20, RN-N21, RN-N18).** Sob fonte única viva, o `upgrade` físico perde sentido. Removem-se `upgrade_project`, o `SyncService` e o alerta passivo de versão (RN-N21), `_get_upstream_version`/`UpstreamVersionUndeterminedError` e o campo `version` do `harness.toml`; `upstream_path` vira a única âncora. O subcomando `upgrade` **sobrevive como no-op barulhento** por transição: ao ser invocado, emite aviso claro ("fonte única — nada a atualizar; o core executa direto do upstream") e sai 0, sem recopiar nada. Não é removido do parser agora (os 17 projetos e a doc ainda o mencionam); a remoção definitiva fica para depois que a base estabilizar. 🟢
   - Origem no legado: revisa `#2.9` (RN-N20, RN-N21) e `#2.9` (RN-N18). Tipo: removida (semântica) / alterada (comando vira no-op)
6. **RN-06: Merge não-destrutivo dos hooks do Claude, por-item (alinha a RN-N27).** A materialização de `.claude/settings.json` passa a fazer merge **por-item dentro do array** de cada evento do harness (`SessionStart`, `PostToolUse`, `Stop`), não por-evento. Identifica o item do harness pela assinatura no `command` (contém `harness cmd resume` / `harness format` / `harness decisions`), **substitui** se presente / **insere** se ausente, e **preserva** todos os demais itens do array (hooks próprios do usuário no mesmo evento). Chaves de topo e eventos de outro nome seguem preservados. 🟢
   - Origem no legado: altera `claude_settings.py` (hoje `hooks[event] = value`); adota o padrão de merge de `#2.11` (RN-N27). Tipo: alterada
7. **RN-07: Hooks git não-destrutivos + via shim (altera RN-N15).** `install_hooks` deixa de sobrescrever incondicionalmente. Para cada um de `pre-commit`/`post-merge`: **ausente** → cria; **presente com** a assinatura `— Harness Core` → atualiza; **presente sem** a assinatura (hook alheio) → **preserva** o conteúdo do projeto (encadeia — ex.: move para `<hook>.local` e o invoca antes do trecho do harness), nunca o descarta. Os hooks passam a invocar o **shim** (`./harness format`, `./harness decisions`) em vez do python local, desacoplando-os do layout do core. 🟢
   - Origem no legado: altera `#2.7` (RN-N15). Tipo: alterada
8. **RN-08: Migração da base instalada.** Um mecanismo de migração converte as 17 instalações de `~/dev` do layout copiado para a fonte única: remove `.harness/harness-core/` (libera ~1,78 GB), instala o shim, reescreve os hooks git para o shim, re-materializa o `settings.json` com o merge de RN-06, e desmonta o layout **duplo** do `livro-mfc` (`harness-core/` legado na raiz + `.harness/harness-core/`). Não-destrutivo quanto ao estado (`.harness/decisoes`, `estado-da-sessao.md`) e a hooks/settings alheios. O mecanismo é um **subcomando versionado `harness migrate`** (não script one-shot): testável, reutilizável em instalações futuras e coeso com o core hexagonal. 🟢
   - Origem no legado: nova (operação de transição). Tipo: nova

## 5. Requisitos Funcionais

| ID    | Requisito                                                                                          | Prioridade | Critério de aceite                                                                                                                                                                     | Confidência |
| ----- | -------------------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | `init` instala shim + `.harness/` + materializações, **sem** copiar o core e **sem** criar `.venv` | Must       | Após `init` num repo limpo, não existe `.harness/harness-core/` nem `.venv` no alvo; existe o shim `harness` executável e o `.harness/` de estado                                      | 🟢          |
| RF-02 | O shim executa o core do upstream com o cwd do projeto                                             | Must       | `./harness bootstrap` (e demais comandos) rodam a partir do alvo e operam sobre o `.harness/`/`harness.toml` **daquele** projeto, usando o python/`main.py` do upstream                | 🟢          |
| RF-03 | O shim falha barulhento se o core do upstream não existir                                          | Must       | Com `upstream_path` inválido/ausente, `./harness <cmd>` imprime erro nomeado em stderr e sai com código ≠ 0; não executa nada degradado                                                | 🟢          |
| RF-04 | Remoção de `upgrade`/`SyncService`/`version`                                                       | Must       | `upgrade_project`, `sync/`, o alerta passivo e o campo `version` não existem mais; a suíte do core passa sem eles                                                                      | 🟢          |
| RF-05 | Merge do `settings.json` preserva itens alheios no mesmo evento                                    | Must       | Com um `PostToolUse` próprio já presente, `materialize`/`init` mantém esse item e adiciona/atualiza o do harness; chaves de topo e eventos de outro nome intactos                      | 🟢          |
| RF-06 | `install_hooks` preserva `pre-commit`/`post-merge` alheios                                         | Must       | Com um `pre-commit` sem assinatura do harness, a instalação preserva seu conteúdo (encadeado) e ainda ativa o hook do harness; um hook do harness antigo é atualizado no lugar         | 🟢          |
| RF-07 | Migração das 17 instalações libera disco e mantém funcionamento                                    | Must       | Após migrar, `.harness/harness-core/` some de cada projeto (~1,78 GB liberados), `./harness` funciona via upstream, e o `livro-mfc` fica com layout único                              | 🟢          |
| RF-08 | Auditoria de resolução por cwd antes de codar                                                      | Must       | Varredura de `core/documentation`, `core/commands`, `core/session` confirma que nenhum comando resolve caminho pelo local do script em vez do cwd (ou os pontos achados são ajustados) | 🟢          |
| RF-09 | Isolamento entre projetos sob fonte única                                                          | Should     | Dois projetos distintos executando o mesmo core do upstream escrevem cada um em seu próprio `.harness/`, sem interferência                                                             | 🟢          |

## 6. Requisitos Não Funcionais

| Tipo                          | Requisito                                                                                                                  | Evidência ou justificativa                                  | Confidência |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ----------- |
| Desempenho/Disco              | Consumo de SSD por instalação cai de ~108 MB para ~0 (só shim + estado); `init` deixa de rodar `pip install` (mais rápido) | Medição: 17 × ~108 MB ≈ 1,83 GB → ~108 MB fixos no upstream | 🟢          |
| Manutenibilidade/Coesão       | Menos superfície: remove `sync/`, `upgrade_project` e a lógica de versão; uma fonte de verdade                             | RN-05; `#2.9` (RN-N20/N21)                                  | 🟢          |
| Observabilidade               | Shim e materializadores falham barulhento (erro nomeado, exit ≠ 0), nunca em silêncio                                      | Espírito ruidoso do harness (`#2.15` RN-N33; RN-N4)         | 🟢          |
| Reprodutibilidade             | O lock (`requirements.txt` via `uv pip compile`) do upstream é a única fonte; determinismo mantido                         | `#2.10` (RN-N25)                                            | 🟢          |
| Segurança/Privacidade         | Nenhum arquivo ignorado é oferecido/tocado; migração não versiona estado sensível de terceiros                             | `list_dirty_paths` via porcelain; RN-08 não-destrutiva      | 🟢          |
| Portabilidade (limite aceito) | A execução depende do upstream local presente; sem clones em outra máquina (H1 travado)                                    | Decisão PCCP; contra explícito de RN-01/RN-03               | 🟡          |

## 7. Critérios de Aceitação

```gherkin
Cenário: init não cria venv nem copia o core
  Dado um repositório git limpo como alvo
  Quando rodo "harness init <alvo>"
  Então o alvo NÃO contém ".harness/harness-core/" nem ".venv"
  E o alvo contém um shim "harness" executável e a árvore ".harness/" de estado
  E o "harness.toml" registra "upstream_path" e não registra "version"

Cenário: shim executa o core do upstream com o cwd do projeto
  Dado um alvo inicializado no modo fonte única
  Quando executo "./harness bootstrap" a partir da raiz do alvo
  Então o comando roda com o python e o main.py do upstream
  E opera sobre o ".harness/" e o "harness.toml" do próprio alvo

Cenário: shim falha barulhento sem o core do upstream
  Dado um "harness.toml" cujo "upstream_path" não existe
  Quando executo "./harness cmd resume"
  Então nada é executado de forma degradada
  E o stderr contém um erro nomeado com instrução e o código de saída é diferente de zero

Cenário: merge do settings.json preserva hook próprio no mesmo evento
  Dado um ".claude/settings.json" com um item próprio em "PostToolUse"
  Quando rodo "harness materialize"
  Então o item próprio de "PostToolUse" permanece
  E o item do harness (command contém "harness format") é adicionado ou atualizado no mesmo array
  E as chaves de topo e os eventos de outro nome permanecem intactos

Cenário: install_hooks preserva pre-commit alheio
  Dado um ".git/hooks/pre-commit" sem a assinatura "— Harness Core"
  Quando a instalação de hooks roda
  Então o conteúdo do pre-commit do projeto é preservado (encadeado)
  E o comportamento do harness ("./harness format") também passa a rodar

Cenário negativo: migração não apaga estado nem hooks alheios
  Dado um projeto com decisões em ".harness/decisoes/" e um "commit-msg" próprio
  Quando rodo a migração para fonte única
  Então ".harness/harness-core/" é removido e o shim é instalado
  E ".harness/decisoes/" e o "commit-msg" próprio permanecem intocados
```

## 8. Prioridade MoSCoW

| Item                | MoSCoW | Justificativa                                                                                   |
| ------------------- | ------ | ----------------------------------------------------------------------------------------------- |
| RF-01, RF-02, RF-03 | Must   | Núcleo da fonte única — é a queixa (SSD) e o mecanismo que a resolve                            |
| RF-04               | Must   | Remover o que perde sentido evita código morto e comportamento contraditório                    |
| RF-05, RF-06        | Must   | Materializadores destrutivos são o segundo eixo travado; perda de hooks do usuário é dano real  |
| RF-07               | Must   | Sem migrar a base, os ~1,78 GB não são recuperados — é o objetivo prático                       |
| RF-08               | Must   | Pré-condição de segurança da RN-01: confirma que o core é cwd-relativo em todos os comandos     |
| RF-09               | Should | Isolamento é invariante a garantir, mas decorre de RN-04 (já comprovada nos comandos auditados) |

## 9. Esclarecimentos

### Sessão 2026-07-01

- **Q:** Sob fonte única, o subcomando `upgrade` deve ser removido do parser ou sobreviver como no-op barulhento por transição?
  **R:** Sobreviver como **no-op barulhento** por transição. Ao ser invocado, emite aviso claro ("fonte única — nada a atualizar; o core executa direto do upstream") e sai 0, sem recopiar nada. Não é removido agora porque os 17 projetos e a doc ainda o mencionam — evita confusão de hábito por um ciclo; a remoção definitiva fica para depois que a base estabilizar. Integrado em RN-05.
- **Q:** O mecanismo de migração das 17 instalações é um subcomando versionado `harness migrate` ou um script one-shot descartável?
  **R:** **Subcomando versionado `harness migrate`.** Testável, reutilizável em instalações futuras e coeso com o core hexagonal — alinhado a longevidade e reprodutibilidade; o one-shot economiza pouco e viraria dívida. Integrado em RN-08.

## 10. Lacunas

> Nenhuma lacuna pendente. As duas dúvidas iniciais (destino do `upgrade`, mecanismo de migração) foram resolvidas na sessão de esclarecimentos de 2026-07-01 (§9).

## 11. Histórico de alterações

| Data       | Alteração                                                                                                                         | Autor   |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------- | ------- |
| 2026-07-01 | Versão inicial gerada por `/reversa-requirements` (escopo travado via PCCP nos 4 itens)                                           | reversa |
| 2026-07-01 | Sessão de esclarecimentos: 2 dúvidas resolvidas (`/reversa-clarify`) — RN-05 no-op barulhento, RN-08 `harness migrate` versionado | reversa |
