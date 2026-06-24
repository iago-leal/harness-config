# Onboarding: Testando o harness-init e Atualizações do Core

> Identificador: `007-bootstrap-harness-init`
> Data: `2026-06-24`

Este guia descreve as etapas para testar a instalação e atualização automatizada do harness em novos repositórios locais via terminal.

## Pré-requisitos de Teste

1. Um terminal aberto no repositório original do harness (`/Users/iagoleal/dev/harness`).
2. Uma pasta vazia fora do repositório configurada como um repositório git válido para servir de destino.
   ```bash
   mkdir -p /tmp/teste-harness-destino
   cd /tmp/teste-harness-destino
   git init
   ```

---

## Passo 1: Inicialização em Novo Projeto de Destino

1. No terminal do repositório original (`/Users/iagoleal/dev/harness`), execute o comando de inicialização apontando para a pasta criada:
   ```bash
   ./harness init /tmp/teste-harness-destino
   ```
2. Verifique o terminal de saída. A execução deve relatar em tempo real:
   - Criação da pasta `harness-core/` no destino.
   - Cópia do wrapper `harness` para a raiz.
   - Criação da venv em `harness-core/.venv/` e instalação de dependências.
   - Criação da pasta de dados `.harness/` e seus arquivos iniciais.
   - Bootstrap dos hooks git locais do destino.
3. Acesse a pasta de destino e confirme que a estrutura física bate com o esperado:
   ```bash
   cd /tmp/teste-harness-destino
   ls -la
   ls -la harness-core/
   ls -la .harness/
   cat harness.toml
   ```
4. Teste a execução do wrapper local no destino:
   ```bash
   ./harness decisions
   ```
   (Deve validar o grafo local de decisões vazias sem erros).

---

## Passo 2: Teste de Proteção Git (Destino Inválido)

1. Tente rodar a inicialização em uma pasta temporária qualquer que não seja repositório git:
   ```bash
   mkdir -p /tmp/teste-pasta-comum
   cd /Users/iagoleal/dev/harness
   ./harness init /tmp/teste-pasta-comum
   ```
2. O script deve falhar de forma barulhenta e abortar imediatamente informando que o destino não possui inicialização do git.

---

## Passo 3: Teste de Sincronia de Versão e Comando `upgrade`

1. Simule uma nova versão no repositório central. Altere temporariamente o número de versão no core original (e.g. mude para `"1.2.44"` em `src/core/domain/config.py` ou arquivo de metadados equivalente).
2. Vá para a pasta de destino (`/tmp/teste-harness-destino`).
3. Execute qualquer comando local, como `./harness decisions`.
4. Um aviso visível deve alertar que há uma nova versão disponível no upstream.
5. Execute o comando de upgrade no destino:
   ```bash
   ./harness upgrade
   ```
6. O terminal deve indicar que a cópia do core foi atualizada a partir do upstream.
7. Valide que as decisões e sessões originais do destino (se houverem) foram preservadas intocadas.
