# Legacy impact: 023-granularidade-lembrete-gate

> Data: `2026-07-15`
> Identificador: `023-granularidade-lembrete-gate`
> Nota de defasagem: o gate de registro (022) ainda não está reconciliado em `_reversa_sdd/` (re-extração pendente, registrada no estado da sessão). O mapeamento abaixo usa `architecture.md`/`domain.md` onde existem âncoras e os artefatos da 022 + MD-0015 onde a extração ainda não chegou.

## 1. Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `.harness/harness-core/src/core/decisions/gate.py` | Gate de registro (domínio; pós-022, sem âncora em `architecture.md` ainda) | regra-alterada | MEDIUM | Nova função pura `compute_lembrete_fingerprint` e campo `fingerprint_lembrete` no `GateVerdict`; avaliação de pendência intocada |
| `.harness/harness-core/src/main.py` | CLI (driver de borda, `architecture.md` — `main.py`) | regra-alterada | MEDIUM | Ramo `--gate` compara/persiste a identidade grossa; formato do stdout, stderr e exit byte-idênticos |
| `.harness/harness-core/src/core/domain/config.py` | Configuração de domínio | delta-de-dados (metadado) | LOW | Bump `2.1.0 → 2.1.1`; nenhum campo de config novo |
| `.harness/harness-core/tests/test_decision_gate.py` | Suíte | componente-novo (casos) | LOW | 3 testes da identidade grossa |
| `.harness/harness-core/tests/test_cli.py` | Suíte | componente-novo (casos) | LOW | 3 testes do ramo `--gate` (teste-queixa, persistência, transição RF-05) |
| `.harness/harness-core/tests/test_close_flow.py` | Suíte | componente-novo (caso-guarda) | LOW | Pina o rearme do portão com identidade fina (D-06) |
| `.harness/decisoes/MD-0016.md` | Governança (fichas de decisão) | componente-novo | LOW | Registro da política; estende MD-0015 |

## 2. Diff conceitual por componente

**Gate de registro (`core/decisions/gate.py`).** O avaliador de pendência não mudou: mesmo sinal físico, mesmas exclusões, mesmo fail-open barulhento. O que mudou é que o veredito agora carrega **duas identidades anti-loop**: a fina (`fingerprint`, âncora+HEAD+sujos), reservada ao portão do encerramento, e a grossa (`fingerprint_lembrete`, só a âncora), reservada ao lembrete do fim de turno. A dualidade está documentada nos docstrings do módulo.

**Ramo `decisions --gate` (`main.py`).** Troca de uma linha semântica: compara e persiste `verdict.fingerprint_lembrete` em vez de `verdict.fingerprint` no campo `gate_lembrete_fingerprint`. Efeito observável: o soft-block passa de ~1 por arquivo tocado para **no máximo 1 por sessão**. Todo o resto do contrato (JSON de bloqueio, silêncio, stderr, exit 0, saída humana sem `--gate`) é byte-idêntico.

**Portão do encerramento (`close_flow.py`).** **Zero mudança de código** — e isso é deliberado e agora guardado por teste: a identidade fina é o que faz trabalho novo sem ficha rearmar a garantia dura.

## 3. Preservadas (regras 🟢 intactas)

- `_reversa_sdd/domain.md#RN-N26` — ganchos do Antigravity declarativos e não-bloqueantes; advisory do gate intocado.
- `_reversa_sdd/domain.md` (RN-N5, via glossário) — core agnóstico ao harness: a escolha de identidade é da borda; o avaliador continua puro.
- `_reversa_sdd/state-machines.md` (gates de aborto de `ATIVA → INATIVA`) — os três portões do encerramento preservados; o 3º portão inclusive ganhou teste-guarda.
- Contrato do `decisions` sem `--gate` (MD-0006) — saída humana intocada.
- Semântica dos fingerprints zerados no fechamento (022) — inalterada.

## 4. Modificadas

- **"Soft-block no máximo UM por estado de pendência"** (regra da 022 — `_reversa_forward/022-hook-registro-decisoes/requirements.md#RF-08`, MD-0015; ainda sem âncora em `domain.md`): a unidade do anti-loop do **lembrete** muda de "estado de pendência fino" (âncora+HEAD+sujos) para "sessão" (âncora). A mesma regra aplicada ao **portão** permanece fina. Registrada em MD-0016.

Nenhuma regra 🟢 do `domain.md` extraído foi alterada ou removida — a regra modificada nasceu na 022, posterior à última extração.
