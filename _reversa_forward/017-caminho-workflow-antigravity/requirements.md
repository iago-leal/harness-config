# Requirements: Corrige o caminho de materialização do workflow Antigravity

> Identificador: `017-caminho-workflow-antigravity`
> Data: `2026-06-27`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O slash command `/encerrar-sessao` que o Harness materializa para o Antigravity não é reconhecido nem pela IDE nem pelo CLI. A causa é o diretório de gravação: o Harness escreve o arquivo em `.agents/workflows/` (plural), enquanto o Antigravity registra workflows a partir de `.agent/workflows/` (singular). Esta feature corrige o caminho de materialização do artefato de workflow para o singular canônico, restaura o reconhecimento do comando e trata o arquivo órfão deixado no caminho antigo. O escopo limita-se ao artefato de workflow; os artefatos irmãos (rules, hooks) ficam fora, conforme decidido nos Esclarecimentos. A lógica de fechamento de sessão permanece intocada: o workflow apenas delega ao `CommandService` (RN-N5 preservada).

## 2. Contexto a partir do legado

| Fonte                                                                                                              | Trecho relevante                                                                                                                                                                                                                                                  | Confidência |
| ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `_reversa_sdd/comandos-customizados/requirements.md#f010`                                                          | A materialização de slash command de IDE grava `.claude/commands/encerrar-sessao.md` (Claude) e `.agents/workflows/encerrar-sessao.md` (Antigravity), "sempre os dois"; o arquivo apenas delega ao `CommandService`. O caminho **plural** está cristalizado aqui. | 🟢          |
| `_reversa_sdd/adrs/0017-comandos-ide-materializados-no-init.md`                                                    | Decisão de materializar os comandos de IDE no `init`/`upgrade`. Origem do artefato de workflow.                                                                                                                                                                   | 🟢          |
| `_reversa_sdd/domain.md#2.12` (RN-N28/RN-N29)                                                                      | Regra que prescreve a materialização do par de slash commands de sessão por harness.                                                                                                                                                                              | 🟢          |
| `.harness/harness-core/src/core/install/harness_profiles.py` (`AntigravityProfile.session_command_artifact`, L191) | Ponto exato do defeito: `return (".agents/workflows/encerrar-sessao.md", content)`.                                                                                                                                                                               | 🟢          |

### 2.1 Diagnóstico: hipóteses levantadas e veredito

O argumento pediu verificação da documentação oficial, hipóteses e proposta de fix. Registro o resultado da investigação, distinguindo as fontes externas (não pertencem ao `_reversa_sdd/`).

**Fontes externas consultadas (documentação oficial do Antigravity e instalação real na máquina):**

- Documentação oficial e dois guias de terceiros que a citam: workflows residem em `.agent/workflows/` (singular); "files anywhere else are ignored". Frontmatter exige apenas `description` (máx. 250 caracteres); corpo limitado a 12.000 caracteres.
- Glob literal do app instalado (`/Applications/Antigravity IDE.app`): o seletor do _Workflow Editor_ é `["**/.agent/workflows/**/*.md", "**/_agent/workflows/**/*.md", "**/.agents/workflows/**/*.md"]`.
- Evidência empírica no disco: dos workflows do usuário que funcionam, **todos** estão em `.agent/workflows/` (singular); os únicos em `.agents/` (plural) foram gerados por Harness/Reversa, e é justamente o `/encerrar-sessao` (plural) que não é reconhecido.

| #   | Hipótese                                                                                      | Veredito                       | Base                                                                                                                                                                                                                         |
| --- | --------------------------------------------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| H1  | Caminho errado: `.agents/workflows/` (plural) em vez de `.agent/workflows/` (singular).       | **CONFIRMADA — causa-raiz** 🟢 | `.agent/` (singular) está em todos os seletores da IDE e abriga 100% dos workflows funcionais do usuário; o artefato do Harness está em plural e não é reconhecido.                                                          |
| H2  | O loader de slash commands varre só o singular, embora o _editor_ de arquivo aceite o plural. | **PROVÁVEL** 🟡                | O glob de edição lista plural, mas nenhum workflow em plural funciona na prática. Distinção entre "abrir o `.md` no editor" e "registrar o comando" explica o sintoma. Não foi possível ler o código do loader (empacotado). |
| H3  | Frontmatter inválido: o arquivo traz `name:` além de `description:`.                          | **IMPROVÁVEL** 🟡              | A doc só exige `description`; `name` é tolerado. Mesmo assim, alinhar ao mínimo documentado reduz risco. Não é a causa-raiz.                                                                                                 |
| H4  | Nome do comando mal derivado (`/encerrar-sessao`).                                            | **DESCARTADA** 🟢              | O comando deriva do nome do arquivo (`encerrar-sessao.md` → `/encerrar-sessao`); está correto.                                                                                                                               |
| H5  | Estouro do limite de 12.000 caracteres do corpo.                                              | **DESCARTADA** 🟢              | O corpo materializado tem poucas centenas de caracteres.                                                                                                                                                                     |

