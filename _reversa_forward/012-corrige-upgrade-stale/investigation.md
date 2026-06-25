# Investigação: Upgrade resiliente do harness-core

> Identificador: `012-corrige-upgrade-stale`
> Data: `2026-06-25`

## 1. Diagnóstico de fundo (observado em produção)

A feature nasce de um incidente real (2026-06-25, projeto-alvo `comentarios-ipm`): após `./harness upgrade`, o core ficou órfão na raiz (`harness-core/`, v1.2.46) e `.harness/harness-core/` permaneceu ausente, com a mensagem "Sucesso" impressa. A causa-raiz tem dois eixos independentes, ambos no `InitializationService`:

- **Eixo A — materialização stale.** Em `upgrade_project`, o `bootstrap` de ganchos Git roda via subprocesso do python de destino (passo 5, **não-stale**), mas os dois materializadores de IDE são chamados **in-process** (passos 6 e 7): `materialize_hooks_json` (gate Antigravity) e `materialize_session_commands` (sempre). Em-process significa "com os módulos Python que já estavam carregados quando o comando começou" — ou seja, o **código antigo**. Um `upgrade` que carrega a correção de um materializador regrava o artefato com a versão stale.
- **Eixo B — versão fantasma.** `_get_upstream_version` lê `config.py` em **um caminho fixo**. Quando o upstream relocou o core (feature 011, root → `.harness/harness-core/`), o código antigo do alvo procurava o caminho velho no upstream, não achava, e caía no fallback `return self.current_version`. Como `current_version` é a própria versão do código em execução, a comparação `upstream_version == local_version` dava verdadeira → `return` antecipado → cópia nenhuma + "Sucesso".

O Eixo B é, em parte, irreparável retroativamente: o código antigo já instalado nunca enxergará o novo layout. Por isso o escopo confirmado (requirements §9) separa **resiliência futura** (não repetir o no-op na próxima relocação) de **recuperação** das instalações já presas (via `init`).

## 2. Alternativas avaliadas

### 2.1 Materialização com código novo (Eixo A)

| Opção                                            | Prós                                                                                      | Contras                                                                                                   | Veredito      |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ------------- |
| **Subcomando interno via subprocesso** (D-01)    | Reusa o molde do `bootstrap`; processo real garante código novo; testável; footprint zero | Um subprocesso a mais por `upgrade`; exige venv de destino presente                                       | **Escolhida** |
| Re-exec `os.execv` do processo de upgrade        | Um único processo "novo" do começo ao fim                                                 | Substitui o processo: complica o `print("Sucesso")`, o exit code e a captura em teste; reentrância frágil | Descartada    |
| `importlib.reload` dos módulos de materialização | Sem subprocesso                                                                           | Não recarrega submódulos transitivos de forma confiável; estado de import compartilhado; frágil           | Descartada    |

Observação de DRY: a lógica de materialização vira uma função única; `init` a chama in-process (lá o código já é o do upstream, fresco) e `upgrade` a chama via subprocesso. Um só caminho de lógica, dois modos de invocação.

### 2.2 Detecção da versão do upstream (Eixo B)

| Opção                                                                     | Prós                                                                                          | Contras                                                                                                          | Veredito        |
| ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------- |
| **Caminhos-candidato (canônico + legado) + erro na ausência** (D-02/D-03) | Cobre a transição root→`.harness/`; elimina o fallback silencioso; fonte única em `layout.py` | Não cobre relayouts **arbitrários** futuros (só os conhecidos)                                                   | **Escolhida**   |
| Manifesto de versão em caminho estável na raiz do upstream                | Layout-independente de verdade                                                                | O repo-fonte não mantém `harness.toml` na raiz hoje; cria artefato novo e processo de manutenção; fora de escopo | Adiada (futuro) |
| Ler a versão via `git describe`/tag do upstream                           | Independe de caminho de arquivo                                                               | Acopla a um esquema de tags que o projeto não usa; o upstream pode não ter tag                                   | Descartada      |

A rede de segurança que torna a opção escolhida suficiente é o **abort barulhento** (RN-04): mesmo diante de um relayout não previsto, o `upgrade` não finge sucesso — ele para e manda rodar `init`.

### 2.3 Semântica de `--force` (RN-07)

- `--force` ignora a comparação de versão e força cópia + rematerialização. Com versão indeterminada, `--force` **não** aborta: copia mesmo assim e mantém o `version` existente no `harness.toml`, emitindo aviso. Racional: `--force` é uma afirmação explícita de "reidrate independentemente do que a versão diga".
- Limite registrado: `--force` só beneficia instalações que **já** rodam o código novo (o comando precisa existir). Não substitui o `init` para as presas no código antigo.

## 3. Padrões aplicáveis

- **Subprocess-as-fresh-code:** já consagrado no projeto pelo `bootstrap` dentro de `upgrade_project`; esta feature generaliza o padrão para a etapa de materialização.
- **Single source of truth de caminho:** `layout.py` já centraliza `CORE_REL_PATH` (feature 011); a lista de candidatos é a evolução natural do mesmo princípio.
- **Fail-fast / erros barulhentos:** alinhado ao princípio do mantenedor e a RN-N19 (erros fail-fast amigáveis no `init`).

## 4. Fontes

- `_reversa_forward/012-corrige-upgrade-stale/requirements.md` (RN/RF e esclarecimentos)
- `_reversa_sdd/domain.md#2.9` (RN-N20, RN-N21), `#2.11-2.12` (RN-N27, RN-N28)
- `_reversa_sdd/adrs/0014-bootstrap-e-evolucao-do-tooling.md`, `0017-comandos-ide-materializados-no-init.md`
- Código: `init_service.py` (`upgrade_project`, `_get_upstream_version`, `_copy_tree`), `main.py` (subparsers e dispatch de `upgrade`), `sync/service.py` (`check_version_update`), `install/session_commands.py`, `install/antigravity_hooks.py`, `domain/layout.py`
- Memória do projeto: registro do bug stale e do incidente de relayout (contexto de manutenção)
