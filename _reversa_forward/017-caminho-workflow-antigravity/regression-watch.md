# Regression Watch: feature 017

> Feature `017-caminho-workflow-antigravity` · 2026-06-28
> Itens que devem continuar verdadeiros nas próximas extrações/re-execuções.

## Watch items

| ID   | Origem (arquivo, seção)                                                                                                    | Regra esperada após a mudança                                                                                                  | Tipo de verificação      | Sinal de violação                                                                                                        |
| ---- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| W001 | `src/core/install/harness_profiles.py` (`AntigravityProfile.session_command_artifact`); `domain.md#2.12` (RN-N28/N29)      | O workflow do Antigravity é materializado em `.agent/workflows/encerrar-sessao.md` (singular).                                 | presença/redação         | `session_command_artifact` devolver `.agents/workflows/…` (plural), ou o caminho singular ausente após `init`/`upgrade`. |
| W002 | `src/core/install/harness_profiles.py` (frontmatter do `content`)                                                          | O frontmatter do workflow Antigravity expõe `description` e **não** expõe `name`.                                              | ausência                 | Reaparecer `name:` no frontmatter materializado.                                                                         |
| W003 | `src/core/install/session_commands.py` (`materialize_session_commands`) + `AntigravityProfile.stale_session_command_paths` | A materialização remove o órfão `.agents/workflows/encerrar-sessao.md` e preserva outros `.md` e o diretório (não-destrutivo). | presença (comportamento) | Órfão plural remanescente após `upgrade`, ou workflow de terceiro removido, ou diretório apagado.                        |

## Observações (sem peso de regressão)

- 🟡 Premissa: `.agent/workflows/` (singular) é reconhecido pelo Antigravity em todas as versões-alvo do mantenedor (base: glob do app + evidência empírica). Se uma versão futura migrar workflows para `.agents/` plural (como fez com _rules_), reabrir como nova feature. Não é invariante de código, então fica fora do watch principal.
- A constante de versão (1.2.54) muda a cada feature; não é watch item de regressão.

## Histórico de re-extrações

### Re-extração 2026-06-28 09:45

> ⚠️ **Mecanismo superado pela feature 018 (ADR 0018 substitui a 0017).** A 018 troca o artefato de entrega de **workflow `.md`** para **skill versionável**; os watch da 017 que fixam a _forma do workflow_ deixam de valer **por decisão de produto**, não por regressão acidental. A propriedade essencial — capacidade de encerrar presente no Antigravity, não-destrutiva, footprint zero — foi preservada e ampliada. Candidatos a arquivar quando a 018 estabilizar. Verificação factual: suíte 212 passed, smoke real de `materialize`.

| ID   | Veredito   | Observação                                                                                                                                                                                                                                                                                                                                                                           |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| W001 | 🟡 amarelo | **Superado pela 018:** o workflow `.agent/workflows/encerrar-sessao.md` (singular) deixou de ser materializado — virou a skill `.agents/skills/encerrar-sessao/`. O órfão singular é removido na migração (`stale_session_command_paths`). A presença-no-Antigravity persiste na forma de skill (`domain.md#RN-N28`/N29). Não é regressão acidental; aguarda julgamento p/ arquivar. |
| W002 | 🟡 amarelo | **Revertido deliberadamente pela 018:** o `SKILL.md` da skill expõe `name` **e** `description` (skills exigem `name`). A ausência de `name` era específica do frontmatter de workflow, que não existe mais. Mudança pretendida.                                                                                                                                                      |
| W003 | 🟢 verde   | **Preservado e ampliado:** `materialize_session_skills` remove o órfão plural `.agents/workflows/encerrar-sessao.md` (e o singular) preservando terceiros e o diretório — smoke real: `deploy-de-terceiro.md` intacto. A não-destrutividade segue válida.                                                                                                                            |

### Re-extração 2026-06-28 00:40

> Primeira verificação dos watch items da 017 contra o `_reversa_sdd/` reconciliado (✨f017). Verificação factual: suíte 210 passed, ruff limpo, smoke real A/B verde.

| ID   | Veredito | Observação                                                                                                                                                           |
| ---- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | `domain.md#RN-N29` e `architecture.md` registram `.agent/workflows/encerrar-sessao.md` (singular); `harness_profiles.py` idem; `test_antigravity_profile.py` verde.  |
| W002 | 🟢 verde | Frontmatter do workflow expõe só `description` (sem `name`) no código e no SDD; teste de frontmatter verde.                                                          |
| W003 | 🟢 verde | `materialize_session_commands` remove o órfão `.agents/workflows/encerrar-sessao.md` preservando terceiros e diretório; testes de migração e smoke cenário B verdes. |

## Arquivadas

<!-- Vazio. -->