**Conclusão:** a correção segura e à prova de versão é materializar o workflow em `.agent/workflows/` (singular) — o denominador comum reconhecido por IDE e CLI, em todas as versões observadas.

## 3. Personas e cenários de uso

| Persona                                   | Objetivo                                            | Cenário-chave                                                                                                          |
| ----------------------------------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Mantenedor no Antigravity IDE             | Encerrar a sessão pelo chat com `/encerrar-sessao`  | Após `init`/`upgrade` num projeto Antigravity, digita `/encerrar-sessao` e a IDE reconhece e executa o workflow.       |
| Mantenedor no Antigravity CLI             | Encerrar a sessão pelo CLI com `/encerrar-sessao`   | O CLI lê o mesmo diretório de workflows e reconhece o comando.                                                         |
| Mantenedor que atualiza projeto existente | Receber o caminho corrigido via `./harness upgrade` | O upgrade regrava o artefato no caminho singular e remove o órfão do caminho plural, sem tocar workflows de terceiros. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** O artefato de slash command do Antigravity para `encerrar-sessao` deve ser gravado em `.agent/workflows/encerrar-sessao.md` (singular). 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.12` (RN-N28/RN-N29) e `comandos-customizados/requirements.md#f010`, que hoje prescrevem o caminho plural.
   - Tipo: **alterada** (corrige o caminho previsto por RN-N28/RN-N29).
2. **RN-02:** A materialização (em `upgrade`, e em `init` sobre projeto previamente materializado) deve **remover** o artefato órfão `.agents/workflows/encerrar-sessao.md` deixado pelo caminho antigo, para que reste um único arquivo de workflow ativo. Remoção confirmada na sessão de esclarecimentos. 🟢
   - Tipo: **nova**.
3. **RN-03:** A limpeza do órfão é **não-destrutiva quanto a terceiros**: remove apenas o `encerrar-sessao.md` que o próprio Harness gera; nunca apaga outros workflows nem o diretório `.agents/workflows/` se ele contiver arquivos alheios. 🟢
   - Origem no legado: diretriz non-destructive já vigente no Reversa/Harness.
   - Tipo: **nova**.
4. **RN-04:** O frontmatter do workflow materializado expõe apenas `description` (o campo `name` é removido), aderindo ao mínimo documentado pela doc oficial do Antigravity. 🟢
   - Tipo: **nova**.

## 5. Requisitos Funcionais

| ID    | Requisito                                                   | Prioridade | Critério de aceite                                                                                                                                                                                                     | Confidência |
| ----- | ----------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | Materializar o workflow do Antigravity no caminho singular. | Must       | Após `init` em projeto com `active_harness == "antigravity"`, existe `.agent/workflows/encerrar-sessao.md` com o conteúdo do `AntigravityProfile`; **não** existe `.agents/workflows/encerrar-sessao.md` recém-criado. | 🟢          |
| RF-02 | Migrar projetos existentes via `upgrade`.                   | Must       | `./harness upgrade` num projeto que tinha o arquivo em `.agents/workflows/encerrar-sessao.md` passa a tê-lo em `.agent/workflows/encerrar-sessao.md` e remove o do caminho antigo.                                     | 🟢          |
| RF-03 | Preservar workflows de terceiros.                           | Must       | Se `.agents/workflows/` contém outros `.md`, eles permanecem intactos; apenas `encerrar-sessao.md` (gerado pelo Harness) é removido de lá.                                                                             | 🟢          |
| RF-04 | Propagação versionada.                                      | Should     | A correção é acompanhada de bump de versão do core, de modo que consumidores recebam o caminho novo via `./harness upgrade` (o upgrade regrava materializadores a partir do código novo).                              | 🟢          |
| RF-05 | Alinhar o frontmatter ao mínimo documentado.                | Could      | O workflow materializado mantém `description` e **remove** o campo `name`, aderindo à doc oficial (RN-04).                                                                                                             | 🟢          |

## 6. Requisitos Não Funcionais

