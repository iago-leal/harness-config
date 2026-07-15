# Requirements: Registro obrigatório de microdecisões via gancho de sessão

> Identificador: `022-hook-registro-decisoes`
> Data: `2026-07-15`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Em algumas sessões o agente toma decisões não óbvias e encerra o trabalho sem criar a ficha `MD-NNNN.md` correspondente; o índice `.harness/microdecisoes.md`, por ser derivado apenas das fichas existentes, permanece formalmente válido porém incompleto por omissão. A feature acrescenta um **gate de registro** ao ciclo de encerramento: diante do sinal físico de trabalho substantivo sem ficha nova ou atualizada, o encerramento não conclui silenciosamente — o agente é instruído a registrar a decisão ou a declarar, de forma auditável, que não houve decisão não óbvia na sessão. O beneficiário é o mantenedor único intermitente, cuja retomada após semanas depende do grafo de decisões completo.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#4-integrações-de-borda` | Ganchos do Claude hoje: `SessionStart → cmd resume` e `Stop → decisions`; o `Stop` apenas valida e reindexa fichas **existentes** — nada detecta a ausência de registro. | 🟢 |
| `_reversa_sdd/domain.md#2.5` (RN-N12/N13/N14) | O índice é DERIVADO das fichas e a integridade validada é a **do que existe** (front-matter, grafo, arestas); omissão de ficha é invisível ao serviço. | 🟢 |
| `_reversa_sdd/domain.md#2.18` (RN-N41) | O `resume` ancora o agente no índice de decisões antes de varreduras amplas; o valor dessa âncora degrada silenciosamente quando decisões deixam de ser registradas. | 🟢 |
| `_reversa_sdd/domain.md#2.16` (RN-N34) | Fichas sujas entram na oferta de commit ao encerrar — cobre fichas **já escritas**, não obriga a escrevê-las. | 🟢 |
| `_reversa_sdd/microdecisoes/requirements.md` | Unit spec do serviço de decisões: responsabilidades são carregar, validar e compilar; o registro em si é voluntário, feito pelo agente. | 🟢 |
| `_reversa_sdd/domain.md#2.11` (RN-N26) | Contrato do `Stop` no Antigravity: emite `{}`, **nunca** bloqueia nem reentra no laço — restrição estrutural para estender o gate a esse harness. | 🟢 |
| `.harness/decisoes/MD-0014.md` | O perfil Claude emite hoje só dois ganchos; precedente recente de alterar a **emissão na fonte** (`hooks_block()`) para que `init`/`upgrade` propaguem a mudança. | 🟢 |
| `_reversa_sdd/domain.md#2.17` (RN-N39) | Materialização dos settings do Claude por merge **por-item** (preserva itens alheios) — via obrigatória para instalar qualquer gancho novo. | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor único intermitente (iagoleal) | Retomar o projeto após semanas com o "porquê" das mudanças completo | Abre sessão meses depois; o `resume` reinjeta um índice de decisões fiel ao que de fato foi decidido. |
| Agente de IA (harness ativo `claude`) | Encerrar o turno sem perder decisões não óbvias | Ao encerrar com trabalho substantivo e nenhuma ficha nova, recebe instrução de registrar `MD-NNNN` (ou declarar ausência) antes de concluir. |
| Mantenedor em repositório documental (empresas, contratos) | Ter alterações de contrato e criação de documentos tratadas como decisões registráveis | Sessão que só altera documentos também dispara o gate — repositório não é só código. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01 — Gate híbrido de registro** 🟢
   - Dois graus, conforme o caráter do ato (esclarecido em 2026-07-15): no **encerramento deliberado** (`encerrar-sessao`), pendência de registro **bloqueia** a conclusão até a ficha ser criada ou o escape declarado; no **fim de turno** (`Stop`), pendência gera apenas **lembrete não-bloqueante** reinjetado ao agente.
   - Origem no legado: `_reversa_sdd/architecture.md#4-integrações-de-borda` (o `Stop` atual só valida/reindexa)
   - Tipo: nova
