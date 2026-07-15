# Regression Watch: feature 018 — encerrar-sessao como skill versionável

> Feature `018-encerrar-sessao-como-skill` · 2026-06-28
> Itens que precisam continuar verdadeiros nas próximas extrações (`/reversa`).
> Derivados da seção "Modificadas" de `legacy-impact.md`. IDs estáveis (não reciclar).

## Watch items

| ID   | Origem (arquivo, seção)                                               | Regra esperada após a mudança                                                                                                                                                                                                    | Tipo de verificação | Sinal de violação                                                                                                                                                                                                           |
| ---- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | `domain.md#RN-N28`; `session_skills.py`                               | A materialização de sessão é **incondicional** (Claude + Antigravity) e grava a **árvore da skill** (`SKILL.md` + `scripts/`) sob o `skills_dir` de cada harness; agnóstica e não-destrutiva, sob `project_path`.                | presença            | `init`/`upgrade`/`materialize` não cria `.claude/skills/encerrar-sessao/SKILL.md` ou `.agents/skills/encerrar-sessao/SKILL.md`; ou volta a gravar `.claude/commands/encerrar-sessao.md`; ou escreve fora de `project_path`. |
| W002 | `domain.md#RN-N29`; `harness_profiles.py`                             | O perfil expõe `skills_dir()` por harness (Claude `.claude/skills`, Antigravity `.agents/skills`, Gemini `None`); `session_command_artifact` não existe mais.                                                                    | ausência + presença | Reaparece `session_command_artifact` em qualquer perfil; ou `skills_dir` diverge (ex.: Antigravity volta a `.agent/...`); ou Gemini passa a expor `skills_dir`.                                                             |
| W003 | `legacy-impact.md#Modificadas`; `stale_session_command_paths`         | A migração remove os órfãos legados (`.claude/commands/encerrar-sessao.md`, `.agent/workflows/encerrar-sessao.md`, `.agents/workflows/encerrar-sessao.md`) preservando arquivos de terceiros (ex.: `SPEC.md`, outros workflows). | presença            | Um órfão sobrevive ao `upgrade`/`materialize`; ou um arquivo de terceiro no mesmo diretório é removido.                                                                                                                     |
| W004 | `roadmap.md#D-01`; `close_flow.py`, `main.py`                         | A orquestração do encerramento vive em `SessionCloseFlow` (core), consumida pela borda CLI **e** pelos scripts finos da skill; o core segue agnóstico (RN-N5) e os scripts não reimplementam a lógica.                           | redação             | A CLI volta a duplicar a orquestração em `main.py`; ou os scripts da skill reimplementam o fluxo em vez de chamar o serviço; ou some a reexportação que os testes da 014 consomem.                                          |
| W005 | `interfaces/skill-contract.md`; `_bootstrap.py`, `encerrar_sessao.py` | Os scripts finos resolvem o core via git, re-executam sob o venv do core (teste por `sys.prefix`) e falham **barulhento** (exit ≠ 0 + mensagem) quando o core não é encontrado/importável.                                       | presença            | Core ausente passa a falhar em silêncio (exit 0) ou com traceback cru sem orientação; ou o re-exec deixa de cair no venv (volta a comparar binário).                                                                        |

## Observações (sem peso de regressão)

- **Ativação semântica no Antigravity** 🟡: a skill é reconhecida por contexto
  (não slash visual). Não verificável localmente; validar contra o Antigravity
  real quando disponível. Originada do amarelo herdado de RN-N29/017 — fora do
  watch principal por contrato (regras originalmente 🟡 não entram como
  regressão).

## Histórico de re-extrações

### Re-extração 2026-07-15 19:22

> Re-verificação dirigida pós-feature 022: o delta atualizou os assets da skill (v1.2.x → 1.3.0: passo 5 do marker `DECISAO_PENDENTE` + flag `--sem-decisao` no script). A propriedade central — scripts finos consumindo o core, sem reimplementação — permanece.

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | Skill materializada nos dois harnesses; árvore agnóstica única (assets), inalterado. |
| W002 | 🟢 verde | `scripts/encerrar_sessao.py` segue compondo `RegenService` → `SessionCloseFlow` do core; a novidade (repassar `sem_decisao=args.sem_decisao`) é fiação, não lógica duplicada (RN-N33). |
| W003 | 🟢 verde | `_bootstrap.py` inalterado (resolução da raiz via git + core importável, falha barulhenta). |
| W004 | 🟢 verde | Órfãos legados (command/workflow) seguem removidos por `stale_session_command_paths`, inalterado. |
| W005 | 🟢 verde | `skills_dir()` por perfil inalterado (`.claude/skills`, `.agents/skills`, `None` no Gemini). |

### Re-extração 2026-06-28 09:45

| ID   | Veredito | Observação                                                                                                                                                                                                                                                                                                                                                                        |
| ---- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | Materialização incondicional grava a árvore da skill (`SKILL.md` + `scripts/`) nos dois `skills_dir` e é não-destrutiva sob `project_path` — `_reversa_sdd/domain.md#RN-N28` reconciliado; smoke real de `apply_local_materializers` criou `.claude/skills/encerrar-sessao/SKILL.md` **e** `.agents/skills/encerrar-sessao/SKILL.md`; suíte 212 verde (`test_session_skills.py`). |
| W002 | 🟢 verde | `HarnessProfile.skills_dir()` → Claude `.claude/skills`, Antigravity `.agents/skills`, Gemini `None`; `session_command_artifact` ausente do código e do SDD — `domain.md#RN-N29` reconciliado; `harness_profiles.py` confirma.                                                                                                                                                    |
| W003 | 🟢 verde | A migração remove os três órfãos (`.claude/commands/…`, `.agent/workflows/…` singular, `.agents/workflows/…` plural) preservando terceiros — smoke real: `deploy-de-terceiro.md` e `SPEC.md` intactos após `materialize`; `legacy-impact.md#Modificadas`.                                                                                                                         |
| W004 | 🟢 verde | `SessionCloseFlow` (`close_flow.py`) é fonte única consumida pela CLI (`main.py:307` `cmd encerrar-sessao`) e pelo script da skill (`encerrar_sessao.py` compõe `RegenService`→`SessionCloseFlow`); helpers reexportados por `src.main`; `domain.md#2.15` (RN-N33) criado.                                                                                                        |
| W005 | 🟢 verde | `_bootstrap.py` resolve a raiz via `git rev-parse --show-toplevel`, re-executa sob o venv do core por `sys.prefix` (`os.execv`, linha 72-73, não compara binário) e falha barulhento (`CoreNotFoundError`, exit 1) quando o core não é encontrado; `interfaces/skill-contract.md`.                                                                                                |

## Arquivadas

<!-- Watch items promovidos/aposentados em extrações futuras. -->
