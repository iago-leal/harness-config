# Requirements: Ganchos de ciclo de vida para o Antigravity

> Identificador: `009-hooks-antigravity`
> Data: `2026-06-24`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Hoje o harness emite ganchos de ciclo de vida para Claude Code (bloco `hooks` completo) e descreve a ponte do Gemini, mas para o Antigravity o perfil de instalação é apenas um aviso de "mecanismo não confirmado". Esta feature fecha essa lacuna: faz o harness produzir, instalar e documentar ganchos reais executáveis pelo Antigravity, para que as três automações já existentes — reinjeção de estado de sessão, formatação ao editar e indexação de microdecisões — passem a disparar também sob esse agente. O contrato de ganchos do Antigravity agora está documentado oficialmente, o que torna a implementação possível sem suposição.

## 2. Contexto a partir do legado

| Fonte                                                                                             | Trecho relevante                                                                                                                                                                                                                                                                                                                                       | Confidência |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| `_reversa_sdd/architecture.md#4-integrações-de-borda`                                             | Os ganchos `SessionStart`/`PostToolUse`/`Stop` (Claude) e `SessionStart` (Gemini) invocam o wrapper `./harness`; é a borda de integração que esta feature estende ao Antigravity.                                                                                                                                                                      | 🟢          |
| `_reversa_sdd/inventory.md#configuração-de-ganchos-por-harness`                                   | A configuração de ganchos vive por harness: `.claude/settings.json` e `.gemini/settings.json`. Falta o arquivo equivalente do Antigravity.                                                                                                                                                                                                             | 🟢          |
| `_reversa_sdd/adrs/0011-reinjecao-multi-harness-strategy-sink.md`                                 | Strategy multi-harness: `HookContextSink` (Claude/Gemini) e `FileProjectionSink` (Antigravity → `.agents/rules/estado-sessao.md`). O sink do Antigravity já existe; o **perfil de ganchos** ainda é placeholder.                                                                                                                                       | 🟢          |
| `_reversa_sdd/adrs/0002-formatacao-automatica-post-tool-use.md`                                   | A formatação ao editar nasce do gancho `PostToolUse` (matcher `Write\|Edit`) chamando `harness format`, sempre não-bloqueante.                                                                                                                                                                                                                         | 🟢          |
| `_reversa_sdd/adrs/0015-reprodutibilidade-e-configuracoes-dinamicas-de-formatacao.md`             | A formatação é configurável por `[formatting]` (opt-out e exclude_paths dinâmicos); o gancho do Antigravity deve preservar esse comportamento.                                                                                                                                                                                                         | 🟢          |
| `_reversa_sdd/architecture.md#6-adrs-pertinentes` (MD-0005)                                       | Footprint global zero: instalar/rodar o harness escreve só dentro do repositório-alvo, nunca em `~`. Restringe ONDE o `hooks.json` do Antigravity pode ser gravado.                                                                                                                                                                                    | 🟢          |
| Documentação oficial do Antigravity — `https://antigravity.google/docs/hooks` (lida nesta sessão) | Contrato `hooks.json`: eventos `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`; handler `{type:"command", command, timeout=30}`; I/O por stdin/stdout JSON camelCase; campos comuns `conversationId`, `workspacePaths`, `transcriptPath`, `artifactDirectoryPath`. Localização: `.agents/` no workspace ou `~/.gemini/config/`. | 🟢          |

> Nota de fonte externa: o contrato do Antigravity não nasce do `_reversa_sdd/` (é sistema de terceiro), mas é a referência normativa desta feature. Foi capturado da página oficial renderizada e do README do SDK Python durante esta sessão.

## 3. Personas e cenários de uso

| Persona                                          | Objetivo                                                                                      | Cenário-chave                                                                                                     |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Mantenedor único (instala o harness num projeto) | Inicializar um repositório escolhendo o Antigravity como agente e receber ganchos prontos     | Roda `./harness init <destino> --harness antigravity` e obtém um `hooks.json` válido sem precisar montá-lo à mão. |
| Desenvolvedor usando o Antigravity no dia a dia  | Que o estado de sessão, a formatação e as decisões funcionem como já funcionam no Claude      | Edita um arquivo no Antigravity e o harness o formata automaticamente, sem ação manual.                           |
| Mantenedor do harness                            | Eliminar o placeholder de "mecanismo não confirmado" e ter paridade verificável entre engines | Lê o `install-prompt` para Antigravity e recebe um bloco colável real em vez de um aviso.                         |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** O perfil de instalação do Antigravity passa a emitir um `hooks.json` válido (em vez do aviso de placeholder), cobrindo os ganchos de ciclo de vida do harness. 🟢
   - Origem no legado: `_reversa_sdd/adrs/0011-reinjecao-multi-harness-strategy-sink.md` (pendência registrada)
   - Tipo: alterada (substitui o comportamento-placeholder atual)
