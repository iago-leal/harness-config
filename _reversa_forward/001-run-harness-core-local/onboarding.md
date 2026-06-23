# Onboarding: Execução Local do Harness Core

> Identificador: `001-run-harness-core-local`
> Data: `2026-06-23`

Este guia descreve o procedimento para habilitar, executar e testar a execução local do `harness-core` a partir da raiz do projeto local.

---

## 🚀 1. Configuração do Ambiente Virtual (Pre-requisitos)

Antes de executar o wrapper `./harness`, garanta que o ambiente virtual e as dependências do `harness-core` estejam devidamente configurados.

```bash
# Navegue até o diretório do core
cd harness-core

# Crie o ambiente virtual
python3 -m venv .venv

# Ative o ambiente virtual
source .venv/bin/activate

# Instale as dependências requeridas pelo núcleo
pip install -r requirements.txt

# Retorne à raiz
cd ..
```

---

## 🛠️ 2. Criação e Execução do Wrapper

O arquivo `./harness` deve ser criado na raiz do repositório `/Users/iagoleal/dev/harness` com as permissões de execução corretas.

Para testar a criação manualmente no seu terminal:

```bash
# 1. Garanta que o arquivo "./harness" existe e possui permissão de execução
chmod +x harness

# 2. Teste o comando de compilação de decisões
./harness decisions
```

---

## 🔄 3. Substituição de Ganchos do Agente (settings.json)

Substitua os ganchos do legado apontando-os para o `./harness` na raiz do seu projeto local.

O snippet a ser utilizado no arquivo `settings.json` do agente de IA local (`claude-config/settings.json` ou arquivo equivalente de configuração do host) é:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear",
        "hooks": [
          {
            "type": "command",
            "command": "./harness cmd resume",
            "timeout": 12,
            "statusMessage": "Iniciando sessão do Harness..."
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "./harness format",
            "timeout": 30,
            "statusMessage": "Formatando código com o Harness..."
          }
        ]
      }
    ]
  }
}
```

---

## 🧪 4. Validação de Funcionamento

1. Execute `./harness decisions` a partir da raiz do repositório. O resultado esperado é:
   ```
   Grafo de microdecisões validado com sucesso (zero erros).
   Índice de decisões compilado com sucesso em 'microdecisoes.md'.
   ```
2. Delete o diretório `harness-core/.venv` temporariamente e execute `./harness decisions`. O resultado esperado é:
   ```
   Erro: O ambiente virtual do harness-core não está configurado em: harness-core/.venv
   Por favor, execute o setup do ambiente conforme o onboarding.md.
   ```
3. Reconfigure a venv para restaurar o estado de execução válido.
