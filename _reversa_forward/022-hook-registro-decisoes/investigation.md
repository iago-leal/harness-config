# Investigation — 022-hook-registro-decisoes

> Data: 2026-07-15 · Pesquisa de fundo que sustenta as decisões do `roadmap.md`.

## 1. O canal do `Stop` no protocolo de ganchos do Claude Code

Restrição física que moldou D-04: num gancho `Stop`, a saída padrão com exit 0 **não é reinjetada ao modelo** — vai apenas ao transcript/verbose do usuário. Os únicos mecanismos que alcançam o agente são:

- **exit 2 + stderr** → bloqueia a parada e entrega o stderr ao modelo;
- **stdout JSON `{"decision": "block", "reason": "..."}`** → idem, com `reason` estruturado (forma preferida: determinística e testável);
- `systemMessage` no JSON → aviso ao **usuário**, não ao modelo (não serve ao lembrete).

Consequência: "lembrete não-bloqueante visível ao agente no `Stop`" não existe literalmente no protocolo. A aproximação fiel à intenção é o **soft-block único por estado de pendência**: bloqueia uma vez com a instrução, grava o fingerprint, e o mesmo estado nunca bloqueia de novo. Custo máximo: uma rodada extra por pendência. O critério do RF-08 foi reconciliado no `requirements.md` para refletir isso (Princípio nº 6 do mantenedor: alterar o artefato exige reconciliar a spec).

Contraste com o `SessionStart` (usado pelo `cmd resume`): lá existe `hookSpecificOutput.additionalContext`, que injeta contexto sem bloquear — é por isso que a 021 pôde ser não-intrusiva e esta feature não pode usar o mesmo caminho no `Stop`.

## 2. Precedentes internos reaproveitados

| Precedente | O que ensina | Onde se aplica aqui |
|---|---|---|
| Markers `COMMIT_PENDENTE` (016/019) e `NARRATIVA_PENDENTE` (018) | Protocolo abortar-e-reexecutar mediado pela skill; dualidade TTY × marker | `DECISAO_PENDENTE` é o 3º portão da mesma família (D-01) |
| `narrative_is_stale` (018) | Gate barulhento e não-fechante com fail-open quando não há baseline legível | Mesmo padrão de resiliência do gate de decisão (âncora ausente → permissivo) |
| `inject_decisions_index` (021) | Flag de seção com default `True`, retrocompatível; gate calculado na borda, serviço puro | `require_registration` (D-07) e a separação veredito/interceptação (RN-07) |
| MD-0014 | Mudar a emissão **na fonte** (`hooks_block()`) para o bootstrap não regredir | D-08: `Stop → decisions --gate` emitido pelo perfil |
| MD-0006 | O git `post-merge` invoca `harness decisions` sem argumentos extras | D-09: sem `--gate`, o subcomando permanece byte-idêntico ao atual |
| Memória `smoke-git-real-vs-mock-porcelain` (019) | `git status --porcelain` colapsa subdiretório untracked; mocks mentem | Smoke real obrigatório para `list_changed_paths_since` e o fluxo do gate |
| RN-N26 (009) | `Stop` do Antigravity jamais bloqueia nem emite `continue` | D-06: advisory por `stderr`, stdout `{}` |

## 3. Alternativas de detecção avaliadas

1. **Só working tree sujo (`list_dirty_paths`)** — descartada: o pré-check da 019 força commit antes do fechamento, então no momento do gate a árvore está limpa; o trabalho da sessão só é visível no diff da âncora.
2. **Só diff `âncora..HEAD`** — insuficiente para o lembrete do `Stop` (turno em andamento, trabalho ainda não commitado). A união dos dois cobre ambos os momentos (D-02).
3. **Parsear o transcript do agente em busca de "decisões"** — descartada: acoplamento a formato de terceiro, não-determinístico, viola RN-02 (sinal físico).
4. **Heurística semântica (diff "parece" decisão?)** — descartada: não-determinística; o esclarecimento de 2026-07-15 fixou o sinal como presença/ausência de mudança, com o julgamento de mérito delegado ao escape auditável.

## 4. Persistência do anti-loop: por que no front-matter da sessão

O candidato natural (arquivo scratch `.harness/decision-gate.json`) tem um defeito estrutural descoberto na leitura do `close_flow.py`: `pending_work_paths` exclui **apenas** `session.state_file` — qualquer arquivo novo sob `.harness/` entraria na oferta de commit (RN-N34) e o scratch do gate se tornaria, ele próprio, um `COMMIT_PENDENTE` perpétuo (ou exigiria nova entrada de `.gitignore` em toda a base instalada, como o T7 ensinou a evitar). O estado de sessão já é a exceção consagrada do pré-check e tem serializer com round-trip garantido (RN-N2) — dois campos opcionais resolvem lembrete e encerramento sem artefato novo (D-03).

Fingerprint: `sha1(âncora + HEAD + "\n".join(sorted(dirty)))`. Mudança nova → HEAD ou conjunto sujo mudam → fingerprint muda → o gate volta a valer. Determinístico, sem relógio.

## 5. Ferramentas e dependências

Nenhuma dependência nova: `hashlib` (stdlib), portas existentes + um método novo em `GitPort`. Compatível com o filtro de longevidade do mantenedor (Princípio nº 3) por construção — só stdlib e git.

## 6. Fontes

- `_reversa_sdd/code-analysis.md#8` (close_flow), `#4` (decisions), `#12` (hook_bridge), `#9` (domain)
- `_reversa_sdd/domain.md#2.5`, `#2.11` (RN-N26), `#2.16` (RN-N34), `#2.18` (RN-N41)
- `_reversa_sdd/state-machines.md#1` (gates de aborto pré-INATIVA)
- `.harness/decisoes/MD-0006.md`, `MD-0014.md`
- Documentação de hooks do Claude Code (semântica de `Stop`/`SessionStart`; conhecimento de plataforma, verificar contra a versão corrente na implementação) 🟡
