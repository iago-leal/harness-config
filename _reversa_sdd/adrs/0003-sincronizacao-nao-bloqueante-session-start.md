# ADR 0003: Sincronização Não-Bloqueante de Estado no SessionStart

- **Status:** Aceito (mecanismo shell superado — ver nota)
- **Data:** 2026-06-21
- **Contexto Técnico:** Módulo `bin` (`sync-check.sh`)
- **Escala de Confiança:** 🟢 CONFIRMADO

> ⚠️ **Atualização (2026-07-05, fechamento do G-05):** a decisão de fundo **permanece** (checagem read-only via `git ls-remote`, throttle por TTL de 24h, alerta não-obstrutivo, degradação resiliente offline). O que foi superado é o mecanismo: `bin/sync-check.sh` deu lugar ao `SyncService` (`src/core/sync/service.py`), acionado no `resume`. O cache deixou de viver no `$STATE_DIR` global por repositório e passou a ser por projeto, em `.harness/sync-cache.json` — caminho com fonte única na constante `SYNC_CACHE_REL_PATH` de `layout.py` (MD-0013). O serviço também absorveu a verificação passiva de versão do upstream (`check_version_update`/`check_version_update_remote`, features 012 e 014). Porta shell→Python sob a arquitetura hexagonal do ADR 0006.

## Contexto e Problema

Em fluxos de trabalho com múltiplos hosts (ex: Mac local e VPS remota) e agentes de IA distintos que compartilham memórias e repositórios locais, o agente pode iniciar tarefas sob uma base de código defasada em relação ao remote. Se o agente executar operações com base desatualizada, causará divergências difíceis de conciliar no Git.

Fazer uma verificação de rede síncrona (como `git fetch` ou `git pull`) a cada abertura de sessão pode introduzir lentidão severa na inicialização ou falhar se o host estiver temporariamente offline.

## Decisão

Adotar o script `bin/sync-check.sh` acoplado ao gancho `SessionStart` (startup, resume e clear) do Claude Code, operando em modo estritamente **read-only** (nunca executa escrita ou pulls na base ativa de forma silenciosa).

O comportamento de rede segue as seguintes diretrizes:

1. **ls-remote Read-Only:** O script executa `git ls-remote` apenas para consultar hashes mais recentes no remote, sem baixar objetos ou alterar o estado do git.
2. **Throttle com Cache Local (TTL):** Limita as consultas de rede a no máximo uma vez a cada 24 horas (TTL de 86400s) por repositório, gravando o hash remoto e o timestamp epoch Unix em um arquivo de cache local sob `$STATE_DIR/$(sanitize "$repo")`.
3. **Verificação de Direção Push (Trabalho Local):** Além de checar atraso em relação ao remote, realiza verificação local (sem rede) por modificações locais não integradas (commits locais à frente do remote ou working tree sujo) exclusivamente em diretórios de infraestrutura física.
4. **Alerta Não-Obstrutivo (SessionStart context):** Emite a notificação das pendências de sincronização formatada em JSON de contexto de sessão, instruindo o agente a alertar o usuário e oferecer as ações adequadas (`git pull --ff-only` ou `git push`), mas sem forçar a interrupção da execução do ambiente de desenvolvimento.

## Alternativas Consideradas

- **Git Pull Automatizado no Início:** Rejeitado porque pode mascarar conflitos de mesclagem locais e causar perda acidental de alterações não salvas pelo desenvolvedor, violando o princípio de integridade e controle humano.

## Consequências

- **Positivas:**
  - Alerta precoce de desvios ou códigos desatualizados logo no início da sessão do agente.
  - Inicialização extremamente veloz da CLI da IA devido ao controle estrito de cache local de 24 horas.
  - Garantia de funcionamento resiliente mesmo em cenários offline (no-op silencioso).
- **Negativas:**
  - O agente ou o desenvolvedor precisam interagir ativamente para resolver os alertas exibidos na tela.
