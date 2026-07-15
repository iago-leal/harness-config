# Roadmap: Granularidade do lembrete do gate de registro (rearme estável por pendência)

> Identificador: `023-granularidade-lembrete-gate`
> Data: `2026-07-15`
> Requirements: `_reversa_forward/023-granularidade-lembrete-gate/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

O gate de registro (feature 022) tem **um avaliador e dois consumidores**: o lembrete de fim de turno (`decisions --gate`, borda Claude) e o 3º portão do encerramento (`SessionCloseFlow.run`). Hoje ambos usam a mesma identidade anti-loop — `sha1(âncora + HEAD + sujos)` — e é essa finura que faz o lembrete rearmar a cada arquivo tocado. A abordagem é **separar as identidades**: o lembrete passa a usar uma identidade grossa derivada só da âncora da sessão (estável do início ao fim → no máximo um lembrete por sessão), enquanto o portão mantém intacta a identidade fina (trabalho novo continua rearmando a garantia dura). Nenhum campo de estado novo, nenhuma flag nova, nenhuma mudança no formato do stdout: o delta é uma função pura nova em `gate.py`, um campo novo no `GateVerdict` e a troca de qual identidade o ramo `--gate` do `main.py` compara e persiste. A transição de versão é autoresolvente: o valor antigo gravado em `gate_lembrete_fingerprint` nunca coincide com a composição nova, então o primeiro fim de turno pós-atualização emite no máximo um lembrete e converge. Execução por TDD: testes vermelhos primeiro — incluindo o que reproduz a queixa — depois o green.

## 2. Princípios aplicados

> `.reversa/principles.md` não existe neste projeto. Aplicam-se os princípios globais do mantenedor (CLAUDE.md).

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Alta coesão | Lembrete e portão seguem compartilhando o mesmo avaliador de pendência; só a identidade anti-loop de cada consumidor difere, e ambas nascem no domínio (`gate.py`) | respeita |
| Baixo acoplamento | O core permanece agnóstico ao harness (RN-N5); a borda escolhe qual identidade consumir | respeita |
| Mínimo de dívida técnica | Zero campos de estado novos, zero flags novas, zero código de migração | respeita |
| TDD | Red antes de green, por exigência da meta da sessão; o teste-queixa entra primeiro | respeita |
| Erros barulhentos | Fail-open com aviso em stderr preservado byte a byte | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Separar as identidades anti-loop: lembrete usa identidade grossa (âncora), portão mantém `verdict.fingerprint` fino | RF-03 exige o portão intacto — é o fingerprint fino que faz trabalho novo rearmar a garantia dura (`close_flow.py` linhas 376-388); só o canal de conveniência acalma | Mudar `compute_fingerprint` globalmente (enfraqueceria o portão: mais trabalho sem ficha deixaria de rearmá-lo); carência por contador de turnos (relógio disfarçado, descartado no clarify) | 🟢 |
| D-02 | Identidade do lembrete = `sha1(âncora)`, computada por função pura nova em `gate.py` e exposta como campo `fingerprint_lembrete` do `GateVerdict` | Regra de domínio fica no domínio; o `GateVerdict` já é o contrato entre avaliador e bordas; sha1 mantém uniformidade com o campo irmão | Armazenar a âncora crua no estado (quebra a uniformidade dos dois campos-fingerprint); computar a identidade na borda `main.py` (vazaria regra de domínio para a borda) | 🟢 |
| D-03 | Nenhuma mudança de schema: reutilizar o campo `gate_lembrete_fingerprint` do `SessionState`, trocando só o valor gravado | O campo já existe (022/D-03) e a comparação por desigualdade absorve o formato antigo — transição autoresolvente (RF-05, esclarecimento Q4) | Campo novo + código de migração (complexidade sem ganho); limpar o campo no upgrade (upgrade não toca estado de sessão, por design) | 🟢 |
| D-04 | Política fixa no core, sem flag nova; `decisions.require_registration` segue como único botão | Esclarecimento Q3: superfície de configuração sem demanda comprovada é dívida; tornar configurável depois não quebra contrato | Flag `decisions.lembrete_policy` no toml (YAGNI) | 🟢 |
| D-05 | Bump do core 2.1.0 → 2.1.1 (patch); materializadores intocados | Nenhum contrato externo muda: o comando do hook, o formato do stdout e os textos de help são os mesmos; muda só a política interna de emissão | Bump minor (reservado a contrato novo, padrão da 022) | 🟢 |
| D-06 | Teste explícito de não-regressão do portão: trabalho novo sem ficha após um bloqueio do portão deve bloquear de novo | É o risco nº 1 da feature (enfraquecer a garantia dura por engano); a suíte da 022 cobre o anti-loop, mas não o rearme por dirty novo no portão | Confiar só na suíte existente | 🟢 |
| D-07 | Registro da decisão de política como ficha MD-0016, estendendo MD-0015 | Decisão não óbvia (granularidade por sessão vs. por commit) tomada por delegação com critérios; o gate da 022 existe exatamente para isso | Deixar só nos esclarecimentos do requirements (menos rastreável no índice de decisões) | 🟢 |

## 4. Premissas

Nenhuma — o `requirements.md` está sem marcadores `[DÚVIDA]` após o clarify de 2026-07-15.

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Gate de registro (domínio) | `.harness/harness-core/src/core/decisions/gate.py` | regra-alterada | Nova função pura `compute_lembrete_fingerprint(anchor)`; `GateVerdict` ganha `fingerprint_lembrete`; `compute_fingerprint` fino intocado |
| Ramo `decisions --gate` (borda CLI) | `.harness/harness-core/src/main.py` | regra-alterada | Compara e persiste `verdict.fingerprint_lembrete` em vez de `verdict.fingerprint`; resto do ramo byte-idêntico |
| 3º portão do encerramento | `.harness/harness-core/src/core/session/close_flow.py` | sem mudança (guardado por teste) | Continua em `verdict.fingerprint` fino; D-06 pina o comportamento |
| Advisory do Antigravity | `.harness/harness-core/src/adapters/antigravity/hook_bridge.py` | sem mudança | Advisory em stderr não bloqueia (RN-N26); frequência de log não é a queixa |
| Suíte de testes | `.harness/harness-core/tests/` | componente-novo (casos) | Casos novos em `test_decision_gate.py`, `test_cli.py`, `test_close_flow.py` |

## 6. Delta no modelo de dados

- Resumo das mudanças: nenhum campo criado ou removido; muda apenas a **semântica do valor** gravado em `SessionState.gate_lembrete_fingerprint` (de composição fina âncora+HEAD+sujos para hash da âncora). `gate_encerramento_fingerprint` inalterado.
- Detalhe completo em: `_reversa_forward/023-granularidade-lembrete-gate/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Soft-block do fim de turno (stdout JSON do hook Stop) | arquivo/stdout | `_reversa_forward/023-granularidade-lembrete-gate/interfaces/stop-gate-lembrete.md` |