2. **RN-02:** A formatação ao editar, sob o Antigravity, é disparada por `PostToolUse` com `matcher` casando as ferramentas de escrita do Antigravity (`write_to_file`, `replace_file_content`, `multi_replace_file_content`), preservando o caráter não-bloqueante e a configuração viva de `[formatting]`. 🟢
   - Origem no legado: `_reversa_sdd/adrs/0002-formatacao-automatica-post-tool-use.md`, `_reversa_sdd/adrs/0015-reprodutibilidade-e-configuracoes-dinamicas-de-formatacao.md`
   - Tipo: alterada (mesmo efeito, gatilho e matcher específicos do Antigravity)
3. **RN-03:** A indexação de microdecisões, sob o Antigravity, é disparada pelo evento `Stop`, chamando o equivalente a `harness decisions`. 🟢
   - Origem no legado: `_reversa_sdd/architecture.md#4-integrações-de-borda`
   - Tipo: alterada (mesmo efeito, evento nativo do Antigravity)
4. **RN-04:** O `hooks.json` do Antigravity é gravado **dentro do projeto-alvo** (diretório `.agents/`), nunca no diretório global do usuário (`~/.gemini/config/`), em conformidade com o footprint global zero. 🟢
   - Origem no legado: `_reversa_sdd/architecture.md#6-adrs-pertinentes` (MD-0005, BR-MIGRAR-007)
   - Tipo: nova
5. **RN-05:** A reinjeção de estado de sessão sob o Antigravity permanece coberta exclusivamente pelo `FileProjectionSink` já existente (projeção em `.agents/rules/estado-sessao.md`). **Nenhum** gancho de ciclo de vida é adicionado para isso no MVP, para não duplicar uma responsabilidade já resolvida e testada (evita a classe de divergência da dívida histórica T2). 🟢
   - Origem no legado: `_reversa_sdd/adrs/0011-reinjecao-multi-harness-strategy-sink.md`
   - Tipo: nova (decidida em `/reversa-clarify`, sessão 2026-06-24)
6. **RN-06:** A tradução do protocolo de ganchos do Antigravity — tanto a entrada (stdin JSON → alvo/invocação) quanto a saída (resultado → stdout JSON por evento) — vive numa **camada de adaptação de borda** instalada junto dos ganchos, mantendo os comandos do core (`harness format`, `harness decisions`) agnósticos ao harness. 🟢
   - Origem no legado: `_reversa_sdd/adrs/0011-reinjecao-multi-harness-strategy-sink.md` (Strategy multi-harness; sem `if`s de harness no core)
   - Tipo: nova (decidida em `/reversa-clarify`, sessão 2026-06-24)

## 5. Requisitos Funcionais

| ID    | Requisito                                                                                                                                                                                                                                                                                                         | Prioridade | Critério de aceite                                                                                                                                                    | Confidência |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | O perfil de instalação do Antigravity deve produzir um bloco `hooks.json` sintaticamente válido e colável, no lugar do aviso de placeholder atual.                                                                                                                                                                | Must       | `install-prompt` com harness ativo `antigravity` retorna JSON que parseia sem erro e contém ao menos os ganchos de formatação e de decisões.                          | 🟢          |
| RF-02 | O bloco deve definir `PostToolUse` com `matcher` casando as ferramentas de escrita do Antigravity e `command` apontando para o wrapper `./harness` do projeto.                                                                                                                                                    | Must       | O `matcher` resultante casa `write_to_file`, `replace_file_content` e `multi_replace_file_content`, e o `command` referencia o `./harness` do projeto-alvo.           | 🟢          |
| RF-03 | O bloco deve definir `Stop` chamando a indexação de microdecisões.                                                                                                                                                                                                                                                | Must       | Existe um handler sob `Stop` cujo `command` dispara o equivalente a `harness decisions`.                                                                              | 🟢          |
| RF-04 | A instalação (`./harness init --harness antigravity`) deve materializar o `hooks.json` no diretório `.agents/` do projeto-alvo, sem escrever fora do repositório.                                                                                                                                                 | Must       | Após `init`, existe `<destino>/.agents/hooks.json` válido e nenhum arquivo é criado em `~`.                                                                           | 🟢          |
| RF-05 | Os comandos disparados pelos ganchos devem honrar o contrato de I/O do Antigravity (entrada por stdin JSON, saída por stdout no formato esperado por evento), sem quebrar o laço de execução do agente. A tradução desse protocolo vive na camada de adaptação de borda (RN-06), com o core agnóstico ao harness. | Must       | Para um payload `PostToolUse` de exemplo no stdin, o comando termina sem erro e a saída não interrompe o laço; ganchos não-bloqueantes não emitem `decision: "deny"`. | 🟡          |
| RF-06 | A formatação ao editar, sob o Antigravity, deve continuar respeitando `formatting.opt_out_file` e `formatting.exclude_paths` do `harness.toml`.                                                                                                                                                                   | Must       | Um arquivo coberto por `exclude_paths` não é formatado quando o gancho dispara sob o Antigravity.                                                                     | 🟢          |
| RF-07 | As instruções de aplicação (`apply_instructions`) do Antigravity devem descrever onde colar o `hooks.json` e deixar de exibir o aviso de "mecanismo não confirmado".                                                                                                                                              | Should     | O texto retornado não contém o aviso de placeholder e indica o caminho `.agents/hooks.json`.                                                                          | 🟢          |
| RF-08 | A paridade de comportamento entre Claude e Antigravity para formatação e decisões deve ser verificável por teste automatizado.                                                                                                                                                                                    | Should     | Há teste cobrindo o perfil do Antigravity análogo ao do Claude, parte da suíte verde.                                                                                 | 🟡          |

