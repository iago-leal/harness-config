# Design: Execução Local do Harness Core

> Identificador: `run-harness-core-local`
> Data: `2026-06-23`
> Requirements: `_reversa_sdd/run-harness-core-local/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Visão Geral do Design

O design foca em desacoplar a execução do Harness Core de ferramentas globais instaladas no host, encapsulando a chamada no ambiente virtual de dependências Python. Ele é composto por duas partes integradas:

```
[ Usuário / Ganchos da IDE ] 
          │
          ▼
   [ Script harness ] (Raiz)
          │
          ├─► (Verifica se .harness/harness-core/.venv existe)
          │
          ▼ (Se válido, repassa "$@")
[ .harness/harness-core/.venv/bin/python3 ] ──► [ .harness/harness-core/src/main.py ]
```

---

## 2. Componentes Chaves

### 2.1 Script Wrapper `harness` 🟢
* **Tipo:** Executável Bash (POSIX compliant).
* **Localização:** Raiz do repositório (`/Users/iagoleal/dev/harness/harness`).
* **Responsabilidade:** 
  1. Descobrir o diretório absoluto de sua própria localização no disco local.
  2. Verificar se o interpretador Python virtual `.harness/harness-core/.venv/bin/python3` e o entry point principal `.harness/harness-core/src/main.py` estão presentes.
  3. Abortar e alertar o usuário caso a venv não exista.
  4. Encaminhar de forma atômica a execução repassando os parâmetros.

### 2.2 Interpretador Virtual Python (`.venv`) 🟢
* **Tipo:** Runtime Python 3 isolado.
* **Localização:** `.harness/harness-core/.venv/`.
* **Responsabilidade:** Executar o script principal da CLI do núcleo com acesso garantido a dependências compiladas e instaladas localmente (ex: `toml`, `mcp`, `pytest`).

---

## 3. Algoritmo de Execução do Wrapper

O algoritmo escrito em Bash deve garantir portabilidade e detecção confiável de caminhos relativos ao próprio script, independentemente de onde o usuário o chame no shell.

```bash
# 1. Resolve o caminho absoluto onde o próprio script reside (independente do CWD atual)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ABS_VENV_PYTHON="$SCRIPT_DIR/.harness/harness-core/.venv/bin/python3"
ABS_MAIN_PY="$SCRIPT_DIR/.harness/harness-core/src/main.py"

# 2. Valida venv (Fail-fast)
if [ ! -f "$ABS_VENV_PYTHON" ]; then
    echo "Erro: O ambiente virtual do harness-core não está configurado em..." >&2
    exit 1
fi

# 3. Executa utilizando exec (substitui o processo Bash atual pelo processo Python)
exec "$ABS_VENV_PYTHON" "$ABS_MAIN_PY" "$@"
```

---

## 4. Integração de Ganchos do Agente (Automação)

A integração com o ciclo de vida do agente de IA local (Claude Code / Gemini) baseia-se na delegação de comandos de hooks ao wrapper local. O modelo de integração é definido em `.reversa/settings.json.snippet`:

* **`SessionStart` (Startup/Resume):** Delegação para `./harness cmd resume` para carregamento de âncoras e consistência Git.
* **`PostToolUse` (Format-on-save):** Delegação para `./harness format` (com o caminho do arquivo modificado anexado pela IDE).
* **`Stop` (Encerramento de ciclo):** Delegação para `./harness decisions` para consolidação do grafo e geração de backlinks.
