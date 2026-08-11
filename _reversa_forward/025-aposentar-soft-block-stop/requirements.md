# Requirements: Aposentar o soft-block do Stop (lembrete de microdecisão vira advisory)

> Identificador: `025-aposentar-soft-block-stop`
> Data: `2026-08-11`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O lembrete de microdecisão do fim de turno do Claude (`Stop → harness decisions --gate`) deixa de emitir o JSON `{"decision":"block",...}` que trava um turno por sessão. O veredito do gate passa a advisory em stderr, na mesma política já vigente no Antigravity, e a garantia de registro permanece integralmente no 3º portão do `encerrar-sessao`, que continua rearmando com trabalho novo. Resolve a queixa do mantenedor de que as interrupções do harness bloqueiam o desenvolvimento: o custo do turno interrompido superou o benefício do aviso com contexto fresco. Reverte parcialmente, por decisão explícita do mantenedor, a política das MD-0015/MD-0016.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/domain.md#2.20` | RN-N44 define o enforcement híbrido em três bordas; a borda (2), hook Stop do Claude, emite soft-block JSON no máximo uma vez por sessão — é exatamente essa borda que esta feature rebaixa a advisory | 🟢 |
| `_reversa_sdd/domain.md#2.21` | RN-N47: dupla identidade anti-loop — lembrete com fingerprint grosso `sha1(âncora)`, portão com fingerprint fino; o teste-guarda `test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio` pina o rearme do portão, que esta feature preserva | 🟢 |
| `_reversa_sdd/domain.md#2.20` (RN-N43/RN-N45) | Avaliação pura em `gate.py`, fail-open barulhento, fingerprints persistidos no estado de sessão e zerados no fechamento — mecânica reaproveitada sem schema novo | 🟢 |
| `_reversa_sdd/code-analysis.md#4` (gate.py) e `#11` (bordas `--gate`/`--sem-decisao`) | O ramo `--gate` do `main.py` reserva o stdout ao JSON de block e move informativos para stderr, com exit 0 sempre; é o ponto único de mudança | 🟢 |
| `_reversa_sdd/domain.md#2.17` (RN-N36..N40) | Fonte única de execução: instalações migradas executam o core do upstream via shim; mudança de comportamento interno propaga sem rematerializar `settings.json` | 🟢 |
| `_reversa_sdd/domain.md#2.5` (RN-N12) | O índice `.harness/microdecisoes.md` é derivado pelo `./harness decisions` no hook Stop; essa função original do hook deve sobreviver à mudança | 🟢 |
| `.harness/decisoes/MD-0015.md` / `MD-0016.md` | O soft-block nasceu na 022 e já foi atenuado na 023 ("um por sessão"); a alternativa "remover o lembrete e confiar só no portão" foi descartada lá — este documento a readota por decisão nova do mantenedor (2026-08-11), com a atenuante de manter o aviso em stderr | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Mantenedor (dev intermitente, via Claude Code) | Trabalhar uma sessão inteira sem nenhum turno interrompido pelo harness | Termina um turno com trabalho substantivo e sem ficha nova; o turno conclui normalmente e o aviso fica em stderr |
| Agente (Claude) | Encerrar a sessão com a garantia de registro intacta | Ao rodar `encerrar-sessao` com pendência de registro, recebe o marker `DECISAO_PENDENTE` e registra a ficha ou declara `--sem-decisao` |
| Base instalada (projetos migrados à fonte única) | Receber o novo comportamento sem intervenção | O shim executa o core do upstream; nenhum `settings.json` precisa ser regravado |

## 4. Regras de negócio novas ou alteradas

