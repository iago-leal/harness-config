# Roadmap: Aposentar o soft-block do Stop (lembrete de microdecisão vira advisory)

> Identificador: `025-aposentar-soft-block-stop`
> Data: `2026-08-11`
> Requirements: `_reversa_forward/025-aposentar-soft-block-stop/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A mudança é cirúrgica e vive num único ponto: o ramo `decisions --gate` de `main.py` (hoje linhas 375–416). O bloco que serializa `{"decision":"block","reason":...}` no stdout (linhas 399–410) passa a imprimir o mesmo conteúdo em **stderr**, prefixado como aviso; a persistência do fingerprint grosso (linhas 397–398), a reindexação, o fail-open e o `sys.exit(0)` permanecem intactos. Nada muda em `gate.py` (avaliação pura), em `close_flow.py` (portão do encerramento), nos perfis (`harness_profiles.py`), nas assinaturas (`claude_settings.py`) nem no Antigravity (`hook_bridge.py`). Como o comando do hook (`decisions --gate`) não muda, os `settings.json` materializados ficam intocados e a base migrada à fonte única recebe o comportamento novo automaticamente pelo shim. Os dez testes do ramo `--gate` em `test_cli.py:841-957` são retargetados de "stdout contém o JSON de block" para "stdout vazio + stderr contém o advisory". Fecha com ficha `MD-0018`, bump minor do core (2.2.0 → 2.3.0) e agendamento da reconciliação do `_reversa_sdd/`.

## 2. Princípios aplicados

n/a — o projeto não possui `.reversa/principles.md`. Registram-se, ainda assim, os filtros operacionais do mantenedor que a feature atende: **erros barulhentos** (o veredito não é suprimido, migra para stderr com conteúdo integral), **estabilidade** (zero mudança de contrato de instalação, zero migração) e **mínimo de dívida** (nenhum campo, flag ou schema novo).

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Alterar apenas o ramo `--gate` de `main.py`; contrato do hook (`Stop → decisions --gate`) inalterado | Propagação automática à base migrada via fonte única (RN-N36); nenhum materializador ou `settings.json` a regravar; instalações pré-020 convergem no próximo `upgrade` | Remover o hook `Stop` do `ClaudeProfile` (perderia a reindexação do índice, RN-N12, e exigiria rematerializar toda a base); flag de política no toml (YAGNI, já descartada na MD-0016) | 🟢 |
| D-02 | O advisory herda o rate-limit do lembrete: identidade grossa, no máximo uma emissão por sessão, reutilizando `gate_lembrete_fingerprint` | Semântica da 023 já estabelece "um lembrete por pendência ≡ um por sessão"; reuso do campo evita schema novo e mantém a transição autoresolvente | Advisory a cada turno (ruído em stderr sem função); suprimir o veredito por completo (perde observabilidade; ver requirements §10) | 🟢 |
| D-03 | Manter `compute_lembrete_fingerprint`, o campo `fingerprint_lembrete` do `GateVerdict` e o campo persistido no `SessionState` | O mecanismo continua em uso pelo advisory (D-02); aposentá-lo seria mudança de schema sem ganho e quebraria estados existentes no round-trip do serializer (RN-N2) | Limpeza do campo + migração de estados (custo sem benefício) | 🟢 |
| D-04 | Retargetar os testes do ramo `--gate` (`test_cli.py:841-957`) e preservar intocado o teste-guarda do portão (`test_close_flow.py::test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio`) | Os testes do lembrete descrevem o canal (stdout JSON) que muda; o teste-guarda pina a garantia dura que NÃO muda (RF-04) | Escrever suíte paralela nova mantendo a antiga (duplicação de expectativa morta) | 🟢 |
| D-05 | Bump minor 2.2.0 → 2.3.0 em `CORE_VERSION` | Comportamento observável de uma borda muda (o hook deixa de devolver bloqueio); não é patch, não quebra contrato de instalação | Patch 2.2.1 (subdimensiona a mudança de comportamento); major (nada é incompatível) | 🟢 |
| D-06 | O texto do advisory reaproveita `render_decisao_pendente_marker` + a frase de ação atual, prefixados por `Aviso:` | Fonte única do formato do marker (contrato da 022 em `interfaces/decisao-pendente-marker.md`); o conteúdo informativo do antigo `reason` é preservado integralmente (RNF de observabilidade) | Redigir mensagem nova (divergência gratuita do contrato do marker) | 🟢 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| O stderr de um hook `Stop` com exit 0 não alcança o modelo nem trava o turno no Claude Code (é visível ao usuário apenas em modo verboso/transcript) | §10 (fundamento da RN-02); já documentado como fundamento da MD-0015 ("stdout exit 0 não é reinjetado") | Se o Claude Code passar a reinjetar stderr, o advisory voltaria a interromper; mitigação trivial: suprimir a emissão (meia dúzia de linhas) |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Borda CLI do gate (`decisions --gate`) | `.harness/harness-core/src/main.py:375-416` (`_reversa_sdd/code-analysis.md#11`) | regra-alterada | O caminho de pendência inédita troca `print(json block)` por aviso em stderr; resto do ramo intocado |
| Enforcement híbrido (RN-N44) | `_reversa_sdd/domain.md#2.20` | regra-alterada | De três políticas para duas: garantia dura no encerramento; advisory nos fins de turno (Claude e Antigravity convergem) |
| Testes da borda `--gate` | `.harness/harness-core/tests/test_cli.py:841-957` | contrato-alterado | Expectativas migram de stdout-JSON para stdout-vazio + stderr-advisory |
| Avaliação pura do gate | `.harness/harness-core/src/core/decisions/gate.py` | inalterado (escopo negativo) | Nenhuma linha muda; registrado para proteger o portão |
| Portão do encerramento | `.harness/harness-core/src/core/session/close_flow.py` | inalterado (escopo negativo) | Identidade fina, rearme e `--sem-decisao` preservados byte a byte |
| Perfis e assinaturas | `harness_profiles.py`, `claude_settings.py` | inalterado (escopo negativo) | `hooks_block()` e `_HARNESS_COMMAND_SIGNATURES` idênticos; nenhum settings regravado |

