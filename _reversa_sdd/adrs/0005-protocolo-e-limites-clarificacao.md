# ADR 0005: Protocolo e Limites de Clarificação no Comando /clarificar

* **Status:** Aceito
* **Data:** 2026-06-21
* **Contexto Técnico:** Módulo `commands` (`clarificar.md`)
* **Escala de Confiança:** 🟢 CONFIRMADO

## Contexto e Problema

Requisitos de software complexos, mal formulados ou com saltos lógicos perigosos podem levar o agente de IA a propor soluções técnicas incorretas ou mal dimensionadas. O protocolo PCCP (Problema-Causa-Consequência-Proposta) fornece uma base sólida para clarificação. 

Entretanto, se a interação de clarificação de requisitos for irrestrita, há o risco de o agente e o usuário humano entrarem em um loop contínuo de perguntas teóricas refinadas, gerando paralisia operacional de análise e alto consumo desnecessário de tokens.

## Decisão

Adotar limites rígidos de rodadas operacionais na implementação do comando `/clarificar`:
1. **Estruturação via PCCP:** Todas as demandas com lacunas identificadas devem ser estruturadas separando fatos verificados (F), inferências (I) e lacunas (H).
2. **Limite Físico de 2 Rodadas:** O comando `/clarificar` impõe o limite máximo de 2 rodadas de esclarecimentos (`MAX_RODADAS_CLARIF=2`).
3. **Mecanismo de Travamento (`/travar`):** Se a demanda for esclarecida e acordada, o usuário digita `/travar` para fechar os requisitos definitivos do escopo antes de gerar o plano técnico.
4. **Fallback defensivo por Esgotamento:** Caso o limite de 2 rodadas seja atingido sem o travamento explícito do usuário, o agente é instruído a assumir uma hipótese de lacuna (H) mínima e segura, alertar o usuário sobre os riscos e prosseguir de forma pragmática para a execução.

## Alternativas Consideradas

* **Diálogo interativo infinito até conciliação total:** Rejeitado porque gera alto desperdício de tempo e recursos com baixo retorno marginal após as primeiras rodadas.

## Consequências

* **Positivas:**
  * Velocidade no levantamento de requisitos e eliminação pragmática de bloqueios.
  * Proteção eficaz contra loops infinitos de clarificação de IAs.
  * Rastreabilidade de fatos, inferências e hipóteses (lacunas).
* **Negativas:**
  * Em cenários extremamente complexos, o fallback com hipótese mínima pode resultar em um escopo ligeiramente simplificado que exigirá ajustes posteriores no ciclo forward.