1. **RN-01: O hook Stop do Claude nunca bloqueia o turno.** 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.20` (RN-N44, borda 2)
   - Tipo: alterada
   - O ramo `decisions --gate` deixa de escrever `{"decision":"block",...}` no stdout em qualquer circunstância. O enforcement híbrido de três políticas colapsa para duas: garantia dura no encerramento, advisory nos fins de turno (Claude e Antigravity convergem).
2. **RN-02: O veredito pendente vira advisory em stderr, no máximo uma vez por sessão.** 🟡 (escolha desta feature; frequência herdada da semântica da 023)
   - Origem no legado: `_reversa_sdd/domain.md#2.21` (RN-N47)
   - Tipo: alterada
   - Com pendência inédita (fingerprint grosso ainda não gravado), o conteúdo hoje emitido como `reason` passa a aviso em stderr; o fingerprint grosso é gravado como hoje, limitando o aviso a um por sessão. Stdout permanece reservado (fica vazio no caminho advisory) e exit 0 sempre.
3. **RN-03: O 3º portão do `encerrar-sessao` é intocado.** 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.20` (RN-N44 borda 1), `#2.21` (identidade fina)
   - Tipo: preservada (reafirmação explícita de escopo negativo)
   - Bloqueio com marker `DECISAO_PENDENTE`, escape `--sem-decisao`, rearme por trabalho novo (fingerprint fino) e anti-loop "não sanada" permanecem byte a byte; o teste-guarda do rearme continua verde.
4. **RN-04: A reindexação no Stop sobrevive.** 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.5` (RN-N12)
   - Tipo: preservada
   - O hook continua regenerando `.harness/microdecisoes.md` a cada fim de turno; sob `--gate`, erros de integridade seguem em stderr sem derrubar o turno.
5. **RN-05: Contrato externo do hook inalterado; propagação pela fonte única.** 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.17`, `#2.19` (RN-N42, precedente da mudança na fonte)
   - Tipo: nova (restrição de implementação)
   - `ClaudeProfile.hooks_block()`, `_HARNESS_COMMAND_SIGNATURES` e os `settings.json` materializados não mudam: o comando do hook permanece `decisions --gate`. Instalações migradas recebem o comportamento novo pelo shim; instalações pré-migração o recebem no próximo `upgrade` do core.