## 6. Delta no modelo de dados

- Resumo das mudanças: nenhum campo novo, removido ou migrado. `gate_lembrete_fingerprint` muda apenas de consumidor semântico (limitava o block; passa a limitar o advisory). Transição autoresolvente idêntica à da 023.
- Detalhe completo em: `_reversa_forward/025-aposentar-soft-block-stop/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Saída do hook `Stop → harness decisions --gate` | arquivo (stdout/stderr de hook do Claude Code) | `_reversa_forward/025-aposentar-soft-block-stop/interfaces/stop-gate-stdout.md` |

## 8. Plano de migração

1. n/a para dados e settings: sem schema novo, sem regravação de `settings.json`.
2. Propagação de código: instalações na fonte única recebem o comportamento no ato (shim executa o upstream); instalações pré-020 no próximo `upgrade`; o core-raiz de `~/dev` converge via `.harness/upgrade-raiz.sh` (fluxo já acumulado das MD-0015/0016/0017, incluindo o T028 pausado da feature 024).
3. Estados de sessão existentes com `gate_lembrete_fingerprint` gravado: nenhum tratamento — se o fingerprint da sessão corrente já estiver gravado, nem advisory é emitido (comportamento correto: o aviso da sessão já foi dado).

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Queda na taxa de registro de microdecisões (o lembrete com contexto fresco era o argumento da MD-0016 contra esta remoção) | médio | média | O portão duro do encerramento permanece com rearme por trabalho novo; o advisory preserva o conteúdo em stderr; se a taxa cair, reverter é reintroduzir 10 linhas |
| Itens do `regression-watch.md` das features 022/023 vigiam o block JSON e ficarão vermelhos por supersessão | baixo | alta | Registrar a supersessão deliberada no `regression-watch.md` da 025 e na ficha `MD-0018`, como feito nas supersessões anteriores (padrão MD-0014) |
| Menções ao lembrete bloqueante em artefatos derivados (skill `encerrar-sessao`, mini-site, `_reversa_sdd/`) ficarem stale | baixo | alta | Varredura por `decision.*block`/`soft-block` na fase de coding; reconciliação do `_reversa_sdd/` agendada (RF-06) |
| Premissa do §4 falhar em versão futura do Claude Code | baixo | baixa | Supressão trivial da emissão; contrato documentado em `interfaces/stop-gate-stdout.md` |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Suíte completa verde (320 + novos), incluindo o teste-guarda do portão sem alteração
- [ ] `regression-watch.md` gerado, com as supersessões da 022/023 explicitadas
- [ ] Ficha `MD-0018` registrada e índice recompilado
- [ ] Re-extração reversa (reconciliação dirigida) agendada como próximo passo, não bloqueante

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-08-11 | Versão inicial gerada por `/reversa-plan` | reversa |
