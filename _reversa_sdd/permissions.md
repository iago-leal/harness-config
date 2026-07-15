# Matriz de Permissões (Permissions) — harness-core

> Regenerado pelo Detective em 2026-06-24 (re-extração após as features 003, 004, 005, 006 e 007)
> Nível de Documentação: **Completo**
> **Reconciliação de 2026-07-05** (pós-features 019-021): linhas `init`/`upgrade` atualizadas (fonte única, feature 020); novas linhas `migrate` e `materialize`; nota de salvaguarda RN-N19 substituída por RN-N36.
> **Reconciliação de 2026-07-15** (pós-MD-0014 e features 022-023): linha `format` atualizada — o gatilho `PostToolUse` do Claude foi **aposentado** (MD-0014; disparo automático só no Antigravity e no git pre-commit); linha `decisions` atualizada para a forma `decisions --gate` no hook Stop; nova salvaguarda do gate de registro (RN-N43..N47).

O `harness-core` é um sistema **monousuário local sem RBAC formal**: não há autenticação, papéis nem ACL no código. A "matriz" abaixo é uma **convenção operacional inferida** — a divisão de fato está entre as automações disparadas por ganchos do agente de IA e a intervenção manual do mantenedor humano via CLI. Toda separação aqui é 🟡 INFERIDA, salvo onde o código impõe o caminho (ex.: ganchos do `settings.json`).

---

## 🔑 1. Atores do Sistema

- **Desenvolvedor Humano (mantenedor):** Mantenedor único. Executa qualquer subcomando da CLI diretamente e edita os artefatos versionados (`.harness/`, `harness.toml`, `settings.json`).
- **Agente de IA (Claude / Gemini / Antigravity):** Assistente no host. Dispara um subconjunto de operações automaticamente via ganchos de ciclo de vida, em sub-shells, sob a premissa de **nunca bloquear** (saída sempre tolerante a falha).

---

## 📊 2. Matriz de Permissões (convenção)

| Operação                | Subcomando / Gatilho                                                                                                                     |              Disparada por hook do agente               | Intervenção manual (humano) | Confiança                                  |
| :---------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- | :-----------------------------------------------------: | :-------------------------: | :----------------------------------------- |
| **bootstrap**           | `./harness bootstrap`                                                                                                                    |                 ❌ Não (setup pontual)                  |           🟢 Sim            | 🟡 INFERIDO                                |
| **init**                | `./harness init <destino>` (feature 007; **fonte única desde a 020**: só shim + `.harness/`, sem copiar core/venv)                       |                 ❌ Não (setup pontual)                  |           🟢 Sim            | 🟡 INFERIDO                                |
| **upgrade**             | `./harness upgrade` (feature 007; ainda ativo — recopia o core para instalações no layout antigo, ver domain.md RN-N20)                  |                         ❌ Não                          |           🟢 Sim            | 🟡 INFERIDO                                |
| **migrate**             | `./harness migrate [root] [--dry-run]` (feature 020, NOVO) — converte instalações do layout copiado para a fonte única                   | ❌ Não (manutenção deliberada da base, não per-projeto) |           🟢 Sim            | 🟢 CONFIRMADO                              |
| **materialize**         | `./harness materialize` (feature 012, interno) — rematerializa artefatos de IDE com o código local; usado pelo `upgrade` via subprocesso |                         ❌ Não                          |       🟢 Sim (avulso)       | 🟢 CONFIRMADO                              |
| **format**              | `./harness format` — desde MD-0014, **sem hook no Claude** (era `PostToolUse` Write\|Edit); on-edit só no Antigravity (`agy-hook`), mais git pre-commit | 🟢 Sim (Antigravity/pre-commit) · ❌ Não no Claude | 🟢 Sim | 🟢 CONFIRMADO (perfil não emite mais o item) |
| **decisions**           | `./harness decisions --gate` — hook `Stop` (022; sem a flag = uso manual/post-merge, byte-idêntico ao anterior)                          |                   🟢 Sim (automático)                   |           🟢 Sim            | 🟢 CONFIRMADO (gatilho no `settings.json`) |
| **cmd resume**          | `./harness cmd resume` — hook `SessionStart`                                                                                             |          🟢 Sim (automático, reinjeta estado)           |           🟢 Sim            | 🟢 CONFIRMADO (gatilho no `settings.json`) |
| **cmd encerrar-sessao** | `./harness cmd encerrar-sessao [--sem-decisao]` (022: 3º portão de registro; o escape exige declaração explícita)                        |            ❌ Não (encerramento deliberado)             |           🟢 Sim            | 🟡 INFERIDO                                |
| **cmd handoff**         | `./harness cmd handoff`                                                                                                                  |                         ❌ Não                          |           🟢 Sim            | 🟡 INFERIDO                                |
| **cmd clarificar**      | `./harness cmd clarificar`                                                                                                               |                         ❌ Não                          |           🟢 Sim            | 🟡 INFERIDO                                |
| **install-prompt**      | `./harness install-prompt`                                                                                                               |          ❌ Não (geração para colagem manual)           |           🟢 Sim            | 🟡 INFERIDO                                |
| **doc-gen**             | `./harness doc-gen`                                                                                                                      |                         ❌ Não                          |           🟢 Sim            | 🟡 INFERIDO                                |
| **doc-serve**           | `./harness doc-serve`                                                                                                                    |                         ❌ Não                          |           🟢 Sim            | 🟡 INFERIDO                                |

