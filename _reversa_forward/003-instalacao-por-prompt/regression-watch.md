# Regression Watch: Instalação do Harness por Prompt Estruturado

> Identificador: `003-instalacao-por-prompt`
> Data: `2026-06-23`

## 1. Watch Items de Regressão

Nenhuma regra 🟢 do legado foi modificada (ver `legacy-impact.md#4-regras-modificadas`), então os itens abaixo guardam os **invariantes novos** que esta feature introduziu e que precisam continuar verdadeiros nas próximas extrações. Todos derivam de requisitos 🟢.

| ID   | Origem (arquivo, seção)                           | Regra esperada após mudança                                                                                                           | Tipo de verificação | Sinal de violação                                                                                                            |
| :--- | :------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------ | :------------------ | :--------------------------------------------------------------------------------------------------------------------------- |
| W001 | `requirements.md#5` (RF-01)                       | O prompt de instalação é **derivado por introspecção** via `InstallPromptService`, não um Markdown estático mantido à mão.            | presença            | Surge um arquivo de instalação estático na raiz/`harness-core` mantido manualmente, ou a introspecção é removida do serviço. |
| W002 | `requirements.md#4` (RN-03) / `roadmap.md` (D-06) | O prompt aponta os ganchos para o `.claude/settings.json` do **projeto** e proíbe editar `~/.claude`.                                 | presença            | O prompt instrui edição da configuração global `~/.claude`, ou deixa de mencionar o escopo de projeto.                       |
| W003 | `requirements.md#4` (RN-05)                       | Enquanto a feature 004 não fechar a regressão, o prompt **sinaliza** a lacuna do `SessionStart` como pendência conhecida (`MD-0001`). | presença            | O prompt deixa de mencionar a pendência do `SessionStart`, mascarando a dívida.                                              |

## 2. Histórico de re-extrações

### Re-extração 2026-06-24 10:06

| ID   | Veredito   | Observação                                                                                                                                                                                                                      |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde   | Introspecção via `InstallPromptService` (`{{COMMANDS}}` derivado do argparse) preservada. Inalterada pela 006.                                                                                                                  |
| W002 | 🟢 verde   | `template.md:23` aponta o `.claude/settings.json` do projeto e proíbe `~/.claude`. Reforçado pelo footprint global zero da 006 (MD-0005 / ADR 0013).                                                                            |
| W003 | 🟡 amarelo | `template.md:42` ainda sinaliza a pendência do `SessionStart` "a ser fechada na feature 004" — dívida já paga (a 004 reinjeta o estado). Defasagem documental persiste, fora do escopo da 006. Aguarda atualização do template. |

### Re-extração 2026-06-24 08:10

| ID   | Veredito   | Observação                                                                                                                                                                                        |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde   | Introspecção confirmada em service.py:19-28; {{COMMANDS}} preenchido dinamicamente do argparse.                                                                                                   |
| W002 | 🟢 verde   | Escopo do `.claude/settings.json` do projeto e proibição de `~/.claude` confirmados em template.md:23.                                                                                            |
| W003 | 🟡 amarelo | Menção da pendência presente (template.md:42), mas redação defasada vs. código: SessionStart já funciona (main.py:211-215, sinks.py:39). Template afirma "ainda não reinjeta" quando já reinjeta. |

### Re-extração 2026-06-23 21:58

| ID   | Veredito   | Observação                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| W001 | 🟢 verde   | Prompt derivado por introspecção via `InstallPromptService` + `core/install/template.md` (placeholder `{{COMMANDS}}` preenchido do argparse); não é Markdown estático mantido à mão.                                                                                                                                                                                                                                           |
| W002 | 🟢 verde   | `template.md:23` — "aplique SEMPRE no `.claude/settings.json` do **projeto**. Nunca edite a configuração global em `~/.claude`".                                                                                                                                                                                                                                                                                               |
| W003 | 🟡 amarelo | Presença satisfeita — o prompt ainda sinaliza a pendência do `SessionStart`/`MD-0001` (`template.md:42`). PORÉM a premissa da regra ("enquanto a feature 004 não fechar") EXPIROU: a 004 foi codada e o `SessionStart` reinjeta o estado (observado no boot desta sessão). A nota virou obsoleta — afirma uma dívida já paga. Recomendação: atualizar `template.md` e arquivar/atualizar este W003. Aguarda julgamento humano. |

## 3. Arquivadas

_Nenhuma regra arquivada nesta rodada._

## 4. Observações (sem peso de regressão)

Itens originalmente 🟡 / 🔴, fora do watch principal:

- **Perfil do `antigravity` (🔴):** o mecanismo de ganchos do antigravity ainda não está documentado no `_reversa_sdd/`; o perfil é um placeholder que avisa antes de aplicar. Quando o mecanismo for confirmado, promover a watch item de presença.
- **Perfil do `gemini` (🟡):** assume a ponte `context.*` descrita no ALICERCE; revalidar contra a SPEC de memória do Gemini se ela mudar.
