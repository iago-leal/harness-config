# Perguntas para Validação — harness

> Regenerado pelo Revisor em 2026-06-24 (Re-extração após as features 003, 004 e 005)
> Responda cada pergunta (preencha o campo **Resposta**) e me avise quando terminar — basta digitar `reversa`.

A re-extração tem confiança alta (≈85%) e cobertura completa do código de produto. As perguntas abaixo **não** decorrem de trechos de código indecifráveis — o código foi lido por inteiro —, mas de **decisões que só o mantenedor pode tomar**: rumo das dívidas, correção dos bugs latentes e o destino dos artefatos desatualizados. São 5 perguntas.

---

## Pergunta 1

**Contexto:** Reprodutibilidade — `harness-core/requirements.txt` usa pins `>=` (mínimos); não há lock file commitado nem CI/CD (`surface.json.ci_cd = []`).
**Spec afetada:** [`_reversa_sdd/dependencies.md`], `confidence-report.md` (Lacunas Pendentes), `gaps.md#G-07`
**Pergunta:** A ausência de lock file e de CI é uma escolha deliberada (projeto pessoal, *single maintainer*) ou uma dívida a sanar? Se a sanar, qual ferramenta de lock prefere (`pip-tools`/`requirements.lock`, `uv`, `poetry`)?
**Impacto:** Define se a lacuna de reprodutibilidade vira 🟢 (decisão consciente, registrada como tal) ou permanece 🔴 com ticket de manutenção. Princípio nº 5.3 do mantenedor sugere lock file commitado sempre.

**Resposta:** <!-- preencha aqui -->

---

## Pergunta 2

**Contexto:** T4 — `harness.toml` declara `[formatting]` (`exclude_paths`, `opt_out_file`), mas `FormattingService.format_file` **ignora** essa config: as blindagens (`~`, `~/Notas`, `~/.claude`) e o nome do opt-out (`.no-autoformat`) estão chumbados no código (`core/formatting/service.py`).
**Spec afetada:** [`_reversa_sdd/format-on-edit/design.md`], [`_reversa_sdd/data-dictionary.md` §6], `code-analysis.md` (T4)
**Pergunta:** A intenção é que o `[formatting]` do `harness.toml` **passe a alimentar** o serviço (config viva, Princípio nº 5.1), ou os valores devem permanecer chumbados e a seção do TOML é vestigial (e deve ser removida)?
**Impacto:** Se a config deve valer, há um bug de coesão a corrigir; se é vestigial, a spec deve declarar `[formatting]` como decorativo e o documento de domínio deixa de sugerir configurabilidade.

**Resposta:** <!-- preencha aqui -->

---

## Pergunta 3

**Contexto:** T5 — `main.py` mantém **duas** vias de configuração: a função legada `load_harness_config` (dict com defaults, sem `[decisions]`, usada pelo subcomando `cmd` para ler `active_harness`) e a tipada `load_config` (usada por `decisions` e `install-prompt`).
**Spec afetada:** [`_reversa_sdd/run-harness-core-local/design.md`], `code-analysis.md` (nota residual / T5)
**Pergunta:** Confirma que a intenção é **consolidar** tudo em `load_config` (tipada) e remover `load_harness_config`? Ou há razão para o `cmd` ler a config pelo caminho legado?
**Impacto:** Determina se T5 é dívida a sanar (downgrade de coesão a registrar) ou um arranjo intencional. Afeta a recomendação de refactor no relatório.

**Resposta:** <!-- preencha aqui -->

---

## Pergunta 4

**Contexto:** T1 e T2 — o driver MCP (`adapters/mcp/server.py`) tem dois bugs latentes confirmados: `process_decisions` chama `load_config` sem import (`NameError`, l.60) e `session_command` aponta para `ESTADO-DA-SESSAO.md` na raiz (l.92), divergente da CLI (`.harness/estado-da-sessao.md`). O ADR 0012 já registra que a seção `[session]` análoga à `[decisions]` **não** foi adotada na feature 005, deixando T2 como pendência consciente.
**Spec afetada:** [`_reversa_sdd/microdecisoes/`], [`_reversa_sdd/session/`], [`_reversa_sdd/comandos-customizados/`], `adrs/0012`
**Pergunta:** O servidor MCP é um caminho de uso ativo (você invoca as tools `process_decisions`/`session_command` via MCP) ou está dormente enquanto o fluxo real é a CLI por hooks? Corrigir T1/T2 (import + caminho de sessão, idealmente via nova seção `[session]`) entra na próxima feature?
**Impacto:** Se o MCP está dormente, T1/T2 são dívida de baixa urgência e a spec deve marcá-los como "tool MCP não exercida". Se é caminho ativo, são bugs de alta prioridade que produzem estado de sessão órfão e índice de decisões nunca gerado via MCP.

**Resposta:** <!-- preencha aqui -->

---

## Pergunta 5

**Contexto:** Artefatos desatualizados — `user-stories/fluxo-de-sincronia-e-sessao.md` e os 5 `flowcharts/*.md` datam de 2026-06-23 e descrevem o **legado purgado** (scripts `sync-check.sh`, `format-on-edit.sh`, `gerar-index-decisoes.sh`, `.claude/ESTADO-DA-SESSAO.md`, manifesto `pyproject.toml`). Não foram regenerados nesta re-extração e contradizem todos os artefatos centrais (que descrevem o core Python e `.harness/`).
**Spec afetada:** [`_reversa_sdd/user-stories/fluxo-de-sincronia-e-sessao.md`], [`_reversa_sdd/flowcharts/*.md`], `gaps.md#G-02`, `#G-03`
**Pergunta:** Quer que esses artefatos sejam **regenerados** alinhados ao estado atual (o Revisor não os reescreveu por estarem fora do conjunto desta re-extração), **marcados como históricos** (snapshot da feature 002), ou **removidos**?
**Impacto:** Hoje são a maior fonte de inconsistência cruzada do `_reversa_sdd/`. Mantê-los como estão pode confundir o "eu de daqui a 12 meses" ao descrever código que não existe mais.

**Resposta:** <!-- preencha aqui -->