| Tipo                       | Requisito                                                                                                                | Evidência ou justificativa                                                                                                                  | Confidência |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| Reprodutibilidade          | O caminho corrigido vale igualmente para `init` e `upgrade`; nenhum projeto fica preso ao caminho plural após atualizar. | Memória operacional: o upgrade regrava materializadores a partir do código em execução, logo a correção exige bump de versão para propagar. | 🟢          |
| Robustez (erro barulhento) | Falha ao gravar ou ao remover o artefato deve falhar de forma explícita, não silenciosa.                                 | Princípio do projeto: software que falha silencioso é dívida.                                                                               | 🟢          |
| Não-destrutividade         | A migração não apaga conteúdo alheio nem diretórios compartilhados.                                                      | Diretriz non-destructive do Reversa/Harness.                                                                                                | 🟢          |
| Compatibilidade            | O caminho escolhido (`.agent/` singular) é reconhecido por todas as versões observadas do Antigravity (IDE e CLI).       | Glob do app + evidência empírica.                                                                                                           | 🟢          |

## 7. Critérios de Aceitação

```gherkin
Cenário: init materializa o workflow no caminho reconhecido pelo Antigravity
  Dado um projeto com active_harness igual a "antigravity"
  Quando o init materializa os slash commands de sessão
  Então existe o arquivo .agent/workflows/encerrar-sessao.md
  E o frontmatter do arquivo expõe description e não expõe name
  E não foi criado .agents/workflows/encerrar-sessao.md

Cenário: upgrade migra o artefato órfão do caminho plural
  Dado um projeto Antigravity que possui .agents/workflows/encerrar-sessao.md gerado por versão anterior
  Quando o usuário roda ./harness upgrade
  Então passa a existir .agent/workflows/encerrar-sessao.md
  E .agents/workflows/encerrar-sessao.md deixa de existir

Cenário: a migração preserva workflows de terceiros
  Dado um projeto cujo .agents/workflows/ contém outro-workflow.md não gerado pelo Harness
  Quando o usuário roda ./harness upgrade
  Então outro-workflow.md permanece intacto em .agents/workflows/
  E apenas encerrar-sessao.md é removido daquele diretório

Cenário: o comando passa a ser reconhecido
  Dado o arquivo .agent/workflows/encerrar-sessao.md materializado
  Quando o usuário digita /encerrar-sessao no chat do Antigravity (IDE ou CLI)
  Então o workflow é reconhecido e conduz o encerramento da sessão
```

## 8. Prioridade MoSCoW

| Item                             | MoSCoW | Justificativa                                                                  |
| -------------------------------- | ------ | ------------------------------------------------------------------------------ |
| RF-01 (materializar no singular) | Must   | É o cerne da correção; sem ele o comando segue inexistente para o Antigravity. |
| RF-02 (migrar via upgrade)       | Must   | Sem migração, projetos já instalados (inclusive este) continuam quebrados.     |
| RF-03 (preservar terceiros)      | Must   | Apagar workflows alheios violaria a diretriz non-destructive.                  |
| RF-04 (bump de versão)           | Should | Mecanismo de propagação; sem ele o upgrade não regrava o caminho novo.         |
| RF-05 (frontmatter mínimo)       | Could  | Mitiga risco residual de parse; não é a causa-raiz.                            |

## 9. Esclarecimentos

### Sessão 2026-06-27

- **Q:** O fix deve cobrir só o workflow, ou também os artefatos irmãos que o `AntigravityProfile` grava em caminho plural — rules (`.agents/rules/estado-sessao.md`) e hooks (`.agents/hooks.json`)?
  **R:** Só o workflow (cirúrgico). Evidência: o app instalado aceita `.agent/rules/` e `.agents/rules/` (rules funcionam em plural por retrocompatibilidade) e os hooks não foram relatados como quebrados. Rules e hooks ficam fora do escopo desta feature; ver Lacunas só se reaparecerem como defeito.
- **Q:** No `upgrade` de um projeto já instalado, o que fazer com o arquivo órfão `.agents/workflows/encerrar-sessao.md`?
  **R:** Remover, de forma não-destrutiva (apaga apenas o `encerrar-sessao.md` gerado pelo Harness; nunca toca outros `.md` nem o diretório se houver arquivos de terceiros). Reflete em RN-02/RN-03 e RF-02/RF-03.
- **Q:** Manter ou remover o campo `name:` no frontmatter do workflow (hoje presente, a doc só exige `description`)?
  **R:** Remover `name:`, aderindo ao mínimo documentado e espelhando o perfil do Claude. Reflete em RN-04 e RF-05.

## 10. Lacunas

> Nenhuma lacuna pendente. As três dúvidas iniciais foram resolvidas na sessão de esclarecimentos de 2026-06-27.

## 11. Histórico de alterações

| Data       | Alteração                                                                                                                            | Autor   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| 2026-06-27 | Versão inicial gerada por `/reversa-requirements`                                                                                    | reversa |
| 2026-06-27 | Esclarecimentos integrados (escopo cirúrgico, remoção do órfão, remoção do `name`); marcadores de dúvida zerados; RN-04 acrescentada | reversa |
