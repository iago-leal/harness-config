# Requirements: harness-core dentro de `.harness/` (footprint de um diretório na raiz)

> Identificador: `011-harness-core-em-dot-harness`
> Data: `2026-06-25`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Hoje toda instalação do harness deixa **dois diretórios** na raiz: `.harness/` (estado e decisões versionados) e `harness-core/` (o código do tool mais a `.venv`). Esta feature realoca `harness-core/` para **dentro** de `.harness/`, passando a `.harness/harness-core/`, de modo que a raiz passe a exibir um único diretório do harness. A mudança vale como **layout canônico único**: idêntico no repositório-fonte e no que `init`/`upgrade` produzem nos projetos-alvo. O wrapper `harness` permanece na raiz como ponto de entrada e passa a resolver o core no novo caminho. Nos projetos-alvo, a cópia vendored de `harness-core/` é gitignorada (regenerável por `upgrade`); no repositório-fonte ela continua versionada, por ser o código canônico do produto. O ganho atende ao mantenedor único intermitente: raiz limpa, layout simétrico entre fonte e instalação, e histórico do projeto-alvo livre do churn do código copiado.

## 2. Contexto a partir do legado

| Fonte                                                                 | Trecho relevante                                                                                                                                                                                                   | Confidência |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| `_reversa_sdd/inventory.md#raiz-do-projeto`                           | A raiz hoje contém o wrapper `harness` e o diretório `harness-core/`; `.harness/` guarda estado e decisões versionados — os dois diretórios que esta feature colapsa em um                                         | 🟢          |
| `_reversa_sdd/domain.md#wrapper-executavel`                           | O wrapper resolve a venv local (`harness-core/.venv/bin/python3`) e encaminha os argumentos para `harness-core/src/main.py` — caminhos que mudam com o move                                                        | 🟢          |
| `_reversa_sdd/domain.md#2.8` (RN-N17)                                 | Footprint global zero: instalar ou executar o harness escreve **apenas** dentro do repositório, nunca em diretório global; restrição fixada por teste                                                              | 🟢          |
| `_reversa_sdd/domain.md#2.9` (RN-N19, RN-N20)                         | `init` replica wrapper e core para o destino e cria a `.venv`; `upgrade` reescreve o core a partir do `upstream_path`, preservando `.reversa/` e `.harness/decisoes/`                                              | 🟢          |
| `_reversa_sdd/adrs/0013-harness-core-modulo-per-projeto-footprint.md` | `harness-core` é módulo per-projeto autocontido, "a um `git checkout` de distância de sumir e reaparecer" — propriedade que o gitignore no alvo tensiona e que esta feature precisa preservar com falha barulhenta | 🟢          |
| `_reversa_sdd/domain.md#2.11-2.12` (RN-N27, RN-N28)                   | `materialize_hooks_json` e `materialize_session_commands` escrevem sob `project_path`; precisam seguir corretos com o novo caminho do core                                                                         | 🟢          |

## 3. Personas e cenários de uso

| Persona                                      | Objetivo                                                            | Cenário-chave                                                                                                                    |
| -------------------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Mantenedor único intermitente                | Manter a raiz do projeto limpa e o setup retomável após meses       | Abre o repositório e vê um único diretório do harness (`.harness/`), em vez de dois soltos na raiz                               |
| Mantenedor instalando em projeto novo        | Inicializar o harness sem poluir a raiz nem o histórico git do alvo | Roda `./harness init <alvo>` e o alvo nasce com `.harness/harness-core/` gitignorado, não com `harness-core/` versionado na raiz |
| Agente de IA (Claude / Gemini / Antigravity) | Executar subcomandos do harness via wrapper                         | Invoca `./harness <subcomando>`; o wrapper resolve o core no novo caminho de forma transparente                                  |

## 4. Regras de negócio novas ou alteradas