6. **RN-06: O Antigravity não é tocado.** 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.20` (RN-N44, borda 3)
   - Tipo: preservada
   - O advisory do `agy-hook stop` já tem a política-alvo; nenhuma mudança no `hook_bridge.py`.

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | `decisions --gate` com pendência inédita não escreve nada no stdout e sai com 0 | Must | Teste: pendência real (mudanças sem ficha), fingerprint grosso ausente → stdout vazio, exit 0; nenhum `"decision"` em nenhuma saída | 🟢 |
| RF-02 | O mesmo cenário emite o aviso em stderr com o conteúdo estruturado do marker `DECISAO_PENDENTE` (mudanças, total, ação) e grava o fingerprint grosso no estado | Must | Teste: stderr contém `[HARNESS:DECISAO_PENDENTE` e a ação; `gate_lembrete_fingerprint` persistido = `sha1(âncora)` | 🟢 |
| RF-03 | Segunda avaliação com o mesmo fingerprint grosso não emite o advisory de pendência | Must | Teste: dois `--gate` consecutivos → aviso só no primeiro | 🟢 |
| RF-04 | O portão do encerramento mantém comportamento e testes atuais, incluindo o rearme com trabalho novo | Must | Suíte existente de `test_close_flow.py` verde sem edição de expectativa do portão (ajustes só onde o texto do lembrete era esperado) | 🟢 |
| RF-05 | Nenhum materializador muda: `hooks_block()`, assinaturas e template/snippet permanecem idênticos | Must | Testes de `test_install_claude_settings.py` e `harness_profiles` verdes sem alteração; diff vazio nos assets de settings | 🟢 |
| RF-06 | Registro e reconciliação: ficha `MD-0018` nova; emendas de supersessão nos ADRs 0022/0023 e nota na RN-N44/RN-N47 do `domain.md` ficam agendadas para a reconciliação do `_reversa_sdd/` | Should | Ficha presente em `.harness/decisoes/`; pendência de reconciliação registrada no regression-watch da feature | 🟢 |
| RF-07 | Bump de versão do core (minor) refletindo mudança de comportamento observável da borda Stop | Should | `CORE_VERSION` 2.2.0 → 2.3.0; `harness.toml` do repo sincronizado | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Compatibilidade | Sem schema novo, sem migração: estados com `gate_lembrete_fingerprint` antigo continuam parseáveis e convergem sozinhos | Mesma estratégia autoresolvente da 023 (`_reversa_sdd/domain.md#2.21`) | 🟢 |
| Observabilidade | O rebaixamento não pode ser silencioso demais: o advisory preserva o conteúdo informativo integral do antigo `reason` (erros barulhentos > conveniência) | Princípio operacional do mantenedor; RN-N45 (fail-open barulhento) | 🟢 |
| Segurança do fluxo | Exit 0 sempre sob `--gate`, inclusive em erro interno; o gate jamais derruba um turno por falha própria | Comportamento atual preservado (`_reversa_sdd/code-analysis.md#11`) | 🟢 |
| Desempenho | Nenhuma chamada nova de git ou rede no caminho do Stop | A avaliação do gate já existente é reaproveitada sem etapas extras | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: fim de turno com pendência não interrompe o trabalho
  Dado uma sessão ativa com trabalho substantivo desde a âncora e nenhuma ficha MD nova
  E o fingerprint grosso ainda não gravado no estado
  Quando o hook Stop executa `harness decisions --gate`
  Então o stdout fica vazio e o processo sai com 0
  E o stderr contém o aviso [HARNESS:DECISAO_PENDENTE ...] com a ação sugerida
  E o campo gate_lembrete_fingerprint é persistido no estado de sessão

Cenário: o aviso não se repete na mesma sessão
  Dado o cenário anterior já ocorrido
  Quando o hook Stop executa `harness decisions --gate` novamente com a mesma pendência
  Então nenhum aviso de pendência é emitido e o turno conclui normalmente

Cenário: a garantia dura permanece no encerramento
  Dado uma sessão com pendência de registro
  Quando `encerrar-sessao` roda sem `--sem-decisao`
  Então o fechamento aborta com o marker DECISAO_PENDENTE, como antes desta feature

Cenário: trabalho novo continua rearmando o portão
  Dado um bloqueio anterior do portão e uma ficha não registrada
  Quando novos arquivos são alterados e `encerrar-sessao` roda de novo
  Então o portão bloqueia novamente (identidade fina), comportamento pinado pelo teste-guarda

Cenário (negativo): nenhum block JSON em qualquer circunstância
  Dado qualquer estado de sessão, pendência ou erro interno do gate
  Quando `harness decisions --gate` executa
  Então a string "decision" não aparece no stdout e o exit code é 0
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01..RF-03 | Must | São a feature em si: fim do bloqueio, aviso preservado, sem ruído repetido |
| RF-04..RF-05 | Must | Escopo negativo que protege a garantia dura e a base instalada; sem eles a mudança viraria regressão |
| RF-06 | Should | Rastro de decisão e reconciliação da spec; não bloqueia a entrega do comportamento |
| RF-07 | Should | Sinalização correta de versão para a checagem passiva e a oferta de upgrade |

## 9. Esclarecimentos

> Nenhuma sessão de dúvidas registrada ainda. Rode `/reversa-clarify` quando houver `[DÚVIDA]` pendente.

## 10. Lacunas

- Nenhuma lacuna aberta. A única escolha de desenho em aberto (manter o advisory em stderr versus suprimir o veredito por completo no Stop) foi resolvida neste documento a favor do advisory (RN-02, 🟡): custo de interrupção zero — stderr do Stop não alcança o modelo nem trava o turno — e preserva a observabilidade exigida pelo perfil de erros barulhentos do mantenedor. Reverter para supressão total é remoção de meia dúzia de linhas, sem impacto de contrato.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-08-11 | Versão inicial gerada por `/reversa-requirements` | reversa |
