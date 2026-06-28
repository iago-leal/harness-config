# Roadmap: Corrige o caminho de materialização do workflow Antigravity

> Identificador: `017-caminho-workflow-antigravity`
> Data: `2026-06-27`
> Requirements: `_reversa_forward/017-caminho-workflow-antigravity/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Delta cirúrgico no materializador de slash commands de sessão (features 010/012). O `AntigravityProfile.session_command_artifact` passa a devolver `.agent/workflows/encerrar-sessao.md` (singular) em vez de `.agents/workflows/` (plural), e o frontmatter perde o campo `name`, restando apenas `description`. Para projetos já instalados, a migração dispensa script próprio: o `upgrade` já reexecuta `apply_local_materializers` com o código recém-copiado (subprocesso fresco, feature 012), gravando no caminho certo; basta a rotina `materialize_session_commands` remover, na mesma passada, o arquivo órfão do caminho plural. A remoção é não-destrutiva: cada perfil declara quais caminhos legados limpar e a rotina remove só esse arquivo, nunca o diretório nem outros `.md`. Bump 1.2.53 → 1.2.54 para o upgrade propagar o código novo.

## 2. Princípios aplicados

Não há `.reversa/principles.md`; aplico os princípios globais do mantenedor (CLAUDE.md). Categoria (P4): **Aplicação** — o `harness-core` tem usuário e evolui; rigor pleno, proporcional ao tamanho do fix.

| Princípio                            | Como a feature se relaciona                                                                                                                    | Status   |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| P4 — Proporcionalidade               | Fix pequeno e localizado; sem novas camadas, reaproveita o pipeline de materialização existente.                                               | respeita |
| P5 — Alta coesão / baixo acoplamento | O conhecimento dos caminhos (atual e legado) fica no `HarnessProfile`; a rotina `materialize_session_commands` permanece agnóstica ao harness. | respeita |
| P5.2 — Erro barulhento               | Gravação atômica e remoção falham de forma explícita (a porta FS propaga exceção).                                                             | respeita |
| Non-destructive (Reversa/Harness)    | A limpeza remove apenas o `encerrar-sessao.md` que o Harness gera; nunca toca terceiros nem diretórios.                                        | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                                                                                                   | Justificativa                                                                                                 | Alternativas descartadas                                                                              | Confidência |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ----------- |
| D-01 | `AntigravityProfile.session_command_artifact` devolve `.agent/workflows/encerrar-sessao.md` (singular).                                                                                                                                                   | Caminho reconhecido pelo loader de slash commands do Antigravity (IDE e CLI).                                 | `.agents/` plural (não reconhecido); suportar ambos gravando dois arquivos (duplica e suja).          | 🟢          |
| D-02 | Remover a linha `name:` do frontmatter; manter só `description`.                                                                                                                                                                                          | Adere ao mínimo documentado pela doc oficial; espelha o `ClaudeProfile`.                                      | Manter `name` (tolerado, mas risco residual de parse).                                                | 🟢          |
| D-03 | Novo método `stale_session_command_paths() -> list[str]` no `HarnessProfile` (default `[]`); `AntigravityProfile` devolve `[".agents/workflows/encerrar-sessao.md"]`. `materialize_session_commands` remove cada caminho existente, sem tocar diretórios. | Mantém a rotina agnóstica ao harness; o perfil é dono dos seus caminhos; extensível a futuros perfis.         | Hardcode da limpeza na rotina (acopla ao Antigravity); remover o diretório vazio (risco a terceiros). | 🟢          |
| D-04 | Bump 1.2.53 → 1.2.54 nos pontos sincronizados (`config.py`, `init_service.py`, asserção em `tests/test_init.py`).                                                                                                                                         | O `upgrade` só regrava materializadores quando detecta versão nova; sem bump, consumidores não recebem o fix. | Não versionar (upgrade não propaga).                                                                  | 🟢          |
| D-05 | Sem script de migração dedicado; reaproveita `apply_local_materializers` chamado pelo `upgrade` (feature 012).                                                                                                                                            | A migração é gravar-no-novo + remover-o-velho, ambos já no caminho de materialização.                         | Migração one-shot separada (redundante).                                                              | 🟢          |

## 4. Premissas

Nenhuma `[DÚVIDA]` ficou em aberto (todas resolvidas no clarify). Registro apenas a premissa técnica de fundo:

| Premissa                                                                                       | Origem (`requirements.md` seção)                    | Risco se errada                                                                                                                            |
| ---------------------------------------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| O Antigravity reconhece `.agent/workflows/` (singular) em todas as versões-alvo do mantenedor. | §2.1 Diagnóstico (glob do app + evidência empírica) | Baixo: o singular é o denominador comum de todos os seletores observados; se uma versão futura exigir plural, reabre-se como nova feature. |

## 5. Delta arquitetural

| Componente                                    | Arquivo de origem no legado                                                               | Tipo de mudança               | Resumo                                                                        |
| --------------------------------------------- | ----------------------------------------------------------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------- |
| `AntigravityProfile.session_command_artifact` | `.harness/harness-core/src/core/install/harness_profiles.py` (L174–191)                   | contrato-alterado             | Caminho singular + frontmatter sem `name`.                                    |
| `HarnessProfile` (base)                       | `.harness/harness-core/src/core/install/harness_profiles.py` (L6–31)                      | contrato-novo                 | Método `stale_session_command_paths()` com default `[]`.                      |
| `materialize_session_commands`                | `.harness/harness-core/src/core/install/session_commands.py`                              | componente-alterado           | Após gravar, remove caminhos legados declarados pelo perfil (não-destrutivo). |
| Versão do core                                | `src/core/domain/config.py`, `src/core/bootstrap/init_service.py`                         | regra-alterada                | 1.2.53 → 1.2.54.                                                              |
| `comandos-customizados` (spec extraída)       | `_reversa_sdd/comandos-customizados/requirements.md#f010`; `_reversa_sdd/adrs/0017-...md` | contrato-alterado (follow-up) | Reconciliação para o caminho singular via re-extração posterior.              |