1. **RN-01: Layout canônico único do core.** O `harness-core` reside em `.harness/harness-core/` em **qualquer** instalação do harness — repositório-fonte e projetos-alvo —, e não mais na raiz. 🟢
   - Origem no legado: `_reversa_sdd/inventory.md#raiz-do-projeto`, `_reversa_sdd/domain.md#wrapper-executavel`
   - Tipo: alterada (estrutura física)
2. **RN-02: Wrapper resolve o core no novo caminho.** O wrapper `harness` permanece na raiz e passa a apontar para `.harness/harness-core/.venv/bin/python3` e `.harness/harness-core/src/main.py`. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#wrapper-executavel`
   - Tipo: alterada
3. **RN-03: `init` e `upgrade` operam sobre `.harness/harness-core/` no alvo.** A replicação física do core (RN-N19) e a evolução não-destrutiva (RN-N20) passam a ter como destino `<alvo>/.harness/harness-core/`. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.9` (RN-N19, RN-N20)
   - Tipo: alterada
4. **RN-04: Footprint global zero preservado.** Toda escrita continua ocorrendo sob o repositório / `project_path`; a realocação não introduz nenhuma escrita fora do repositório (RN-N17 inalterada). 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.8` (RN-N17)
   - Tipo: inalterada (invariante a respeitar)
5. **RN-05: Gitignore da cópia vendored apenas no alvo.** Em projetos-alvo, `init` registra `.harness/harness-core/` no `.gitignore` do alvo, tornando o core uma cópia vendored não versionada e regenerável. No repositório-fonte, `.harness/harness-core/` permanece **versionado** por ser o código canônico. 🟡
   - Origem no legado: `_reversa_sdd/adrs/0013-harness-core-modulo-per-projeto-footprint.md` (footprint per-projeto, reprodutível e reversível)
   - Tipo: nova
6. **RN-06: Não-destrutividade do estado versionado.** A realocação não toca os artefatos versionados sob `.harness/` (`decisoes/`, `microdecisoes.md`, `estado-da-sessao.md`) nem `.reversa/`; eles permanecem rastreados e intactos (preserva RN-N20). 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.9` (RN-N20)
   - Tipo: inalterada (invariante a respeitar)
7. **RN-07: Falha barulhenta quando o core está ausente.** Com a cópia vendored gitignorada no alvo, um clone novo pode não conter `harness-core`. Nesse caso o wrapper deve falhar com mensagem clara, código de saída diferente de zero e instrução explícita de restauração (`upgrade`/`init` a partir do `upstream_path`). 🟡
   - Origem no legado: `_reversa_sdd/domain.md#2.9` (RN-N19, erros fail-fast amigáveis)
   - Tipo: nova (reforça o fail-fast existente para proteger a reprodutibilidade)

## 5. Requisitos Funcionais

