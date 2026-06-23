# Roadmap: Estado de sessão unificado em `.harness/` com reinjeção de contexto

> Identificador: `004-estado-sessao-unificado`
> Data: `2026-06-23`
> Requirements: `_reversa_forward/004-estado-sessao-unificado/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA
> Decisões: `decisoes/MD-0002.md` (arquitetura), `decisoes/MD-0003.md` (escopo multi-harness)

## 1. Resumo da abordagem

A mudança é um delta sobre o módulo `commands` (`code-analysis.md#2.5`) e o domínio `SessionState` (`models.py`). O `SessionState` ganha um value-object `SessionNarrative`; o arquivo de sessão deixa de ser quatro campos planos e passa a um único `.harness/estado-da-sessao.md` com **front-matter YAML** (header-máquina) mais **corpo Markdown em seções** (a narrativa). O parse/render vira round-trip testável usando `pyyaml` e `pydantic`, ambos já no `requirements.txt` — nenhuma dependência nova. O `cmd resume` passa a emitir, no stdout, o JSON `hookSpecificOutput.additionalContext`, que serve Claude e Gemini CLI sem distinção. O `cmd encerrar-sessao` é portado para a CLI: o agente escreve a prosa, a CLI sela o header-máquina via `GitPort`. Um ponto de seleção por `active_harness` (Strategy, reusando o padrão de `core/install/harness_profiles.py`) escolhe o mecanismo de entrega: hook+`additionalContext` para Claude/Gemini, projeção em arquivo estático (`.agents/rules/estado-sessao.md`) para Antigravity. A máquina de estados `INACTIVE↔ACTIVE` (`state-machines.md#1`) é preservada integralmente.

## 2. Princípios aplicados

> Não há `.reversa/principles.md` formal neste projeto. Aplicam-se os princípios do mantenedor (CLAUDE.md / ALICERCE), usados como crivo.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Alta coesão / SRP | Domínio (`SessionState`+`SessionNarrative`), serialização e entrega por-harness ficam em responsabilidades separadas | respeita |
| Baixo acoplamento | Core emite texto puro; o mecanismo Claude/Gemini/Antigravity vive na borda (RN-N5/RN-N6) | respeita |
| OOP / contratos explícitos | Value-object pydantic + Strategy de saída com interface única | respeita |
| TDD | Propriedade `parse(render(x)) == x` e os três sinks cobertos antes da troca de fiação | respeita |
| SDD | O formato único do arquivo é a spec executável da sessão (ver `interfaces/`) | respeita |
| Erros barulhentos | Parse de estado malformado falha nomeado (RN-N4), não degrada em silêncio | respeita |
| Longevidade / desacoplamento | Local neutro `.harness/`, sem amarra a harness de IA | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Arquivo = front-matter YAML (header-máquina) + corpo Markdown em seções `##` (narrativa) | `pyyaml`+`pydantic` já são dependências; round-trip testável; legível para humano | JSON puro (ilegível como narrativa); regex ad-hoc (frágil, é o atual); TOML (front-matter YAML é convenção de Markdown e já usamos pyyaml em decisões) | 🟢 |
| D-02 | `SessionState` ganha value-object `SessionNarrative` (feito, próximos passos, pendências, ponteiros) | Encapsula a narrativa sem inchar o `SessionState`; round-trip por propriedade | Campos soltos no `SessionState` (vira God-object) | 🟢 |
| D-03 | `cmd resume` emite no stdout o JSON `hookSpecificOutput.additionalContext` (exit 0) | Mesmo envelope serve Claude e Gemini; injeta como system reminder | Plain stdout (mistura status/erro com conteúdo); wrapper `jq` (peça externa desnecessária) | 🟢 |
| D-04 | Strategy de entrega por `active_harness`, reusando `core/install/harness_profiles.py` | Há três consumidores reais; duas famílias (hook / arquivo) | Hardcode Claude (rejeitado, MD-0003); mecanismo único (impossível no Antigravity) | 🟢 |
| D-05 | Antigravity: projeção de `.harness/estado-da-sessao.md` → `.agents/rules/estado-sessao.md`; âncora/status no boot via hook `PreInvocation` do `agy` (a confirmar) | `agy` não injeta stdout; relê markdown estático a cada sessão | MCP resource (exige o agente chamar; servidor a manter) | 🟡 |
| D-06 | `cmd encerrar-sessao` portado: agente edita a prosa, CLI sela o header via `GitPort` | SRP; agente é o autor da narrativa, CLI guarda o contrato/âncora | CLI gera a narrativa (pobre); transporte por stdin/arquivo (cerimônia sem ganho) | 🟢 |
| D-07 | Parse distingue "ausente" (cria sessão nova) de "presente-mas-malformado" (erro nomeado, exit≠0) | RN-N4 / erros barulhentos | Retornar `None` em ambos (mascara corrupção — comportamento atual) | 🟢 |
| D-08 | Serializer e sinks num novo `core/session/`; domínio segue em `core/domain/models.py` | Separa a sessão do `CommandService` genérico (que faz handoff/clarificar) | Tudo no `CommandService` (baixa coesão) | 🟡 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| O `agy` (Antigravity) tem um hook de pré-invocação capaz de rodar `cmd resume` para atualizar âncora/status no boot; na ausência, vale a reinjeção passiva (arquivo já materializado no encerramento, relido no próximo boot) | §10 Lacunas | Médio: sem o hook, o ramo Antigravity não valida divergência de âncora no boot — degrada para reinjeção passiva, ainda funcional |
| Gemini CLI instalado é ≥ 0.25 | §6 RNF (compatibilidade) | Médio: em < 0.25 o hook `SessionStart` não dispara; fallback para projeção em arquivo |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `SessionState` | `code-analysis.md#2.5` / `models.py` | regra-alterada | Ganha `SessionNarrative`; validação de parse barulhenta |
| `CommandService` | `code-analysis.md#2.5` / `commands/service.py` | contrato-alterado | `load/save_session` viram round-trip; `resume` emite JSON; novo `encerrar-sessao` selando header |
| `core/session/` (novo) | — | componente-novo | Serializer (front-matter+corpo) e sinks de entrega por-harness |
| Seleção por harness | `harness_profiles.py` (feat. 003) | componente-novo | Strategy de saída reusando o padrão de perfis |
| `main.py` | `main.py` | contrato-alterado | `session_file` → `.harness/estado-da-sessao.md`; envelope JSON na borda |
| Arquivo de estado | `state-machines.md#1` | contrato-alterado | `ESTADO-DA-SESSAO.md` (raiz, pobre) e `.claude/ESTADO-DA-SESSAO.md` (rico) → `.harness/estado-da-sessao.md` único |

