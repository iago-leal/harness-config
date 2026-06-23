# Regression Watch: Instalação do Harness por Prompt Estruturado

> Identificador: `003-instalacao-por-prompt`
> Data: `2026-06-23`

## 1. Watch Items de Regressão

Nenhuma regra 🟢 do legado foi modificada (ver `legacy-impact.md#4-regras-modificadas`), então os itens abaixo guardam os **invariantes novos** que esta feature introduziu e que precisam continuar verdadeiros nas próximas extrações. Todos derivam de requisitos 🟢.

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
| :--- | :--- | :--- | :--- | :--- |
| W001 | `requirements.md#5` (RF-01) | O prompt de instalação é **derivado por introspecção** via `InstallPromptService`, não um Markdown estático mantido à mão. | presença | Surge um arquivo de instalação estático na raiz/`harness-core` mantido manualmente, ou a introspecção é removida do serviço. |
| W002 | `requirements.md#4` (RN-03) / `roadmap.md` (D-06) | O prompt aponta os ganchos para o `.claude/settings.json` do **projeto** e proíbe editar `~/.claude`. | presença | O prompt instrui edição da configuração global `~/.claude`, ou deixa de mencionar o escopo de projeto. |
| W003 | `requirements.md#4` (RN-05) | Enquanto a feature 004 não fechar a regressão, o prompt **sinaliza** a lacuna do `SessionStart` como pendência conhecida (`MD-0001`). | presença | O prompt deixa de mencionar a pendência do `SessionStart`, mascarando a dívida. |

## 2. Histórico de re-extrações

*Vazio. Será preenchido quando `/reversa` rodar novamente sobre o projeto.*

## 3. Arquivadas

*Nenhuma regra arquivada nesta rodada.*

## 4. Observações (sem peso de regressão)

Itens originalmente 🟡 / 🔴, fora do watch principal:
* **Perfil do `antigravity` (🔴):** o mecanismo de ganchos do antigravity ainda não está documentado no `_reversa_sdd/`; o perfil é um placeholder que avisa antes de aplicar. Quando o mecanismo for confirmado, promover a watch item de presença.
* **Perfil do `gemini` (🟡):** assume a ponte `context.*` descrita no ALICERCE; revalidar contra a SPEC de memória do Gemini se ela mudar.