| ID    | Requisito                                                                              | Prioridade | Critério de aceite                                                                                                                                          | Confidência |
| ----- | -------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | Realocar `harness-core/` para `.harness/harness-core/` no repositório-fonte            | Must       | Após a mudança não existe `./harness-core/` na raiz; existe `.harness/harness-core/src/main.py`; a suíte `pytest` segue verde                               | 🟢          |
| RF-02 | Wrapper `harness` (na raiz) resolve o core em `.harness/harness-core/`                 | Must       | `./harness format`, `./harness decisions` e demais subcomandos executam a partir da raiz sem erro de caminho                                                | 🟢          |
| RF-03 | `init` copia o core para `<alvo>/.harness/harness-core/`                               | Must       | Após `init` em um alvo limpo, existe `<alvo>/.harness/harness-core/src/main.py` e **não** existe `<alvo>/harness-core/`                                     | 🟢          |
| RF-04 | `upgrade` atualiza o core em `<alvo>/.harness/harness-core/`                           | Must       | Após `upgrade`, o conteúdo de `<alvo>/.harness/harness-core/` reflete o upstream; `.harness/decisoes/` e `.reversa/` permanecem intactos                    | 🟢          |
| RF-05 | `init` registra `.harness/harness-core/` no `.gitignore` do alvo, de forma idempotente | Must       | Após `init`, o `.gitignore` do alvo contém a linha; reexecutar `init`/`upgrade` não a duplica                                                               | 🟡          |
| RF-06 | No repositório-fonte, `.harness/harness-core/` permanece rastreado pelo git            | Must       | `git ls-files .harness/harness-core/` lista os arquivos-fonte do core (a `.venv` e caches seguem ignorados pelas regras existentes)                         | 🟢          |
| RF-07 | Wrapper falha com mensagem clara e exit ≠ 0 quando o core está ausente                 | Should     | Em um diretório sem `.harness/harness-core/`, `./harness` imprime instrução de restauração e encerra com código ≠ 0                                         | 🟡          |
| RF-08 | Materializadores e bootstrap funcionam com o novo caminho                              | Must       | `materialize_hooks_json`, `materialize_session_commands` e o bootstrap de ganchos Git operam sob o novo layout; `test_init.py` e `test_footprint.py` verdes | 🟢          |

## 6. Requisitos Não Funcionais

| Tipo                  | Requisito                                                                                                                                      | Evidência ou justificativa                                                                                                            | Confidência |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| Manutenibilidade      | Layout idêntico entre fonte e alvo, com wrapper copiável **verbatim** (sem reescrita de caminhos no momento da cópia)                          | Evita ramificar a lógica em "fonte vs alvo" — baixo acoplamento e menos dívida; `_reversa_sdd/domain.md#2.9`                          | 🟢          |
| Reprodutibilidade     | O alvo gitignorado deve ser reidratável por um único comando (`upgrade`/`init`), com `upstream_path` e `version` registrados no `harness.toml` | Preserva a propriedade "a um `git checkout` de distância de reaparecer" do ADR 0013 sob o novo modelo; `_reversa_sdd/adrs/0013-...md` | 🟡          |
| Observabilidade       | A ausência do core produz falha barulhenta com instrução de restauração (RN-07), nunca falha silenciosa                                        | Princípio de erros barulhentos do mantenedor; `_reversa_sdd/domain.md#2.9` (fail-fast)                                                | 🟡          |
| Segurança / Footprint | Nenhuma escrita fora do repositório / `project_path` é introduzida pela realocação ou pela edição do `.gitignore`                              | RN-N17 fixada por teste; `_reversa_sdd/domain.md#2.8`                                                                                 | 🟢          |
| Compatibilidade       | Ganchos (`.claude/settings.json`, `.gemini/settings.json`, `.agents/hooks.json`) e slash commands continuam válidos                            | Eles invocam `./harness` por caminho do wrapper, que permanece na raiz; `_reversa_sdd/domain.md#2.11-2.12`                            | 🟡          |

> **Decisão de escopo (🟢, esclarecida em 2026-06-25):** o wrapper `harness` permanece um **arquivo na raiz**; apenas o **diretório** `harness-core/` migra. Isso preserva a ergonomia `./harness` e todas as referências de ganchos e slash commands a `${CLAUDE_PROJECT_DIR}/harness` e `<ABS>/harness`, sem revisão.
>
> **Decisão técnica do `harness.toml` (🟢, esclarecida em 2026-06-25):** o `harness.toml` **operativo** permanece na raiz do projeto, lido cwd-relative por `load_config(fs, config_path="harness.toml")` como hoje; apenas o `harness-core/harness.toml` (template no fonte) acompanha o core para `.harness/harness-core/`. Nenhuma mudança em `load_config` nem nos call-sites.

## 7. Critérios de Aceitação

