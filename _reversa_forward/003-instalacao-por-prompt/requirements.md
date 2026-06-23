# Requirements: Instalação do Harness por Prompt Estruturado

> Identificador: `003-instalacao-por-prompt`
> Data: `2026-06-23`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Esta feature entrega um **prompt de instalação estruturado, copiável e colável no agente de IA** (o harness ativo: Claude Code, Gemini CLI ou antigravity), que executa por conta própria a instalação local completa e idempotente do `harness-core` — ambiente virtual, dependências, wrapper de raiz, ganchos de ciclo de vida do harness ativo e índice de decisões — encerrando com uma verificação de saúde explícita. Substitui a sequência de comandos manuais do onboarding por uma única colagem, transferindo a execução do humano para o agente e eliminando o acoplamento a caminhos globais do host.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#5-dividas-tecnicas-identificadas` | Dependência implícita de interpretador Python global no host: o setup de dependências assume `venv`/`pip` ativos no host, fricção que a instalação precisa absorver e reportar. | 🟢 |
| `_reversa_sdd/inventory.md#wrapper-de-conveniencia-raiz-do-projeto` | O wrapper `harness` na raiz invoca a venv local e encaminha argumentos ao núcleo; é o ponto de entrada que a instalação deve garantir presente e executável. | 🟢 |
| `_reversa_sdd/code-analysis.md#21-modulo-bootstrap` | Instalação idempotente de ganchos como capacidade já existente do núcleo (corte definitivo), base para a etapa de ganchos da instalação. | 🟢 |
| `_reversa_sdd/domain.md#22-integridade-e-salvaguarda-de-arquivos-formatacao` | Garantia de não-bloqueio (RN-03) e proteção de diretórios críticos (RN-04): a instalação não pode introduzir hooks que travem o editor do agente. | 🟢 |
| `decisoes/MD-0001.md` | Corte dos hooks vivos para a CLI já aplicado; regressão pendente: o `SessionStart` ainda não reinjeta o estado da sessão. A instalação precisa lidar com essa lacuna sem mascará-la. | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor único intermitente | Instalar ou reinstalar o harness num projeto após meses de pausa, sem reler o onboarding inteiro. | Abre o projeto, copia o prompt de instalação, cola no agente e o agente executa todo o setup, reportando saúde ao final. |
| Agente de IA (executor) | Executar a instalação passo a passo com checagens explícitas e falhas legíveis. | Recebe o prompt, detecta o que já existe, completa só o que falta e valida cada etapa antes de prosseguir. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01: Instalação por colagem única** 🟢
   - Origem no legado: `_reversa_sdd/inventory.md#wrapper-de-conveniencia-raiz-do-projeto`
   - Tipo: nova
   - Descrição: A interface primária de instalação é um prompt estruturado colável no agente; o agente executa as ações, e o humano não roda comandos manuais salvo quando uma credencial ou permissão indisponível impeça a automação.

2. **RN-02: Idempotência da instalação** 🟢
   - Tipo: nova
   - Descrição: Executar o prompt mais de uma vez não corrompe o estado: cada etapa detecta o que já está presente e completa apenas o que falta, sem refazer destrutivamente o que existe.

3. **RN-03: Aderência ao harness ativo** 🟢
   - Origem no legado: `_reversa_sdd/domain.md` (configuração `active_harness` em `harness.toml`)
   - Tipo: nova
   - Descrição: A etapa de ganchos configura o ciclo de vida do harness atualmente ativo, conforme declarado na configuração do projeto, sem assumir um agente fixo. Um único prompt parametrizado pelo `active_harness` cobre claude, gemini e antigravity, sem variantes duplicadas.

4. **RN-04: Verificação de saúde pós-instalação com falha barulhenta** 🟢
   - Origem no legado: `_reversa_sdd/domain.md#22-integridade-e-salvaguarda-de-arquivos-formatacao`
   - Tipo: nova
   - Descrição: Ao final, a instalação valida ambiente virtual, wrapper executável, ganchos aplicados e a execução de validação de decisões; qualquer etapa ausente ou inconsistente é reportada de forma explícita, nunca silenciada.

