# Comandos Customizados (Commands) — Design Técnico

> Regenerado pelo Writer em 2026-06-24 (Re-extração após a feature 004)
> Foca no COMO a unit é construída, a partir do código legado lido. Escala: 🟢 / 🟡 / 🔴

## Interface

| Símbolo                          | Assinatura                                     | Retorno                | Observação                                                   |
| -------------------------------- | ---------------------------------------------- | ---------------------- | ------------------------------------------------------------ |
| `CommandService.execute_command` | `(command, args, repo_path, session_filepath)` | `str`                  | Normaliza e despacha; comando desconhecido → string de erro. |
| `CommandService.load_session`    | `(session_filepath)`                           | `SessionState \| None` | Ausente → `None`; malformado → `MalformedSessionStateError`. |
| `CommandService.save_session`    | `(state, session_filepath)`                    | —                      | `serializer.render` + gravação atômica.                      |

## Fluxo Principal

1. **Normalização:** `command.strip().lower().lstrip("/")`. 🟢
2. **`encerrar-sessao`:** carrega sessão; ausente/inativa → erro. Lê HEAD (`GitPort`), `session.close_session(commit)`, salva atomicamente. 🟢
3. **`resume`:**
   - Sem sessão → cria `SessionState` com HEAD atual e feature `args[0]` (ou `"default_feature"`), salva, retorna "Nova sessão". 🟢
   - Com sessão → compara `session.commit_hash` com HEAD; se divergir, monta `⚠️ ALERTA` (RN-07); `start_session` reativa **preservando a narrativa** (RN-N3); salva; retorna `<warning><corpo da narrativa>\n<footer>`. O corpo vem de `serializer.render_narrative`. 🟢
4. **`clarificar`:** texto fixo (limite de 2 rodadas). 🟢
5. **`handoff`:** monta bloco Markdown com feature ativa + HEAD. 🟢
6. **Desconhecido:** `"Comando desconhecido: <command>"`. 🟢

## Fluxos Alternativos

- **Estado ausente em `resume`:** sessão nova normal (não erro). 🟢
- **Estado malformado:** `load_session` levanta `MalformedSessionStateError` (RN-N4). 🟢
- **`encerrar-sessao` sem sessão ativa:** erro explícito. 🟢
- **Divergência de âncora:** alerta antecede a narrativa; reativa mesmo assim. 🟢

## Dependências

- `GitPort` — HEAD para criação/encerramento e validação da âncora.
- `FileSystemPort` — leitura/gravação atômica do estado.
- `core/session/serializer` — `render` (persistência) e `render_narrative` (reinjeção).
- `core/session/errors.MalformedSessionStateError`.
- `core/domain/models.SessionState` / `SessionNarrative`.
- (Na borda) `core/session/sinks.get_sink` — escolhido por `main.py` conforme `active_harness` (RN-N5).

## Decisões de Design Identificadas

| Decisão                                                  | Evidência no código                   | Confiança |
| -------------------------------------------------------- | ------------------------------------- | --------- |
| Serviço agnóstico a IDE/harness; sink escolhido na borda | `service.py` (texto puro) + `main.py` | 🟢        |
| Âncora Git como detector de divergência na retomada      | `service.py` (`resume`)               | 🟢        |
| Narrativa preservada na reativação (não reinventada)     | `service.py` (`start_session`)        | 🟢        |
| Ausente ≠ malformado em `load_session`                   | `service.py` + `session/errors.py`    | 🟢        |

## Estado Interno

O estado de domínio é externalizado em `.harness/estado-da-sessao.md` (gerido pela unit `session`). O `CommandService` não guarda estado em memória entre chamadas; cada comando carrega/grava o arquivo.

## Observabilidade

- Alerta `⚠️` textual em divergência de âncora.
- `MalformedSessionStateError` como sinal barulhento de corrupção.
- A reinjeção real (stdout/arquivo) acontece na borda, pelo sink.

## Riscos e Lacunas

- 🟢 **T2 (resolvido na feature 006):** via MCP, `session_command` lê o caminho de sessão de `config.session.state_file` — o mesmo `.harness/estado-da-sessao.md` da CLI. Não há mais estado paralelo na raiz nem divergência CLI×MCP.
- 🟡 `clarificar` e `handoff` produzem texto; a ação efetiva (commits, push) descrita no Markdown legado não é mais executada pelo serviço (escopo reduzido).