```gherkin
Cenário: Repositório-fonte após a realocação
  Dado o repositório-fonte do harness
  Quando o harness-core é movido para .harness/harness-core/
  Então a raiz não contém mais o diretório harness-core/
  E ./harness executa qualquer subcomando sem erro de caminho
  E os arquivos-fonte do core seguem versionados pelo git

Cenário: init em um projeto-alvo limpo
  Dado um diretório-alvo que é um repositório git válido e vazio de harness
  Quando rodo ./harness init <alvo>
  Então existe <alvo>/.harness/harness-core/src/main.py
  E não existe <alvo>/harness-core/
  E o .gitignore do alvo contém a linha .harness/harness-core/

Cenário: idempotência do gitignore no upgrade
  Dado um alvo já inicializado cujo .gitignore contém .harness/harness-core/
  Quando rodo ./harness upgrade no alvo
  Então a linha .harness/harness-core/ aparece uma única vez no .gitignore
  E .harness/decisoes/ e .reversa/ permanecem intactos

Cenário: falha barulhenta com o core ausente (caso negativo)
  Dado um alvo recém-clonado em que .harness/harness-core/ está ausente por estar gitignorado
  Quando rodo ./harness format arquivo.py
  Então o wrapper imprime uma instrução de restauração via upgrade/init
  E encerra com código de saída diferente de zero
```

## 8. Prioridade MoSCoW

| Item                     | MoSCoW | Justificativa                                                                                             |
| ------------------------ | ------ | --------------------------------------------------------------------------------------------------------- |
| RF-01, RF-02             | Must   | Sem o move e o wrapper ajustado a feature não existe                                                      |
| RF-03, RF-04             | Must   | O benefício precisa valer para instalações novas e existentes, não só para o repo-fonte                   |
| RF-05                    | Must   | O gitignore no alvo é o segundo pedido explícito; sem ele o churn de código vendored permanece            |
| RF-06                    | Must   | Garante que o repo-fonte não perca o código canônico ao adotar o novo layout                              |
| RF-08                    | Must   | Regressão zero nos materializadores e no footprint é condição de aceite                                   |
| RF-07                    | Should | Protege a reprodutibilidade do alvo gitignorado; o fail-fast já existe parcialmente e pode ser endurecido |
| RNF de reprodutibilidade | Should | Mitiga o trade-off do gitignore; restauração confirmada como `upgrade`/`init` do upstream (seção 9)       |

## 9. Esclarecimentos

### Sessão 2026-06-25

- **Q:** Posição do wrapper `harness` após o move do core para `.harness/harness-core/`?
  **R:** O wrapper permanece um arquivo na raiz; só o diretório do core migra. Preserva `./harness` e as referências dos ganchos e slash commands, sem revisão.
- **Q:** Com o core gitignorado no alvo, como deve ser a restauração quando ele estiver ausente (clone novo)?
  **R:** Único caminho de restauração = `upgrade`/`init` a partir do `upstream_path`. O wrapper, ao não achar o core, imprime esse comando e encerra com código ≠ 0 (RN-07). Aceita-se a dependência de o upstream host-local estar acessível.
- **Q:** Onde fica o `harness.toml` operativo no novo layout?
  **R:** Permanece na raiz, lido cwd-relative como hoje; só o `harness-core/harness.toml` (template) acompanha o core. `load_config` não muda.

## 10. Lacunas

> Nenhuma lacuna em aberto. As três dúvidas iniciais (posição do wrapper, reidratação do alvo gitignorado e descoberta do `harness.toml`) foram resolvidas na sessão de esclarecimentos de 2026-06-25 (ver seção 9).

## 11. Histórico de alterações

| Data       | Alteração                                                                                                          | Autor   |
| ---------- | ------------------------------------------------------------------------------------------------------------------ | ------- |
| 2026-06-25 | Versão inicial gerada por `/reversa-requirements`                                                                  | reversa |
| 2026-06-25 | Três dúvidas resolvidas por `/reversa-clarify` (wrapper na raiz, restauração via upstream, `harness.toml` na raiz) | reversa |
