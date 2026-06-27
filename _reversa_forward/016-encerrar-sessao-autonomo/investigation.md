# Investigation: encerrar-sessao autônomo

> Identificador: `016-encerrar-sessao-autonomo`
> Data: `2026-06-27`

## 1. Raiz do RN-05 — por que o hook de resume não foi plantado no consumidor

**Achado (🟢, confirmado por inspeção do código):** nenhuma rotina do `init`/`upgrade` escreve `.claude/settings.json`. Cadeia verificada:

- `apply_local_materializers` (`src/core/install/local_apply.py:19`) aplica **apenas** `materialize_session_commands` (sempre) e `materialize_hooks_json` (somente `active_harness == "antigravity"`). Não há materializador de `settings.json` do Claude.
- `ClaudeProfile.hooks_block()` (`harness_profiles.py:37`) devolve o JSON `{"hooks": {...}}` com `SessionStart → ${CLAUDE_PROJECT_DIR}/harness cmd resume`, mas esse texto só é consumido pelo **install-prompt** (`install/service.py:26`, substituição de `{{HOOKS_BLOCK}}`) — um bloco para o usuário **colar à mão**. O próprio `apply_instructions` diz "Mescle o bloco abaixo na chave `hooks` do `.claude/settings.json` do PROJETO (crie o arquivo se não existir)".

**Conclusão:** no perfil Claude, o hook de resume nunca é materializado automaticamente. O `harness` (este upstream) tem `.claude/settings.json` porque foi montado manualmente; um consumidor novo (ex.: `contrato-fotos-higor`) recebe só o slash command, nunca o hook de boot → a sessão nasce e morre `inactive` → o `encerrar-sessao` (pós-015) falha barulhento. Hipótese da sessão de diagnóstico **confirmada**.

**Decisão derivada (D-05):** materializador idempotente `materialize_claude_settings`, ligado ao `apply_local_materializers` com gate `claude`, garantindo a presença do hook de resume sem apagar configurações/hook de terceiros.

## 2. Reaproveitamento do `ProcessPort` para o regen

**Achado (🟢):** já existe `ProcessPort` (`src/core/ports/process.py`) com `run_command(args, cwd) -> (exit_code, stdout, stderr)` e adapter `HostFormatterAdapter` (`src/adapters/process/formatter.py`). O dispatch CLI já instancia `process` (usado nas ofertas de upgrade da 014). Logo, **não** se cria port novo: o `RegenService` recebe um `ProcessPort` e invoca `run_command(["sh","-c", command], cwd=repo_path)`. O shell é necessário porque o comando declarado pode ser composto (`python gerar_site.py && python empacotar.py`).

## 3. Lacuna do `GitPort` para o item (ii)

**Achado (🟢):** o `GitPort` tem `is_working_tree_clean(repo_path) -> bool` (só o booleano), mas não há como **listar** os caminhos sujos para filtrar `.harness/` e mostrar ao agente. Decisão (D-04): novo verbo `list_dirty_paths(repo_path) -> list[str]` via `git status --porcelain`, devolvendo os caminhos; o filtro de `.harness/` fica na borda (core agnóstico).

## 4. Reconciliação com a feature 015

A 015 introduziu `NoActiveSessionError` para ausente∪inativa com exit ≠ 0 (falha barulhenta). O D1/D3 **reverte conscientemente** essa parte: ausente → no-op ruidoso (exit 0), inativa → reativa+fecha (exit 0). Preserva-se o que a 015 acertou: **malformado** continua barulhento (`MalformedSessionStateError`, exit ≠ 0) para comandos explícitos, e `resume` segue não-bloqueante. A distinção RN-N4 (ausente ≠ malformado) sai reforçada: agora ausente é tolerado e malformado é o único caso barulhento. `NoActiveSessionError` provavelmente fica órfã no caminho do encerrar; avaliar remoção no coding (ou mantê-la para uso defensivo documentado).

## 5. Alternativas avaliadas

| Tema                    | Escolhido                                   | Descartado                                               | Porquê                                                                    |
| ----------------------- | ------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------- |
| Execução do regen       | `ProcessPort` + `sh -c`                     | Port novo; sem shell                                     | Abstração já existe; shell habilita comando composto                      |
| Orquestração "faz tudo" | Sequência na skill `.md` (regen → encerrar) | `encerrar` chamar regen internamente                     | RN-N5/SRP; mantém comandos testáveis e desacoplados                       |
| Commit do pendente      | Marker + agente (dualidade 014)             | Auto-commit pelo core                                    | Mensagem descritiva e split são julgamento do agente; evita capturar lixo |
| Recuperação (D2)        | Abortar sem fechar, sem rollback            | Rollback automático                                      | Espelha RN-N32; rollback é frágil/surpreendente                           |
| settings.json do Claude | Merge idempotente "garantir presença"       | Substituir a chave `hooks`; manter só a instrução manual | Não apaga hooks de terceiros; fecha a raiz                                |

## 6. Padrões aplicáveis do próprio legado

- **Merge não-destrutivo por chave** — molde de `materialize_hooks_json` (RN-N27): ler JSON existente, mesclar só a parte do harness, gravar atômico. O `materialize_claude_settings` segue o mesmo molde, adaptado a hooks por evento.
- **Dualidade TTY × não-TTY com marker** — `conduct_end_session_offers` / `render_offer_markers` da feature 014 (`interfaces/session-end-offers.md`). O `COMMIT_PENDENTE` é uma oferta irmã, porém **pré-fechamento**.
- **Falha barulhenta sem reverter estado** — `SessionCommitError` (RN-N32) como referência de contrato de recuperação.
