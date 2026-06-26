# Requirements: Correção do no-op silencioso no `encerrar-sessao`

> Identificador: `015-corrige-encerrar-sessao-noop`
> Data: `2026-06-26`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Diante de um estado de sessão cujo commit-âncora tem hash curto — escrito por uma versão antiga do harness, antes da validação de quarenta caracteres —, o comando `encerrar-sessao` emite um aviso em `stderr` e termina com `exit 0`, sem fechar nada. O usuário recebe um sucesso aparente enquanto a sessão segue aberta, e só destrava reescrevendo o estado à mão. A feature elimina esse falso sucesso: o encerramento explícito passa a falhar barulhento (saída diferente de zero) ou a auto-reparar o hash curto recuperável, preservando a saída não-bloqueante apenas no caminho de boot que reinjeta a sessão (`resume`).

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/domain.md#2.3` (RN-N4) | Estado **ausente** → `None`; estado **malformado** (sem `---`, YAML inválido, campo obrigatório ausente, **commit não-SHA1**) → `MalformedSessionStateError`, "falha explícita, **nunca silenciosa**". O defeito viola diretamente esta regra. | 🟢 |
| `_reversa_sdd/domain.md#2.14` (RN-N32) | No fechamento, falha que impeça o registro levanta erro nomeado com `exit ≠ 0`, sem devolver sucesso — "RN-N4 estendida ao fechamento". O comportamento atual contradiz esta extensão. | 🟢 |
| `_reversa_sdd/architecture.md#4` (Integrações de Borda) | O slash command `./harness cmd encerrar-sessao` é materializado para Claude e Antigravity; a borda `cmd` em `main.py` despacha todos os comandos de sessão. | 🟢 |
| `_reversa_sdd/architecture.md#5` (Dívidas Técnicas) | T1–T6 dados como resolvidos; este no-op silencioso é bug latente **ainda não catalogado**, observado em uso (dogfooding). | 🟡 |
| `_reversa_sdd/domain.md#glossário` | Âncora Git de Sessão = SHA-1 do commit HEAD gravado no fechamento; usada na retomada para detectar divergência da base local. | 🟢 |

Locus confirmado por leitura de código (fora do `_reversa_sdd/`, citado como apoio): o `try/except MalformedSessionStateError` na borda `cmd` envolve **todos** os comandos de sessão e responde com aviso em `stderr` mais `exit 0`. O comentário no código justifica a saída zero como proteção do `SessionStart` do agente — proteção legítima para o `resume` no boot, indevida para o `encerrar-sessao` explícito.

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor intermitente | Encerrar a sessão de forma confiável após semanas de pausa | Retoma o repositório com um estado de sessão legado de hash curto e roda `/encerrar-sessao`; espera fechamento real ou falha clara, não sucesso falso |
| Agente de IA no boot | Reinjetar a sessão sem travar a inicialização | Roda `resume` no `SessionStart` sobre um estado malformado; a inicialização não pode ser interrompida por saída diferente de zero |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** O `encerrar-sessao` explícito, diante de estado malformado que não possa ser reparado, **falha barulhento**: saída diferente de zero e mensagem nomeada que identifica o arquivo de estado e a causa. Nunca `exit 0` silencioso. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.3` (RN-N4) e `_reversa_sdd/domain.md#2.14` (RN-N32)
   - Tipo: alterada (corrige a borda que hoje contradiz RN-N4)
2. **RN-02:** Quando o estado traz um hash curto **recuperável** — prefixo que resolve, no repositório local, a um único commit existente —, o comando **auto-repara**: expande para o SHA-1 de quarenta caracteres, regrava o estado de forma atômica e prossegue o fechamento normalmente. 🟡
   - Origem no legado: estende `_reversa_sdd/domain.md#2.3` (RN-N4), que hoje classifica o hash curto como malformado terminal
   - Tipo: nova
3. **RN-03:** O caminho não-bloqueante (aviso em `stderr` com `exit 0`) permanece válido **apenas** para a reinjeção de sessão no boot (`resume`/`SessionStart`); não pode mascarar a falha de comandos explícitos de sessão. 🟡
   - Origem no legado: `_reversa_sdd/domain.md#2.3` (RN-07/RN-N3, semântica do `resume`) e `_reversa_sdd/architecture.md#4` (borda como ponto de escolha do mecanismo)
   - Tipo: nova (formaliza a fronteira que o catch atual ignora)
4. **RN-04:** O auto-reparo nunca **fabrica** uma âncora: só aceita um hash que o próprio repositório resolva. Hash que não resolve recai em RN-01 (falha barulhenta). 🟢
   - Origem no legado: `_reversa_sdd/domain.md#glossário` (âncora = SHA-1 real do HEAD)
   - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | `encerrar-sessao` sobre estado malformado irrecuperável termina barulhento | Must | Executar o comando com estado de hash curto irreparável → código de saída diferente de zero e mensagem nomeando arquivo e causa; a sessão **não** é marcada como encerrada | 🟢 |
