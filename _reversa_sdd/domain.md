# Modelo de Domínio e Glossário (Domain) — harness-core

> Gerado pelo Detective em 2026-06-23 (Re-extração após Feature 002)
> Nível de Documentação: **Completo**

Este documento define o glossário semântico e as regras de domínio fundamentais que regem o comportamento e as restrições do núcleo Python do `harness`.

---

## 📖 1. Glossário de Domínio

### 🛡️ 1.1 Conceitos e Entidades Chave

* **Sessão do Agente:** Estado temporal que indica se o assistente de IA está em atividade ativa em uma determinada feature, monitorada pelo `ESTADO-DA-SESSAO.md`.
* **Âncora Git de Sessão:** SHA-1 do commit de fechamento da sessão gravado para assegurar integridade referencial se houver retomada da sessão sob uma revisão ou branch defasada.
* **Wrapper Executável (`harness`):** Ponto de entrada de conveniência em Bash localizado na raiz do projeto que direciona chamadas para o interpretador virtual Python, garantindo isolamento de dependências.
* **Formatador de Arquivos (`Formatter`):** Utilitário executável local ou global invocado automaticamente após a IA modificar arquivos para manter a padronização do código.
* **Shadow Mode (Coexistência Paralela):** Modo de bootstrap em que os ganchos legados rodam em primeiro plano enquanto a CLI Python executa em segundo plano de forma passiva para gravação de logs de fumaça.
* **Corte Definitivo:** Modo de bootstrap em que a CLI Python assume exclusivamente as responsabilidades dos hooks Git locais.
* **Opt-out de Formatação:** Mecanismo de recusa de formatação automática ativado pela presença do arquivo `.no-autoformat` na raiz ou subdiretórios.
* **Documentação Standalone (`harness-docs.html`):** Arquivo único autossuficiente e offline contendo a documentação CLI, regras de domínio vigentes e o andamento dos checkpoints do Reversa.

---

## ⚡ 2. Regras de Domínio Fundamentais

### 🔄 2.1 Fluxo de Sincronização e Resiliência

* **RN-01: Janela TTL de Sincronia (Cache Local)** 🟢
  - Origem: `harness-core/src/core/sync/service.py`
  - Evita chamadas Git redundantes guardando o resultado da verificação remota no cache por 24 horas.
* **RN-02: Resiliência Offline** 🟢
  - Origem: `harness-core/src/core/sync/service.py`
  - Se a chamada Git de rede (`ls-remote`) falhar, o sistema emite um aviso no terminal e assume que o repositório está sincronizado (`True`), nunca travando a inicialização do agente de IA.

### ✍️ 2.2 Integridade e Salvaguarda de Arquivos (Formatação)

* **RN-03: Não-Bloqueio de Formatadores (Blindagem)** 🟢
  - Origem: `harness-core/src/core/formatting/service.py`
  - A execução de formatadores e linters deve sempre retornar código de saída `0` (inclusive sob falha das ferramentas ou erros de importação), de modo a nunca causar pânico ou abortar as tarefas de escrita do editor do agente de IA.
* **RN-04: Proteção de Diretórios Críticos** 🟢
  - Origem: `harness-core/src/core/formatting/service.py`
  - O formatador deve abortar instantaneamente a execução sem alterar o arquivo se detectado que o arquivo reside na pasta `$HOME`, Notas Obsidian (`~/Notas`) ou configurações globais (`~/.claude`).
* **RN-05: Precedência de Executáveis Locais** 🟢
  - Origem: `harness-core/src/core/formatting/service.py`
  - O resolvedor de formatadores prioriza o uso de binários instalados na raiz do projeto (como `.venv/bin/ruff` ou `node_modules/.bin/prettier`) em detrimento a instalações globais do host.
* **RN-06: Opt-out do Projeto** 🟢
  - Origem: `harness-core/src/core/formatting/service.py`
  - A presença do arquivo `.no-autoformat` na pasta do arquivo ou em qualquer diretório superior cancela a formatação imediata.

### 👥 2.3 Tomada de Decisão e Consistência de Sessão

* **RN-07: Validação da Âncora de Integridade Git** 🟢
  - Origem: `harness-core/src/core/commands/service.py`
  - Ao retomar uma sessão, se a hash do commit HEAD atual do repositório diferir da hash gravada no `ESTADO-DA-SESSAO.md` no fechamento anterior, um alerta de inconsistência de estado deve ser impresso de forma explícita.

### 📝 2.4 Geração e Exposição de Documentação

* **RN-08: Sincronização Automática da Documentação (Build)** 🟢
  - Origem: `harness-core/src/core/documentation/service.py`
  - O arquivo HTML gerado deve ser atualizado de forma síncrona ou assíncrona na raiz do projeto (`harness-docs.html`) toda vez que comandos da CLI ou regras de negócio sofrerem alteração, ou através do comando `./harness doc-gen`.
* **RN-09: Autossuficiência e Portabilidade do HTML** 🟢
  - Origem: `harness-core/src/core/documentation/service.py`
  - A documentação gerada deve consistir em um único arquivo HTML contendo todos os estilos (CSS inline) e scripts necessários, sem depender de conexões externas de rede.
* **RN-10: Introspecção Dinâmica dos Comandos** 🟡
  - Origem: `harness-core/src/core/documentation/service.py`
  - A ajuda dos comandos CLI do `harness-core` deve ser extraída diretamente das definições do `argparse.ArgumentParser`, evitando discrepâncias manuais no HTML.
