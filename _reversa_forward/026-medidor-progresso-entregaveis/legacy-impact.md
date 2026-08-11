# Legacy Impact: medidor de progresso de entregáveis

> Identificador: `026-medidor-progresso-entregaveis`
> Data: `2026-08-11`
> Âncora da extração: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`

## Arquivos afetados

| Arquivo afetado | Componente (`_reversa_sdd/architecture.md`) | Tipo | Severidade | Justificativa |
|-----------------|---------------------------------------------|------|------------|---------------|
| `.harness/harness-core/src/core/progress/service.py` | Componente novo — serviço de medição (hexagonal, core puro) | componente-novo | MEDIUM | `ProgressService.measure` computa a `Medicao` das quatro fontes em leitura pura; nenhum estado próprio, nenhuma escrita |
| `.harness/harness-core/src/core/progress/stages.py` | Componente novo — paridade com o skill `reversa-requirements` | componente-novo | MEDIUM | Implementação em código da tabela de estágio físico e da regra de contagem de checkboxes que vivem em prosa no skill; ponto único de paridade |
| `.harness/harness-core/src/core/progress/render.py` | Componente novo — renderizadores | componente-novo | LOW | Projeções markdown (sem timestamp, sem caminho absoluto) e JSON (com `aferido_em`) da mesma `Medicao` |
| `.harness/harness-core/src/main.py` (parser nº 13 + ramo `progress`) | Borda CLI (`main.py`) | regra-nova | MEDIUM | Novo subcomando com três modos (padrão / `--json` / `--em-hook`, mutuamente exclusivos) e contrato de exit codes 0/1/2; toda escrita do artefato vive na borda |
| `.harness/harness-core/src/core/domain/config.py` | Domínio — configuração canônica | regra-nova | LOW | `ProgressSection` (`[progress].file`, default `.harness/progresso.md`) com herança sem migração; `version` 2.3.0 → 2.4.0 |
| `.harness/harness-core/tests/test_progress_stages.py`, `tests/test_progress_service.py`, `tests/test_cli.py` (append) | Suíte de testes | componente-novo | LOW | 32 testes novos (10 stages, 14 serviço/render, 8 CLI em subprocesso real); suíte total 352 |
| `.harness/decisoes/MD-0019.md` | Governança — microdecisões | componente-novo | LOW | Ficha da decisão; relações `relaciona MD-0018` e `refina MD-0013` |
| `.harness/progresso.md` | Artefato derivado novo (nível projeto, não core) | delta-de-dados | LOW | Primeiro artefato versionado 100% recomputável das fontes; regravado apenas quando o estado muda |
| `.reversa/active-requirements.json` (campo `current-stage`) | Dados do Reversa (gerenciados) | delta-de-dados | LOW | Correção de metadado informativo (`requirements` → `coding`) após o próprio medidor apontar a divergência no smoke; a fonte foi corrigida, não o achado suprimido |

## Diff conceitual por componente

**Serviço de medição (`core/progress/`).** Componente inteiramente novo, aditivo: nenhuma linha de código pré-existente do domínio mudou de comportamento. O serviço lê `.reversa/active-requirements.json` (feature ativa, pausadas), os artefatos físicos de `_reversa_forward/*` (estágio físico via `stages.py`, checkboxes por fase), os `regression-watch.md` (marca "pendência de reconciliação" vira alerta média) e o estado do harness (sessão via `CommandService.load_session`, fichas MD por listagem, gate de registro reavaliado por `evaluate_registration_gate` em leitura pura, sem persistir fingerprint). Divergência entre estágio declarado e físico vira alerta alta persistente (`coding` declarado casa com `coding-em-progresso` físico); fonte ausente é `n/a` legítimo; fonte presente mas ilegível é falha real.

**Borda CLI (`main.py`).** O ramo `progress` concentra toda a escrita: modo padrão regrava `[progress].file` somente quando o conteúdo muda; `--em-hook` regrava artefato defasado e sai com 1 instruindo o re-commit, alerta grave vira aviso em stderr sem jamais bloquear (o exit 3 do medidor original de comentarios-concursos NÃO foi transplantado, D-03: bloqueio duro continua exclusivo do portão de encerramento, MD-0018); falha real ecoa `Erro de leitura:` e sai com 2 SEM regravar, preservando o artefato bom. `--json` carimba `aferido_em` porque stdout não é versionado.

**Instalação/materializadores.** Nenhum: o comando novo chega à base migrada pela fonte única (shim → upstream) sem rematerializar nada. O modo `--em-hook` existe na CLI, mas nenhum hook git foi instalado ou alterado nesta feature; a adoção no pre-commit é decisão por projeto.

## Preservadas (regras 🟢 do `_reversa_sdd/domain.md` intactas)

- RN-N43 — avaliação pura do gate: reusada como consumidor read-only, sem alteração no `gate.py`.
- RN-N44 (pós-025, duas políticas) — o medidor não cria terceira política de bloqueio; `--em-hook` falha apenas por artefato defasado, nunca por alerta.
- RN-N45/N47 — fingerprints do lembrete/portão: intocados; o medidor não persiste identidade nenhuma.
- RN-N12 — índice de decisões derivado: inalterado; o medidor apenas conta fichas por listagem.
- RN-N36..N40 — fonte única (shim, upstream, migrate, versão canônica): inalterada; o bump 2.4.0 segue o fluxo padrão.
- RN-N26 — ganchos do Antigravity: fora do escopo, byte-idênticos.

## Modificadas

- Nenhuma regra 🟢 do `_reversa_sdd/domain.md` foi alterada ou removida: a feature é aditiva. A defasagem estrutural é de COBERTURA, não de contradição: o `domain.md` e o `architecture.md` ainda não descrevem o componente `core/progress/` nem o artefato `.harness/progresso.md` (ver pendência no `regression-watch.md`).