| RF-02 | A reinjeção de sessão no boot continua não-bloqueante | Must | `resume` sobre o mesmo estado malformado → código de saída zero e aviso em `stderr`; o boot do agente não é interrompido | 🟢 |
| RF-03 | Auto-reparo do hash curto legado recuperável | Should | Estado cujo hash é prefixo válido de um commit local → comando expande para quarenta caracteres, regrava o estado e fecha com sucesso; o estado resultante contém âncora de quarenta caracteres | 🟡 |
| RF-04 | Teste de regressão do no-op | Must | Suíte ganha caso que reproduz "hash curto + `encerrar-sessao`" e verifica o novo comportamento (falha barulhenta ou reparo); o teste falharia contra o código atual | 🟢 |
| RF-05 | Orientação ao usuário no caminho irrecuperável | Could | A mensagem de falha indica como destravar (ex.: regravar a âncora) quando o reparo não é possível | 🟡 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Observabilidade | Erro nomeado, saída diferente de zero, mensagem clara em `stderr`; nada de sucesso silencioso | Princípio "erros barulhentos > performance" e RN-N4 / RN-N32 (`_reversa_sdd/domain.md#2.3`, `#2.14`) | 🟢 |
| Compatibilidade | O boot do agente não regride: `SessionStart`/`resume` jamais é travado por estado malformado | `_reversa_sdd/architecture.md#4` (ganchos de ciclo de vida) e o comentário de borda que originou o `exit 0` | 🟢 |
| Reprodutibilidade | Estado escrito por versões antigas do harness deve ser retomável sem edição manual obrigatória | Princípio "retomável após semanas/meses" do mantenedor intermitente | 🟡 |
| Segurança/Integridade | O reparo só usa âncora que o repositório resolve; nunca inventa ou trunca SHA arbitrário | RN-04; `_reversa_sdd/domain.md#glossário` (âncora = SHA-1 real) | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Encerramento explícito sobre estado de hash curto irrecuperável falha barulhento
  Dado um arquivo de estado de sessão ativo cujo commit-âncora é um hash curto que não resolve no repositório
  Quando o mantenedor executa o comando encerrar-sessao
  Então o comando termina com código de saída diferente de zero
  E exibe uma mensagem nomeando o arquivo de estado e a causa
  E a sessão permanece marcada como ativa, sem registro falso de encerramento

Cenário: Reinjeção de sessão no boot tolera estado malformado
  Dado o mesmo arquivo de estado malformado
  Quando o agente executa resume no SessionStart
  Então o comando termina com código de saída zero
  E emite um aviso em stderr
  E o boot do agente prossegue sem interrupção

Cenário: Auto-reparo de hash curto recuperável conclui o encerramento
  Dado um arquivo de estado ativo cujo commit-âncora é um prefixo que resolve a um único commit local
  Quando o mantenedor executa o comando encerrar-sessao
  Então o comando expande a âncora para o SHA-1 de quarenta caracteres
  E regrava o estado de forma atômica
  E encerra a sessão com sucesso, registrando o fechamento
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 (falha barulhenta no encerrar explícito) | Must | É o núcleo do defeito: o falso sucesso contraria RN-N4/RN-N32 e o princípio de erros barulhentos |
| RF-02 (boot não-bloqueante preservado) | Must | Sem esta fronteira, endurecer o encerramento poderia travar o `SessionStart` — regressão inaceitável |
| RF-04 (teste de regressão) | Must | Hoje não há cobertura do caso de hash curto no `encerrar-sessao`; sem teste, o no-op pode voltar |
| RF-03 (auto-reparo) | Should | Melhora forte de UX para o mantenedor intermitente, porém depende da decisão de escopo (ver Lacunas) |
| RF-05 (orientação na mensagem) | Could | Refinamento de mensagem; subordinado a RF-01 |

## 9. Esclarecimentos

> Nenhuma sessão de dúvidas registrada ainda. Rode `/reversa-clarify` quando houver `[DÚVIDA]` pendente.

## 10. Lacunas

- 🔴 [DÚVIDA] Estratégia primária de escopo: a feature deve **auto-reparar** o hash curto recuperável (RF-03/RN-02), **falhar barulhento** sempre (apenas RF-01/RN-01), ou combinar as duas — reparar quando o hash resolve e falhar barulhento quando não? A combinação é a leitura natural do brief, mas eleva o escopo e introduz o caminho de reparo com seus próprios casos de borda.
- 🔴 [DÚVIDA] Fronteira de diferenciação: o endurecimento deve valer **só** para `encerrar-sessao`, ou para **todos** os comandos explícitos de sessão (`handoff`, `clarificar`), mantendo a saída zero não-bloqueante exclusivamente no `resume` de boot? E por qual sinal a borda distingue "invocação de boot" de "invocação explícita", já que hoje o mesmo despacho `cmd` atende ambos sob o mesmo `try/except`?

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-26 | Versão inicial gerada por `/reversa-requirements` | reversa |
