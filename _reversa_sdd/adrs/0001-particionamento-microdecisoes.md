# ADR 0001: Particionamento de Microdecisões de Design

* **Status:** Aceito
* **Data:** 2026-06-21
* **Contexto Técnico:** Módulo `decisoes`
* **Escala de Confiança:** 🟢 CONFIRMADO

## Contexto e Problema

Anteriormente, as microdecisões de design e arquitetura eram registradas em um único arquivo monolítico (`microdecisoes.md`). Conforme o volume de decisões cresceu, esse arquivo único tornou-se difícil de gerenciar, propenso a conflitos de mesclagem (merge conflicts) entre sessões paralelas de agentes de desenvolvimento, e gerava um alto consumo de tokens de contexto para as IAs lerem todo o histórico histórico de decisões irrelevantes à tarefa atual.

## Decisão

Particionar o log de microdecisões de design de modo que **cada decisão seja armazenada em um arquivo individual de Markdown** sob o diretório `decisoes/` no formato `MD-NNNN.md` (onde NNNN é um sequencial de quatro dígitos com preenchimento de zeros, ex: `MD-0008.md`).

A consolidação do histórico e o índice de decisões são gerados de forma programática automatizada a partir dos metadados das microdecisões por meio do script `bin/gerar-index-decisoes.sh`, que é executado automaticamente durante o encerramento da sessão de desenvolvimento.

## Alternativas Consideradas

* **Manter o Monólito (`microdecisoes.md`):** Descartado devido à falta de escalabilidade de tokens, propensão a conflitos e falta de rastreabilidade fina de alterações via controle de versão.
* **Banco de Dados Relacional Local (SQLite):** Descartado porque exige dependências de runtime e inviabiliza a leitura direta das decisões no formato de arquivos de documentação Markdown nativos do repositório Git.

## Consequências

* **Positivas:**
  * Facilidade de leitura e edição focada por arquivos menores.
  * Redução significativa de conflitos no Git em projetos editados por múltiplos agentes de IA de forma assíncrona.
  * Otimização de contexto das IAs, permitindo carregar apenas as microdecisões associadas ao gancho da tarefa ativa.
* **Negativas:**
  * Necessidade de manter e executar um script de compilação (`gerar-index-decisoes.sh`) para manter o índice visual (`microdecisoes.md`) atualizado.