## 6. Requisitos Não Funcionais

| Tipo                          | Requisito                                                                                                                           | Evidência ou justificativa                                                                                                                                                       | Confidência |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| Footprint / Reprodutibilidade | A geração e a instalação do `hooks.json` não podem escrever fora do repositório-alvo.                                               | MD-0005 / BR-MIGRAR-007 em `_reversa_sdd/architecture.md#6-adrs-pertinentes`; contrato fixado por `tests/test_footprint.py`.                                                     | 🟢          |
| Robustez                      | Ganchos de formatação e decisão devem ser não-bloqueantes: falha do comando não pode abortar o laço do agente.                      | `_reversa_sdd/adrs/0002-formatacao-automatica-post-tool-use.md` (sempre exit 0); o Antigravity interpreta `decision: "deny"` como bloqueio, que deve ser evitado nesses ganchos. | 🟢          |
| Observabilidade               | Falhas dos ganchos devem ser visíveis (erro barulhento em log), nunca silenciosas a ponto de mascarar quebra de contrato.           | Preferência operacional do mantenedor (erros barulhentos > performance).                                                                                                         | 🟡          |
| Manutenibilidade              | A emissão do `hooks.json` deve seguir a abstração Strategy já existente (`HarnessProfile`), sem `if`s de harness espalhados.        | `_reversa_sdd/adrs/0011-reinjecao-multi-harness-strategy-sink.md`; perfis em `harness_profiles.py`.                                                                              | 🟢          |
| Portabilidade                 | O `command` dos ganchos deve resolver o wrapper do projeto sem depender de variável específica do Claude (`${CLAUDE_PROJECT_DIR}`). | O perfil do Claude usa `${CLAUDE_PROJECT_DIR}`; o Antigravity expõe `workspacePaths` no payload, não essa variável.                                                              | 🟡          |

## 7. Critérios de Aceitação

```gherkin
Cenário: Instalação gera hooks.json do Antigravity no projeto
  Dado um repositório-alvo com git inicializado
  Quando rodo "./harness init <destino> --harness antigravity"
  Então existe o arquivo "<destino>/.agents/hooks.json"
  E o JSON parseia sem erro
  E nenhum arquivo é criado fora do repositório-alvo

Cenário: Prompt de instalação do Antigravity não exibe mais placeholder
  Dado o harness ativo configurado como "antigravity"
  Quando solicito o install-prompt
  Então o bloco de ganchos é um hooks.json válido
  E o texto não contém o aviso "mecanismo de ganchos do antigravity ainda não confirmado"

Cenário: Formatação ao editar dispara sob o Antigravity
  Dado um hooks.json do Antigravity instalado
  E um arquivo de código fora de "exclude_paths"
  Quando o evento PostToolUse de uma ferramenta de escrita dispara
  Então o arquivo editado é formatado pelo formatador correspondente

Cenário (negativo): Arquivo excluído não é formatado
  Dado um arquivo coberto por "formatting.exclude_paths"
  Quando o gancho PostToolUse dispara sob o Antigravity
  Então o arquivo não é formatado
  E o gancho termina sem bloquear o laço do agente

Cenário (negativo): Gancho não-bloqueante não interrompe o agente
  Dado um gancho de formatação que falha ao executar o formatador
  Quando o evento PostToolUse dispara
  Então o laço de execução do Antigravity continua normalmente
  E a falha é registrada de forma visível
```

