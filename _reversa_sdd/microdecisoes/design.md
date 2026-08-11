# Microdecisões (Decisions) — Design Técnico

> Regenerado pelo Writer em 2026-06-24 (Re-extração após a feature 005)
> Foca no COMO a unit é construída, a partir do código legado lido. Escala: 🟢 / 🟡 / 🔴
> **Reconciliação de 2026-08-11 (feature 025):** o ramo `--gate` do driver passou a advisory (stderr `Aviso:`, stdout vazio); `gate.py` e o serviço byte-idênticos. O medidor da 026 reavalia o mesmo gate em leitura pura, sem persistir fingerprint (RN-N52).

## Interface

| Símbolo                              | Assinatura                    | Retorno          | Observação                                                                                           |
| ------------------------------------ | ----------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------- |
| `DecisionService.load_decisions`     | `(directory: str)`            | `List[Decision]` | Lista ordenada de `MD-*.md`; diretório ausente → `[]`; front-matter ausente/inválido → `ValueError`. |
| `DecisionService.validate_integrity` | `(decisions: List[Decision])` | `List[str]`      | Lista de erros; vazia = grafo válido.                                                                |
| `DecisionService.compile_index`      | `(decisions, output, header)` | —                | Deriva backlinks e grava o índice atomicamente.                                                      |
| `evaluate_registration_gate` (022)   | `(git, repo_path, session, config)` | `GateVerdict` | Avaliação pura de pendência de registro; fail-open barulhento (nunca levanta).                       |
| `compute_fingerprint` (022)          | `(anchor, head, dirty)`       | `str`            | Identidade fina `sha1(âncora+HEAD+sujos ordenados)` — portão do encerramento.                        |
| `compute_lembrete_fingerprint` (023) | `(anchor)`                    | `str`            | Identidade grossa `sha1(âncora)` — lembrete do Stop, máx. 1 por sessão.                              |

Driver CLI (`main.py`, subcomando `decisions [--gate]`): `config = load_config(fs)` → `decisoes_dir = config.decisions.dir`, `output_file = config.decisions.index_file`, `header_file = config.decisions.header_file`. Sem literais. Sob `--gate` (hook Stop do Claude): tudo em stderr, **stdout sempre vazio** (advisory desde a 025 — o envelope JSON de soft-block foi aposentado), exit 0 sempre; após indexar, avalia o gate e, quando a identidade grossa é inédita, persiste-a no estado via `CommandService.save_session` **antes** de emitir a linha `Aviso:` em stderr (máx. um aviso por sessão).

## Fluxo Principal

1. **load_decisions(directory):** lista `MD-*.md` ordenados; para cada, split por `---` (front-matter YAML, máx. 3 partes). Extrai `id`, `gancho`, `estado` (default `ativo`); parseia `relacoes` (cada string = `<verbo> <MD-XXXX>`, dois tokens). Diretório ausente → lista vazia; front-matter ausente/YAML inválido → `ValueError`. 🟢
2. **validate_integrity(decisions):** agrega erros — validação individual de cada ficha (`Decision.validate_integrity`: H1 com o ID + 4 seções), auto-relação (`target == self.id`) e aresta órfã (alvo fora do `decision_map`). 🟢
3. **compile_index(decisions, output, header):**
   - Tabela de **verbos inversos**: `refina→refinado-por`, `depende-de→requerido-por`, `estende→estendido-por`, `substitui→substituído-por`, `relaciona→relacionado-com`, `bloqueia→bloqueado-por`; verbo fora da tabela → `inverso-de-<verbo>`.
   - Backlinks ordenados por ID de origem (determinismo).
   - Título extraído do H1 `# MD-XXXX — <título>` por regex.
   - Sub-linha `↳ <saídas> · <entradas>` montada por composição.
   - Cabeçalho opcional concatenado no topo. Gravação **atômica** via `write_file_atomic`. 🟢

4. **evaluate_registration_gate(git, repo_path, session, config) (022):** âncora = `session.commit_hash`; coleta `head`/`dirty`/`changed` via `GitPort` (falha → `GateVerdict(pendente=False, aviso=...)`); universo ordenado = `changed ∪ dirty`; exclui `{state_file, index_file, header_file}`; fichas = prefixo `decisions.dir` + regex `^MD-.*\.md$`; `pendente = bool(mudancas) and not fichas`; preenche os dois fingerprints. 🟢