## 6. Delta no modelo de dados

- Resumo das mudanças: `SessionState` passa a carregar uma narrativa estruturada (`SessionNarrative`); o artefato persistido muda de quatro campos planos para front-matter YAML + corpo em seções. Nenhum campo-máquina é removido; a máquina de estados `INACTIVE↔ACTIVE` é preservada.
- Detalhe completo em: `_reversa_forward/004-estado-sessao-unificado/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Formato do arquivo de estado | arquivo | `interfaces/estado-da-sessao-formato.md` |
| Reinjeção de contexto por harness | arquivo/hook | `interfaces/reinjecao-por-harness.md` |

## 8. Plano de migração

1. Criar `core/session/` (serializer + sinks) e estender `SessionState` com `SessionNarrative`, sob TDD (round-trip + parse barulhento) — antes de tocar a fiação.
2. Apontar `main.py` `session_file` para `.harness/estado-da-sessao.md`; `cmd resume` passa a emitir o JSON na borda.
3. Migrar a narrativa de `.claude/ESTADO-DA-SESSAO.md` para `.harness/estado-da-sessao.md` (`git rm` do antigo, `git add` do novo) e apagar o `ESTADO-DA-SESSAO.md` pobre da raiz (untracked).
4. Configurar o gatilho do Gemini (`.gemini/settings.json` com hook `SessionStart`) e a projeção/gatilho do Antigravity (`.agents/rules/estado-sessao.md` + hook de pré-invocação a validar).
5. Teste de fumaça do boot real em cada harness disponível antes de confiar nos hooks (mitiga o dogfooding).

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Dogfooding: a 004 altera o `cmd resume` que roda no `SessionStart` desta própria sessão; um bug quebra o boot | alto | média | TDD antes da fiação; manter exit 0 no caminho feliz; validar `./harness cmd resume` manual antes do hook; rollback trivial |
| Texto solto vaza no stdout e quebra o JSON → Claude/Gemini não injetam | médio | média | Só o JSON no stdout; logs/avisos a stderr; teste cobrindo a saída |
| Gemini CLI < 0.25 no ambiente | médio | média | `gemini --version` no onboarding; fallback para projeção em arquivo |
| Nomes de hook do Antigravity incertos | médio | média | Teste de fumaça; fallback para reinjeção passiva pura |
| Narrativa estoura 10 KB no Claude | baixo | média | Priorizar seções (próximos passos > pendências > feito) e truncar com aviso |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Testes verdes: round-trip `parse∘render`, parse barulhento (ausente vs malformado), os sinks por-harness; suíte total sem regressão
- [ ] Teste de fumaça do boot real nos harnesses disponíveis (estado aparece no contexto)
- [ ] `.claude/ESTADO-DA-SESSAO.md` e `ESTADO-DA-SESSAO.md` da raiz removidos; `.harness/estado-da-sessao.md` versionado com a narrativa migrada
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-plan` | reversa |
