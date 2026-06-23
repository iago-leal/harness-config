# Comandos Customizados, Requisitos (Requirements)

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**
> Rastreabilidade ao Legado: [commands/](file:///Users/iagoleal/dev/harness/harness-config/commands/)

## Visão Geral
Define e estende as capacidades e instruções de ciclo de vida da interface de linha de comando dos agentes de IA (Claude Code / Gemini CLI) por meio de slash commands customizados (comandos de barra) mapeados em arquivos Markdown, padronizando tarefas de clarificação de escopo, fechamento de sessão e handoff semântico de tarefas.

## Responsabilidades
* Guiar o agente na condução do processo de clarificação de demandas complexas (protocolo PCCP). 🟢
* Automatizar a consolidação do progresso e o fechamento íntegro de sessões locais de desenvolvimento. 🟢
* Fornecer o mecanismo de passagem (handoff) e retomada (resume) do bastão de tarefas entre diferentes agentes de IA. 🟢

## Regras de Negócio
* **Teto de Rodadas de Clarificação:** O processo de clarificação de escopo de demandas complexas (PCCP) é limitado estritamente a 2 interações para mitigar paralisia conceitual. 🟢 [clarificar.md:39](file:///Users/iagoleal/dev/harness/harness-config/commands/clarificar.md#L39)
* **Precedência de Travamento:** A geração do plano técnico e codificação de uma demanda complexa exige o travamento explícito dos requisitos pelo usuário humano (`/travar`) ou a hipótese de lacuna mínima em caso de esgotamento de rodadas. 🟢 [clarificar.md:42](file:///Users/iagoleal/dev/harness/harness-config/commands/clarificar.md#L42)
* **Isolamento de Diretório no Fechamento:** O comando de encerramento de sessão deve restringir commits e atualizações apenas dentro da árvore física da raiz do repositório ativo. 🟢 [encerrar-sessao.md:11](file:///Users/iagoleal/dev/harness/harness-config/commands/encerrar-sessao.md#L11)
* **Âncora de Integridade Git:** Toda finalização de sessão deve carregar e gravar o hash SHA-1 do HEAD ativo do Git no `ESTADO-DA-SESSAO.md` para servir como validação contra divergências conceituais na inicialização subsequente. 🟢 [encerrar-sessao.md:22](file:///Users/iagoleal/dev/harness/harness-config/commands/encerrar-sessao.md#L22) (inferido a partir do commit `2266801`)

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
| :--- | :--- | :---: | :--- |
| **RF-01** | Comando `/clarificar`. | Must | Processar demandas sob o protocolo PCCP mapeando Fatos (F), Inferências (I) e Hipóteses/Lacunas (H). |
| **RF-02** | Comando `/encerrar-sessao`. | Must | Automatizar commits incrementais, rodar o indexador de microdecisões, propagar ganchos locais e registrar o estado do repositório. |
| **RF-03** | Comandos `/handoff` e `/resume`. | Must | Gravar/ler dados do arquivo físico `BASTAO.md` e executar scripts auxiliares de commits locais na pasta de memória comum. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
| :--- | :--- | :--- | :---: |
| Portabilidade | Uso de caminhos portáveis de ambiente baseados em `~/` e variáveis de ambiente Unix. | `encerrar-sessao.md:099d9a0` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que a IA identificou lacunas (H) ao analisar uma nova demanda complexa
Quando o comando /clarificar for acionado
Então ele deve classificar as dúvidas em blocos e aguardar as respostas do desenvolvedor, aceitando o comando /travar.

Dado que o agente concluiu suas tarefas de desenvolvimento na sessão ativa
Quando o comando /encerrar-sessao for executado
Então ele deve realizar commits das alterações locais, reindexar as microdecisões e registrar o commit HEAD no arquivo ESTADO-DA-SESSAO.md.
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
| :--- | :---: | :--- |
| Fechamento e consolidação de sessão | Must | Garante integridade histórica dos dados e evita perda de contexto. |
| Protocolo PCCP com teto de rodadas | Must | Impede consumo excessivo de tokens e loop de diálogo inútil. |
| Handoff sem rede | Should | Importante para sincronia cross-agent de forma robusta e descentralizada. |
