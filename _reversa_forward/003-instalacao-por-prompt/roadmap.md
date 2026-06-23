# Roadmap: Instalação do Harness por Prompt Estruturado

> Identificador: `003-instalacao-por-prompt`
> Data: `2026-06-23`
> Requirements: `_reversa_forward/003-instalacao-por-prompt/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A instalação por colagem nasce como um **novo módulo coeso do core**, `core/install/`, espelhando o padrão de introspecção que o `DocumentationService` já usa para o `doc-gen`. Um `InstallPromptService` compõe o prompt a partir de três fontes derivadas — a superfície da CLI (introspecção do `argparse`), o `active_harness` lido via o modelo `HarnessConfig` (hoje ocioso) e um perfil de ganchos por harness — e o despeja como texto puro no stdout através de um novo subcomando `install-prompt`. Nada de Markdown mantido à mão: o artefato é sempre derivado, fonte única. O wrapper `harness` não muda (repasse genérico). O escopo fica restrito aos ganchos de ciclo de vida do agente; ganchos Git e o porte da reinjeção de contexto do `SessionStart` ficam fora (este último vai para a feature 004).

## 2. Princípios aplicados

> `.reversa/principles.md` **não existe** neste projeto. Não há princípios formais a verificar. O desenho honra os princípios globais do mantenedor (alta coesão, baixo acoplamento, OOP, fonte única, TDD), que ancoraram as decisões do `/reversa-clarify`. Sugestão: rodar `/reversa-principles` para torná-los obrigatórios no fluxo.

| Princípio (global) | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Alta coesão / SRP | Novo módulo `core/install/` isolado, sem misturar com `documentation/`. | respeita |
| Baixo acoplamento | Serviço depende só de `FileSystemPort`; sem acoplamento a infra concreta. | respeita |
| Fonte única | Prompt derivado por introspecção, sem cópia estática paralela. | respeita |
| Mínima dívida | Usa o `HarnessConfig` ocioso (fecha config decorativo); adia o que não é coeso (004). | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Novo módulo `core/install/` com `InstallPromptService(fs)` | Coesão/SRP: instalar é concern próprio, separado de `documentation/`. | (a) enfiar no `DocumentationService` — mistura concerns; (b) script shell solto — acoplado, não testável | 🟢 |
| D-02 | Prompt gerado por introspecção do `argparse` + template renderizado | Fonte única, sem drift; reaproveita o padrão de `DocumentationService.extract_commands`. | Markdown estático mantido à mão | 🟢 |
| D-03 | Ler `active_harness` via o modelo `HarnessConfig` (pydantic) | Fecha a dívida do config decorativo (`HarnessConfig` hoje não é usado). | Re-parsear `harness.toml` à mão (duplica fonte) | 🟢 |
| D-04 | Perfil de ganchos por harness (Strategy) | Extensível para claude/gemini/antigravity sem `if` espalhado; OOP. | Hardcode só claude (fere RF-06) | 🟡 |
| D-05 | Saída como texto puro no stdout | Maximiza o "colável"; sem efeito colateral em disco. | Gravar arquivo (efeito colateral, menos portátil) | 🟢 |
| D-06 | Ganchos aplicados no nível do **projeto** (`.claude/settings.json`), nunca em `~/.claude` | Não tocar config global protegida; consistente com o corte já feito (MD-0001). | Editar config global do host | 🟡 |

## 4. Premissas

> Nenhum `[DÚVIDA]` ficou aberto no `requirements.md`. As premissas abaixo derivam de decisões de plano, não de dúvidas não resolvidas.

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| O mecanismo de hooks do gemini segue a ponte `context.*` descrita no ALICERCE; o do antigravity ainda não é conhecido. | §5 RF-06, §9 ressalva | Perfil multi-harness incompleto; antigravity fica 🔴 até confirmação. |
| Os ganchos são sempre do projeto, não globais. | §4 RN-03, D-06 | Editar `~/.claude` por engano romperia config global. |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `InstallPromptService` | `_reversa_sdd/architecture.md#1-estilo-de-arquitetura` | componente-novo | Módulo `core/install/` que renderiza o prompt por introspecção + perfil de harness. |
| Perfis de harness | `_reversa_sdd/architecture.md#1-estilo-de-arquitetura` | componente-novo | Strategy por `active_harness` que produz o bloco de ganchos e as instruções de aplicação. |
| CLI `main.py` | `_reversa_sdd/code-analysis.md#2-detalhamento-tecnico-por-submodulo` | regra-alterada | Novo subcomando `install-prompt` (parser + handler). |
| `HarnessConfig` | `_reversa_sdd/domain.md` (config) | regra-alterada | Deixa de ser ocioso: passa a ser a fonte de `active_harness`. |
| Suite de testes | `_reversa_sdd/architecture.md#1-estilo-de-arquitetura` | componente-novo | `tests/test_install.py` (TDD) valida o prompt por harness. |

## 6. Delta no modelo de dados

- Resumo das mudanças: nenhuma entidade persistente nova. A feature passa a **consumir** `HarnessConfig.harness.active_harness` (já modelado, antes ocioso). Nenhum campo novo, nenhuma migração.
- Detalhe completo em: `_reversa_forward/003-instalacao-por-prompt/data-delta.md`

## 7. Delta de contratos externos

> Nenhum contrato externo (HTTP, fila, gRPC, GraphQL) é afetado. O prompt é texto no stdout, consumido por colagem humana. Diretório `interfaces/` omitido.

## 8. Plano de migração

1. n/a — a feature é puramente aditiva (novo subcomando). Instalações existentes não exigem migração; a idempotência (RN-02) é responsabilidade das instruções do próprio prompt.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Mecanismos de hook divergem por harness (gemini `context.*`, antigravity desconhecido) | médio | médio | claude completo e testado; gemini documentado; antigravity marcado 🔴, não bloqueia o caso primário. |
| Parte templada (venv/pip/chmod) diverge da realidade com o tempo | médio | baixo | health-check executável valida a realidade; manter passos templados mínimos. |
| Agente cola o prompt e edita `~/.claude` por engano | médio | baixo | o prompt aponta explicitamente para o `.claude/settings.json` do projeto e proíbe tocar a config global. |
| Regressão do `SessionStart` (MD-0001) esquecida até a 004 | baixo | médio | health-check sinaliza a lacuna; RN-05; dependência registrada. |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `./harness install-prompt` imprime um prompt completo, ordenado e parametrizado por `active_harness`
- [ ] `tests/test_install.py` verde, cobrindo o conteúdo do prompt por harness e a seção de health-check
- [ ] O prompt aponta para o `.claude/settings.json` do projeto e não instrui edição de `~/.claude`
- [ ] O health-check do prompt sinaliza explicitamente a lacuna do `SessionStart` (RN-05)
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-plan` | reversa |