2. **RN-02 — Disparo por sinal físico, nunca auto-declarado** 🟢
   - O veredito deriva de artefatos verificáveis — diferenças no repositório desde a âncora da sessão (e/ou working tree sujo) cruzadas com o estado das fichas em `.harness/decisoes/` — jamais de metadado declarado pelo próprio agente sem lastro. Coerente com a filosofia de detecção por artefato físico já usada no ciclo forward.
   - **Trabalho substantivo** é qualquer mudança versionável desde a âncora, **sem filtro por tipo de arquivo** (esclarecido em 2026-07-15): repositórios não são só código — alterações de contrato, criação e edição de documentos também carregam decisões não óbvias. Excluem-se apenas os artefatos de estado do próprio harness (arquivo de estado da sessão, índice derivado, cache de sync) e as próprias fichas de decisão.
   - Origem no legado: `_reversa_sdd/domain.md#2.16` (RN-N34, detecção via git real)
   - Tipo: nova
3. **RN-03 — Escape auditável** 🟢
   - O agente pode satisfazer o gate declarando explicitamente "sem decisão não óbvia nesta sessão"; a declaração fica registrada no **estado da sessão** (`.harness/estado-da-sessao.md`), inspecionável na retomada seguinte (nunca um bypass invisível). (Esclarecido em 2026-07-15.)
   - Tipo: nova
4. **RN-04 — Anti-loop** 🟢
   - No mesmo encerramento, o gate dispara **no máximo uma vez**: satisfeito por ficha nova ou pelo escape, o encerramento prossegue. Um gate que re-bloqueia indefinidamente é dano maior que a omissão que combate.
   - Tipo: nova
5. **RN-05 — Falha permissiva e barulhenta** 🟢
   - Erro interno do gate (git indisponível, configuração corrompida, estado de sessão ausente) nunca trava o agente: o encerramento prossegue com aviso em `stderr`. Estende o contrato de não-bloqueio dos ganchos do harness.
   - Origem no legado: `_reversa_sdd/domain.md#2.2` (RN-03) e `#2.11` (RN-N26)
   - Tipo: nova
6. **RN-06 — Emissão pelo perfil e propagação pelo bootstrap** 🟢
   - O gate entra na configuração materializada do harness pela mesma via dos ganchos existentes — emissão no perfil (`hooks_block()`) e merge por-item nos settings — de modo que `init`/`upgrade`/`migrate` o propaguem e nenhum item alheio seja destruído.
   - O gate nasce **ligado por default** em toda instalação, inclusive nos projetos-alvo via bootstrap; o opt-out é por flag na seção `[decisions]`. (Esclarecido em 2026-07-15.)
   - Origem no legado: `_reversa_sdd/domain.md#2.17` (RN-N39); precedente `.harness/decisoes/MD-0014.md`
   - Tipo: alterada (estende a emissão atual do perfil Claude)
7. **RN-07 — Core agnóstico ao harness** 🟡
   - A avaliação do gate é serviço de domínio puro (entrada: estado do repositório + fichas; saída: veredito + mensagem); **como** interceptar o encerramento é decisão da borda, por harness.
   - Origem no legado: `_reversa_sdd/domain.md#2.3` (RN-N5)
   - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Avaliar, de forma determinística, se há pendência de registro: qualquer mudança versionável desde a âncora da sessão (código, documentos, configuração) sem ficha `MD-*.md` nova ou modificada; artefatos de estado do próprio harness não contam como mudança. | Must | Mesmo estado do repositório → mesmo veredito; casos (com/sem mudança, com/sem ficha, mudança só de estado do harness, mudança só documental) cobertos por testes. | 🟢 |
