# Matriz de Permissões (Permissions) — harness-core

> Regenerado pelo Detective em 2026-06-24 (re-extração após as features 003, 004, 005, 006 e 007)
> Nível de Documentação: **Completo**

O `harness-core` é um sistema **monousuário local sem RBAC formal**: não há autenticação, papéis nem ACL no código. A "matriz" abaixo é uma **convenção operacional inferida** — a divisão de fato está entre as automações disparadas por ganchos do agente de IA e a intervenção manual do mantenedor humano via CLI. Toda separação aqui é 🟡 INFERIDA, salvo onde o código impõe o caminho (ex.: ganchos do `settings.json`).

---

## 🔑 1. Atores do Sistema

* **Desenvolvedor Humano (mantenedor):** Mantenedor único. Executa qualquer subcomando da CLI diretamente e edita os artefatos versionados (`.harness/`, `harness.toml`, `settings.json`).
* **Agente de IA (Claude / Gemini / Antigravity):** Assistente no host. Dispara um subconjunto de operações automaticamente via ganchos de ciclo de vida, em sub-shells, sob a premissa de **nunca bloquear** (saída sempre tolerante a falha).

---

## 📊 2. Matriz de Permissões (convenção)

| Operação | Subcomando / Gatilho | Disparada por hook do agente | Intervenção manual (humano) | Confiança |
| :--- | :--- | :---: | :---: | :--- |
| **bootstrap** | `./harness bootstrap` | ❌ Não (setup pontual) | 🟢 Sim | 🟡 INFERIDO |
| **init** | `./harness init <destino>` (feature 007) | ❌ Não (setup pontual) | 🟢 Sim | 🟡 INFERIDO |
| **upgrade** | `./harness upgrade` (feature 007) | ❌ Não | 🟢 Sim | 🟡 INFERIDO |
| **format** | `./harness format` — hook `PostToolUse` (Write\|Edit) | 🟢 Sim (automático) | 🟢 Sim | 🟢 CONFIRMADO (gatilho no `settings.json`) |
| **decisions** | `./harness decisions` — hook `Stop` | 🟢 Sim (automático) | 🟢 Sim | 🟢 CONFIRMADO (gatilho no `settings.json`) |
| **cmd resume** | `./harness cmd resume` — hook `SessionStart` | 🟢 Sim (automático, reinjeta estado) | 🟢 Sim | 🟢 CONFIRMADO (gatilho no `settings.json`) |
| **cmd encerrar-sessao** | `./harness cmd encerrar-sessao` | ❌ Não (encerramento deliberado) | 🟢 Sim | 🟡 INFERIDO |
| **cmd handoff** | `./harness cmd handoff` | ❌ Não | 🟢 Sim | 🟡 INFERIDO |
| **cmd clarificar** | `./harness cmd clarificar` | ❌ Não | 🟢 Sim | 🟡 INFERIDO |
| **install-prompt** | `./harness install-prompt` | ❌ Não (geração para colagem manual) | 🟢 Sim | 🟡 INFERIDO |
| **doc-gen** | `./harness doc-gen` | ❌ Não | 🟢 Sim | 🟡 INFERIDO |
| **doc-serve** | `./harness doc-serve` | ❌ Não | 🟢 Sim | 🟡 INFERIDO |

---

## 🛡️ 3. Salvaguardas como Controle de Acesso de Fato

Na ausência de RBAC, o controle efetivo de "o que o agente pode fazer sem supervisão" é exercido por blindagens no código, não por papéis:

* **Blindagem de diretórios pessoais (RN-04):** o agente, via hook de formatação, **não pode** tocar `~`, `~/Notas` ou `~/.claude` — barreira de dados pessoais.
* **Opt-out por projeto (RN-06):** `.no-autoformat` retira o consentimento de formatação automática num projeto.
* **Não-bloqueio (RN-03/RN-02/RN-N15):** todas as operações de hook degradam para no-op em vez de abortar — o agente nunca "trava" o ambiente.
* **Resolução de Perfil e Setup Fail-Fast (RN-N10 / RN-N19):** o init executa o setup de ganchos e `.venv` validando dependências de forma fail-fast e informando o usuário sobre correções no host.
* **Evolução Não-Destrutiva (RN-N20):** o upgrade atualiza o core e wrapper do local de destino, mas preserva intactas as pastas locais `.reversa/` e `.harness/decisoes/`.
* **Seleção de mecanismo por harness (RN-N6):** o *sink* de sessão e o *perfil* de instalação são escolhidos pelo `active_harness`; um harness desconhecido **falha barulhento** em vez de agir por padrão silencioso.

> 🔴 **LACUNA:** não há modelo de permissões multiusuário, autenticação nem trilha de auditoria de quem executou cada comando — coerente com o contexto de *single maintainer* local. Caso o harness venha a rodar em host compartilhado (ex.: VPS multiusuário), esta matriz precisaria virar um RBAC real.