## Fluxos Alternativos

- **Diretório de decisões ausente:** `load_decisions` retorna `[]` (não erro). 🟢
- **Relação malformada** (≠ dois tokens, verbo fora do conjunto, alvo fora do padrão): `ValueError` no parse (`Relationship`). 🟢
- **Grafo inconsistente:** `validate_integrity` devolve a lista de erros; o driver decide (o índice não deve ser compilado a partir de grafo inválido). 🟡 INFERIDO (política do driver).
- **Verbo de relação sem inverso conhecido:** backlink genérico `inverso-de-<verbo>`. 🟢
- **Gate sob `--gate` com grafo inválido (022):** erros de integridade vão para stderr e o turno NÃO é derrubado (sem a flag: exit 1, byte-idêntico ao comportamento pré-022). 🟢
- **Gate com sessão ausente/inativa ou `require_registration=False`:** silêncio — nenhum veredito é avaliado. 🟢
- **Falha interna do gate no `--gate`:** aviso em stderr, exit 0 — o gate nunca trava o agente (RN-N4/fail-open). 🟢

## Dependências

- `core/domain/models.Decision` / `Relationship` — entidades e validação.
- `core/domain/config.load_config` — origem dos caminhos (no driver).
- `FileSystemPort` — leitura das fichas e gravação atômica do índice.
- `PyYAML` — parse do front-matter.

## Decisões de Design Identificadas

| Decisão                                                       | Evidência no código                                          | Confiança               |
| ------------------------------------------------------------- | ------------------------------------------------------------ | ----------------------- |
| Fichas particionadas + índice derivado (vs banco de decisões) | `core/decisions/service.py`, `.harness/decisoes/`            | 🟢 (ADR 0001)           |
| Caminhos por configuração (`[decisions]`), sem literais       | `service.py` (parâmetros) + `config.py` (`DecisionsSection`) | 🟢 (ADR 0012 / MD-0004) |
| Backlinks por tabela de verbos inversos, ordenados por ID     | `compile_index`                                              | 🟢                      |
| Gravação atômica do índice                                    | `write_file_atomic` (`adapters/fs/local.py`)                 | 🟢                      |
| Gate como avaliação pura, política nas bordas (022)           | `gate.py` (sem `active_harness`), 3 bordas distintas         | 🟢 (ADR 0022 / MD-0015) |
| Dupla identidade fina/grossa por consumidor (023)             | `compute_fingerprint` × `compute_lembrete_fingerprint`       | 🟢 (ADR 0023 / MD-0016) |
| Advisory no fim de turno; portão duro único no encerramento (025) | `main.py` (ramo `--gate`: stderr `Aviso:`, stdout vazio); `gate.py` intocado | 🟢 (ADR 0025 / MD-0018) |

## Estado Interno

Sem estado em memória entre execuções. O "estado" é o conjunto de fichas em `.harness/decisoes/` e o índice derivado `.harness/microdecisoes.md` — ambos versionados no Git. O `decision_map` (id → Decision) é construído por execução durante a validação.

## Observabilidade

- `ValueError` barulhento em front-matter/relação inválidos.
- `validate_integrity` devolve mensagens de erro acionáveis (auto-relação, aresta órfã, seção ausente).
- O cabeçalho do índice (`_cabecalho.md`) declara explicitamente "Não edite à mão".

## Riscos e Lacunas

- 🟢 **T1 (resolvido):** via MCP (`server.py:60`), `load_config` era chamado sem import → `NameError`, e a tool `process_decisions` nunca processava decisões. Corrigido no commit `cf73980` (`from src.core.domain.config import load_config` em `server.py:12`); o caminho configurável passou a ser exercido também pelo MCP.
- 🟡 Diferença sutil: o MCP deriva o `header_file` de `os.path.join(dir, "_cabecalho.md")`, ignorando um eventual override de `header_file` no `harness.toml` (a CLI respeita o override). Inconsistência menor, não bug.