## 8. Prioridade MoSCoW

| Item             | MoSCoW | Justificativa                                                                        |
| ---------------- | ------ | ------------------------------------------------------------------------------------ |
| RF-01            | Must   | Sem o bloco válido, não há feature; substitui o placeholder.                         |
| RF-02            | Must   | A formatação é o gancho de maior valor diário e exige o matcher correto.             |
| RF-03            | Must   | Indexação de decisões é parte do contrato de ciclo de vida já existente.             |
| RF-04            | Must   | Footprint zero é princípio inegociável do projeto.                                   |
| RF-05            | Must   | Honrar o contrato de I/O é o que torna o gancho de fato executável pelo Antigravity. |
| RF-06            | Must   | Regressão de formatação dinâmica seria perda de comportamento já entregue.           |
| RF-07            | Should | Melhora a experiência de instalação, mas não bloqueia o funcionamento.               |
| RF-08            | Should | Garante a paridade no tempo, mas o valor entra mesmo sem o teste no MVP.             |
| RNF de footprint | Must   | Restringe onde o arquivo pode ser escrito.                                           |
| RNF de robustez  | Must   | Gancho que aborta o agente é pior que gancho ausente.                                |

## 9. Esclarecimentos

### Sessão 2026-06-24

As três respostas foram delegadas pelo mantenedor à recomendação do esclarecedor, sob as prioridades declaradas: longevidade, manutenibilidade e dívida técnica mínima — alta coesão, baixo acoplamento, OOP, TDD e SDD.

- **Q:** O Antigravity não tem evento `SessionStart`, e a reinjeção de estado já é coberta pelo `FileProjectionSink`. Quais ganchos entram no MVP?
  **R:** Formatação (`PostToolUse`) + decisões (`Stop`). A reinjeção de estado permanece exclusivamente com o `FileProjectionSink`. _Porquê:_ um `PreInvocation` para reinjetar estado duplicaria responsabilidade já resolvida e testada (ADR 0011), recriando a classe de divergência da dívida histórica T2; `SessionStart` não tem evento nativo no Antigravity, e forçar análogo é inventar superfície. → Resolve RN-05.

- **Q:** O `PostToolUse` do Antigravity não traz o caminho do arquivo editado (só `stepIdx`/`error`). Como o `harness format` obtém o alvo?
  **R:** Camada de adaptação de borda instalada em `.agents/`, que traduz o evento do Antigravity numa invocação `harness format <path>` pela interface de argumento de CLI já existente. _Porquê:_ ler o `transcript.jsonl` ou ramificar o comando por harness acoplaria o domínio a um formato frágil de terceiro; a tradução de protocolo pertence ao adaptador (arquitetura hexagonal), deixando `FormattingService`/`resolve_format_target` intactos. → Resolve RN-06.

- **Q:** O Antigravity espera stdout JSON por evento (`{}` no `PostToolUse`; `decision` no `Stop`). Como honrar o contrato?
  **R:** A mesma camada de adaptação de borda da resposta anterior envelopa o resultado dos comandos no JSON esperado por evento. _Porquê:_ o contrato de fio é concern de fronteira; mantê-lo fora do core evita os `if`s de harness espalhados que a Strategy do ADR 0011 nasceu para eliminar. As duas dúvidas técnicas colapsam num único adaptador coeso que traduz os dois sentidos (entrada e saída). → Resolve RN-06.

## 10. Lacunas

> Nenhuma lacuna aberta. Todos os `[DÚVIDA]` da versão inicial foram resolvidos na sessão de esclarecimentos acima.

**Diferido ao plano (detalhe de desenho, não dúvida de requisito):** a estratégia exata pela qual a camada de adaptação descobre o caminho do arquivo editado (ler o `transcriptPath` no `stepIdx` versus formatar o diff do workspace no `Stop`) é decisão de `/reversa-plan`, e fica isolada dentro do adaptador de borda.

## 11. Histórico de alterações

| Data       | Alteração                                             | Autor   |
| ---------- | ----------------------------------------------------- | ------- |
| 2026-06-24 | Versão inicial gerada por `/reversa-requirements`     | reversa |
| 2026-06-24 | 3 dúvidas resolvidas em `/reversa-clarify` (sessão 1) | reversa |