---

## 🛡️ 3. Salvaguardas como Controle de Acesso de Fato

Na ausência de RBAC, o controle efetivo de "o que o agente pode fazer sem supervisão" é exercido por blindagens no código, não por papéis:

- **Blindagem de diretórios pessoais (RN-04):** o agente, via hook de formatação, **não pode** tocar `~`, `~/Notas` ou `~/.claude` — barreira de dados pessoais.
- **Opt-out por projeto (RN-06):** `.no-autoformat` retira o consentimento de formatação automática num projeto.
- **Não-bloqueio (RN-03/RN-02/RN-N15):** todas as operações de hook degradam para no-op em vez de abortar — o agente nunca "trava" o ambiente.
- **Resolução de Perfil Fail-Fast (RN-N10):** o `install-prompt` resolve o perfil do harness antes de qualquer I/O; harness inválido falha barulhento.
- **Fonte Única no `init` (RN-N36, substitui a nota histórica sobre RN-N19):** desde a feature 020, `init` não copia mais código nem cria `.venv` no destino — grava só o shim + `.harness/`; o setup fail-fast de dependências de host descrito na extração anterior aplica-se hoje ao `upgrade` (RN-N20, instalações ainda no layout antigo), não ao `init`.
- **Evolução Não-Destrutiva (RN-N20):** o upgrade atualiza o core e wrapper do local de destino, mas preserva intactas as pastas locais `.reversa/` e `.harness/decisoes/`. Ainda ativo — a remoção planejada pela 020 foi desescopada (ver domain.md, nota de reconciliação).
- **Guardas do `migrate` contra autodestruição (RN-N38):** `harness migrate` nunca remove o core do próprio upstream nem cai numa autorreferência circular; `_safe_remove_core` recusa remover qualquer diretório cujo nome-base não seja `harness-core` — um controle de acesso de fato sobre uma operação que, por design, escreve fora do projeto corrente (única exceção ao footprint per-projeto, RN-N17).
- **Seleção de mecanismo por harness (RN-N6):** o _sink_ de sessão e o _perfil_ de instalação são escolhidos pelo `active_harness`; um harness desconhecido **falha barulhento** em vez de agir por padrão silencioso. **Desde a feature 021**, essa mesma seleção também decide se o agente recebe o apêndice do índice de decisões no resume (RN-N41): hoje só o Claude, por corte deliberado de escopo — um controle de acesso de fato a mais dado por-harness, não por-papel.
- **Gate de registro de microdecisões (RN-N43..N47, features 022/023):** o agente não consegue encerrar sessão com trabalho substantivo sem registrar ficha `MD-NNNN` ou declarar explicitamente `--sem-decisao` (rastro auditável na narrativa) — uma obrigação imposta ao ator "agente de IA" pelo código, não por papel. A pressão é calibrada por borda: bloqueio no encerramento (com anti-loop), um soft-block por sessão no Stop do Claude, aviso simples no Antigravity. Desativável por projeto via `decisions.require_registration` (o mantenedor decide, não o agente).
- **Format-on-edit revogado no Claude (RN-N42, MD-0014):** o consentimento de formatação automática por edição foi retirado do perfil Claude na fonte — reintrodução é opt-in manual por diretório. O agente não formata mais nada implicitamente a cada `Write|Edit`.

> 🔴 **LACUNA:** não há modelo de permissões multiusuário, autenticação nem trilha de auditoria de quem executou cada comando — coerente com o contexto de _single maintainer_ local. Caso o harness venha a rodar em host compartilhado (ex.: VPS multiusuário), esta matriz precisaria virar um RBAC real.