## 6. Delta no modelo de dados

- Resumo das mudanças: não há modelo de dados de runtime. O delta é de **artefato materializado no filesystem do consumidor** (caminho e frontmatter do arquivo de workflow) e da constante de versão.
- Detalhe completo em: `_reversa_forward/017-caminho-workflow-antigravity/data-delta.md`

## 7. Delta de contratos externos

| Contrato                                                 | Tipo    | Arquivo de detalhe                                                                              |
| -------------------------------------------------------- | ------- | ----------------------------------------------------------------------------------------------- |
| Arquivo de workflow consumido pelo Antigravity (IDE/CLI) | arquivo | `_reversa_forward/017-caminho-workflow-antigravity/interfaces/antigravity-workflow-contract.md` |

## 8. Plano de migração

1. **`init`** (projeto novo): grava automaticamente em `.agent/workflows/encerrar-sessao.md`; nenhum órfão a limpar.
2. **`upgrade`** (projeto existente): detecta versão nova → reexecuta `apply_local_materializers` com o código fresco → grava no singular e remove `.agents/workflows/encerrar-sessao.md` se existir, preservando outros `.md`.
3. **Follow-up (fora do código)**: re-extração (`/reversa`) reconcilia `comandos-customizados/requirements.md#f010` e o ADR 0017, que ainda registram o caminho plural.

## 9. Riscos e mitigações

| Risco                                                                                      | Impacto | Probabilidade | Mitigação                                                                                              |
| ------------------------------------------------------------------------------------------ | ------- | ------------- | ------------------------------------------------------------------------------------------------------ |
| Perfis fake nos testes não implementam `stale_session_command_paths`.                      | baixo   | baixa         | Default `[]` na base `HarnessProfile`; nenhum chamador é obrigado a sobrescrever.                      |
| Versão futura do Antigravity migrar workflows para `.agents/` plural (como fez com rules). | médio   | baixa         | O singular é reconhecido por todos os seletores observados; monitorar e reabrir feature se necessário. |
| Diretório `.agents/workflows/` fica vazio após a limpeza.                                  | baixo   | média         | Inócuo; a rotina remove apenas arquivos, nunca diretórios.                                             |
| Spec extraída (`comandos-customizados`, ADR 0017) fica divergente até a re-extração.       | baixo   | alta          | Registrado como follow-up no plano de migração; não bloqueia o fix.                                    |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `AntigravityProfile` grava `.agent/workflows/encerrar-sessao.md` sem `name:` (teste verde)
- [ ] `materialize_session_commands` remove o órfão plural e preserva terceiros e diretório (teste verde)
- [ ] Versão 1.2.54 sincronizada nos três pontos (teste de versão verde)
- [ ] Suíte do core verde + smoke: `init` em sandbox antigravity grava no singular; `upgrade` migra e limpa
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa (recomendada, não obrigatória) para reconciliar a spec

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-06-27 | Versão inicial gerada por `/reversa-plan` | reversa |
