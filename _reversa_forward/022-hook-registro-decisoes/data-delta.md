# Data Delta — 022-hook-registro-decisoes

> Diff conceitual sobre o modelo extraído em `_reversa_sdd/erd-complete.md`. Sem banco relacional: a "persistência" é front-matter YAML + TOML (arquivos versionados).

## 1. `SessionState` (front-matter de `.harness/estado-da-sessao.md`)

| Campo | Tipo | Default | Novo/alterado | Semântica |
|-------|------|---------|---------------|-----------|
| `gate_lembrete_fingerprint` | `Optional[str]` | `None` | **novo** | Último estado de pendência já lembrado no `Stop` (Claude). Fingerprint igual → não bloqueia de novo (D-04). |
| `gate_encerramento_fingerprint` | `Optional[str]` | `None` | **novo** | Último estado de pendência que já bloqueou um `encerrar-sessao`. Fingerprint igual na tentativa seguinte → conclui com aviso (RF-04). |

- **Fingerprint:** `sha1(âncora + HEAD + "\n".join(sorted(caminhos_sujos)))` — determinístico, sem relógio.
- **Round-trip (RN-N2):** `parse(render(x)) == x` preservado; campo ausente no YAML → `None` (estados pré-022 continuam válidos, RN-N4).
- **Limpeza:** ambos os campos são zerados no fechamento bem-sucedido da sessão (não vazam para a sessão seguinte).
- **Narrativa (escape, D-05):** o `--sem-decisao` anexa à seção "O que foi feito" a linha padrão `Declarado: sem decisão não óbvia nesta sessão (gate de registro).` — corpo Markdown, não front-matter, legível na retomada (escolha 5a).

## 2. `DecisionsSection` (`[decisions]` do `harness.toml`)

| Campo | Tipo | Default | Novo/alterado | Semântica |
|-------|------|---------|---------------|-----------|
| `require_registration` | `bool` | `True` | **novo** | Liga o gate (bloqueio no encerramento + lembrete no `Stop` + advisory Antigravity). Tomls sem o campo herdam `True` (escolha 3a; mesmo padrão do `inject_decisions_index` da 021). |

## 3. Veredito do gate (em memória, não persistido)

`GateVerdict` (modelo Pydantic novo em `core/decisions/gate.py`): `pendente: bool`, `mudancas: list[str]`, `fichas_tocadas: list[str]`, `fingerprint: str`. Não é gravado em disco — só o fingerprint persiste (§1).

**Conjuntos de entrada:**
- `mudancas` = (`git diff --name-only <âncora> HEAD` ∪ `list_dirty_paths`) − {`session.state_file`, `decisions.index_file`, `decisions.header_file`} − fichas sob `decisions.dir`
- `fichas_tocadas` = elementos do mesmo universo que casam `<decisions.dir>/MD-*.md`
- `pendente` = `mudancas ≠ ∅` **e** `fichas_tocadas = ∅`
- Âncora ausente/ilegível (sessão nova, repo sem commit) → `pendente = False` com aviso (fail-open, RN-05; mesmo padrão do `narrative_is_stale`).

## 4. Migrações necessárias

Nenhuma. Ambos os artefatos toleram a ausência dos campos novos (defaults) e versões antigas do core ignoram campos desconhecidos apenas se o serializer os preservar — como o serializer é do core e o core é fonte única (020), não há janela de esquema misto por projeto.