5. **RN-05: Não-mascaramento da regressão de estado de sessão** 🟢
   - Origem no legado: `decisoes/MD-0001.md`
   - Tipo: alterada
   - Descrição: Portar a reinjeção do estado de sessão para a CLI está **fora do escopo desta feature** e é tratado numa feature própria (004), preservando a coesão da 003. Enquanto o núcleo não reinjetar o estado da última sessão no início da sessão, a verificação de saúde deve sinalizar essa lacuna conhecida em vez de declarar a instalação plenamente concluída.

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Prompt de instalação exposto como comando da CLI (`./harness install-prompt`), gerado por introspecção | Must | Um comando da CLI imprime o prompt completo e atualizado por introspecção do núcleo e da configuração; copiado e colado no agente, descreve todas as etapas da instalação em ordem executável. Fonte única, sem cópia mantida à mão. | 🟢 |
| RF-02 | Etapa de ambiente virtual e dependências idempotente | Must | A partir de um projeto sem ambiente virtual, a execução cria a venv e instala as dependências fixadas; reexecutar não recria destrutivamente. | 🟢 |
| RF-03 | Etapa de wrapper de raiz garantido e executável | Must | Após a execução, o wrapper da raiz existe e possui permissão de execução; uma chamada simples ao núcleo retorna com sucesso. | 🟢 |
| RF-04 | Etapa de aplicação de ganchos de ciclo de vida do harness ativo | Must | Os ganchos de ciclo de vida (SessionStart/PostToolUse/Stop) do harness ativo passam a apontar para o ponto de entrada local, a partir do snippet canônico. Os ganchos Git locais (pre-commit/post-merge via bootstrap) ficam fora do escopo desta feature. | 🟢 |
| RF-05 | Verificação de saúde final legível | Should | A execução termina imprimindo o estado de cada item verificado, com marcação clara de aprovado/pendente e destaque para a lacuna de estado de sessão. | 🟢 |
| RF-06 | Suporte multi-harness por parametrização única | Should | Um único prompt, parametrizado pelo `active_harness` do `harness.toml`, aplica os ganchos do harness certo (claude, gemini ou antigravity) sem variantes duplicadas. | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Portabilidade | Compatibilidade com sistemas POSIX (macOS e Linux). | Consistência com os RNF das features 001/002 e com o wrapper shell existente. | 🟢 |
| Robustez | Falhas explícitas e legíveis em cada etapa; nenhum erro silencioso. | Princípio operacional de erros barulhentos; `_reversa_sdd/domain.md` (não-bloqueio é para o editor, não para o instalador). | 🟢 |
| Reprodutibilidade | Instalação determinística a partir de dependências fixadas. | `_reversa_sdd/architecture.md#5-dividas-tecnicas-identificadas` aponta o setup como ponto frágil. | 🟡 |
| Independência de rede | Nenhuma dependência de rede além da obtenção de pacotes na etapa de dependências. | Resiliência offline já é regra do núcleo (`_reversa_sdd/domain.md#21`). | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Instalação limpa por colagem única
  Dado um projeto com o harness-core presente mas sem ambiente virtual configurado
  Quando o mantenedor cola o prompt de instalação no agente ativo
  Então o agente cria a venv, instala as dependências, garante o wrapper executável e aplica os ganchos do harness ativo
  E ao final imprime uma verificação de saúde com cada item marcado como aprovado

Cenário: Reexecução idempotente
  Dado um projeto onde a instalação já foi concluída
  Quando o prompt de instalação é colado e executado novamente
  Então nenhuma etapa corrompe o estado existente
  E a verificação de saúde permanece aprovada

Cenário: Lacuna de estado de sessão sinalizada
  Dado que o núcleo ainda não reinjeta o estado da última sessão no início da sessão
  Quando a verificação de saúde é executada ao final da instalação
  Então a lacuna de estado de sessão é reportada explicitamente como pendente conhecida
  E a instalação não a declara como plenamente concluída
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | É a própria entrega: o prompt de instalação por colagem, como comando da CLI. |
| RF-02 | Must | Sem venv e dependências, o núcleo não roda. |
| RF-03 | Must | O wrapper é o ponto de entrada dos ganchos e do uso manual. |
| RF-04 | Must | Sem os ganchos aplicados, a instalação não conecta o agente ao núcleo. |
| RF-05 | Should | Verificação de saúde é o que torna a instalação confiável e retomável. |
| RF-06 | Should | Multi-harness por parametrização única atende à operação real Claude ↔ Gemini sem duplicação. |

## 9. Esclarecimentos

### Sessão 2026-06-23

- **Q:** Formato e local do artefato do prompt de instalação?
  **R:** Comando da CLI `./harness install-prompt`, gerado por introspecção — fonte única, sem Markdown mantido à mão (evita drift e índice paralelo). Reflete em RF-01.
- **Q:** A 003 deve portar a reinjeção de contexto do `SessionStart` (fechar MD-0001) ou adiar?
  **R:** Adiar para uma feature própria (004), preservando a coesão da 003 (instalar) e o baixo acoplamento ao contrato de estado. A dívida fica documentada (MD-0001) e sinalizada pelo health-check. Reflete em RN-05.
- **Q:** Como cobrir claude, gemini e antigravity no prompt?
  **R:** Um único prompt parametrizado pelo `active_harness` do `harness.toml`, sem variantes duplicadas — atende à operação real Claude ↔ Gemini com baixo acoplamento. Ressalva de plano: os mecanismos de hook diferem por harness (o Gemini usa a ponte `context.*`). Reflete em RN-03/RF-06.
- **Q:** A instalação também instala os ganchos Git locais (pre-commit/post-merge via bootstrap)?
  **R:** Não. Só os ganchos de ciclo de vida do agente. Os ganchos Git ficam fora do escopo (o `pre-commit` do bootstrap ainda é cru). Reflete em RF-04.

## 10. Lacunas

- Nenhuma lacuna pendente. As três dúvidas iniciais foram resolvidas na sessão de esclarecimentos de 2026-06-23.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-06-23 | Dúvidas resolvidas (artefato como comando da CLI, porte do SessionStart adiado p/ 004, multi-harness parametrizado, ganchos Git fora de escopo) por `/reversa-clarify` | reversa |