## 8. Plano de migração

n/a — transição autoresolvente (D-03): o primeiro fim de turno pós-atualização com pendência emite no máximo um lembrete e o estado converge. A base instalada herda o comportamento pelo fluxo normal de atualização do core (pendência já registrada de propagação, fora do escopo desta feature).

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Enfraquecer o portão do encerramento por engano (trocar a identidade errada) | alto | baixo | D-06: teste explícito de rearme do portão com trabalho novo; RF-03 na suíte |
| Lembrete calar demais: sessões muito longas com várias decisões recebem um único aviso | baixo | médio | Aceito por design (RN-01/RN-03); a garantia real é o portão; reavaliável em feature futura se incomodar |
| Sessão com âncora vazia/ilegível | baixo | baixo | Fail-open barulhento já existente (RN-05 da 022); `sha1("")` é constante → no máximo 1 lembrete |
| Base instalada continua no comportamento antigo até o upgrade | médio | certo | Só este repo tem o gate materializado hoje (verificado na varredura); propagação já é pendência conhecida |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Suíte completa verde (293 + casos novos), com os testes novos tendo nascido vermelhos (TDD)
- [ ] Smoke real do `onboarding.md` (cenários A–E) verde
- [ ] `regression-watch.md` gerado
- [ ] Ficha MD-0016 registrada e índice regenerado
- [ ] Core em 2.1.1

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-07-15 | Versão inicial gerada por `/reversa-plan` | reversa |
