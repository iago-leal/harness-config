# Legacy Impact: aposentar o soft-block do Stop

> Identificador: `025-aposentar-soft-block-stop`
> Data: `2026-08-11`
> Âncora da extração: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`

## Arquivos afetados

| Arquivo afetado | Componente (`_reversa_sdd/architecture.md`) | Tipo | Severidade | Justificativa |
|-----------------|---------------------------------------------|------|------------|---------------|
| `.harness/harness-core/src/main.py` (ramo `--gate`, ~l.399) | Borda CLI (`main.py`) | regra-alterada | HIGH | O caminho de pendência troca o JSON de bloqueio no stdout por advisory em stderr; muda o comportamento observável de uma borda (RN-N44) |
| `.harness/harness-core/src/main.py` (helps do argparse, l.103-115) | Borda CLI (`main.py`) | regra-alterada | LOW | Textos de ajuda atualizados para descrever o advisory (varredura anti-stale, T007) |
| `.harness/harness-core/tests/test_cli.py` (l.841-975) | Suíte de testes da CLI | delta-de-contrato-externo | MEDIUM | Expectativas dos 3 cenários de bloqueio migram para stdout-vazio + stderr-advisory; asserções de silêncio viram ausência do marker (as-built: informativos já saíam em stderr) |
| `.harness/harness-core/src/core/domain/config.py` (l.13) | Domínio — configuração canônica | regra-alterada | LOW | `version` 2.2.0 → 2.3.0 (D-05); comentário da `DecisionsSection` atualizado para o enforcement em duas políticas |
| `.harness/decisoes/MD-0018.md` | Governança — microdecisões | componente-novo | LOW | Ficha da decisão; relações `substitui MD-0016` e `refina MD-0015` (vocabulário fixo do grafo não admite "reverte-parcialmente") |

## Diff conceitual por componente

**Borda CLI (`main.py`).** O ramo `decisions --gate` mantém toda a mecânica das 022/023 (avaliação pura via `evaluate_registration_gate`, persistência da identidade grossa antes da emissão, reindexação, fail-open, `sys.exit(0)`), mas o desfecho da pendência inédita muda de instrução de bloqueio ao runner (`{"decision":"block","reason":...}` no stdout) para uma linha de aviso em stderr (`Aviso:` + marker da 022 + frase de ação sem "e conclua o turno"). O stdout sob `--gate` passa a ser sempre vazio. O enforcement híbrido colapsa de três políticas para duas: advisory nos fins de turno (Claude converge com o Antigravity, que já era advisory por construção) e bloqueio somente no 3º portão do `encerrar-sessao`.

**Domínio.** Nenhuma lógica de domínio mudou: `gate.py`, `close_flow.py`, serializer e modelos permanecem byte-idênticos (escopo negativo do roadmap §5, conferido no diff). A única alteração em `config.py` é o literal de versão e um comentário.

**Instalação/materializadores.** Nenhum: o comando do hook não mudou, nenhum `settings.json` foi regravado, nenhuma assinatura de merge foi tocada. A propagação à base migrada é automática pela fonte única (shim → upstream); confirmada no smoke (CLI do projeto descartável já reportou v2.3.0 e o comportamento novo sem reinstalação).

## Preservadas (regras 🟢 do `_reversa_sdd/domain.md` intactas)

- RN-N43 — avaliação pura do gate (universo `changed ∪ dirty`, exclusões, fail-open com `aviso`).
- RN-N45 — fingerprints opcionais no estado, round-trip do serializer, zeramento no `close_session`.
- RN-N46 — escape `--sem-decisao` com rastro na narrativa; anti-loop do portão.
- RN-N47 — dupla identidade (grossa para o aviso de fim de turno, fina para o portão).
- RN-N44 (parte dura) — o 3º portão do encerramento bloqueia e rearma com trabalho novo.
- RN-N12 — índice de decisões derivado, recompilado no fim de turno.
- RN-N36..N40 — fonte única (shim, upstream, migrate) inalterada.
- RN-N26 — advisory do Antigravity (`hook_bridge._handle_stop`) inalterado.

## Modificadas

- RN-N44 (parte do lembrete) — "enforcement híbrido em três políticas: portão bloqueante no encerramento, soft-block único no Stop do Claude, advisory no Antigravity" → o soft-block foi aposentado (MD-0018); restam duas políticas. A redação em 🟢 no `domain.md` §2.20 fica deliberadamente defasada até a re-extração dirigida (pendência registrada no `regression-watch.md`).