| RF-02 | Bloquear o encerramento deliberado (`encerrar-sessao`) quando o veredito for "pendente", entregando ao agente instrução com o formato da ficha (`D/PORQUÊ/DESCARTADO/ESTADO`) e o local canônico (`.harness/decisoes/`). | Must | `encerrar-sessao` com mudanças e nenhuma ficha → fluxo interceptado com a instrução; com ficha nova/modificada → conclui limpo. | 🟢 |
| RF-03 | Oferecer escape auditável: a declaração de ausência de decisão satisfaz o gate e fica registrada no estado da sessão. | Must | Após a declaração, o mesmo encerramento não volta a bloquear; o registro é legível em `.harness/estado-da-sessao.md`. | 🟢 |
| RF-04 | Garantir anti-loop: no mesmo encerramento, o gate não dispara mais de uma vez. | Must | Segunda tentativa consecutiva de encerrar sem mudança nova → conclui, com aviso. | 🟢 |
| RF-05 | Permitir desligar o gate por flag na seção `[decisions]` do `harness.toml`; default **ligado** (opt-out). | Should | Flag desligada → comportamento atual intocado; flag ausente → gate ativo. | 🟢 |
| RF-06 | Materializar o gancho do gate via perfil + merge por-item, propagado por `init`/`upgrade`/`migrate`. | Must | Projeto-alvo com settings contendo itens alheios → após materializar, item do gate presente e alheios preservados. | 🟢 |
| RF-07 | Variante advisory (não-bloqueante) para o Antigravity, cujo contrato de `Stop` proíbe bloqueio. | Must | Sob o Antigravity, pendência gera apenas registro/aviso, jamais alteração do fluxo do agente. | 🟢 |
| RF-08 | Lembrete no fim de turno (`Stop`) do Claude quando houver pendência de registro, com interferência mínima: **no máximo um soft-block por estado de pendência** (o protocolo do `Stop` não tem canal não-bloqueante que alcance o agente — ver `roadmap.md` D-04). | Must | Turno com pendência → lembrete reinjetado uma única vez (soft-block com instrução); mesmo estado de pendência → nunca lembra de novo; sem pendência → silêncio; a repetição da conclusão do turno jamais é impedida. | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Robustez | Falha interna do gate nunca impede o encerramento (permissivo + aviso). | Contrato de não-bloqueio dos ganchos: `_reversa_sdd/domain.md#2.2`, `#2.11`. | 🟢 |
| Determinismo | Veredito reprodutível, sem dependência de rede; só leitura local de git e fichas. | Padrão do core: `_reversa_sdd/microdecisoes/requirements.md#requisitos-não-funcionais`. | 🟢 |
| Testabilidade | Cobertura TDD do serviço puro **e** smoke com git real (o porcelain colapsa subdiretório untracked; mocks mascaram). | Achado da feature 019: `_reversa_sdd/domain.md#2.16` (RN-N34). | 🟢 |
| Observabilidade | Veredito e motivo sempre visíveis (`stderr` ou saída estruturada); nunca falha silenciosa. | Princípio de erros barulhentos do projeto. | 🟢 |
| Footprint | Toda escrita (rastro do escape, estado do gate) ocorre sob o repositório do projeto. | `_reversa_sdd/domain.md#2.8` (RN-N17). | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: trabalho substantivo sem ficha bloqueia o encerramento deliberado
  Dado uma sessão ativa com arquivos alterados desde a âncora (código ou documentos)
  E nenhuma ficha MD-*.md nova ou modificada em .harness/decisoes/
  Quando o agente roda o encerramento deliberado (encerrar-sessao)
  Então o encerramento é interceptado com instrução de registrar a decisão (formato + local canônico)

Cenário: fim de turno com pendência lembra uma única vez
  Dado um turno do agente com mudanças versionáveis e nenhuma ficha nova
  Quando o evento de fim de turno (Stop) ocorre
  Então um lembrete de registro é reinjetado ao agente (soft-block único)
  E no fim de turno seguinte, com o mesmo estado de pendência, o turno conclui sem novo lembrete

Cenário: ficha registrada libera o encerramento
  Dado a mesma sessão com uma ficha MD-*.md nova em .harness/decisoes/
  Quando o agente tenta encerrar
  Então o encerramento conclui sem interceptação

Cenário: escape auditável libera o encerramento
  Dado um encerramento interceptado pelo gate
  Quando o agente declara explicitamente que não houve decisão não óbvia
  Então o encerramento conclui e a declaração fica registrada em artefato inspecionável

Cenário: anti-loop no mesmo encerramento
  Dado um encerramento já interceptado uma vez pelo gate
  Quando o agente tenta encerrar de novo sem nenhuma mudança nova
  Então o encerramento conclui, com aviso de pendência não sanada

