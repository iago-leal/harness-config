# Spec Impact Matrix — harness-config

> Gerado pelo Architect em 2026-06-23
> Nível de Documentação: **Completo**

Esta matriz mapeia as relações de dependência e impacto entre as regras de negócio / requisitos do sistema e os componentes de software legados identificados nos módulos.

---

## 📊 Matriz de Impacto

A tabela abaixo cruza cada comportamento ou regra de negócio com o componente correspondente que o implementa e as possíveis consequências de alterações no código:

| Regra / Requisito | Componente Técnico | Código Origem | Severidade do Impacto em Caso de Mudança | Rastreabilidade / Efeito Cascata |
| :--- | :--- | :--- | :---: | :--- |
| **Garantia de Não-Bloqueio do Hook de Formatação** | `format-on-edit.sh` | [format-on-edit.sh:14](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh#L14) | **CRITICAL** | Bloquear a saída com status diferente de `0` trava e interrompe a gravação de progresso da IA, quebrando a usabilidade do editor. |
| **Proteção de Diretórios Pessoais e Configurações** | `format-on-edit.sh` | [format-on-edit.sh:38](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh#L38) | **HIGH** | Alterações nos vetores `DENY_PREFIXES` ou `NON_ROOT_DIRS` podem expor arquivos pessoais do usuário (`$HOME/Notas`) a formatações indesejadas e corrupção de conteúdo. |
| **Opt-out do Projeto (`.no-autoformat`)** | `format-on-edit.sh` | [format-on-edit.sh:111](file:///Users/iagoleal/dev/harness/harness-config/hooks/format-on-edit.sh#L111) | **MEDIUM** | Mudar a validação desse arquivo remove o controle do desenvolvedor humano sobre quais repositórios não devem sofrer formatação automatizada. |
| **Controle de TTL (Throttle) de Rede no Boot** | `sync-check.sh` | [sync-check.sh:20](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh#L20) | **HIGH** | Alterar ou desabilitar o TTL causa chamadas síncronas excessivas ao remote via `ls-remote` a cada inicialização da CLI do agente, resultando em lentidão extrema de boot. |
| **Alerta SessionStart Não-Obstrutivo** | `sync-check.sh` | [sync-check.sh:130](file:///Users/iagoleal/dev/harness/harness-config/bin/sync-check.sh#L130) | **HIGH** | Alterações no JSON de retorno impedem a CLI de injetar contexto ao agente, ocultando alertas importantes de bases defasadas ou trabalho pendente de push. |
| **Compilação de Relações e Backlinks de Decisões** | `gerar-index-decisoes.sh` | [gerar-index-decisoes.sh](file:///Users/iagoleal/dev/harness/harness-config/bin/gerar-index-decisoes.sh) | **MEDIUM** | Modificar a lógica do parser de relações inviabiliza a geração de backlinks e corrompe o índice navegável geral em `microdecisoes.md`. |
| **Bloqueio de Commits Manual no Pre-Commit** | `bootstrap.sh` | [bootstrap.sh:53](file:///Users/iagoleal/dev/harness/harness-config/bin/bootstrap.sh#L53) | **HIGH** | Alterações nesse gancho permitem commits inconsistentes no Git, quebrando a garantia de que as microdecisões e o código de infraestrutura evoluam sincronizados. |
| **Limite de Clarificações do Protocolo PCCP** | `clarificar.md` | [clarificar.md:39](file:///Users/iagoleal/dev/harness/harness-config/commands/clarificar.md#L39) | **MEDIUM** | Mudar ou remover a constante de limite máximo de rodadas expõe a IA e o desenvolvedor a loops infinitos de discussão conceitual de escopo. |