Cenário negativo: falha interna do gate não trava o agente
  Dado que o repositório git está inacessível ou a configuração está corrompida
  Quando o gate roda no encerramento
  Então o encerramento prossegue normalmente e o erro é reportado em stderr

Cenário: gate desligado por configuração preserva o comportamento atual
  Dado um harness.toml com a flag do gate desligada na seção [decisions]
  Quando o agente encerra com trabalho substantivo e nenhuma ficha nova
  Então o encerramento conclui sem interceptação, idêntico ao comportamento pré-feature

Cenário: materialização preserva itens alheios
  Dado um projeto-alvo cujos settings contêm itens de ganchos de terceiros
  Quando o bootstrap materializa o gancho do gate
  Então o item do gate está presente e todos os itens alheios permanecem intactos

Cenário: variante advisory nunca bloqueia o Antigravity
  Dado o harness ativo antigravity com pendência de registro detectada
  Quando o evento de encerramento do agente ocorre
  Então o fluxo do agente segue inalterado e a pendência é apenas registrada como aviso
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 (avaliação determinística) | Must | Núcleo da feature; sem veredito confiável não há gate. |
| RF-02 (bloqueio no `encerrar-sessao`) | Must | É o mecanismo que torna o registro obrigatório — a demanda literal do pedido. |
| RF-03 (escape auditável) | Must | Sem escape, todo falso positivo vira beco sem saída; com escape invisível, o gate vira teatro. |
| RF-04 (anti-loop) | Must | Gate que re-bloqueia indefinidamente quebra o laço do agente — risco maior que a omissão. |
| RF-05 (flag de opt-out) | Should | Default ligado escolhido em 2026-07-15; a flag preserva a saída honrosa por projeto. |
| RF-06 (materialização pelo perfil) | Must | Default ligado em projetos-alvo exige propagação por `init`/`upgrade` — sem ela o escopo escolhido não se realiza. |
| RF-07 (advisory Antigravity) | Must | Incluído no escopo desta iteração em 2026-07-15; o contrato do `Stop` local proíbe bloqueio, daí a variante. |
| RF-08 (lembrete no `Stop` do Claude) | Must | Metade não-bloqueante do enforcement híbrido escolhido em 2026-07-15. |

## 9. Esclarecimentos

### Sessão 2026-07-15

- **Q:** O que conta como "trabalho substantivo" que dispara o gate?
  **R:** Qualquer mudança versionável desde a âncora, sem filtro por tipo de arquivo. Repositórios muitas vezes não são só código: alterações de contrato, criação e edição de documentos (ex.: repositório de empresas) são exemplos de decisões não óbvias. Excluem-se só os artefatos de estado do próprio harness e as fichas.
- **Q:** Qual o grau de enforcement?
  **R:** Híbrido: bloqueio duro no `encerrar-sessao` (ato deliberado) + lembrete não-bloqueante no `Stop` de cada turno.
- **Q:** O gate nasce ligado por default?
  **R:** Sim, em todo lugar — inclusive projetos-alvo via `init`/`upgrade`; opt-out por flag em `[decisions]`.
- **Q:** Alcance de harness nesta iteração?
  **R:** Claude com bloqueio + Antigravity com variante advisory (o `Stop` do Antigravity não pode bloquear, RN-N26). Gemini fora do escopo desta iteração.
- **Q:** Onde vive o rastro auditável do escape ("sem decisão não óbvia")?
  **R:** No estado da sessão (`.harness/estado-da-sessao.md`), como registro da narrativa.

## 10. Lacunas

- Nenhuma lacuna pendente. As três dúvidas da versão inicial foram resolvidas na sessão de 2026-07-15 (ver seção 9).

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-07-15 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-07-15 | Sessão de esclarecimentos: 5 dúvidas resolvidas e integradas por `/reversa-clarify` (enforcement híbrido, sinal sem filtro de tipo, default ligado, Claude+Antigravity, rastro no estado da sessão) | reversa |
| 2026-07-15 | RF-08 reconciliado pelo `/reversa-plan`: o protocolo do `Stop` não tem canal não-bloqueante que alcance o agente — lembrete vira soft-block único por estado de pendência (roadmap D-04) | reversa |
